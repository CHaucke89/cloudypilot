"""Remote UI client connection state shared between stream_server and the UI.

Replaces the ``RemoteUIClientConnected`` param. Param writes go through a
tmp file + fsync + rename, which is far too heavy to do from the streaming
path. Instead, ``stream_server`` owns a tiny POSIX shared memory segment at
``/dev/shm/openpilot_ui_clients`` holding the current WebSocket client count,
and the UI maps it read-only. Reads are a plain memory access, no syscalls.

The writer never unlinks the segment: a reader's mmap is bound to the inode,
so recreating the file would leave readers looking at a stale copy forever.
"""

import mmap
import os
import struct

SHM_PATH = "/dev/shm/openpilot_ui_clients"
STATE_FMT = "<I"  # uint32 client count
STATE_SIZE = struct.calcsize(STATE_FMT)


class ClientStateWriter:
  """Owned by stream_server. Publishes the number of connected browsers."""

  def __init__(self):
    fd = os.open(SHM_PATH, os.O_RDWR | os.O_CREAT, 0o644)
    try:
      if os.fstat(fd).st_size < STATE_SIZE:
        os.ftruncate(fd, STATE_SIZE)
      self._map = mmap.mmap(fd, STATE_SIZE, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE)
    finally:
      os.close(fd)
    self.set_client_count(0)

  def set_client_count(self, count: int) -> None:
    struct.pack_into(STATE_FMT, self._map, 0, max(0, count))

  def close(self) -> None:
    self.set_client_count(0)
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
    return struct.unpack_from(STATE_FMT, self._map, 0)[0] > 0

  def close(self) -> None:
    if self._map is not None:
      self._map.close()
      self._map = None
