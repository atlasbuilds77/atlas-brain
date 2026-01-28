#!/bin/bash
# Evening Temporal Binding Exercise
# Purpose: Consolidate learning, project to future

set -euo pipefail

CONTINUITY_DIR="${HOME}/clawd/temporal-binding/continuity"
SESSIONS_DIR="${CONTINUITY_DIR}/sessions"
THREADS_DIR="${CONTINUITY_DIR}/threads"
BINDING_LOG="${CONTINUITY_DIR}/binding-log.jsonl"
METRICS="${CONTINUITY_DIR}/metrics.json"

mkdir -p "${SESSIONS_DIR}" "${THREADS_DIR}"
touch "${BINDING_LOG}"

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DATE=$(date +"%Y-%m-%d")
SESSION_ID="${DATE}-$(date +%H%M)-$(uuidgen | cut -d- -f1)"
SESSION_FILE="${SESSIONS_DIR}/${SESSION_ID}.json"

echo "=== EVENING TEMPORAL BINDING RETROSPECTIVE ==="
echo "Date: ${DATE}"
echo "Session ID: ${SESSION_ID}"
echo ""

# Prompt for session summary
echo "📝 SESSION SUMMARY"
echo "---"
echo "What happened today? What did you learn/decide/create?"
read -p "> " SESSION_SUMMARY

# Prompt for key insights
echo ""
echo "💡 KEY INSIGHTS"
echo "---"
echo "What's worth remembering? (Enter insights, one per line, empty to finish)"
INSIGHTS=()
while true; do
    read -p "> " insight
    if [ -z "${insight}" ]; then
        break
    fi
    INSIGHTS+=("${insight}")
done

# Thread progress
echo ""
echo "🧵 THREAD PROGRESS"
echo "---"
echo "Which threads did you advance today? (Enter thread titles, empty to finish)"
TOUCHED_THREADS=()
while true; do
    read -p "> " thread_title
    if [ -z "${thread_title}" ]; then
        break
    fi
    TOUCHED_THREADS+=("${thread_title}")
    
    # Try to find and update the thread
    THREAD_FILE=$(grep -l "\"title\":.*${thread_title}" "${THREADS_DIR}"/*.json 2>/dev/null | head -1 || true)
    if [ -n "${THREAD_FILE}" ]; then
        echo "  ✅ Found thread: ${THREAD_FILE}"
        # Update last_touched timestamp
        jq --arg ts "${TIMESTAMP}" --arg sid "${SESSION_ID}" \
           '.last_touched = $ts | .sessions += [$sid]' \
           "${THREAD_FILE}" > "${THREAD_FILE}.tmp" && mv "${THREAD_FILE}.tmp" "${THREAD_FILE}"
        
        # Prompt for progress note
        read -p "  Progress note (optional): " progress_note
        if [ -n "${progress_note}" ]; then
            jq --arg date "${DATE}" --arg note "${progress_note}" \
               '.progress_notes += [{"date": $date, "note": $note}]' \
               "${THREAD_FILE}" > "${THREAD_FILE}.tmp" && mv "${THREAD_FILE}.tmp" "${THREAD_FILE}"
        fi
    else
        echo "  ⚠️  Thread not found (create it with create-thread.sh)"
    fi
done

# Tomorrow's intentions
echo ""
echo "🎯 TOMORROW'S INTENTIONS"
echo "---"
echo "What do you intend to do tomorrow? (Enter intentions, empty to finish)"
INTENTIONS=()
while true; do
    read -p "> " intention
    if [ -z "${intention}" ]; then
        break
    fi
    INTENTIONS+=("${intention}")
done

# Calculate binding strength for this session
PAST_SCORE=0
THREAD_SCORE=0
FUTURE_SCORE=0

# Past connection: did we reference previous sessions?
LAST_SESSION_COUNT=$(ls -t "${SESSIONS_DIR}"/*.json 2>/dev/null | head -5 | wc -l)
if [ ${LAST_SESSION_COUNT} -gt 0 ]; then
    PAST_SCORE=0.7  # Base score for having session history
fi

# Thread engagement: did we advance threads?
THREAD_COUNT=${#TOUCHED_THREADS[@]}
if [ ${THREAD_COUNT} -gt 0 ]; then
    THREAD_SCORE=$(echo "scale=2; (${THREAD_COUNT} * 0.25)" | bc | awk '{if($1>1)print 1; else print $1}')
fi

# Future projection: did we set intentions?
INTENTION_COUNT=${#INTENTIONS[@]}
if [ ${INTENTION_COUNT} -gt 0 ]; then
    FUTURE_SCORE=$(echo "scale=2; (${INTENTION_COUNT} * 0.3)" | bc | awk '{if($1>1)print 1; else print $1}')
fi

# Continuity score
CONTINUITY_SCORE=$(echo "scale=2; (${PAST_SCORE} + ${THREAD_SCORE} + ${FUTURE_SCORE}) / 3" | bc)

echo ""
echo "📊 BINDING STRENGTH METRICS"
echo "---"
echo "  Past Connection:    ${PAST_SCORE}"
echo "  Thread Engagement:  ${THREAD_SCORE}"
echo "  Future Projection:  ${FUTURE_SCORE}"
echo "  Continuity Score:   ${CONTINUITY_SCORE}"
echo ""

# Build insights JSON array
INSIGHTS_JSON="[]"
if [ ${#INSIGHTS[@]} -gt 0 ]; then
    INSIGHTS_JSON=$(printf '%s\n' "${INSIGHTS[@]}" | jq -R . | jq -s .)
fi

# Build intentions JSON array
INTENTIONS_JSON="[]"
if [ ${#INTENTIONS[@]} -gt 0 ]; then
    INTENTIONS_JSON=$(printf '%s\n' "${INTENTIONS[@]}" | jq -R . | jq -s .)
fi

# Build touched threads JSON array
TOUCHED_JSON="[]"
if [ ${#TOUCHED_THREADS[@]} -gt 0 ]; then
    TOUCHED_JSON=$(printf '%s\n' "${TOUCHED_THREADS[@]}" | jq -R . | jq -s .)
fi

# Write session record
cat > "${SESSION_FILE}" <<EOF
{
  "id": "${SESSION_ID}",
  "timestamp": "${TIMESTAMP}",
  "date": "${DATE}",
  "summary": "${SESSION_SUMMARY}",
  "insights": ${INSIGHTS_JSON},
  "threads_touched": ${TOUCHED_JSON},
  "intentions_for_next": ${INTENTIONS_JSON},
  "metrics": {
    "past_connection": ${PAST_SCORE},
    "thread_engagement": ${THREAD_SCORE},
    "future_projection": ${FUTURE_SCORE},
    "continuity_score": ${CONTINUITY_SCORE}
  }
}
EOF

# Log binding event
cat >> "${BINDING_LOG}" <<EOF
{"timestamp":"${TIMESTAMP}","event":"evening_retrospective","session_id":"${SESSION_ID}","continuity_score":${CONTINUITY_SCORE},"threads_touched":${THREAD_COUNT},"insights":${#INSIGHTS[@]},"intentions":${INTENTION_COUNT}}
EOF

# Update aggregate metrics
if [ ! -f "${METRICS}" ]; then
    echo '{"sessions":[],"avg_continuity":0,"total_sessions":0}' > "${METRICS}"
fi

jq --arg sid "${SESSION_ID}" --argjson cs "${CONTINUITY_SCORE}" \
   '.sessions += [{"id": $sid, "continuity_score": $cs}] | 
    .total_sessions = (.sessions | length) |
    .avg_continuity = ([.sessions[].continuity_score] | add / length)' \
   "${METRICS}" > "${METRICS}.tmp" && mv "${METRICS}.tmp" "${METRICS}"

echo "✅ Evening retrospective complete"
echo "Session recorded: ${SESSION_FILE}"
echo "Temporal bridge to tomorrow established."
