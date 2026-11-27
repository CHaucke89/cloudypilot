import subprocess
import threading
from enum import Enum

import pyray as rl
from openpilot.common.basedir import BASEDIR
from openpilot.common.git import get_branch, get_short_branch
from openpilot.common.swaglog import cloudlog
from openpilot.selfdrive.ui.cloudypilot.widgets.card import (BUTTON_FONT_SIZE, BUTTON_HEIGHT, BUTTON_SPACING, CARD_COLOR, CARD_PADDING, ROW_SPACING,
                                                              GreenButton, RedButton, YellowButton, render_divider, render_row)
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.button import Button, ButtonStyle

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


class UpdateCheck(Enum):
  NONE = 0
  FAST_FORWARD = 1
  DIVERGED = 2


class SoftwareWidget(Widget):
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

  def _render(self, rect: rl.Rectangle):
    rl.draw_rectangle_rounded(rect, 0.04, 20, CARD_COLOR)

    x = rect.x + CARD_PADDING
    w = rect.width - 2 * CARD_PADDING
    content_h = BUTTON_HEIGHT * 3 + ROW_SPACING * 2
    y = rect.y + (rect.height - content_h) / 2

    y = render_row(x, y, w, tr("Current Branch"), get_short_branch(), self._select_button)
    y = render_divider(x, y, w)

    busy = self._updating or self._checking
    self._check_button.set_enabled(not busy)
    y = render_row(x, y, w, tr("Instant Update"), self._status_text(), self._check_button)
    y += ROW_SPACING

    # unchecked (or failed check) keeps both enabled so a hard reset is always reachable
    soft_ok = self._check_result in (None, UpdateCheck.FAST_FORWARD)
    hard_ok = self._check_result in (None, UpdateCheck.DIVERGED)
    half_w = (w - BUTTON_SPACING) / 2
    for i, (button, ok) in enumerate(((self._soft_button, soft_ok), (self._hard_button, hard_ok))):
      button.set_enabled(ok and not busy)
      button.render(rl.Rectangle(x + i * (half_w + BUTTON_SPACING), y, half_w, BUTTON_HEIGHT))
