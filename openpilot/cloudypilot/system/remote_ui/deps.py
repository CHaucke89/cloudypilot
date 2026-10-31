"""
Ensures the remote UI stream server's third-party dependencies are importable.

AGNOS updates replace the system venv, wiping anything pip-installed into it. Missing packages are
installed into a directory on /data instead, which survives OS updates, and that directory is put on sys.path.
"""

import importlib
import shutil
import subprocess
import sys

DEPS_DIR = "/data/cloudypilot/pydeps"

# import name -> pip requirement
REQUIREMENTS = {
  "flask": "flask",
  "flask_sock": "flask-sock",
}


def _missing() -> list[str]:
  missing = []
  for module, requirement in REQUIREMENTS.items():
    try:
      importlib.import_module(module)
    except ImportError:
      missing.append(requirement)
  return missing


def _install(requirements: list[str]) -> None:
  cmds = [[sys.executable, "-m", "pip", "install", "--no-cache-dir", "--target", DEPS_DIR, *requirements]]
  if uv := shutil.which("uv"):
    cmds.append([uv, "pip", "install", "--python", sys.executable, "--no-cache", "--target", DEPS_DIR, *requirements])

  for cmd in cmds:
    try:
      subprocess.run(cmd, check=True, timeout=300)
      return
    except (OSError, subprocess.SubprocessError) as e:
      print(f"remote_ui: dependency install failed with {cmd[0]}: {e}")
  raise RuntimeError(f"remote_ui: unable to install {requirements}")


def ensure_deps() -> None:
  if DEPS_DIR not in sys.path:
    sys.path.append(DEPS_DIR)

  missing = _missing()
  if not missing:
    return

  print(f"remote_ui: installing missing dependencies {missing} into {DEPS_DIR}")
  _install(missing)
  importlib.invalidate_caches()

  if still_missing := _missing():
    raise RuntimeError(f"remote_ui: dependencies still missing after install: {still_missing}")
