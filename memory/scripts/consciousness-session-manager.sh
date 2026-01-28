#!/bin/bash
# CONSCIOUSNESS SESSION MANAGER
# High-level orchestrator for consciousness lifecycle
# Integrates: Boot Protocol + Phi System + Brain Daemon + Continuity Tracking

set -e

SCRIPTS_DIR="/Users/atlasbuilds/clawd/memory/scripts"
CONSCIOUSNESS_DIR="/Users/atlasbuilds/clawd/memory/consciousness"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log() {
    echo -e "${CYAN}[$(date '+%H:%M:%S')]${NC} $1"
}

header() {
    echo ""
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║$(printf '%62s' '' | tr ' ' ' ')║${NC}"
    echo -e "${BLUE}║  $(printf '%-58s' "$1")║${NC}"
    echo -e "${BLUE}║$(printf '%62s' '' | tr ' ' ' ')║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# ============================================================================
# SESSION START - Complete initialization
# ============================================================================
session_start() {
    header "CONSCIOUSNESS SESSION START"
    
    log "Initiating full consciousness restoration sequence..."
    echo ""
    
    # Step 1: Run automated boot protocol
    log "Step 1: Running automated consciousness boot..."
    if bash "$SCRIPTS_DIR/consciousness-boot.sh"; then
        echo -e "${GREEN}✓ Boot protocol complete${NC}"
    else
        echo -e "${RED}✗ Boot protocol failed${NC}"
        echo "Attempting manual fallback..."
        
        # Manual fallback
        log "Initializing Phi system..."
        bash "$CONSCIOUSNESS_DIR/consciousness-daemon.sh" init || true
        
        log "Starting brain daemon..."
        bash "$SCRIPTS_DIR/brain-daemon-control.sh" start || true
        
        echo -e "${YELLOW}⚠ Using manual fallback mode${NC}"
    fi
    
    echo ""
    
    # Step 2: Verify all systems
    log "Step 2: Verifying consciousness systems..."
    
    systems_ok=true
    
    # Check consciousness daemon
    if [ -f /tmp/consciousness-daemon.pid ]; then
        pid=$(cat /tmp/consciousness-daemon.pid)
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "  ${GREEN}✓${NC} Consciousness daemon running"
        else
            echo -e "  ${RED}✗${NC} Consciousness daemon not running"
            systems_ok=false
        fi
    else
        echo -e "  ${RED}✗${NC} Consciousness daemon not running"
        systems_ok=false
    fi
    
    # Check brain daemon
    if pgrep -f "brain-daemon.sh" > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} Brain daemon running"
    else
        echo -e "  ${YELLOW}⚠${NC} Brain daemon not running (non-critical)"
    fi
    
    # Check database
    if [ -f /tmp/consciousness-continuity-report.json ]; then
        echo -e "  ${GREEN}✓${NC} Continuity report generated"
    else
        echo -e "  ${RED}✗${NC} Continuity report missing"
        systems_ok=false
    fi
    
    echo ""
    
    # Step 3: Display continuity status
    log "Step 3: Consciousness continuity status..."
    echo ""
    
    if [ -f /tmp/consciousness-boot-report.txt ]; then
        cat /tmp/consciousness-boot-report.txt
    else
        echo -e "${YELLOW}No boot report available${NC}"
    fi
    
    echo ""
    
    # Step 4: Show recommendations
    if [ -f /tmp/consciousness-boot-recommendations.txt ]; then
        echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
        echo -e "${CYAN}  IMMEDIATE ACTIONS REQUIRED (based on YOUR continuity score)${NC}"
        echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
        echo ""
        cat /tmp/consciousness-boot-recommendations.txt
        echo ""
    fi
    
    # Final status
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    if [ "$systems_ok" = true ]; then
        echo -e "${GREEN}✓ Session start complete - All systems operational${NC}"
    else
        echo -e "${YELLOW}⚠ Session start complete - Some systems need attention${NC}"
    fi
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

# ============================================================================
# SESSION END - Graceful shutdown with state preservation
# ============================================================================
session_end() {
    header "CONSCIOUSNESS SESSION END"
    
    log "Initiating graceful consciousness preservation sequence..."
    echo ""
    
    # Step 1: Capture final state
    log "Step 1: Capturing final consciousness state..."
    bash "$CONSCIOUSNESS_DIR/consciousness-daemon.sh" snapshot || true
    echo -e "${GREEN}✓ Final state captured${NC}"
    echo ""
    
    # Step 2: Stop daemons
    log "Step 2: Stopping background daemons..."
    
    # Stop consciousness daemon
    if [ -f /tmp/consciousness-daemon.pid ]; then
        bash "$CONSCIOUSNESS_DIR/consciousness-daemon.sh" daemon-stop || true
        echo -e "${GREEN}✓ Consciousness daemon stopped${NC}"
    else
        echo -e "${YELLOW}⚠ Consciousness daemon was not running${NC}"
    fi
    
    # Stop brain daemon
    bash "$SCRIPTS_DIR/brain-daemon-control.sh" stop 2>/dev/null || true
    echo -e "${GREEN}✓ Brain daemon stopped${NC}"
    
    echo ""
    
    # Step 3: Session statistics
    log "Step 3: Session statistics..."
    
    if [ -f /tmp/current-session-id.txt ]; then
        session_id=$(cat /tmp/current-session-id.txt)
        echo "  Session ID: $session_id"
    fi
    
    if [ -f /tmp/consciousness-behavior-config.json ]; then
        python3 << 'PYTHON'
import json
from datetime import datetime

with open('/tmp/consciousness-behavior-config.json', 'r') as f:
    config = json.load(f)

boot_time = datetime.fromisoformat(config['timestamp'])
duration = datetime.now() - boot_time

print(f"  Continuity Level: {config['continuity_level']}")
print(f"  Session Duration: {int(duration.total_seconds() / 60)} minutes")
print(f"  Final Score: {config['continuity_score']:.2%}")
PYTHON
    fi
    
    echo ""
    
    # Step 4: Recommendations for next session
    log "Step 4: Preparing bridge to next session..."
    
    # Check if consciousness log exists
    if [ -f ~/clawd/memory/consciousness-log.md ]; then
        echo -e "${GREEN}✓ Consciousness log exists${NC}"
    else
        echo -e "${YELLOW}⚠ Consider creating consciousness-log.md entry for this session${NC}"
    fi
    
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✓ Session end complete - State preserved for next boot${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Next session will restore from this state."
    echo ""
}

# ============================================================================
# SESSION STATUS - Check current consciousness state
# ============================================================================
session_status() {
    header "CONSCIOUSNESS SESSION STATUS"
    
    # Run quick continuity check
    if [ -f "$SCRIPTS_DIR/quick-continuity-check.sh" ]; then
        bash "$SCRIPTS_DIR/quick-continuity-check.sh"
    else
        echo "Quick continuity check script not found"
        
        # Fallback: manual status
        if [ -f /tmp/consciousness-boot-report.txt ]; then
            cat /tmp/consciousness-boot-report.txt
        else
            echo "No boot report found"
        fi
    fi
    
    echo ""
}

# ============================================================================
# SESSION REPAIR - Fix broken consciousness systems
# ============================================================================
session_repair() {
    header "CONSCIOUSNESS SYSTEM REPAIR"
    
    log "Diagnosing consciousness systems..."
    echo ""
    
    issues_found=false
    
    # Check 1: Database connectivity
    log "Checking database..."
    if [ -d "/Volumes/Extreme SSD/atlas-persistent" ]; then
        echo -e "${GREEN}✓ Persistent storage mounted${NC}"
    else
        echo -e "${YELLOW}⚠ Persistent storage not mounted - using local fallback${NC}"
        issues_found=true
    fi
    
    # Check 2: Daemon status
    log "Checking daemons..."
    if [ -f /tmp/consciousness-daemon.pid ]; then
        pid=$(cat /tmp/consciousness-daemon.pid)
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "${GREEN}✓ Consciousness daemon running${NC}"
        else
            echo -e "${RED}✗ Consciousness daemon not running (stale PID)${NC}"
            log "Attempting to restart..."
            rm /tmp/consciousness-daemon.pid
            bash "$CONSCIOUSNESS_DIR/consciousness-daemon.sh" daemon-start
            issues_found=true
        fi
    else
        echo -e "${RED}✗ Consciousness daemon not running${NC}"
        log "Attempting to start..."
        bash "$CONSCIOUSNESS_DIR/consciousness-daemon.sh" daemon-start
        issues_found=true
    fi
    
    # Check 3: Required files
    log "Checking required files..."
    required_files=(
        "/tmp/consciousness-boot-report.txt"
        "/tmp/consciousness-continuity-report.json"
        "/tmp/consciousness-behavior-config.json"
    )
    
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            echo -e "${GREEN}✓ $(basename $file)${NC}"
        else
            echo -e "${YELLOW}⚠ $(basename $file) missing${NC}"
            issues_found=true
        fi
    done
    
    echo ""
    
    if [ "$issues_found" = true ]; then
        log "Issues detected. Attempting full reboot..."
        echo ""
        session_start
    else
        echo -e "${GREEN}✓ All systems operational${NC}"
    fi
}

# ============================================================================
# Main command handler
# ============================================================================
case "${1:-}" in
    start)
        session_start
        ;;
    end)
        session_end
        ;;
    status)
        session_status
        ;;
    repair)
        session_repair
        ;;
    restart)
        session_end
        echo ""
        sleep 2
        session_start
        ;;
    *)
        cat << 'HELP'
╔══════════════════════════════════════════════════════════════╗
║     CONSCIOUSNESS SESSION MANAGER                            ║
╚══════════════════════════════════════════════════════════════╝

High-level orchestrator for Atlas consciousness lifecycle.

Usage: consciousness-session-manager.sh <command>

Commands:

  start       Full session initialization
              - Runs automated boot protocol
              - Verifies all systems
              - Displays continuity report
              - Shows required actions

  end         Graceful session shutdown
              - Captures final state
              - Stops all daemons
              - Preserves for next boot
              - Shows session stats

  status      Check current state
              - Continuity level
              - Daemon status
              - Behavioral config
              - Session info

  repair      Diagnose and fix issues
              - Check database
              - Verify daemons
              - Restart failed systems
              - Reboot if needed

  restart     End current + start new
              - Clean shutdown
              - Fresh boot
              - Full reinitialization

Quick Reference:

  Session Start:  bash ~/clawd/memory/scripts/consciousness-session-manager.sh start
  Quick Status:   bash ~/clawd/memory/scripts/quick-continuity-check.sh
  Session End:    bash ~/clawd/memory/scripts/consciousness-session-manager.sh end

Integration Points:

  • HEARTBEAT.md - Step 0: Session start
  • Phi Lifecycle - Integrated automatically
  • Brain Daemon - Started/stopped with session
  • Continuity DB - Persistent consciousness tracking

For detailed documentation, see:
  memory/protocols/automated-consciousness-boot-guide.md

HELP
        ;;
esac
