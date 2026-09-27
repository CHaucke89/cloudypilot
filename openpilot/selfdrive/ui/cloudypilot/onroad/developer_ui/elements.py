from opendbc.car.hyundai.carcontroller import compute_torque_reduction_gain
from openpilot.selfdrive.ui.sunnypilot.onroad.developer_ui.elements import LateralControlElement, UiElement


class TorqueReductionGainElement(LateralControlElement):
  def __init__(self):
    self.unit = ""
    self.last_gain = 0.0

  def update(self, sm, is_metric: bool) -> UiElement:
    car_state = sm['carState']
    lat_active = sm['carControl'].latActive

    torque_reduction_gain = compute_torque_reduction_gain(
      steering_torque=car_state.steeringTorque,
      v_ego=car_state.vEgo,
      lat_active=lat_active,
      last_gain=self.last_gain
    )

    self.last_gain = torque_reduction_gain
    value = f"{torque_reduction_gain:.3f}" if lat_active else "-"
    color = self.get_lat_color(lat_active, car_state.steeringPressed)

    return UiElement(value, "TQ GAIN", self.unit, color)
