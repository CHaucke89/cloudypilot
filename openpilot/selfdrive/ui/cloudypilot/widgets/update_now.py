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

UPDATE_COMMANDS = (
  ["git", "fetch", UPDATE_REMOTE],
  ["git", "reset", "--hard", f"{UPDATE_REMOTE}/{UPDATE_BRANCH}"],
  ["git", "submodule", "update", "--init", "--recursive"],
)


class YellowButton(Button):
  def _update_state(self):
    super()._update_state()
    if not self.enabled:
      self._background_color = YELLOW_DISABLED
    else:
      self._background_color = YELLOW_PRESSED if self.is_pressed else YELLOW
    self._label.set_text_color(BUTTON_TEXT)


class UpdateNowWidget(Widget):
  """Card with a button that fetches origin, hard-resets to origin/ch-dev, updates submodules, then soft reboots."""

  def __init__(self):
    super().__init__()
    self._updating = False
    self._button = YellowButton(lambda: tr("Updating...") if self._updating else tr("Update Now"), self._on_clicked,
                                button_style=ButtonStyle.NORMAL)
    self._title_label = Label(lambda: tr("Update"), font_weight=FontWeight.MEDIUM, font_size=64)

  def _on_clicked(self):
    if self._updating:
      return
    self._updating = True
    threading.Thread(target=self._run_update, daemon=True).start()

  def _run_update(self):
    cmd: list[str] = []
    try:
      for cmd in UPDATE_COMMANDS:
        subprocess.run(cmd, cwd=BASEDIR, check=True, capture_output=True, text=True)
      ui_state.params.put_bool("DoSoftReboot", True)
    except subprocess.CalledProcessError as e:
      cloudlog.error(f"immediate update failed: {' '.join(cmd)}: {e.stderr}")
      self._updating = False
    except Exception:
      cloudlog.exception("immediate update failed")
      self._updating = False

  def _render(self, rect: rl.Rectangle):
    rl.draw_rectangle_rounded(rl.Rectangle(rect.x, rect.y, rect.width, 400), 0.04, 20, rl.Color(51, 51, 51, 255))

    x = rect.x + 56
    y = rect.y + 40
    w = rect.width - 112
    spacing = 42

    self._title_label.render(rl.Rectangle(rect.x, y, rect.width, 64))
    y += 64 + spacing

    desc_font = gui_app.font(FontWeight.NORMAL)
    for line in wrap_text(desc_font, tr(f"Pull latest {UPDATE_BRANCH} and reboot"), 40, int(w)):
      text_size = measure_text_cached(desc_font, line, 40)
      rl.draw_text_ex(desc_font, line, rl.Vector2(int(rect.x + (rect.width - text_size.x) // 2), int(y)), 40, 0, rl.WHITE)
      y += 40 * FONT_SCALE

    y += spacing

    self._button.set_enabled(not self._updating)
    self._button.render(rl.Rectangle(x, y, w, 48 + 64))
