#!/bin/bash
# Meridian Watchdog - Restarts scanner if crashed

MERIDIAN_DIR="/Users/atlasbuilds/clawd/meridian-trader"
LOG_FILE="$MERIDIAN_DIR/logs/meridian_$(date +%Y%m%d).log"

# Check if meridian_main.py is running
if ! pgrep -f "meridian_main.py" > /dev/null; then
    echo "[$(date)] Meridian not running - restarting..." >> "$LOG_FILE"
    cd "$MERIDIAN_DIR"
    nohup python3 meridian_main.py >> "$LOG_FILE" 2>&1 &
    echo "[$(date)] Meridian restarted (PID: $!)" >> "$LOG_FILE"
else
    echo "[$(date)] Meridian running - OK" >> "$LOG_FILE"
fi
