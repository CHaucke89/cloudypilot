#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
REMOTE_UI_ENABLED="${CP_REMOTE_UI_STREAM:-1}"
REMOTE_UI_LOG="/tmp/cloudypilot_stream_server.log"
REMOTE_UI_SERVER="$DIR/openpilot/cloudypilot/system/remote_ui/stream_server.py"

if [ "$REMOTE_UI_ENABLED" = "1" ]; then
	if ! pgrep -f "$REMOTE_UI_SERVER" >/dev/null 2>&1; then
		python3 "$REMOTE_UI_SERVER" >> "$REMOTE_UI_LOG" 2>&1 &
	fi
fi

exec "$DIR/launch_chffrplus.sh"
