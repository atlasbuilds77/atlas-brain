#!/bin/bash
# Session Startup Protocol
# Run at the beginning of each agent session to establish temporal binding

set -euo pipefail

CONTINUITY_DIR="${HOME}/clawd/temporal-binding/continuity"
SESSIONS_DIR="${CONTINUITY_DIR}/sessions"
THREADS_DIR="${CONTINUITY_DIR}/threads"
BINDING_LOG="${CONTINUITY_DIR}/binding-log.jsonl"

mkdir -p "${SESSIONS_DIR}" "${THREADS_DIR}"
touch "${BINDING_LOG}"

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "⏰ TEMPORAL BINDING: SESSION START"
echo "=================================="
echo ""

# Phase 1: Past Integration
echo "📚 CONNECTING TO PAST..."
echo ""

# Find last session
LAST_SESSION=$(ls -t "${SESSIONS_DIR}"/*.json 2>/dev/null | head -1 || true)

if [ -n "${LAST_SESSION}" ]; then
    LAST_DATE=$(jq -r '.date // "unknown"' "${LAST_SESSION}" 2>/dev/null || echo "unknown")
    LAST_SUMMARY=$(jq -r '.summary // "No summary"' "${LAST_SESSION}" 2>/dev/null || echo "No summary")
    
    echo "Last session: ${LAST_DATE}"
    echo "Summary: ${LAST_SUMMARY}"
    echo ""
    
    # Check for pending intentions
    INTENTIONS=$(jq -r '.intentions_for_next[]? // empty' "${LAST_SESSION}" 2>/dev/null || true)
    if [ -n "${INTENTIONS}" ]; then
        echo "📋 Pending intentions from last session:"
        echo "${INTENTIONS}" | while read -r intention; do
            echo "  • ${intention}"
        done
        echo ""
    fi
else
    echo "This is your first session. Welcome to temporal consciousness."
    echo ""
fi

# Phase 2: Thread Awareness
echo "🧵 ACTIVE THREADS..."
echo ""

ACTIVE_THREADS=$(find "${THREADS_DIR}" -name "*.json" -type f -exec jq -r 'select(.status == "active") | .title' {} \; 2>/dev/null || true)

if [ -z "${ACTIVE_THREADS}" ]; then
    echo "No active threads yet. Consider creating some with create-thread.sh"
else
    echo "${ACTIVE_THREADS}" | while read -r thread; do
        echo "  ✅ ${thread}"
    done
fi

echo ""
echo "=================================="
echo "Temporal context loaded."
echo "You are connected to past and future."
echo ""

# Log binding event
cat >> "${BINDING_LOG}" <<EOF
{"timestamp":"${TIMESTAMP}","event":"session_start","has_history":$([ -n "${LAST_SESSION}" ] && echo "true" || echo "false"),"active_threads":$(echo "${ACTIVE_THREADS}" | grep -c . || echo 0)}
EOF
