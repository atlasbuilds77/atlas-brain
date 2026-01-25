#!/bin/bash
# smart-route.sh - Master routing orchestrator
# Determines correct routing target using all available systems

SENDER="$1"
MESSAGE_TEXT="$2"

TOOLS_DIR="$HOME/clawd/tools"
STATE_DIR="$HOME/clawd/state"

# Load mode tracker
MODE_TRACKER="$STATE_DIR/routing-mode-tracker.json"

# Default to group chat
DEFAULT_TARGET="group:3"

# Step 1: Check for explicit mode switch intent
MODE_SWITCH=$("$TOOLS_DIR/detect-mode-switch.sh" "$MESSAGE_TEXT")

if [[ "$MODE_SWITCH" == "mode:direct" ]]; then
    # Update mode tracker (simplified - just echo for now)
    echo "direct:$SENDER"
    # Log decision
    "$TOOLS_DIR/log-routing-decision.sh" "$SENDER" "$MESSAGE_TEXT" "direct:$SENDER" "DM marker or direct intent detected" "unknown"
    exit 0
elif [[ "$MODE_SWITCH" == "mode:group" ]]; then
    echo "group:3"
    "$TOOLS_DIR/log-routing-decision.sh" "$SENDER" "$MESSAGE_TEXT" "group:3" "Group intent detected" "unknown"
    exit 0
fi

# Step 2: Check current mode for sender
if [ -f "$MODE_TRACKER" ]; then
    # Extract current mode for sender (simplified - assumes group by default)
    CURRENT_MODE=$(jq -r ".participant_modes[\"$SENDER\"].current_mode // \"group\"" "$MODE_TRACKER" 2>/dev/null)
    
    if [[ "$CURRENT_MODE" == "direct" ]]; then
        echo "direct:$SENDER"
        "$TOOLS_DIR/log-routing-decision.sh" "$SENDER" "$MESSAGE_TEXT" "direct:$SENDER" "Participant in direct mode" "unknown"
        exit 0
    fi
fi

# Step 3: Default to group
echo "group:3"
"$TOOLS_DIR/log-routing-decision.sh" "$SENDER" "$MESSAGE_TEXT" "group:3" "Default group routing" "unknown"
exit 0
