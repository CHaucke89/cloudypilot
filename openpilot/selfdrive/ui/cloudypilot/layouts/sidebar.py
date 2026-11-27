import pyray as rl
import socket
import time
from collections.abc import Callable
from openpilot.cereal import log
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app, FontWeight, MouseEvent, MousePos, FONT_SCALE
from openpilot.system.ui.lib.multilang import tr, tr_noop
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget

from openpilot.selfdrive.ui.sunnypilot.layouts.sidebar import MetricData, SidebarSP

SIDEBAR_WIDTH = 300
METRIC_HEIGHT = 126
METRIC_WIDTH = 240
METRIC_MARGIN = 30
FONT_SIZE = 35

MAX_TILES = 4
STORAGE_WARNING_PERCENT = 10  # deleter keeps this much free, so lower means it can't keep up
STORAGE_DANGER_PERCENT = 7  # selfdrived raises outOfSpace below this
BATTERY_WARNING_MARGIN_V = 0.3
LOAD_WARNING_PERCENT = 80
CPU_DANGER_PERCENT = 95
MEMORY_DANGER_PERCENT = 90  # selfdrived raises lowMemory above this

TILE_KEYS = ("temp", "vehicle", "connect", "sunnylink", "storage", "gps", "battery", "remote_ui", "update", "load")
DRAG_HOLD_S = 0.45  # same as the settings long press
DRAG_CANCEL_PX = 20  # drifting this far before the hold fires is a tap or swipe, not a grab
TILE_SLIDE_RATE = 0.3

SETTINGS_BTN = rl.Rectangle(50, 35, 200, 117)
HOME_BTN = rl.Rectangle(60, 860, 180, 180)

ThermalStatus = log.DeviceState.ThermalStatus
NetworkType = log.DeviceState.NetworkType


def wifi_ip_address() -> str:
  try:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
      # Connecting a UDP socket only resolves the route, nothing is sent
      sock.connect(("8.8.8.8", 80))
      return sock.getsockname()[0]
  except OSError:
    return ""


class Colors:
  WHITE = rl.WHITE
  WHITE_DIM = rl.Color(255, 255, 255, 85)
  GRAY = rl.Color(84, 84, 84, 255)

  # Status colors
  GOOD = rl.WHITE
  WARNING = rl.Color(218, 202, 37, 255)
  DANGER = rl.Color(201, 34, 49, 255)
  PROGRESS = rl.Color(0, 134, 233, 255)
  DISABLED = rl.Color(128, 128, 128, 255)
  LIFTED_BG = rl.Color(45, 45, 45, 255)

  # UI elements
  METRIC_BORDER = rl.Color(255, 255, 255, 85)
  BUTTON_NORMAL = rl.WHITE
  BUTTON_PRESSED = rl.Color(255, 255, 255, 166)


NETWORK_TYPES = {
  NetworkType.none: tr_noop("--"),
  NetworkType.wifi: tr_noop("Wi-Fi"),
  NetworkType.ethernet: tr_noop("ETH"),
  NetworkType.cell2G: tr_noop("2G"),
  NetworkType.cell3G: tr_noop("3G"),
  NetworkType.cell4G: tr_noop("LTE"),
  NetworkType.cell5G: tr_noop("5G"),
}


UPDATER_STATES = {
  "checking...": tr_noop("CHECKING"),
  "downloading...": tr_noop("FETCHING"),
  "finalizing update...": tr_noop("FINISHING"),
}


class SidebarCP(Widget, SidebarSP):
  def __init__(self):
    Widget.__init__(self)
    SidebarSP.__init__(self)
    self._net_type = NETWORK_TYPES[NetworkType.none]
    self._net_strength = 0
    self._net_ip = ""

    self._temp_status = MetricData(tr_noop("TEMP"), tr_noop("GOOD"), Colors.GOOD)
    self._panda_status = MetricData(tr_noop("VEHICLE"), tr_noop("ONLINE"), Colors.GOOD)
    self._connect_status = MetricData(tr_noop("CONNECT"), tr_noop("OFFLINE"), Colors.WARNING)
    self._storage_status = MetricData(tr_noop("STORAGE"), "--", Colors.DISABLED)
    self._gps_status = MetricData(tr_noop("GPS"), tr_noop("OFF"), Colors.DISABLED)
    self._battery_status = MetricData(tr_noop("BATTERY"), "--", Colors.DISABLED)
    self._remote_ui_status = MetricData(tr_noop("REMOTE UI"), tr_noop("DISABLED"), Colors.DISABLED)
    self._update_status = MetricData(tr_noop("UPDATE"), "--", Colors.DISABLED)
    self._load_status = MetricData(tr_noop("CPU"), tr_noop("MEM"), Colors.DISABLED)
    self._updater_busy = False
    self._recording_audio = False

    self._press_key: str | None = None
    self._press_t = 0.0
    self._press_pos = MousePos(0, 0)
    self._drag_key: str | None = None
    self._drag_y = 0.0
    self._grab_dy = 0.0
    self._suppress_release = False
    self._local_order: list[str] | None = None
    self._visible_keys: list[str] = []
    self._tile_rects: dict[str, rl.Rectangle] = {}
    self._tile_y: dict[str, float] = {}
    self._tiles_start_y = 0.0
    self._tiles_spacing = 0.0

    self._home_img = gui_app.texture("images/button_home.png", HOME_BTN.width, HOME_BTN.height)
    self._flag_img = gui_app.texture("images/button_flag.png", HOME_BTN.width, HOME_BTN.height)
    self._settings_img = gui_app.texture("images/button_settings.png", SETTINGS_BTN.width, SETTINGS_BTN.height)
    self._mic_img = gui_app.texture("icons/microphone.png", 30, 30)
    self._mic_indicator_rect = rl.Rectangle(0, 0, 0, 0)
    self._font_regular = gui_app.font(FontWeight.NORMAL)
    self._font_bold = gui_app.font(FontWeight.SEMI_BOLD)

    # Callbacks
    self._on_settings_click: Callable | None = None
    self._on_flag_click: Callable | None = None
    self._open_settings_callback: Callable | None = None

  def set_callbacks(self, on_settings: Callable | None = None, on_flag: Callable | None = None,
                    open_settings: Callable | None = None):
    self._on_settings_click = on_settings
    self._on_flag_click = on_flag
    self._open_settings_callback = open_settings

  def _render(self, rect: rl.Rectangle):
    # Background
    rl.draw_rectangle_rec(rect, rl.BLACK)

    self._draw_buttons(rect)
    self._draw_network_indicator(rect)
    self._draw_metrics(rect)

  def _update_state(self):
    self._update_drag()

    sm = ui_state.sm
    if not sm.updated['deviceState']:
      return

    device_state = sm['deviceState']

    self._recording_audio = ui_state.recording_audio
    self._update_network_status(device_state)
    self._update_temperature_status(device_state)
    self._update_connection_status(device_state)
    self._update_panda_status()
    SidebarSP._update_sunnylink_status(self)
    self._update_storage_status(device_state)
    self._update_gps_status()
    self._update_battery_status()
    self._update_remote_ui_status()
    self._update_updater_status()
    self._update_load_status(device_state)

  def _update_network_status(self, device_state):
    net_type = device_state.networkType.raw
    self._net_type = NETWORK_TYPES.get(net_type, tr_noop("Unknown"))
    self._net_ip = wifi_ip_address() if ui_state.sidebar_network_ip and net_type == NetworkType.wifi else ""
    strength = device_state.networkStrength
    self._net_strength = max(0, min(5, strength.raw + 1)) if strength.raw > 0 else 0

  def _update_temperature_status(self, device_state):
    hot = device_state.thermalStatus != ThermalStatus.ok

    if ui_state.sidebar_temp_degrees:
      temp_c = device_state.maxTempC
      value = f"{temp_c:.0f}°C" if ui_state.is_metric else f"{temp_c * 9 / 5 + 32:.0f}°F"
    else:
      value = tr_noop("HIGH") if hot else tr_noop("GOOD")

    self._temp_status.update(tr_noop("TEMP"), value, Colors.DANGER if hot else Colors.GOOD)

  def _update_connection_status(self, device_state):
    last_ping = device_state.lastAthenaPingTime
    if last_ping == 0:
      self._connect_status.update(tr_noop("CONNECT"), tr_noop("OFFLINE"), Colors.WARNING)
    elif time.monotonic_ns() - last_ping < 80_000_000_000:  # 80 seconds in nanoseconds
      self._connect_status.update(tr_noop("CONNECT"), tr_noop("ONLINE"), Colors.GOOD)
    else:
      self._connect_status.update(tr_noop("CONNECT"), tr_noop("ERROR"), Colors.DANGER)

  def _update_panda_status(self):
    if ui_state.panda_type == log.PandaState.PandaType.unknown:
      self._panda_status.update(tr_noop("NO"), tr_noop("PANDA"), Colors.DANGER)
    else:
      self._panda_status.update(tr_noop("VEHICLE"), tr_noop("ONLINE"), Colors.GOOD)

  def _update_storage_status(self, device_state):
    free = device_state.freeSpacePercent
    if free < STORAGE_DANGER_PERCENT:
      color = Colors.DANGER
    elif free < STORAGE_WARNING_PERCENT:
      color = Colors.WARNING
    else:
      color = Colors.GOOD

    self._storage_status.update(tr_noop("STORAGE"), tr("{}% FREE").format(round(free)), color)

  def _update_gps_status(self):
    sm = ui_state.sm
    # alive, not valid: the GPS daemons stop offroad and valid would keep the last fix
    gps = next((sm[s] for s in ("gpsLocationExternal", "gpsLocation") if sm.alive[s]), None)

    if gps is None:
      self._gps_status.update(tr_noop("GPS"), tr_noop("OFF"), Colors.DISABLED)
    elif not gps.hasFix:
      self._gps_status.update(tr_noop("GPS"), tr_noop("NO FIX"), Colors.WARNING)
    elif gps.satelliteCount > 0:
      self._gps_status.update(tr_noop("GPS"), tr("{} SAT").format(gps.satelliteCount), Colors.GOOD)
    else:
      # qcomgpsd doesn't report a satellite count
      self._gps_status.update(tr_noop("GPS"), tr_noop("FIX"), Colors.GOOD)

  def _update_battery_status(self):
    panda_states = ui_state.sm["pandaStates"]
    if ui_state.panda_type == log.PandaState.PandaType.unknown or len(panda_states) == 0:
      self._battery_status.update(tr_noop("BATTERY"), "--", Colors.DISABLED)
      return

    voltage = panda_states[0].voltage / 1000
    if voltage <= ui_state.shutdown_voltage:
      color = Colors.DANGER
    elif voltage <= ui_state.shutdown_voltage + BATTERY_WARNING_MARGIN_V:
      color = Colors.WARNING
    else:
      color = Colors.GOOD

    self._battery_status.update(tr_noop("BATTERY"), f"{voltage:.1f} V", color)

  def _update_remote_ui_status(self):
    if not ui_state.remote_ui:
      self._remote_ui_status.update(tr_noop("REMOTE UI"), tr_noop("DISABLED"), Colors.DISABLED)
      return

    clients = ui_state.remote_ui_client_count
    value = tr("1 CLIENT") if clients == 1 else tr("{} CLIENTS").format(clients)
    self._remote_ui_status.update(tr_noop("REMOTE UI"), value, Colors.PROGRESS if clients > 0 else Colors.GOOD)

  def _update_updater_status(self):
    # Costs up to five param reads, so skip them while the tile is hidden
    if not ui_state.sidebar_show_update:
      return

    if ui_state.started:
      # updated stops for the drive without resetting UpdaterState, and UpdateAvailable is cleared onroad,
      # so hold the last offroad status instead of reading stale params
      if self._updater_busy:
        self._updater_busy = False
        self._update_status.update(tr_noop("UPDATE"), tr_noop("PAUSED"), Colors.DISABLED)
      return

    params = ui_state.params
    updater_state = params.get("UpdaterState")
    self._updater_busy = False

    if params.get_bool("DisableUpdates"):
      status, color = tr_noop("DISABLED"), Colors.DISABLED
    elif updater_state is None:
      # updated only runs offroad and hasn't reported since boot
      status, color = "--", Colors.DISABLED
    elif updater_state != "idle":
      self._updater_busy = True
      status, color = UPDATER_STATES.get(updater_state, tr_noop("BUSY")), Colors.PROGRESS
    elif params.get_bool("UpdateAvailable"):
      status, color = tr_noop("READY"), Colors.WARNING
    elif (params.get("UpdateFailedCount") or 0) > 0:
      status, color = tr_noop("FAILED"), Colors.DANGER
    elif params.get_bool("UpdaterFetchAvailable"):
      status, color = tr_noop("AVAILABLE"), Colors.WARNING
    else:
      status, color = tr_noop("UP TO DATE"), Colors.GOOD

    self._update_status.update(tr_noop("UPDATE"), status, color)

  def _update_load_status(self, device_state):
    cores = device_state.cpuUsagePercent
    cpu = round(sum(cores) / len(cores)) if len(cores) > 0 else 0
    memory = device_state.memoryUsagePercent

    if cpu >= CPU_DANGER_PERCENT or memory > MEMORY_DANGER_PERCENT:
      color = Colors.DANGER
    elif cpu >= LOAD_WARNING_PERCENT or memory >= LOAD_WARNING_PERCENT:
      color = Colors.WARNING
    else:
      color = Colors.GOOD

    self._load_status.update(tr("CPU {}%").format(cpu), tr("MEM {}%").format(memory), color)

  def _tiles(self) -> dict[str, tuple[bool, MetricData]]:
    return {
      "temp": (ui_state.sidebar_show_temp, self._temp_status),
      "vehicle": (ui_state.sidebar_show_vehicle, self._panda_status),
      "connect": (ui_state.sidebar_show_connect, self._connect_status),
      "sunnylink": (ui_state.sidebar_show_sunnylink, self._sunnylink_status),
      "storage": (ui_state.sidebar_show_storage, self._storage_status),
      "gps": (ui_state.sidebar_show_gps, self._gps_status),
      "battery": (ui_state.sidebar_show_battery, self._battery_status),
      "remote_ui": (ui_state.sidebar_show_remote_ui, self._remote_ui_status),
      "update": (ui_state.sidebar_show_update, self._update_status),
      "load": (ui_state.sidebar_show_load, self._load_status),
    }

  def _tile_order(self) -> list[str]:
    # The params thread lags a drop by up to a refresh, so hold our own copy until it catches up
    if self._local_order is not None and ui_state.sidebar_tile_order == self._local_order:
      self._local_order = None
    saved = self._local_order if self._local_order is not None else ui_state.sidebar_tile_order
    order = list(dict.fromkeys(key for key in saved if key in TILE_KEYS))
    return order + [key for key in TILE_KEYS if key not in order]

  def _update_drag(self):
    if ui_state.started or not self.is_visible:
      self._press_key = self._drag_key = None
      return

    # Touch events only arrive on change, so a finger held still has to be timed here
    if self._press_key is not None and self.is_pressed and time.monotonic() - self._press_t >= DRAG_HOLD_S:
      rect = self._tile_rects.get(self._press_key)
      if rect is not None:
        self._drag_key = self._press_key
        self._drag_y = self._press_pos.y
        self._grab_dy = self._press_pos.y - rect.y
      self._press_key = None

  def _dragged_top(self) -> float:
    last_y = self._tiles_start_y + (len(self._visible_keys) - 1) * self._tiles_spacing
    return max(self._tiles_start_y, min(self._drag_y - self._grab_dy, last_y))

  def _drop_index(self) -> int:
    return round((self._dragged_top() - self._tiles_start_y) / self._tiles_spacing) if self._tiles_spacing else 0

  def _drop(self):
    assert self._drag_key is not None
    visible = [key for key in self._visible_keys if key != self._drag_key]
    visible.insert(self._drop_index(), self._drag_key)

    # Hidden tiles keep their slots so they come back where they were
    order = self._tile_order()
    slots = [i for i, key in enumerate(order) if key in visible]
    for slot, key in zip(slots, visible, strict=True):
      order[slot] = key

    self._tile_y[self._drag_key] = self._dragged_top()
    self._local_order = order
    ui_state.params.put("SidebarTileOrder", order)
    self._drag_key = None

  def _handle_mouse_event(self, mouse_event: MouseEvent):
    if mouse_event.slot != 0:
      return

    if mouse_event.left_pressed:
      self._drag_key = None
      self._suppress_release = False
      self._press_key = None
      if not ui_state.started:
        self._press_key = next((key for key, rect in self._tile_rects.items() if rl.check_collision_point_rec(mouse_event.pos, rect)), None)
        self._press_t, self._press_pos = mouse_event.t, mouse_event.pos
    elif mouse_event.left_released:
      if self._drag_key is not None:
        self._drop()
        # The release that ends a drag must not also tap the settings or flag button
        self._suppress_release = True
      self._press_key = None
    elif mouse_event.left_down:
      if self._drag_key is not None:
        self._drag_y = mouse_event.pos.y
      elif self._press_key is not None:
        moved = max(abs(mouse_event.pos.x - self._press_pos.x), abs(mouse_event.pos.y - self._press_pos.y))
        if moved > DRAG_CANCEL_PX:
          self._press_key = None

  def _handle_mouse_release(self, mouse_pos: MousePos):
    if self._suppress_release:
      self._suppress_release = False
      return

    if rl.check_collision_point_rec(mouse_pos, SETTINGS_BTN):
      if self._on_settings_click:
        self._on_settings_click()
    elif rl.check_collision_point_rec(mouse_pos, HOME_BTN) and ui_state.started:
      if self._on_flag_click:
        self._on_flag_click()
    elif self._recording_audio and rl.check_collision_point_rec(mouse_pos, self._mic_indicator_rect):
      if self._open_settings_callback:
        self._open_settings_callback()

  def _draw_buttons(self, rect: rl.Rectangle):
    mouse_pos = rl.get_mouse_position()
    mouse_down = self.is_pressed and self._drag_key is None and rl.is_mouse_button_down(rl.MouseButton.MOUSE_BUTTON_LEFT)

    # Settings button
    settings_down = mouse_down and rl.check_collision_point_rec(mouse_pos, SETTINGS_BTN)
    tint = Colors.BUTTON_PRESSED if settings_down else Colors.BUTTON_NORMAL
    rl.draw_texture_ex(self._settings_img, rl.Vector2(SETTINGS_BTN.x, SETTINGS_BTN.y), 0.0, 1.0, tint)

    # Home/Flag button
    flag_pressed = mouse_down and rl.check_collision_point_rec(mouse_pos, HOME_BTN)
    button_img = self._flag_img if ui_state.started else self._home_img
    button_pos = rl.Vector2(HOME_BTN.x, HOME_BTN.y)
    icon_opacity = 1.0

    if gui_app.sunnypilot_ui():
      button_img, button_pos, icon_opacity = SidebarSP._get_home_icon(self, button_img)

    tint = Colors.BUTTON_PRESSED if (ui_state.started and flag_pressed) else Colors.BUTTON_NORMAL
    if icon_opacity < 1.0:
      tint = rl.Color(tint[0], tint[1], tint[2], int(255 * icon_opacity))
    rl.draw_texture_ex(button_img, button_pos, 0.0, 1.0, tint)

    # Microphone button
    if self._recording_audio:
      self._mic_indicator_rect = rl.Rectangle(rect.x + rect.width - 130, rect.y + 245, 75, 40)

      mic_pressed = mouse_down and rl.check_collision_point_rec(mouse_pos, self._mic_indicator_rect)
      bg_color = rl.Color(Colors.DANGER.r, Colors.DANGER.g, Colors.DANGER.b, int(255 * 0.65)) if mic_pressed else Colors.DANGER

      rl.draw_rectangle_rounded(self._mic_indicator_rect, 1, 10, bg_color)
      rl.draw_texture_ex(self._mic_img, rl.Vector2(self._mic_indicator_rect.x + (self._mic_indicator_rect.width - self._mic_img.width) / 2,
                         self._mic_indicator_rect.y + (self._mic_indicator_rect.height - self._mic_img.height) / 2), 0.0, 1.0, Colors.WHITE)

  def _draw_network_indicator(self, rect: rl.Rectangle):
    if not ui_state.sidebar_show_network:
      return

    # Signal strength dots
    x_start = rect.x + 58
    y_pos = rect.y + 196
    dot_size = 27
    dot_spacing = 37

    for i in range(5):
      color = Colors.WHITE if i < self._net_strength else Colors.GRAY
      x = int(x_start + i * dot_spacing + dot_size // 2)
      y = int(y_pos + dot_size // 2)
      rl.draw_circle(x, y, dot_size // 2, color)

    # Network type text
    text_y = rect.y + 247
    text_pos = rl.Vector2(rect.x + 58, text_y)
    text, font_size = tr(self._net_type), FONT_SIZE
    # The mic indicator sits on the same row, so the IP only shows while it's hidden
    if self._net_ip and not self._recording_audio:
      text = self._net_ip
      max_width = rect.width - 58 - METRIC_MARGIN
      font_size = min(FONT_SIZE, FONT_SIZE * max_width / measure_text_cached(self._font_regular, text, FONT_SIZE).x)
    rl.draw_text_ex(self._font_regular, text, text_pos, font_size, 0, Colors.WHITE)

  def _draw_metrics(self, rect: rl.Rectangle):
    if gui_app.cloudypilot_ui():
      # Spacing stays sized for four so hidden metrics don't spread the rest apart
      _, start_y, spacing = SidebarSP._draw_metrics_w_sunnylink(self, rect, self._temp_status, self._panda_status, self._connect_status)
      self._tiles_start_y, self._tiles_spacing = start_y, spacing
      tiles = self._tiles()
      # The panel enforces the cap, but params can also be set from outside it
      self._visible_keys = [key for key in self._tile_order() if tiles[key][0]][:MAX_TILES]
      if self._drag_key not in self._visible_keys:
        self._drag_key = None

      layout = [key for key in self._visible_keys if key != self._drag_key]
      if self._drag_key is not None:
        layout.insert(self._drop_index(), self._drag_key)

      self._tile_rects = {}
      for idx, key in enumerate(layout):
        target_y = start_y + idx * spacing
        self._tile_rects[key] = rl.Rectangle(rect.x + METRIC_MARGIN, target_y, METRIC_WIDTH, METRIC_HEIGHT)
        y = self._tile_y.get(key, target_y)
        y = target_y if abs(target_y - y) < 0.5 else y + (target_y - y) * TILE_SLIDE_RATE
        self._tile_y[key] = y
        if key != self._drag_key:
          self._draw_metric(rect, tiles[key][1], y)

      # Drawn last so it stays on top of the tiles it passes over
      if self._drag_key is not None:
        self._draw_metric(rect, tiles[self._drag_key][1], self._dragged_top(), lifted=True)

      return

    metrics = [(self._temp_status, 338), (self._panda_status, 496), (self._connect_status, 654)]

    for metric, y_offset in metrics:
      self._draw_metric(rect, metric, rect.y + y_offset)

  def _draw_metric(self, rect: rl.Rectangle, metric: MetricData, y: float, lifted: bool = False):
    metric_rect = rl.Rectangle(rect.x + METRIC_MARGIN, y, METRIC_WIDTH, METRIC_HEIGHT)
    if lifted:
      rl.draw_rectangle_rounded(metric_rect, 0.3, 10, Colors.LIFTED_BG)
    # Draw colored left edge (clipped rounded rectangle)
    edge_rect = rl.Rectangle(metric_rect.x + 4, metric_rect.y + 4, 100, 118)
    rl.begin_scissor_mode(int(metric_rect.x + 4), int(metric_rect.y), 18, int(metric_rect.height))
    rl.draw_rectangle_rounded(edge_rect, 0.3, 10, metric.color)
    rl.end_scissor_mode()

    # Draw border
    rl.draw_rectangle_rounded_lines_ex(metric_rect, 0.3, 10, 3 if lifted else 2, Colors.WHITE if lifted else Colors.METRIC_BORDER)

    # Draw label and value
    labels = [tr(metric.label), tr(metric.value)]
    text_y = metric_rect.y + (metric_rect.height / 2 - len(labels) * FONT_SIZE * FONT_SCALE)
    for text in labels:
      text_size = measure_text_cached(self._font_bold, text, FONT_SIZE)
      text_y += text_size.y
      text_pos = rl.Vector2(
        metric_rect.x + 22 + (metric_rect.width - 22 - text_size.x) / 2,
        text_y
      )
      rl.draw_text_ex(self._font_bold, text, text_pos, FONT_SIZE, 0, Colors.WHITE)
