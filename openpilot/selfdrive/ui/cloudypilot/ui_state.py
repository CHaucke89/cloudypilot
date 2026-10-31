from openpilot.cloudypilot.system.remote_ui.client_state import ClientStateReader


class UIStateCP:
  def __init__(self):
    self.torque_bar_fade: bool = False
    self.use_feet: bool = False
    self.remote_ui: bool = False
    self._remote_ui_client_state = ClientStateReader()

  @property
  def remote_ui_client_connected(self) -> bool:
    return self._remote_ui_client_state.connected()

  def update_params(self) -> None:
    self.torque_bar_fade = self.params.get_bool("TorqueBarFade")
    self.use_feet = self.params.get_bool("UseFeetGPS")
    self.remote_ui = self.params.get_bool("EnableRemoteUI")
