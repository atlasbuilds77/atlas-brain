#!/bin/bash
# Test script for brain daemon
# Run this to verify the daemon works correctly

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTROL="$SCRIPT_DIR/brain-daemon-control.sh"
INDEX="/tmp/atlas-memory-index.json"
LOG="/tmp/brain-daemon.log"

echo "🧠 Brain Daemon Test Suite"
echo "=========================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0

# Test function
test() {
    local name="$1"
    shift
    echo -n "Testing: $name ... "
    if "$@" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        PASS=$((PASS + 1))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        FAIL=$((FAIL + 1))
        return 1
    fi
}

# Test 1: Scripts exist
test "Scripts exist" test -f "$SCRIPT_DIR/brain-daemon.js" -a -f "$CONTROL"

# Test 2: Control script is executable
test "Control script executable" test -x "$CONTROL"

# Test 3: Node.js available
test "Node.js available" command -v node

# Test 4: Start daemon
echo -n "Testing: Start daemon ... "
bash "$CONTROL" start > /dev/null 2>&1
sleep 2
if bash "$CONTROL" status | grep -q "RUNNING"; then
    echo -e "${GREEN}✓ PASS${NC}"
    PASS=$((PASS + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    FAIL=$((FAIL + 1))
fi

# Test 5: Index file created
test "Index file created" test -f "$INDEX"

# Test 6: Index is valid JSON
echo -n "Testing: Index is valid JSON ... "
if node -e "JSON.parse(require('fs').readFileSync('$INDEX', 'utf8'))" 2>/dev/null; then
    echo -e "${GREEN}✓ PASS${NC}"
    PASS=$((PASS + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    FAIL=$((FAIL + 1))
fi

# Test 7: Index has required fields
echo -n "Testing: Index structure ... "
node -e "
    const index = JSON.parse(require('fs').readFileSync('$INDEX', 'utf8'));
    if (!index.generated || !index.categories || !index.allFiles || !index.stats) {
        process.exit(1);
    }
" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    PASS=$((PASS + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    FAIL=$((FAIL + 1))
fi

# Test 8: Log file created
test "Log file created" test -f "$LOG"

# Test 9: Daemon survives a few scan cycles
echo -n "Testing: Multiple scan cycles ... "
sleep 3
if bash "$CONTROL" status | grep -q "RUNNING"; then
    echo -e "${GREEN}✓ PASS${NC}"
    PASS=$((PASS + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    FAIL=$((FAIL + 1))
fi

# Test 10: Stop daemon
echo -n "Testing: Stop daemon ... "
bash "$CONTROL" stop > /dev/null 2>&1
sleep 1
if ! bash "$CONTROL" status | grep -q "RUNNING"; then
    echo -e "${GREEN}✓ PASS${NC}"
    PASS=$((PASS + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    FAIL=$((FAIL + 1))
fi

# Test 11: PID file cleaned up
test "PID file cleaned up" test ! -f "/tmp/brain-daemon.pid"

# Summary
echo ""
echo "=========================="
echo "Test Results:"
echo -e "  ${GREEN}Passed: $PASS${NC}"
echo -e "  ${RED}Failed: $FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Start daemon: bash $CONTROL start"
    echo "  2. Check status: bash $CONTROL status"
    echo "  3. Query index: bash $SCRIPT_DIR/brain-query.sh stats"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    echo ""
    echo "Check the log file for details:"
    echo "  tail -50 $LOG"
    exit 1
fi
