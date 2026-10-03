#!/usr/bin/env bash

python3 /data/stream_server.py &

exec ./launch_chffrplus.sh
