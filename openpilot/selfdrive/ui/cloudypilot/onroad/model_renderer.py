import pyray as rl
from openpilot.selfdrive.ui.onroad.model_renderer import ModelRenderer
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.shader_polygon import draw_polygon, Gradient

ORANGE_PATH_GRADIENT = Gradient(
  start=(0.0, 1.0),
  end=(0.0, 0.0),
  colors=[rl.Color(255, 140, 0, 102), rl.Color(255, 165, 0, 89), rl.Color(255, 165, 0, 0)],
  stops=[0.0, 0.5, 1.0],
)


class ModelRendererCP(ModelRenderer):
  def _draw_path(self):
    # Swap the upstream green stock path gradient for orange
    rainbow = ui_state.rainbow_path and self._lateral_active
    if self._path.projected_points.size and not self._longitudinal_control and not rainbow:
      draw_polygon(self._rect, self._path.projected_points, gradient=ORANGE_PATH_GRADIENT)
      return
    super()._draw_path()
