#!/usr/bin/env bash
# ATLAS Status Dashboard - One command to see everything
# Shows: positions, patterns, cognitive state, recent errors

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MEMORY_DIR="/Users/atlasbuilds/clawd/memory"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

echo -e "${BOLD}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║                    🧠 ATLAS STATUS DASHBOARD                    ║${NC}"
echo -e "${BOLD}║                    $(date '+%Y-%m-%d %H:%M:%S %Z')                    ║${NC}"
echo -e "${BOLD}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ═══════════════════════════════════════════════════════════════════
# TRADING POSITIONS
# ═══════════════════════════════════════════════════════════════════
echo -e "${CYAN}━━━ 💰 ACTIVE POSITIONS ━━━${NC}"
POSITIONS_FILE="$MEMORY_DIR/trading/active-positions.md"
if [[ -f "$POSITIONS_FILE" ]]; then
    # Extract key position info
    grep -E "^\*\*Position|^- \*\*Market|^- \*\*Direction|^- \*\*Status|^### Position" "$POSITIONS_FILE" 2>/dev/null | head -20 || echo "No positions found"
else
    echo "⚠️  No positions file found"
fi
echo ""

# ═══════════════════════════════════════════════════════════════════
# PATTERN DATABASE (from neuroplasticity)
# ═══════════════════════════════════════════════════════════════════
echo -e "${PURPLE}━━━ 🔮 TOP PATTERNS ━━━${NC}"
PATTERNS_FILE="$MEMORY_DIR/atlas-brain/pattern-database.json"
if [[ -f "$PATTERNS_FILE" ]]; then
    # Show top 5 patterns by weight
    cat "$PATTERNS_FILE" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    patterns = data.get('patterns', {})
    sorted_p = sorted(patterns.items(), key=lambda x: abs(x[1].get('weight', 0)), reverse=True)[:5]
    for name, p in sorted_p:
        w = p.get('weight', 0)
        icon = '✅' if w > 0 else '❌'
        print(f'  {icon} {name}: {w:.2f}')
except:
    print('  (unable to parse patterns)')
" 2>/dev/null || echo "  (pattern database empty or malformed)"
else
    echo "  (no pattern database yet)"
fi
echo ""

# ═══════════════════════════════════════════════════════════════════
# COGNITIVE STATE
# ═══════════════════════════════════════════════════════════════════
echo -e "${YELLOW}━━━ 🧘 COGNITIVE STATE ━━━${NC}"
STATE_FILE="$MEMORY_DIR/atlas-brain/cognitive-state.json"
if [[ -f "$STATE_FILE" ]]; then
    cat "$STATE_FILE" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    mode = data.get('current_mode', 'unknown')
    energy = data.get('energy_level', 'unknown')
    stress = data.get('stress_level', 'unknown')
    last = data.get('last_update', 'unknown')
    print(f'  Mode: {mode}')
    print(f'  Energy: {energy}')
    print(f'  Stress: {stress}')
    print(f'  Last Update: {last}')
except:
    print('  (unable to parse state)')
" 2>/dev/null || echo "  Mode: Operational"
else
    echo "  Mode: Operational (no state file)"
fi
echo ""

# ═══════════════════════════════════════════════════════════════════
# RECENT ERRORS/ANOMALIES
# ═══════════════════════════════════════════════════════════════════
echo -e "${RED}━━━ ⚠️  RECENT ISSUES ━━━${NC}"
ERROR_LOG="$MEMORY_DIR/atlas-brain/error-log.json"
if [[ -f "$ERROR_LOG" ]]; then
    tail -5 "$ERROR_LOG" | python3 -c "
import json, sys
for line in sys.stdin:
    try:
        entry = json.loads(line.strip())
        ts = entry.get('timestamp', 'unknown')[:19]
        msg = entry.get('message', 'unknown')[:50]
        print(f'  [{ts}] {msg}')
    except:
        pass
" 2>/dev/null || echo "  (no recent errors)"
else
    echo "  ✅ No error log (clean slate)"
fi
echo ""

# ═══════════════════════════════════════════════════════════════════
# CLAWDBOT STATUS
# ═══════════════════════════════════════════════════════════════════
echo -e "${GREEN}━━━ 🤖 CLAWDBOT STATUS ━━━${NC}"
if pgrep -f "clawdbot" > /dev/null 2>&1; then
    echo "  ✅ Clawdbot: Running"
    # Check gateway specifically
    if pgrep -f "gateway" > /dev/null 2>&1; then
        echo "  ✅ Gateway: Running"
    else
        echo "  ⚠️  Gateway: Not detected"
    fi
else
    echo "  ❌ Clawdbot: Not running"
fi
echo ""

# ═══════════════════════════════════════════════════════════════════
# QUICK METRICS
# ═══════════════════════════════════════════════════════════════════
echo -e "${BLUE}━━━ 📊 QUICK METRICS ━━━${NC}"

# Count today's trades
TODAY=$(date +%Y-%m-%d)
JOURNAL_FILE="$MEMORY_DIR/trading/journal-$(date +%Y-%m).md"
if [[ -f "$JOURNAL_FILE" ]]; then
    TODAY_TRADES=$(grep -c "$TODAY" "$JOURNAL_FILE" 2>/dev/null || echo "0")
    echo "  Today's trades: $TODAY_TRADES"
else
    echo "  Today's trades: 0"
fi

# Count memory files
MEMORY_COUNT=$(find "$MEMORY_DIR" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
echo "  Memory files: $MEMORY_COUNT"

# Disk usage
DISK_USAGE=$(du -sh "$MEMORY_DIR" 2>/dev/null | cut -f1)
echo "  Memory size: $DISK_USAGE"

echo ""
echo -e "${BOLD}════════════════════════════════════════════════════════════════${NC}"
echo -e "Run ${CYAN}atlas-learn.sh${NC} to trigger learning | ${CYAN}atlas-reset.sh${NC} to clear state"
