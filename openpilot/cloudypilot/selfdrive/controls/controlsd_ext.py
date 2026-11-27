from openpilot.common.params import Params


class ControlsExtCP:
  def __init__(self, params: Params):
    self.params = params

  # Determine if we're using the learned steer ratio or a custom fixed value
  def get_steer_ratio(self, lp):
    if self.params.get_bool("UseCustomSR"):
      custom_sr = self.params.get("CustomSR", return_default=True)
      return max(round(custom_sr, 2), 0.1)
    return max(lp.steerRatio, 0.1)
