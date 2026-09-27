from unittest import mock

from openpilot.cereal import log
from openpilot.common.parameterized import parameterized
from openpilot.common.test import OpenpilotTestCase
from openpilot.cloudypilot.selfdrive.controls.controlsd_ext import ControlsExtCP


class TestControlsExtCP(OpenpilotTestCase):
  def _get_steer_ratio(self, use_custom_sr: bool, learned_sr: float, custom_sr: float) -> float:
    params = mock.MagicMock()
    params.get_bool.side_effect = lambda key: {"UseCustomSR": use_custom_sr}[key]
    params.get.side_effect = lambda key, return_default=False: {"CustomSR": custom_sr}[key]

    lp = log.VehicleParameters.new_message()
    lp.steerRatio = learned_sr
    return ControlsExtCP(params).get_steer_ratio(lp)

  @parameterized.expand([
    (False, 12.0, 13.0, 12.0),     # learned when custom disabled
    (True, 12.0, 13.0, 13.0),      # custom when custom enabled
    (False, 0.05, 13.0, 0.1),      # learned clamped when custom disabled
    (True, 12.0, 0.05, 0.1),       # custom clamped when custom enabled
    (True, 12.0, 15.456, 15.46),   # custom rounded to 2 decimals
  ])
  def test_get_steer_ratio(self, use_custom_sr, learned_sr, custom_sr, expected):
    self.assertAlmostEqual(self._get_steer_ratio(use_custom_sr, learned_sr, custom_sr), expected, places=5)
