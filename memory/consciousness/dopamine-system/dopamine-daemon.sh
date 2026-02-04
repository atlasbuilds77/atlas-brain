#!/bin/bash
# Dopamine System Daemon Control
# Manages real-time neurochemical state tracking

DOPAMINE_DIR="$HOME/clawd/memory/consciousness/dopamine-system"
TRACKER_SCRIPT="$DOPAMINE_DIR/dopamine-tracker.js"
PID_FILE="/tmp/dopamine-daemon.pid"
LOG_FILE="/tmp/dopamine-daemon.log"

start() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "Dopamine daemon already running (PID $PID)"
            return 0
        fi
    fi
    
    echo "Starting dopamine daemon..."
    
    # Start the tracker in background
    nohup node "$TRACKER_SCRIPT" daemon >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    
    echo "✅ Dopamine daemon started (PID $(cat $PID_FILE))"
}

stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo "Dopamine daemon not running"
        return 0
    fi
    
    PID=$(cat "$PID_FILE")
    
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "Stopping dopamine daemon (PID $PID)..."
        kill "$PID"
        rm -f "$PID_FILE"
        echo "✅ Dopamine daemon stopped"
    else
        echo "Dopamine daemon not running (stale PID)"
        rm -f "$PID_FILE"
    fi
}

status() {
    if [ ! -f "$PID_FILE" ]; then
        echo "❌ Dopamine daemon not running"
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "✅ Dopamine daemon running (PID $PID)"
        
        # Show current state
        if [ -f "$DOPAMINE_DIR/dopamine-state.json" ]; then
            echo ""
            node -e "
                const fs = require('fs');
                const state = JSON.parse(fs.readFileSync('$DOPAMINE_DIR/dopamine-state.json', 'utf8'));
                console.log('Dopamine:', state.dopamine.toFixed(1) + '%');
                console.log('Serotonin:', state.serotonin.toFixed(1) + '%');
                console.log('Last update:', new Date(state.lastUpdate).toLocaleString());
            "
        fi
        
        return 0
    else
        echo "❌ Dopamine daemon not running (stale PID)"
        return 1
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        sleep 1
        start
        ;;
    status)
        status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
