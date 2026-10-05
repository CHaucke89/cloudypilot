from openpilot.selfdrive.ui.sunnypilot.layouts.settings.steering_sub_layouts.lane_change_settings import LaneChangeSettingsLayout
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp, LineSeparatorSP


class LaneChangeSettingsLayoutCP(LaneChangeSettingsLayout):
  def __init__(self, back_btn_callback):
    super().__init__(back_btn_callback)

  def _initialize_items(self):
    items = super()._initialize_items()

    self._always_on_bsm = toggle_item_sp(
      param="AlwaysOnBsm",
      title=lambda: tr("Blind Spot Audible Alert"),
      description=lambda: tr("Play an audible alert when a vehicle is detected in the blind spot while the blinker is on, \
                              even if lateral control is inactive."),
    )

    items.insert(items.index(self._bsm_delay) + 1, [LineSeparatorSP(40), self._always_on_bsm])
    return items
