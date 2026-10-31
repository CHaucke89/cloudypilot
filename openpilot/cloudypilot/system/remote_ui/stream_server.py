#!/usr/bin/env python3
"""
OpenPilot UI Streaming Server - Fixed Real-Time Version
Real-time WebSocket streaming with proper frame broadcasting
"""

import os
import time
import json
import socket
import struct
import mmap
import subprocess
import threading
import base64
from collections import deque

from openpilot.cloudypilot.system.remote_ui.deps import ensure_deps
ensure_deps()

from flask import Flask, render_template_string, request, jsonify, Response, send_from_directory
from flask_sock import Sock
from openpilot.cloudypilot.system.remote_ui.client_state import ClientStateWriter

app = Flask(__name__)
sock = Sock(app)

# Shared memory configuration
SHM_NAME = "/openpilot_ui_frames"
# Match C++ SharedFrame packed struct:
# timestamp(8) + width(4) + height(4) + size(4) + format(4) + ready(1) + padding(6) = 31 bytes, then data
FRAME_DATA_SIZE = 4 * 1920 * 1080  # 8,294,400 bytes
METADATA_SIZE = 31  # Packed struct metadata
SHM_SIZE = METADATA_SIZE + FRAME_DATA_SIZE  # Total size

TOUCH_SOCKET_PATH = '/tmp/ui_touch_socket'

# Binary frame message: type(1) + timestamp ms(8) + width(4) + height(4) + source width(2) + source height(2),
# then JPEG bytes. Source size is the UI's real resolution, which input coordinates are in.
FRAME_MSG_TYPE = 1
FRAME_HEADER_FMT = '<BQIIHH'

# Client feedback older than this no longer counts towards the published network delay
FEEDBACK_STALE_S = 3.0

websocket_clients = set()
clients_lock = threading.Lock()
client_state: ClientStateWriter | None = None
client_feedback: dict[int, tuple[float, float]] = {}  # client id -> (monotonic time, queue delay ms)
client_view_widths: dict[int, int] = {}  # client id -> frame width the browser wants


def publish_requested_width():
  """One encode is shared by every client, so the widest request wins. Caller holds clients_lock."""
  if client_state is not None:
    client_state.set_requested_width(max(client_view_widths.values(), default=0))


def publish_network_delay():
  """Publish the worst fresh client queue delay so the UI can back off. Caller holds clients_lock."""
  now = time.monotonic()
  for cid in [cid for cid, (t, _) in client_feedback.items() if now - t > FEEDBACK_STALE_S]:
    del client_feedback[cid]
  if client_state is not None:
    client_state.set_network_delay_ms(max((d for _, d in client_feedback.values()), default=0))


class InputForwarder:
  """Keeps one connection to the UI's touch injector and streams newline-delimited JSON over it."""

  def __init__(self, path=TOUCH_SOCKET_PATH):
    self.path = path
    self.sock = None
    self.lock = threading.Lock()

  def _connect(self):
    self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    self.sock.settimeout(0.5)
    self.sock.connect(self.path)

  def _close(self):
    if self.sock is not None:
      try:
        self.sock.close()
      except OSError:
        pass
      self.sock = None

  def send(self, event: dict):
    payload = (json.dumps({**event, 'timestamp': time.monotonic()}) + '\n').encode()
    with self.lock:
      # Retry once with a fresh connection in case the UI restarted.
      for attempt in range(2):
        try:
          if self.sock is None:
            self._connect()
          assert self.sock is not None
          self.sock.sendall(payload)
          return
        except OSError:
          self._close()
          if attempt:
            raise


input_forwarder = InputForwarder()


class DriveState:
  """Tracks whether openpilot is engaged so remote input can be refused while driving."""

  def __init__(self):
    self.engaged = False

  def start(self):
    try:
      import cereal.messaging as messaging
    except ImportError as e:
      # The UI process applies the same gate, so this only costs the browser banner.
      print(f"DriveState: cereal unavailable, not gating input here: {e}")
      return

    def loop():
      sm = messaging.SubMaster(['deviceState', 'selfdriveState', 'selfdriveStateSP'])
      while True:
        sm.update(200)
        self.engaged = bool(
          sm['deviceState'].started and (sm['selfdriveState'].enabled or sm['selfdriveStateSP'].mads.enabled)
        )

    threading.Thread(target=loop, daemon=True).start()


drive_state = DriveState()


# Frame cache for efficient streaming
class FrameCache:
  def __init__(self, max_frames=3):
    self.frames = deque(maxlen=max_frames)
    self.lock = threading.Lock()
    self.latest_timestamp = 0
    self.latest_frame = None

  def add_frame(self, timestamp: int, data: bytes, width: int, height: int, source_width: int = 0, source_height: int = 0):
    with self.lock:
      if timestamp > self.latest_timestamp:
        # Pack the WebSocket message once here instead of once per client.
        packet = struct.pack(FRAME_HEADER_FMT, FRAME_MSG_TYPE, timestamp, width, height,
                             source_width or width, source_height or height) + data
        frame_info = {'timestamp': timestamp, 'data': data, 'packet': packet, 'size': len(data), 'width': width, 'height': height}
        self.frames.append(frame_info)
        self.latest_timestamp = timestamp
        self.latest_frame = frame_info
        return True
      return False

  def get_latest(self):
    with self.lock:
      return self.latest_frame

  def get_stats(self):
    with self.lock:
      total_size = sum(f['size'] for f in self.frames)
      return {'frames_cached': len(self.frames), 'total_memory_kb': total_size // 1024, 'latest_timestamp': self.latest_timestamp}


frame_cache = FrameCache()


# Shared memory reader
class SharedMemoryReader:
  def __init__(self):
    self.shm_fd = None
    self.shm_map = None
    self.running = False
    self.last_timestamp = 0

  def connect(self):
    """Connect to shared memory created by Qt application"""
    try:
      # Open existing shared memory
      shm_path = f"/dev/shm{SHM_NAME}"

      # Check if file exists and get its size
      if os.path.exists(shm_path):
        stat_info = os.stat(shm_path)
        actual_size = stat_info.st_size

        if actual_size == 0:
          print("Shared memory exists but is empty (0 bytes)")
          return False
        elif actual_size < SHM_SIZE:
          print(f"Shared memory exists but is smaller than expected: {actual_size} < {SHM_SIZE}")
          # Try to map with the actual size instead
          self.shm_fd = os.open(shm_path, os.O_RDONLY)
          self.shm_map = mmap.mmap(self.shm_fd, actual_size, mmap.MAP_SHARED, mmap.PROT_READ)
          print(f"Connected to shared memory with reduced size: {actual_size} bytes")
          return True
        else:
          # Normal case - full size available
          self.shm_fd = os.open(shm_path, os.O_RDONLY)
          self.shm_map = mmap.mmap(self.shm_fd, SHM_SIZE, mmap.MAP_SHARED, mmap.PROT_READ)
          print(f"Connected to shared memory: {SHM_NAME} ({SHM_SIZE} bytes)")
          return True
      else:
        print(f"Shared memory not found at {shm_path}")
        return False

    except Exception as e:
      print(f"Failed to connect to shared memory: {e}")
      return False

  def read_frame(self):
    """Read frame from shared memory"""
    if not self.shm_map:
      return None

    try:
      # Read metadata - matching C++ packed SharedFrame struct
      self.shm_map.seek(0)
      timestamp = struct.unpack('<Q', self.shm_map.read(8))[0]  # uint64_t (little-endian)
      width = struct.unpack('<I', self.shm_map.read(4))[0]  # uint32_t
      height = struct.unpack('<I', self.shm_map.read(4))[0]  # uint32_t
      size = struct.unpack('<I', self.shm_map.read(4))[0]  # uint32_t
      format_type = struct.unpack('<I', self.shm_map.read(4))[0]  # uint32_t
      ready = struct.unpack('B', self.shm_map.read(1))[0]  # uint8_t

      # Source (pre-scaling) size, then 2 bytes of padding. Zero from writers that predate scaling.
      source_width, source_height = struct.unpack('<HH', self.shm_map.read(4))
      self.shm_map.read(2)

      if ready == 0 or size == 0 or timestamp <= self.last_timestamp:
        return None

      # Data starts right after padding (at offset 31)
      frame_data = self.shm_map.read(size)

      self.last_timestamp = timestamp

      return {'timestamp': timestamp, 'width': width, 'height': height, 'source_width': source_width, 'source_height': source_height,
              'size': size, 'format': 'jpeg' if format_type == 1 else 'raw', 'data': frame_data}
    except Exception as e:
      print(f"Error reading frame: {e}")
      return None

  def start_monitoring(self):
    """Start monitoring shared memory for new frames"""
    self.running = True

    def monitor_loop():
      retry_count = 0
      frame_count = 0

      while self.running:
        # Try to connect if not connected
        if not self.shm_map:
          if self.connect():
            retry_count = 0
          else:
            retry_count += 1
            time.sleep(2 if retry_count < 10 else 10)
            continue

        # Read frame
        frame = self.read_frame()
        if frame:
          frame_count += 1
          # Add to cache
          if frame_cache.add_frame(frame['timestamp'], frame['data'], frame['width'], frame['height'],
                                   frame['source_width'], frame['source_height']):
            # Debug: Check if frame data is valid JPEG
            if frame_count % 10 == 0:
              # Check JPEG header
              if frame['data'][:2] == b'\xff\xd8':
                print(f"Frame {frame_count}: Valid JPEG, {frame['size']} bytes, {frame['width']}x{frame['height']}")
              else:
                print(f"Frame {frame_count}: INVALID DATA! First bytes: {frame['data'][:10].hex() if frame['data'] else 'empty'}")

        time.sleep(0.05)  # Check 20 times per second for low latency

    thread = threading.Thread(target=monitor_loop, daemon=True)
    thread.start()
    print("Frame monitoring started")

  def close(self):
    """Clean up shared memory connection"""
    self.running = False
    if self.shm_map:
      self.shm_map.close()
    if self.shm_fd:
      os.close(self.shm_fd)


shm_reader = SharedMemoryReader()

# Enhanced HTML with improved WebSocket handling
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
  <title>cloudypilot Remote UI</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover, user-scalable=no, maximum-scale=1">
  <meta name="theme-color" content="#000000">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="cloudypilot">
  <link rel="manifest" href="/remote_ui.webmanifest">
  <link rel="stylesheet" href="/remote_ui.css">
</head>
<body>
  <div id="ui-container">
    <canvas id="ui" width="2160" height="1080"></canvas>
    <div class="status">
      <div class="status-indicator" id="status-indicator"></div>
      <span id="status-text">Connecting...</span>
    </div>
    <div class="stats" id="stats">
      FPS: 0 | Frames: 0 | Latency: 0ms
    </div>
    <div id="debug"></div>
    <button id="res-toggle" type="button" title="Stream resolution">Res: Auto</button>
  </div>

  <script src="/remote_ui.js"></script>
</body>
</html>
"""


@app.route('/')
def index():
  return render_template_string(HTML_PAGE)


@app.route('/remote_ui.js')
def remote_ui_js():
  return send_from_directory(os.path.dirname(__file__), 'remote_ui_client.js')


@app.route('/remote_ui.css')
def remote_ui_css():
  return send_from_directory(os.path.dirname(__file__), 'remote_ui.css')


@app.route('/remote_ui.webmanifest')
def remote_ui_manifest():
  return send_from_directory(os.path.dirname(__file__), 'remote_ui.webmanifest')


def forward_input(event) -> bool:
  """Forward one input event to the UI. Returns False if it was dropped."""
  if not isinstance(event, dict) or drive_state.engaged:
    return False
  try:
    input_forwarder.send(event)
    return True
  except OSError as e:
    print(f"Failed to send input event: {e}")
    return False


@app.route('/input', methods=['POST'])
def handle_input():
  """Handle input events from web client (fallback for when the WebSocket is down)"""
  data = request.get_json(silent=True)
  if drive_state.engaged:
    return jsonify({'status': 'blocked', 'message': 'Remote input is disabled while engaged'}), 409
  if not forward_input(data):
    return jsonify({'status': 'error', 'message': 'Failed to send input event'}), 500
  return jsonify({'status': 'success'})


def handle_client_message(ws, client_id, data):
  try:
    msg = json.loads(data)
  except (json.JSONDecodeError, TypeError):
    return
  if not isinstance(msg, dict):
    return

  msg_type = msg.get('type')
  if msg_type == 'input':
    forward_input(msg.get('event'))
  elif msg_type == 'feedback':
    try:
      queue_delay = max(0.0, float(msg.get('queue_delay_ms', 0)))
    except (TypeError, ValueError):
      return
    with clients_lock:
      client_feedback[client_id] = (time.monotonic(), queue_delay)
      publish_network_delay()
  elif msg_type == 'view':
    try:
      width = max(0, int(msg.get('width', 0)))
    except (TypeError, ValueError):
      return
    with clients_lock:
      client_view_widths[client_id] = width
      publish_requested_width()
  elif msg_type == 'request_frame':
    latest = frame_cache.get_latest()
    if latest:
      ws.send(latest['packet'])


@sock.route('/stream')
def stream(ws):
  """WebSocket endpoint for real-time frame streaming and input"""
  client_id = id(ws)
  print(f"Client {client_id} connected")

  with clients_lock:
    websocket_clients.add(ws)
    client_count = len(websocket_clients)
    if client_state is not None:
      client_state.set_client_count(client_count)

  print(f"Total clients: {client_count}")

  try:
    last_sent_timestamp = 0
    last_stats_sent = 0.0
    input_blocked = None

    # Send current frame immediately if available
    latest = frame_cache.get_latest()
    if latest:
      ws.send(latest['packet'])
      last_sent_timestamp = latest['timestamp']
      print(f"Sent initial frame to client {client_id}")

    # Main streaming loop
    while True:
      try:
        if drive_state.engaged != input_blocked:
          input_blocked = drive_state.engaged
          ws.send(json.dumps({'type': 'status', 'input_blocked': input_blocked}))

        latest = frame_cache.get_latest()
        if latest and latest['timestamp'] > last_sent_timestamp:
          ws.send(latest['packet'])
          last_sent_timestamp = latest['timestamp']
        elif (time.monotonic() - last_stats_sent) >= 5.0:
          stats = frame_cache.get_stats()
          ws.send(json.dumps({'type': 'stats', 'frames_cached': stats['frames_cached'], 'memory_kb': stats['total_memory_kb']}))
          last_stats_sent = time.monotonic()
      except Exception as e:
        print(f"Error sending to client {client_id}: {e}")
        break

      # Wait for client messages (input, feedback, frame requests) instead of sleeping, so
      # input is forwarded as soon as it arrives. Then drain anything else already queued.
      data = ws.receive(timeout=0.02)
      while data:
        handle_client_message(ws, client_id, data)
        data = ws.receive(timeout=0)

  except Exception as e:
    print(f"Client {client_id} error: {e}")
  finally:
    with clients_lock:
      websocket_clients.discard(ws)
      client_feedback.pop(client_id, None)
      client_view_widths.pop(client_id, None)
      client_count = len(websocket_clients)
      if client_state is not None:
        client_state.set_client_count(client_count)
      publish_network_delay()
      publish_requested_width()
    print(f"Client {client_id} disconnected. Total clients: {client_count}")


@app.route('/stats')
def get_stats():
  """Get memory and performance statistics"""
  stats = frame_cache.get_stats()
  with clients_lock:
    stats['websocket_clients'] = len(websocket_clients)
  return jsonify(stats)


# Alternative SSE endpoint for browsers that have WebSocket issues
@app.route('/stream-sse')
def stream_sse():
  """Server-Sent Events endpoint as fallback"""

  def generate():
    last_timestamp = 0
    while True:
      latest = frame_cache.get_latest()
      if latest and latest['timestamp'] > last_timestamp:
        last_timestamp = latest['timestamp']
        data = {
          'type': 'frame',
          'timestamp': latest['timestamp'],
          'width': latest['width'],
          'height': latest['height'],
          'data': base64.b64encode(latest['data']).decode('utf-8'),
        }
        yield f"data: {json.dumps(data)}\n\n"
      else:
        # Send heartbeat
        yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
      time.sleep(0.1)

  return Response(generate(), mimetype="text/event-stream")


def wait_for_wifi(interface="wlan0", timeout=10, delay=2):
  """Wait for network connection"""
  print("Waiting for network connection...")
  for _ in range(timeout // delay):
    try:
      result = subprocess.run(["ip", "route", "show", "dev", interface], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
      if result.stdout.strip():
        print("Network is up.")
        return True
    except Exception:
      pass
    time.sleep(delay)
  print("Network not detected, continuing anyway...")
  return False


def main() -> None:
  global client_state
  client_state = ClientStateWriter()
  wait_for_wifi()

  print("=" * 60)
  print("cloudypilot Remote UI Streaming Server")
  print("=" * 60)
  print("✅ Zero disk storage - Memory only")
  print("✅ WebSocket real-time streaming")
  print("✅ Automatic frame broadcasting")
  print("=" * 60)

  # Start shared memory monitoring
  shm_reader.start_monitoring()
  drive_state.start()

  # Run Flask with WebSocket support
  try:
    app.run(host='0.0.0.0', port=8081, debug=False)
  finally:
    client_state.close()
    shm_reader.close()
