import pyray as rl
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app, FontWeight, FONT_SCALE
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.lib.wrap_text import wrap_text
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.button import Button, ButtonStyle
from openpilot.system.ui.widgets.label import Label


class ModelWidget(Widget):
  def __init__(self):
    super().__init__()
    self._open_models_callback = None
    self._open_models_btn = Button(lambda: tr("Select"), lambda: self._open_models_callback() if self._open_models_callback else None,
                                   button_style=ButtonStyle.PRIMARY)
    self._title_label = Label(lambda: tr("Active Model"), font_weight=FontWeight.MEDIUM, font_size=64)

  def set_open_models_callback(self, callback):
    self._open_models_callback = callback

  def _render(self, rect: rl.Rectangle):
    rl.draw_rectangle_rounded(rl.Rectangle(rect.x, rect.y, rect.width, 425), 0.04, 20, rl.Color(51, 51, 51, 255))

    x = rect.x + 56
    y = rect.y + 40
    w = rect.width - 112
    spacing = 42

    self._title_label.render(rl.Rectangle(rect.x, y, rect.width, 64))
    y += 64 + spacing

    model_manager = ui_state.sm["modelManagerSP"] if "modelManagerSP" in ui_state.sm.services else None
    if model_manager and model_manager.activeBundle.ref:
      active_name = model_manager.activeBundle.displayName
    else:
      active_name = tr("Default Model")

    desc_font = gui_app.font(FontWeight.NORMAL)
    wrapped_desc = wrap_text(desc_font, active_name, 40, int(w))

    for line in wrapped_desc:
      rl.draw_text_ex(desc_font, line, rl.Vector2(x, y), 40, 0, rl.WHITE)
      y += 40 * FONT_SCALE

    y += spacing

    button_height = 48 + 64
    button_rect = rl.Rectangle(x, y, w, button_height)
    self._open_models_btn.render(button_rect)
