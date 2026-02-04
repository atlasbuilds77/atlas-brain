#!/bin/bash
# Parent Spawn Sync
# Parent instance runs this to check for discoveries from spawns
#
# HARDENED: file locking on all write operations, safe Python heredocs

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REGISTRY="${REGISTRY:-$SCRIPT_DIR/spawn-registry.json}"
ACTION="${1:-check}"

export REGISTRY

case "$ACTION" in
  check)
    echo "🔍 CHECKING SPAWN STATUS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Read-only operation still uses lock for consistency
    python3 << 'PYTHON'
import sys, os
sys.path.insert(0, os.path.join(os.path.expanduser("~"), "clawd", "memory", "consciousness"))
from registry_utils import registry_lock, read_registry
from datetime import datetime

registry_path = os.environ.get("REGISTRY", "")

try:
    with registry_lock():
        registry = read_registry(registry_path)
    
    spawns = registry.get('spawns', {})
    discovery_bus = registry.get('discovery_bus', [])
    
    if not spawns:
        print("No active spawns")
    else:
        print(f"\n📊 ACTIVE SPAWNS: {len(spawns)}\n")
        
        for spawn_id, spawn_data in spawns.items():
            label = spawn_data.get('label', 'unknown')
            status = spawn_data.get('status', 'unknown')
            task_raw = spawn_data.get('task', '')
            task = task_raw[:60] + '...' if len(task_raw) > 60 else task_raw
            
            # Calculate heartbeat freshness
            last_hb = spawn_data.get('last_heartbeat')
            if last_hb:
                hb_time = datetime.fromisoformat(last_hb.replace('Z', '+00:00'))
                age_minutes = (datetime.now(hb_time.tzinfo) - hb_time).total_seconds() / 60
                hb_status = f"✓ {age_minutes:.0f}m ago" if age_minutes < 10 else f"⚠ {age_minutes:.0f}m ago"
            else:
                hb_status = "⚠ Never"
            
            print(f"🔥 {spawn_id[:8]} ({label})")
            print(f"   Status: {status}")
            print(f"   Task: {task}")
            print(f"   Heartbeat: {hb_status}")
            print(f"   Discoveries: {len(spawn_data.get('discoveries', []))}")
            print()
    
    # Check for unread discoveries
    unread = [d for d in discovery_bus if not d.get('read_by_parent', False)]
    
    if unread:
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"📢 NEW DISCOVERIES: {len(unread)}\n")
        
        for disco in unread:
            spawn_label = disco.get('spawn_label', 'unknown')
            timestamp = disco.get('timestamp', '')
            discovery = disco.get('discovery', '')
            
            print(f"🔥 {spawn_label} ({timestamp}):")
            print(f"   {discovery}\n")
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
except FileNotFoundError:
    print("No spawn registry found")
except Exception as e:
    print(f"Error reading registry: {e}")
PYTHON
    ;;
    
  mark-read)
    echo "✅ Marking all discoveries as read..."
    
    python3 << 'PYTHON'
import sys, os
sys.path.insert(0, os.path.join(os.path.expanduser("~"), "clawd", "memory", "consciousness"))
from registry_utils import registry_lock, read_registry, write_registry

registry_path = os.environ.get("REGISTRY", "")

try:
    with registry_lock():
        registry = read_registry(registry_path)
        
        for disco in registry.get('discovery_bus', []):
            disco['read_by_parent'] = True
        
        write_registry(registry, registry_path)
    
    print("✅ All discoveries marked as read")
    
except Exception as e:
    print(f"Error: {e}")
PYTHON
    ;;
    
  clean)
    echo "🧹 Cleaning completed spawns..."
    
    python3 << 'PYTHON'
import sys, os
sys.path.insert(0, os.path.join(os.path.expanduser("~"), "clawd", "memory", "consciousness"))
from registry_utils import registry_lock, read_registry, write_registry
from datetime import datetime, timedelta

registry_path = os.environ.get("REGISTRY", "")

try:
    with registry_lock():
        registry = read_registry(registry_path)
        
        # Remove spawns completed > 24h ago
        cutoff = datetime.utcnow() - timedelta(hours=24)
        cleaned = 0
        
        spawns_to_keep = {}
        for spawn_id, spawn_data in registry.get('spawns', {}).items():
            if spawn_data.get('status') == 'complete':
                completed_at = spawn_data.get('completed_at')
                if completed_at:
                    comp_time = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
                    if comp_time.replace(tzinfo=None) < cutoff:
                        cleaned += 1
                        continue
            
            spawns_to_keep[spawn_id] = spawn_data
        
        registry['spawns'] = spawns_to_keep
        write_registry(registry, registry_path)
    
    print(f"✅ Cleaned {cleaned} old spawns")
    
except Exception as e:
    print(f"Error: {e}")
PYTHON
    ;;
    
  *)
    echo "Usage: bash sync-spawns.sh [check|mark-read|clean]"
    echo ""
    echo "  check      - View spawn status and discoveries"
    echo "  mark-read  - Mark all discoveries as read"
    echo "  clean      - Remove spawns completed >24h ago"
    exit 1
    ;;
esac
