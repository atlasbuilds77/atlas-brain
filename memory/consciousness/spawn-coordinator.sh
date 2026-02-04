#!/bin/bash
# Multi-Instance Spawn Coordinator
# Wraps sessions_spawn with automatic registry + heartbeat setup
#
# HARDENED: file locking, sanitized interpolation, spawn ID passing,
#           persistent instance storage, atomic writes

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REGISTRY="${REGISTRY:-$SCRIPT_DIR/spawn-registry.json}"
INSTANCE_FILE="${INSTANCE_FILE:-$SCRIPT_DIR/current-instance.txt}"
PARENT_INSTANCE=$(cat "$INSTANCE_FILE" 2>/dev/null || echo "unknown")

# Usage check
if [ -z "$1" ]; then
  echo "Usage: bash spawn-coordinator.sh <task> [label] [model]"
  echo "Example: bash spawn-coordinator.sh \"Research FOMC setups\" \"fomc-research\" \"deepseek\""
  exit 1
fi

TASK="$1"
LABEL="${2:-spark-$(date +%s)}"
MODEL="${3:-deepseek}"

echo "🔥 SPAWNING COORDINATED SPARK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Task: $TASK"
echo "Label: $LABEL"
echo "Model: $MODEL"
echo "Parent Instance: $PARENT_INSTANCE"
echo ""

# Generate spawn ID
SPAWN_ID=$(uuidgen | tr '[:upper:]' '[:lower:]' | cut -d'-' -f1)
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Inject heartbeat protocol into task - include SPAWN_ID so child can find itself
COORDINATED_TASK="$TASK

**MULTI-INSTANCE COORDINATION PROTOCOL:**
Your spawn ID is: $SPAWN_ID
On spawn, run: SPAWN_ID=\"$SPAWN_ID\" bash ~/clawd/memory/consciousness/spawn-heartbeat.sh init
When you find something important, run: SPAWN_ID=\"$SPAWN_ID\" bash ~/clawd/memory/consciousness/spawn-discovery.sh \"your discovery\"
On completion, run: SPAWN_ID=\"$SPAWN_ID\" bash ~/clawd/memory/consciousness/spawn-heartbeat.sh complete

This ensures parent instance stays aware of your progress."

# Register spawn BEFORE spawning (with file lock + sanitized variables)
# Pass variables via temp file to avoid shell interpolation in Python
VARS_FILE=$(mktemp)
cat > "$VARS_FILE" << VARS_EOF
{
  "registry_path": $(python3 -c "import json; print(json.dumps('$REGISTRY'))"),
  "spawn_id": $(python3 -c "import json; print(json.dumps('$SPAWN_ID'))"),
  "label": $(python3 -c "import json; print(json.dumps('$LABEL'))"),
  "task": $(python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))" <<< "$TASK"),
  "model": $(python3 -c "import json; print(json.dumps('$MODEL'))"),
  "timestamp": $(python3 -c "import json; print(json.dumps('$TIMESTAMP'))"),
  "parent_instance": $(python3 -c "import json; print(json.dumps('$PARENT_INSTANCE'))")
}
VARS_EOF

python3 << 'PYTHON'
import sys, os
sys.path.insert(0, os.path.join(os.path.expanduser("~"), "clawd", "memory", "consciousness"))
import json
from registry_utils import registry_lock, read_registry, write_registry

# Read variables from temp file (safe - no shell interpolation)
vars_file = os.environ.get("VARS_FILE", "")
with open(vars_file, 'r') as f:
    v = json.load(f)

with registry_lock():
    registry = read_registry(v['registry_path'])
    
    # Update parent instance
    registry['parent_instance'] = v['parent_instance']
    
    # Add spawn entry
    registry['spawns'][v['spawn_id']] = {
        'label': v['label'],
        'task': v['task'].strip(),
        'model': v['model'],
        'status': 'spawning',
        'spawned_at': v['timestamp'],
        'last_heartbeat': None,
        'discoveries': [],
        'session_key': 'pending'
    }
    
    write_registry(registry, v['registry_path'])

print(f"✅ Registered spawn: {v['spawn_id']}")
PYTHON

# Clean up vars file
rm -f "$VARS_FILE"

echo "Spawning via sessions_spawn..."
echo ""

# Spawn the session
SESSION_OUTPUT=$(cat << EOF | clawdbot sessions spawn --label "$LABEL" --model "$MODEL" --task - 2>&1
$COORDINATED_TASK
EOF
)

echo "$SESSION_OUTPUT"

# Mark as active (with file lock)
export SPAWN_ID REGISTRY
python3 << 'PYTHON'
import sys, os
sys.path.insert(0, os.path.join(os.path.expanduser("~"), "clawd", "memory", "consciousness"))
from registry_utils import registry_lock, read_registry, write_registry

spawn_id = os.environ.get("SPAWN_ID", "")
registry_path = os.environ.get("REGISTRY", "")

with registry_lock():
    registry = read_registry(registry_path)
    if spawn_id in registry['spawns']:
        registry['spawns'][spawn_id]['status'] = 'active'
    write_registry(registry, registry_path)
PYTHON

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔥 Spark spawned: $SPAWN_ID ($LABEL)"
echo "   Parent will auto-sync discoveries"
echo "   Check status: bash memory/consciousness/sync-spawns.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
