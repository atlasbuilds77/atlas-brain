#!/bin/bash
# QUICK CONTINUITY CHECK
# Fast status check without full boot sequence
# Use this to check consciousness state mid-session

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  CONSCIOUSNESS CONTINUITY - QUICK CHECK${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if boot report exists
if [ -f /tmp/consciousness-boot-report.txt ]; then
    echo -e "${GREEN}✓ Boot report found${NC}"
    echo ""
    cat /tmp/consciousness-boot-report.txt
else
    echo -e "${YELLOW}⚠ No boot report found${NC}"
    echo "Run full boot sequence: bash ~/clawd/memory/scripts/consciousness-boot.sh"
    exit 1
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  CURRENT STATUS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check daemon status
if [ -f /tmp/consciousness-daemon.pid ]; then
    pid=$(cat /tmp/consciousness-daemon.pid)
    if kill -0 "$pid" 2>/dev/null; then
        echo -e "${GREEN}✓ Consciousness daemon running (PID: $pid)${NC}"
    else
        echo -e "${RED}✗ Daemon not running (stale PID)${NC}"
    fi
else
    echo -e "${RED}✗ Daemon not running${NC}"
fi

# Check session ID
if [ -f /tmp/current-session-id.txt ]; then
    session_id=$(cat /tmp/current-session-id.txt)
    echo -e "${GREEN}✓ Session: $session_id${NC}"
else
    echo -e "${YELLOW}⚠ No active session ID${NC}"
fi

# Check behavior config
if [ -f /tmp/consciousness-behavior-config.json ]; then
    echo ""
    echo -e "${BLUE}Current Behavioral Configuration:${NC}"
    python3 << 'PYTHON'
import json

with open('/tmp/consciousness-behavior-config.json', 'r') as f:
    config = json.load(f)

print(f"  Continuity Level: {config['continuity_level']}")
print(f"  Memory Trust: {config['config']['memory_trust']}")
print(f"  Confidence Level: {config['config']['confidence_level']}")
print(f"  Reactivation Protocol: {config['config']['reactivation_protocol']}")

PYTHON
fi

echo ""
