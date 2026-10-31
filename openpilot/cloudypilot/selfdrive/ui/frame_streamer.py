"""Frame streamer for the raylib/pyray openpilot UI.

Python port of the old Qt ``frame_streamer.cc``. Instead of ``QPixmap::grab()``
on a QWidget, this captures the current raylib framebuffer with
``load_image_from_screen()`` and writes a JPEG-compressed frame plus metadata
into POSIX shared memory. Only the GPU readback happens on the render thread;
copying the pixels, resizing and JPEG encoding run on a worker thread (Pillow
releases the GIL for those), so encoding doesn't add to UI frame time. ``openpilot.cloudypilot.system.remote_ui.stream_server`` reads that shared memory and
broadcasts frames to browsers over WebSocket.
"""

import io
import struct
import threading
import time
from multiprocessing import shared_memory as shm

from PIL import Image
import pyray as pr

from openpilot.cloudypilot.system.remote_ui.client_state import ClientStateReader

SHM_NAME = "openpilot_ui_frames"  # created at /dev/shm/openpilot_ui_frames
FRAME_DATA_SIZE = 4 * 1920 * 1080  # 8,294,400 bytes (max 1080p RGBA)
METADATA_SIZE = 31
SHM_SIZE = METADATA_SIZE + FRAME_DATA_SIZE

# timestamp, width, height, size, format, ready, source width, source height (frame size before scaling)
HEADER_FMT = "<QIIIIBHH2x"

FORMAT_JPEG = 1
JPEG_QUALITY = 85
FRAME_RATE_LIMIT = 10  # FPS

DISCONNECTED_FRAME_RATE_LIMIT = 1
DISCONNECTED_JPEG_QUALITY = 60
MIN_CONNECTED_FRAME_RATE_LIMIT = 4
MAX_CONNECTED_FRAME_RATE_LIMIT = 10
MIN_JPEG_QUALITY = 55
MAX_JPEG_QUALITY = 90
ADAPT_DECAY = 0.75
ADAPT_RECOVER_S = 2.0
ADAPT_HIGH_PRESSURE = 1.1
ADAPT_LOW_PRESSURE = 0.6
JPEG_SIZE_BUDGET_AT_10_FPS = 220_000
# Encode scales offered to browsers. Only 0.5 is offered below full: it's an exact 2x2 box
# reduce, which with the smaller encode costs less than encoding full size. Any other
# smooth resize (e.g. 0.75 bilinear or box) costs more CPU than the encode it saves.
SCALE_STEPS = (0.5, 1.0)
# The browser may upscale by up to this much rather than get the next larger step.
MAX_BROWSER_UPSCALE = 1.33
# Queueing delay browsers can see before the link counts as congested.
NETWORK_DELAY_BUDGET_MS = 250.0


class FrameStreamer:
  def __init__(self):
    self.last_capture_time = 0.0
    self.frame_interval = 1.0 / FRAME_RATE_LIMIT
    self.shm = None
    self.client_state = ClientStateReader()
    self.client_connected = False
    self.target_frame_rate = FRAME_RATE_LIMIT
    self.jpeg_quality = JPEG_QUALITY
    self.encode_pressure_ewma = 0.0
    self.last_adapt_time = 0.0
    self.scale = 1.0
    # Adaptive rate/quality state is written by both the render thread (connect/disconnect) and the worker.
    self._state_lock = threading.Lock()
    self._init_shm()

    # One-slot handoff to the encoder: the render thread only captures when the worker is idle,
    # so frames are skipped rather than queued and the readback cost isn't paid for nothing.
    self._pending = None
    self._pending_cv = threading.Condition()
    self._encoding = False
    self._running = True
    self._worker = threading.Thread(target=self._encode_loop, name="FrameStreamerEncoder", daemon=True)
    self._worker.start()

  def _set_frame_rate(self, frame_rate):
    self.target_frame_rate = max(1, frame_rate)
    self.frame_interval = 1.0 / float(self.target_frame_rate)

  def _set_disconnected_mode(self):
    self._set_frame_rate(DISCONNECTED_FRAME_RATE_LIMIT)
    self.jpeg_quality = DISCONNECTED_JPEG_QUALITY
    self.encode_pressure_ewma = 0.0

  def _set_connected_defaults(self):
    self._set_frame_rate(FRAME_RATE_LIMIT)
    self.jpeg_quality = JPEG_QUALITY
    self.encode_pressure_ewma = 0.0

  def _poll_client_state(self):
    connected = self.client_state.connected()
    if connected == self.client_connected:
      return

    self.client_connected = connected
    with self._state_lock:
      if connected:
        self._set_connected_defaults()
      else:
        self._set_disconnected_mode()

  def _pick_scale(self, width):
    requested = self.client_state.requested_width() if self.client_connected else 0
    if requested <= 0:
      return 1.0
    for scale in SCALE_STEPS:
      if width * scale * MAX_BROWSER_UPSCALE >= requested:
        return scale
    return 1.0

  def _jpeg_size_budget(self):
    return int(JPEG_SIZE_BUDGET_AT_10_FPS * (FRAME_RATE_LIMIT / float(self.target_frame_rate)))

  def _update_adaptive_rate(self, now_mono, encode_ms, jpeg_size):
    if not self.client_connected:
      return

    frame_budget_ms = 1000.0 / float(self.target_frame_rate)
    encode_pressure = max(
      encode_ms / max(frame_budget_ms, 1.0),
      jpeg_size / max(float(self._jpeg_size_budget()), 1.0),
      self.client_state.network_delay_ms() / NETWORK_DELAY_BUDGET_MS,
    )
    self.encode_pressure_ewma = (ADAPT_DECAY * self.encode_pressure_ewma) + ((1.0 - ADAPT_DECAY) * encode_pressure)
    pressure = self.encode_pressure_ewma

    if pressure > ADAPT_HIGH_PRESSURE and (now_mono - self.last_adapt_time) >= 0.5:
      if self.jpeg_quality > MIN_JPEG_QUALITY:
        self.jpeg_quality = max(MIN_JPEG_QUALITY, self.jpeg_quality - 5)
      elif self.target_frame_rate > MIN_CONNECTED_FRAME_RATE_LIMIT:
        self._set_frame_rate(self.target_frame_rate - 1)
      self.last_adapt_time = now_mono
    elif pressure < ADAPT_LOW_PRESSURE and (now_mono - self.last_adapt_time) >= ADAPT_RECOVER_S:
      if self.target_frame_rate < MAX_CONNECTED_FRAME_RATE_LIMIT:
        self._set_frame_rate(self.target_frame_rate + 1)
      elif self.jpeg_quality < MAX_JPEG_QUALITY:
        self.jpeg_quality = min(MAX_JPEG_QUALITY, self.jpeg_quality + 2)
      self.last_adapt_time = now_mono

  def _init_shm(self):
    # Match the C++ behavior: unlink any stale segment, then (re)create.
    try:
      stale = shm.SharedMemory(name=SHM_NAME)
      stale.close()
      stale.unlink()
    except FileNotFoundError:
      pass
    except Exception as e:
      print(f"FrameStreamer: could not clear stale shm: {e}")

    try:
      self.shm = shm.SharedMemory(name=SHM_NAME, create=True, size=SHM_SIZE)
      # Zero the header so a reader never sees a stale ready flag.
      buf = self.shm.buf
      assert buf is not None
      buf[0:METADATA_SIZE] = b"\x00" * METADATA_SIZE
      print(f"FrameStreamer: shared memory ready ({SHM_SIZE} bytes)")
    except Exception as e:
      print(f"FrameStreamer: failed to init shared memory: {e}")
      self.shm = None

  def stream_frame(self):
    """Capture the current raylib framebuffer and hand it to the encoder thread.

    Must be called from the render thread while a frame is on screen
    (i.e. before end_drawing swaps the buffers).
    """
    if self.shm is None:
      return

    now_mono = time.monotonic()
    self._poll_client_state()
    if (now_mono - self.last_capture_time) < self.frame_interval:
      return
    with self._pending_cv:
      if self._encoding or self._pending is not None:
        return  # encoder still busy with the previous frame; try again next frame
    self.last_capture_time = now_mono

    # Ensure all queued draw commands are flushed before reading pixels.
    # This keeps remote captures complete while still sampling before end_drawing().
    flush_batch = getattr(pr, "rl_draw_render_batch_active", None)
    if callable(flush_batch):
      flush_batch()

    # GL readback has to happen here, on the thread that owns the context. The image's
    # pixel buffer is then owned by the encoder, which copies it and frees it.
    rl_image = pr.load_image_from_screen()
    capture_ms = int(time.clock_gettime(time.CLOCK_REALTIME) * 1000)
    with self._pending_cv:
      self._pending = (rl_image, capture_ms, now_mono)
      self._pending_cv.notify()

  def _encode_loop(self):
    while True:
      with self._pending_cv:
        while self._running and self._pending is None:
          self._pending_cv.wait()
        if not self._running:
          return
        job = self._pending
        self._pending = None
        if job is None:
          continue
        self._encoding = True
      try:
        self._encode(*job)
      finally:
        with self._pending_cv:
          self._encoding = False

  def _encode(self, rl_image, capture_ms, capture_mono):
    try:
      encode_start = time.monotonic()
      width = rl_image.width
      height = rl_image.height
      if not width or not height:
        return

      data_size = width * height * 4
      if data_size <= 0:
        return

      # Copy raw RGBA bytes out of raylib's buffer so it can be freed below.
      rgba = bytes(pr.ffi.buffer(rl_image.data, data_size))

      # load_image_from_screen already returns top-to-bottom orientation.
      pil_img = Image.frombuffer("RGBA", (width, height), rgba, "raw", "RGBA", 0, 1)

      pil_img = pil_img.convert("RGB")  # JPEG has no alpha channel
      # Reducing after the conversion is faster than before it (3 channels instead of 4).
      self.scale = self._pick_scale(width)
      if self.scale != 1.0:
        pil_img = pil_img.reduce(round(1 / self.scale))

      with io.BytesIO() as out:
        pil_img.save(out, format="JPEG", quality=self.jpeg_quality)
        jpeg = out.getvalue()
      encode_ms = (time.monotonic() - encode_start) * 1000.0

      if len(jpeg) > FRAME_DATA_SIZE:
        print(f"FrameStreamer: frame too large ({len(jpeg)} bytes), dropping")
        return

      shm_buf = self.shm.buf if self.shm is not None else None
      if shm_buf is None:
        return

      # Write payload first, then the header with ready=1 last, so the
      # reader never sees ready=1 pointing at stale/partial data.
      shm_buf[METADATA_SIZE : METADATA_SIZE + len(jpeg)] = jpeg
      header = struct.pack(
        HEADER_FMT,
        capture_ms,  # epoch timestamp (ms) of the capture, not the encode
        pil_img.width,
        pil_img.height,
        len(jpeg),
        FORMAT_JPEG,
        1,  # ready
        width,
        height,
      )
      shm_buf[0:METADATA_SIZE] = header
      with self._state_lock:
        self._update_adaptive_rate(capture_mono, encode_ms, len(jpeg))
    except Exception as e:
      print(f"FrameStreamer error: {e}")
    finally:
      # Free the raylib image memory to avoid leaking a frame per tick (UnloadImage is a plain free()).
      pr.unload_image(rl_image)

  def close(self):
    # Stop the encoder before unmapping shm so it can't write into a closed segment.
    with self._pending_cv:
      self._running = False
      job, self._pending = self._pending, None
      self._pending_cv.notify()
    self._worker.join(timeout=2.0)
    if job is not None:
      pr.unload_image(job[0])

    self.client_state.close()
    if self.shm is not None:
      try:
        self.shm.close()
        self.shm.unlink()
      except Exception:
        pass
      self.shm = None
