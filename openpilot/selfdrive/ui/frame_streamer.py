"""Frame streamer for the raylib/pyray openpilot UI.

Python port of the old Qt ``frame_streamer.cc``. Instead of ``QPixmap::grab()``
on a QWidget, this captures the current raylib framebuffer with
``load_image_from_screen()`` and writes a JPEG-compressed frame plus metadata
into POSIX shared memory. ``stream_server.py`` reads that shared memory and
broadcasts frames to browsers over WebSocket.

Usage (inside the UI's raylib render loop, between begin/end drawing):

    streamer = FrameStreamer()
    for _ in gui_app.render():
        ...draw the frame...
        streamer.stream_frame()   # reads the framebuffer just drawn
    streamer.close()
"""

import ctypes
import io
import struct
import time
from multiprocessing import shared_memory as shm

from PIL import Image
import pyray as pr

# Must match stream_server.py and the legacy C++ SharedFrame struct.
SHM_NAME = "openpilot_ui_frames"  # created at /dev/shm/openpilot_ui_frames
FRAME_DATA_SIZE = 4 * 1920 * 1080  # 8,294,400 bytes (max 1080p RGBA)
METADATA_SIZE = 31                 # packed header, see HEADER_FMT below
SHM_SIZE = METADATA_SIZE + FRAME_DATA_SIZE  # 8,294,431 bytes

# Packed struct (little-endian, no alignment padding):
#   uint64 timestamp | uint32 width | uint32 height | uint32 size |
#   uint32 format | uint8 ready | uint8 padding[6]
HEADER_FMT = "<QIIIIB6x"

FORMAT_JPEG = 1
JPEG_QUALITY = 85
FRAME_RATE_LIMIT = 10  # FPS


class FrameStreamer:
    def __init__(self):
        self.last_capture_time = 0.0
        self.frame_interval = 1.0 / FRAME_RATE_LIMIT
        self.shm = None
        self._init_shm()

    def _init_shm(self):
        # Match the C++ behaviour: unlink any stale segment, then (re)create.
        try:
            stale = shm.SharedMemory(name=SHM_NAME)
            stale.close()
            stale.unlink()
        except FileNotFoundError:
            pass
        except Exception as e:  # noqa: BLE001 - best effort cleanup
            print(f"FrameStreamer: could not clear stale shm: {e}")

        try:
            self.shm = shm.SharedMemory(name=SHM_NAME, create=True, size=SHM_SIZE)
            # Zero the header so a reader never sees a stale ready flag.
            self.shm.buf[0:METADATA_SIZE] = b"\x00" * METADATA_SIZE
            print(f"FrameStreamer: shared memory ready ({SHM_SIZE} bytes)")
        except Exception as e:  # noqa: BLE001
            print(f"FrameStreamer: failed to init shared memory: {e}")
            self.shm = None

    def stream_frame(self):
        """Capture the current raylib framebuffer and publish it.

        Must be called from the render thread while a frame is on screen
        (i.e. before end_drawing swaps the buffers).
        """
        if self.shm is None:
            return

        now = time.time()
        if (now - self.last_capture_time) < self.frame_interval:
            return
        self.last_capture_time = now

        rl_image = pr.load_image_from_screen()
        try:
            width = rl_image.width
            height = rl_image.height
            # rl_image.data is a cffi pointer; int() yields its raw address.
            addr = int(rl_image.data)
            if not width or not height or addr == 0:
                return

            # Wrap the raw RGBA framebuffer without copying.
            data_size = width * height * 4
            buf = (ctypes.c_ubyte * data_size).from_address(addr)

            # load_image_from_screen already returns top-to-bottom orientation.
            pil_img = Image.frombuffer("RGBA", (width, height), buf, "raw", "RGBA", 0, 1)
            pil_img = pil_img.convert("RGB")  # JPEG has no alpha channel

            with io.BytesIO() as out:
                pil_img.save(out, format="JPEG", quality=JPEG_QUALITY)
                jpeg = out.getvalue()

            if len(jpeg) > FRAME_DATA_SIZE:
                print(f"FrameStreamer: frame too large ({len(jpeg)} bytes), dropping")
                return

            # Write payload first, then the header with ready=1 last, so the
            # reader never sees ready=1 pointing at stale/partial data.
            self.shm.buf[METADATA_SIZE:METADATA_SIZE + len(jpeg)] = jpeg
            header = struct.pack(
                HEADER_FMT,
                int(now * 1000),  # timestamp (ms)
                width,
                height,
                len(jpeg),
                FORMAT_JPEG,
                1,                # ready
            )
            self.shm.buf[0:METADATA_SIZE] = header
        except Exception as e:  # noqa: BLE001
            print(f"FrameStreamer error: {e}")
        finally:
            # Free the raylib image memory to avoid leaking a frame per tick.
            pr.unload_image(rl_image)

    def close(self):
        if self.shm is not None:
            try:
                self.shm.close()
                self.shm.unlink()
            except Exception:  # noqa: BLE001
                pass
            self.shm = None
