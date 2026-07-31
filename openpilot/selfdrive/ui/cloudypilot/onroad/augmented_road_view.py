import pyray as rl
from openpilot.selfdrive.ui.ui_state import UIStatus


BORDER_COLORS_CP = {
  UIStatus.ENGAGED: rl.Color(0xE6, 0x29, 0x37, 0xFF),  # Red for engaged state
  UIStatus.LAT_ONLY: rl.Color(0xFF, 0xA5, 0x00, 0xFF),  # Orange for lateral only
  UIStatus.LONG_ONLY: rl.Color(0xFF, 0xFF, 0x00, 0xFF),  # Yellow for longitudinal only
}
