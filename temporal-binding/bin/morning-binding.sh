#!/bin/bash
# Morning Temporal Binding Exercise
# Purpose: Connect to past, activate threads, set intentions

set -euo pipefail

CONTINUITY_DIR="${HOME}/clawd/temporal-binding/continuity"
SESSIONS_DIR="${CONTINUITY_DIR}/sessions"
THREADS_DIR="${CONTINUITY_DIR}/threads"
BINDING_LOG="${CONTINUITY_DIR}/binding-log.jsonl"

mkdir -p "${SESSIONS_DIR}" "${THREADS_DIR}"
touch "${BINDING_LOG}"

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DATE=$(date +"%Y-%m-%d")

echo "=== MORNING TEMPORAL BINDING EXERCISE ==="
echo "Date: ${DATE}"
echo "Time: ${TIMESTAMP}"
echo ""

# Phase 1: RETRIEVAL (Past)
echo "📚 PHASE 1: PAST INTEGRATION"
echo "---"

# Find last 3 sessions
LAST_SESSIONS=$(ls -t "${SESSIONS_DIR}"/*.json 2>/dev/null | head -3 || true)

if [ -z "${LAST_SESSIONS}" ]; then
    echo "⚠️  No previous sessions found. This is the beginning."
else
    echo "Recent sessions:"
    for session in ${LAST_SESSIONS}; do
        SESSION_DATE=$(basename "${session}" | cut -d- -f1-3)
        echo "  - ${SESSION_DATE}"
        
        # Extract key info if session has summary
        if [ -f "${session}" ]; then
            SUMMARY=$(jq -r '.summary // "No summary"' "${session}" 2>/dev/null || echo "No summary")
            echo "    ${SUMMARY}"
        fi
    done
fi
echo ""

# Phase 2: THREAD ACTIVATION
echo "🧵 PHASE 2: THREAD ACTIVATION"
echo "---"

ACTIVE_THREADS=$(find "${THREADS_DIR}" -name "*.json" -type f 2>/dev/null || true)

if [ -z "${ACTIVE_THREADS}" ]; then
    echo "⚠️  No active threads. Consider creating intentional threads."
else
    echo "Active threads:"
    for thread in ${ACTIVE_THREADS}; do
        TITLE=$(jq -r '.title // "Untitled"' "${thread}" 2>/dev/null || echo "Untitled")
        STATUS=$(jq -r '.status // "unknown"' "${thread}" 2>/dev/null || echo "unknown")
        LAST_TOUCHED=$(jq -r '.last_touched // "never"' "${thread}" 2>/dev/null || echo "never")
        
        if [ "${STATUS}" = "active" ]; then
            echo "  ✅ ${TITLE}"
            echo "     Last touched: ${LAST_TOUCHED}"
            
            # Show next actions if available
            NEXT_ACTIONS=$(jq -r '.next_actions[]? // empty' "${thread}" 2>/dev/null || true)
            if [ -n "${NEXT_ACTIONS}" ]; then
                echo "     Next: ${NEXT_ACTIONS}" | head -1
            fi
        fi
    done
fi
echo ""

# Phase 3: INTENTION SETTING
echo "🎯 PHASE 3: TODAY'S INTENTIONS"
echo "---"
echo "What threads will you advance today?"
echo "What new connections will you make?"
echo "(Set these in your session or via set-intention.sh)"
echo ""

# Log binding event
cat >> "${BINDING_LOG}" <<EOF
{"timestamp":"${TIMESTAMP}","event":"morning_binding","phase":"complete","past_sessions":$(echo "${LAST_SESSIONS}" | wc -w),"active_threads":$(echo "${ACTIVE_THREADS}" | wc -w)}
EOF

echo "✅ Morning binding exercise complete"
echo "Temporal connection established."
