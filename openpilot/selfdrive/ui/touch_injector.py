"""Touch/mouse injector for the raylib/pyray openpilot UI.

Python port of the old Qt ``touch_injector.cc``. The Qt version received JSON
input events on a Unix socket and synthesised ``QMouseEvent``/``QWheelEvent``
objects. raylib has no event queue to post into: input is *polled* every frame
(``is_mouse_button_pressed`` etc.). So instead we monkeypatch pyray's input
functions to report remote state, falling back to the real functions when no
remote client is active.

Wire protocol matches ``stream_server.py`` exactly: a JSON object per
connection over a ``SOCK_STREAM`` Unix socket at ``/tmp/ui_touch_socket``, e.g.
``{"type": "click", "x": 100, "y": 200}``.
"""

import json
import os
import select
import socket
import threading
import time

import pyray as pr

SOCKET_PATH = "/tmp/ui_touch_socket"

# How long a synthetic "click"/"tap" is held down before releasing, so the UI
# sees a full press -> release cycle across polled frames.
CLICK_HOLD_S = 0.12
# Fall back to local input if no remote event arrives within this window.
REMOTE_TIMEOUT_S = 1.0

MOUSE_BUTTON_LEFT = 0


class TouchInjector:
    def __init__(self):
        self.running = False
        self.thread = None
        self._lock = threading.Lock()

        # Remote input state (guarded by _lock).
        self._last_msg_time = 0.0
        self._x = 0
        self._y = 0
        self._down = False
        self._down_until = None          # auto-release time for taps; None = held
        self._need_release = False       # pending falling edge for is_..._released
        self._pressed_consumed = True    # rising edge already reported?
        self._wheel = 0.0                # pending scroll delta

        # Keep references to the genuine pyray functions for local fallback.
        self._orig_get_mouse_position = pr.get_mouse_position
        self._orig_is_mouse_button_down = pr.is_mouse_button_down
        self._orig_is_mouse_button_pressed = pr.is_mouse_button_pressed
        self._orig_is_mouse_button_released = pr.is_mouse_button_released
        self._orig_get_mouse_wheel_move = pr.get_mouse_wheel_move

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
        while self.running:
            # 1s timeout so we can notice self.running going False.
            ready, _, _ = select.select([self.server], [], [], 1.0)
            if not ready:
                continue
            try:
                client, _ = self.server.accept()
            except OSError:
                continue
            try:
                chunks = []
                client.settimeout(0.5)
                while True:
                    data = client.recv(4096)
                    if not data:
                        break
                    chunks.append(data)
            except (socket.timeout, OSError):
                pass
            finally:
                client.close()
            if chunks:
                self._process_message(b"".join(chunks))

    def _process_message(self, raw):
        try:
            msg = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return

        msg_type = msg.get("type", "click")
        now = time.time()
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

    # --- state helpers (call with _lock held) ------------------------------

    def _refresh(self, now):
        """Advance the tap auto-release timer."""
        if self._down and self._down_until is not None and now >= self._down_until:
            self._release()

    def _remote_active(self, now):
        return (now - self._last_msg_time) < REMOTE_TIMEOUT_S

    # --- pyray hooks -------------------------------------------------------

    def _hook_get_mouse_position(self):
        now = time.time()
        with self._lock:
            if self._remote_active(now):
                return pr.Vector2(float(self._x), float(self._y))
        return self._orig_get_mouse_position()

    def _hook_is_mouse_button_down(self, button):
        now = time.time()
        with self._lock:
            if self._remote_active(now):
                self._refresh(now)
                if button == MOUSE_BUTTON_LEFT:
                    return self._down
                return False
        return self._orig_is_mouse_button_down(button)

    def _hook_is_mouse_button_pressed(self, button):
        now = time.time()
        with self._lock:
            if self._remote_active(now):
                self._refresh(now)
                if button == MOUSE_BUTTON_LEFT and self._down and not self._pressed_consumed:
                    self._pressed_consumed = True
                    return True
                return False
        return self._orig_is_mouse_button_pressed(button)

    def _hook_is_mouse_button_released(self, button):
        now = time.time()
        with self._lock:
            if self._remote_active(now):
                self._refresh(now)
                if button == MOUSE_BUTTON_LEFT and self._need_release:
                    self._need_release = False
                    return True
                return False
        return self._orig_is_mouse_button_released(button)

    def _hook_get_mouse_wheel_move(self):
        now = time.time()
        with self._lock:
            if self._remote_active(now) and self._wheel != 0.0:
                delta = self._wheel
                self._wheel = 0.0
                return delta
        return self._orig_get_mouse_wheel_move()

    def _apply_hooks(self):
        print("TouchInjector: hooking pyray input functions")
        pr.get_mouse_position = self._hook_get_mouse_position
        pr.is_mouse_button_down = self._hook_is_mouse_button_down
        pr.is_mouse_button_pressed = self._hook_is_mouse_button_pressed
        pr.is_mouse_button_released = self._hook_is_mouse_button_released
        pr.get_mouse_wheel_move = self._hook_get_mouse_wheel_move
