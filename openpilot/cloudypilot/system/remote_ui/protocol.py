"""IPC layout shared by the UI process (frame_streamer, touch_injector) and stream_server."""

import struct

# Frame shared memory at /dev/shm/<SHM_NAME>: header, then JPEG bytes.
SHM_NAME = "openpilot_ui_frames"
# timestamp, width, height, size, format, ready, source width, source height (frame size before scaling)
HEADER_FMT = "<QIIIIBHH2x"
METADATA_SIZE = struct.calcsize(HEADER_FMT)  # 31
FRAME_DATA_SIZE = 4 * 1920 * 1080  # 8,294,400 bytes (max 1080p RGBA)
SHM_SIZE = METADATA_SIZE + FRAME_DATA_SIZE
FORMAT_JPEG = 1

# Input events, as newline-delimited JSON
TOUCH_SOCKET_PATH = "/tmp/ui_touch_socket"
