"""Touch/mouse/keyboard injector for the raylib/pyray openpilot UI.

Python port of the old Qt ``touch_injector.cc``. The Qt version received JSON
input events on a Unix socket and synthesized ``QMouseEvent``/``QWheelEvent``
objects. raylib has no event queue to post into: input is *polled* every frame
(``is_mouse_button_pressed`` etc.). So instead we monkeypatch pyray's input
functions to report remote state, falling back to the real functions when no
remote client is active.

Clients may either send a single JSON object per connection (legacy) or keep
a connection open and stream newline-delimited JSON objects.

Keyboard events (``keydown``/``keyup``/``keytap`` with a browser ``KeyboardEvent.key``
name, and ``text`` for typed or pasted strings) are queued and handed to the UI
one frame at a time by ``end_frame()``, which the render loop calls once per frame,
mirroring how raylib fills its key and char queues in ``PollInputEvents``.
"""

import json
import os
import select
import socket
import threading
import time
from collections import deque

import pyray as pr

SOCKET_PATH = "/tmp/ui_touch_socket"

# How long a synthetic "click"/"tap" is held down before releasing, so the UI
# sees a full press -> release cycle across polled frames.
CLICK_HOLD_S = 0.12
# Fall back to local input if no remote event arrives within this window.
REMOTE_TIMEOUT_S = 1.0

MOUSE_BUTTON_LEFT = 0

# Release remote-held keys if the browser goes quiet (e.g. the tab lost focus mid-press).
# Held keys are kept alive by the browser's auto-repeat keydowns.
KEY_HOLD_TIMEOUT_S = 1.0
# Most characters a single frame will accept, so a large paste can't stall the UI.
MAX_PENDING_CHARS = 512

# Browser KeyboardEvent.key -> raylib key name (KEY_<name>)
BROWSER_KEY_NAMES = {
  "Enter": "ENTER",
  "Escape": "ESCAPE",
  "Backspace": "BACKSPACE",
  "Tab": "TAB",
  "Delete": "DELETE",
  "ArrowLeft": "LEFT",
  "ArrowRight": "RIGHT",
  "ArrowUp": "UP",
  "ArrowDown": "DOWN",
  "Home": "HOME",
  "End": "END",
  "PageUp": "PAGE_UP",
  "PageDown": "PAGE_DOWN",
  " ": "SPACE",
}


def browser_key_to_raylib(key) -> int:
  """Map a browser KeyboardEvent.key to a raylib key code, 0 if unmapped."""
  if not isinstance(key, str):
    return 0
  name = BROWSER_KEY_NAMES.get(key)
  if name is None and len(key) == 1 and key.isascii() and key.isalnum():
    name = key.upper()  # raylib's KEY_A..KEY_Z and KEY_ZERO..KEY_NINE are their ASCII codes
    return ord(name)
  return int(getattr(pr, f"KEY_{name}", 0)) if name else 0


class TouchInjector:
  def __init__(self, input_blocked=None):
    # Optional callable; while it returns True remote input is dropped and
    # local touch stays in control (e.g. while engaged).
    self._input_blocked = input_blocked or (lambda: False)
    self.running = False
    self.thread = None
    self._lock = threading.Lock()

    self._last_msg_time = 0.0
    self._x = 0
    self._y = 0
    self._down = False
    self._down_until = None
    self._need_release = False
    self._pressed_consumed = True
    self._wheel = 0.0

    # Keyboard: events since the last end_frame() ...
    self._key_last_msg_time = 0.0
    self._held_keys: set[int] = set()
    self._pending_presses: list[int] = []
    self._pending_releases: set[int] = set()
    self._pending_chars: list[int] = []
    # ... and what the UI sees during the current frame.
    self._frame_key_queue: deque[int] = deque()
    self._frame_pressed: set[int] = set()
    self._frame_released: set[int] = set()
    self._frame_char_queue: deque[int] = deque()

    # Keep references to the genuine pyray functions for local fallback.
    self._orig_get_touch_position = pr.get_touch_position
    self._orig_get_mouse_position = pr.get_mouse_position
    self._orig_is_mouse_button_down = pr.is_mouse_button_down
    self._orig_is_mouse_button_pressed = pr.is_mouse_button_pressed  # noqa: TID251
    self._orig_is_mouse_button_released = pr.is_mouse_button_released  # noqa: TID251
    self._orig_get_mouse_wheel_move = pr.get_mouse_wheel_move
    self._orig_get_key_pressed = pr.get_key_pressed
    self._orig_get_char_pressed = pr.get_char_pressed
    self._orig_is_key_pressed = pr.is_key_pressed
    self._orig_is_key_down = pr.is_key_down
    self._orig_is_key_released = pr.is_key_released
    self._orig_is_key_up = pr.is_key_up

    self._setup_socket()
    self._apply_hooks()

  # --- socket ------------------------------------------------------------

  def _setup_socket(self):
    if os.path.exists(SOCKET_PATH):
      os.remove(SOCKET_PATH)
    self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    self.server.bind(SOCKET_PATH)
    self.server.listen(5)
    self.server.setblocking(False)
    print(f"TouchInjector: listening on {SOCKET_PATH}")

  def start(self):
    self.running = True
    self.thread = threading.Thread(target=self._accept_loop, daemon=True)
    self.thread.start()

  def stop(self):
    self.running = False
    if self.thread is not None:
      self.thread.join(timeout=2.0)
    try:
      self.server.close()
    finally:
      if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)

  def _accept_loop(self):
    clients: dict[socket.socket, bytearray] = {}
    try:
      while self.running:
        # 1s timeout so we can notice self.running going False.
        ready, _, _ = select.select([self.server, *clients], [], [], 1.0)
        for s in ready:
          if s is self.server:
            try:
              client, _ = self.server.accept()
            except OSError:
              continue
            client.setblocking(False)
            clients[client] = bytearray()
            continue

          try:
            data = s.recv(4096)
          except BlockingIOError:
            continue
          except OSError:
            data = b""

          buf = clients[s]
          if data:
            buf.extend(data)
            *lines, rest = buf.split(b"\n")
            clients[s] = bytearray(rest)
            for line in lines:
              if line.strip():
                self._process_message(bytes(line))
          else:
            # EOF: a legacy one-shot client sends a single object without a newline.
            if buf.strip():
              self._process_message(bytes(buf))
            del clients[s]
            s.close()
    finally:
      for client in clients:
        client.close()

  def _process_message(self, raw):
    try:
      msg = json.loads(raw.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
      return

    if not isinstance(msg, dict):
      return

    msg_type = msg.get("type", "click")
    now = time.monotonic()
    if self._is_blocked():
      return

    if msg_type in ("keydown", "keyup", "keytap", "text"):
      # Keyboard events leave the pointer alone, so they don't take over local touch.
      with self._lock:
        self._process_key_message(msg_type, msg, now)
      return

    with self._lock:
      self._last_msg_time = now
      if "x" in msg and "y" in msg:
        self._x = int(msg["x"])
        self._y = int(msg["y"])

      if msg_type in ("click", "tap", "touch"):
        # Instantaneous tap: press now, auto-release shortly after.
        self._begin_press(now, hold=True)
      elif msg_type in ("mousedown", "touchstart"):
        self._begin_press(now, hold=False)
      elif msg_type in ("mousemove", "touchmove", "drag"):
        # Position already updated above; keep button state as-is.
        pass
      elif msg_type in ("mouseup", "touchend", "dragend"):
        self._release()
      elif msg_type == "scroll":
        # Positive deltaY scrolls down in the browser; raylib's wheel
        # move is positive up, so invert.
        self._wheel += -float(msg.get("deltaY", 0)) / 100.0

  def _process_key_message(self, msg_type, msg, now):
    self._key_last_msg_time = now
    if msg_type == "text":
      text = msg.get("text")
      if isinstance(text, str):
        self._queue_chars(text)
      return

    key = msg.get("key")
    code = browser_key_to_raylib(key)
    if msg_type in ("keydown", "keytap"):
      if msg.get("repeat"):
        # Auto-repeat just keeps the key held; the UI does its own repeat via is_key_down.
        return
      if isinstance(key, str) and len(key) == 1:
        self._queue_chars(key)
      if code:
        self._pending_presses.append(code)
        self._held_keys.add(code)
    if code and msg_type in ("keyup", "keytap"):
      self._pending_releases.add(code)

  def _queue_chars(self, text):
    room = MAX_PENDING_CHARS - len(self._pending_chars)
    self._pending_chars.extend(ord(c) for c in text[:max(0, room)])

  def end_frame(self):
    """Publish keyboard events received since the last call. Call once per rendered frame."""
    now = time.monotonic()
    with self._lock:
      if self._held_keys and (now - self._key_last_msg_time) >= KEY_HOLD_TIMEOUT_S:
        self._pending_releases |= self._held_keys

      pressed = self._pending_presses
      # A key pressed and released within one frame stays down for that frame, released on the next.
      released = self._pending_releases - set(pressed)
      self._pending_presses = []
      self._pending_releases -= released
      self._held_keys -= released

      self._frame_key_queue = deque(pressed)
      self._frame_pressed = set(pressed)
      self._frame_released = released
      self._frame_char_queue = deque(self._pending_chars)
      self._pending_chars = []

  def _begin_press(self, now, hold):
    if not self._down:
      self._pressed_consumed = False  # arm a rising edge
    self._down = True
    self._down_until = (now + CLICK_HOLD_S) if hold else None

  def _release(self):
    if self._down:
      self._need_release = True  # arm a falling edge
    self._down = False
    self._down_until = None

  def _refresh(self, now):
    """Advance the tap auto-release timer."""
    if self._down and self._down_until is not None and now >= self._down_until:
      self._release()

  def refresh_blocked(self):
    """Called once per frame so a press in progress is dropped as soon as the gate closes."""
    self._is_blocked()

  def _is_blocked(self):
    try:
      blocked = bool(self._input_blocked())
    except Exception:
      blocked = False
    if blocked:
      with self._lock:
        self._drop_remote_state()
    return blocked

  def _drop_remote_state(self):
    # Hand control straight back to local input and forget any held press.
    self._last_msg_time = 0.0
    self._down = False
    self._down_until = None
    self._need_release = False
    self._pressed_consumed = True
    self._wheel = 0.0
    self._held_keys.clear()
    self._pending_presses.clear()
    self._pending_releases.clear()
    self._pending_chars.clear()
    self._frame_key_queue.clear()
    self._frame_pressed.clear()
    self._frame_released.clear()
    self._frame_char_queue.clear()

  def _remote_active(self, now):
    return (now - self._last_msg_time) < REMOTE_TIMEOUT_S

  def _hook_get_touch_position(self, slot):
    now = time.monotonic()
    with self._lock:
      if self._remote_active(now):
        if slot == MOUSE_BUTTON_LEFT:
          return pr.Vector2(float(self._x), float(self._y))
        # No synthetic second touch point for remote input.
        return pr.Vector2(-1.0, -1.0)
    return self._orig_get_touch_position(slot)

  def _hook_get_mouse_position(self):
    now = time.monotonic()
    with self._lock:
      if self._remote_active(now):
        return pr.Vector2(float(self._x), float(self._y))
    return self._orig_get_mouse_position()

  def _hook_is_mouse_button_down(self, button):
    now = time.monotonic()
    with self._lock:
      if self._remote_active(now):
        self._refresh(now)
        if button == MOUSE_BUTTON_LEFT:
          return self._down
        return False
    return self._orig_is_mouse_button_down(button)

  def _hook_is_mouse_button_pressed(self, button):
    now = time.monotonic()
    with self._lock:
      if self._remote_active(now):
        self._refresh(now)
        if button == MOUSE_BUTTON_LEFT and self._down and not self._pressed_consumed:
          self._pressed_consumed = True
          return True
        return False
    return self._orig_is_mouse_button_pressed(button)

  def _hook_is_mouse_button_released(self, button):
    now = time.monotonic()
    with self._lock:
      if self._remote_active(now):
        self._refresh(now)
        if button == MOUSE_BUTTON_LEFT and self._need_release:
          self._need_release = False
          return True
        return False
    return self._orig_is_mouse_button_released(button)

  def _hook_get_mouse_wheel_move(self):
    now = time.monotonic()
    with self._lock:
      if self._remote_active(now) and self._wheel != 0.0:
        delta = self._wheel
        self._wheel = 0.0
        return delta
    return self._orig_get_mouse_wheel_move()

  # Keyboard hooks: remote keys are merged with local ones (the device has no keyboard,
  # but a PC running the UI does).

  def _hook_get_key_pressed(self):
    with self._lock:
      if self._frame_key_queue:
        return self._frame_key_queue.popleft()
    return self._orig_get_key_pressed()

  def _hook_get_char_pressed(self):
    with self._lock:
      if self._frame_char_queue:
        return self._frame_char_queue.popleft()
    return self._orig_get_char_pressed()

  def _hook_is_key_pressed(self, key):
    with self._lock:
      if key in self._frame_pressed:
        return True
    return self._orig_is_key_pressed(key)

  def _hook_is_key_down(self, key):
    with self._lock:
      if key in self._held_keys:
        return True
    return self._orig_is_key_down(key)

  def _hook_is_key_released(self, key):
    with self._lock:
      if key in self._frame_released:
        return True
    return self._orig_is_key_released(key)

  def _hook_is_key_up(self, key):
    with self._lock:
      if key in self._held_keys:
        return False
    return self._orig_is_key_up(key)

  def _apply_hooks(self):
    print("TouchInjector: hooking pyray input functions")
    pr.get_touch_position = self._hook_get_touch_position
    pr.get_mouse_position = self._hook_get_mouse_position
    pr.is_mouse_button_down = self._hook_is_mouse_button_down
    pr.is_mouse_button_pressed = self._hook_is_mouse_button_pressed  # noqa: TID251
    pr.is_mouse_button_released = self._hook_is_mouse_button_released  # noqa: TID251
    pr.get_mouse_wheel_move = self._hook_get_mouse_wheel_move
    pr.get_key_pressed = self._hook_get_key_pressed
    pr.get_char_pressed = self._hook_get_char_pressed
    pr.is_key_pressed = self._hook_is_key_pressed
    pr.is_key_down = self._hook_is_key_down
    pr.is_key_released = self._hook_is_key_released
    pr.is_key_up = self._hook_is_key_up
