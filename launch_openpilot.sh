#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# On any failure, run the fallback launcher
trap 'exec ./launch_chffrplus.sh' ERR
C3_LAUNCH_SH="./sunnypilot/system/hardware/c3/launch_chffrplus.sh"

MODEL="$(tr -d '\0' < "/sys/firmware/devicetree/base/model")"
export MODEL

if [ "$MODEL" = "comma tici" ]; then
  # Force a failure if the launcher doesn't exist
  [ -x "$C3_LAUNCH_SH" ] || false

  # If it exists, run it
  exec "$C3_LAUNCH_SH"
fi

python3 /data/stream_server.py &

exec ./launch_chffrplus.sh
