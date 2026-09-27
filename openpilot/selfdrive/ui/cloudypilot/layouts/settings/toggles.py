from openpilot.selfdrive.ui.layouts.settings.toggles import TogglesLayout
from openpilot.system.ui.lib.multilang import tr, tr_noop

DESCRIPTIONS_CP = {
  "AlwaysOffDM": tr_noop("Disable driver monitoring even when cloudypilot is engaged."),
}


class TogglesLayoutCP(TogglesLayout):
  def __init__(self):
    super().__init__()

  def _initialize_items(self):
    items = super()._initialize_items()

    param = "AlwaysOffDM"
    self._toggle_defs[param] = (
      lambda: tr("Always-Off Driver Monitoring"),
      DESCRIPTIONS_CP[param],
      "monitoring.png",
      False,
    )
    toggle = self._build_toggle(param, *self._toggle_defs[param])

    items.insert(items.index(self._toggles["AlwaysOnDM"]) + 1, toggle)
    return items
