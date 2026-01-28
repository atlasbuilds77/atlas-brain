#!/usr/bin/env bash
# ATLAS Anomaly Detection - Watch for unusual patterns
# Checks: sudden losses, repeated errors, mode confusion, risk breaches

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MEMORY_DIR="/Users/atlasbuilds/clawd/memory"
BRAIN_DIR="$MEMORY_DIR/atlas-brain"
ANOMALY_LOG="$BRAIN_DIR/anomaly-log.json"
ANNOUNCE_SCRIPT="$SCRIPT_DIR/announce.sh"

# Ensure directories exist
mkdir -p "$BRAIN_DIR"

# Thresholds
MAX_DAILY_TRADES=5
MAX_LOSSES_STREAK=3
MAX_RISK_PERCENT=10
ERROR_THRESHOLD=5  # errors in last hour

echo "🔍 ATLAS Anomaly Watch - $(date '+%Y-%m-%d %H:%M:%S')"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

ANOMALIES_FOUND=0

log_anomaly() {
    local type="$1"
    local message="$2"
    local severity="$3"  # warning, alert, critical
    
    echo "{\"timestamp\":\"$(date -Iseconds)\",\"type\":\"$type\",\"message\":\"$message\",\"severity\":\"$severity\"}" >> "$ANOMALY_LOG"
    
    case "$severity" in
        critical)
            echo "🚨 CRITICAL: $message"
            if [[ -x "$ANNOUNCE_SCRIPT" ]]; then
                "$ANNOUNCE_SCRIPT" "Critical anomaly detected: $message" --level critical --category alert
            fi
            ;;
        alert)
            echo "⚠️  ALERT: $message"
            if [[ -x "$ANNOUNCE_SCRIPT" ]]; then
                "$ANNOUNCE_SCRIPT" "Alert: $message" --level major --category alert
            fi
            ;;
        warning)
            echo "⚡ WARNING: $message"
            ;;
    esac
    
    ((ANOMALIES_FOUND++))
}

# ═══════════════════════════════════════════════════════════════════
# CHECK 1: Rapid Trading (Overtrading Detection)
# ═══════════════════════════════════════════════════════════════════
echo ""
echo "📊 Checking trading frequency..."

TODAY=$(date +%Y-%m-%d)
JOURNAL_FILE="$MEMORY_DIR/trading/journal-$(date +%Y-%m).md"
if [[ -f "$JOURNAL_FILE" ]]; then
    TODAY_TRADES=$(grep -c "$TODAY" "$JOURNAL_FILE" 2>/dev/null || echo "0")
    if [[ $TODAY_TRADES -gt $MAX_DAILY_TRADES ]]; then
        log_anomaly "overtrading" "Placed $TODAY_TRADES trades today (max: $MAX_DAILY_TRADES)" "alert"
    else
        echo "  ✅ Trades today: $TODAY_TRADES (limit: $MAX_DAILY_TRADES)"
    fi
else
    echo "  ℹ️  No journal file for today"
fi

# ═══════════════════════════════════════════════════════════════════
# CHECK 2: Loss Streak Detection
# ═══════════════════════════════════════════════════════════════════
echo ""
echo "📉 Checking for loss streaks..."

# Look for consecutive losses in recent entries
POSITIONS_FILE="$MEMORY_DIR/trading/active-positions.md"
if [[ -f "$POSITIONS_FILE" ]]; then
    RECENT_LOSSES=$(grep -c "LOSS\|❌" "$POSITIONS_FILE" 2>/dev/null || echo "0")
    if [[ $RECENT_LOSSES -gt $MAX_LOSSES_STREAK ]]; then
        log_anomaly "loss_streak" "Found $RECENT_LOSSES recent losses (threshold: $MAX_LOSSES_STREAK)" "alert"
    else
        echo "  ✅ Recent losses: $RECENT_LOSSES (threshold: $MAX_LOSSES_STREAK)"
    fi
else
    echo "  ℹ️  No positions file found"
fi

# ═══════════════════════════════════════════════════════════════════
# CHECK 3: Error Rate
# ═══════════════════════════════════════════════════════════════════
echo ""
echo "🔴 Checking error rate..."

ERROR_LOG="$BRAIN_DIR/error-log.json"
if [[ -f "$ERROR_LOG" ]]; then
    # Count errors in last hour
    ONE_HOUR_AGO=$(date -v-1H +%Y-%m-%dT%H 2>/dev/null || date -d '1 hour ago' +%Y-%m-%dT%H 2>/dev/null || echo "")
    if [[ -n "$ONE_HOUR_AGO" ]]; then
        RECENT_ERRORS=$(grep -c "$ONE_HOUR_AGO" "$ERROR_LOG" 2>/dev/null || echo "0")
        if [[ $RECENT_ERRORS -gt $ERROR_THRESHOLD ]]; then
            log_anomaly "error_spike" "Found $RECENT_ERRORS errors in last hour (threshold: $ERROR_THRESHOLD)" "warning"
        else
            echo "  ✅ Recent errors: $RECENT_ERRORS (threshold: $ERROR_THRESHOLD)"
        fi
    else
        echo "  ℹ️  Unable to check error rate"
    fi
else
    echo "  ✅ No error log (clean)"
fi

# ═══════════════════════════════════════════════════════════════════
# CHECK 4: Risk Exposure
# ═══════════════════════════════════════════════════════════════════
echo ""
echo "💰 Checking risk exposure..."

# This would ideally connect to actual broker APIs
# For now, we check the documented positions
if [[ -f "$POSITIONS_FILE" ]]; then
    # Count active positions as rough proxy
    ACTIVE_COUNT=$(grep -c "Status: OPEN\|Status: ACTIVE" "$POSITIONS_FILE" 2>/dev/null || echo "0")
    if [[ $ACTIVE_COUNT -gt 5 ]]; then
        log_anomaly "high_exposure" "Have $ACTIVE_COUNT active positions (consider reducing)" "warning"
    else
        echo "  ✅ Active positions: $ACTIVE_COUNT"
    fi
fi

# ═══════════════════════════════════════════════════════════════════
# CHECK 5: Cognitive State Anomalies
# ═══════════════════════════════════════════════════════════════════
echo ""
echo "🧠 Checking cognitive state..."

STATE_FILE="$BRAIN_DIR/cognitive-state.json"
if [[ -f "$STATE_FILE" ]]; then
    python3 << 'PYTHON_SCRIPT' 2>/dev/null || true
import json
import sys

STATE_FILE = "/Users/atlasbuilds/clawd/memory/atlas-brain/cognitive-state.json"

try:
    with open(STATE_FILE, 'r') as f:
        state = json.load(f)
    
    stress = state.get('stress_level', 'low')
    energy = state.get('energy_level', 'high')
    
    issues = []
    if stress in ['high', 'critical']:
        issues.append(f"High stress: {stress}")
    if energy in ['low', 'depleted']:
        issues.append(f"Low energy: {energy}")
    
    if issues:
        print(f"  ⚠️  State issues: {', '.join(issues)}")
        sys.exit(1)
    else:
        print(f"  ✅ Cognitive state: stress={stress}, energy={energy}")
except Exception as e:
    print(f"  ℹ️  Unable to check state: {e}")
PYTHON_SCRIPT
else
    echo "  ℹ️  No cognitive state file"
fi

# ═══════════════════════════════════════════════════════════════════
# CHECK 6: Pattern Violations
# ═══════════════════════════════════════════════════════════════════
echo ""
echo "🔮 Checking pattern violations..."

PATTERNS_FILE="$BRAIN_DIR/pattern-database.json"
if [[ -f "$PATTERNS_FILE" ]]; then
    python3 << 'PYTHON_SCRIPT' 2>/dev/null || true
import json

PATTERNS_FILE = "/Users/atlasbuilds/clawd/memory/atlas-brain/pattern-database.json"

try:
    with open(PATTERNS_FILE, 'r') as f:
        data = json.load(f)
    
    negative_patterns = []
    for name, info in data.get('patterns', {}).items():
        weight = info.get('weight', 0)
        if weight < -0.5:
            negative_patterns.append(f"{name} ({weight:.2f})")
    
    if negative_patterns:
        print(f"  ⚠️  Strongly negative patterns: {', '.join(negative_patterns[:3])}")
    else:
        print("  ✅ No critically negative patterns")
except Exception as e:
    print(f"  ℹ️  Unable to check patterns: {e}")
PYTHON_SCRIPT
else
    echo "  ℹ️  No pattern database yet"
fi

# ═══════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [[ $ANOMALIES_FOUND -eq 0 ]]; then
    echo "✅ No anomalies detected - all systems normal"
else
    echo "⚠️  Found $ANOMALIES_FOUND anomalies - review above"
fi
echo ""
echo "Log: $ANOMALY_LOG"
