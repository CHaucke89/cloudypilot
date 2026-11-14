from openpilot.selfdrive.ui.sunnypilot.layouts.settings.display import DisplayLayout
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import multiple_button_item_sp


class DisplayLayoutCP(DisplayLayout):
  def __init__(self):
    super().__init__()

  def _initialize_items(self):
    items = super()._initialize_items()

    self._screensaver_animation = multiple_button_item_sp(
      title=lambda: tr("Screen Saver Animation"),
      description=lambda: tr("Choose how the screen saver text moves: bouncing around the screen, or dropping from the top."),
      param="ScreenSaverAnimation",
      buttons=[lambda: tr("Bounce"), lambda: tr("Drop"), lambda: tr("Bounce (Rotating)")],
      button_width=364,
      inline=False,
    )

    items.insert(items.index(self._screensaver_timeout) + 1, self._screensaver_animation)
    return items

  def _update_state(self):
    super()._update_state()

    self._screensaver_animation.set_visible(self._screensaver_toggle.action_item.get_state())
