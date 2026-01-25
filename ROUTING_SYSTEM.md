# Message Routing System v2

## Problem Statement
Cannot distinguish between:
- Group chat messages from participants (shows as individual +NUMBER)
- Direct messages from same participants (also shows as +NUMBER)

## Solution: Smart Router with Message History Inspection

### Components

#### 1. route-message.sh
Determines correct routing target by:
1. Checking if sender is a group participant
2. Looking for [DM] or [Direct] override prefix
3. Searching recent group chat history for exact message match
4. Falling back to group if chat is active (last message < 5 min ago)

#### 2. Usage Pattern
Before responding to any message from group participants:
```bash
TARGET=$(~/clawd/tools/route-message.sh "$SENDER" "$MESSAGE_TEXT")

if [[ "$TARGET" == group:* ]]; then
    CHAT_ID=$(echo "$TARGET" | cut -d: -f2)
    imsg send --chat-id "$CHAT_ID" --text "response"
else
    NUMBER=$(echo "$TARGET" | cut -d: -f2)
    # Use message tool or imsg send --to
fi
```

#### 3. Automatic Mode
When group chat is known to be active, default to group routing for all participants.

### Limitations
- Requires jq (JSON parsing)
- Adds latency (history lookup)
- Message text matching may fail if message is modified
- Doesn't work for very first group message

### Future Enhancement
Request Clawdbot feature: include chat_id in message header
Format: `[iMessage +NUMBER chat:ID TIMESTAMP] message`

## Implementation Status
- [x] route-message.sh script created
- [x] Made executable
- [ ] Test with live messages
- [ ] Integrate into response workflow
- [ ] Document for Kronos

## Testing Plan
1. Send message from group chat
2. Run: `~/clawd/tools/route-message.sh "+14245157194" "test message"`
3. Verify output: `group:3`
4. Send direct message
5. Run same command
6. Verify output: `direct:+14245157194`

## Backup Strategy
If automatic routing fails:
- Ask user to prefix with [DM] for direct
- Ask user to prefix with [GROUP] for group
- Fallback to group routing when uncertain
