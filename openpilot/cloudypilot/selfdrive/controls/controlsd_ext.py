from openpilot.common.params import Params


class ControlsExtCP:
  def __init__(self, params: Params):
    self.params = params

  # Determine if we're using the learned steer ratio or a custom fixed value
  def get_steer_ratio(self, vehicle_params):
    use_custom_sr = self.params.get_bool("UseCustomSR")
    custom_sr = self.params.get("CustomSR", return_default=True)
    sr = max(vehicle_params.steerRatio, 0.1) if not use_custom_sr else max(round(custom_sr, 2), 0.1)
    return sr
