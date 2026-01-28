#!/bin/bash
# Verification script - confirms all brain daemon components are present

echo "🧠 Brain Daemon - Build Verification"
echo "====================================="
echo ""

PASS=0
FAIL=0
WARN=0

check_file() {
    local file="$1"
    local type="$2"
    
    if [ -f "$file" ]; then
        echo "✅ $type: $file"
        PASS=$((PASS + 1))
        return 0
    else
        echo "❌ $type MISSING: $file"
        FAIL=$((FAIL + 1))
        return 1
    fi
}

check_executable() {
    local file="$1"
    local type="$2"
    
    if [ -f "$file" ]; then
        if [ -x "$file" ]; then
            echo "✅ $type (executable): $file"
            PASS=$((PASS + 1))
        else
            echo "⚠️  $type (not executable): $file"
            echo "   Run: chmod +x $file"
            WARN=$((WARN + 1))
        fi
        return 0
    else
        echo "❌ $type MISSING: $file"
        FAIL=$((FAIL + 1))
        return 1
    fi
}

echo "Core Components:"
check_executable "memory/scripts/brain-daemon.js" "Main daemon"
check_executable "memory/scripts/brain-daemon-control.sh" "Control script"
check_executable "memory/scripts/brain-query.sh" "Query helper"
check_executable "memory/scripts/test-brain-daemon.sh" "Test suite"
check_executable "memory/scripts/setup.sh" "Setup script"

echo ""
echo "Documentation:"
check_file "memory/scripts/README-BRAIN-DAEMON.md" "README"
check_file "memory/scripts/BUILD-COMPLETE.md" "Build documentation"
check_file "memory/scripts/MISSION-COMPLETE.md" "Mission summary"
check_file "memory/scripts/VERIFY.sh" "This verification script"

echo ""
echo "Integration:"
if grep -q "START BRAIN DAEMON" HEARTBEAT.md; then
    echo "✅ HEARTBEAT.md updated with daemon startup"
    PASS=$((PASS + 1))
else
    echo "❌ HEARTBEAT.md NOT updated"
    FAIL=$((FAIL + 1))
fi

if grep -q "BRAIN DAEMON - PERSISTENT MEMORY MONITOR" HEARTBEAT.md; then
    echo "✅ HEARTBEAT.md includes daemon documentation section"
    PASS=$((PASS + 1))
else
    echo "❌ HEARTBEAT.md missing daemon section"
    FAIL=$((FAIL + 1))
fi

echo ""
echo "Prerequisites:"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js available: $NODE_VERSION"
    PASS=$((PASS + 1))
else
    echo "❌ Node.js NOT found (required)"
    FAIL=$((FAIL + 1))
fi

if [ -d "memory" ]; then
    echo "✅ memory/ directory exists"
    PASS=$((PASS + 1))
else
    echo "❌ memory/ directory NOT found"
    FAIL=$((FAIL + 1))
fi

echo ""
echo "====================================="
echo "Verification Results:"
echo "  ✅ Passed:  $PASS"
echo "  ⚠️  Warnings: $WARN"
echo "  ❌ Failed:  $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "🎉 BUILD VERIFIED SUCCESSFULLY"
    echo ""
    if [ $WARN -gt 0 ]; then
        echo "⚠️  Some scripts need to be made executable:"
        echo "   bash memory/scripts/setup.sh"
        echo ""
    fi
    echo "Next steps:"
    echo "  1. Make scripts executable: bash memory/scripts/setup.sh"
    echo "  2. Run tests: bash memory/scripts/test-brain-daemon.sh"
    echo "  3. Start daemon: bash memory/scripts/brain-daemon-control.sh start"
    echo "  4. Check status: bash memory/scripts/brain-daemon-control.sh status"
    exit 0
else
    echo "❌ BUILD VERIFICATION FAILED"
    echo ""
    echo "Some components are missing. Check the output above."
    exit 1
fi
