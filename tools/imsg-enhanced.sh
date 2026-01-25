#!/bin/bash
# Enhanced imsg wrapper that adds participant metadata to messages
# This solves the context bleeding issue by detecting group vs DM chats

set -euo pipefail

TOOLS_DIR="$(cd "$(dirname "$0")" && pwd)"

# Function to get chat participants
get_participants() {
  local chat_id="$1"
  "$TOOLS_DIR/get-chat-participants.sh" "$chat_id" 2>/dev/null || echo ""
}

# Function to check if chat is group
is_group_chat() {
  local chat_id="$1"
  local chat_info
  chat_info=$(get_participants "$chat_id")
  
  if [[ -z "$chat_info" ]]; then
    return 1
  fi
  
  local participant_count
  participant_count=$(echo "$chat_info" | cut -d'|' -f5)
  
  [[ "$participant_count" -ge 2 ]]
}

# Watch mode with participant enrichment
if [[ "${1:-}" == "watch" ]]; then
  shift
  
  # Stream messages with enriched metadata
  imsg watch "$@" --json | while read -r line; do
    # Extract chat_id from message
    chat_id=$(echo "$line" | jq -r '.chat_id // empty')
    
    if [[ -n "$chat_id" ]]; then
      # Get participant info
      chat_info=$(get_participants "$chat_id")
      
      if [[ -n "$chat_info" ]]; then
        participants=$(echo "$chat_info" | cut -d'|' -f4)
        participant_count=$(echo "$chat_info" | cut -d'|' -f5)
        
        # Add metadata
        echo "$line" | jq --arg participants "$participants" \
                          --arg count "$participant_count" \
                          --arg is_group "$([[ "$participant_count" -ge 2 ]] && echo "true" || echo "false")" \
                          '. + {participants: $participants, participant_count: ($count | tonumber), is_group: ($is_group == "true")}'
      else
        echo "$line"
      fi
    else
      echo "$line"
    fi
  done
else
  # Pass through to regular imsg for other commands
  exec imsg "$@"
fi
