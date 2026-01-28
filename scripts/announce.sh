#!/usr/bin/env bash
# ATLAS Smart Announcement System
# Context-aware speech that respects quiet hours and importance levels
# Usage: announce.sh "message" [--level critical|major|normal] [--category type]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SPEAK_SCRIPT="$SCRIPT_DIR/atlas-speak.sh"
CONFIG_FILE="/Users/atlasbuilds/clawd/memory/.audio/announce-config.json"
LOG_FILE="/Users/atlasbuilds/clawd/memory/.audio/announce-log.json"

# Defaults
MESSAGE=""
LEVEL="normal"
CATEGORY="general"
FORCE=false

# Parse args
while [[ $# -gt 0 ]]; do
    case "$1" in
        --level)
            LEVEL="$2"
            shift 2
            ;;
        --category)
            CATEGORY="$2"
            shift 2
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --help|-h)
            cat <<EOF
Usage: announce.sh "message" [options]

Options:
  --level    critical|major|normal (default: normal)
  --category trade|alert|research|task|general (default: general)
  --force    Speak regardless of quiet hours

Levels:
  critical - Always speaks (3 AM alerts, emergency losses)
  major    - Speaks except 11 PM - 6 AM (big trades, completions)
  normal   - Only 7 AM - 10 PM (routine updates)

Categories:
  trade    - Trading alerts (entries, exits, P&L)
  alert    - System alerts (errors, anomalies)
  research - Research completions
  task     - Task completions
  general  - Everything else
EOF
            exit 0
            ;;
        *)
            MESSAGE="$1"
            shift
            ;;
    esac
done

if [[ -z "$MESSAGE" ]]; then
    echo "Error: No message provided" >&2
    exit 1
fi

# Get current hour (24h format)
CURRENT_HOUR=$(date +%H)

# Determine if we should speak based on level and time
should_speak() {
    if [[ "$FORCE" == "true" ]]; then
        return 0
    fi

    case "$LEVEL" in
        critical)
            # Always speak
            return 0
            ;;
        major)
            # Speak except 11 PM - 6 AM
            if [[ $CURRENT_HOUR -ge 6 && $CURRENT_HOUR -lt 23 ]]; then
                return 0
            fi
            return 1
            ;;
        normal)
            # Only 7 AM - 10 PM
            if [[ $CURRENT_HOUR -ge 7 && $CURRENT_HOUR -lt 22 ]]; then
                return 0
            fi
            return 1
            ;;
        *)
            # Default to normal behavior
            if [[ $CURRENT_HOUR -ge 7 && $CURRENT_HOUR -lt 22 ]]; then
                return 0
            fi
            return 1
            ;;
    esac
}

# Ensure directories exist
mkdir -p "$(dirname "$LOG_FILE")"

# Log the announcement (always)
LOG_ENTRY=$(cat <<EOF
{"timestamp":"$(date -Iseconds)","message":"$(echo "$MESSAGE" | sed 's/"/\\"/g')","level":"$LEVEL","category":"$CATEGORY","hour":$CURRENT_HOUR,"spoken":false}
EOF
)

# Check if we should speak
if should_speak; then
    # Determine urgency for speak script
    SPEAK_ARGS=""
    if [[ "$LEVEL" == "critical" ]]; then
        SPEAK_ARGS="--urgent"
    fi

    # Speak the message
    "$SPEAK_SCRIPT" "$MESSAGE" $SPEAK_ARGS
    
    # Update log to mark as spoken
    LOG_ENTRY=$(cat <<EOF
{"timestamp":"$(date -Iseconds)","message":"$(echo "$MESSAGE" | sed 's/"/\\"/g')","level":"$LEVEL","category":"$CATEGORY","hour":$CURRENT_HOUR,"spoken":true}
EOF
)
    echo "📢 Announced: $MESSAGE"
else
    echo "🔇 Queued (quiet hours): $MESSAGE"
fi

# Write log
echo "$LOG_ENTRY" >> "$LOG_FILE"
