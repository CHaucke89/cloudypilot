from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.scroller_tici import Scroller


class PersonalizeLayout(Widget):
  def __init__(self):
    super().__init__()

    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=True, spacing=0)

  def _initialize_items(self):
    sidebar_toggles = [
      ("SidebarShowNetwork", lambda: tr("Sidebar: Network"), lambda: tr("Show the signal strength and connection type in the sidebar.")),
      ("SidebarShowTemp", lambda: tr("Sidebar: Temperature"), lambda: tr("Show the device temperature status in the sidebar.")),
      ("SidebarShowVehicle", lambda: tr("Sidebar: Vehicle"), lambda: tr("Show the vehicle (panda) connection status in the sidebar.")),
      ("SidebarShowConnect", lambda: tr("Sidebar: Connect"), lambda: tr("Show the comma connect status in the sidebar.")),
      ("SidebarShowSunnylink", lambda: tr("Sidebar: sunnylink"), lambda: tr("Show the sunnylink status in the sidebar.")),
    ]

    return [toggle_item_sp(title=title, description=desc, param=param) for param, title, desc in sidebar_toggles]

  def _render(self, rect):
    self._scroller.render(rect)

  def show_event(self):
    self._scroller.show_event()
