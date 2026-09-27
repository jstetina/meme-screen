#!/bin/sh
xset s off || true
xset -dpms || true
xset s noblank || true
PICTURES_DIR="${PICTURES_DIRECTORY:-/tmp/meme-screen/pictures}"
INTERVAL="${SLIDESHOW_INTERVAL_SECONDS:-10}"
RELOAD_FLAG="$PICTURES_DIR/.reload"
while [ -z "$(ls "$PICTURES_DIR" 2>/dev/null)" ]; do sleep 5; done
while true; do
    rm -f "$RELOAD_FLAG"
    feh --fullscreen --auto-zoom --hide-pointer --quiet \
        --slideshow-delay "$INTERVAL" \
        "$PICTURES_DIR" &
    FEH_PID=$!
    while kill -0 "$FEH_PID" 2>/dev/null; do
        [ -f "$RELOAD_FLAG" ] && kill "$FEH_PID" 2>/dev/null && break
        sleep 2
    done
    wait "$FEH_PID" 2>/dev/null
done
