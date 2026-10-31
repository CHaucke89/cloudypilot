"""Remote UI client connection state shared between stream_server and the UI.

Replaces the ``RemoteUIClientConnected`` param. Param writes go through a
tmp file + fsync + rename, which is far too heavy to do from the streaming
path. Instead, ``stream_server`` owns a tiny POSIX shared memory segment at
``/dev/shm/openpilot_ui_clients`` holding the current WebSocket client count,
the worst network queueing delay reported by those clients and the widest
frame any of them asked for, and the UI maps it read-only. Reads are a plain memory access, no syscalls.

The writer never unlinks the segment: a reader's mmap is bound to the inode,
so recreating the file would leave readers looking at a stale copy forever.
"""

import mmap
import os
import struct

SHM_PATH = "/dev/shm/openpilot_ui_clients"
STATE_FMT = "<III"  # uint32 client count, uint32 worst client queue delay (ms), uint32 requested frame width (0 = full)
STATE_SIZE = struct.calcsize(STATE_FMT)


class ClientStateWriter:
  """Owned by stream_server. Publishes the number of connected browsers and their network delay."""

  def __init__(self):
    fd = os.open(SHM_PATH, os.O_RDWR | os.O_CREAT, 0o644)
    try:
      if os.fstat(fd).st_size < STATE_SIZE:
        os.ftruncate(fd, STATE_SIZE)
      self._map = mmap.mmap(fd, STATE_SIZE, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE)
    finally:
      os.close(fd)
    self.set_client_count(0)
    self.set_network_delay_ms(0)
    self.set_requested_width(0)

  def set_client_count(self, count: int) -> None:
    struct.pack_into("<I", self._map, 0, max(0, count))

  def set_network_delay_ms(self, delay_ms: float) -> None:
    struct.pack_into("<I", self._map, 4, max(0, min(int(delay_ms), 0xFFFFFFFF)))

  def set_requested_width(self, width: int) -> None:
    struct.pack_into("<I", self._map, 8, max(0, min(int(width), 0xFFFFFFFF)))

  def close(self) -> None:
    self.set_client_count(0)
    self.set_network_delay_ms(0)
    self.set_requested_width(0)
    self._map.close()


class ClientStateReader:
  """Used by the UI process. Cheap enough to call every frame."""

  def __init__(self):
    self._map: mmap.mmap | None = None

  def _open(self) -> bool:
    try:
      fd = os.open(SHM_PATH, os.O_RDONLY)
    except FileNotFoundError:
      return False
    try:
      if os.fstat(fd).st_size < STATE_SIZE:
        return False
      self._map = mmap.mmap(fd, STATE_SIZE, mmap.MAP_SHARED, mmap.PROT_READ)
      return True
    finally:
      os.close(fd)

  def connected(self) -> bool:
    # Retry until stream_server creates the segment; one failed open() per call is negligible.
    if self._map is None and not self._open():
      return False
    assert self._map is not None
    return struct.unpack_from("<I", self._map, 0)[0] > 0

  def network_delay_ms(self) -> int:
    """Worst queueing delay reported by connected browsers, 0 if unknown."""
    if self._map is None and not self._open():
      return 0
    assert self._map is not None
    return struct.unpack_from("<I", self._map, 4)[0]

  def requested_width(self) -> int:
    """Widest frame (in pixels) any connected browser wants, 0 for full resolution."""
    if self._map is None and not self._open():
      return 0
    assert self._map is not None
    return struct.unpack_from("<I", self._map, 8)[0]

  def close(self) -> None:
    if self._map is not None:
      self._map.close()
      self._map = None
