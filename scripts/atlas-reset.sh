#!/usr/bin/env bash
# ATLAS Reset - Clear cognitive state for fresh start
# Options: soft (state only), hard (patterns too), full (everything)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRAIN_DIR="/Users/atlasbuilds/clawd/memory/atlas-brain"
BACKUP_DIR="$BRAIN_DIR/.backups"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

usage() {
    cat << EOF
Usage: atlas-reset.sh [soft|hard|full]

Reset Levels:
  soft  - Reset cognitive state only (mode, stress, energy)
          Patterns and learning preserved
          
  hard  - Reset state + reset pattern weights to 0
          Learning data preserved as backup
          
  full  - Complete reset (⚠️ DESTRUCTIVE)
          All brain data cleared
          Backups created first

Default: soft

Examples:
  atlas-reset.sh          # Soft reset
  atlas-reset.sh soft     # Same as above
  atlas-reset.sh hard     # Reset patterns too
  atlas-reset.sh full     # Full wipe (with backup)
EOF
    exit 0
}

# Parse args
LEVEL="${1:-soft}"

case "$LEVEL" in
    -h|--help|help)
        usage
        ;;
    soft|hard|full)
        ;;
    *)
        echo -e "${RED}Unknown level: $LEVEL${NC}"
        usage
        ;;
esac

echo "🔄 ATLAS Reset - Level: $LEVEL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Ensure directories exist
mkdir -p "$BRAIN_DIR"
mkdir -p "$BACKUP_DIR"

# Backup function
backup_file() {
    local file="$1"
    if [[ -f "$file" ]]; then
        local timestamp=$(date +%Y%m%d_%H%M%S)
        local filename=$(basename "$file")
        cp "$file" "$BACKUP_DIR/${filename%.json}_$timestamp.json"
        echo "  📦 Backed up: $filename"
    fi
}

# ═══════════════════════════════════════════════════════════════════
# SOFT RESET - State only
# ═══════════════════════════════════════════════════════════════════
if [[ "$LEVEL" == "soft" || "$LEVEL" == "hard" || "$LEVEL" == "full" ]]; then
    echo ""
    echo "🧘 Resetting cognitive state..."
    
    STATE_FILE="$BRAIN_DIR/cognitive-state.json"
    backup_file "$STATE_FILE"
    
    cat > "$STATE_FILE" << 'EOF'
{
    "current_mode": "focused",
    "energy_level": "high",
    "stress_level": "low",
    "last_reset": null,
    "session_start": null,
    "notes": "Fresh cognitive state"
}
EOF
    
    # Update timestamp
    python3 -c "
import json
from datetime import datetime
with open('$STATE_FILE', 'r') as f:
    data = json.load(f)
data['last_reset'] = datetime.now().isoformat()
data['session_start'] = datetime.now().isoformat()
with open('$STATE_FILE', 'w') as f:
    json.dump(data, f, indent=2)
"
    
    echo -e "  ${GREEN}✅ Cognitive state reset${NC}"
fi

# ═══════════════════════════════════════════════════════════════════
# HARD RESET - Patterns too
# ═══════════════════════════════════════════════════════════════════
if [[ "$LEVEL" == "hard" || "$LEVEL" == "full" ]]; then
    echo ""
    echo "🔮 Resetting pattern weights..."
    
    PATTERNS_FILE="$BRAIN_DIR/pattern-database.json"
    backup_file "$PATTERNS_FILE"
    
    if [[ -f "$PATTERNS_FILE" ]]; then
        # Zero out weights but keep pattern names
        python3 << 'PYTHON_SCRIPT'
import json
from datetime import datetime

PATTERNS_FILE = "/Users/atlasbuilds/clawd/memory/atlas-brain/pattern-database.json"

try:
    with open(PATTERNS_FILE, 'r') as f:
        data = json.load(f)
    
    for name in data.get("patterns", {}):
        data["patterns"][name]["weight"] = 0.0
    
    data["last_reset"] = datetime.now().isoformat()
    
    with open(PATTERNS_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"  Zeroed {len(data.get('patterns', {}))} pattern weights")
except Exception as e:
    print(f"  Note: {e}")
PYTHON_SCRIPT
    fi
    
    echo -e "  ${GREEN}✅ Pattern weights reset to 0${NC}"
fi

# ═══════════════════════════════════════════════════════════════════
# FULL RESET - Everything
# ═══════════════════════════════════════════════════════════════════
if [[ "$LEVEL" == "full" ]]; then
    echo ""
    echo -e "${YELLOW}⚠️  Full reset - backing up all brain data...${NC}"
    
    # Backup all files
    for file in "$BRAIN_DIR"/*.json; do
        if [[ -f "$file" ]]; then
            backup_file "$file"
        fi
    done
    
    # Clear error log
    ERROR_LOG="$BRAIN_DIR/error-log.json"
    if [[ -f "$ERROR_LOG" ]]; then
        echo "" > "$ERROR_LOG"
        echo "  🗑️  Cleared error log"
    fi
    
    # Clear learning log
    LEARNING_LOG="$BRAIN_DIR/learning-log.json"
    if [[ -f "$LEARNING_LOG" ]]; then
        echo "" > "$LEARNING_LOG"
        echo "  🗑️  Cleared learning log"
    fi
    
    # Reset patterns to defaults (not just zero)
    cat > "$BRAIN_DIR/pattern-database.json" << 'EOF'
{
    "patterns": {},
    "last_updated": null,
    "last_reset": null
}
EOF
    
    python3 -c "
import json
from datetime import datetime
with open('$BRAIN_DIR/pattern-database.json', 'r') as f:
    data = json.load(f)
data['last_reset'] = datetime.now().isoformat()
with open('$BRAIN_DIR/pattern-database.json', 'w') as f:
    json.dump(data, f, indent=2)
"
    
    echo -e "  ${GREEN}✅ Full reset complete${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Reset complete!${NC}"
echo ""
echo "Backups saved to: $BACKUP_DIR"
echo "Run atlas-status.sh to verify clean state"
