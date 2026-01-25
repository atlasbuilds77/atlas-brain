#!/bin/bash
# check-message-source.sh
# Determines if a message came from a group chat or direct message

SENDER_NUMBER="$1"
MESSAGE_TEXT="$2"

# Query recent messages from the sender
RECENT_MSGS=$(imsg history --with "$SENDER_NUMBER" --limit 5 --json 2>/dev/null)

# Check if the most recent message appears in chat-id 3 (group)
GROUP_CHECK=$(imsg history --chat-id 3 --limit 10 --json 2>/dev/null | grep -F "$MESSAGE_TEXT" | head -1)

if [ -n "$GROUP_CHECK" ]; then
    echo "group:3"
else
    echo "direct:$SENDER_NUMBER"
fi
