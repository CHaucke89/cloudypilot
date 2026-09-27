from openpilot.selfdrive.ui.sunnypilot.layouts.settings.visuals import VisualsLayout
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp


class VisualsLayoutCP(VisualsLayout):
  def __init__(self):
    super().__init__()

  def _initialize_items(self):
    items = super()._initialize_items()

    param = "TorqueBarFade"
    self._toggle_defs[param] = (
      lambda: tr("Steering Arc Fade"),
      tr("Enable or disable the fade at the bottom of the onroad screen with Steering Arc enabled."),
      None,
    )
    title, desc, callback = self._toggle_defs[param]
    self._toggles[param] = toggle_item_sp(
      title=title,
      description=desc,
      param=param,
      initial_state=ui_state.params.get_bool(param),
      callback=callback,
    )

    items.insert(items.index(self._toggles["TorqueBar"]) + 1, self._toggles[param])
    return items

  def _update_state(self):
    super()._update_state()

    self._toggles["TorqueBarFade"].set_visible(self._toggles["TorqueBar"].action_item.get_state())
