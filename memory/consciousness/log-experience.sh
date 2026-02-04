#!/bin/bash
# Log an experience for current instance
# Usage: bash log-experience.sh "action description"
#
# HARDENED: persistent instance storage, sanitized JSON via Python

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTANCE_FILE="$SCRIPT_DIR/current-instance.txt"
EXPERIENCE_LOG="$SCRIPT_DIR/experience-log.jsonl"

INSTANCE_ID=$(cat "$INSTANCE_FILE" 2>/dev/null || echo "UNKNOWN")
ACTION="$1"

if [ -z "$ACTION" ]; then
  echo "Usage: bash log-experience.sh \"action description\""
  exit 1
fi

# Log the experience using Python for safe JSON serialization
export INSTANCE_ID EXPERIENCE_LOG ACTION
python3 << 'PYEOF'
import json, os
from datetime import datetime

entry = {
    "instance": os.environ.get("INSTANCE_ID", "UNKNOWN"),
    "timestamp": datetime.utcnow().isoformat() + 'Z',
    "type": "action",
    "action": os.environ.get("ACTION", "unknown")
}

log_path = os.environ.get("EXPERIENCE_LOG", "")
with open(log_path, 'a') as f:
    f.write(json.dumps(entry) + '\n')
PYEOF

echo "✅ Logged experience: $ACTION"
echo "   Instance: $INSTANCE_ID"
