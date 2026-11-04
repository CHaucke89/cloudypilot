from unittest import mock

import openpilot.system.manager.manager as manager
from openpilot.common.hardware.comma.hardware import HardwareComma
from openpilot.common.hardware.pc.hardware import HardwarePc
from openpilot.common.params import Params
from openpilot.common.test import OpenpilotTestCase


class TestSoftReboot(OpenpilotTestCase):
  def test_comma_restarts_service(self):
    with mock.patch("subprocess.check_output") as run:
      HardwareComma.soft_reboot(mock.MagicMock())
    run.assert_called_once_with(["sudo", "systemctl", "restart", "comma"])

  def test_comma_soft_reboot_is_not_hardware_reboot(self):
    with mock.patch("subprocess.check_output") as run:
      HardwareComma.soft_reboot(mock.MagicMock())
    assert run.call_args.args[0] != ["sudo", "reboot"]

  def test_pc_has_soft_reboot(self):
    # manager.main() calls HARDWARE.soft_reboot() on any platform
    assert callable(getattr(HardwarePc(), "soft_reboot", None))

  def test_param_is_cleared_on_manager_start(self):
    params = Params()
    params.put_bool("DoSoftReboot", True, block=True)
    params.clear_all(manager.ParamKeyFlag.CLEAR_ON_MANAGER_START)
    assert not params.get_bool("DoSoftReboot")

  def test_main_dispatch(self):
    for param, expected in (("DoSoftReboot", "soft_reboot"), ("DoReboot", "reboot"), ("DoShutdown", "shutdown"), ("DoUninstall", "uninstall")):
      self._check_dispatch(param, expected)

  def _check_dispatch(self, param, expected):
    params = Params()
    params.put_bool(param, True, block=True)

    with mock.patch.object(manager, "manager_init"), mock.patch.object(manager, "manager_thread"), \
         mock.patch.object(manager, "manager_cleanup"), mock.patch.object(manager, "HARDWARE") as hw:
      manager.main()

    for name in ("soft_reboot", "reboot", "shutdown", "uninstall"):
      assert getattr(hw, name).called == (name == expected), name
    params.put_bool(param, False, block=True)

  def test_main_no_flag_does_nothing(self):
    with mock.patch.object(manager, "manager_init"), mock.patch.object(manager, "manager_thread"), \
         mock.patch.object(manager, "manager_cleanup"), mock.patch.object(manager, "HARDWARE") as hw:
      manager.main()
    assert not hw.soft_reboot.called
