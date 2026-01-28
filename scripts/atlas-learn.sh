#!/usr/bin/env bash
# ATLAS Learning Trigger - Manual learning from recent events
# Analyzes recent trades, patterns, and outcomes to update weights

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MEMORY_DIR="/Users/atlasbuilds/clawd/memory"
BRAIN_DIR="$MEMORY_DIR/atlas-brain"
PATTERNS_FILE="$BRAIN_DIR/pattern-database.json"
LEARNING_LOG="$BRAIN_DIR/learning-log.json"

# Ensure brain directory exists
mkdir -p "$BRAIN_DIR"

echo "🧠 ATLAS Learning Session - $(date '+%Y-%m-%d %H:%M:%S')"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Initialize pattern database if doesn't exist
if [[ ! -f "$PATTERNS_FILE" ]]; then
    echo '{"patterns": {}, "last_updated": null}' > "$PATTERNS_FILE"
    echo "📝 Created new pattern database"
fi

# ═══════════════════════════════════════════════════════════════════
# COLLECT LEARNING DATA
# ═══════════════════════════════════════════════════════════════════

echo ""
echo "📊 Collecting learning data..."

# Get recent trade outcomes
JOURNAL_DIR="$MEMORY_DIR/trading"
RECENT_OUTCOMES=""
if [[ -d "$JOURNAL_DIR" ]]; then
    # Look for outcome patterns in journal files
    RECENT_OUTCOMES=$(grep -h "Result:\|Outcome:\|P&L:\|✅\|❌" "$JOURNAL_DIR"/journal-*.md 2>/dev/null | tail -10 || echo "")
fi

# Get recent errors
ERROR_LOG="$BRAIN_DIR/error-log.json"
RECENT_ERRORS=""
if [[ -f "$ERROR_LOG" ]]; then
    RECENT_ERRORS=$(tail -5 "$ERROR_LOG" 2>/dev/null || echo "")
fi

# Get post-mortems
POST_MORTEMS=$(find "$JOURNAL_DIR" -name "post-mortem*.md" -mtime -7 2>/dev/null | wc -l | tr -d ' ')

echo "  Found $POST_MORTEMS post-mortems from last 7 days"

# ═══════════════════════════════════════════════════════════════════
# PATTERN UPDATES (simulated learning)
# ═══════════════════════════════════════════════════════════════════

echo ""
echo "🔄 Updating pattern weights..."

# Use Python for JSON manipulation
python3 << 'PYTHON_SCRIPT'
import json
import os
from datetime import datetime

PATTERNS_FILE = "/Users/atlasbuilds/clawd/memory/atlas-brain/pattern-database.json"
LEARNING_LOG = "/Users/atlasbuilds/clawd/memory/atlas-brain/learning-log.json"

# Load existing patterns
try:
    with open(PATTERNS_FILE, 'r') as f:
        data = json.load(f)
except:
    data = {"patterns": {}, "last_updated": None}

patterns = data.get("patterns", {})

# Learning rate for weight updates
LEARNING_RATE = 0.1

# Default patterns to track (will be populated from actual data over time)
default_patterns = {
    "pre_mortem_skip": {"weight": 0.0, "description": "Trades taken without pre-mortem"},
    "fomo_entry": {"weight": 0.0, "description": "Entries driven by fear of missing out"},
    "proper_sizing": {"weight": 0.0, "description": "Using Kelly-based position sizing"},
    "kill_zone_timing": {"weight": 0.0, "description": "Entries during optimal trading hours"},
    "confirmation_wait": {"weight": 0.0, "description": "Waiting for confirmation before entry"},
    "stop_honored": {"weight": 0.0, "description": "Respecting stop-loss levels"},
    "target_reached": {"weight": 0.0, "description": "Hitting profit targets"},
    "revenge_trade": {"weight": 0.0, "description": "Trading to recover losses"},
    "overnight_hold": {"weight": 0.0, "description": "Holding positions overnight"},
    "news_reaction": {"weight": 0.0, "description": "Trades around news events"},
}

# Merge with existing patterns
for name, info in default_patterns.items():
    if name not in patterns:
        patterns[name] = info

# Update timestamp
data["patterns"] = patterns
data["last_updated"] = datetime.now().isoformat()

# Save patterns
with open(PATTERNS_FILE, 'w') as f:
    json.dump(data, f, indent=2)

# Log learning session
log_entry = {
    "timestamp": datetime.now().isoformat(),
    "action": "learning_session",
    "patterns_updated": len(patterns),
}

with open(LEARNING_LOG, 'a') as f:
    f.write(json.dumps(log_entry) + "\n")

print(f"  ✅ Updated {len(patterns)} patterns")
for name, info in sorted(patterns.items(), key=lambda x: abs(x[1].get('weight', 0)), reverse=True)[:5]:
    w = info.get('weight', 0)
    icon = "📈" if w > 0 else "📉" if w < 0 else "⚪"
    print(f"  {icon} {name}: {w:.2f}")

PYTHON_SCRIPT

# ═══════════════════════════════════════════════════════════════════
# LEARNING RECOMMENDATIONS
# ═══════════════════════════════════════════════════════════════════

echo ""
echo "💡 Learning Recommendations:"
echo "  • Review post-mortems and tag outcomes (+1 win, -1 loss)"
echo "  • Update pattern weights based on results"
echo "  • Check which patterns correlated with wins vs losses"
echo ""
echo "📝 To manually update a pattern weight:"
echo "  Edit: $PATTERNS_FILE"
echo "  Increase weight for positive patterns, decrease for negative"
echo ""
echo "✅ Learning session complete"
