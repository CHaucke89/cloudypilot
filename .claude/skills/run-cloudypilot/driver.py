#!/usr/bin/env python3
"""Headless driver for the comma 3x (BIG) UI: reads commands on stdin, injects touches, saves screenshots."""

import argparse
import json
import os
import queue
import shlex
import socket
import sys
import threading
import time
import traceback

os.environ.setdefault("BIG", "1")
os.environ.setdefault("SCALE", "1")

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--out", default="/tmp/cloudypilot-ui", help="directory for screenshots without an absolute path")
parser.add_argument("--prime", type=int, default=0, help="PRIME_TYPE; 0 shows the Device/Quick Toggles cards on home")
parser.add_argument("--onboarding", action="store_true", help="keep the terms/training onboarding instead of skipping it")
parser.add_argument("--no-fake", action="store_true", help="don't publish fake deviceState/pandaStates/gps")
parser.add_argument("--remote", action="store_true", help="also stream frames to Remote UI (start stream_server.py first)")
parser.add_argument("--param", action="append", default=[], metavar="KEY=VALUE", help="set a param before the UI starts")
args = parser.parse_args()

os.environ.setdefault("PRIME_TYPE", str(args.prime))
os.makedirs(args.out, exist_ok=True)

import pyray as rl
from openpilot.common.prefix import OpenpilotPrefix
from openpilot.common.params import Params, ParamKeyType


def log(msg: str) -> None:
  print(f"drv> {msg}", flush=True)


def parse_value(p: Params, key: str, raw: str):
  t = p.get_type(key)
  if t == ParamKeyType.BOOL:
    return raw.lower() in ("1", "true", "on", "yes")
  if t == ParamKeyType.INT:
    return int(raw)
  if t == ParamKeyType.FLOAT:
    return float(raw)
  if t == ParamKeyType.JSON:
    return json.loads(raw)
  return raw


def seed_params(p: Params) -> None:
  # A bare prefix has no defaults (manager.py normally writes them), so default-on toggles would read False.
  for k in p.all_keys():
    d = p.get_default_value(k)
    if d is not None and p.get(k) is None:
      p.put(k, d)
  if not args.onboarding:
    from openpilot.common.version import terms_version, terms_version_sp, training_version
    p.put("HasAcceptedTerms", terms_version)
    p.put("HasAcceptedTermsSP", terms_version_sp)
    p.put("CompletedTrainingVersion", training_version)
    p.put("CompletedSunnylinkConsentVersion", "-1")
  p.put("UpdaterState", "idle")
  for kv in args.param:
    k, _, v = kv.partition("=")
    p.put(k, parse_value(p, k, v))


def stdin_reader(q: queue.Queue) -> None:
  for line in sys.stdin:
    line = line.strip()
    if line and not line.startswith("#"):
      q.put(line)
  q.put("quit")


HELP = """commands (coordinates are UI pixels, 2160x1080):
  ss [name]                 screenshot (relative names go to --out, .png added)
  tap X Y                   press+release
  longpress X Y [sec]       hold (default 0.8s)
  swipe X1 Y1 X2 Y2 [sec]   drag (default 0.3s); use for scrolling lists
  wheel DY                  mouse wheel, positive scrolls down
  key NAME                  Enter, Escape, Backspace, ArrowLeft, ...
  type TEXT                 type text into a focused keyboard
  settings [PANEL]          open settings (DEVICE, NETWORK, TOGGLES, SOFTWARE, PERSONALIZE, DEVELOPER, ...)
  home                      close settings
  param KEY VALUE           write a param (typed from the key's ParamKeyType)
  get KEY                   read a param
  tree [FILTER]             widgets drawn last frame: class, label, rect, center (FILTER matches class or label)
  find TEXT                 drawn widgets whose label contains TEXT
  tapon TEXT                tap the center of the innermost drawn widget whose label contains TEXT
  panels                    list settings panel names
  wait SEC                  keep rendering for SEC seconds
  eval PYTHON               run code; names: main, ui_state, gui_app, params, rl, device, PanelType, MainState
  quit"""


def main():
  cmds: queue.Queue[str] = queue.Queue()

  with OpenpilotPrefix():
    params = Params()
    seed_params(params)

    from openpilot.cereal import log as clog, messaging
    from openpilot.system.ui.lib.application import gui_app
    from openpilot.selfdrive.ui.layouts.main import MainLayout, MainState
    from openpilot.selfdrive.ui.layouts.settings.settings import PanelType
    from openpilot.selfdrive.ui.ui_state import device, ui_state
    from openpilot.cloudypilot.selfdrive.ui.touch_injector import SOCKET_PATH, TouchInjector

    # Without this the UI drops back to home ~10 s after the last touch.
    device.set_override_interactive_timeout(3600)

    pm = messaging.PubMaster(["deviceState", "pandaStates", "gpsLocationExternal"])

    def publish_fake():
      ds = messaging.new_message("deviceState")
      ds.deviceState.networkType = clog.DeviceState.NetworkType.wifi
      ds.deviceState.networkStrength = clog.DeviceState.NetworkStrength.great
      ds.deviceState.freeSpacePercent = 82
      ds.deviceState.cpuUsagePercent = [18, 22, 15, 20]
      ds.deviceState.memoryUsagePercent = 41
      ds.deviceState.maxTempC = 48
      pm.send("deviceState", ds)
      ps = messaging.new_message("pandaStates", 1)
      ps.pandaStates[0].pandaType = clog.PandaState.PandaType.tres
      ps.pandaStates[0].voltage = 12600
      pm.send("pandaStates", ps)
      gps = messaging.new_message("gpsLocationExternal")
      gps.gpsLocationExternal.hasFix = True
      gps.gpsLocationExternal.satelliteCount = 14
      pm.send("gpsLocationExternal", gps)

    gui_app.init_window("cloudypilot-driver")
    main_layout = MainLayout()

    # Same input path as Remote UI: JSON lines over the injector's unix socket.
    remote = None
    if args.remote:
      from openpilot.cloudypilot.selfdrive.ui.remote_ui import RemoteUI
      remote = RemoteUI()
      injector = remote.injector
    else:
      injector = TouchInjector()
      injector.start()
      gui_app.add_nav_stack_tick(injector.end_frame)
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(SOCKET_PATH)

    def send(**msg):
      sock.sendall((json.dumps(msg) + "\n").encode())

    def screenshot(name: str):
      path = name if os.path.isabs(name) else os.path.join(args.out, name)
      if not path.endswith(".png"):
        path += ".png"
      # Flush raylib's pending draw batch, or the last-drawn widgets are missing from the capture.
      rl.rl_draw_render_batch_active()
      img = rl.load_image_from_screen()
      rl.export_image(img, path)
      rl.unload_image(img)
      return path

    # Record every widget drawn each frame, so tree/find reflect what is on screen right now.
    from openpilot.system.ui.widgets import Widget
    drawn: list[tuple[int, Widget, tuple[float, float, float, float]]] = []
    frame_widgets: list[tuple[int, Widget, tuple[float, float, float, float]]] = []
    depth = [0]
    orig_render = Widget.render

    def recording_render(self, rect=None):
      idx = len(drawn)
      drawn.append((depth[0], self, (0, 0, 0, 0)))
      depth[0] += 1
      try:
        return orig_render(self, rect)
      finally:
        depth[0] -= 1
        r = self.rect
        drawn[idx] = (drawn[idx][0], self, (r.x, r.y, r.width, r.height))

    Widget.render = recording_render

    def label(w) -> str:
      for attr in ("title", "text", "_title", "_text", "_label"):
        try:
          v = getattr(w, attr, None)
          v = v() if callable(v) else v
        except Exception:
          continue
        if isinstance(v, str) and v:
          return v
      info = getattr(w, "panel_info", None)
      return getattr(info, "name", "") or ""

    def on_screen(r) -> bool:
      return r[2] > 0 and r[3] > 0 and r[0] < gui_app.width and r[1] < gui_app.height and r[0] + r[2] > 0 and r[1] + r[3] > 0

    def describe(d, w, r):
      text = label(w)
      text = f' "{text[:40]}"' if text else ""
      off = "" if on_screen(r) else " [off-screen]"
      return f"{'  ' * d}{type(w).__name__}{text} rect=({r[0]:.0f},{r[1]:.0f},{r[2]:.0f},{r[3]:.0f}) center=({r[0] + r[2] / 2:.0f},{r[1] + r[3] / 2:.0f}){off}"

    def find(text):
      text = text.lower()
      return [(d, w, r) for d, w, r in frame_widgets if w.is_visible and on_screen(r) and text in label(w).lower()]

    def panel_names():
      return [p.name for p in PanelType]

    ns = {"main": main_layout, "ui_state": ui_state, "gui_app": gui_app, "params": params, "rl": rl,
          "device": device, "PanelType": PanelType, "MainState": MainState}

    # Each step is (seconds to wait after sending, message or None).
    pending: list[tuple[float, dict | None]] = []
    # Let the fake deviceState reach the sidebar before the first command runs.
    busy_until = time.monotonic() + 1.5
    shot_n = 0

    def run(line: str) -> bool:
      nonlocal busy_until, shot_n
      parts = shlex.split(line) if not line.startswith(("eval ", "type ")) else line.split(" ", 1)
      cmd, a = parts[0], parts[1:]
      now = time.monotonic()
      if cmd == "quit":
        return False
      elif cmd == "help":
        print(HELP, flush=True)
      elif cmd == "ss":
        shot_n += 1
        log(f"saved {screenshot(a[0] if a else f'{shot_n:03d}')}")
      elif cmd == "tap":
        x, y = int(a[0]), int(a[1])
        pending.extend([(0.05, {"type": "mousemove", "x": x, "y": y}), (0.12, {"type": "mousedown", "x": x, "y": y}),
                        (0.5, {"type": "mouseup", "x": x, "y": y})])
      elif cmd == "longpress":
        x, y = int(a[0]), int(a[1])
        hold = float(a[2]) if len(a) > 2 else 0.8
        pending.append((0.05, {"type": "mousedown", "x": x, "y": y}))
        t = 0.0
        while t < hold:
          pending.append((0.2, {"type": "mousemove", "x": x, "y": y}))  # keeps the injector's 1 s remote window alive
          t += 0.2
        pending.append((0.5, {"type": "mouseup", "x": x, "y": y}))
      elif cmd == "swipe":
        x1, y1, x2, y2 = map(int, a[:4])
        dur = float(a[4]) if len(a) > 4 else 0.3
        steps = max(int(dur / 0.016), 2)
        pending.append((0.05, {"type": "mousedown", "x": x1, "y": y1}))
        for i in range(1, steps + 1):
          pending.append((dur / steps, {"type": "mousemove", "x": int(x1 + (x2 - x1) * i / steps), "y": int(y1 + (y2 - y1) * i / steps)}))
        # Holding still before release kills the fling so the list stops where the swipe ended.
        pending.extend([(0.15, {"type": "mousemove", "x": x2, "y": y2}), (0.8, {"type": "mouseup", "x": x2, "y": y2})])
      elif cmd == "wheel":
        pending.append((0.6, {"type": "scroll", "deltaY": float(a[0]), "x": 1080, "y": 540}))
      elif cmd == "key":
        pending.extend([(0.05, {"type": "keydown", "key": a[0]}), (0.2, {"type": "keyup", "key": a[0]})])
      elif cmd == "type":
        pending.append((0.3, {"type": "text", "text": a[0] if a else ""}))
      elif cmd == "settings":
        main_layout.open_settings(PanelType[a[0].upper()] if a else PanelType.DEVICE)
        busy_until = now + 0.6
      elif cmd == "home":
        main_layout._set_mode_for_state()
        busy_until = now + 0.6
      elif cmd == "param":
        params.put(a[0], parse_value(params, a[0], " ".join(a[1:])))
        busy_until = now + 0.3
      elif cmd == "get":
        log(f"{a[0]} = {params.get(a[0])!r}")
      elif cmd == "panels":
        log(" ".join(panel_names()))
      elif cmd == "tree":
        filt = a[0].lower() if a else ""
        for d, w, r in frame_widgets:
          if w.is_visible and (not filt or filt in type(w).__name__.lower() or filt in label(w).lower()):
            log(describe(d, w, r))
      elif cmd == "find":
        for _, w, r in find(" ".join(a)):
          log(describe(0, w, r).strip())
      elif cmd == "tapon":
        hits = find(" ".join(a))
        if not hits:
          log(f"err no visible widget labelled {' '.join(a)!r}")
          return True
        r = hits[-1][2]
        return run(f"tap {r[0] + r[2] / 2:.0f} {r[1] + r[3] / 2:.0f}")
      elif cmd == "wait":
        busy_until = now + float(a[0])
      elif cmd == "eval":
        code = a[0]
        try:
          log(repr(eval(code, ns)))
        except SyntaxError:
          exec(code, ns)
      else:
        log(f"unknown command {cmd!r}; try help")
        return True
      if cmd not in ("ss", "get", "tree", "find", "panels", "help"):
        log(f"ok {line}")
      return True

    threading.Thread(target=stdin_reader, args=(cmds,), daemon=True).start()
    log(f"ready ({gui_app.width}x{gui_app.height}); screenshots -> {args.out}")

    last_pub = 0.0
    running = True
    for _ in gui_app.render():
      frame_widgets[:] = drawn
      drawn.clear()
      now = time.monotonic()
      if not args.no_fake and now - last_pub > 0.2:
        publish_fake()
        last_pub = now
      ui_state.update()
      if remote is not None and ui_state.remote_ui_client_connected:
        rl.rl_draw_render_batch_active()
        remote.stream_frame()

      if now < busy_until:
        continue
      if pending:
        delay, msg = pending.pop(0)
        if msg is not None:
          send(**msg)
        busy_until = now + delay
        continue
      if not running:
        break
      try:
        line = cmds.get_nowait()
      except queue.Empty:
        continue
      try:
        running = run(line)
      except Exception:
        log(f"error in {line!r}:\n{traceback.format_exc()}")

    log("quit")
    sock.close()
    if remote is not None:
      remote.close()
    else:
      injector.stop()
    gui_app.close()


if __name__ == "__main__":
  main()
