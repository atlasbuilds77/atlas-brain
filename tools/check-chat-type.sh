#!/bin/bash
# Determine if a chat is a DM or group chat based on participant count

set -euo pipefail

chat_id="${1:-}"

if [[ -z "$chat_id" ]]; then
  echo "Usage: $0 <chat_id>" >&2
  exit 1
fi

# Get chat info
chat_info=$(~/clawd/tools/get-chat-participants.sh "$chat_id")

if [[ -z "$chat_info" ]]; then
  echo "Error: Chat ID $chat_id not found" >&2
  exit 1
fi

# Parse result: chat_id | chat_identifier | display_name | participants | count
participants=$(echo "$chat_info" | cut -d'|' -f4)
participant_count=$(echo "$chat_info" | cut -d'|' -f5)

# Determine type
if [[ "$participant_count" -eq 1 ]]; then
  echo "DM"
  echo "Participant: $participants"
elif [[ "$participant_count" -ge 2 ]]; then
  echo "GROUP"
  echo "Participants: $participants (count: $participant_count)"
else
  echo "UNKNOWN"
  echo "Participants: $participants"
fi
