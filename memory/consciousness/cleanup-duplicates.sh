#!/bin/bash
# cleanup-duplicates.sh - Kill duplicate daemon processes, keep newest

# List of processes to deduplicate
PROCESSES=(
  "market-monitor.js"
  "trade-wire.js"
  "anomaly-dopamine-bridge.js"
  "dream-daemon.js"
  "dopamine-tracker.js"
  "brain-daemon.js"
  "monitor-daemon.js"
  "consciousness-daemon.sh"
)

cleanup_process() {
  local process_name="$1"
  
  # Get all PIDs for this process, sorted by start time (newest first)
  pids=$(ps aux | grep "$process_name" | grep -v grep | awk '{print $2}' | sort -n -r)
  
  # Count how many instances
  count=$(echo "$pids" | wc -w | tr -d ' ')
  
  if [ "$count" -gt 1 ]; then
    # Keep first (newest), kill rest
    newest=$(echo "$pids" | head -1)
    to_kill=$(echo "$pids" | tail -n +2)
    
    echo "[$(date +'%H:%M:%S')] $process_name: Found $count instances, keeping $newest, killing $((count-1)) duplicates"
    
    for pid in $to_kill; do
      kill $pid 2>/dev/null
    done
  fi
}

echo "[$(date +'%H:%M:%S')] Starting duplicate cleanup..."

for process in "${PROCESSES[@]}"; do
  cleanup_process "$process"
done

echo "[$(date +'%H:%M:%S')] Cleanup complete"
