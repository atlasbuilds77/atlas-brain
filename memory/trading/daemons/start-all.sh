#!/bin/bash
# Start all trading automation daemons

DAEMON_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="/tmp/trading-daemons"

# Create log directory
mkdir -p "$LOG_DIR"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "==================================="
echo "Starting Trading Automation Daemons"
echo "==================================="
echo ""

# Function to start a daemon
start_daemon() {
    local name=$1
    local script=$2
    local log_file="$LOG_DIR/${name}.log"
    
    # Check if already running
    if pgrep -f "$script" > /dev/null; then
        echo -e "${YELLOW}⚠${NC}  $name already running"
        return 0
    fi
    
    # Start daemon
    echo -n "Starting $name... "
    nohup python3 "$DAEMON_DIR/$script" >> "$log_file" 2>&1 &
    local pid=$!
    
    # Wait a moment and check if it's still running
    sleep 2
    if kill -0 $pid 2>/dev/null; then
        echo -e "${GREEN}✓${NC} (PID: $pid)"
        return 0
    else
        echo -e "${RED}✗${NC} Failed to start"
        return 1
    fi
}

# Start each daemon
start_daemon "Setup Scanner" "setup-scanner.py"
start_daemon "Level Watcher" "level-watcher.py"
start_daemon "Order Block Updater" "order-block-updater.py"

echo ""
echo "==================================="
echo "Startup complete"
echo "==================================="
echo ""
echo "Logs: $LOG_DIR"
echo "Run './status.sh' to check daemon status"
echo ""
