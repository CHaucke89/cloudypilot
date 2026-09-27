class UIStateCP:
  def __init__(self):
    self.torque_bar_fade: bool = False

  def update_params(self) -> None:
    self.torque_bar_fade = self.params.get_bool("TorqueBarFade")
