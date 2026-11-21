import pyray as rl
from openpilot.system.ui.lib.application import FontWeight
from openpilot.system.ui.widgets.button import Button
from openpilot.system.ui.widgets.label import gui_label

YELLOW = rl.Color(255, 204, 0, 255)
YELLOW_PRESSED = rl.Color(214, 170, 0, 255)
YELLOW_DISABLED = rl.Color(120, 100, 20, 255)
RED = rl.Color(255, 70, 70, 255)
RED_PRESSED = rl.Color(226, 44, 44, 255)
RED_DISABLED = rl.Color(120, 20, 20, 255)
GREEN = rl.Color(51, 171, 76, 255)
GREEN_PRESSED = rl.Color(40, 140, 62, 255)
GREEN_DISABLED = rl.Color(25, 85, 38, 255)
BUTTON_TEXT = rl.Color(20, 20, 20, 255)

CARD_COLOR = rl.Color(51, 51, 51, 255)
DIVIDER_COLOR = rl.Color(86, 86, 86, 255)
VALUE_COLOR = rl.Color(170, 170, 170, 255)
CARD_PADDING = 56
HEADER_FONT_SIZE = 48
VALUE_FONT_SIZE = 40
TEXT_SPACING = 8
ROW_SPACING = 24
BUTTON_SPACING = 24
BUTTON_HEIGHT = 96
ROW_BUTTON_WIDTH = 300
BUTTON_FONT_SIZE = 44


class YellowButton(Button):
  def _update_state(self):
    super()._update_state()
    if not self.enabled:
      self._background_color = YELLOW_DISABLED
    else:
      self._background_color = YELLOW_PRESSED if self.is_pressed else YELLOW
    self._label.set_text_color(BUTTON_TEXT)

class RedButton(Button):
  def _update_state(self):
    super()._update_state()
    if not self.enabled:
      self._background_color = RED_DISABLED
    else:
      self._background_color = RED_PRESSED if self.is_pressed else RED
    self._label.set_text_color(BUTTON_TEXT)

class GreenButton(Button):
  def _update_state(self):
    super()._update_state()
    if not self.enabled:
      self._background_color = GREEN_DISABLED
    else:
      self._background_color = GREEN_PRESSED if self.is_pressed else GREEN
    self._label.set_text_color(BUTTON_TEXT)


def render_row(x: float, y: float, w: float, header: str, value: str, button: Button, button_w: float = ROW_BUTTON_WIDTH) -> float:
  text_w = w - button_w - BUTTON_SPACING
  text_y = y + (BUTTON_HEIGHT - (HEADER_FONT_SIZE + TEXT_SPACING + VALUE_FONT_SIZE)) / 2
  gui_label(rl.Rectangle(x, text_y, text_w, HEADER_FONT_SIZE), header, HEADER_FONT_SIZE, rl.WHITE, FontWeight.MEDIUM)
  text_y += HEADER_FONT_SIZE + TEXT_SPACING
  gui_label(rl.Rectangle(x, text_y, text_w, VALUE_FONT_SIZE), value, VALUE_FONT_SIZE, VALUE_COLOR)
  button.render(rl.Rectangle(x + w - button_w, y, button_w, BUTTON_HEIGHT))
  return y + BUTTON_HEIGHT


def render_divider(x: float, y: float, w: float) -> float:
  y += ROW_SPACING / 2
  rl.draw_line_ex(rl.Vector2(x, y), rl.Vector2(x + w, y), 2, DIVIDER_COLOR)
  return y + ROW_SPACING / 2
