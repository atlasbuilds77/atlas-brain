#!/bin/bash
# Quick temporal binding status check
# Use in session startup or heartbeat

set -euo pipefail

CONTINUITY_DIR="${HOME}/clawd/temporal-binding/continuity"
METRICS="${CONTINUITY_DIR}/metrics.json"
THREADS_DIR="${CONTINUITY_DIR}/threads"

# Check if system is initialized
if [ ! -d "${CONTINUITY_DIR}" ]; then
    echo "⚠️  Temporal binding not initialized. Run: setup-automation.sh"
    exit 1
fi

# Get key metrics
if [ -f "${METRICS}" ]; then
    AVG_CONTINUITY=$(jq -r '.avg_continuity // 0' "${METRICS}" 2>/dev/null || echo 0)
    TOTAL_SESSIONS=$(jq -r '.total_sessions // 0' "${METRICS}" 2>/dev/null || echo 0)
else
    AVG_CONTINUITY=0
    TOTAL_SESSIONS=0
fi

ACTIVE_THREADS=$(find "${THREADS_DIR}" -name "*.json" -exec jq -r 'select(.status == "active") | .id' {} \; 2>/dev/null | wc -l | tr -d ' ')

# Status emoji
STATUS_EMOJI="⚠️"
if (( $(echo "${AVG_CONTINUITY} >= 0.75" | bc -l 2>/dev/null || echo 0) )); then
    STATUS_EMOJI="✅"
elif (( $(echo "${AVG_CONTINUITY} >= 0.5" | bc -l 2>/dev/null || echo 0) )); then
    STATUS_EMOJI="⚡"
fi

# Compact output
echo "🧠 Temporal Binding: ${STATUS_EMOJI}"
echo "   Continuity: ${AVG_CONTINUITY} | Sessions: ${TOTAL_SESSIONS} | Active threads: ${ACTIVE_THREADS}"

# Warning if no recent activity
if [ ${TOTAL_SESSIONS} -eq 0 ]; then
    echo "   💡 Tip: Run evening-retrospective.sh to record your first session"
elif [ ${ACTIVE_THREADS} -eq 0 ]; then
    echo "   💡 Tip: Create threads with create-thread.sh for stronger binding"
fi
