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
import queue
from typing import Set
from collections import deque

from flask import Flask, render_template_string, request, jsonify, Response
from flask_sock import Sock

app = Flask(__name__)
sock = Sock(app)

# Shared memory configuration
SHM_NAME = "/openpilot_ui_frames"
# Match C++ SharedFrame packed struct:
# timestamp(8) + width(4) + height(4) + size(4) + format(4) + ready(1) + padding(6) = 31 bytes, then data
FRAME_DATA_SIZE = 4 * 1920 * 1080  # 8,294,400 bytes
METADATA_SIZE = 31  # Packed struct metadata
SHM_SIZE = METADATA_SIZE + FRAME_DATA_SIZE  # Total size

# Global queue for frame distribution
frame_queue = queue.Queue(maxsize=10)
websocket_clients = set()
clients_lock = threading.Lock()

# Frame cache for efficient streaming
class FrameCache:
    def __init__(self, max_frames=3):
        self.frames = deque(maxlen=max_frames)
        self.lock = threading.Lock()
        self.latest_timestamp = 0
        self.latest_frame = None

    def add_frame(self, timestamp: int, data: bytes, width: int, height: int):
        with self.lock:
            if timestamp > self.latest_timestamp:
                frame_info = {
                    'timestamp': timestamp,
                    'data': data,
                    'size': len(data),
                    'width': width,
                    'height': height
                }
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
            return {
                'frames_cached': len(self.frames),
                'total_memory_kb': total_size // 1024,
                'latest_timestamp': self.latest_timestamp
            }

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
                    print(f"Shared memory exists but is empty (0 bytes)")
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
            width = struct.unpack('<I', self.shm_map.read(4))[0]      # uint32_t
            height = struct.unpack('<I', self.shm_map.read(4))[0]     # uint32_t
            size = struct.unpack('<I', self.shm_map.read(4))[0]       # uint32_t
            format_type = struct.unpack('<I', self.shm_map.read(4))[0] # uint32_t
            ready = struct.unpack('B', self.shm_map.read(1))[0]       # uint8_t

            # Skip 6 bytes of padding
            self.shm_map.read(6)

            if ready == 0 or size == 0 or timestamp <= self.last_timestamp:
                return None

            # Data starts right after padding (at offset 31)
            frame_data = self.shm_map.read(size)

            self.last_timestamp = timestamp

            return {
                'timestamp': timestamp,
                'width': width,
                'height': height,
                'size': size,
                'format': 'jpeg' if format_type == 1 else 'raw',
                'data': frame_data
            }
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
                    if frame_cache.add_frame(frame['timestamp'], frame['data'],
                                            frame['width'], frame['height']):

                        # Broadcast to all WebSocket clients
                        with clients_lock:
                            if websocket_clients:
                                # Create frame message
                                frame_msg = json.dumps({
                                    'type': 'frame',
                                    'timestamp': frame['timestamp'],
                                    'width': frame['width'],
                                    'height': frame['height'],
                                    'format': frame['format'],
                                    'data': base64.b64encode(frame['data']).decode('utf-8')
                                })

                                # Add to queue for all clients
                                try:
                                    frame_queue.put_nowait(frame_msg)
                                except queue.Full:
                                    # Remove oldest frame if queue is full
                                    try:
                                        frame_queue.get_nowait()
                                        frame_queue.put_nowait(frame_msg)
                                    except:
                                        pass

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
  <title>OpenPilot UI Stream - Real-Time</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {
      margin: 0;
      background: #000;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      overflow: hidden;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    #ui-container {
      position: relative;
      max-width: 100%;
      max-height: 100%;
    }
    #ui {
      width: 100%;
      height: auto;
      touch-action: none;
      user-select: none;
      image-rendering: optimizeSpeed;
      display: block;
    }
    .status {
      position: absolute;
      top: 10px;
      left: 10px;
      color: #fff;
      background: rgba(0,0,0,0.8);
      padding: 8px 12px;
      border-radius: 8px;
      font-size: 13px;
      display: flex;
      align-items: center;
      gap: 8px;
      backdrop-filter: blur(10px);
      z-index: 100;
    }
    .status-indicator {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #ff4444;
      animation: pulse 2s infinite;
    }
    .status-indicator.connected {
      background: #44ff44;
      animation: none;
    }
    .status-indicator.streaming {
      background: #44ff44;
      animation: pulse 1s infinite;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.3; }
    }
    .stats {
      position: absolute;
      top: 10px;
      right: 10px;
      color: #fff;
      background: rgba(0,0,0,0.8);
      padding: 8px 12px;
      border-radius: 8px;
      font-size: 11px;
      font-family: monospace;
      backdrop-filter: blur(10px);
      z-index: 100;
    }
    .touch-indicator {
      position: absolute;
      width: 40px;
      height: 40px;
      border: 2px solid #00ff00;
      border-radius: 50%;
      background: rgba(0, 255, 0, 0.2);
      pointer-events: none;
      transform: translate(-50%, -50%);
      animation: fadeOut 0.5s ease-out forwards;
      z-index: 200;
    }
    @keyframes fadeOut {
      0% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
      100% { opacity: 0; transform: translate(-50%, -50%) scale(1.5); }
    }
    .loading {
      color: #fff;
      text-align: center;
      padding: 20px;
      font-size: 18px;
    }
    #debug {
      position: absolute;
      bottom: 10px;
      left: 10px;
      color: #0f0;
      background: rgba(0,0,0,0.8);
      padding: 5px;
      font-family: monospace;
      font-size: 10px;
      max-width: 300px;
      z-index: 100;
    }
  </style>
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
  </div>

  <script>
    const canvas = document.getElementById('ui');
    const ctx = canvas.getContext('2d', { alpha: false });
    const container = document.getElementById('ui-container');
    const statusIndicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');
    const stats = document.getElementById('stats');
    const debug = document.getElementById('debug');

    let ws = null;
    let reconnectTimer = null;
    let frameCount = 0;
    let totalFrames = 0;
    let fps = 0;
    let lastFpsTime = Date.now();
    let latency = 0;
    let isConnected = false;
    let lastFrameTime = 0;

    // Optimized image rendering
    const imagePool = [];
    let currentImageIndex = 0;

    // Pre-create image objects for better performance
    for (let i = 0; i < 3; i++) {
      imagePool.push(new Image());
    }

    // FPS calculation
    function updateStats() {
      const now = Date.now();
      const elapsed = now - lastFpsTime;
      if (elapsed >= 1000) {
        fps = Math.round((frameCount * 1000) / elapsed);
        frameCount = 0;
        lastFpsTime = now;
      }
      stats.textContent = `FPS: ${fps} | Frames: ${totalFrames} | Latency: ${latency}ms`;
    }

    function renderFrame(frameData) {
      const img = imagePool[currentImageIndex];
      currentImageIndex = (currentImageIndex + 1) % imagePool.length;

      img.onload = function() {
        // Update canvas size if needed
        if (canvas.width !== img.width || canvas.height !== img.height) {
          canvas.width = img.width;
          canvas.height = img.height;
        }

        // Draw frame
        ctx.drawImage(img, 0, 0);

        frameCount++;
        totalFrames++;
        lastFrameTime = Date.now();
        updateStats();
      };

      img.onerror = function() {
        console.error('Failed to load frame');
      };

      // Set image source
      img.src = 'data:image/jpeg;base64,' + frameData;
    }

    function connectWebSocket() {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/stream`;

      console.log('Connecting to WebSocket:', wsUrl);
      debug.textContent = `Connecting to ${wsUrl}...`;

      ws = new WebSocket(wsUrl);

      ws.binaryType = 'arraybuffer';

      ws.onopen = () => {
        console.log('WebSocket connected');
        isConnected = true;
        statusIndicator.className = 'status-indicator connected';
        statusText.textContent = 'Connected - Waiting for frames';
        debug.textContent = 'Connected successfully';

        if (reconnectTimer) {
          clearTimeout(reconnectTimer);
          reconnectTimer = null;
        }

        // Request initial frame
        ws.send(JSON.stringify({ type: 'request_frame' }));
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);

          if (message.type === 'frame') {
            const receiveTime = Date.now();
            latency = Math.max(0, receiveTime - message.timestamp);

            // Update status to show streaming
            statusIndicator.className = 'status-indicator streaming';
            statusText.textContent = 'Streaming';

            // Render frame
            renderFrame(message.data);

            debug.textContent = `Frame received: ${message.width}x${message.height}, ${latency}ms latency`;
          } else if (message.type === 'stats') {
            debug.textContent = `Server stats: ${message.frames_cached} frames, ${message.memory_kb}KB`;
          }
        } catch (e) {
          console.error('Error processing message:', e);
          debug.textContent = `Error: ${e.message}`;
        }
      };

      ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        isConnected = false;
        statusIndicator.className = 'status-indicator';
        statusText.textContent = 'Disconnected - Reconnecting...';
        debug.textContent = `Disconnected: ${event.reason || 'Connection lost'}`;

        // Reconnect after 2 seconds
        if (!reconnectTimer) {
          reconnectTimer = setTimeout(connectWebSocket, 2000);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        debug.textContent = `WebSocket error occurred`;
      };
    }

    // Check for stale frames
    setInterval(() => {
      if (isConnected && Date.now() - lastFrameTime > 5000) {
        debug.textContent = 'No frames received for 5 seconds';
        // Request a frame
        if (ws && ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'request_frame' }));
        }
      }
    }, 5000);

    // Touch/click handling
    function getDeviceCoordinates(clientX, clientY) {
      const rect = canvas.getBoundingClientRect();
      const scaleX = canvas.width / rect.width;
      const scaleY = canvas.height / rect.height;
      return {
        x: Math.round((clientX - rect.left) * scaleX),
        y: Math.round((clientY - rect.top) * scaleY)
      };
    }

    function sendInput(eventData) {
      fetch('/input', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(eventData)
      }).catch(err => console.error('Input send failed:', err));
    }

    function showTouchIndicator(x, y) {
      const indicator = document.createElement('div');
      indicator.className = 'touch-indicator';
      const rect = canvas.getBoundingClientRect();
      indicator.style.left = (x + rect.left) + 'px';
      indicator.style.top = (y + rect.top) + 'px';
      container.appendChild(indicator);
      setTimeout(() => container.removeChild(indicator), 500);
    }

    // Mouse events
    canvas.addEventListener('click', (e) => {
      const coords = getDeviceCoordinates(e.clientX, e.clientY);
      showTouchIndicator(e.clientX - canvas.getBoundingClientRect().left,
                        e.clientY - canvas.getBoundingClientRect().top);
      sendInput({ type: 'click', x: coords.x, y: coords.y });
    });

    // Touch events
    canvas.addEventListener('touchstart', (e) => {
      e.preventDefault();
      if (e.touches.length === 1) {
        const touch = e.touches[0];
        const coords = getDeviceCoordinates(touch.clientX, touch.clientY);
        sendInput({ type: 'touchstart', x: coords.x, y: coords.y });
      }
    });

    // Start WebSocket connection
    connectWebSocket();

    // Update stats periodically
    setInterval(updateStats, 100);
  </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/input', methods=['POST'])
def handle_input():
    """Handle input events from web client"""
    data = request.get_json()
    event_type = data.get('type', 'click')
    print(f"Received {event_type} event: {data}")

    # Send to Qt application via Unix socket
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.connect('/tmp/ui_touch_socket')
            message = json.dumps({
                **data,
                'timestamp': time.time()
            })
            sock.send(message.encode())
            return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Failed to send input event: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@sock.route('/stream')
def stream(ws):
    """WebSocket endpoint for real-time frame streaming"""
    client_id = id(ws)
    print(f"Client {client_id} connected")

    with clients_lock:
        websocket_clients.add(ws)
        client_count = len(websocket_clients)

    print(f"Total clients: {client_count}")

    try:
        # Send current frame immediately if available
        latest = frame_cache.get_latest()
        if latest:
            initial_msg = json.dumps({
                'type': 'frame',
                'timestamp': latest['timestamp'],
                'width': latest['width'],
                'height': latest['height'],
                'format': 'jpeg',
                'data': base64.b64encode(latest['data']).decode('utf-8')
            })
            ws.send(initial_msg)
            print(f"Sent initial frame to client {client_id}")

        # Main streaming loop
        while True:
            try:
                # Wait for new frames with timeout
                frame_msg = frame_queue.get(timeout=5)

                # Send frame to this client
                ws.send(frame_msg)

                # Clear the queue item
                frame_queue.task_done()

            except queue.Empty:
                # Send keepalive/stats
                stats = frame_cache.get_stats()
                ws.send(json.dumps({
                    'type': 'stats',
                    'frames_cached': stats['frames_cached'],
                    'memory_kb': stats['total_memory_kb']
                }))
            except Exception as e:
                print(f"Error sending to client {client_id}: {e}")
                break

            # Check for client messages (like frame requests)
            data = ws.receive(timeout=0)
            if data:
                try:
                    msg = json.loads(data)
                    if msg.get('type') == 'request_frame':
                        latest = frame_cache.get_latest()
                        if latest:
                            ws.send(json.dumps({
                                'type': 'frame',
                                'timestamp': latest['timestamp'],
                                'width': latest['width'],
                                'height': latest['height'],
                                'format': 'jpeg',
                                'data': base64.b64encode(latest['data']).decode('utf-8')
                            }))
                except:
                    pass

    except Exception as e:
        print(f"Client {client_id} error: {e}")
    finally:
        with clients_lock:
            websocket_clients.discard(ws)
            client_count = len(websocket_clients)
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
                    'data': base64.b64encode(latest['data']).decode('utf-8')
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
            result = subprocess.run(["ip", "route", "show", "dev", interface],
                                  stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
            if result.stdout.strip():
                print("Network is up.")
                return True
        except:
            pass
        time.sleep(delay)
    print("Network not detected, continuing anyway...")
    return False

if __name__ == '__main__':
    wait_for_wifi()

    print("="*60)
    print("🚀 OpenPilot UI Real-Time Streaming Server")
    print("="*60)
    print("✅ Zero disk storage - Memory only")
    print("✅ WebSocket real-time streaming")
    print("✅ Automatic frame broadcasting")
    print("="*60)

    # Start shared memory monitoring
    shm_reader.start_monitoring()

    # Run Flask with WebSocket support
    try:
        app.run(host='0.0.0.0', port=8081, debug=False)
    finally:
        shm_reader.close()