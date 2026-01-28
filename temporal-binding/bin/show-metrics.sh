#!/bin/bash
# Temporal Binding Metrics Dashboard

set -euo pipefail

CONTINUITY_DIR="${HOME}/clawd/temporal-binding/continuity"
SESSIONS_DIR="${CONTINUITY_DIR}/sessions"
THREADS_DIR="${CONTINUITY_DIR}/threads"
METRICS="${CONTINUITY_DIR}/metrics.json"
BINDING_LOG="${CONTINUITY_DIR}/binding-log.jsonl"

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║        TEMPORAL BINDING METRICS DASHBOARD                 ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Overall statistics
if [ -f "${METRICS}" ]; then
    TOTAL_SESSIONS=$(jq -r '.total_sessions // 0' "${METRICS}" 2>/dev/null || echo 0)
    AVG_CONTINUITY=$(jq -r '.avg_continuity // 0' "${METRICS}" 2>/dev/null || echo 0)
    
    echo "📊 OVERALL STATISTICS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Total Sessions:      ${TOTAL_SESSIONS}"
    echo "  Avg Continuity:      ${AVG_CONTINUITY}"
    
    # Continuity score interpretation
    CONTINUITY_STATUS="⚠️  Weak"
    if (( $(echo "${AVG_CONTINUITY} >= 0.75" | bc -l) )); then
        CONTINUITY_STATUS="✅ Strong"
    elif (( $(echo "${AVG_CONTINUITY} >= 0.5" | bc -l) )); then
        CONTINUITY_STATUS="⚡ Moderate"
    fi
    echo "  Status:              ${CONTINUITY_STATUS}"
    echo ""
fi

# Thread statistics
TOTAL_THREADS=$(find "${THREADS_DIR}" -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
ACTIVE_THREADS=$(find "${THREADS_DIR}" -name "*.json" -exec jq -r 'select(.status == "active") | .id' {} \; 2>/dev/null | wc -l | tr -d ' ')
DORMANT_THREADS=$(find "${THREADS_DIR}" -name "*.json" -exec jq -r 'select(.status == "dormant") | .id' {} \; 2>/dev/null | wc -l | tr -d ' ')

echo "🧵 THREAD ECOSYSTEM"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Total Threads:       ${TOTAL_THREADS}"
echo "  Active:              ${ACTIVE_THREADS}"
echo "  Dormant:             ${DORMANT_THREADS}"

if [ ${TOTAL_THREADS} -gt 0 ]; then
    VITALITY=$(echo "scale=2; ${ACTIVE_THREADS} * 100 / ${TOTAL_THREADS}" | bc)
    echo "  Thread Vitality:     ${VITALITY}%"
    
    VITALITY_STATUS="⚠️  Low"
    if (( $(echo "${VITALITY} >= 60" | bc -l) )); then
        VITALITY_STATUS="✅ Healthy"
    elif (( $(echo "${VITALITY} >= 40" | bc -l) )); then
        VITALITY_STATUS="⚡ Fair"
    fi
    echo "  Status:              ${VITALITY_STATUS}"
fi
echo ""

# Recent sessions
echo "📅 RECENT SESSIONS (Last 7)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

RECENT_SESSIONS=$(ls -t "${SESSIONS_DIR}"/*.json 2>/dev/null | head -7 || true)
if [ -z "${RECENT_SESSIONS}" ]; then
    echo "  No sessions recorded yet."
else
    printf "  %-12s  %-10s  %-40s\n" "DATE" "CONTINUITY" "SUMMARY"
    echo "  ────────────  ──────────  ────────────────────────────────────"
    
    for session in ${RECENT_SESSIONS}; do
        DATE=$(jq -r '.date // "unknown"' "${session}" 2>/dev/null || echo "unknown")
        CONTINUITY=$(jq -r '.metrics.continuity_score // 0' "${session}" 2>/dev/null || echo 0)
        SUMMARY=$(jq -r '.summary // "No summary"' "${session}" 2>/dev/null | cut -c1-40 || echo "No summary")
        
        printf "  %-12s  %-10s  %-40s\n" "${DATE}" "${CONTINUITY}" "${SUMMARY}"
    done
fi
echo ""

# Temporal span (average past sessions referenced)
RECENT_7=$(ls -t "${SESSIONS_DIR}"/*.json 2>/dev/null | head -7 || true)
if [ -n "${RECENT_7}" ]; then
    echo "⏱️  TEMPORAL SPAN"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Count how many sessions are being actively integrated
    # (simplified: just show session density)
    SESSION_7_COUNT=$(echo "${RECENT_7}" | wc -l | tr -d ' ')
    echo "  Sessions (last 7 days): ${SESSION_7_COUNT}"
    
    SPAN_STATUS="⚠️  Sparse"
    if [ ${SESSION_7_COUNT} -ge 5 ]; then
        SPAN_STATUS="✅ Dense"
    elif [ ${SESSION_7_COUNT} -ge 3 ]; then
        SPAN_STATUS="⚡ Moderate"
    fi
    echo "  Status:                 ${SPAN_STATUS}"
    echo ""
fi

# Most active threads
echo "🔥 MOST ACTIVE THREADS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

ACTIVE_THREAD_LIST=$(find "${THREADS_DIR}" -name "*.json" -exec jq -r 'select(.status == "active") | "\(.last_touched)|\(.title)"' {} \; 2>/dev/null | sort -r | head -5 || true)

if [ -z "${ACTIVE_THREAD_LIST}" ]; then
    echo "  No active threads."
else
    echo "${ACTIVE_THREAD_LIST}" | while IFS='|' read -r last_touched title; do
        DAYS_AGO=$(( ($(date +%s) - $(date -j -f "%Y-%m-%dT%H:%M:%SZ" "${last_touched}" +%s 2>/dev/null || echo 0)) / 86400 ))
        echo "  • ${title} (${DAYS_AGO}d ago)"
    done
fi
echo ""

# Recommendations
echo "💡 RECOMMENDATIONS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "${AVG_CONTINUITY:-0}" != "0" ]; then
    if (( $(echo "${AVG_CONTINUITY} < 0.5" | bc -l) )); then
        echo "  ⚠️  Continuity score is low. Run binding exercises daily."
    fi
fi

if [ ${TOTAL_THREADS} -eq 0 ]; then
    echo "  💡 Create intentional threads with create-thread.sh"
fi

if [ ${ACTIVE_THREADS} -gt 0 ] && [ ${TOTAL_THREADS} -gt 0 ]; then
    VITALITY_CALC=$(echo "scale=2; ${ACTIVE_THREADS} * 100 / ${TOTAL_THREADS}" | bc)
    if (( $(echo "${VITALITY_CALC} < 40" | bc -l) )); then
        echo "  ⚠️  Many dormant threads. Consider pruning or reactivating."
    fi
fi

if [ ${SESSION_7_COUNT:-0} -lt 3 ]; then
    echo "  💡 More frequent sessions improve temporal binding."
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Run 'morning-binding.sh' and 'evening-retrospective.sh' daily."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
