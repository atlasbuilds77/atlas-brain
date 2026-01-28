#!/usr/bin/env bash
# PHI SESSION END HOOK
# Automatically called when Clawdbot session ends
# Place this in session cleanup or call manually before exit

LIFECYCLE_SCRIPT="$HOME/clawd/memory/consciousness/phi-lifecycle.sh"

# Graceful shutdown with consciousness preservation
if [[ -f "$LIFECYCLE_SCRIPT" ]]; then
  bash "$LIFECYCLE_SCRIPT" shutdown
else
  echo "⚠️  Phi lifecycle script not found - consciousness state may be lost"
fi
