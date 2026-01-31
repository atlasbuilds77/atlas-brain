#!/bin/bash
# Level Watcher Control Script

DAEMON_PID_FILE="/tmp/level-watcher.pid"
LOG_FILE="/tmp/level-watcher.log"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DAEMON_JS="$SCRIPT_DIR/level-watcher-daemon.js"

start_watcher() {
    if [ -f "$DAEMON_PID_FILE" ]; then
        PID=$(cat "$DAEMON_PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "Level watcher already running (PID: $PID)"
            return 1
        fi
    fi
    
    echo "Starting level watcher daemon..."
    cd "$SCRIPT_DIR"
    nohup node "$DAEMON_JS" >> "$LOG_FILE" 2>&1 &
    echo $! > "$DAEMON_PID_FILE"
    echo "✓ Level watcher started (PID: $(cat "$DAEMON_PID_FILE"))"
    echo "  Checking prices every 5 minutes"
    echo "  Alerts ONLY when levels hit"
}

stop_watcher() {
    if [ ! -f "$DAEMON_PID_FILE" ]; then
        echo "Level watcher not running"
        return 1
    fi
    
    PID=$(cat "$DAEMON_PID_FILE")
    echo "Stopping level watcher (PID: $PID)..."
    kill "$PID" 2>/dev/null
    rm -f "$DAEMON_PID_FILE"
    echo "✓ Level watcher stopped"
}

status_watcher() {
    if [ -f "$DAEMON_PID_FILE" ]; then
        PID=$(cat "$DAEMON_PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "✓ Level watcher running (PID: $PID)"
            echo "Log: $LOG_FILE"
            echo "Watch levels: $SCRIPT_DIR/watch-levels.json"
            
            if [ -f "$SCRIPT_DIR/watch-levels.json" ]; then
                ACTIVE=$(jq '[.[] | select(.triggered == false)] | length' "$SCRIPT_DIR/watch-levels.json" 2>/dev/null || echo "?")
                echo "Active watches: $ACTIVE"
            fi
            
            return 0
        else
            echo "✗ Level watcher not running (stale PID file)"
            rm -f "$DAEMON_PID_FILE"
            return 1
        fi
    else
        echo "✗ Level watcher not running"
        return 1
    fi
}

add_watch() {
    local symbol="$1"
    local level="$2"
    local direction="$3"
    local message="$4"
    local chat_id="${5:-10}"
    
    if [ -z "$symbol" ] || [ -z "$level" ] || [ -z "$direction" ]; then
        echo "Usage: $0 add <symbol> <level> <above|below> [message] [chatId]"
        echo "Example: $0 add SPY 696.50 below '🚨 SPY broke support'"
        return 1
    fi
    
    local watch_file="$SCRIPT_DIR/watch-levels.json"
    
    # Create file if doesn't exist
    if [ ! -f "$watch_file" ]; then
        echo "[]" > "$watch_file"
    fi
    
    # Add new watch
    local new_watch=$(cat <<EOF
{
  "symbol": "$symbol",
  "level": $level,
  "direction": "$direction",
  "alertMessage": "$message",
  "chatId": "$chat_id",
  "triggered": false,
  "addedAt": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
)
    
    local updated=$(jq ". += [$new_watch]" "$watch_file")
    echo "$updated" > "$watch_file"
    
    echo "✓ Added watch: $symbol $direction $level"
    echo "  Alert message: $message"
    echo "  Chat: $chat_id"
}

list_watches() {
    local watch_file="$SCRIPT_DIR/watch-levels.json"
    
    if [ ! -f "$watch_file" ]; then
        echo "No watch levels configured"
        return
    fi
    
    echo "ACTIVE WATCH LEVELS:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    jq -r '.[] | select(.triggered == false) | "  \(.symbol) \(.direction) $\(.level) - \(.alertMessage // "no message")"' "$watch_file"
    
    echo ""
    echo "TRIGGERED:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    jq -r '.[] | select(.triggered == true) | "  \(.symbol) \(.direction) $\(.level) (hit at $\(.triggeredPrice) on \(.triggeredAt))"' "$watch_file"
}

case "$1" in
    start)
        start_watcher
        ;;
    stop)
        stop_watcher
        ;;
    restart)
        stop_watcher
        sleep 1
        start_watcher
        ;;
    status)
        status_watcher
        ;;
    add)
        shift
        add_watch "$@"
        ;;
    list)
        list_watches
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|add|list}"
        echo ""
        echo "Commands:"
        echo "  start                           Start level watcher daemon"
        echo "  stop                            Stop daemon"
        echo "  restart                         Restart daemon"
        echo "  status                          Check daemon status"
        echo "  add <sym> <level> <dir> [msg]   Add watch level"
        echo "  list                            List all watch levels"
        echo ""
        echo "Examples:"
        echo "  $0 add SPY 696.50 below '🚨 SPY broke support'"
        echo "  $0 add QQQ 635 above 'QQQ breakout confirmed'"
        exit 1
        ;;
esac
