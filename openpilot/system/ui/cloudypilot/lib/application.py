import os

CLOUDYPILOT_UI = os.getenv("CLOUDYPILOT_UI", "1") == "1"


class GuiApplicationExt:
  def __init__(self):
    pass

  @staticmethod
  def cloudypilot_ui() -> bool:
    return CLOUDYPILOT_UI
