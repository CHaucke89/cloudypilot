import pyray as rl
from collections.abc import Callable
from typing import NamedTuple
from openpilot.selfdrive.ui.cloudypilot.widgets.card import CARD_COLOR, CARD_PADDING, ROW_SPACING, TEXT_SPACING, VALUE_COLOR, VALUE_FONT_SIZE, \
  render_divider
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app, TextAlignment
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.label import gui_label
from openpilot.system.ui.sunnypilot.widgets.toggle import ToggleSP as Toggle
from openpilot.system.ui.sunnypilot.lib.styles import style
if gui_app.cloudypilot_ui():
  from openpilot.system.ui.cloudypilot.lib.styles import style

LABEL_FONT_SIZE = 44
ROW_HEIGHT = 100
MAX_QUICK_TOGGLES = 3


def _icbm_available() -> bool:
  # mirrors the Cruise panel: ICBM only applies when the car supports it and cloudypilot isn't doing longitudinal
  cp_sp = ui_state.CP_SP
  return cp_sp is not None and cp_sp.intelligentCruiseButtonManagementAvailable and not ui_state.has_longitudinal_control


def _scc_available() -> bool:
  # mirrors the Cruise panel: Smart Cruise Control needs cloudypilot longitudinal or ICBM
  return ui_state.CP is not None and (ui_state.has_longitudinal_control or ui_state.has_icbm)


class QuickToggle(NamedTuple):
  show_param: str
  param: str
  label: Callable[[], str]
  name: Callable[[], str]
  available: Callable[[], bool] = lambda: True
  needs_restart: bool = False


QUICK_TOGGLES = (
  QuickToggle("QuickToggleShowCloudypilot", "OpenpilotEnabledToggle", lambda: tr("Enable cloudypilot"), lambda: tr("Enable cloudypilot"),
              needs_restart=True),
  QuickToggle("QuickToggleShowRemoteUI", "EnableRemoteUI", lambda: tr("Remote UI"), lambda: tr("Remote UI")),
  QuickToggle("QuickToggleShowICBM", "IntelligentCruiseButtonManagement", lambda: tr("ICBM"),
              lambda: tr("Intelligent Cruise Button Management"), available=_icbm_available),
  QuickToggle("QuickToggleShowMads", "Mads", lambda: tr("MADS"), lambda: tr("Modular Assistive Driving System"), available=ui_state.is_offroad),
  QuickToggle("QuickToggleShowSCCVision", "SmartCruiseControlVision", lambda: tr("SCC Vision"), lambda: tr("Smart Cruise Control - Vision"),
              available=_scc_available),
  QuickToggle("QuickToggleShowSCCMap", "SmartCruiseControlMap", lambda: tr("SCC Map"), lambda: tr("Smart Cruise Control - Map"),
              available=_scc_available),
  QuickToggle("QuickToggleShowDisengageOnGas", "DisengageOnAccelerator", lambda: tr("Disengage on Gas"),
              lambda: tr("Disengage on Accelerator Pedal")),
  QuickToggle("QuickToggleShowLDW", "IsLdwEnabled", lambda: tr("Lane Departure"), lambda: tr("Lane Departure Warnings")),
  QuickToggle("QuickToggleShowAlwaysOnDM", "AlwaysOnDM", lambda: tr("Always-On DM"), lambda: tr("Always-On Driver Monitoring")),
  QuickToggle("QuickToggleShowRecordFront", "RecordFront", lambda: tr("Driver Camera"), lambda: tr("Record and Upload Driver Camera"),
              needs_restart=True),
  QuickToggle("QuickToggleShowRecordAudio", "RecordAudio", lambda: tr("Record Audio"), lambda: tr("Record and Upload Microphone Audio"),
              needs_restart=True),
  QuickToggle("QuickToggleShowMetric", "IsMetric", lambda: tr("Metric Units"), lambda: tr("Use Metric System")),
)


class QuickTogglesWidget(Widget):
  def __init__(self):
    super().__init__()
    self._toggles = {qt.param: Toggle(ui_state.params.get_bool(qt.param), callback=lambda state, qt=qt: self._on_toggled(qt, state))
                     for qt in QUICK_TOGGLES}

  @staticmethod
  def _on_toggled(qt: QuickToggle, state: bool):
    ui_state.params.put_bool(qt.param, state, block=True)
    if qt.needs_restart:
      ui_state.params.put_bool("OnroadCycleRequested", True, block=True)

  def _render(self, rect: rl.Rectangle):
    rl.draw_rectangle_rounded(rect, 0.04, 20, CARD_COLOR)

    x = rect.x + CARD_PADDING
    w = rect.width - 2 * CARD_PADDING
    # Personalize enforces the cap, but params can also be set from outside it
    rows = [qt for qt in QUICK_TOGGLES if qt.show_param in ui_state.quick_toggles_shown][:MAX_QUICK_TOGGLES]

    if not rows:
      y = rect.y + (rect.height - LABEL_FONT_SIZE - TEXT_SPACING - VALUE_FONT_SIZE) / 2
      gui_label(rl.Rectangle(x, y, w, LABEL_FONT_SIZE), tr("No Quick Toggles"), LABEL_FONT_SIZE, alignment=TextAlignment.CENTER)
      gui_label(rl.Rectangle(x, y + LABEL_FONT_SIZE + TEXT_SPACING, w, VALUE_FONT_SIZE), tr("Choose them in Personalize"),
                VALUE_FONT_SIZE, VALUE_COLOR, alignment=TextAlignment.CENTER)
      return

    content_h = ROW_HEIGHT * len(rows) + ROW_SPACING * (len(rows) - 1)
    y = rect.y + (rect.height - content_h) / 2

    for i, qt in enumerate(rows):
      if i > 0:
        y = render_divider(x, y, w)
      available = qt.available()
      toggle = self._toggles[qt.param]
      toggle.set_enabled(available)
      toggle.set_state(available and ui_state.params.get_bool(qt.param))

      label = qt.label() if available else f"{qt.label()} ({tr('Unavailable')})"
      gui_label(rl.Rectangle(x, y, w - style.TOGGLE_WIDTH - ROW_SPACING, ROW_HEIGHT), label, LABEL_FONT_SIZE,
                rl.WHITE if available else VALUE_COLOR)
      toggle.render(rl.Rectangle(x + w - style.TOGGLE_WIDTH, y + (ROW_HEIGHT - style.TOGGLE_BG_HEIGHT + style.ITEM_PADDING) / 2,
                                 style.TOGGLE_WIDTH, style.TOGGLE_HEIGHT))
      y += ROW_HEIGHT
