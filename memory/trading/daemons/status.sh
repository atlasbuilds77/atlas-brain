#!/bin/bash
# Check status of all trading automation daemons

DAEMON_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="/tmp/trading-daemons"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "==================================="
echo "Trading Automation Daemon Status"
echo "==================================="
echo ""

# Function to check daemon status
check_daemon() {
    local name=$1
    local script=$2
    local log_file="$LOG_DIR/${3:-$(echo $name | tr '[:upper:]' '[:lower:]' | tr ' ' '-')}.log"
    
    # Find process
    local pids=$(pgrep -f "$script")
    
    if [ -z "$pids" ]; then
        echo -e "${RED}●${NC} $name: ${RED}STOPPED${NC}"
        return 1
    else
        # Get process uptime
        local uptime=$(ps -p $pids -o etime= | tr -d ' ')
        echo -e "${GREEN}●${NC} $name: ${GREEN}RUNNING${NC} (PID: $pids, uptime: $uptime)"
        
        # Show last log line if log file exists
        if [ -f "$log_file" ]; then
            local last_log=$(tail -n 1 "$log_file" 2>/dev/null)
            if [ ! -z "$last_log" ]; then
                echo -e "   ${BLUE}└→${NC} Last: $(echo "$last_log" | cut -c 1-80)"
            fi
        fi
        
        return 0
    fi
}

# Check each daemon
check_daemon "Setup Scanner" "setup-scanner.py" "setup-scanner"
echo ""
check_daemon "Level Watcher" "level-watcher.py" "level-watcher"
echo ""
check_daemon "Order Block Updater" "order-block-updater.py" "order-block-updater"

echo ""
echo "==================================="

# Show market hours status
current_hour=$(date +%H)
current_minute=$(date +%M)
day_of_week=$(date +%u)

echo ""
echo "Market Status:"

if [ "$day_of_week" -gt 5 ]; then
    echo -e "  ${YELLOW}●${NC} Weekend (daemons idle)"
elif [ "$current_hour" -lt 6 ] || [ "$current_hour" -gt 13 ] || ([ "$current_hour" -eq 6 ] && [ "$current_minute" -lt 30 ]); then
    echo -e "  ${YELLOW}●${NC} Outside market hours (daemons idle)"
else
    echo -e "  ${GREEN}●${NC} Market hours (daemons active)"
fi

echo ""
echo "Logs: $LOG_DIR"
echo ""
