import pyray as rl
from openpilot.selfdrive.ui.cloudypilot.widgets.card import (BUTTON_FONT_SIZE, BUTTON_HEIGHT, BUTTON_SPACING, CARD_COLOR, CARD_PADDING, ROW_SPACING,
                                                              RedButton, YellowButton, render_divider, render_row)
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import DialogResult, Widget
from openpilot.system.ui.widgets.button import Button, ButtonStyle
from openpilot.system.ui.widgets.confirm_dialog import ConfirmDialog

OFFROAD_BUTTON_WIDTH = 220


def _confirm_param(prompt: str, confirm_text: str, param: str):
  def on_result(result: DialogResult):
    if result == DialogResult.CONFIRM:
      ui_state.params.put_bool(param, True, block=True)

  gui_app.push_widget(ConfirmDialog(prompt, confirm_text, callback=on_result))


class DeviceWidget(Widget):
  def __init__(self):
    super().__init__()
    self._enter_offroad_button = Button(lambda: tr("Enter"), lambda: ui_state.params.put_bool("OffroadMode", True),
                                        font_size=BUTTON_FONT_SIZE, button_style=ButtonStyle.PRIMARY)
    self._exit_offroad_button = Button(lambda: tr("Exit"), lambda: ui_state.params.put_bool("OffroadMode", False),
                                       font_size=BUTTON_FONT_SIZE, button_style=ButtonStyle.DANGER)
    self._soft_reboot_button = YellowButton(lambda: tr("Soft Reboot"),
                                            lambda: _confirm_param(tr("Are you sure you want to soft reboot?"), tr("Soft Reboot"), "DoSoftReboot"),
                                            font_size=BUTTON_FONT_SIZE, button_style=ButtonStyle.NORMAL)
    self._reboot_button = RedButton(lambda: tr("Reboot"),
                                    lambda: _confirm_param(tr("Are you sure you want to reboot?"), tr("Reboot"), "DoReboot"),
                                    font_size=BUTTON_FONT_SIZE, button_style=ButtonStyle.NORMAL)
    self._power_off_button = Button(lambda: tr("Power Off"),
                                    lambda: _confirm_param(tr("Are you sure you want to power off?"), tr("Power Off"), "DoShutdown"),
                                    font_size=BUTTON_FONT_SIZE, button_style=ButtonStyle.DANGER)

  def _render(self, rect: rl.Rectangle):
    rl.draw_rectangle_rounded(rect, 0.04, 20, CARD_COLOR)

    x = rect.x + CARD_PADDING
    w = rect.width - 2 * CARD_PADDING
    content_h = BUTTON_HEIGHT * 3 + ROW_SPACING * 2
    y = rect.y + (rect.height - content_h) / 2

    offroad = ui_state.params.get_bool("OffroadMode")
    offroad_button = self._exit_offroad_button if offroad else self._enter_offroad_button
    y = render_row(x, y, w, tr("Always Offroad"), tr("On") if offroad else tr("Off"), offroad_button, OFFROAD_BUTTON_WIDTH)
    y = render_divider(x, y, w)

    half_w = (w - BUTTON_SPACING) / 2
    self._soft_reboot_button.render(rl.Rectangle(x, y, half_w, BUTTON_HEIGHT))
    self._reboot_button.render(rl.Rectangle(x + half_w + BUTTON_SPACING, y, half_w, BUTTON_HEIGHT))
    y += BUTTON_HEIGHT + BUTTON_SPACING
    self._power_off_button.render(rl.Rectangle(x, y, w, BUTTON_HEIGHT))
