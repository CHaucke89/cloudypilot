from collections.abc import Callable
from openpilot.selfdrive.ui.cloudypilot.layouts.sidebar import MAX_TILES
from openpilot.selfdrive.ui.cloudypilot.widgets.quick_toggles import MAX_QUICK_TOGGLES, QUICK_TOGGLES
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import ListItemSP, toggle_item_sp
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.scroller_tici import Scroller


class CappedToggleGroup:
  def __init__(self, cap: int, cap_desc: Callable[[], str]):
    self._cap = cap
    self._cap_desc = cap_desc
    self.items: list[ListItemSP] = []

  def add(self, param: str, title: Callable[[], str], desc: Callable[[], str]) -> ListItemSP:
    item = toggle_item_sp(title=title, description=desc, param=param)
    # Set after construction since both callbacks need the item itself
    item.set_description(lambda: desc() if self._can_toggle(item) else desc() + "<br>" + self._cap_desc())
    item.action_item.set_enabled(lambda: self._can_toggle(item))
    self.items.append(item)
    return item

  def _can_toggle(self, item: ListItemSP) -> bool:
    # Items that are on stay enabled so they can always be turned off
    return item.action_item.get_state() or sum(i.action_item.get_state() for i in self.items) < self._cap


class PersonalizeLayout(Widget):
  def __init__(self):
    super().__init__()

    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=True, spacing=0)

  def _initialize_items(self):
    network = toggle_item_sp(
      title=lambda: tr("Sidebar: Network"),
      description=lambda: tr("Show the signal strength and connection type in the sidebar."),
      param="SidebarShowNetwork",
    )
    network_ip = toggle_item_sp(
      title=lambda: tr("Sidebar: Network IP Address"),
      description=lambda: tr("Show the device's IP address instead of Wi-Fi when connected to Wi-Fi."),
      param="SidebarNetworkIP",
      enabled=lambda: network.action_item.get_state(),
    )

    reorder = ListItemSP(
      title=lambda: tr("> Reorder Sidebar Tiles <"),
      description=lambda: tr("While parked, hold a sidebar tile for half a second until it lifts, then drag it to a new spot."),
    )

    tiles = CappedToggleGroup(MAX_TILES, lambda: tr("The sidebar fits {} tiles. Turn one off to show this one.").format(MAX_TILES))
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
    for param, title, desc in tile_toggles:
      tiles.add(param, title, desc)

    temp = tiles.items[0]
    temp_degrees = toggle_item_sp(
      title=lambda: tr("Sidebar: Temperature in Degrees"),
      description=lambda: tr("Show the device temperature in degrees instead of GOOD or HIGH."),
      param="SidebarTempDegrees",
      enabled=lambda: temp.action_item.get_state(),
    )

    quick_toggles = CappedToggleGroup(MAX_QUICK_TOGGLES, lambda: tr("The Quick Toggles card fits {} toggles. Turn one off to show this one.")
                                      .format(MAX_QUICK_TOGGLES))
    for qt in QUICK_TOGGLES:
      quick_toggles.add(qt.show_param, lambda qt=qt: tr("Quick Toggle: {}").format(qt.label()),
                        lambda qt=qt: tr("Show {} on the home screen's Quick Toggles card.").format(qt.name()))

    return [reorder, network, network_ip, temp, temp_degrees, *tiles.items[1:], *quick_toggles.items]

  def _render(self, rect):
    self._scroller.render(rect)

  def show_event(self):
    self._scroller.show_event()
