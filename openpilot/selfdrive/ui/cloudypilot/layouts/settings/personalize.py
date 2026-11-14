from openpilot.selfdrive.ui.cloudypilot.layouts.sidebar import MAX_TILES
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.scroller_tici import Scroller


class PersonalizeLayout(Widget):
  def __init__(self):
    super().__init__()

    self._tile_items = []
    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=True, spacing=0)

  def _initialize_items(self):
    network = toggle_item_sp(
      title=lambda: tr("Sidebar: Network"),
      description=lambda: tr("Show the signal strength and connection type in the sidebar."),
      param="SidebarShowNetwork",
    )

    tile_toggles = [
      ("SidebarShowTemp", lambda: tr("Sidebar: Temperature"), lambda: tr("Show the device temperature status in the sidebar.")),
      ("SidebarShowVehicle", lambda: tr("Sidebar: Vehicle"), lambda: tr("Show the vehicle (panda) connection status in the sidebar.")),
      ("SidebarShowConnect", lambda: tr("Sidebar: Connect"), lambda: tr("Show the comma connect status in the sidebar.")),
      ("SidebarShowSunnylink", lambda: tr("Sidebar: sunnylink"), lambda: tr("Show the sunnylink status in the sidebar.")),
      ("SidebarShowStorage", lambda: tr("Sidebar: Storage"), lambda: tr("Show the free storage space in the sidebar.")),
      ("SidebarShowGps", lambda: tr("Sidebar: GPS"), lambda: tr("Show the GPS fix and satellite count in the sidebar.")),
      ("SidebarShowBattery", lambda: tr("Sidebar: Car Battery"), lambda: tr("Show the car battery voltage in the sidebar.")),
      ("SidebarShowRemoteUI", lambda: tr("Sidebar: Remote UI"), lambda: tr("Show the number of connected Remote UI clients in the sidebar.")),
      ("SidebarShowUpdate", lambda: tr("Sidebar: Update"), lambda: tr("Show the software update status in the sidebar.")),
      ("SidebarShowLoad", lambda: tr("Sidebar: System Load"), lambda: tr("Show the CPU and memory usage in the sidebar.")),
    ]
    self._tile_items = [self._tile_item(param, title, desc) for param, title, desc in tile_toggles]

    temp = self._tile_items[0]
    temp_degrees = toggle_item_sp(
      title=lambda: tr("Sidebar: Temperature in Degrees"),
      description=lambda: tr("Show the device temperature in degrees instead of GOOD or HIGH."),
      param="SidebarTempDegrees",
      enabled=lambda: temp.action_item.get_state(),
    )

    return [network, temp, temp_degrees, *self._tile_items[1:]]

  def _tile_item(self, param, title, desc):
    item = toggle_item_sp(title=title, description=desc, param=param)
    # Set after construction since both callbacks need the item itself
    item.set_description(lambda: self._tile_description(item, desc))
    item.action_item.set_enabled(lambda: self._can_toggle(item))
    return item

  def _total_tiles_on(self) -> int:
    return sum(item.action_item.get_state() for item in self._tile_items)

  def _can_toggle(self, item) -> bool:
    # Tiles that are on stay enabled so they can always be turned off
    return item.action_item.get_state() or self._total_tiles_on() < MAX_TILES

  def _tile_description(self, item, desc) -> str:
    if self._can_toggle(item):
      return desc()
    return desc() + "<br>" + tr("The sidebar fits {} tiles. Turn one off to show this one.").format(MAX_TILES)

  def _render(self, rect):
    self._scroller.render(rect)

  def show_event(self):
    self._scroller.show_event()
