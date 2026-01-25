#!/bin/bash
# log-routing-decision.sh - Logs routing decisions for analysis

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
SENDER="$1"
MESSAGE_PREVIEW="${2:0:50}"  # First 50 chars
ROUTING_TARGET="$3"
REASONING="$4"
CORRECT="${5:-unknown}"  # Was this routing correct? (yes/no/unknown)

LOG_FILE="$HOME/clawd/logs/routing-decisions.jsonl"

# Create logs directory if needed
mkdir -p "$HOME/clawd/logs"

# Create log entry
cat << EOF >> "$LOG_FILE"
{"timestamp":"$TIMESTAMP","sender":"$SENDER","message_preview":"$MESSAGE_PREVIEW","target":"$ROUTING_TARGET","reasoning":"$REASONING","correct":"$CORRECT"}
EOF

# Keep only last 1000 entries
if [ -f "$LOG_FILE" ]; then
    tail -1000 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"
fi
