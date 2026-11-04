import subprocess
import threading

import pyray as rl
from openpilot.common.basedir import BASEDIR
from openpilot.common.swaglog import cloudlog
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app, FontWeight, FONT_SCALE
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.lib.wrap_text import wrap_text
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.button import Button, ButtonStyle
from openpilot.system.ui.widgets.label import Label

YELLOW = rl.Color(255, 204, 0, 255)
YELLOW_PRESSED = rl.Color(214, 170, 0, 255)
YELLOW_DISABLED = rl.Color(120, 100, 20, 255)
BUTTON_TEXT = rl.Color(20, 20, 20, 255)

UPDATE_REMOTE = "origin"
UPDATE_BRANCH = "ch-dev"

HARD_UPDATE_COMMANDS = (
  ["git", "fetch", UPDATE_REMOTE],
  ["git", "reset", "--hard", f"{UPDATE_REMOTE}/{UPDATE_BRANCH}"],
  ["git", "submodule", "update", "--init", "--recursive"],
)

SOFT_UPDATE_COMMANDS = (
  ["git", "pull", UPDATE_REMOTE],
  ["git", "submodule", "update", "--init", "--recursive"],
)

BUTTON_SPACING = 24
BUTTON_FONT_SIZE = 44  # right column is narrow; default 60 won't fit two labels side by side


class YellowButton(Button):
  def _update_state(self):
    super()._update_state()
    if not self.enabled:
      self._background_color = YELLOW_DISABLED
    else:
      self._background_color = YELLOW_PRESSED if self.is_pressed else YELLOW
    self._label.set_text_color(BUTTON_TEXT)


class UpdateNowWidget(Widget):
  """Card with Hard/Soft update buttons. Hard: fetch + reset --hard to origin/ch-dev. Soft: pull. Both update submodules, then soft reboot."""

  def __init__(self):
    super().__init__()
    self._updating = False
    self._hard_button = YellowButton(lambda: tr("Updating...") if self._updating else tr("Hard Update"),
                                     lambda: self._start_update(HARD_UPDATE_COMMANDS), font_size=BUTTON_FONT_SIZE, button_style=ButtonStyle.NORMAL)
    self._soft_button = YellowButton(lambda: tr("Updating...") if self._updating else tr("Soft Update"),
                                     lambda: self._start_update(SOFT_UPDATE_COMMANDS), font_size=BUTTON_FONT_SIZE, button_style=ButtonStyle.NORMAL)
    self._title_label = Label(lambda: tr("Instant Update"), font_weight=FontWeight.MEDIUM, font_size=64)

  def _start_update(self, commands):
    if self._updating:
      return
    self._updating = True
    threading.Thread(target=self._run_update, args=(commands,), daemon=True).start()

  def _run_update(self, commands):
    cmd: list[str] = []
    try:
      for cmd in commands:
        subprocess.run(cmd, cwd=BASEDIR, check=True, capture_output=True, text=True)
      ui_state.params.put_bool("DoSoftReboot", True)
    except subprocess.CalledProcessError as e:
      cloudlog.error(f"immediate update failed: {' '.join(cmd)}: {e.stderr}")
      self._updating = False
    except Exception:
      cloudlog.exception("immediate update failed")
      self._updating = False

  def _render(self, rect: rl.Rectangle):
    rl.draw_rectangle_rounded(rl.Rectangle(rect.x, rect.y, rect.width, rect.height), 0.04, 20, rl.Color(51, 51, 51, 255))

    x = rect.x + 56
    w = rect.width - 112
    spacing = 42

    desc_font = gui_app.font(FontWeight.NORMAL)
    wrapped_desc = wrap_text(desc_font, tr(f"Update to latest {UPDATE_BRANCH}"), 40, int(w))

    button_height = 48 + 64
    content_height = 64 + spacing + len(wrapped_desc) * 40 * FONT_SCALE + spacing + button_height
    y = rect.y + (rect.height - content_height) / 2

    self._title_label.render(rl.Rectangle(rect.x, y, rect.width, 64))
    y += 64 + spacing

    for line in wrapped_desc:
      text_size = measure_text_cached(desc_font, line, 40)
      rl.draw_text_ex(desc_font, line, rl.Vector2(int(rect.x + (rect.width - text_size.x) // 2), int(y)), 40, 0, rl.WHITE)
      y += 40 * FONT_SCALE

    y += spacing

    half_w = (w - BUTTON_SPACING) / 2
    for i, button in enumerate((self._soft_button, self._hard_button)):
      button.set_enabled(not self._updating)
      button.render(rl.Rectangle(x + i * (half_w + BUTTON_SPACING), y, half_w, button_height))
