
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.steering import SteeringLayout
from openpilot.system.ui.cloudypilot.widgets.list_view import LineSeparatorCP
from openpilot.system.ui.cloudypilot.widgets.list_view import option_item_cp



class SteeringLayoutCP(SteeringLayout):
  def __init__(self):
    super().__init__()

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
      description=lambda: tr("Set a custom steer ratio value."),
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
