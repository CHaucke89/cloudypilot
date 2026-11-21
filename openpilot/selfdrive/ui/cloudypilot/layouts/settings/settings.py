from enum import IntEnum

from openpilot.selfdrive.ui.sunnypilot.layouts.settings import settings as SP
from openpilot.selfdrive.ui.cloudypilot.layouts.settings.developer import DeveloperLayoutCP
from openpilot.selfdrive.ui.cloudypilot.layouts.settings.device import DeviceLayoutCP
from openpilot.selfdrive.ui.cloudypilot.layouts.settings.display import DisplayLayoutCP
from openpilot.selfdrive.ui.cloudypilot.layouts.settings.models import ModelsLayoutCP
from openpilot.selfdrive.ui.cloudypilot.layouts.settings.personalize import PersonalizeLayout
from openpilot.selfdrive.ui.cloudypilot.layouts.settings.steering import SteeringLayoutCP
from openpilot.selfdrive.ui.cloudypilot.layouts.settings.visuals import VisualsLayoutCP
from openpilot.system.ui.lib.multilang import tr_noop

SP.OP.PanelType = IntEnum(  # type: ignore[assignment] # ty: ignore[invalid-assignment]
  "PanelType",
  [es.name for es in SP.OP.PanelType] + ["PERSONALIZE"],
  start=0,
)


class SettingsLayoutCP(SP.SettingsLayoutSP):
  def __init__(self):
    super().__init__()

    self._panels.pop(SP.OP.PanelType.FIREHOSE, None)

    panel_overrides = {
      SP.OP.PanelType.DEVICE: DeviceLayoutCP,
      SP.OP.PanelType.DEVELOPER: DeveloperLayoutCP,
      SP.OP.PanelType.DISPLAY: DisplayLayoutCP,
      SP.OP.PanelType.MODELS: ModelsLayoutCP,
      SP.OP.PanelType.STEERING: SteeringLayoutCP,
      SP.OP.PanelType.VISUALS: VisualsLayoutCP,
    }

    for panel_type, layout_cls in panel_overrides.items():
      panel_info = self._panels[panel_type]
      self._panels[panel_type] = SP.PanelInfo(panel_info.name, layout_cls(), icon=panel_info.icon)

    # Dict order is nav order, so rebuild it to slot Personalize in after Display
    panels = {}
    for panel_type, panel_info in self._panels.items():
      panels[panel_type] = panel_info
      if panel_type == SP.OP.PanelType.DISPLAY:
        panels[SP.OP.PanelType.PERSONALIZE] = SP.PanelInfo(tr_noop("Personalize"), PersonalizeLayout(), icon="icons/menu.png")
    self._panels = panels
