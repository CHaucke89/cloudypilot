import pyray as rl
from openpilot.selfdrive.ui.onroad.model_renderer import ModelRenderer, THROTTLE_COLORS

ORANGE_THROTTLE_COLORS = [
  rl.Color(255, 140, 0, 102),
  rl.Color(255, 165, 0, 89),
  rl.Color(255, 165, 0, 0),
]


class ModelRendererCP(ModelRenderer):
  @staticmethod
  def _blend_colors(begin_colors, end_colors, t):
    # Swap the upstream green "throttle" gradient for orange
    if end_colors is THROTTLE_COLORS:
      end_colors = ORANGE_THROTTLE_COLORS
    return ModelRenderer._blend_colors(begin_colors, end_colors, t)
