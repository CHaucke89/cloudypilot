from openpilot.selfdrive.ui.sunnypilot.layouts.settings.device import DeviceLayoutSP
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import dual_button_item_sp
from openpilot.system.ui.cloudypilot.widgets.list_view import LineSeparatorCP, option_item_cp


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

    self._low_voltage_shutdown = option_item_cp(
      title=lambda: tr("Minimum Battery Voltage"),
      description=lambda: tr("Device will automatically shutdown if the car battery reaches the set voltage.\n(11.8V is the default)"),
      param="CustomShutdownVoltage",
      min_value=1170,
      max_value=1280,
      value_change_step=10,
      on_value_changed=None,
      enabled=True,
      icon="",
      value_map=None,
      label_width=360,
      use_float_scaling=True,
      inline=True,
      label_callback=self._update_low_voltage_shutdown_label,
      reset_enabled=True,
    )

    # Place above the separator preceding the power buttons
    power_idx = items.index(self._power_buttons) - 1
    items[power_idx:power_idx] = [LineSeparatorCP(), self._soft_reboot_btn]

    # Place below the separator beneath max time offroad
    time_offroad_idx = items.index(self._max_time_offroad) + 1
    items[time_offroad_idx:time_offroad_idx] = [LineSeparatorCP(), self._low_voltage_shutdown]
    return items

  @staticmethod
  def _update_low_voltage_shutdown_label(value: int) -> str:
    label = tr("Disabled") if value == 1170 else f"{value / 100}" + tr("V")
    label += tr(" (Default)") if value == 1180 else ""
    return label
