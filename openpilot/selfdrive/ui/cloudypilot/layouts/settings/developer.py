
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.developer import DeveloperLayoutSP
from openpilot.system.ui.lib.multilang import tr

from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp



class DeveloperLayoutCP(DeveloperLayoutSP):
  def __init__(self):
    super().__init__()

  def _initialize_items(self):
    super()._initialize_items()
    self.permalatch = toggle_item_sp(tr("PermaLatch"), tr("Permanently latch the driver seatbelt."), param="PermaLatch")
    self.items.append(self.permalatch)

  def _update_state(self):
    super()._update_state()

    self.permalatch.set_visible(True)
