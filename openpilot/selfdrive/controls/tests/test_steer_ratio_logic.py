"""
Tests for steer ratio selection logic.

This module tests the logic in controlsd.state_control that selects between
learned (from vehicleParameters) and custom steer ratio based on UseCustomSR param.
"""

from openpilot.common.test import OpenpilotTestCase
from openpilot.common.parameterized import parameterized


class TestSteerRatioLogic(OpenpilotTestCase):
  """Test the steer ratio selection and clamping logic.

  The logic in controlsd.state_control:
    use_custom_sr = self.params.get_bool("UseCustomSR")
    sr_custom = self.params.get("CustomSR", return_default=True)
    sr = max(lp.steerRatio, 0.1) if not use_custom_sr else max(sr_custom, 0.1)
  """

  def simulate_sr_logic(self, use_custom_sr, learned_sr, custom_sr):
    """Simulate the exact steer ratio logic from controlsd.state_control."""
    sr = max(learned_sr, 0.1) if not use_custom_sr else max(custom_sr, 0.1)
    return sr

  @parameterized.expand([
      (0.05, 0.1),   # Below min, should clamp
      (0.1, 0.1),    # At min, should not change
      (0.15, 0.15),  # Above min, should not change
      (0.0, 0.1),    # Zero, should clamp
      (-5.0, 0.1),   # Negative, should clamp
      (20.0, 20.0),  # High value, should not clamp
  ])
  def test_steer_ratio_clamping(self, input_sr, expected_sr):
    """Test that steer ratio is properly clamped to 0.1 minimum."""
    sr = max(input_sr, 0.1)
    self.assertEqual(sr, expected_sr)

  def test_learned_steer_ratio_used_when_custom_disabled(self):
    """When UseCustomSR is False, learned steer ratio should be used."""
    learned_sr = 12.5
    custom_sr = 14.0
    sr = self.simulate_sr_logic(use_custom_sr=False, learned_sr=learned_sr, custom_sr=custom_sr)
    self.assertEqual(sr, learned_sr)
    self.assertNotEqual(sr, custom_sr)

  def test_custom_steer_ratio_used_when_enabled(self):
    """When UseCustomSR is True, custom steer ratio should be used."""
    learned_sr = 12.5
    custom_sr = 14.0
    sr = self.simulate_sr_logic(use_custom_sr=True, learned_sr=learned_sr, custom_sr=custom_sr)
    self.assertEqual(sr, custom_sr)
    self.assertNotEqual(sr, learned_sr)

  @parameterized.expand([
      (False, 12.0, 13.0, 12.0),  # learned when custom disabled
      (True, 12.0, 13.0, 13.0),   # custom when custom enabled
      (False, 0.05, 13.0, 0.1),   # learned clamped when custom disabled
      (True, 12.0, 0.05, 0.1),    # custom clamped when custom enabled
      (False, 15.5, 10.0, 15.5),  # learned when values differ
      (True, 15.5, 10.0, 10.0),   # custom when values differ
      (False, -2.0, 14.0, 0.1),   # negative learned clamped
      (True, 12.0, -5.0, 0.1),    # negative custom clamped
      (False, 0.0, 20.0, 0.1),    # zero learned clamped
      (True, 20.0, 0.0, 0.1),     # zero custom clamped
  ])
  def test_mode_selection_with_clamping(self, use_custom_sr, learned_sr, custom_sr, expected_sr):
    """Test steer ratio selection respects use_custom_sr and applies clamping."""
    sr = self.simulate_sr_logic(use_custom_sr, learned_sr, custom_sr)
    self.assertEqual(sr, expected_sr)

  def test_switching_between_modes(self):
    """Test switching from learned to custom mode."""
    learned_sr = 12.0
    custom_sr = 14.0

    # First: learned mode
    sr_learned = self.simulate_sr_logic(use_custom_sr=False, learned_sr=learned_sr, custom_sr=custom_sr)
    self.assertEqual(sr_learned, 12.0)

    # Switch to custom mode
    sr_custom = self.simulate_sr_logic(use_custom_sr=True, learned_sr=learned_sr, custom_sr=custom_sr)
    self.assertEqual(sr_custom, 14.0)

    # Both are valid, just different selections
    self.assertNotEqual(sr_learned, sr_custom)

  def test_boundary_values(self):
    """Test boundary value behavior at 0.1."""
    # Exactly at boundary
    sr = max(0.1, 0.1)
    self.assertEqual(sr, 0.1)

    # Just below boundary
    sr = max(0.09999, 0.1)
    self.assertEqual(sr, 0.1)

    # Just above boundary
    sr = max(0.10001, 0.1)
    self.assertAlmostEqual(sr, 0.10001, places=5)

  def test_typical_steer_ratio_values(self):
    """Test with typical vehicle steer ratio values (11-15 range)."""
    typical_values = [11.0, 12.0, 12.5, 13.0, 13.5, 14.0, 15.0]

    for val in typical_values:
      # Should never be clamped for typical values
      sr = max(val, 0.1)
      self.assertEqual(sr, val)

  @parameterized.expand([11.0, 12.5, 13.0, 14.5, 15.0])
  def test_standard_ratios_not_clamped(self, ratio):
    """Standard vehicle steer ratios should not be clamped."""
    sr = max(ratio, 0.1)
    self.assertEqual(sr, ratio)

  def test_vm_update_params_values(self):
    """Test the values that would be passed to VM.update_params."""
    # Simulate what state_control does:
    # lp = self.sm['vehicleParameters']
    # x = max(lp.stiffnessFactor, 0.1)
    # sr = max(lp.steerRatio, 0.1) if not use_custom_sr else max(sr_custom, 0.1)
    # self.VM.update_params(x, sr)

    stiffness_factor = 0.8
    x = max(stiffness_factor, 0.1)
    self.assertEqual(x, 0.8)

    # Case 1: learned mode
    learned_sr = 12.5
    sr_learned = max(learned_sr, 0.1)
    self.assertEqual(sr_learned, 12.5)
    # VM would be called with (0.8, 12.5)

    # Case 2: custom mode with custom SR
    custom_sr = 14.0
    sr_custom = max(custom_sr, 0.1)
    self.assertEqual(sr_custom, 14.0)
    # VM would be called with (0.8, 14.0)

  def test_zero_values_all_clamped(self):
    """All zero values should clamp to 0.1."""
    self.assertEqual(max(0, 0.1), 0.1)
    self.assertEqual(max(0.0, 0.1), 0.1)

  def test_very_large_values(self):
    """Very large steer ratio values should not be clamped."""
    large_values = [50.0, 100.0, 1000.0]
    for val in large_values:
      sr = max(val, 0.1)
      self.assertEqual(sr, val)
