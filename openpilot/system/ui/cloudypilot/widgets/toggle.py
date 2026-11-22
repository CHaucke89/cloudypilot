from openpilot.system.ui.sunnypilot.widgets.toggle import ToggleSP


class ToggleCP(ToggleSP):
  def refresh(self):
    if self.param_key:
      self.set_state(self.params.get_bool(self.param_key))
      self._progress = self._target
