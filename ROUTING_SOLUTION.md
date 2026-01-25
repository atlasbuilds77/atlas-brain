# Message Routing Solution

## Problem
Cannot distinguish between:
- Group chat messages (from chat-id 3)
- Direct messages (from individual numbers)

Both show as: `[iMessage +NUMBER TIMESTAMP] message`

## Root Cause
Clawdbot message format doesn't include chat_id context, only sender number.

## Solutions Explored

### 1. Script-based detection (PARTIAL)
Created: `~/clawd/tools/check-message-source.sh`
- Queries recent message history
- Checks if message appears in group chat
- Returns: "group:3" or "direct:NUMBER"

Limitations: Requires running script for every message, adds latency

### 2. Conversation state tracking (IMPLEMENTED)
Created: `~/clawd/state/conversation-context.json`
- Tracks active group chat sessions
- Lists participants
- Routing rule: When group is active, assume all messages from participants are FROM group

Override syntax: Users can prefix with `[DM]` or `[Direct]` for private messages

### 3. Ideal Solution (FUTURE)
**Modify Clawdbot message format to include chat context:**

Current: `[iMessage +14245157194 TIMESTAMP] message`
Proposed: `[iMessage +14245157194 chat:direct TIMESTAMP] message`
Or: `[iMessage +16193845759 chat:3 TIMESTAMP] message`

This would require updating the Clawdbot iMessage plugin to pass chat_id in the message header.

## Current Workaround

**Active Group Mode:**
1. When group chat is happening, set `active_group_chat.active = true`
2. ALL messages from listed participants route to chat-id 3
3. If someone needs to DM me, they prefix with `[DM]` or `[Direct]`

**Direct Mode:**
1. When no group chat active, route to sender number directly

**Toggle:**
- User says "group mode on/off"
- Or I detect group activity and auto-enable

## Implementation

```bash
# Check if sender is in active group
if [ group_active ] && [ sender in participants ]; then
    route_to="chat-id 3"
else
    route_to="sender_number"
fi

# Override check
if message starts with "[DM]" or "[Direct]"; then
    route_to="sender_number"
fi
```

## Next Steps
1. Test conversation state approach during this session
2. If successful, document for Kronos
3. Consider submitting PR to Clawdbot for chat context in message headers
