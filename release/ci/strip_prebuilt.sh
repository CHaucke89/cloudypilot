#!/usr/bin/env bash
# Removes build intermediates and sources from the prebuilt tree in $1.
set -euo pipefail

cd "$1"
find . -name '*.a' -delete
find . -name '*.o' -delete
find . -name '*.os' -delete
find . -name '*.pyc' -delete
find . -name 'moc_*' -delete
find . -name '__pycache__' -type d -exec rm -rf {} +
find . -name 'SConstruct' -delete
find . -name 'SConscript' -delete
rm -rf .sconsign.dblite Jenkinsfile tools/release/ release/
rm -f openpilot/selfdrive/modeld/models/*.onnx*
rm -f openpilot/sunnypilot/modeld*/models/*.onnx*
find openpilot/third_party/ -name '*x86*' -exec rm -r {} +
find openpilot/third_party/ -name '*Darwin*' -exec rm -r {} +
