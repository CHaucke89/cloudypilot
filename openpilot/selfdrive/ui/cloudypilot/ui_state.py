from openpilot.cloudypilot.system.remote_ui.client_state import ClientStateReader


class UIStateCP:
  def __init__(self):
    self.torque_bar_fade: bool = False
    self.use_feet: bool = False
    self.remote_ui: bool = False
    self.sidebar_show_network: bool = True
    self.sidebar_show_temp: bool = True
    self.sidebar_show_vehicle: bool = True
    self.sidebar_show_connect: bool = True
    self.sidebar_show_sunnylink: bool = True
    self.sidebar_show_storage: bool = False
    self.sidebar_show_gps: bool = False
    self.sidebar_show_battery: bool = False
    self.sidebar_show_remote_ui: bool = False
    self.sidebar_show_update: bool = False
    self.sidebar_show_load: bool = False
    self.sidebar_temp_degrees: bool = False
    self.shutdown_voltage: float = 11.8
    self._remote_ui_client_state = ClientStateReader()

  @property
  def remote_ui_client_connected(self) -> bool:
    return self._remote_ui_client_state.connected()

  @property
  def remote_ui_client_count(self) -> int:
    return self._remote_ui_client_state.client_count()

  def update_params(self) -> None:
    self.torque_bar_fade = self.params.get_bool("TorqueBarFade")
    self.use_feet = self.params.get_bool("UseFeetGPS")
    self.remote_ui = self.params.get_bool("EnableRemoteUI")
    self.sidebar_show_network = self.params.get_bool("SidebarShowNetwork")
    self.sidebar_show_temp = self.params.get_bool("SidebarShowTemp")
    self.sidebar_show_vehicle = self.params.get_bool("SidebarShowVehicle")
    self.sidebar_show_connect = self.params.get_bool("SidebarShowConnect")
    self.sidebar_show_sunnylink = self.params.get_bool("SidebarShowSunnylink")
    self.sidebar_show_storage = self.params.get_bool("SidebarShowStorage")
    self.sidebar_show_gps = self.params.get_bool("SidebarShowGps")
    self.sidebar_show_battery = self.params.get_bool("SidebarShowBattery")
    self.sidebar_show_remote_ui = self.params.get_bool("SidebarShowRemoteUI")
    self.sidebar_show_update = self.params.get_bool("SidebarShowUpdate")
    self.sidebar_show_load = self.params.get_bool("SidebarShowLoad")
    self.sidebar_temp_degrees = self.params.get_bool("SidebarTempDegrees")
    self.shutdown_voltage = self.params.get("CustomShutdownVoltage", return_default=True)
