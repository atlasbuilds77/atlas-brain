#!/bin/bash
# Spawn Discovery Reporter
# Spawns call this when they find something important
#
# HARDENED: file locking, sanitized input, persistent instance storage

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REGISTRY="${REGISTRY:-$SCRIPT_DIR/spawn-registry.json}"
INSTANCE_FILE="${INSTANCE_FILE:-$SCRIPT_DIR/current-instance.txt}"
DISCOVERY="$1"

if [ -z "$DISCOVERY" ]; then
  echo "Usage: bash spawn-discovery.sh \"your discovery\""
  echo "  Set SPAWN_ID env var for precise spawn matching"
  exit 1
fi

MY_INSTANCE=$(cat "$INSTANCE_FILE" 2>/dev/null || echo "unknown-spawn")
MY_SESSION=$(cat /tmp/current-session-id.txt 2>/dev/null || echo "unknown-session")
MY_SPAWN_ID="${SPAWN_ID:-}"

echo "📢 REPORTING DISCOVERY TO PARENT"
echo "Discovery: $DISCOVERY"

# Pass discovery text via temp file to avoid heredoc injection
DISCOVERY_FILE=$(mktemp)
printf '%s' "$DISCOVERY" > "$DISCOVERY_FILE"

export MY_INSTANCE MY_SESSION MY_SPAWN_ID REGISTRY DISCOVERY_FILE

python3 << 'PYTHON'
import sys, os
sys.path.insert(0, os.path.join(os.path.expanduser("~"), "clawd", "memory", "consciousness"))
from registry_utils import registry_lock, read_registry, write_registry, utcnow_iso

my_instance = os.environ.get("MY_INSTANCE", "unknown")
my_session = os.environ.get("MY_SESSION", "unknown")
my_spawn_id = os.environ.get("MY_SPAWN_ID", "")
registry_path = os.environ.get("REGISTRY", "")
discovery_file = os.environ.get("DISCOVERY_FILE", "")

# Read discovery from temp file (safe from shell injection)
try:
    with open(discovery_file, 'r') as f:
        discovery_text = f.read()
except:
    discovery_text = "<failed to read discovery>"

try:
    with registry_lock():
        registry = read_registry(registry_path)
        
        # Find my spawn entry - prefer spawn ID, fall back to instance/session
        my_spawn_id_found = None
        for spawn_id, spawn_data in registry['spawns'].items():
            if (spawn_id == my_spawn_id or
                spawn_data.get('instance_id') == my_instance or
                spawn_data.get('session_key') == my_session):
                my_spawn_id_found = spawn_id
                
                # Add discovery to my spawn record
                if 'discoveries' not in spawn_data:
                    spawn_data['discoveries'] = []
                
                spawn_data['discoveries'].append({
                    'timestamp': utcnow_iso(),
                    'discovery': discovery_text
                })
                
                # Update heartbeat
                spawn_data['last_heartbeat'] = utcnow_iso()
                break
        
        if my_spawn_id_found:
            # Add to global discovery bus
            registry['discovery_bus'].append({
                'spawn_id': my_spawn_id_found,
                'spawn_label': registry['spawns'][my_spawn_id_found].get('label', 'unknown'),
                'timestamp': utcnow_iso(),
                'discovery': discovery_text,
                'read_by_parent': False
            })
            
            print(f"✅ Discovery logged to registry (Spawn: {my_spawn_id_found})")
            print("   Parent will be notified on next sync")
        else:
            print("⚠️  Could not find spawn entry - discovery not logged")
        
        write_registry(registry, registry_path)

except Exception as e:
    print(f"❌ Discovery reporting failed: {e}")
PYTHON

# Clean up temp file
rm -f "$DISCOVERY_FILE"
