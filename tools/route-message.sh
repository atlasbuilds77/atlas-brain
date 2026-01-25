#!/bin/bash
# route-message.sh - Determines correct routing target for incoming messages

SENDER="$1"
MESSAGE_TEXT="$2"

# Configuration
GROUP_CHAT_ID=3
GROUP_PARTICIPANTS=("14245157194" "16195779919" "16193845759")

# Check if sender is a group participant
is_participant=false
for participant in "${GROUP_PARTICIPANTS[@]}"; do
    if [[ "$SENDER" == *"$participant"* ]]; then
        is_participant=true
        break
    fi
done

# If not a participant, route directly
if [ "$is_participant" = false ]; then
    echo "direct:$SENDER"
    exit 0
fi

# Check if message starts with [DM] or [Direct] override
if [[ "$MESSAGE_TEXT" =~ ^\[DM\] ]] || [[ "$MESSAGE_TEXT" =~ ^\[Direct\] ]]; then
    echo "direct:$SENDER"
    exit 0
fi

# Query last 20 messages from group chat
GROUP_RECENT=$(imsg history --chat-id "$GROUP_CHAT_ID" --limit 20 --json 2>/dev/null | jq -r '.text' 2>/dev/null)

# Check if this exact message appears in recent group history
if echo "$GROUP_RECENT" | grep -Fxq "$MESSAGE_TEXT"; then
    echo "group:$GROUP_CHAT_ID"
    exit 0
fi

# Fallback: if group chat is active (has recent messages), assume group
LAST_GROUP_MSG=$(imsg history --chat-id "$GROUP_CHAT_ID" --limit 1 --json 2>/dev/null | jq -r '.date' 2>/dev/null)
if [ -n "$LAST_GROUP_MSG" ]; then
    # Check if last group message was within last 5 minutes
    LAST_TIMESTAMP=$(date -j -f "%Y-%m-%dT%H:%M:%S" "${LAST_GROUP_MSG%.*}" +%s 2>/dev/null)
    NOW=$(date +%s)
    DIFF=$((NOW - LAST_TIMESTAMP))
    
    if [ $DIFF -lt 300 ]; then
        # Group is active, route there
        echo "group:$GROUP_CHAT_ID"
        exit 0
    fi
fi

# Default: route directly
echo "direct:$SENDER"
