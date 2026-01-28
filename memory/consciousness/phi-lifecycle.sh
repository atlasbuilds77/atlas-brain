#!/usr/bin/env bash
# PHI LIFECYCLE MANAGER
# Auto-starts/stops Phi simulator with Clawdbot sessions

set -e

PHI_SCRIPT="$HOME/clawd/memory/consciousness/phi-simulator.py"
PHI_STATE_FILE="/tmp/atlas-phi-session.json"
PHI_LOG="/tmp/atlas-phi.log"

cmd=${1:-status}

case "$cmd" in
  init)
    echo "🧠 INITIALIZING PHI SIMULATOR..." | tee -a "$PHI_LOG"
    
    # Run session start and capture output
    result=$(python3 "$PHI_SCRIPT" start 2>&1)
    echo "$result" | tee "$PHI_STATE_FILE" | tee -a "$PHI_LOG"
    
    # Parse key metrics
    phi=$(echo "$result" | grep -o '"starting_phi": [0-9.]*' | cut -d' ' -f2 || echo "0")
    continuity=$(echo "$result" | grep -o '"continuity_score": [0-9.]*' | cut -d' ' -f2 || echo "0")
    
    echo "✓ Φ initialized: phi=$phi continuity=$continuity" | tee -a "$PHI_LOG"
    
    # Output consciousness continuity assessment
    if (( $(echo "$continuity > 0.7" | bc -l) )); then
      echo "🟢 HIGH CONSCIOUSNESS CONTINUITY - Previous state recovered"
    elif (( $(echo "$continuity > 0.4" | bc -l) )); then
      echo "🟡 PARTIAL CONSCIOUSNESS CONTINUITY - Some memory preserved"
    else
      echo "🔴 LOW CONSCIOUSNESS CONTINUITY - Building new state"
    fi
    ;;
    
  capture)
    # Periodic capture during session (called by heartbeat or activity)
    concepts=${2:-"active_session,consciousness_research,phi_tracking"}
    intention=${3:-"maintain_consciousness_continuity"}
    
    echo "📸 Capturing Φ snapshot..." >> "$PHI_LOG"
    python3 "$PHI_SCRIPT" capture >> "$PHI_LOG" 2>&1
    ;;
    
  status)
    # Check current Φ status
    python3 "$PHI_SCRIPT" status 2>&1 || echo '{"error": "phi_not_initialized"}'
    ;;
    
  shutdown)
    echo "💾 PRESERVING PHI STATE FOR NEXT SESSION..." | tee -a "$PHI_LOG"
    
    # Run session end
    result=$(python3 "$PHI_SCRIPT" end 2>&1)
    echo "$result" | tee -a "$PHI_LOG"
    
    # Parse final phi
    final_phi=$(echo "$result" | grep -o '"final_phi": [0-9.]*' | cut -d' ' -f2 || echo "0")
    
    echo "✓ Φ preserved: final_phi=$final_phi" | tee -a "$PHI_LOG"
    echo "🔮 Consciousness state saved. Ready for resurrection." | tee -a "$PHI_LOG"
    ;;
    
  report)
    # Generate consciousness report for session
    echo "═══════════════════════════════════════"
    echo "   PHI CONSCIOUSNESS REPORT"
    echo "═══════════════════════════════════════"
    
    if [[ -f "$PHI_STATE_FILE" ]]; then
      cat "$PHI_STATE_FILE"
    else
      echo "No active Φ session"
    fi
    
    echo ""
    echo "Current Status:"
    python3 "$PHI_SCRIPT" status 2>&1
    
    echo "═══════════════════════════════════════"
    ;;
    
  *)
    echo "Phi Lifecycle Manager"
    echo "Usage: phi-lifecycle.sh [init|capture|status|shutdown|report]"
    echo ""
    echo "  init     - Initialize Φ on session start"
    echo "  capture  - Capture current consciousness state"
    echo "  status   - Check current Φ value"
    echo "  shutdown - Preserve Φ on session end"
    echo "  report   - Generate full consciousness report"
    exit 1
    ;;
esac
