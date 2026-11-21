import subprocess
import threading
from enum import Enum

import pyray as rl
from openpilot.common.basedir import BASEDIR
from openpilot.common.git import get_branch, get_short_branch
from openpilot.common.swaglog import cloudlog
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import FontWeight
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.button import Button, ButtonStyle
from openpilot.system.ui.widgets.label import gui_label

YELLOW = rl.Color(255, 204, 0, 255)
YELLOW_PRESSED = rl.Color(214, 170, 0, 255)
YELLOW_DISABLED = rl.Color(120, 100, 20, 255)
RED = rl.Color(255, 70, 70, 255)
RED_PRESSED = rl.Color(226, 44, 44, 255)
RED_DISABLED = rl.Color(120, 20, 20, 255)
GREEN = rl.Color(51, 171, 76, 255)
GREEN_PRESSED = rl.Color(40, 140, 62, 255)
GREEN_DISABLED = rl.Color(25, 85, 38, 255)
BUTTON_TEXT = rl.Color(20, 20, 20, 255)

UPDATE_REMOTE = "origin"
UPDATE_BRANCH = get_branch().split("/", 1)[-1]

HARD_UPDATE_COMMANDS = (
  ["git", "fetch", UPDATE_REMOTE],
  ["git", "reset", "--hard", f"{UPDATE_REMOTE}/{UPDATE_BRANCH}"],
  ["git", "submodule", "update", "--init", "--recursive"],
)

SOFT_UPDATE_COMMANDS = (
  ["git", "pull", UPDATE_REMOTE],
  ["git", "submodule", "update", "--init", "--recursive"],
)

CARD_COLOR = rl.Color(51, 51, 51, 255)
DIVIDER_COLOR = rl.Color(86, 86, 86, 255)
VALUE_COLOR = rl.Color(170, 170, 170, 255)
CARD_PADDING = 56
HEADER_FONT_SIZE = 48
VALUE_FONT_SIZE = 40
TEXT_SPACING = 8
ROW_SPACING = 24
BUTTON_SPACING = 24
BUTTON_HEIGHT = 96
ROW_BUTTON_WIDTH = 300
BUTTON_FONT_SIZE = 44


class UpdateCheck(Enum):
  NONE = 0
  FAST_FORWARD = 1
  DIVERGED = 2


class YellowButton(Button):
  def _update_state(self):
    super()._update_state()
    if not self.enabled:
      self._background_color = YELLOW_DISABLED
    else:
      self._background_color = YELLOW_PRESSED if self.is_pressed else YELLOW
    self._label.set_text_color(BUTTON_TEXT)

class RedButton(Button):
  def _update_state(self):
    super()._update_state()
    if not self.enabled:
      self._background_color = RED_DISABLED
    else:
      self._background_color = RED_PRESSED if self.is_pressed else RED
    self._label.set_text_color(BUTTON_TEXT)

class GreenButton(Button):
  def _update_state(self):
    super()._update_state()
    if not self.enabled:
      self._background_color = GREEN_DISABLED
    else:
      self._background_color = GREEN_PRESSED if self.is_pressed else GREEN
    self._label.set_text_color(BUTTON_TEXT)

class SoftwareWidget(Widget):
  """Branch selector beside instant update; Check gates Soft (fast-forward) vs Hard (force-pushed)."""

  def __init__(self):
    super().__init__()
    self._open_software_callback = None
    self._updating = False
    self._checking = False
    self._check_result: UpdateCheck | None = None
    self._select_button = Button(lambda: tr("Select"), lambda: self._open_software_callback() if self._open_software_callback else None,
                                 font_size=BUTTON_FONT_SIZE, button_style=ButtonStyle.PRIMARY)
    self._check_button = GreenButton(lambda: tr("Checking...") if self._checking else tr("Check"),
                                     self._start_check, font_size=BUTTON_FONT_SIZE, button_style=ButtonStyle.NORMAL)
    self._hard_button = RedButton(lambda: tr("Updating...") if self._updating else tr("Hard Update"),
                                     lambda: self._start_update(HARD_UPDATE_COMMANDS), font_size=BUTTON_FONT_SIZE, button_style=ButtonStyle.NORMAL)
    self._soft_button = YellowButton(lambda: tr("Updating...") if self._updating else tr("Soft Update"),
                                     lambda: self._start_update(SOFT_UPDATE_COMMANDS), font_size=BUTTON_FONT_SIZE, button_style=ButtonStyle.NORMAL)

  def set_open_software_callback(self, callback):
    self._open_software_callback = callback

  def _start_update(self, commands):
    if self._updating:
      return
    self._updating = True
    threading.Thread(target=self._run_update, args=(commands,), daemon=True).start()

  def _start_check(self):
    if self._checking or self._updating:
      return
    self._checking = True
    threading.Thread(target=self._run_check, daemon=True).start()

  def _run_check(self):
    try:
      subprocess.run(["git", "fetch", UPDATE_REMOTE], cwd=BASEDIR, check=True, capture_output=True, text=True)
      head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=BASEDIR, text=True).strip()
      remote = subprocess.check_output(["git", "rev-parse", f"{UPDATE_REMOTE}/{UPDATE_BRANCH}"], cwd=BASEDIR, text=True).strip()
      if head == remote:
        self._check_result = UpdateCheck.NONE
      elif subprocess.run(["git", "merge-base", "--is-ancestor", head, remote], cwd=BASEDIR).returncode == 0:
        self._check_result = UpdateCheck.FAST_FORWARD
      else:
        # also covers remote rewound behind HEAD, which only a hard reset can follow
        self._check_result = UpdateCheck.DIVERGED
    except subprocess.CalledProcessError as e:
      cloudlog.error(f"update check failed: {' '.join(e.cmd)}: {e.stderr}")
      self._check_result = None
    except Exception:
      cloudlog.exception("update check failed")
      self._check_result = None
    finally:
      self._checking = False

  def _status_text(self) -> str:
    if self._checking:
      return tr("Checking for updates...")
    if self._check_result == UpdateCheck.NONE:
      return tr("Up to date")
    if self._check_result == UpdateCheck.FAST_FORWARD:
      return tr("Update available")
    if self._check_result == UpdateCheck.DIVERGED:
      return tr("Branch was force-pushed")
    return tr("Check for updates")

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

  def _render_row(self, x: float, y: float, w: float, header: str, value: str, button: Button) -> float:
    text_w = w - ROW_BUTTON_WIDTH - BUTTON_SPACING
    text_y = y + (BUTTON_HEIGHT - (HEADER_FONT_SIZE + TEXT_SPACING + VALUE_FONT_SIZE)) / 2
    gui_label(rl.Rectangle(x, text_y, text_w, HEADER_FONT_SIZE), header, HEADER_FONT_SIZE, rl.WHITE, FontWeight.MEDIUM)
    text_y += HEADER_FONT_SIZE + TEXT_SPACING
    gui_label(rl.Rectangle(x, text_y, text_w, VALUE_FONT_SIZE), value, VALUE_FONT_SIZE, VALUE_COLOR)
    button.render(rl.Rectangle(x + w - ROW_BUTTON_WIDTH, y, ROW_BUTTON_WIDTH, BUTTON_HEIGHT))
    return y + BUTTON_HEIGHT

  def _render(self, rect: rl.Rectangle):
    rl.draw_rectangle_rounded(rect, 0.04, 20, CARD_COLOR)

    x = rect.x + CARD_PADDING
    w = rect.width - 2 * CARD_PADDING
    content_h = BUTTON_HEIGHT * 3 + ROW_SPACING * 2
    y = rect.y + (rect.height - content_h) / 2

    y = self._render_row(x, y, w, tr("Current Branch"), get_short_branch(), self._select_button)
    y += ROW_SPACING / 2
    rl.draw_line_ex(rl.Vector2(x, y), rl.Vector2(x + w, y), 2, DIVIDER_COLOR)
    y += ROW_SPACING / 2

    busy = self._updating or self._checking
    self._check_button.set_enabled(not busy)
    y = self._render_row(x, y, w, tr("Instant Update"), self._status_text(), self._check_button)
    y += ROW_SPACING

    # unchecked (or failed check) keeps both enabled so a hard reset is always reachable
    soft_ok = self._check_result in (None, UpdateCheck.FAST_FORWARD)
    hard_ok = self._check_result in (None, UpdateCheck.DIVERGED)
    half_w = (w - BUTTON_SPACING) / 2
    for i, (button, ok) in enumerate(((self._soft_button, soft_ok), (self._hard_button, hard_ok))):
      button.set_enabled(ok and not busy)
      button.render(rl.Rectangle(x + i * (half_w + BUTTON_SPACING), y, half_w, BUTTON_HEIGHT))
