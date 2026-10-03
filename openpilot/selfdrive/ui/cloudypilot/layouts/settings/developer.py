
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.developer import DeveloperLayoutSP
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import DialogResult
from openpilot.system.ui.widgets.confirm_dialog import ConfirmDialog

from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp



class DeveloperLayoutCP(DeveloperLayoutSP):
  def __init__(self):
    super().__init__()

  def _initialize_items(self):
    super()._initialize_items()
    self.error_log_btn.set_description(tr("View the error log for cloudypilot crashes."))

    self.konik_toggle = toggle_item_sp(tr("Use Konik API"), tr("Use Konik's API rather than comma's. Requires reboot."), param="KonikApi",
                                       callback=self._on_konik_toggled)
    self.permalatch = toggle_item_sp(tr("PermaLatch"), tr("Permanently latch the driver seatbelt."), param="PermaLatch")
    self.remote_stream = toggle_item_sp(tr("Remote UI"), tr("Enable remote UI streaming on port 8081."), param="EnableRemoteUI")

    self.items.insert(self.items.index(self.error_log_btn), self.konik_toggle)
    self.items.append(self.permalatch)
    self.items.append(self.remote_stream)

  def _perform_soft_reboot(self, result):
    if result == DialogResult.CONFIRM:
      ui_state.params.put_bool("DoSoftReboot", True)

  def _on_konik_toggled(self, result):
    dialog = ConfirmDialog(tr("Soft reboot required for changes to take effect. Soft reboot now?"), tr("Soft Reboot"), callback=self._perform_soft_reboot)
    gui_app.push_widget(dialog)

  def _update_state(self):
    super()._update_state()

    self.konik_toggle.set_visible(ui_state.params.get_bool("ShowAdvancedControls"))
    self.permalatch.set_visible(True)
    self.remote_stream.set_visible(True)
