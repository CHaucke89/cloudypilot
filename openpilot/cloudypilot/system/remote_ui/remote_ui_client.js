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
let lastTelemetrySent = 0;
let renderedFramesInWindow = 0;
let renderFps = 0;
let lastRenderFpsUpdate = Date.now();

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
  const renderElapsed = now - lastRenderFpsUpdate;
  if (renderElapsed >= 1000) {
    renderFps = Math.round((renderedFramesInWindow * 1000) / renderElapsed);
    renderedFramesInWindow = 0;
    lastRenderFpsUpdate = now;
  }
  const bufferedAmount = ws && ws.readyState === WebSocket.OPEN ? ws.bufferedAmount : 0;
  stats.textContent = `FPS: ${fps} | Render FPS: ${renderFps} | Frames: ${totalFrames} | Latency: ${latency}ms | Buffered: ${bufferedAmount}`;
}

function sendFeedback(force = false) {
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    return;
  }

  const now = Date.now();
  if (!force && now - lastTelemetrySent < 250) {
    return;
  }

  lastTelemetrySent = now;
  ws.send(JSON.stringify({
    type: 'feedback',
    latency_ms: latency,
    render_fps: renderFps,
    buffered_amount: ws.bufferedAmount,
    frame_age_ms: now - lastFrameTime,
  }));
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

    renderedFramesInWindow += 1;
    lastFrameTime = Date.now();
    frameCount++;
    totalFrames++;
    sendFeedback(false);
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

let mouseDown = false;
let dragActive = false;
let dragStartX = 0;
let dragStartY = 0;
const dragThreshold = 8;

// Mouse events
canvas.addEventListener('mousedown', (e) => {
  const coords = getDeviceCoordinates(e.clientX, e.clientY);
  mouseDown = true;
  dragActive = false;
  dragStartX = e.clientX;
  dragStartY = e.clientY;
  sendInput({ type: 'mousedown', x: coords.x, y: coords.y });
});

canvas.addEventListener('mousemove', (e) => {
  if (!mouseDown) {
    return;
  }

  const moved = Math.hypot(e.clientX - dragStartX, e.clientY - dragStartY);
  if (moved >= dragThreshold) {
    dragActive = true;
  }

  const coords = getDeviceCoordinates(e.clientX, e.clientY);
  sendInput({ type: dragActive ? 'drag' : 'mousemove', x: coords.x, y: coords.y });
});

canvas.addEventListener('mouseup', (e) => {
  if (!mouseDown) {
    return;
  }

  const coords = getDeviceCoordinates(e.clientX, e.clientY);
  sendInput({ type: dragActive ? 'dragend' : 'mouseup', x: coords.x, y: coords.y });
  mouseDown = false;
  dragActive = false;
});

canvas.addEventListener('mouseleave', (e) => {
  if (!mouseDown) {
    return;
  }

  const coords = getDeviceCoordinates(e.clientX, e.clientY);
  sendInput({ type: dragActive ? 'dragend' : 'mouseup', x: coords.x, y: coords.y });
  mouseDown = false;
  dragActive = false;
});

canvas.addEventListener('click', (e) => {
  if (dragActive) {
    dragActive = false;
    return;
  }
  const coords = getDeviceCoordinates(e.clientX, e.clientY);
  showTouchIndicator(e.clientX - canvas.getBoundingClientRect().left,
                    e.clientY - canvas.getBoundingClientRect().top);
  sendInput({ type: 'click', x: coords.x, y: coords.y });
});

canvas.addEventListener('wheel', (e) => {
  e.preventDefault();
  const coords = getDeviceCoordinates(e.clientX, e.clientY);
  sendInput({ type: 'scroll', x: coords.x, y: coords.y, deltaY: e.deltaY });
}, { passive: false });

// Touch events
canvas.addEventListener('touchstart', (e) => {
  e.preventDefault();
  if (e.touches.length === 1) {
    const touch = e.touches[0];
    const coords = getDeviceCoordinates(touch.clientX, touch.clientY);
    sendInput({ type: 'touchstart', x: coords.x, y: coords.y });
  }
}, { passive: false });

canvas.addEventListener('touchmove', (e) => {
  e.preventDefault();
  if (e.touches.length === 1) {
    const touch = e.touches[0];
    const coords = getDeviceCoordinates(touch.clientX, touch.clientY);
    sendInput({ type: 'touchmove', x: coords.x, y: coords.y });
  }
}, { passive: false });

canvas.addEventListener('touchend', (e) => {
  e.preventDefault();
  const touch = e.changedTouches[0];
  if (touch) {
    const coords = getDeviceCoordinates(touch.clientX, touch.clientY);
    sendInput({ type: 'touchend', x: coords.x, y: coords.y });
  } else {
    sendInput({ type: 'touchend' });
  }
}, { passive: false });

canvas.addEventListener('touchcancel', (e) => {
  e.preventDefault();
  const touch = e.changedTouches[0];
  if (touch) {
    const coords = getDeviceCoordinates(touch.clientX, touch.clientY);
    sendInput({ type: 'touchend', x: coords.x, y: coords.y });
  } else {
    sendInput({ type: 'touchend' });
  }
}, { passive: false });

// Start WebSocket connection
connectWebSocket();

// Update stats periodically
setInterval(updateStats, 100);
setInterval(() => sendFeedback(false), 500);
