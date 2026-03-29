"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import numpy as np

from cereal import car

from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.common.swaglog import cloudlog
from openpilot.sunnypilot import PARAMS_UPDATE_PERIOD

RELAXED_MIN_BUCKET_POINTS = np.array([1, 200, 300, 500, 500, 300, 200, 1])

ALLOWED_CARS = ['toyota', 'hyundai', 'rivian', 'honda']

# Default speed bins — used when car has no speed_dependent.toml entry.
# Skip <5 m/s where lat_accel = v*yaw_rate is noisy.
DEFAULT_SPEED_BIN_BOUNDS = [(5, 8), (8, 12), (12, 18), (18, 24), (24, 29), (29, 35), (35, 40)]
DEFAULT_SPEED_BIN_CENTERS = [6.5, 10.0, 15.0, 21.0, 26.5, 32.0, 37.5]
MIN_POINTS_PER_SPEED_BIN = 600
FIT_POINTS_PER_SPEED_BIN = 400
POINTS_PER_SPEED_BUCKET = 500
SPEED_BIN_MIN_CAL_PERC = 80  # min cal% before applying learned values to closure
FRICTION_FACTOR = 1.5  # same as upstream


class TorqueEstimatorExt:
  """SP extension mixed into TorqueEstimator via multiple inheritance.

  Adds per-speed-bin learning on top of upstream's single-value torqued.
  Gated by SpeedDependentTorqueToggle (polled dynamically, no restart needed).

  Data flow:
    1. torqued calls _on_torque_point() for each quality-filtered sample → routed to speed bin
    2. _estimate_params_speed_binned() runs independent SVD fit per bin (same algo as upstream)
    3. _extend_msg() writes per-bin latAccelFactor/friction/valid/cal% to cereal message
    4. controlsd_ext picks up the message and calls latcontrol_torque_ext.update_speed_dep_torque()
    5. The lateral controller interpolates latAccelFactor and friction by speed each frame

  Bin configuration:
    - Cars with a speed_dependent.toml entry use per-car bin centers (and derived bounds)
    - Cars without an entry use DEFAULT_SPEED_BIN_BOUNDS and seed all bins with global offline values
    - Bin ranges are derived from centers via midpoint calculation (see _centers_to_bounds)
  """

  def __init__(self, CP: car.CarParams):
    self.CP = CP
    self._params = Params()
    self.frame = -1

    self.enforce_torque_control_toggle = self._params.get_bool("EnforceTorqueControl")  # only during init
    self.use_params = self.CP.brand in ALLOWED_CARS and self.CP.lateralTuning.which() == 'torque'
    self.self_tune_enabled = self._params.get_bool("LiveTorqueParamsToggle")
    self.custom_live_params = self._params.get_bool("TorqueParamsOverrideEnabled")
    self.use_speed_dep = self._params.get_bool("SpeedDependentTorqueToggle")
    self.speed_binned = False
    self.min_bucket_points = RELAXED_MIN_BUCKET_POINTS
    self.factor_sanity = 0.0
    self.friction_sanity = 0.0
    self.offline_latAccelFactor = 0.0
    self.offline_friction = 0.0

  def initialize_custom_params(self, decimated=False):
    self.update_use_params()

    if self.enforce_torque_control_toggle:
      if self._params.get_bool("LiveTorqueParamsRelaxedToggle"):
        self.min_bucket_points = RELAXED_MIN_BUCKET_POINTS / (10 if decimated else 1)
        self.factor_sanity = 0.5 if decimated else 1.0
        self.friction_sanity = 0.8 if decimated else 1.0

      if self._params.get_bool("CustomTorqueParams"):
        self.offline_latAccelFactor = float(self._params.get("TorqueParamsOverrideLatAccelFactor", return_default=True))
        self.offline_friction = float(self._params.get("TorqueParamsOverrideFriction", return_default=True))

    # Speed-binned learning: toggle-gated, works for any torque car
    self.speed_binned = self.CP.lateralTuning.which() == 'torque' and self.use_speed_dep

    # Eagerly init speed bins and restore cache so bins exist before the
    # first cache write (frame 0). Without this, the first cache write emits
    # empty bin arrays that overwrite the previous route's cached points.
    if self.speed_binned:
      self._post_reset()
      try:
        from cereal import log
        cache = self._params.get("LiveTorqueParameters")
        if cache:
          with log.Event.from_bytes(cache) as evt:
            self._restore_ext_cache(evt.liveTorqueParameters)
      except Exception:
        cloudlog.exception("speed-dep: failed to restore cache on init")

  def _update_params(self):
    if self.frame % int(PARAMS_UPDATE_PERIOD / DT_MDL) == 0:
      self.self_tune_enabled = self._params.get_bool("LiveTorqueParamsToggle")
      self.custom_live_params = self._params.get_bool("TorqueParamsOverrideEnabled")
      self.use_speed_dep = self._params.get_bool("SpeedDependentTorqueToggle")
      self.speed_binned = self.CP.lateralTuning.which() == 'torque' and self.use_speed_dep

  def update_use_params(self):
    self._update_params()

    if self.enforce_torque_control_toggle:
      if self.custom_live_params:
        self.use_params = False
      else:
        self.use_params = self.self_tune_enabled

    self.frame += 1

  # --- Speed-binned learning hooks (called from TorqueEstimator) ---

  @staticmethod
  def _centers_to_bounds(centers):
    """Derive bin bounds from centers using midpoints between consecutive centers.
    First bin starts at default lower edge (5 m/s), last bin ends at default upper edge (40 m/s)."""
    bounds = []
    for i, c in enumerate(centers):
      lo = DEFAULT_SPEED_BIN_BOUNDS[0][0] if i == 0 else (centers[i - 1] + c) / 2
      hi = DEFAULT_SPEED_BIN_BOUNDS[-1][1] if i == len(centers) - 1 else (c + centers[i + 1]) / 2
      bounds.append((lo, hi))
    return bounds

  def _post_reset(self):
    """Called from TorqueEstimator.reset(). Initializes per-speed-bin buckets."""
    if not self.speed_binned:
      return

    from openpilot.selfdrive.locationd.torqued import TorqueBuckets, STEER_BUCKET_BOUNDS, MIN_FILTER_DECAY
    from opendbc.sunnypilot.car.interfaces import get_speed_dep_config

    cfg = get_speed_dep_config().get(self.CP.carFingerprint, {})

    # Per-car bin ranges from config, or defaults
    if 'speed_bp' in cfg:
      self.speed_bin_centers = list(cfg['speed_bp'])
      self.speed_bin_bounds = self._centers_to_bounds(self.speed_bin_centers)
    else:
      self.speed_bin_bounds = list(DEFAULT_SPEED_BIN_BOUNDS)
      self.speed_bin_centers = list(DEFAULT_SPEED_BIN_CENTERS)

    n_bins = len(self.speed_bin_bounds)

    self.speed_bin_points = [self._make_speed_bin_bucket(TorqueBuckets, STEER_BUCKET_BOUNDS) for _ in range(n_bins)]

    ref_lafs = cfg.get('laf_bp', [self.offline_latAccelFactor] * n_bins)
    ref_frictions = cfg.get('friction_bp', [self.offline_friction] * n_bins)
    self.speed_bin_decays = [MIN_FILTER_DECAY] * n_bins
    self.speed_bin_filtered = [
      {'latAccelFactor': FirstOrderFilter(ref_lafs[i], self.speed_bin_decays[i], DT_MDL),
       'frictionCoefficient': FirstOrderFilter(ref_frictions[i], self.speed_bin_decays[i], DT_MDL)}
      for i in range(n_bins)
    ]
    # Fixed ±30% sanity bounds for speed bins — independent of the "Less Restrict"
    # toggle. Without this, default factor_sanity=0.0 would clamp learned values
    # to exactly the seed values, silently preventing any learning.
    SPEED_BIN_SANITY = 0.3
    self.speed_bin_lat_accel_factor_bounds = [
      ((1.0 - SPEED_BIN_SANITY) * factor, (1.0 + SPEED_BIN_SANITY) * factor)
      for factor in ref_lafs
    ]
    self.speed_bin_friction_bounds = [
      ((1.0 - SPEED_BIN_SANITY) * f, (1.0 + SPEED_BIN_SANITY) * f)
      for f in ref_frictions
    ]

  def _make_speed_bin_bucket(self, TorqueBuckets, STEER_BUCKET_BOUNDS):
    """Create a single speed-bin TorqueBuckets instance."""
    return TorqueBuckets(x_bounds=STEER_BUCKET_BOUNDS,
                         min_points=self.min_bucket_points,
                         min_points_total=MIN_POINTS_PER_SPEED_BIN,
                         points_per_bucket=POINTS_PER_SPEED_BUCKET,
                         rowsize=3)

  def _ensure_speed_bins(self):
    """Init speed bins on first call only (also handles toggle-on after init).
    Speed bins are independent of the global learner — a global NaN reset does
    not affect them. Each bin resets independently if its own SVD produces NaN."""
    if hasattr(self, 'speed_bin_points'):
      return
    self._post_reset()
    try:
      from cereal import log
      cache = self._params.get("LiveTorqueParameters")
      if cache:
        with log.Event.from_bytes(cache) as evt:
          self._restore_ext_cache(evt.liveTorqueParameters)
    except Exception:
      cloudlog.exception("speed-dep: failed to restore cache on first init")

  def _on_torque_point(self, steer, lateral_acc, vego):
    """Called from handle_log. Routes quality-filtered points to speed bins."""
    if not self.speed_binned:
      return
    self._ensure_speed_bins()
    for i, (lo, hi) in enumerate(self.speed_bin_bounds):
      if lo <= vego < hi:
        self.speed_bin_points[i].add_point(steer, lateral_acc)
        break

  def _restore_ext_cache(self, cache_ltp):
    """Restores per-bin filter values and points from cache."""
    if not self.speed_binned:
      return
    n_bins = len(self.speed_bin_bounds)
    if (len(cache_ltp.speedBinLatAccelFactors) == n_bins and
        len(cache_ltp.speedBinFrictions) == n_bins):
      for i in range(n_bins):
        self.speed_bin_filtered[i]['latAccelFactor'].x = cache_ltp.speedBinLatAccelFactors[i]
        self.speed_bin_filtered[i]['frictionCoefficient'].x = cache_ltp.speedBinFrictions[i]
      if len(cache_ltp.speedBinPoints) == n_bins:
        for i in range(n_bins):
          self.speed_bin_points[i].load_points(cache_ltp.speedBinPoints[i])
      self.speed_bin_decays = [self.decay] * n_bins
      cloudlog.info("restored speed-bin torque params from cache")

  def _estimate_params_speed_binned(self):
    """Run independent SVD fit per speed bin. Following upstream pattern:
    if a bin has enough data (is_valid) but produces NaN, reset that bin only."""
    from openpilot.selfdrive.locationd.torqued import TorqueBuckets, STEER_BUCKET_BOUNDS, slope2rot, \
      MIN_FILTER_DECAY, MAX_FILTER_DECAY

    results = []
    for i, bucket in enumerate(self.speed_bin_points):
      if bucket.is_calculable():
        points = bucket.get_points(FIT_POINTS_PER_SPEED_BIN)
        try:
          _, _, v = np.linalg.svd(points, full_matrices=False)
          slope, offset = -v.T[0:2, 2] / v.T[2, 2]
          _, spread = np.matmul(points[:, [0, 2]], slope2rot(slope)).T
          friction_coeff = np.std(spread) * FRICTION_FACTOR
          if not any(np.isnan(val) for val in [slope, friction_coeff]):
            factor_lo, factor_hi = self.speed_bin_lat_accel_factor_bounds[i]
            fric_lo, fric_hi = self.speed_bin_friction_bounds[i]
            clipped_factor = np.clip(slope, factor_lo, factor_hi)
            fric = np.clip(friction_coeff, fric_lo, fric_hi)
            self.speed_bin_decays[i] = min(self.speed_bin_decays[i] + DT_MDL, MAX_FILTER_DECAY)
            self.speed_bin_filtered[i]['latAccelFactor'].update(clipped_factor)
            self.speed_bin_filtered[i]['latAccelFactor'].update_alpha(self.speed_bin_decays[i])
            self.speed_bin_filtered[i]['frictionCoefficient'].update(fric)
            self.speed_bin_filtered[i]['frictionCoefficient'].update_alpha(self.speed_bin_decays[i])
            results.append((i, True))
            continue
        except np.linalg.LinAlgError:
          pass

        # Fell through: NaN or SVD failure. Following upstream pattern,
        # reset this bin only if it had enough data to be valid.
        if bucket.is_valid():
          cloudlog.warning(f"speed-dep: bin {i} produced NaN with valid data, resetting bin")
          self.speed_bin_points[i] = self._make_speed_bin_bucket(TorqueBuckets, STEER_BUCKET_BOUNDS)
          self.speed_bin_decays[i] = MIN_FILTER_DECAY
      results.append((i, False))
    return results

  def _extend_msg(self, ltp, with_points):
    """Called from get_msg. Populates speed-bin fields in cereal message.
    Skips if bins aren't initialized yet — prevents overwriting a good Params
    cache with empty arrays before _ensure_speed_bins has restored it."""
    if not self.speed_binned or not hasattr(self, 'speed_bin_points'):
      return
    bin_results = self._estimate_params_speed_binned()
    n_bins = len(self.speed_bin_bounds)
    bin_cal_percs = [float(self.speed_bin_points[i].get_valid_percent()) for i in range(n_bins)]
    ltp.speedBinCenters = self.speed_bin_centers
    ltp.speedBinLatAccelFactors = [float(self.speed_bin_filtered[i]['latAccelFactor'].x) for i in range(n_bins)]
    ltp.speedBinFrictions = [float(self.speed_bin_filtered[i]['frictionCoefficient'].x) for i in range(n_bins)]
    ltp.speedBinValid = [valid and bin_cal_percs[i] >= SPEED_BIN_MIN_CAL_PERC for i, (_, valid) in enumerate(bin_results)]
    ltp.speedBinCalPerc = bin_cal_percs
    if with_points:
      ltp.speedBinPoints = [bucket.get_points(FIT_POINTS_PER_SPEED_BIN)[:, [0, 2]].tolist() for bucket in self.speed_bin_points]
