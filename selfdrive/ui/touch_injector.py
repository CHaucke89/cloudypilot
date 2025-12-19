import os
import socket
import json
import threading
import time
import pyray as rl

SOCKET_PATH = "/tmp/ui_touch_socket"

class TouchInjector:
    def __init__(self):
        self.running = True
        self.thread = None

        self.remote_active = False
        self.last_msg_time = 0
        self.remote_x = 0
        self.remote_y = 0
        self.remote_down = False

        self.orig_get_mouse_position = rl.get_mouse_position
        self.orig_is_mouse_button_down = rl.is_mouse_button_down
        self.orig_is_mouse_button_pressed = rl.is_mouse_button_pressed
        self.orig_is_mouse_button_released = rl.is_mouse_button_released


        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)

        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(SOCKET_PATH)
        self.server.setblocking(False)

        self._apply_hooks()

    def start(self):
        self.thread = threading.Thread(target=self._socket_loop, daemon=True)
        self.thread.start()

    def _socket_loop(self):
        while self.running:
            try:
                data, _ = self.server.recvfrom(4096)
                self._process_message(data)
            except BlockingIOError:
                time.sleep(0.01)
            except Exception as e:
                print(f"TouchInjector Error: {e}")
                break

    def _process_message(self, data):
        try:
            msg = json.loads(data.decode('utf-8'))
            self.last_msg_time = time.monotonic()
            self.remote_active = True

            if 'x' in msg and 'y' in msg:
                self.remote_x = int(msg['x'])
                self.remote_y = int(msg['y'])

            msg_type = msg.get('type')

            if msg_type in ['touchstart', 'touchmove', 'mousedown', 'mousemove']:
                self.remote_down = True
            elif msg_type in ['touchend', 'mouseup']:
                self.remote_down = False

        except json.JSONDecodeError:
            pass

    def _is_remote_valid(self):
        return self.remote_active and (time.monotonic() - self.last_msg_time < 1.0)

    # --- Hook Functions ---

    def _hook_get_mouse_position(self):
        if self._is_remote_valid():
            vec = rl.Vector2(self.remote_x, self.remote_y)
            return vec
        return self.orig_get_mouse_position()

    def _hook_is_mouse_button_down(self, button):
        if self._is_remote_valid():
            # Assume Left Mouse (0) for all touch interactions
            if button == 0:
                return self.remote_down
        return self.orig_is_mouse_button_down(button)

    def _hook_is_mouse_button_pressed(self, button):
        if self._is_remote_valid() and button == 0:
            return self.remote_down
        return self.orig_is_mouse_button_pressed(button)

    def _apply_hooks(self):
        print("Hooking PyRay input functions for Remote UI...")
        rl.get_mouse_position = self._hook_get_mouse_position
        rl.is_mouse_button_down = self._hook_is_mouse_button_down
        rl.is_mouse_button_pressed = self._hook_is_mouse_button_pressed
