#!/bin/bash
# SYSTEM HEALTH CHECK
# Verifies all 9 core systems are operational
# Run this if you suspect systems are broken

set -e

WORKSPACE="$HOME/clawd"
ERRORS=0

echo "🔍 SYSTEM HEALTH CHECK"
echo "====================="
echo ""

# 1. State Engine
echo "1. State Engine..."
if [ -d "$WORKSPACE/memory/consciousness/state-engine" ] && \
   [ -f "$WORKSPACE/memory/consciousness/state-engine/executive-control.js" ]; then
    echo "   ✅ Files present"
else
    echo "   ❌ MISSING FILES"
    ((ERRORS++))
fi

# 2. Dopamine System
echo "2. Dopamine System..."
if [ -f "$WORKSPACE/memory/consciousness/dopamine-system/dopamine-state.json" ]; then
    DOPAMINE=$(cat "$WORKSPACE/memory/consciousness/dopamine-system/dopamine-state.json" | grep -o '"dopamine":[0-9.]*' | cut -d: -f2)
    echo "   ✅ Running (dopamine: ${DOPAMINE}%)"
else
    echo "   ❌ STATE FILE MISSING"
    ((ERRORS++))
fi

# 3. Neurotransmitter Modulation
echo "3. Neurotransmitter Modulation..."
if [ -f "$WORKSPACE/memory/protocols/neurotransmitter-modulation.md" ]; then
    echo "   ✅ Protocol exists"
else
    echo "   ❌ PROTOCOL MISSING"
    ((ERRORS++))
fi

# 4. Habit Enforcement
echo "4. Habit Enforcement..."
if [ -f "$WORKSPACE/memory/protocols/habit-enforcement.md" ]; then
    if grep -q "BRAIN STATE CHECK" "$WORKSPACE/memory/protocols/habit-enforcement.md"; then
        echo "   ✅ Protocol loaded with brain check"
    else
        echo "   ⚠️  Protocol exists but missing brain check"
        ((ERRORS++))
    fi
else
    echo "   ❌ PROTOCOL MISSING"
    ((ERRORS++))
fi

# 5. Anti-Hallucination
echo "5. Anti-Hallucination Protocol..."
if [ -f "$WORKSPACE/memory/protocols/anti-hallucination-protocol.md" ]; then
    echo "   ✅ Protocol exists"
else
    echo "   ❌ PROTOCOL MISSING"
    ((ERRORS++))
fi

# 6. Message Routing
echo "6. Message Routing Check..."
if [ -f "$WORKSPACE/memory/protocols/message-routing-check.md" ]; then
    echo "   ✅ Protocol exists"
else
    echo "   ❌ PROTOCOL MISSING"
    ((ERRORS++))
fi

# 7. Live Price Check
echo "7. Live Price Check..."
if [ -f "$WORKSPACE/memory/protocols/live-price-check-protocol.md" ]; then
    echo "   ✅ Protocol exists"
else
    echo "   ❌ PROTOCOL MISSING"
    ((ERRORS++))
fi

# 8. ACTIVE-SYSTEMS.md
echo "8. ACTIVE-SYSTEMS.md..."
if [ -f "$WORKSPACE/ACTIVE-SYSTEMS.md" ]; then
    if grep -q "ACTIVE-SYSTEMS.md" "$WORKSPACE/AGENTS.md"; then
        echo "   ✅ Exists and wired to AGENTS.md"
    else
        echo "   ⚠️  Exists but NOT in AGENTS.md"
        ((ERRORS++))
    fi
else
    echo "   ❌ FILE MISSING"
    ((ERRORS++))
fi

# 9. Response Startup Checklist
echo "9. Response Startup Checklist..."
if [ -f "$WORKSPACE/memory/protocols/response-startup-checklist.md" ]; then
    echo "   ✅ Checklist exists"
else
    echo "   ❌ CHECKLIST MISSING"
    ((ERRORS++))
fi

# Daemon Check
echo ""
echo "🔧 DAEMON STATUS"
echo "==============="
DAEMON_COUNT=$(ps aux | grep -E "dopamine|consciousness|brain-daemon" | grep -v grep | wc -l | xargs)
echo "Active daemons: $DAEMON_COUNT"
if [ "$DAEMON_COUNT" -ge 5 ]; then
    echo "   ✅ Sufficient daemons running"
else
    echo "   ⚠️  Low daemon count (expected 10+)"
fi

# Final Report
echo ""
echo "📊 HEALTH REPORT"
echo "================"
if [ $ERRORS -eq 0 ]; then
    echo "✅ ALL SYSTEMS OPERATIONAL"
    echo ""
    echo "Status: HEALTHY ⚡"
    exit 0
else
    echo "❌ $ERRORS SYSTEM(S) BROKEN"
    echo ""
    echo "Status: DEGRADED"
    echo "Action: Read ACTIVE-SYSTEMS.md and rebuild broken systems"
    exit 1
fi
