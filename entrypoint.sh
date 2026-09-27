#!/bin/sh

# Disable screen blanking/sleep (ignore errors — xset may not support all flags)
xset s off || true
xset -dpms || true
xset s noblank || true

exec python /app/meme_screen.py
