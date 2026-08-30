"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import math
import os
import time
from enum import IntEnum

import pyray as rl

from openpilot.common.hardware import HARDWARE
from openpilot.common.params import Params
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget


class ScreenSaverAnimation(IntEnum):
  BOUNCE = 0
  DROP = 1
  BOUNCE_ROTATE = 2


class ScreenSaverSP(Widget):
  def __init__(self, params: Params | None = None):
    super().__init__()
    self.set_rect(rl.Rectangle(0, 0, gui_app.width, gui_app.height))
    self._params = params or Params()
    self._is_mici = HARDWARE.get_device_type() == 'mici' or (HARDWARE.get_device_type() == "pc" and os.getenv("BIG") != "1")

    self.x = 0.0
    self.y = 100.0
    self.vx = 120.0 if self._is_mici else 300.0
    self.vy = 70.0 if self._is_mici else 200.0
    self.color = self._pick_orange_shade()

    self.text = "cloudypilot"
    self.font_size = 50 if self._is_mici else 100
    self._start_time = None
    self._dismiss = False
    self._screensaver_timeout = 300
    self._animation = ScreenSaverAnimation.BOUNCE
    self._hit_last_frame = False
    self._needs_new_drop = True
    self.rotation = 0.0
    self._rotation_speed = 45.0 if self._is_mici else 90.0

  @property
  def is_active(self) -> bool:
    return self._start_time is not None and not self._dismiss

  @property
  def was_dismissed(self) -> bool:
    return self._dismiss

  def initialize(self):
    self._screensaver_timeout = self._params.get("ScreenSaverTimeout", return_default=True)
    self._animation = int(self._params.get("ScreenSaverAnimation", return_default=True))
    if self._start_time is None:
      self._start_time = time.monotonic()
    self._dismiss = False

  def hide_event(self):
    super().hide_event()
    self._dismiss = False
    self._start_time = None

  def _handle_mouse_release(self, mouse_pos):
    self._dismiss = True
    self._start_time = None
    gui_app.pop_widget()
    return super()._handle_mouse_release(mouse_pos)

  def _pick_orange_shade(self):
    hue = rl.get_random_value(20, 40)
    saturation = rl.get_random_value(70, 100) / 100.0
    value = rl.get_random_value(70, 100) / 100.0
    return rl.color_from_hsv(hue, saturation, value)

  def _update_state(self):
    super()._update_state()

    self.font = gui_app.font(FontWeight.AUDIOWIDE)
    text_size = measure_text_cached(self.font, self.text, self.font_size, 0)
    self.logo_width = text_size.x
    self.logo_height = text_size.y

    if self._start_time and time.monotonic() - self._start_time > self._screensaver_timeout:
      self._dismiss = True
      self._start_time = None

    dt = rl.get_frame_time()

    if self._animation in (ScreenSaverAnimation.BOUNCE, ScreenSaverAnimation.BOUNCE_ROTATE):
      self._update_bounce(dt)
      if self._animation == ScreenSaverAnimation.BOUNCE_ROTATE:
        self.rotation = (self.rotation + self._rotation_speed * dt) % 360
    else:
      self._update_drop(dt)

  def _update_bounce(self, dt: float):
    self.x += self.vx * dt
    self.y += self.vy * dt

    hit_x = hit_y = False

    if self._animation == ScreenSaverAnimation.BOUNCE_ROTATE:
      # For rotating text, use diagonal distance from center to corner to keep it fully on-screen
      half_diagonal = math.sqrt((self.logo_width / 2) ** 2 + (self.logo_height / 2) ** 2)
      center_x = self.x + self.logo_width / 2
      center_y = self.y + self.logo_height / 2

      if center_x + half_diagonal > self.rect.width:
        self.vx *= -1
        center_x = self.rect.width - half_diagonal
        hit_x = True
      elif center_x - half_diagonal < 0:
        self.vx *= -1
        center_x = half_diagonal
        hit_x = True

      if center_y + half_diagonal > self.rect.height:
        self.vy *= -1
        center_y = self.rect.height - half_diagonal
        hit_y = True
      elif center_y - half_diagonal < 0:
        self.vy *= -1
        center_y = half_diagonal
        hit_y = True

      # Convert back to top-left corner position
      self.x = center_x - self.logo_width / 2
      self.y = center_y - self.logo_height / 2
    else:
      # Regular bounce for non-rotating animations
      if self.x + self.logo_width > self.rect.width:
        self.vx *= -1
        self.x = self.rect.width - self.logo_width
        hit_x = True
      elif self.x < 0:
        self.vx *= -1
        self.x = 0
        hit_x = True

      if self.y + self.logo_height > self.rect.height:
        self.vy *= -1
        self.y = self.rect.height - self.logo_height
        hit_y = True
      elif self.y < 0:
        self.vy *= -1
        self.y = 0
        hit_y = True

    hit = hit_x or hit_y
    if hit and not self._hit_last_frame:
      self.color = self._pick_orange_shade()
    self._hit_last_frame = hit

  def _update_drop(self, dt: float):
    if self._needs_new_drop:
      max_x = max(int(self.rect.width - self.logo_width), 0)
      self.x = float(rl.get_random_value(0, max_x))
      self.y = -self.logo_height
      self.color = self._pick_orange_shade()
      self._needs_new_drop = False

    self.y += self.vy * dt

    if self.y > self.rect.height:
      self._needs_new_drop = True

  def _render(self, rect: rl.Rectangle):
    self.set_rect(rect)
    rl.clear_background(rl.BLACK)

    if self._animation == ScreenSaverAnimation.BOUNCE_ROTATE:
      origin = rl.Vector2(self.logo_width / 2, self.logo_height / 2)
      center = rl.Vector2(int(self.x) + self.logo_width / 2, int(self.y) + self.logo_height / 2)
      rl.draw_text_pro(self.font, self.text, center, origin, self.rotation, self.font_size, 0, self.color)
    else:
      rl.draw_text_ex(self.font, self.text, rl.Vector2(int(self.x), int(self.y)), self.font_size, 0, self.color)
    return -1
