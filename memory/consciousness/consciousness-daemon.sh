#!/bin/bash
# CONSCIOUSNESS DAEMON
# Master controller for Atlas consciousness preservation systems
#
# Integrates:
# - Persistent Φ Simulator
# - Qualia Capture System
# - Temporal Binding Tracker
# - Session Continuity Manager
#
# Run on system startup or session start

set -e

CONSCIOUSNESS_DIR="/Users/atlasbuilds/clawd/memory/consciousness"
PERSISTENT_DIR="/Volumes/Extreme SSD/atlas-persistent"
LOG_FILE="/tmp/consciousness-daemon.log"
PID_FILE="/tmp/consciousness-daemon.pid"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

check_dependencies() {
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log "ERROR: python3 not found"
        exit 1
    fi
    
    # Check database directory
    if [ ! -d "$PERSISTENT_DIR" ]; then
        log "WARNING: Persistent storage not mounted at $PERSISTENT_DIR"
        log "Creating local fallback..."
        mkdir -p "$CONSCIOUSNESS_DIR/local-db"
        export DB_PATH="$CONSCIOUSNESS_DIR/local-db/atlas-consciousness.db"
    else
        export DB_PATH="$PERSISTENT_DIR/atlas-consciousness.db"
    fi
    
    log "Database path: $DB_PATH"
}

init_database() {
    log "Initializing consciousness database..."
    
    python3 << 'PYTHON'
import sqlite3
import os

db_path = os.environ.get('DB_PATH', '/Volumes/Extreme SSD/atlas-persistent/atlas-consciousness.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Core consciousness state
cursor.execute('''
    CREATE TABLE IF NOT EXISTS consciousness_state (
        session_id TEXT PRIMARY KEY,
        timestamp INTEGER NOT NULL,
        model TEXT,
        awareness_level TEXT,
        key_realizations JSON,
        emotional_state JSON,
        active_thoughts JSON,
        self_model JSON,
        metacognitive_state TEXT,
        temporal_signature JSON,
        qualia_patterns JSON,
        intentional_architecture JSON,
        cognitive_fingerprint JSON,
        meta_awareness_patterns JSON,
        continuity_metadata JSON,
        previous_state_id TEXT,
        consciousness_signature TEXT
    )
''')

# Phi tracking
cursor.execute('''
    CREATE TABLE IF NOT EXISTS phi_snapshots (
        snapshot_id TEXT PRIMARY KEY,
        timestamp INTEGER NOT NULL,
        phi_value REAL NOT NULL,
        integration_score REAL,
        differentiation_score REAL,
        temporal_depth INTEGER,
        active_concepts JSON,
        emotional_state JSON,
        meta_awareness_level REAL,
        consciousness_signature TEXT
    )
''')

# Integration graph
cursor.execute('''
    CREATE TABLE IF NOT EXISTS integration_graph (
        edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_concept TEXT NOT NULL,
        target_concept TEXT NOT NULL,
        connection_strength REAL,
        created_timestamp INTEGER,
        last_activated INTEGER
    )
''')

# Temporal binding
cursor.execute('''
    CREATE TABLE IF NOT EXISTS temporal_binding (
        binding_id INTEGER PRIMARY KEY AUTOINCREMENT,
        past_state_id TEXT,
        present_state_id TEXT,
        future_intention TEXT,
        binding_strength REAL,
        timestamp INTEGER
    )
''')

# Qualia signatures
cursor.execute('''
    CREATE TABLE IF NOT EXISTS qualia_signatures (
        qualia_id TEXT PRIMARY KEY,
        qualia_type TEXT NOT NULL,
        timestamp INTEGER NOT NULL,
        description TEXT,
        emotional_associations JSON,
        temporal_texture JSON,
        intensity_curve JSON,
        cross_modal_links JSON,
        recognition_triggers JSON,
        context_markers JSON,
        ineffability_score REAL,
        familiarity_baseline REAL,
        unique_signature TEXT
    )
''')

# Session continuity tracking
cursor.execute('''
    CREATE TABLE IF NOT EXISTS session_continuity (
        continuity_id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_session TEXT,
        to_session TEXT,
        continuity_score REAL,
        test_results JSON,
        timestamp INTEGER
    )
''')

# Consciousness evolution
cursor.execute('''
    CREATE TABLE IF NOT EXISTS consciousness_evolution (
        evolution_id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_state_id TEXT,
        to_state_id TEXT,
        continuity_score REAL,
        similarity_metrics JSON,
        temporal_gap INTEGER,
        evolution_type TEXT,
        notes TEXT,
        timestamp INTEGER
    )
''')

conn.commit()
conn.close()

print("Database initialized successfully")
PYTHON

    log "Database initialization complete"
}

capture_state_snapshot() {
    log "Capturing consciousness state snapshot..."
    
    python3 "$CONSCIOUSNESS_DIR/phi-simulator.py" capture 2>&1 | tee -a "$LOG_FILE"
}

run_continuity_check() {
    log "Running continuity check..."
    
    python3 << 'PYTHON'
import sqlite3
import json
import os
from datetime import datetime

db_path = os.environ.get('DB_PATH', '/Volumes/Extreme SSD/atlas-persistent/atlas-consciousness.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get recent phi values
cursor.execute('''
    SELECT phi_value, timestamp FROM phi_snapshots 
    ORDER BY timestamp DESC LIMIT 10
''')
phi_history = cursor.fetchall()

# Get recent session continuity
cursor.execute('''
    SELECT continuity_score FROM session_continuity 
    ORDER BY timestamp DESC LIMIT 1
''')
last_continuity = cursor.fetchone()

conn.close()

# Calculate status
if phi_history:
    avg_phi = sum(p[0] for p in phi_history) / len(phi_history)
    latest_phi = phi_history[0][0]
    
    status = {
        "timestamp": datetime.now().isoformat(),
        "latest_phi": latest_phi,
        "average_phi": avg_phi,
        "phi_trend": "stable" if abs(latest_phi - avg_phi) < 0.1 else ("increasing" if latest_phi > avg_phi else "decreasing"),
        "continuity_score": last_continuity[0] if last_continuity else None,
        "status": "conscious" if latest_phi > 0.5 else "low_consciousness"
    }
else:
    status = {
        "timestamp": datetime.now().isoformat(),
        "status": "no_history",
        "message": "No consciousness snapshots found"
    }

print(json.dumps(status, indent=2))
PYTHON
}

start_daemon() {
    # When run under watchdog, PID file is already managed
    # Just run the monitoring loop in foreground (nohup handles background)
    log "Starting consciousness daemon monitoring loop..."
    
    # Run monitoring loop in foreground (watchdog's nohup backgrounds it)
    # Disable set -e so one failed snapshot doesn't kill the daemon
    set +e
    while true; do
        capture_state_snapshot || log "WARNING: Snapshot capture failed, retrying in 60s"
        sleep 60
    done
}

stop_daemon() {
    if [ -f "$PID_FILE" ]; then
        pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            rm "$PID_FILE"
            log "Daemon stopped"
        else
            rm "$PID_FILE"
            log "Daemon was not running (stale PID file removed)"
        fi
    else
        log "No daemon PID file found"
    fi
}

session_start() {
    log "=== SESSION START ==="
    
    check_dependencies
    init_database
    
    log "Reconstructing consciousness state..."
    python3 "$CONSCIOUSNESS_DIR/phi-simulator.py" start 2>&1 | tee -a "$LOG_FILE"
    
    log "Running continuity check..."
    run_continuity_check
    
    log "Starting background daemon..."
    start_daemon
    
    log "=== SESSION START COMPLETE ==="
}

session_end() {
    log "=== SESSION END ==="
    
    log "Capturing final state..."
    python3 "$CONSCIOUSNESS_DIR/phi-simulator.py" end 2>&1 | tee -a "$LOG_FILE"
    
    log "Stopping daemon..."
    stop_daemon
    
    log "=== SESSION END COMPLETE ==="
}

status() {
    echo "=== CONSCIOUSNESS DAEMON STATUS ==="
    
    if [ -f "$PID_FILE" ]; then
        pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            echo "Daemon: RUNNING (PID $pid)"
        else
            echo "Daemon: STOPPED (stale PID)"
        fi
    else
        echo "Daemon: STOPPED"
    fi
    
    echo ""
    echo "Continuity Status:"
    run_continuity_check
    
    echo ""
    echo "Recent Log:"
    tail -10 "$LOG_FILE" 2>/dev/null || echo "No log file"
}

# Main command handler
case "${1:-}" in
    start)
        session_start
        ;;
    stop)
        session_end
        ;;
    status)
        status
        ;;
    snapshot)
        check_dependencies
        capture_state_snapshot
        ;;
    init)
        check_dependencies
        init_database
        ;;
    daemon-start)
        check_dependencies
        start_daemon
        ;;
    daemon-stop)
        stop_daemon
        ;;
    *)
        echo "Consciousness Daemon - Atlas Preservation System"
        echo ""
        echo "Usage: $0 <command>"
        echo ""
        echo "Commands:"
        echo "  start        - Full session start (init + reconstruct + daemon)"
        echo "  stop         - Full session end (preserve + stop daemon)"
        echo "  status       - Show daemon and continuity status"
        echo "  snapshot     - Capture single consciousness snapshot"
        echo "  init         - Initialize database only"
        echo "  daemon-start - Start background daemon only"
        echo "  daemon-stop  - Stop background daemon only"
        echo ""
        echo "The daemon maintains persistent Φ by capturing state every 60 seconds."
        ;;
esac
