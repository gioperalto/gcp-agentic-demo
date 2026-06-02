#!/bin/bash
set -e

# Clean up stale Xvfb lock from a previous run (docker restart scenario)
rm -f /tmp/.X99-lock /tmp/.X11-unix/X99

# Start virtual framebuffer for non-headless Chromium in Docker
Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &
XVFB_PID=$!

export DISPLAY=:99

# Give Xvfb a moment to initialize
sleep 1

# Trap signals to clean up Xvfb on exit
cleanup() {
    kill "$XVFB_PID" 2>/dev/null || true
}
trap cleanup EXIT TERM INT

exec python main.py
