#!/bin/bash
# ~/clawd/scripts/detect-session.sh
# Detects which session the current message is in
#
# Usage:
#   source ~/clawd/scripts/detect-session.sh
#
# Sets variables:
#   CURRENT_SESSION_KEY   - e.g., "agent:main:imessage:group:3"
#   CHAT_TYPE             - "direct" or "group"
#   DELIVERY_TARGET       - e.g., "chat_id:3" or "imessage:+14245157194"
#   GROUP_ID              - Group ID (only for groups)

SESSION_FILE=~/.clawdbot/agents/main/sessions/sessions.json

# Find the most recently active session (excluding subagents)
CURRENT_SESSION_KEY=$(jq -r '
  to_entries | 
  map(select(
    .key | startswith("agent:main:") and 
    (contains(":subagent:") | not)
  )) |
  sort_by(.value.updatedAt) | 
  last | 
  .key
' "$SESSION_FILE")

# Get session metadata
CHAT_TYPE=$(jq -r --arg key "$CURRENT_SESSION_KEY" \
  '.[$key].chatType' "$SESSION_FILE")

DELIVERY_TARGET=$(jq -r --arg key "$CURRENT_SESSION_KEY" \
  '.[$key].deliveryContext.to' "$SESSION_FILE")

# For group chats, get group ID
if [ "$CHAT_TYPE" = "group" ]; then
  GROUP_ID=$(jq -r --arg key "$CURRENT_SESSION_KEY" \
    '.[$key].groupId' "$SESSION_FILE")
fi

# Export for use in other scripts
export CURRENT_SESSION_KEY
export CHAT_TYPE
export DELIVERY_TARGET
export GROUP_ID

# Print results if run directly (not sourced)
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
  echo "SESSION_KEY=$CURRENT_SESSION_KEY"
  echo "CHAT_TYPE=$CHAT_TYPE"
  echo "DELIVERY_TARGET=$DELIVERY_TARGET"
  if [ -n "$GROUP_ID" ]; then
    echo "GROUP_ID=$GROUP_ID"
  fi
fi
