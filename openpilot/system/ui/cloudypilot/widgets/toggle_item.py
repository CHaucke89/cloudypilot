from collections.abc import Callable

from openpilot.system.ui.cloudypilot.widgets.toggle import ToggleCP
from openpilot.system.ui.sunnypilot.widgets.list_view import ListItemSP, ToggleActionSP


class ToggleActionCP(ToggleActionSP):
  def __init__(self, initial_state: bool = False, enabled: bool | Callable[[], bool] = True,
               callback: Callable[[bool], None] | None = None, param: str | None = None):
    super().__init__(initial_state=initial_state, enabled=enabled, callback=callback, param=param)
    self.toggle = ToggleCP(initial_state=initial_state, callback=callback, param=param)

  def show_event(self):
    super().show_event()
    # the param can change elsewhere (e.g. home quick toggles) while this panel is hidden
    self.toggle.refresh()


class ListItemCP(ListItemSP):
  def show_event(self):
    super().show_event()
    # stock ListItem doesn't register its action as a child, so it never sees show_event
    if self.action_item:
      self.action_item.show_event()


def toggle_item_cp(title: str | Callable[[], str], description: str | Callable[[], str] | None = None, initial_state: bool = False,
                   callback: Callable | None = None, icon: str = "", enabled: bool | Callable[[], bool] = True,
                   param: str | None = None) -> ListItemSP:
  action = ToggleActionCP(initial_state=initial_state, enabled=enabled, callback=callback, param=param)
  return ListItemCP(title=title, description=description, action_item=action, icon=icon)
