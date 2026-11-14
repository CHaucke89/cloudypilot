from openpilot.cloudypilot.selfdrive.ui.frame_streamer import FrameStreamer
from openpilot.cloudypilot.selfdrive.ui.touch_injector import TouchInjector


class RemoteUI:
  def __init__(self):
    # Imported here so the standalone smoke test below doesn't need the full UI.
    from openpilot.selfdrive.ui.ui_state import ui_state
    from openpilot.system.ui.lib.application import gui_app
    self._gui_app = gui_app

    # Remote taps are ignored while engaged; local touch keeps working.
    self.injector = TouchInjector(input_blocked=lambda: ui_state.engaged)
    self.injector.start()
    # Runs every rendered frame, before widgets read input, whether or not a browser is connected.
    gui_app.add_nav_stack_tick(self.injector.end_frame)
    self.streamer = FrameStreamer()
    print("RemoteUI: streaming + input injection started")

  def stream_frame(self):
    self.streamer.stream_frame()

  def close(self):
    self._gui_app.remove_nav_stack_tick(self.injector.end_frame)
    self.streamer.close()
    self.injector.stop()
    print("RemoteUI: stopped")


if __name__ == "__main__":
  # Smoke test without the full UI; run stream_server.py separately and open the page.
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
      injector.end_frame()
      streamer.stream_frame()
      pr.end_drawing()
  finally:
    streamer.close()
    injector.stop()
    pr.close_window()
