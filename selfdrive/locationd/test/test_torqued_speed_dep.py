"""Tests for speed-binned learning in torqued (vehicle-agnostic).

Uses get_speed_dep_config() to discover configured cars.
All tests are driven by config, not hardcoded fingerprints.
"""
import pytest

from unittest.mock import MagicMock, patch  # noqa: TID251
from opendbc.sunnypilot.car.interfaces import get_speed_dep_config
from openpilot.selfdrive.locationd.torqued import (
  TorqueEstimator, VERSION,
)
from openpilot.sunnypilot.selfdrive.locationd.torqued_ext import (
  DEFAULT_SPEED_BIN_BOUNDS as SPEED_BIN_BOUNDS, DEFAULT_SPEED_BIN_CENTERS as SPEED_BIN_CENTERS,
)

# Discover configured cars
SPEED_DEP_CARS = get_speed_dep_config()
SPEED_DEP_FINGERPRINT = next(iter(SPEED_DEP_CARS)) if SPEED_DEP_CARS else None

# Sentinel fingerprint that must not appear in speed_dependent.toml
NON_SPEED_DEP_FINGERPRINT = 'NOT_IN_SPEED_DEP_TOML'
assert NON_SPEED_DEP_FINGERPRINT not in SPEED_DEP_CARS, f"{NON_SPEED_DEP_FINGERPRINT} unexpectedly in speed_dependent.toml"

# Both Params locations need mocking: torqued.py (cache) and torqued_ext.py (toggles)
PATCH_PARAMS = 'openpilot.selfdrive.locationd.torqued.Params'
PATCH_EXT_PARAMS = 'openpilot.sunnypilot.selfdrive.locationd.torqued_ext.Params'


def _setup_ext_mock(mock_ext_params_cls, speed_dep_on):
  """Configure the torqued_ext Params mock for toggle state."""
  def _get_bool(param):
    if param == "SpeedDependentTorqueToggle":
      return speed_dep_on
    return False
  mock_ext_params_cls.return_value.get_bool.side_effect = _get_bool
  mock_ext_params_cls.return_value.get.return_value = None


def make_mock_CP(fingerprint=None, lat_accel_factor=1.25, friction=0.125):
  if fingerprint is None:
    fingerprint = SPEED_DEP_FINGERPRINT
  CP = MagicMock()
  CP.brand = 'test'
  CP.carFingerprint = fingerprint
  CP.lateralTuning.which.return_value = 'torque'
  CP.lateralTuning.torque.friction = friction
  CP.lateralTuning.torque.latAccelFactor = lat_accel_factor
  return CP


class TestSpeedDepConfig:
  """Config-level tests that don't need a TorqueEstimator."""

  def test_speed_dep_config_has_entries(self):
    assert len(SPEED_DEP_CARS) > 0

  def test_version_exists(self):
    assert VERSION >= 1

  def test_speed_bin_bounds_cover_full_range(self):
    all_bounds = [b for bounds in SPEED_BIN_BOUNDS for b in bounds]
    assert min(all_bounds) == 5
    assert max(all_bounds) >= 35

  def test_speed_bin_centers_match_bounds(self):
    for center, (lo, hi) in zip(SPEED_BIN_CENTERS, SPEED_BIN_BOUNDS, strict=True):
      assert center >= lo
      assert center <= hi


@pytest.mark.skipif(SPEED_DEP_FINGERPRINT is None, reason="No cars in speed_dependent.toml")
class TestSpeedBinnedLearning:
  """Test speed-binned learning with toggle ON."""

  @patch(PATCH_EXT_PARAMS)
  @patch(PATCH_PARAMS)
  def test_speed_bins_initialized(self, mock_params_cls, mock_ext):
    mock_params_cls.return_value.get.return_value = None
    _setup_ext_mock(mock_ext, speed_dep_on=True)
    for fingerprint in SPEED_DEP_CARS:
      est = TorqueEstimator(make_mock_CP(fingerprint=fingerprint))
      assert est.speed_binned
      # Bins are lazy-initialized on first point
      est._on_torque_point(0.1, 0.3, 10.0)
      assert len(est.speed_bin_points) == len(SPEED_BIN_BOUNDS)

  @patch(PATCH_EXT_PARAMS)
  @patch(PATCH_PARAMS)
  def test_speed_bin_routing(self, mock_params_cls, mock_ext):
    mock_params_cls.return_value.get.return_value = None
    _setup_ext_mock(mock_ext, speed_dep_on=True)
    for bin_idx, (lo, hi) in enumerate(SPEED_BIN_BOUNDS):
      est = TorqueEstimator(make_mock_CP())
      vego = (lo + hi) / 2.0
      est._on_torque_point(0.1, 0.3, vego)
      assert len(est.speed_bin_points[bin_idx]) == 1, \
        f"bin {bin_idx} ({lo}-{hi} m/s) should have 1 point at vego={vego}"
      for j in range(len(SPEED_BIN_BOUNDS)):
        if j != bin_idx:
          assert len(est.speed_bin_points[j]) == 0, \
            f"bin {j} should be empty when vego={vego}"

  @patch(PATCH_EXT_PARAMS)
  @patch(PATCH_PARAMS)
  def test_cereal_message_fields(self, mock_params_cls, mock_ext):
    mock_params_cls.return_value.get.return_value = None
    _setup_ext_mock(mock_ext, speed_dep_on=True)
    for fingerprint in SPEED_DEP_CARS:
      est = TorqueEstimator(make_mock_CP(fingerprint=fingerprint))
      # Trigger lazy bin init so _extend_msg populates fields
      est._on_torque_point(0.1, 0.3, 10.0)
      msg = est.get_msg()
      ltp = msg.liveTorqueParameters
      assert len(ltp.speedBinCenters) == len(SPEED_BIN_CENTERS)
      assert len(ltp.speedBinLatAccelFactors) == len(SPEED_BIN_BOUNDS)
      assert len(ltp.speedBinFrictions) == len(SPEED_BIN_BOUNDS)
      assert len(ltp.speedBinValid) == len(SPEED_BIN_BOUNDS)
      assert len(ltp.speedBinCalPerc) == len(SPEED_BIN_BOUNDS)

  @patch(PATCH_EXT_PARAMS)
  @patch(PATCH_PARAMS)
  def test_global_fit_unchanged(self, mock_params_cls, mock_ext):
    mock_params_cls.return_value.get.return_value = None
    _setup_ext_mock(mock_ext, speed_dep_on=True)
    est = TorqueEstimator(make_mock_CP(lat_accel_factor=1.25, friction=0.125))
    msg = est.get_msg()
    ltp = msg.liveTorqueParameters
    assert ltp.latAccelFactorFiltered == pytest.approx(1.25, abs=1e-2)
    assert ltp.frictionCoefficientFiltered == pytest.approx(0.125, abs=1e-3)

  @patch(PATCH_EXT_PARAMS)
  @patch(PATCH_PARAMS)
  def test_global_buckets_still_require_min_vel(self, mock_params_cls, mock_ext):
    mock_params_cls.return_value.get.return_value = None
    _setup_ext_mock(mock_ext, speed_dep_on=True)
    est = TorqueEstimator(make_mock_CP())
    assert len(est.filtered_points) == 0


class TestToggleGate:
  """Toggle OFF should disable speed-binning even for configured cars."""

  @patch(PATCH_EXT_PARAMS)
  @patch(PATCH_PARAMS)
  def test_toggle_off_no_speed_bins(self, mock_params_cls, mock_ext):
    mock_params_cls.return_value.get.return_value = None
    _setup_ext_mock(mock_ext, speed_dep_on=False)
    if SPEED_DEP_FINGERPRINT:
      est = TorqueEstimator(make_mock_CP(fingerprint=SPEED_DEP_FINGERPRINT))
      assert not est.speed_binned


class TestBackwardCompatibility:
  """Cars with toggle OFF should be unaffected."""

  @patch(PATCH_EXT_PARAMS)
  @patch(PATCH_PARAMS)
  def test_unconfigured_car_no_speed_bins(self, mock_params_cls, mock_ext):
    mock_params_cls.return_value.get.return_value = None
    _setup_ext_mock(mock_ext, speed_dep_on=False)
    est = TorqueEstimator(make_mock_CP(fingerprint=NON_SPEED_DEP_FINGERPRINT))
    assert not est.speed_binned

  @patch(PATCH_EXT_PARAMS)
  @patch(PATCH_PARAMS)
  def test_unconfigured_car_no_speed_bin_fields(self, mock_params_cls, mock_ext):
    mock_params_cls.return_value.get.return_value = None
    _setup_ext_mock(mock_ext, speed_dep_on=False)
    est = TorqueEstimator(make_mock_CP(fingerprint=NON_SPEED_DEP_FINGERPRINT))
    msg = est.get_msg()
    ltp = msg.liveTorqueParameters
    assert len(ltp.speedBinCenters) == 0
    assert len(ltp.speedBinLatAccelFactors) == 0
    assert len(ltp.speedBinFrictions) == 0
    assert len(ltp.speedBinValid) == 0
    assert len(ltp.speedBinCalPerc) == 0

  @patch(PATCH_EXT_PARAMS)
  @patch(PATCH_PARAMS)
  def test_unconfigured_car_global_params_still_work(self, mock_params_cls, mock_ext):
    mock_params_cls.return_value.get.return_value = None
    _setup_ext_mock(mock_ext, speed_dep_on=False)
    est = TorqueEstimator(make_mock_CP(fingerprint=NON_SPEED_DEP_FINGERPRINT, lat_accel_factor=2.0, friction=0.15))
    msg = est.get_msg()
    ltp = msg.liveTorqueParameters
    assert ltp.latAccelFactorFiltered == pytest.approx(2.0, abs=1e-2)
    assert ltp.frictionCoefficientFiltered == pytest.approx(0.15, abs=1e-3)
    assert not est.speed_binned

  @patch(PATCH_EXT_PARAMS)
  @patch(PATCH_PARAMS)
  def test_unconfigured_car_no_speed_bin_attributes(self, mock_params_cls, mock_ext):
    mock_params_cls.return_value.get.return_value = None
    _setup_ext_mock(mock_ext, speed_dep_on=False)
    est = TorqueEstimator(make_mock_CP(fingerprint=NON_SPEED_DEP_FINGERPRINT))
    assert not hasattr(est, 'speed_bin_points')
    assert not hasattr(est, 'speed_bin_filtered')

  @patch(PATCH_EXT_PARAMS)
  @patch(PATCH_PARAMS)
  def test_cal_percent_works_for_both(self, mock_params_cls, mock_ext):
    mock_params_cls.return_value.get.return_value = None
    _setup_ext_mock(mock_ext, speed_dep_on=True)
    fingerprints = [NON_SPEED_DEP_FINGERPRINT]
    if SPEED_DEP_FINGERPRINT:
      fingerprints.append(SPEED_DEP_FINGERPRINT)
    for fp in fingerprints:
      est = TorqueEstimator(make_mock_CP(fingerprint=fp))
      msg = est.get_msg()
      assert msg.liveTorqueParameters.calPerc == 0
