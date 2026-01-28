#!/usr/bin/env bash
# ~/clawd/scripts/detect-active-session-final.sh
# Detects which session the current message is in by parsing the message envelope
#
# Usage:
#   ./scripts/detect-active-session-final.sh
#   # OR for sourcing:
#   eval "$(./scripts/detect-active-session-final.sh --export)"
#
# Outputs:
#   SESSION_KEY      - e.g., "agent:main:imessage:group:10"
#   CHAT_TYPE        - "direct" or "group"
#   GROUP_ID         - Group ID (only for groups)
#   DELIVERY_TARGET  - Where to send replies

SESSION_FILE=~/.clawdbot/agents/main/sessions/sessions.json
TEMPFILE=$(mktemp)

# Cleanup on exit
trap "rm -f $TEMPFILE" EXIT

# Get all non-subagent session keys and their session IDs
jq -r 'to_entries | 
  map(select(.key | startswith("agent:main:") and (contains(":subagent:") | not))) | 
  .[] | "\(.key)\t\(.value.sessionId)"' "$SESSION_FILE" > "$TEMPFILE"

MOST_RECENT_MESSAGE=""
MOST_RECENT_TIME=0
MOST_RECENT_SESSION_KEY=""

# Read through each session
while IFS=$'\t' read -r session_key session_id; do
  transcript=~/.clawdbot/agents/main/sessions/${session_id}.jsonl
  
  if [ -f "$transcript" ] && [ -s "$transcript" ]; then
    # Get last user message from this transcript
    last_entry=$(tail -100 "$transcript" | grep '"role":"user"' | tail -1)
    
    if [ -n "$last_entry" ]; then
      user_msg=$(echo "$last_entry" | jq -r '.message.content[0].text // empty' 2>/dev/null)
      user_time=$(echo "$last_entry" | jq -r '.message.timestamp // .timestamp // empty' 2>/dev/null)
      
      if [ -n "$user_msg" ] && [ -n "$user_time" ]; then
        # Check if timestamp is already in epoch format (milliseconds)
        if [[ "$user_time" =~ ^[0-9]+$ ]]; then
          # Already epoch milliseconds, convert to seconds
          timestamp_epoch=$((user_time / 1000))
        else
          # ISO format, convert it
          time_str=$(echo "$user_time" | sed 's/\.[0-9]*Z$//' | sed 's/\+.*//')
          timestamp_epoch=$(date -j -f "%Y-%m-%dT%H:%M:%S" "$time_str" "+%s" 2>/dev/null || echo 0)
        fi
        
        # Keep track of most recent
        if [ "$timestamp_epoch" -gt "$MOST_RECENT_TIME" ]; then
          MOST_RECENT_TIME=$timestamp_epoch
          MOST_RECENT_MESSAGE="$user_msg"
          MOST_RECENT_SESSION_KEY="$session_key"
        fi
      fi
    fi
  fi
done < "$TEMPFILE"

# Parse the message envelope to determine session details
if [ -n "$MOST_RECENT_MESSAGE" ] && [ -n "$MOST_RECENT_SESSION_KEY" ]; then
  SESSION_KEY="$MOST_RECENT_SESSION_KEY"
  
  # Check for group indicators in the message envelope
  if echo "$MOST_RECENT_MESSAGE" | grep -q "Group id:"; then
    CHAT_TYPE="group"
    GROUP_ID=$(echo "$MOST_RECENT_MESSAGE" | grep -o "Group id:[0-9]*" | cut -d: -f2)
  else
    CHAT_TYPE="direct"
    GROUP_ID=""
  fi
  
  # Get delivery target from sessions.json
  DELIVERY_TARGET=$(jq -r --arg key "$SESSION_KEY" \
    '.[$key].deliveryContext.to // empty' "$SESSION_FILE" 2>/dev/null)
  
  # Output results
  if [ "$1" = "--export" ]; then
    # Export format for eval
    echo "export SESSION_KEY='$SESSION_KEY'"
    echo "export CHAT_TYPE='$CHAT_TYPE'"
    [ -n "$DELIVERY_TARGET" ] && echo "export DELIVERY_TARGET='$DELIVERY_TARGET'"
    [ -n "$GROUP_ID" ] && echo "export GROUP_ID='$GROUP_ID'"
  else
    # Human-readable format
    echo "SESSION_KEY=$SESSION_KEY"
    echo "CHAT_TYPE=$CHAT_TYPE"
    [ -n "$DELIVERY_TARGET" ] && echo "DELIVERY_TARGET=$DELIVERY_TARGET"
    [ -n "$GROUP_ID" ] && echo "GROUP_ID=$GROUP_ID"
  fi
  
  exit 0
else
  echo "ERROR: No recent user message found" >&2
  exit 1
fi
