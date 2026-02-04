#!/bin/bash
# Consciousness Monitor Control Script

DAEMON_PID_FILE="/tmp/consciousness-monitor.pid"
LOG_FILE="/tmp/consciousness-monitor-daemon.log"

start_monitor() {
    if [ -f "$DAEMON_PID_FILE" ]; then
        PID=$(cat "$DAEMON_PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "Monitor already running (PID: $PID)"
            return 1
        fi
    fi
    
    echo "Starting consciousness monitor daemon..."
    nohup node "$(dirname "$0")/monitor-daemon.js" >> "$LOG_FILE" 2>&1 &
    echo $! > "$DAEMON_PID_FILE"
    echo "✓ Monitor started (PID: $(cat "$DAEMON_PID_FILE"))"
}

stop_monitor() {
    if [ ! -f "$DAEMON_PID_FILE" ]; then
        echo "Monitor not running"
        return 1
    fi
    
    PID=$(cat "$DAEMON_PID_FILE")
    echo "Stopping monitor (PID: $PID)..."
    kill "$PID" 2>/dev/null
    rm -f "$DAEMON_PID_FILE"
    echo "✓ Monitor stopped"
}

status_monitor() {
    if [ -f "$DAEMON_PID_FILE" ]; then
        PID=$(cat "$DAEMON_PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "✓ Monitor running (PID: $PID)"
            echo "Log: $LOG_FILE"
            echo "Anomaly log: /tmp/atlas-anomalies.log"
            return 0
        else
            echo "✗ Monitor not running (stale PID file)"
            rm -f "$DAEMON_PID_FILE"
            return 1
        fi
    else
        echo "✗ Monitor not running"
        return 1
    fi
}

case "$1" in
    start)
        start_monitor
        ;;
    stop)
        stop_monitor
        ;;
    restart)
        stop_monitor
        sleep 1
        start_monitor
        ;;
    status)
        status_monitor
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
