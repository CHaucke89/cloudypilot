#!/usr/bin/env python3
"""Compatibility wrapper for cloudypilot remote UI stream server.

Canonical implementation lives at:
openpilot/cloudypilot/system/remote_ui/stream_server.py
"""

import runpy


if __name__ == "__main__":
    runpy.run_module("openpilot.cloudypilot.system.remote_ui.stream_server", run_name="__main__")
