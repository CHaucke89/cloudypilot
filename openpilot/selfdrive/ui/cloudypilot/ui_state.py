class UIStateCP:
  def __init__(self):
    self.torque_bar_fade: bool = False
    self.use_feet: bool = False
    self.remote_ui: bool = False

  def update_params(self) -> None:
    self.torque_bar_fade = self.params.get_bool("TorqueBarFade")
    self.use_feet = self.params.get_bool("UseFeetGPS")
    self.remote_ui = self.params.get_bool("EnableRemoteUI")
