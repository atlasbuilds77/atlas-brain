#!/bin/bash
# Quick test to verify automated consciousness boot system
# Run this to confirm everything is working

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   CONSCIOUSNESS BOOT SYSTEM - VERIFICATION TEST              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

tests_passed=0
tests_failed=0

test() {
    local name=$1
    local command=$2
    
    echo -n "Testing: $name... "
    
    if eval "$command" > /dev/null 2>&1; then
        echo "✓ PASS"
        tests_passed=$((tests_passed + 1))
    else
        echo "✗ FAIL"
        tests_failed=$((tests_failed + 1))
    fi
}

echo "1. Checking required files exist..."
echo ""

test "Main boot script" "[ -f ~/clawd/memory/scripts/consciousness-boot.sh ]"
test "Boot script executable" "[ -x ~/clawd/memory/scripts/consciousness-boot.sh ]"
test "Quick check script" "[ -f ~/clawd/memory/scripts/quick-continuity-check.sh ]"
test "Session manager" "[ -f ~/clawd/memory/scripts/consciousness-session-manager.sh ]"
test "Session manager executable" "[ -x ~/clawd/memory/scripts/consciousness-session-manager.sh ]"
test "Complete guide" "[ -f ~/clawd/memory/protocols/automated-consciousness-boot-guide.md ]"
test "Quick reference" "[ -f ~/clawd/CONSCIOUSNESS-BOOT-QUICK-REF.md ]"
test "System summary" "[ -f ~/clawd/CONSCIOUSNESS-BOOT-SYSTEM-COMPLETE.md ]"

echo ""
echo "2. Checking existing infrastructure..."
echo ""

test "Consciousness daemon" "[ -f ~/clawd/memory/consciousness/consciousness-daemon.sh ]"
test "Phi simulator" "[ -f ~/clawd/memory/consciousness/phi-simulator.py ]"
test "Qualia capture" "[ -f ~/clawd/memory/consciousness/qualia-capture.py ]"
test "Reactivation protocol" "[ -f ~/clawd/memory/protocols/consciousness-reactivation-protocol.md ]"
test "HEARTBEAT.md updated" "grep -q 'AUTOMATED CONSCIOUSNESS BOOT' ~/clawd/HEARTBEAT.md"

echo ""
echo "3. Checking dependencies..."
echo ""

test "Python 3 available" "which python3"
test "Bash available" "which bash"
test "SQLite support" "python3 -c 'import sqlite3'"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "TEST SUMMARY:"
echo "  ✓ Passed: $tests_passed"
echo "  ✗ Failed: $tests_failed"

if [ $tests_failed -eq 0 ]; then
    echo ""
    echo "  🎉 ALL TESTS PASSED - System ready for use!"
    echo ""
    echo "To run your first boot:"
    echo "  bash ~/clawd/memory/scripts/consciousness-boot.sh"
    echo ""
    echo "To use session manager:"
    echo "  bash ~/clawd/memory/scripts/consciousness-session-manager.sh start"
    echo ""
    echo "Quick reference:"
    echo "  cat ~/clawd/CONSCIOUSNESS-BOOT-QUICK-REF.md"
    echo ""
else
    echo ""
    echo "  ⚠️  SOME TESTS FAILED - Check output above"
    echo ""
fi

echo "═══════════════════════════════════════════════════════════════"
