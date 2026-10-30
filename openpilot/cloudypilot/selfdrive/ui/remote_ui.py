"""Remote UI bootstrap for the raylib/pyray openpilot UI.

Python equivalent of the old Qt ``main.cc``, which constructed a
``TouchInjector`` and a ``FrameStreamer`` and started them alongside the
``MainWindow``. The new openpilot UI has no ``main.cc`` to replace; it runs a
raylib render loop (``selfdrive/ui/ui.py``). So instead of owning ``main``,
this module exposes a single object you splice into that existing loop.
"""

from openpilot.cloudypilot.selfdrive.ui.frame_streamer import FrameStreamer
from openpilot.cloudypilot.selfdrive.ui.touch_injector import TouchInjector


def _engaged() -> bool:
  # Imported lazily so the standalone smoke test below doesn't need the full UI state.
  from openpilot.selfdrive.ui.ui_state import ui_state
  return ui_state.engaged


class RemoteUI:
  def __init__(self):
    # Remote taps are ignored while engaged; local touch keeps working.
    self.injector = TouchInjector(input_blocked=_engaged)
    self.injector.start()
    self.streamer = FrameStreamer()
    print("RemoteUI: streaming + input injection started")

  def stream_frame(self):
    self.injector.refresh_blocked()
    self.streamer.stream_frame()

  def close(self):
    self.streamer.close()
    self.injector.stop()
    print("RemoteUI: stopped")


if __name__ == "__main__":
  # Standalone smoke test: open a window, draw a moving box, stream it, and
  # report remote clicks. Run openpilot/cloudypilot/system/remote_ui/stream_server.py separately and open the page.
  import pyray as pr

  injector = TouchInjector()
  injector.start()
  pr.init_window(2160, 1080, "remote_ui smoke test")
  pr.set_target_fps(60)
  streamer = FrameStreamer()
  try:
    x = 0
    while not pr.window_should_close():
      x = (x + 5) % 2160
      pr.begin_drawing()
      pr.clear_background(pr.BLACK)
      pr.draw_rectangle(x, 500, 120, 120, pr.RAYWHITE)
      if pr.is_mouse_button_pressed(0):  # noqa: TID251
        p = pr.get_mouse_position()
        print(f"click at ({p.x:.0f}, {p.y:.0f})")
      streamer.stream_frame()
      pr.end_drawing()
  finally:
    streamer.close()
    injector.stop()
    pr.close_window()
