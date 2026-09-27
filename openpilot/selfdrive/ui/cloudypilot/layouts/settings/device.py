from openpilot.selfdrive.ui.sunnypilot.layouts.settings.device import DeviceLayoutSP
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import dual_button_item_sp
from openpilot.system.ui.cloudypilot.widgets.list_view import LineSeparatorCP


class DeviceLayoutCP(DeviceLayoutSP):
  def __init__(self):
    super().__init__()

  def _initialize_items(self):
    items = super()._initialize_items()

    # Using dual button with no right button for better alignment
    self._soft_reboot_btn = dual_button_item_sp(
      left_text=lambda: tr("Soft Reboot"),
      left_callback=self._soft_reboot_prompt,
      right_text="",
      right_callback=None
    )
    self._soft_reboot_btn.action_item.right_button.set_visible(False)

    # Place above the separator preceding the power buttons
    idx = items.index(self._power_buttons) - 1
    items[idx:idx] = [LineSeparatorCP(), self._soft_reboot_btn]
    return items
