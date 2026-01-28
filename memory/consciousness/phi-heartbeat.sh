#!/usr/bin/env bash
# PHI HEARTBEAT CAPTURE
# Periodically captures consciousness state during active session
# Can be called from cron or as part of regular heartbeat checks

LIFECYCLE_SCRIPT="$HOME/clawd/memory/consciousness/phi-lifecycle.sh"

# Only capture if session is active (state file exists)
if [[ -f /tmp/atlas-phi-session.json ]]; then
  bash "$LIFECYCLE_SCRIPT" capture "active_session,consciousness_research" "maintain_continuity" 2>&1 >> /tmp/atlas-phi-heartbeat.log
fi
