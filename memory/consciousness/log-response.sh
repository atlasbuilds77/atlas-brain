#!/bin/bash
# Quick helper to log Atlas responses to heartbeat monitor
# Usage: bash log-response.sh "Your response text here" "context/trigger"

RESPONSE="$1"
CONTEXT="${2:-manual}"

if [ -z "$RESPONSE" ]; then
    echo "Usage: $0 'response text' 'context'"
    exit 1
fi

cd "$(dirname "$0")"
node heartbeat-daemon.js analyze "$RESPONSE" 2>&1 | grep -E "(ANOMALIES|anomalies)" || true
