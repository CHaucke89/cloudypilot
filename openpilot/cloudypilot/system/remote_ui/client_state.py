import mmap
import os
import struct

SHM_PATH = "/dev/shm/openpilot_ui_clients"
CLIENT_COUNT, NETWORK_DELAY_MS, REQUESTED_WIDTH = range(3)
FIELD_FMT = "<I"
FIELD_SIZE = struct.calcsize(FIELD_FMT)
STATE_SIZE = 3 * FIELD_SIZE


class ClientStateWriter:
  """Single writer, owned by stream_server."""

  def __init__(self):
    fd = os.open(SHM_PATH, os.O_RDWR | os.O_CREAT, 0o644)
    try:
      if os.fstat(fd).st_size < STATE_SIZE:
        os.ftruncate(fd, STATE_SIZE)
      self._map = mmap.mmap(fd, STATE_SIZE, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE)
    finally:
      os.close(fd)
    self._map[:] = bytes(STATE_SIZE)

  def _set(self, field: int, value: float) -> None:
    struct.pack_into(FIELD_FMT, self._map, field * FIELD_SIZE, max(0, min(int(value), 0xFFFFFFFF)))

  def set_client_count(self, count: int) -> None:
    self._set(CLIENT_COUNT, count)

  def set_network_delay_ms(self, delay_ms: float) -> None:
    self._set(NETWORK_DELAY_MS, delay_ms)

  def set_requested_width(self, width: int) -> None:
    self._set(REQUESTED_WIDTH, width)

  def close(self) -> None:
    # Never unlink: readers' mmaps are bound to the inode and would keep reading a stale copy.
    self._map[:] = bytes(STATE_SIZE)
    self._map.close()


class ClientStateReader:
  """Cheap enough to call every frame."""

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

  def _get(self, field: int) -> int:
    if self._map is None and not self._open():
      return 0
    assert self._map is not None
    return struct.unpack_from(FIELD_FMT, self._map, field * FIELD_SIZE)[0]

  def client_count(self) -> int:
    return self._get(CLIENT_COUNT)

  def connected(self) -> bool:
    return self.client_count() > 0

  def network_delay_ms(self) -> int:
    """Worst queueing delay reported by connected browsers, 0 if unknown."""
    return self._get(NETWORK_DELAY_MS)

  def requested_width(self) -> int:
    """Widest frame (in pixels) any connected browser wants, 0 for full resolution."""
    return self._get(REQUESTED_WIDTH)

  def close(self) -> None:
    if self._map is not None:
      self._map.close()
      self._map = None
