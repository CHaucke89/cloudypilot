import os


def _is_cloudypilot():
  version_file = "openpilot/cloudypilot/common/version.h"
  if os.path.exists(version_file):
    with open(version_file) as f:
      if "CLOUDYPILOT_VERSION" in f.read():
        return True
      else:
        return False


CLOUDY = _is_cloudypilot()
