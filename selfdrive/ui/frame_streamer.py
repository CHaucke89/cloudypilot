import time
import struct
import io
import ctypes
import multiprocessing.shared_memory as shm
from PIL import Image
import pyray as rl

# Shared Memory Constants
SHM_NAME = "openpilot_ui_frames"
# 31 bytes header + ~8MB buffer (1920*1080*4 rounded up)
SHM_SIZE = 8294431
JPEG_QUALITY = 85
FRAME_RATE_LIMIT = 10  # FPS

class FrameStreamer:
    def __init__(self):
        self.last_capture_time = 0
        self.frame_interval = 1.0 / FRAME_RATE_LIMIT
        self.shm = None
        self._init_shm()

    def _init_shm(self):
        try:
            # Try to create new shared memory
            self.shm = shm.SharedMemory(name=ta, create=True, size=SHM_SIZE)
        except FileExistsError:
            # Connect to existing if server is already running/didn't clean up
            self.shm = shm.SharedMemory(name=SHM_NAME)
        except Exception as e:
            print(f"FrameStreamer: Failed to init shared memory: {e}")

    def stream_frame(self):
        """
        Captures the current Raylib buffer, comrlesses it, and writes to SHM.
        Must be called inside the main Raylib drawing loop.
        """
        if self.shm is None:
            return

        now = time.monotonic()
        if (now - self.last_capture_time) < self.frame_interval:
            return

        self.last_capture_time = now

        # 1. Capture Image from Raylib (Raw RGBA)
        # load_image_from_screen returns a pyray.Image struct
        rl_image = rl.load_image_from_screen()

        try:
            width = rl_image.width
            height = rl_image.height

            # 2. Convert Raylib C-Struct data to Python Bytes
            # rl_image.data is a void pointer. We access it via ctypes.
            data_size = width * height * 4
            if rl_image.data == 0:
                return

            if hasattr(rl_image.data, '__int__'):
                data_ptr = int(rl_image.data)
            else:
                # Handle cffi void* pointer
                import ctypes
                data_ptr = int(ctypes.cast(rl_image.data, ctypes.c_void_p).value)
            c_ubyte_ptr = (ctypes.c_ubyte * data_size).from_address(data_ptr)

            # 3. Create PIL Image and Compress to JPEG
            # 'flipped' because Raylib/GL sometimes captures upside down depending on context,
            # but load_image_from_screen usually handles this. Adjust if output is inverted.
            pil_img = Image.frombuffer("RGBA", (width, height), c_ubyte_ptr, "raw", "RGBA", 0, 1)

            # Convert to RGB (JPEG doesn't support Alpha)
            pil_img = pil_img.convert("RGB")

            with io.BytesIO() as output:
                pil_img.save(output, format="JPEG", quality=JPEG_QUALITY)
                jpeg_bytes = output.getvalue()
                jpeg_len = len(jpeg_bytes)

            # 4. Write to Shared Memory
            # Header Format:
            # uint64_t timestamp (ms)
            # uint32_t width
            # uint32_t height
            # uint32_t size
            # uint32_t format (1 = JPEG)
            # uint8_t  ready
            # uint8_t  padding[6] (To align total header to 31 bytes per spec)

            timestamp_ms = int(now * 1000)
            header_fmt = "=QIIIIB6x" # '=' ensures standard size, no extra alignment padding
            header = struct.pack(header_fmt,
                                 timestamp_ms,
                                 width,
                                 height,
                                 jpeg_len,
                                 1, # JPEG format
                                 1) # Ready flag

            # Write Header (0-31)
            self.shm.buf[0:31] = header

            # Write Data (31-End)
            self.shm.buf[31:31+jpeg_len] = jpeg_bytes

        except Exception as e:
            print(f"FrameStreamer Error: {e}")
        finally:
            # Important: Free the Raylib image memory to prevent leaks
            rl.unload_image(rl_image)

    def close(self):
        if self.shm:
            self.shm.close()
            try:
                self.shm.unlink()
            except Exception:
                pass
