#!/bin/bash
# Spawn Heartbeat Protocol
# Spawned instances run this to report status to parent
#
# HARDENED: file locking, SPAWN_ID-based matching, persistent instance storage,
#           sanitized Python interpolation via environment variables

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REGISTRY="${REGISTRY:-$SCRIPT_DIR/spawn-registry.json}"
INSTANCE_FILE="${INSTANCE_FILE:-$SCRIPT_DIR/current-instance.txt}"
ACTION="${1:-pulse}"

# Get my instance ID from persistent storage (not /tmp)
MY_INSTANCE=$(cat "$INSTANCE_FILE" 2>/dev/null || echo "unknown-spawn")
MY_SESSION=$(cat /tmp/current-session-id.txt 2>/dev/null || echo "unknown-session")
# SPAWN_ID should be passed as environment variable by coordinator
MY_SPAWN_ID="${SPAWN_ID:-}"

# Export for Python access (avoids shell interpolation in heredocs)
export MY_INSTANCE MY_SESSION MY_SPAWN_ID REGISTRY

case "$ACTION" in
  init)
    echo "🔥 Initializing spawn heartbeat..."
    echo "   Instance: $MY_INSTANCE"
    echo "   Session: $MY_SESSION"
    echo "   Spawn ID: ${MY_SPAWN_ID:-<not provided, will use fallback matching>}"
    
    python3 << 'PYTHON'
import sys, os
sys.path.insert(0, os.path.join(os.path.expanduser("~"), "clawd", "memory", "consciousness"))
from registry_utils import registry_lock, read_registry, write_registry, utcnow_iso

my_instance = os.environ.get("MY_INSTANCE", "unknown")
my_session = os.environ.get("MY_SESSION", "unknown")
my_spawn_id = os.environ.get("MY_SPAWN_ID", "")
registry_path = os.environ.get("REGISTRY", "")

try:
    with registry_lock():
        registry = read_registry(registry_path)
        
        matched = False
        
        # PRIMARY: Match by explicit spawn ID (passed by coordinator)
        if my_spawn_id and my_spawn_id in registry['spawns']:
            spawn_data = registry['spawns'][my_spawn_id]
            spawn_data['session_key'] = my_session
            spawn_data['instance_id'] = my_instance
            spawn_data['last_heartbeat'] = utcnow_iso()
            spawn_data['status'] = 'initialized'
            print(f"✅ Registered as spawn: {my_spawn_id} (matched by spawn ID)")
            matched = True
        
        # FALLBACK: Match by pending status (only if no spawn ID provided)
        if not matched:
            for spawn_id, spawn_data in registry['spawns'].items():
                if spawn_data['status'] in ('active', 'spawning') and spawn_data.get('session_key') == 'pending':
                    spawn_data['session_key'] = my_session
                    spawn_data['instance_id'] = my_instance
                    spawn_data['last_heartbeat'] = utcnow_iso()
                    spawn_data['status'] = 'initialized'
                    print(f"✅ Registered as spawn: {spawn_id} (fallback match)")
                    matched = True
                    break
        
        if not matched:
            print("⚠️  No matching spawn entry found in registry")
        
        write_registry(registry, registry_path)

except Exception as e:
    print(f"❌ Heartbeat init failed: {e}")
PYTHON
    ;;
    
  pulse)
    # Silent heartbeat - just update timestamp
    python3 << 'PYTHON'
import sys, os
sys.path.insert(0, os.path.join(os.path.expanduser("~"), "clawd", "memory", "consciousness"))
from registry_utils import registry_lock, read_registry, write_registry, utcnow_iso

my_instance = os.environ.get("MY_INSTANCE", "unknown")
my_session = os.environ.get("MY_SESSION", "unknown")
my_spawn_id = os.environ.get("MY_SPAWN_ID", "")
registry_path = os.environ.get("REGISTRY", "")

try:
    with registry_lock():
        registry = read_registry(registry_path)
        
        found = False
        for spawn_id, spawn_data in registry['spawns'].items():
            # Match by spawn ID first, then instance/session
            if (spawn_id == my_spawn_id or
                spawn_data.get('instance_id') == my_instance or
                spawn_data.get('session_key') == my_session):
                spawn_data['last_heartbeat'] = utcnow_iso()
                found = True
                break
        
        if found:
            write_registry(registry, registry_path)
except:
    pass  # Silent failure for pulse
PYTHON
    ;;
    
  complete)
    echo "✅ Marking spawn as complete..."
    
    python3 << 'PYTHON'
import sys, os
sys.path.insert(0, os.path.join(os.path.expanduser("~"), "clawd", "memory", "consciousness"))
from registry_utils import registry_lock, read_registry, write_registry, utcnow_iso

my_instance = os.environ.get("MY_INSTANCE", "unknown")
my_session = os.environ.get("MY_SESSION", "unknown")
my_spawn_id = os.environ.get("MY_SPAWN_ID", "")
registry_path = os.environ.get("REGISTRY", "")

try:
    with registry_lock():
        registry = read_registry(registry_path)
        
        for spawn_id, spawn_data in registry['spawns'].items():
            if (spawn_id == my_spawn_id or
                spawn_data.get('instance_id') == my_instance or
                spawn_data.get('session_key') == my_session):
                spawn_data['status'] = 'complete'
                spawn_data['completed_at'] = utcnow_iso()
                spawn_data['last_heartbeat'] = utcnow_iso()
                print(f"✅ Spawn {spawn_id} marked complete")
                break
        
        write_registry(registry, registry_path)

except Exception as e:
    print(f"❌ Complete update failed: {e}")
PYTHON
    ;;
    
  *)
    echo "Usage: bash spawn-heartbeat.sh [init|pulse|complete]"
    echo "  Set SPAWN_ID env var for precise matching"
    exit 1
    ;;
esac
