import json
import os
import tempfile
import time
from unittest import mock

import pyray as pr

from openpilot.common.test import OpenpilotTestCase
from openpilot.cloudypilot.selfdrive.ui import touch_injector
from openpilot.cloudypilot.selfdrive.ui.touch_injector import CLICK_HOLD_S, MOUSE_BUTTON_LEFT, TouchInjector

HOOKED = ("get_touch_position", "get_mouse_position", "is_mouse_button_down", "is_mouse_button_pressed",
          "is_mouse_button_released", "get_mouse_wheel_move", "get_key_pressed", "get_char_pressed",
          "is_key_pressed", "is_key_down", "is_key_released", "is_key_up")


class TestTouchInjector(OpenpilotTestCase):
  def setUp(self):
    self._saved = {name: getattr(pr, name) for name in HOOKED}
    self._tmp = tempfile.TemporaryDirectory()
    with mock.patch.object(touch_injector, "SOCKET_PATH", os.path.join(self._tmp.name, "touch")):
      self.injector = TouchInjector()

  def tearDown(self):
    self.injector.server.close()
    for name, fn in self._saved.items():
      setattr(pr, name, fn)
    self._tmp.cleanup()

  def _send(self, **msg):
    self.injector._process_message(json.dumps(msg).encode())

  def _poll(self):
    return (pr.is_mouse_button_pressed(MOUSE_BUTTON_LEFT),  # noqa: TID251
            pr.is_mouse_button_released(MOUSE_BUTTON_LEFT),  # noqa: TID251
            pr.is_mouse_button_down(MOUSE_BUTTON_LEFT))

  def test_down_up_between_polls_still_clicks(self):
    self._send(type="mousedown", x=10, y=20)
    self._send(type="mouseup", x=10, y=20)
    self.assertEqual(self._poll(), (True, False, True))
    time.sleep(CLICK_HOLD_S + 0.02)
    self.assertEqual(self._poll(), (False, True, False))
    self.assertEqual(self._poll(), (False, False, False))

  def test_up_after_polled_press_releases_immediately(self):
    self._send(type="mousedown", x=10, y=20)
    self.assertEqual(self._poll(), (True, False, True))
    self._send(type="mouseup", x=10, y=20)
    self.assertEqual(self._poll(), (False, True, False))
