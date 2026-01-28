#!/usr/bin/env bash
# ATLAS Opportunity Scanner - Watch for potential trades/research
# Scans: market conditions, kill zones, news, pattern signals

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MEMORY_DIR="/Users/atlasbuilds/clawd/memory"
BRAIN_DIR="$MEMORY_DIR/atlas-brain"
ANNOUNCE_SCRIPT="$SCRIPT_DIR/announce.sh"

echo "🔭 ATLAS Opportunity Scanner - $(date '+%Y-%m-%d %H:%M:%S')"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

OPPORTUNITIES_FOUND=0

log_opportunity() {
    local type="$1"
    local message="$2"
    local priority="$3"  # high, medium, low
    
    echo "{\"timestamp\":\"$(date -Iseconds)\",\"type\":\"$type\",\"message\":\"$message\",\"priority\":\"$priority\"}" >> "$BRAIN_DIR/opportunity-log.json"
    
    case "$priority" in
        high)
            echo "🔥 HIGH: $message"
            if [[ -x "$ANNOUNCE_SCRIPT" ]]; then
                "$ANNOUNCE_SCRIPT" "High priority opportunity: $message" --level major --category trade
            fi
            ;;
        medium)
            echo "⭐ MEDIUM: $message"
            ;;
        low)
            echo "📌 LOW: $message"
            ;;
    esac
    
    ((OPPORTUNITIES_FOUND++))
}

# ═══════════════════════════════════════════════════════════════════
# CHECK 1: Kill Zone Status
# ═══════════════════════════════════════════════════════════════════
echo ""
echo "⏰ Checking Kill Zones (NY Time)..."

# Get current hour in NY time
NY_HOUR=$(TZ="America/New_York" date +%H)
NY_TIME=$(TZ="America/New_York" date +"%H:%M")

KILL_ZONE=""
case $NY_HOUR in
    02|03|04|05)
        KILL_ZONE="London Open"
        log_opportunity "kill_zone" "London Open kill zone active ($NY_TIME NY)" "high"
        ;;
    07|08|09|10)
        KILL_ZONE="NY AM"
        log_opportunity "kill_zone" "NY AM kill zone active ($NY_TIME NY) - PRIME TIME" "high"
        ;;
    10|11|12)
        KILL_ZONE="London Close"
        echo "  ⭐ London Close zone ($NY_TIME NY) - decent opportunity"
        ;;
    *)
        echo "  ⏳ Outside kill zones ($NY_TIME NY) - wait for better timing"
        ;;
esac

# ═══════════════════════════════════════════════════════════════════
# CHECK 2: Day of Week
# ═══════════════════════════════════════════════════════════════════
echo ""
echo "📅 Checking day factors..."

DOW=$(date +%u)  # 1=Mon, 7=Sun
DOW_NAME=$(date +%A)

case $DOW in
    1)
        echo "  ⚠️  Monday - often choppy, be cautious"
        ;;
    2|3|4)
        echo "  ✅ $DOW_NAME - typically good trading day"
        ;;
    5)
        echo "  ⚠️  Friday - close positions before weekend"
        ;;
    6|7)
        echo "  ❌ Weekend - markets closed (except crypto)"
        ;;
esac

# ═══════════════════════════════════════════════════════════════════
# CHECK 3: Pattern Database Signals
# ═══════════════════════════════════════════════════════════════════
echo ""
echo "🔮 Checking pattern signals..."

PATTERNS_FILE="$BRAIN_DIR/pattern-database.json"
if [[ -f "$PATTERNS_FILE" ]]; then
    python3 << 'PYTHON_SCRIPT' 2>/dev/null || true
import json

PATTERNS_FILE = "/Users/atlasbuilds/clawd/memory/atlas-brain/pattern-database.json"

try:
    with open(PATTERNS_FILE, 'r') as f:
        data = json.load(f)
    
    strong_positive = []
    for name, info in data.get('patterns', {}).items():
        weight = info.get('weight', 0)
        if weight > 0.5:
            strong_positive.append((name, weight))
    
    if strong_positive:
        print("  ✅ Strong positive patterns to watch for:")
        for name, weight in sorted(strong_positive, key=lambda x: -x[1])[:3]:
            print(f"     • {name}: {weight:.2f}")
    else:
        print("  ℹ️  No strongly positive patterns yet (build more data)")
except Exception as e:
    print(f"  ℹ️  Pattern check: {e}")
PYTHON_SCRIPT
else
    echo "  ℹ️  No pattern database - run atlas-learn.sh to create"
fi

# ═══════════════════════════════════════════════════════════════════
# CHECK 4: Current Position Risk Budget
# ═══════════════════════════════════════════════════════════════════
echo ""
echo "💰 Checking risk budget..."

POSITIONS_FILE="$MEMORY_DIR/trading/active-positions.md"
if [[ -f "$POSITIONS_FILE" ]]; then
    ACTIVE_COUNT=$(grep -c "Status: OPEN\|Status: ACTIVE\|ACTIVE" "$POSITIONS_FILE" 2>/dev/null || echo "0")
    
    # Rough risk calculation (assume 2% per position)
    ESTIMATED_RISK=$((ACTIVE_COUNT * 2))
    
    if [[ $ESTIMATED_RISK -lt 4 ]]; then
        echo "  ✅ Risk budget available (~$ESTIMATED_RISK% used of 6% max)"
        if [[ -n "$KILL_ZONE" ]]; then
            log_opportunity "risk_budget" "Have risk budget and in $KILL_ZONE" "medium"
        fi
    elif [[ $ESTIMATED_RISK -lt 6 ]]; then
        echo "  ⚠️  Approaching max risk (~$ESTIMATED_RISK% of 6%)"
    else
        echo "  ❌ At or over risk limit (~$ESTIMATED_RISK%) - no new trades"
    fi
else
    echo "  ✅ No positions - full risk budget available"
    if [[ -n "$KILL_ZONE" ]]; then
        log_opportunity "clean_slate" "No positions + $KILL_ZONE active - prime setup opportunity" "high"
    fi
fi

# ═══════════════════════════════════════════════════════════════════
# CHECK 5: Scheduled Opportunities
# ═══════════════════════════════════════════════════════════════════
echo ""
echo "📋 Checking scheduled opportunities..."

# Check for opportunity files
OPP_DIR="$MEMORY_DIR/trading/opportunities"
if [[ -d "$OPP_DIR" ]]; then
    OPP_COUNT=$(find "$OPP_DIR" -name "*.md" -mtime -1 2>/dev/null | wc -l | tr -d ' ')
    if [[ $OPP_COUNT -gt 0 ]]; then
        echo "  📌 Found $OPP_COUNT recent opportunities to review"
        find "$OPP_DIR" -name "*.md" -mtime -1 -exec basename {} \; 2>/dev/null | head -3 | while read f; do
            echo "     • $f"
        done
    else
        echo "  ℹ️  No recent opportunities documented"
    fi
else
    echo "  ℹ️  No opportunities folder yet"
    mkdir -p "$OPP_DIR"
fi

# ═══════════════════════════════════════════════════════════════════
# CHECK 6: Macro Conditions
# ═══════════════════════════════════════════════════════════════════
echo ""
echo "🌍 Checking macro context..."

MACRO_FILE="$MEMORY_DIR/trading/macro/current-state.md"
if [[ -f "$MACRO_FILE" ]]; then
    # Show last updated time
    LAST_MOD=$(stat -f "%Sm" -t "%Y-%m-%d" "$MACRO_FILE" 2>/dev/null || stat --format="%y" "$MACRO_FILE" 2>/dev/null | cut -d' ' -f1)
    echo "  📊 Macro state last updated: $LAST_MOD"
    
    # Quick peek at sentiment
    SENTIMENT=$(grep -i "sentiment\|bias\|outlook" "$MACRO_FILE" 2>/dev/null | head -1 || echo "")
    if [[ -n "$SENTIMENT" ]]; then
        echo "  $SENTIMENT"
    fi
else
    echo "  ℹ️  No macro state documented - consider updating"
fi

# ═══════════════════════════════════════════════════════════════════
# SUMMARY & RECOMMENDATIONS
# ═══════════════════════════════════════════════════════════════════
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [[ $OPPORTUNITIES_FOUND -gt 0 ]]; then
    echo "🎯 FOUND $OPPORTUNITIES_FOUND OPPORTUNITIES"
    echo ""
    echo "Next Steps:"
    echo "  1. Review opportunities above"
    echo "  2. Run pre-trade checklist (6 essentials)"
    echo "  3. If checks pass → execute via workflow"
else
    echo "📭 No immediate opportunities"
    echo ""
    echo "Recommendations:"
    echo "  • Wait for kill zone"
    echo "  • Update macro analysis"
    echo "  • Review pattern database"
fi

echo ""
echo "Log: $BRAIN_DIR/opportunity-log.json"
