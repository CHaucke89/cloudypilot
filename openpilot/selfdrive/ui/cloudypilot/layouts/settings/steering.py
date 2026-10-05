
from openpilot.selfdrive.ui.cloudypilot.layouts.settings.steering_sub_layouts.lane_change_settings import LaneChangeSettingsLayoutCP
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.steering import PanelType, SteeringLayout
from openpilot.system.ui.cloudypilot.widgets.list_view import LineSeparatorCP, option_item_cp
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp


class SteeringLayoutCP(SteeringLayout):
  def __init__(self):
    super().__init__()
    self._lane_change_settings_layout = LaneChangeSettingsLayoutCP(lambda: self._set_current_panel(PanelType.STEERING))

  def _initialize_items(self):
    items = super()._initialize_items()

    self._sr_toggle = toggle_item_sp(
      param="UseCustomSR",
      title=lambda: tr("Enable Custom Steer Ratio"),
      description="",
    )

    self._custom_sr = option_item_cp(
      param="CustomSR",
      title=lambda: tr("Custom Steer Ratio"),
      min_value=1000,
      max_value=2000,
      value_change_step=5,
      use_float_scaling=True,
      description=lambda: tr("Current learned steer ratio: ") + (
                          f"{ui_state.CP.steerRatio:.2f}" if ui_state.CP is not None else tr("unknown")
      ),
      label_callback=lambda sr: f'{sr / 100.0:.2f}',
      reset_enabled=True,
    )

    items += [
      self._sr_toggle,
      self._custom_sr,
      LineSeparatorCP(40),
    ]
    return items

  def _update_state(self):
    super()._update_state()

    self._sr_toggle.action_item.set_enabled(True)
    self._custom_sr.set_visible(self._sr_toggle.action_item.get_state())
