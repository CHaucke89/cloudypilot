import pyray as rl

from opendbc.car.hyundai.carcontroller import compute_torque_reduction_gain
from openpilot.selfdrive.ui.sunnypilot.onroad.developer_ui.elements import LateralControlElement, UiElement, GpsInfoElement

METER_TO_FOOT = 3.28084


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


class AltitudeElement(GpsInfoElement):
  def __init__(self):
    self.unit = "m"

  def update(self, sm, use_feet: bool) -> UiElement:
    gps_data, valid = self.get_gps_data(sm)

    gps_accuracy = 0.0
    altitude = 0.0

    self.unit = "ft" if use_feet else "m"

    if valid:
      altitude = gps_data.altitude * METER_TO_FOOT if use_feet else gps_data.altitude
      if sm.valid['gpsLocationExternal']:
        gps_accuracy = gps_data.horizontalAccuracy
      else:
        gps_accuracy = 1.0  # Simulate valid for legacy check

    value = f"{altitude:.1f}" if gps_accuracy != 0.0 else "-"
    return UiElement(value, "ALT.", self.unit, rl.WHITE)
