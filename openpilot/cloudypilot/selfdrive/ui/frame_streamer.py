"""Frame streamer for the raylib/pyray openpilot UI.

Python port of the old Qt ``frame_streamer.cc``. Instead of ``QPixmap::grab()``
on a QWidget, this captures the current raylib framebuffer with
``load_image_from_screen()`` and writes a JPEG-compressed frame plus metadata
into POSIX shared memory. ``openpilot.cloudypilot.system.remote_ui.stream_server`` reads that shared memory and
broadcasts frames to browsers over WebSocket.
"""

import io
import struct
import time
from multiprocessing import shared_memory as shm

from PIL import Image
import pyray as pr

from openpilot.common.params import Params

SHM_NAME = "openpilot_ui_frames"  # created at /dev/shm/openpilot_ui_frames
FRAME_DATA_SIZE = 4 * 1920 * 1080  # 8,294,400 bytes (max 1080p RGBA)
METADATA_SIZE = 31
SHM_SIZE = METADATA_SIZE + FRAME_DATA_SIZE

HEADER_FMT = "<QIIIIB6x"

FORMAT_JPEG = 1
JPEG_QUALITY = 85
FRAME_RATE_LIMIT = 10  # FPS

DISCONNECTED_FRAME_RATE_LIMIT = 1
DISCONNECTED_JPEG_QUALITY = 60
MIN_CONNECTED_FRAME_RATE_LIMIT = 4
MAX_CONNECTED_FRAME_RATE_LIMIT = 10
MIN_JPEG_QUALITY = 55
MAX_JPEG_QUALITY = 90
CLIENT_STATE_POLL_S = 0.5
ADAPT_DECAY = 0.75
ADAPT_RECOVER_S = 2.0
ADAPT_HIGH_PRESSURE = 1.1
ADAPT_LOW_PRESSURE = 0.6
JPEG_SIZE_BUDGET_AT_10_FPS = 220_000


class FrameStreamer:
  def __init__(self):
    self.last_capture_time = 0.0
    self.frame_interval = 1.0 / FRAME_RATE_LIMIT
    self.shm = None
    self.params = Params()
    self.client_connected = False
    self.target_frame_rate = FRAME_RATE_LIMIT
    self.jpeg_quality = JPEG_QUALITY
    self.encode_pressure_ewma = 0.0
    self.last_adapt_time = 0.0
    self.last_client_state_poll = 0.0
    self._init_shm()

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

  def _poll_client_state(self, now_mono):
    if (now_mono - self.last_client_state_poll) < CLIENT_STATE_POLL_S:
      return

    self.last_client_state_poll = now_mono
    try:
      connected = self.params.get_bool("RemoteUIClientConnected")
    except Exception:
      connected = False

    if connected == self.client_connected:
      return

    self.client_connected = connected
    if connected:
      self._set_connected_defaults()
    else:
      self._set_disconnected_mode()

  def _jpeg_size_budget(self):
    return int(JPEG_SIZE_BUDGET_AT_10_FPS * (FRAME_RATE_LIMIT / float(self.target_frame_rate)))

  def _update_adaptive_rate(self, now_mono, encode_ms, jpeg_size):
    if not self.client_connected:
      return

    frame_budget_ms = 1000.0 / float(self.target_frame_rate)
    pressure = max(
      encode_ms / max(frame_budget_ms, 1.0),
      jpeg_size / max(float(self._jpeg_size_budget()), 1.0),
    )
    self.encode_pressure_ewma = (ADAPT_DECAY * self.encode_pressure_ewma) + ((1.0 - ADAPT_DECAY) * pressure)

    if self.encode_pressure_ewma > ADAPT_HIGH_PRESSURE and (now_mono - self.last_adapt_time) >= 0.5:
      if self.jpeg_quality > MIN_JPEG_QUALITY:
        self.jpeg_quality = max(MIN_JPEG_QUALITY, self.jpeg_quality - 5)
      elif self.target_frame_rate > MIN_CONNECTED_FRAME_RATE_LIMIT:
        self._set_frame_rate(self.target_frame_rate - 1)
      self.last_adapt_time = now_mono
    elif self.encode_pressure_ewma < ADAPT_LOW_PRESSURE and (now_mono - self.last_adapt_time) >= ADAPT_RECOVER_S:
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
    """Capture the current raylib framebuffer and publish it.

    Must be called from the render thread while a frame is on screen
    (i.e. before end_drawing swaps the buffers).
    """
    shm_buf = self.shm.buf if self.shm is not None else None
    if shm_buf is None:
      return

    now_mono = time.monotonic()
    self._poll_client_state(now_mono)
    if (now_mono - self.last_capture_time) < self.frame_interval:
      return
    self.last_capture_time = now_mono

    # Ensure all queued draw commands are flushed before reading pixels.
    # This keeps remote captures complete while still sampling before end_drawing().
    flush_batch = getattr(pr, "rl_draw_render_batch_active", None)
    if callable(flush_batch):
      flush_batch()

    rl_image = pr.load_image_from_screen()
    try:
      encode_start = time.monotonic()
      width = rl_image.width
      height = rl_image.height
      if not width or not height:
        return

      data_size = width * height * 4
      if data_size <= 0:
        return

      # Read raw RGBA bytes from pyray's cffi pointer safely.
      rgba = bytes(pr.ffi.buffer(rl_image.data, data_size))

      # load_image_from_screen already returns top-to-bottom orientation.
      pil_img = Image.frombuffer("RGBA", (width, height), rgba, "raw", "RGBA", 0, 1)
      pil_img = pil_img.convert("RGB")  # JPEG has no alpha channel

      with io.BytesIO() as out:
        pil_img.save(out, format="JPEG", quality=self.jpeg_quality)
        jpeg = out.getvalue()
      encode_ms = (time.monotonic() - encode_start) * 1000.0

      if len(jpeg) > FRAME_DATA_SIZE:
        print(f"FrameStreamer: frame too large ({len(jpeg)} bytes), dropping")
        return

      # Write payload first, then the header with ready=1 last, so the
      # reader never sees ready=1 pointing at stale/partial data.
      shm_buf[METADATA_SIZE : METADATA_SIZE + len(jpeg)] = jpeg
      header = struct.pack(
        HEADER_FMT,
        int(time.clock_gettime(time.CLOCK_REALTIME) * 1000),  # epoch timestamp (ms)
        width,
        height,
        len(jpeg),
        FORMAT_JPEG,
        1,  # ready
      )
      shm_buf[0:METADATA_SIZE] = header
      self._update_adaptive_rate(now_mono, encode_ms, len(jpeg))
    except Exception as e:
      print(f"FrameStreamer error: {e}")
    finally:
      # Free the raylib image memory to avoid leaking a frame per tick.
      pr.unload_image(rl_image)

  def close(self):
    if self.shm is not None:
      try:
        self.shm.close()
        self.shm.unlink()
      except Exception:
        pass
      self.shm = None
