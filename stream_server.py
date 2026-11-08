#!/usr/bin/env python3
"""Shim for launchers that still run stream_server.py from the repo root."""

import runpy


if __name__ == "__main__":
    runpy.run_module("openpilot.cloudypilot.system.remote_ui.stream_server", run_name="__main__")
