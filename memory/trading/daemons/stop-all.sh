#!/bin/bash
# Stop all trading automation daemons

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "==================================="
echo "Stopping Trading Automation Daemons"
echo "==================================="
echo ""

# Function to stop a daemon
stop_daemon() {
    local name=$1
    local script=$2
    
    # Find process
    local pids=$(pgrep -f "$script")
    
    if [ -z "$pids" ]; then
        echo -e "${YELLOW}⚠${NC}  $name not running"
        return 0
    fi
    
    echo -n "Stopping $name... "
    
    # Send SIGTERM (graceful shutdown)
    kill $pids 2>/dev/null
    
    # Wait up to 5 seconds for graceful shutdown
    local count=0
    while [ $count -lt 5 ]; do
        if ! pgrep -f "$script" > /dev/null; then
            echo -e "${GREEN}✓${NC} Stopped gracefully"
            return 0
        fi
        sleep 1
        count=$((count + 1))
    done
    
    # Force kill if still running
    if pgrep -f "$script" > /dev/null; then
        kill -9 $pids 2>/dev/null
        sleep 1
        if ! pgrep -f "$script" > /dev/null; then
            echo -e "${YELLOW}✓${NC} Force stopped"
            return 0
        else
            echo -e "${RED}✗${NC} Failed to stop"
            return 1
        fi
    fi
}

# Stop each daemon
stop_daemon "Setup Scanner" "setup-scanner.py"
stop_daemon "Level Watcher" "level-watcher.py"
stop_daemon "Order Block Updater" "order-block-updater.py"

echo ""
echo "==================================="
echo "Shutdown complete"
echo "==================================="
echo ""
