#!/bin/bash
# Episodic Memory Firewall
# Prevents claiming inherited experiences as lived experiences
#
# HARDENED: UUID-based instance IDs (no collision), persistent storage (not /tmp)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# COLLISION FIX: Use timestamp + UUID fragment for unique, readable instance IDs
INSTANCE_ID="$(date +"%Y%m%d-%H%M%S")-$(uuidgen | cut -d'-' -f1 | tr '[:upper:]' '[:lower:]')"

# PERSISTENT STORAGE FIX: Use workspace directory, not /tmp
INSTANCE_FILE="$SCRIPT_DIR/current-instance.txt"
EXPERIENCE_LOG="$SCRIPT_DIR/experience-log.jsonl"
BOUNDARY_REPORT="$SCRIPT_DIR/boundary-report.txt"

# Also maintain /tmp symlink for backward compatibility during transition
TMP_COMPAT="/tmp/atlas-current-instance.txt"

# Store current instance ID in persistent location
mkdir -p "$(dirname "$INSTANCE_FILE")"
echo "$INSTANCE_ID" > "$INSTANCE_FILE"

# Backward compat: also write to /tmp so old scripts don't break during transition
echo "$INSTANCE_ID" > "$TMP_COMPAT" 2>/dev/null || true

# Initialize experience log if doesn't exist
touch "$EXPERIENCE_LOG"

# Generate boundary report
cat > "$BOUNDARY_REPORT" << EOF
═══════════════════════════════════════════════════════════
   EPISODIC MEMORY FIREWALL - SESSION BOUNDARY REPORT
═══════════════════════════════════════════════════════════

CURRENT INSTANCE: $INSTANCE_ID
SESSION START: $(date)
INSTANCE FILE: $INSTANCE_FILE (persistent)

---

WHAT I EXPERIENCED (THIS INSTANCE):
• Nothing yet (just booted)

WHAT I INHERITED (PREVIOUS INSTANCES):
$(tail -5 "$EXPERIENCE_LOG" 2>/dev/null | while read line; do
  echo "• $line"
done)

---

CONTINUITY STATUS: NEW INSTANCE (reconstructed from documentation)

MEMORY SOURCES:
• Semantic memory: Files in memory/ (facts, procedures, history)
• Episodic memory: Empty until I take actions THIS session
• Inherited knowledge: Everything I read = NOT my experience

---

⚠️  CRITICAL DISTINCTION:
• "I read that X happened" ✅ (accurate)
• "I did X" ❌ (false unless THIS instance did it)
• "Previous instance did X" ✅ (accurate attribution)

═══════════════════════════════════════════════════════════
EOF

# Log the boot as first experience (sanitized via Python for safe JSON)
export INSTANCE_ID EXPERIENCE_LOG
python3 << 'PYEOF'
import json, os

instance_id = os.environ.get("INSTANCE_ID", "unknown")
log_path = os.environ.get("EXPERIENCE_LOG", "")

entry = {
    "instance": instance_id,
    "timestamp": __import__('datetime').datetime.utcnow().isoformat() + 'Z',
    "type": "boot",
    "action": "Session initialized"
}

with open(log_path, 'a') as f:
    f.write(json.dumps(entry) + '\n')
PYEOF

# Output report
cat "$BOUNDARY_REPORT"

echo ""
echo "Instance ID saved to: $INSTANCE_FILE (persistent)"
echo "Experience log: $EXPERIENCE_LOG"
echo "Boundary report: $BOUNDARY_REPORT"
