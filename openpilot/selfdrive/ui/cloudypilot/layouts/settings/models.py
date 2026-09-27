from openpilot.selfdrive.ui.sunnypilot.layouts.settings.models import ModelsLayout
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.cloudypilot.lib.styles import style
from openpilot.system.ui.cloudypilot.widgets.list_view import option_item_cp


class ModelsLayoutCP(ModelsLayout):
  def __init__(self):
    super().__init__()

  def _initialize_items(self):
    super()._initialize_items()

    # Replace camera offset control with one that resets to default when the label is tapped
    idx = self.items.index(self.camera_offset)
    self.camera_offset = option_item_cp(tr("Adjust Camera Offset"), "CameraOffset", -35, 35,
                                        tr("Virtually shift camera's perspective to move model's center to Left(+ values) or Right (- values)"),
                                        1, None, True, "", style.BUTTON_ACTION_WIDTH, None, True,
                                        lambda v: f"{v / 100:.2f} m", reset_enabled=True)
    self.items[idx] = self.camera_offset
