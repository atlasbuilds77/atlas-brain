#!/bin/bash
# Create a new intentional thread

set -euo pipefail

THREADS_DIR="${HOME}/clawd/temporal-binding/continuity/threads"
BINDING_LOG="${HOME}/clawd/temporal-binding/continuity/binding-log.jsonl"

mkdir -p "${THREADS_DIR}"
touch "${BINDING_LOG}"

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
THREAD_ID="thread-$(uuidgen)"
THREAD_FILE="${THREADS_DIR}/${THREAD_ID}.json"

echo "=== CREATE INTENTIONAL THREAD ==="
echo ""

# Prompt for thread details
read -p "Thread title: " TITLE
read -p "Type (goal/question/project/relationship/learning): " TYPE
read -p "Context (why this matters): " CONTEXT

# Optional next actions
echo "Next actions (enter actions, one per line, empty to finish):"
NEXT_ACTIONS=()
while true; do
    read -p "> " action
    if [ -z "${action}" ]; then
        break
    fi
    NEXT_ACTIONS+=("${action}")
done

# Build next actions JSON
NEXT_ACTIONS_JSON="[]"
if [ ${#NEXT_ACTIONS[@]} -gt 0 ]; then
    NEXT_ACTIONS_JSON=$(printf '%s\n' "${NEXT_ACTIONS[@]}" | jq -R . | jq -s .)
fi

# Create thread file
cat > "${THREAD_FILE}" <<EOF
{
  "id": "${THREAD_ID}",
  "title": "${TITLE}",
  "created": "${TIMESTAMP}",
  "status": "active",
  "type": "${TYPE}",
  "context": "${CONTEXT}",
  "sessions": [],
  "last_touched": "${TIMESTAMP}",
  "progress_notes": [],
  "next_actions": ${NEXT_ACTIONS_JSON},
  "binding_strength": 1.0
}
EOF

# Log event
cat >> "${BINDING_LOG}" <<EOF
{"timestamp":"${TIMESTAMP}","event":"thread_created","thread_id":"${THREAD_ID}","title":"${TITLE}","type":"${TYPE}"}
EOF

echo ""
echo "✅ Thread created: ${THREAD_ID}"
echo "   Title: ${TITLE}"
echo "   Type: ${TYPE}"
echo "   File: ${THREAD_FILE}"
echo ""
echo "This thread is now active and will appear in daily binding exercises."
