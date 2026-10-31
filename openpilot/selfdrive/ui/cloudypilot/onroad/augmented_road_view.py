import pyray as rl
from openpilot.selfdrive.ui.ui_state import UIStatus, ui_state
from openpilot.selfdrive.ui.sunnypilot.onroad.augmented_road_view import AugmentedRoadViewSP


BORDER_COLORS_CP = {
  UIStatus.ENGAGED: rl.Color(0xE6, 0x29, 0x37, 0xFF),  # Red for engaged state
  UIStatus.LAT_ONLY: rl.Color(0xFF, 0xA5, 0x00, 0xFF),  # Orange for lateral only
  UIStatus.LONG_ONLY: rl.Color(0xFF, 0xFF, 0x00, 0xFF),  # Yellow for longitudinal only
}


class AugmentedRoadViewCP(AugmentedRoadViewSP):
  def update_fade_out_bottom_overlay(self, _content_rect):
    # Fade out bottom of overlays for looks (only when engaged), controlled independently of the steering arc
    fade_alpha = self._fade_alpha_filter.update(ui_state.status != UIStatus.DISENGAGED)
    if ui_state.torque_bar_fade and fade_alpha > 1e-2:
      # Scale the fade texture to the content rect
      rl.draw_texture_pro(self._fade_texture,
                          rl.Rectangle(0, 0, self._fade_texture.width, self._fade_texture.height),
                          _content_rect, rl.Vector2(0, 0), 0.0,
                          rl.Color(255, 255, 255, int(255 * fade_alpha)))
