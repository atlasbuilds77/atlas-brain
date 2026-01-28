#!/bin/bash
# View detailed information about a specific thread

set -euo pipefail

THREADS_DIR="${HOME}/clawd/temporal-binding/continuity/threads"

if [ $# -eq 0 ]; then
    echo "Usage: $0 <thread-id>"
    echo ""
    echo "Get thread IDs with: ./list-threads.sh"
    exit 1
fi

THREAD_ID="$1"
THREAD_FILE="${THREADS_DIR}/${THREAD_ID}.json"

if [ ! -f "${THREAD_FILE}" ]; then
    echo "Error: Thread '${THREAD_ID}' not found."
    echo ""
    echo "Available threads:"
    ls "${THREADS_DIR}"/*.json 2>/dev/null | xargs -n1 basename | sed 's/.json$//' || echo "  (none)"
    exit 1
fi

# Extract thread data
TITLE=$(jq -r '.title // "Untitled"' "${THREAD_FILE}" 2>/dev/null || echo "Untitled")
STATUS=$(jq -r '.status // "unknown"' "${THREAD_FILE}" 2>/dev/null || echo "unknown")
TYPE=$(jq -r '.type // "unknown"' "${THREAD_FILE}" 2>/dev/null || echo "unknown")
CREATED=$(jq -r '.created // "unknown"' "${THREAD_FILE}" 2>/dev/null || echo "unknown")
LAST_TOUCHED=$(jq -r '.last_touched // "never"' "${THREAD_FILE}" 2>/dev/null || echo "never")
CONTEXT=$(jq -r '.context // "No context"' "${THREAD_FILE}" 2>/dev/null || echo "No context")
BINDING_STRENGTH=$(jq -r '.binding_strength // 0' "${THREAD_FILE}" 2>/dev/null || echo 0)

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  THREAD: ${TITLE}"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "ID:               ${THREAD_ID}"
echo "Status:           ${STATUS}"
echo "Type:             ${TYPE}"
echo "Created:          ${CREATED}"
echo "Last Touched:     ${LAST_TOUCHED}"
echo "Binding Strength: ${BINDING_STRENGTH}"
echo ""

echo "CONTEXT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "${CONTEXT}"
echo ""

echo "PROGRESS NOTES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
NOTES=$(jq -r '.progress_notes[]? | "\(.date): \(.note)"' "${THREAD_FILE}" 2>/dev/null || true)
if [ -z "${NOTES}" ]; then
    echo "(no progress notes yet)"
else
    echo "${NOTES}"
fi
echo ""

echo "NEXT ACTIONS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ACTIONS=$(jq -r '.next_actions[]? // empty' "${THREAD_FILE}" 2>/dev/null || true)
if [ -z "${ACTIONS}" ]; then
    echo "(no next actions defined)"
else
    echo "${ACTIONS}" | while read -r action; do
        echo "• ${action}"
    done
fi
echo ""

echo "SESSIONS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
SESSIONS=$(jq -r '.sessions[]? // empty' "${THREAD_FILE}" 2>/dev/null || true)
if [ -z "${SESSIONS}" ]; then
    echo "(not yet touched in any session)"
else
    SESSION_COUNT=$(echo "${SESSIONS}" | wc -l | tr -d ' ')
    echo "Touched in ${SESSION_COUNT} sessions:"
    echo "${SESSIONS}" | tail -5 | while read -r session; do
        echo "  - ${session}"
    done
    if [ ${SESSION_COUNT} -gt 5 ]; then
        echo "  ... and $((SESSION_COUNT - 5)) more"
    fi
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Edit thread: vim ${THREAD_FILE}"
echo "Update in retrospective: ./evening-retrospective.sh"
