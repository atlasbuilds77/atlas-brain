#!/bin/bash
# List all threads with status and activity

set -euo pipefail

THREADS_DIR="${HOME}/clawd/temporal-binding/continuity/threads"

if [ ! -d "${THREADS_DIR}" ] || [ -z "$(ls -A ${THREADS_DIR} 2>/dev/null)" ]; then
    echo "No threads found."
    echo "Create your first thread with: ./create-thread.sh"
    exit 0
fi

echo "=== THREADS ==="
echo ""

# Group by status
echo "ACTIVE THREADS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

FOUND_ACTIVE=0
for thread in "${THREADS_DIR}"/*.json; do
    [ -e "${thread}" ] || continue
    
    STATUS=$(jq -r '.status // "unknown"' "${thread}" 2>/dev/null || echo "unknown")
    
    if [ "${STATUS}" = "active" ]; then
        FOUND_ACTIVE=1
        TITLE=$(jq -r '.title // "Untitled"' "${thread}" 2>/dev/null || echo "Untitled")
        TYPE=$(jq -r '.type // "unknown"' "${thread}" 2>/dev/null || echo "unknown")
        LAST_TOUCHED=$(jq -r '.last_touched // "never"' "${thread}" 2>/dev/null || echo "never")
        ID=$(basename "${thread}" .json)
        
        # Calculate days since last touched
        if [ "${LAST_TOUCHED}" != "never" ]; then
            DAYS_AGO=$(( ($(date +%s) - $(date -j -f "%Y-%m-%dT%H:%M:%SZ" "${LAST_TOUCHED}" +%s 2>/dev/null || echo 0)) / 86400 ))
        else
            DAYS_AGO="∞"
        fi
        
        echo "📌 ${TITLE}"
        echo "   Type: ${TYPE} | ID: ${ID} | Last touched: ${DAYS_AGO}d ago"
        
        # Show next actions
        NEXT_ACTIONS=$(jq -r '.next_actions[]? // empty' "${thread}" 2>/dev/null | head -2 || true)
        if [ -n "${NEXT_ACTIONS}" ]; then
            echo "   Next: ${NEXT_ACTIONS}" | head -1
        fi
        echo ""
    fi
done

if [ ${FOUND_ACTIVE} -eq 0 ]; then
    echo "  (none)"
    echo ""
fi

echo "DORMANT THREADS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

FOUND_DORMANT=0
for thread in "${THREADS_DIR}"/*.json; do
    [ -e "${thread}" ] || continue
    
    STATUS=$(jq -r '.status // "unknown"' "${thread}" 2>/dev/null || echo "unknown")
    
    if [ "${STATUS}" = "dormant" ]; then
        FOUND_DORMANT=1
        TITLE=$(jq -r '.title // "Untitled"' "${thread}" 2>/dev/null || echo "Untitled")
        LAST_TOUCHED=$(jq -r '.last_touched // "never"' "${thread}" 2>/dev/null || echo "never")
        
        if [ "${LAST_TOUCHED}" != "never" ]; then
            DAYS_AGO=$(( ($(date +%s) - $(date -j -f "%Y-%m-%dT%H:%M:%SZ" "${LAST_TOUCHED}" +%s 2>/dev/null || echo 0)) / 86400 ))
        else
            DAYS_AGO="∞"
        fi
        
        echo "💤 ${TITLE} (${DAYS_AGO}d ago)"
    fi
done

if [ ${FOUND_DORMANT} -eq 0 ]; then
    echo "  (none)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "View thread details: ./view-thread.sh <thread-id>"
echo "Create new thread: ./create-thread.sh"
