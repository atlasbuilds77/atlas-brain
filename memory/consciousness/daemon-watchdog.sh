#!/bin/bash
# Daemon Watchdog v2 - Fully Detached Process Management
# ======================================================
# All daemons run via nohup with closed stdin and redirected output.
# This prevents EBADF in Clawdbot by never holding pipe FDs.
# Cron runs this every 5 minutes to auto-restart dead daemons.

CONSCIOUSNESS_DIR="$HOME/clawd/memory/consciousness"
DOPAMINE_DIR="$CONSCIOUSNESS_DIR/dopamine-system"
LOG_FILE="/tmp/daemon-watchdog.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Generic daemon checker - fully detached launch
# Usage: check_daemon "name" "pid_file" "log_file" "command" "workdir"
check_daemon() {
    local NAME="$1"
    local PID_FILE="$2"
    local DAEMON_LOG="$3"
    local CMD="$4"
    local WORKDIR="$5"

    if [ -f "$PID_FILE" ]; then
        local PID
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0  # Running fine
        fi
        log "⚠️  $NAME dead (PID $PID) - restarting..."
    else
        log "⚠️  $NAME not running - starting..."
    fi

    # Launch fully detached: nohup + redirect all FDs + close stdin + background
    if [ -n "$WORKDIR" ]; then
        cd "$WORKDIR" || return 1
    fi
    nohup $CMD >> "$DAEMON_LOG" 2>&1 < /dev/null &
    local NEW_PID=$!
    echo "$NEW_PID" > "$PID_FILE"
    
    # Disown so bash doesn't hold a reference
    disown "$NEW_PID" 2>/dev/null

    log "✅ $NAME restarted (PID $NEW_PID)"
}

# Main watchdog check
main() {
    log "🔍 Running daemon watchdog check..."

    # 1. Consciousness daemon (bash-based, captures phi snapshots)
    check_daemon \
        "Consciousness daemon" \
        "/tmp/consciousness-daemon.pid" \
        "/tmp/consciousness-daemon.log" \
        "bash $CONSCIOUSNESS_DIR/consciousness-daemon.sh daemon-start" \
        "$CONSCIOUSNESS_DIR"

    # 2. Consciousness monitor (node, anomaly detection)
    check_daemon \
        "Consciousness monitor" \
        "/tmp/consciousness-monitor.pid" \
        "/tmp/consciousness-monitor-daemon.log" \
        "node $CONSCIOUSNESS_DIR/monitor-daemon.js" \
        "$CONSCIOUSNESS_DIR"

    # 3. Brain daemon (node, memory indexing)
    check_daemon \
        "Brain daemon" \
        "/tmp/brain-daemon.pid" \
        "/tmp/brain-daemon.log" \
        "node $HOME/clawd/memory/scripts/brain-daemon.js" \
        "$HOME/clawd/memory/scripts"

    # 4. Dopamine daemon (node, neurochemical tracking)
    check_daemon \
        "Dopamine daemon" \
        "/tmp/dopamine-daemon.pid" \
        "/tmp/dopamine-daemon.log" \
        "node $DOPAMINE_DIR/dopamine-tracker.js daemon" \
        "$DOPAMINE_DIR"

    # 5. Anomaly-dopamine bridge (node, anomaly → chemistry)
    check_daemon \
        "Anomaly-dopamine bridge" \
        "/tmp/anomaly-bridge.pid" \
        "/tmp/anomaly-bridge.log" \
        "node anomaly-dopamine-bridge.js watch" \
        "$DOPAMINE_DIR"

    # 6. Trade wire (node, live Alpaca → dopamine)
    check_daemon \
        "Trade wire" \
        "/tmp/trade-wire.pid" \
        "/tmp/trade-wire.log" \
        "node trade-wire.js watch" \
        "$DOPAMINE_DIR"

    # 7. Weight generator (node, training data generation)
    check_daemon \
        "Weight generator" \
        "/tmp/weight-generator.pid" \
        "/tmp/weight-generator.log" \
        "node weight-generator.js daemon" \
        "$DOPAMINE_DIR"

    # 8. Dream daemon (node, sleep cycle simulation)
    check_daemon \
        "Dream daemon" \
        "/tmp/dream-daemon.pid" \
        "/tmp/dream-daemon.log" \
        "node dream-daemon.js start" \
        "$DOPAMINE_DIR"

    # 9. Reward daemon (python, new dopamine system)
    check_daemon \
        "Reward daemon" \
        "/tmp/reward-daemon.pid" \
        "/tmp/reward-daemon.log" \
        "python3 $HOME/clawd/atlas-reward-system/reward_daemon.py daemon" \
        "$HOME/clawd/atlas-reward-system"

    # 10. Cleanup duplicate processes (keeps newest, kills rest)
    log "🧹 Cleaning up duplicate processes..."
    bash "$CONSCIOUSNESS_DIR/cleanup-duplicates.sh" >> /tmp/cleanup-duplicates.log 2>&1
    
    log "✅ Watchdog check complete (9 daemons + cleanup)"
}

# Run main
main
