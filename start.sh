#!/bin/bash
set -e

echo "[*] Setting up X11 access for Podman container..."

# Ensure DISPLAY is set
if [ -z "$DISPLAY" ]; then
    export DISPLAY=:0
    echo "[INFO] DISPLAY set to :0"
fi

# Allow local connections to X11
xhost +local: 2>/dev/null || echo "[WARN] Could not run xhost (X11 might not be running yet)"

# Load config
if [ ! -f "config.env" ]; then
    echo "[ERROR] config.env not found. Run: cp config.env.example config.env"
    exit 1
fi

if [ ! -f "credentials.json" ]; then
    echo "[ERROR] credentials.json not found"
    exit 1
fi

echo "[*] Starting meme-screen..."
export DISPLAY
podman-compose up
