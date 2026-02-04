#!/bin/bash
# Log rotation script for Clawdbot gateway logs
# Run daily via cron: 0 2 * * * /Users/atlasbuilds/clawd/memory/scripts/log-rotation.sh

LOG_DIR="/Users/atlasbuilds/.clawdbot/logs"
MAX_SIZE_MB=100
KEEP_DAYS=7

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

rotate_log() {
    local log_file="$1"
    local max_size_bytes=$((MAX_SIZE_MB * 1024 * 1024))
    
    if [ ! -f "$log_file" ]; then
        return 0
    fi
    
    local size=$(stat -f%z "$log_file" 2>/dev/null || echo 0)
    
    if [ "$size" -gt "$max_size_bytes" ]; then
        log "Rotating $log_file (size: $((size/1024/1024))MB)"
        
        # Create timestamped backup
        local timestamp=$(date '+%Y%m%d_%H%M%S')
        local backup_file="${log_file}.${timestamp}"
        
        mv "$log_file" "$backup_file"
        touch "$log_file"
        
        log "Created backup: $backup_file"
        
        # Restart gateway to pick up new log file
        log "Restarting clawdbot gateway..."
        clawdbot gateway restart 2>/dev/null || true
    fi
}

cleanup_old() {
    log "Cleaning up logs older than $KEEP_DAYS days..."
    find "$LOG_DIR" -name "*.old" -mtime +$KEEP_DAYS -delete 2>/dev/null
    find "$LOG_DIR" -name "gateway.err.log.*" -mtime +$KEEP_DAYS -delete 2>/dev/null
    find "$LOG_DIR" -name "gateway.log.*" -mtime +$KEEP_DAYS -delete 2>/dev/null
}

main() {
    log "Starting log rotation for Clawdbot..."
    
    # Ensure log directory exists
    mkdir -p "$LOG_DIR"
    
    # Rotate main logs
    rotate_log "$LOG_DIR/gateway.err.log"
    rotate_log "$LOG_DIR/gateway.log"
    
    # Clean up old backups
    cleanup_old
    
    log "Log rotation complete"
}

main