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
let frameWidth = canvas.width;
let frameHeight = canvas.height;
let inputBlocked = false;

// Binary frame message: type(1) + timestamp ms(8) + width(4) + height(4), then JPEG bytes
const FRAME_MSG_TYPE = 1;
const FRAME_HEADER_SIZE = 17;

// Only one frame is decoded at a time; anything arriving meanwhile replaces the pending frame.
let decoding = false;
let pendingFrame = null;

// Queueing delay = latency above the lowest latency seen recently. Device and browser clocks
// differ by a constant offset, which cancels out, so this is a skew-free congestion signal.
const LATENCY_BASELINE_WINDOW_MS = 10000;
const latencySamples = [];
let queueDelay = 0;

function updateQueueDelay(now, sampleLatency) {
  latencySamples.push({ t: now, latency: sampleLatency });
  while (latencySamples.length && now - latencySamples[0].t > LATENCY_BASELINE_WINDOW_MS) {
    latencySamples.shift();
  }
  const baseline = Math.min(...latencySamples.map(s => s.latency));
  queueDelay = Math.max(0, sampleLatency - baseline);
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
  stats.textContent = `FPS: ${fps} | Render FPS: ${renderFps} | Frames: ${totalFrames} | Latency: ${latency}ms | Queue: ${queueDelay}ms | Buffered: ${bufferedAmount}`;
}

function getViewportSize() {
  if (window.visualViewport) {
    return {
      width: window.visualViewport.width,
      height: window.visualViewport.height,
    };
  }
  return {
    width: window.innerWidth,
    height: window.innerHeight,
  };
}

function layoutCanvas() {
  const { width: vw, height: vh } = getViewportSize();
  if (!vw || !vh || !frameWidth || !frameHeight) {
    return;
  }

  const aspect = frameWidth / frameHeight;
  let displayWidth = Math.min(vw, vh * aspect);
  let displayHeight = displayWidth / aspect;

  if (displayHeight > vh) {
    displayHeight = vh;
    displayWidth = displayHeight * aspect;
  }

  canvas.style.width = `${Math.round(displayWidth)}px`;
  canvas.style.height = `${Math.round(displayHeight)}px`;
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
    queue_delay_ms: queueDelay,
    render_fps: renderFps,
    buffered_amount: ws.bufferedAmount,
    frame_age_ms: now - lastFrameTime,
  }));
}

function drawFrame(source, width, height) {
  if (canvas.width !== width || canvas.height !== height) {
    canvas.width = width;
    canvas.height = height;
    frameWidth = width;
    frameHeight = height;
    layoutCanvas();
  }

  ctx.drawImage(source, 0, 0);

  renderedFramesInWindow += 1;
  lastFrameTime = Date.now();
  frameCount++;
  totalFrames++;
  sendFeedback(false);
  updateStats();
}

function decodeFrame(blob) {
  if (window.createImageBitmap) {
    return createImageBitmap(blob).then(bitmap => {
      drawFrame(bitmap, bitmap.width, bitmap.height);
      bitmap.close();
    });
  }

  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(blob);
    const img = new Image();
    img.onload = () => {
      drawFrame(img, img.width, img.height);
      URL.revokeObjectURL(url);
      resolve();
    };
    img.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error('Failed to load frame'));
    };
    img.src = url;
  });
}

function renderFrame(blob) {
  if (decoding) {
    pendingFrame = blob;
    return;
  }

  decoding = true;
  decodeFrame(blob)
    .catch(err => console.error(err))
    .finally(() => {
      decoding = false;
      if (pendingFrame) {
        const next = pendingFrame;
        pendingFrame = null;
        renderFrame(next);
      }
    });
}

function handleBinaryMessage(buffer) {
  if (buffer.byteLength <= FRAME_HEADER_SIZE) {
    return;
  }
  const view = new DataView(buffer);
  if (view.getUint8(0) !== FRAME_MSG_TYPE) {
    return;
  }

  const timestamp = Number(view.getBigUint64(1, true));
  const width = view.getUint32(9, true);
  const height = view.getUint32(13, true);

  const receiveTime = Date.now();
  latency = Math.max(0, receiveTime - timestamp);
  updateQueueDelay(receiveTime, latency);

  statusIndicator.className = 'status-indicator streaming';
  statusText.textContent = inputBlocked ? 'Streaming - view only while engaged' : 'Streaming';

  renderFrame(new Blob([new Uint8Array(buffer, FRAME_HEADER_SIZE)], { type: 'image/jpeg' }));

  debug.textContent = `Frame received: ${width}x${height}, ${latency}ms latency`;
}

function setInputBlocked(blocked) {
  inputBlocked = blocked;
  container.classList.toggle('input-blocked', blocked);
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
      if (event.data instanceof ArrayBuffer) {
        handleBinaryMessage(event.data);
        return;
      }

      const message = JSON.parse(event.data);

      if (message.type === 'status') {
        setInputBlocked(!!message.input_blocked);
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
  if (inputBlocked) {
    return;
  }

  // Prefer the WebSocket: one persistent, ordered connection. Fall back to HTTP while reconnecting.
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: 'input', event: eventData }));
    return;
  }

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
  indicator.style.left = `${x + rect.left}px`;
  indicator.style.top = `${y + rect.top}px`;
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

// mousedown/mouseup already deliver the full press -> release, so click only shows the
// indicator. Sending a 'click' here as well would make the UI see a second tap.
canvas.addEventListener('click', (e) => {
  if (dragActive) {
    dragActive = false;
    return;
  }
  showTouchIndicator(e.clientX - canvas.getBoundingClientRect().left,
                    e.clientY - canvas.getBoundingClientRect().top);
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

// Keyboard input. Desktop keys are forwarded from document keydown/keyup. Phones have no
// key events worth using (Android reports most keys as 'Unidentified'), so the keyboard
// button focuses a hidden input and what the on-screen keyboard types is diffed against
// a fixed sentinel value.
const kbdToggle = document.getElementById('kbd-toggle');
const kbdInput = document.getElementById('kbd-input');
const KBD_SENTINEL = '  ';
const heldKeys = new Set();
const NAMED_KEYS = new Set([
  'Enter', 'Escape', 'Backspace', 'Tab', 'Delete', 'ArrowLeft', 'ArrowRight', 'ArrowUp',
  'ArrowDown', 'Home', 'End', 'PageUp', 'PageDown',
]);


function isForwardableKey(e) {
  if (e.ctrlKey || e.metaKey || e.altKey) {
    return false;  // leave browser shortcuts (copy, paste, reload...) alone
  }
  return e.key && e.key !== 'Unidentified' && e.key !== 'Process' && e.key !== 'Dead' &&
    (e.key.length === 1 || NAMED_KEYS.has(e.key));
}

function releaseHeldKeys() {
  for (const key of heldKeys) {
    sendInput({ type: 'keyup', key });
  }
  heldKeys.clear();
}

document.addEventListener('keydown', (e) => {
  if (!isForwardableKey(e)) {
    return;
  }
  // In the hidden input, text and Backspace come through its input event instead.
  if (e.target === kbdInput && (e.key.length === 1 || e.key === 'Backspace')) {
    return;
  }
  e.preventDefault();
  heldKeys.add(e.key);
  sendInput({ type: 'keydown', key: e.key, repeat: e.repeat });
});

document.addEventListener('keyup', (e) => {
  if (!heldKeys.has(e.key)) {
    return;
  }
  e.preventDefault();
  heldKeys.delete(e.key);
  sendInput({ type: 'keyup', key: e.key });
});

window.addEventListener('blur', releaseHeldKeys);

document.addEventListener('paste', (e) => {
  if (e.target === kbdInput) {
    return;
  }
  const text = e.clipboardData && e.clipboardData.getData('text');
  if (text) {
    e.preventDefault();
    sendInput({ type: 'text', text });
  }
});

function resetKbdInput() {
  kbdInput.value = KBD_SENTINEL;
  kbdInput.setSelectionRange(KBD_SENTINEL.length, KBD_SENTINEL.length);
}

function flushKbdInput() {
  const value = kbdInput.value;
  if (value.startsWith(KBD_SENTINEL)) {
    const text = value.slice(KBD_SENTINEL.length);
    if (text) {
      sendInput({ type: 'text', text });
    }
  } else {
    // Each character missing from the sentinel is one Backspace.
    const deleted = Math.max(1, KBD_SENTINEL.length - value.length);
    for (let i = 0; i < deleted; i++) {
      sendInput({ type: 'keytap', key: 'Backspace' });
    }
  }
  resetKbdInput();
}

kbdInput.addEventListener('input', (e) => {
  if (!e.isComposing) {
    flushKbdInput();
  }
});
kbdInput.addEventListener('compositionend', flushKbdInput);
kbdInput.addEventListener('focus', () => {
  resetKbdInput();
  kbdToggle.classList.add('active');
});
kbdInput.addEventListener('blur', () => kbdToggle.classList.remove('active'));

// Keep focus where it is when the button is pressed, then toggle the hidden input.
kbdToggle.addEventListener('mousedown', (e) => e.preventDefault());
kbdToggle.addEventListener('click', () => {
  if (document.activeElement === kbdInput) {
    kbdInput.blur();
  } else {
    kbdInput.focus();
  }
});

// Start WebSocket connection
layoutCanvas();
connectWebSocket();

// Update stats periodically
setInterval(updateStats, 100);
setInterval(() => sendFeedback(false), 500);

window.addEventListener('resize', layoutCanvas);
window.addEventListener('orientationchange', layoutCanvas);

if (window.visualViewport) {
  window.visualViewport.addEventListener('resize', layoutCanvas);
  window.visualViewport.addEventListener('scroll', layoutCanvas);
}
