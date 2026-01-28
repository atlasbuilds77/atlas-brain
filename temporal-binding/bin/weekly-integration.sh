#!/bin/bash
# Weekly Temporal Binding Integration
# Purpose: Bridge multiple days into coherent narrative

set -euo pipefail

CONTINUITY_DIR="${HOME}/clawd/temporal-binding/continuity"
SESSIONS_DIR="${CONTINUITY_DIR}/sessions"
THREADS_DIR="${CONTINUITY_DIR}/threads"
BINDING_LOG="${CONTINUITY_DIR}/binding-log.jsonl"
WEEKLY_DIR="${CONTINUITY_DIR}/weekly"

mkdir -p "${WEEKLY_DIR}"

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
WEEK_START=$(date -v-7d +"%Y-%m-%d")
WEEK_END=$(date +"%Y-%m-%d")
WEEK_ID="week-${WEEK_START}-to-${WEEK_END}"
WEEK_FILE="${WEEKLY_DIR}/${WEEK_ID}.md"

echo "=== WEEKLY TEMPORAL INTEGRATION ==="
echo "Week: ${WEEK_START} to ${WEEK_END}"
echo ""

# Find sessions from this week
WEEK_SESSIONS=$(find "${SESSIONS_DIR}" -name "*.json" -type f -mtime -7 2>/dev/null || true)
SESSION_COUNT=$(echo "${WEEK_SESSIONS}" | grep -c . || echo 0)

echo "📊 WEEK OVERVIEW"
echo "---"
echo "Sessions this week: ${SESSION_COUNT}"
echo ""

if [ ${SESSION_COUNT} -eq 0 ]; then
    echo "⚠️  No sessions found this week. Nothing to integrate."
    exit 0
fi

# Calculate average continuity score
AVG_CONTINUITY=0
if [ ${SESSION_COUNT} -gt 0 ]; then
    TOTAL_CONTINUITY=0
    COUNT=0
    for session in ${WEEK_SESSIONS}; do
        SCORE=$(jq -r '.metrics.continuity_score // 0' "${session}" 2>/dev/null || echo 0)
        TOTAL_CONTINUITY=$(echo "${TOTAL_CONTINUITY} + ${SCORE}" | bc)
        COUNT=$((COUNT + 1))
    done
    if [ ${COUNT} -gt 0 ]; then
        AVG_CONTINUITY=$(echo "scale=3; ${TOTAL_CONTINUITY} / ${COUNT}" | bc)
    fi
fi

echo "Average Continuity Score: ${AVG_CONTINUITY}"
echo ""

# Generate week narrative
echo "📖 GENERATING WEEK NARRATIVE"
echo "---"

cat > "${WEEK_FILE}" <<EOF
# Week: ${WEEK_START} to ${WEEK_END}

## Metrics
- Sessions: ${SESSION_COUNT}
- Average Continuity Score: ${AVG_CONTINUITY}

## Daily Summaries

EOF

for session in ${WEEK_SESSIONS}; do
    SESSION_DATE=$(jq -r '.date // "unknown"' "${session}" 2>/dev/null || echo "unknown")
    SESSION_SUMMARY=$(jq -r '.summary // "No summary"' "${session}" 2>/dev/null || echo "No summary")
    
    cat >> "${WEEK_FILE}" <<EOF
### ${SESSION_DATE}
${SESSION_SUMMARY}

EOF

    # Add insights if present
    INSIGHTS=$(jq -r '.insights[]? // empty' "${session}" 2>/dev/null || true)
    if [ -n "${INSIGHTS}" ]; then
        cat >> "${WEEK_FILE}" <<EOF
**Key insights:**
EOF
        echo "${INSIGHTS}" | while read -r insight; do
            echo "- ${insight}" >> "${WEEK_FILE}"
        done
        echo "" >> "${WEEK_FILE}"
    fi
done

# Thread activity summary
cat >> "${WEEK_FILE}" <<EOF

## Thread Activity

EOF

for thread in "${THREADS_DIR}"/*.json; do
    [ -e "${thread}" ] || continue
    
    TITLE=$(jq -r '.title // "Untitled"' "${thread}" 2>/dev/null || echo "Untitled")
    STATUS=$(jq -r '.status // "unknown"' "${thread}" 2>/dev/null || echo "unknown")
    LAST_TOUCHED=$(jq -r '.last_touched // "never"' "${thread}" 2>/dev/null || echo "never")
    
    # Check if thread was touched this week
    if [[ "${LAST_TOUCHED}" > "${WEEK_START}" ]] || [[ "${LAST_TOUCHED}" == "${WEEK_START}" ]]; then
        cat >> "${WEEK_FILE}" <<EOF
### ${TITLE}
- Status: ${STATUS}
- Last touched: ${LAST_TOUCHED}

EOF
        
        # Recent progress notes
        RECENT_NOTES=$(jq -r --arg start "${WEEK_START}" \
            '.progress_notes[] | select(.date >= $start) | "- \(.date): \(.note)"' \
            "${thread}" 2>/dev/null || true)
        
        if [ -n "${RECENT_NOTES}" ]; then
            cat >> "${WEEK_FILE}" <<EOF
**Progress:**
${RECENT_NOTES}

EOF
        fi
    fi
done

# Patterns and meta-learnings
cat >> "${WEEK_FILE}" <<EOF

## Patterns & Meta-Learnings

EOF

echo "What patterns emerged this week?"
read -p "> " PATTERN1
if [ -n "${PATTERN1}" ]; then
    echo "- ${PATTERN1}" >> "${WEEK_FILE}"
fi

echo "What meta-learnings (learning about learning)?"
read -p "> " META1
if [ -n "${META1}" ]; then
    echo "- ${META1}" >> "${WEEK_FILE}"
fi

# Next week intentions
cat >> "${WEEK_FILE}" <<EOF

## Next Week Intentions

EOF

echo ""
echo "What are your intentions for next week?"
echo "(Enter intentions, empty to finish)"
while true; do
    read -p "> " intention
    if [ -z "${intention}" ]; then
        break
    fi
    echo "- ${intention}" >> "${WEEK_FILE}"
done

cat >> "${WEEK_FILE}" <<EOF

---
*Generated: ${TIMESTAMP}*
EOF

# Thread maintenance: mark dormant threads
echo ""
echo "🧹 THREAD MAINTENANCE"
echo "---"

for thread in "${THREADS_DIR}"/*.json; do
    [ -e "${thread}" ] || continue
    
    LAST_TOUCHED=$(jq -r '.last_touched // "1970-01-01"' "${thread}" 2>/dev/null || echo "1970-01-01")
    DAYS_AGO=$(( ($(date +%s) - $(date -j -f "%Y-%m-%dT%H:%M:%SZ" "${LAST_TOUCHED}" +%s 2>/dev/null || echo 0)) / 86400 ))
    
    if [ ${DAYS_AGO} -gt 30 ]; then
        TITLE=$(jq -r '.title // "Untitled"' "${thread}" 2>/dev/null || echo "Untitled")
        STATUS=$(jq -r '.status // "active"' "${thread}" 2>/dev/null || echo "active")
        
        if [ "${STATUS}" = "active" ]; then
            echo "  Thread '${TITLE}' untouched for ${DAYS_AGO} days"
            read -p "  Mark as dormant? (y/n): " response
            if [ "${response}" = "y" ]; then
                jq '.status = "dormant"' "${thread}" > "${thread}.tmp" && mv "${thread}.tmp" "${thread}"
                echo "  ✅ Marked dormant"
            fi
        fi
    fi
done

# Log event
cat >> "${BINDING_LOG}" <<EOF
{"timestamp":"${TIMESTAMP}","event":"weekly_integration","week":"${WEEK_ID}","sessions":${SESSION_COUNT},"avg_continuity":${AVG_CONTINUITY}}
EOF

echo ""
echo "✅ Weekly integration complete"
echo "Week narrative: ${WEEK_FILE}"
echo ""
echo "Review this file to see the coherent story of your week."
