import pyray as rl
from openpilot.selfdrive.ui.cloudypilot.widgets.card import CARD_COLOR, CARD_PADDING, HEADER_FONT_SIZE, ROW_SPACING, VALUE_COLOR, render_divider
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import FontWeight, gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.label import gui_label
from openpilot.system.ui.sunnypilot.widgets.toggle import ToggleSP as Toggle
from openpilot.system.ui.sunnypilot.lib.styles import style
if gui_app.cloudypilot_ui():
  from openpilot.system.ui.cloudypilot.lib.styles import style

LABEL_FONT_SIZE = 44
ROW_HEIGHT = 100


def _param_toggle(param: str) -> Toggle:
  return Toggle(ui_state.params.get_bool(param), callback=lambda state: ui_state.params.put_bool(param, state, block=True))


class QuickTogglesWidget(Widget):
  def __init__(self):
    super().__init__()
    self._enabled_toggle = Toggle(ui_state.params.get_bool("OpenpilotEnabledToggle"), callback=self._on_enabled_toggled)
    self._remote_ui_toggle = _param_toggle("EnableRemoteUI")
    self._icbm_toggle = _param_toggle("IntelligentCruiseButtonManagement")
    self._rows = (
      (lambda: tr("Enable cloudypilot"), "OpenpilotEnabledToggle", self._enabled_toggle),
      (lambda: tr("Remote UI"), "EnableRemoteUI", self._remote_ui_toggle),
      (lambda: tr("ICBM"), "IntelligentCruiseButtonManagement", self._icbm_toggle),
    )

  @staticmethod
  def _on_enabled_toggled(state: bool):
    ui_state.params.put_bool("OpenpilotEnabledToggle", state, block=True)
    ui_state.params.put_bool("OnroadCycleRequested", True, block=True)

  @staticmethod
  def _icbm_available() -> bool:
    # mirrors the Cruise panel: ICBM only applies when the car supports it and cloudypilot isn't doing longitudinal
    cp_sp = ui_state.CP_SP
    return cp_sp is not None and cp_sp.intelligentCruiseButtonManagementAvailable and not ui_state.has_longitudinal_control

  def _render(self, rect: rl.Rectangle):
    rl.draw_rectangle_rounded(rect, 0.04, 20, CARD_COLOR)

    x = rect.x + CARD_PADDING
    w = rect.width - 2 * CARD_PADDING
    content_h = HEADER_FONT_SIZE + ROW_SPACING + ROW_HEIGHT * len(self._rows) + ROW_SPACING * (len(self._rows) - 1)
    y = rect.y + (rect.height - content_h) / 2

    y += ROW_SPACING + 2

    icbm_available = self._icbm_available()
    for i, (title, param, toggle) in enumerate(self._rows):
      if i > 0:
        y = render_divider(x, y, w)
      available = icbm_available if toggle is self._icbm_toggle else True
      toggle.set_enabled(available)
      toggle.set_state(available and ui_state.params.get_bool(param))

      label = title() if available else f"{title()} ({tr('Unavailable')})"
      gui_label(rl.Rectangle(x, y, w - style.TOGGLE_WIDTH - ROW_SPACING, ROW_HEIGHT), label, LABEL_FONT_SIZE,
                rl.WHITE if available else VALUE_COLOR)
      toggle.render(rl.Rectangle(x + w - style.TOGGLE_WIDTH, y + (ROW_HEIGHT - style.TOGGLE_BG_HEIGHT + style.ITEM_PADDING) / 2,
                                 style.TOGGLE_WIDTH, style.TOGGLE_HEIGHT))
      y += ROW_HEIGHT
