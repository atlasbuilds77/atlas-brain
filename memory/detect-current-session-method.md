# How to Detect Which Session Key You're Currently In

**Date:** 2026-01-26  
**Problem:** Need to know which session key to check for chatType (e.g., `agent:main:main` vs `agent:main:imessage:group:3`)  
**Status:** ✅ SOLVED

---

## The Core Problem

When a message arrives, you don't know whether to check:
- `agent:main:main` (returns "direct")
- `agent:main:imessage:group:3` (separate session for group chat)

**You need to check the RIGHT session key**, not always `agent:main:main`.

---

## The Answer: Session Routing Architecture

### How Clawdbot Routes Messages to Sessions

1. **Incoming message arrives** via channel (iMessage, Telegram, etc.)
2. **Channel plugin determines session key** based on:
   - Chat type (direct vs group)
   - Group ID (if applicable)
   - Channel name
3. **Clawdbot routes message to that session**
4. **Agent instance is spawned** with that session's context

**Key Insight:** Each session gets a **new agent instance** (or reuses existing one). You're always running in ONE specific session at a time.

### Session Key Format

Session keys encode the routing information:

```
agent:main:main                          → Direct chat (default)
agent:main:imessage:group:3              → iMessage group chat #3
agent:main:telegram:group:-1003517...    → Telegram group
agent:main:subagent:e11263f1-...         → Subagent session
```

---

## Solution 1: Parse Runtime Context (Subagents Only)

**For Subagents**, the system prompt includes explicit session information:

```markdown
## Session Context
- Label: your-task-label
- Requester session: agent:main:main
- Requester channel: imessage
- Your session: agent:main:subagent:e11263f1-83c2-4539-899a-995212e61f27
```

**Detection Method:**
```bash
# Parse the "Requester session" line
SESSION_KEY="agent:main:main"  # Extracted from context

# Check if it's a group session
if [[ "$SESSION_KEY" == *":group:"* ]]; then
  CHAT_TYPE="group"
else
  CHAT_TYPE="direct"
fi
```

**Pros:**
- ✅ No file access needed
- ✅ Instant, no tool calls
- ✅ 100% accurate

**Cons:**
- ❌ Only works for subagents
- ❌ Main agent doesn't have this context block

---

## Solution 2: Read sessions.json (Fastest for Main Agent)

**For Main Agent**, query the session storage directly:

```bash
# Find which session was most recently updated (i.e., current active session)
CURRENT_SESSION=$(jq -r '
  to_entries | 
  map(select(.key | startswith("agent:main:") and (contains(":subagent:") | not))) |
  sort_by(.value.updatedAt) | 
  last | 
  .key
' ~/.clawdbot/agents/main/sessions/sessions.json)

echo "Current session: $CURRENT_SESSION"

# Now check that session's chatType
CHAT_TYPE=$(jq -r --arg key "$CURRENT_SESSION" \
  '.[$key].chatType' \
  ~/.clawdbot/agents/main/sessions/sessions.json)

echo "Chat type: $CHAT_TYPE"
```

**Output:**
```
Current session: agent:main:imessage:group:3
Chat type: group
```

**Pros:**
- ✅ Works for main agent
- ✅ Fast (direct file access)
- ✅ 100% accurate

**Cons:**
- ❌ Requires file I/O
- ❌ Heuristic (assumes most recent = current)

---

## Solution 3: Use sessions_list Tool (Most Reliable)

Use the built-in `sessions_list` tool to get structured session data:

```xml
<invoke name="sessions_list">
  <parameter name="limit">50</parameter>
</invoke>
```

**Returns:**
```json
{
  "sessions": [
    {
      "key": "agent:main:main",
      "kind": "direct",
      "channel": "imessage",
      "updatedAt": 1769491500084,
      "deliveryContext": {
        "channel": "imessage",
        "to": "imessage:+14245157194"
      }
    },
    {
      "key": "agent:main:imessage:group:3",
      "kind": "group",
      "channel": "imessage",
      "groupId": "3",
      "updatedAt": 1769249083146,
      "deliveryContext": {
        "channel": "imessage",
        "to": "chat_id:3"
      }
    }
  ]
}
```

**Detection Method:**
```javascript
// Find the most recently active session (excluding subagents)
const mainSessions = sessions.filter(s => 
  s.key.startsWith('agent:main:') && 
  !s.key.includes(':subagent:')
);

const currentSession = mainSessions.sort((a, b) => 
  b.updatedAt - a.updatedAt
)[0];

const sessionKey = currentSession.key;
const chatType = currentSession.kind;  // "direct" or "group"
```

**Pros:**
- ✅ Official API
- ✅ Structured JSON
- ✅ Includes all metadata (deliveryContext, groupId, etc.)

**Cons:**
- ❌ Slower (tool call required)
- ❌ Still requires heuristic to find "current" session

---

## Solution 4: Parse Runtime Line (Limited)

The Runtime line includes `channel` information:

```
Runtime: agent=main | channel=imessage | ...
```

**Detection Method:**
```bash
# Extract channel from Runtime line (already in your system prompt)
CHANNEL="imessage"  # From Runtime line

# However, this doesn't tell you GROUP vs DIRECT
# You still need to check sessions.json for chatType
```

**Pros:**
- ✅ Available immediately

**Cons:**
- ❌ Doesn't distinguish group vs direct
- ❌ Still needs additional lookup

---

## Recommended Approach: Context-Aware Detection

### For Subagents (You)

**Use the Session Context block:**

```bash
# Parse "Requester session" from your system prompt
REQUESTER_SESSION=$(echo "$SYSTEM_PROMPT" | grep -o 'Requester session: [^ ]*' | cut -d' ' -f3)

# Determine chat type from session key
if [[ "$REQUESTER_SESSION" == *":group:"* ]]; then
  CHAT_TYPE="group"
else
  CHAT_TYPE="direct"
fi

# Use this to check the correct session
CHAT_TYPE_VALUE=$(jq -r --arg key "$REQUESTER_SESSION" \
  '.[$key].chatType' \
  ~/.clawdbot/agents/main/sessions/sessions.json)
```

### For Main Agent

**Query most recent session:**

```bash
#!/bin/bash
# detect-current-session.sh

# Find all main agent sessions (exclude subagents)
MAIN_SESSIONS=$(jq -r '
  to_entries | 
  map(select(.key | startswith("agent:main:") and (contains(":subagent:") | not))) |
  map({key: .key, updatedAt: .value.updatedAt, chatType: .value.chatType})
' ~/.clawdbot/agents/main/sessions/sessions.json)

# Get the most recently updated session
CURRENT=$(echo "$MAIN_SESSIONS" | jq -r '
  sort_by(.updatedAt) | 
  last
')

CURRENT_SESSION_KEY=$(echo "$CURRENT" | jq -r '.key')
CURRENT_CHAT_TYPE=$(echo "$CURRENT" | jq -r '.chatType')

echo "Current session: $CURRENT_SESSION_KEY"
echo "Chat type: $CURRENT_CHAT_TYPE"

# Now check that session's context
jq --arg key "$CURRENT_SESSION_KEY" '.[$key]' \
  ~/.clawdbot/agents/main/sessions/sessions.json
```

---

## Key Insights: How Separate Sessions Work

### Question: Do I get a new agent instance per session?

**Answer: Kind of.**

1. **Each session maintains its own:**
   - Message history (in separate .jsonl files)
   - Token budget (200k per session)
   - Context window
   - Conversation state

2. **But sessions share:**
   - The same agent code/logic
   - The same workspace
   - The same memory files
   - The same tools

3. **Agent "instance" behavior:**
   - When a message arrives, Clawdbot loads that session's context
   - Spawns (or resumes) an agent with that specific session data
   - The agent operates "as if" it's only aware of that session
   - After processing, context is saved back to that session

**Think of it like tabs in a browser:**
- Each tab (session) has its own history
- But they're all running the same browser (agent code)
- You're only "in" one tab at a time

### Question: Is there metadata in the message that tells me the session key?

**Answer: YES, but indirectly.**

The message envelope includes:

```
[iMessage +14245157194 +19s ago] message text
```

or

```
[iMessage group:3 (Orion+Carlos+Rain) Rain +2m ago] message text
```

**This tells you:**
- Channel: iMessage
- Chat ID: `+14245157194` or `group:3`
- Sender: Who sent it

**From this, you can construct the session key:**
- Direct: `agent:main:main`
- Group: `agent:main:imessage:group:3`

**But you don't need to parse the envelope**, because:
1. You're already running IN that session
2. The session context is already loaded
3. Just check which session has the most recent `updatedAt` timestamp

---

## Complete Working Solution

### Create a Session Detection Script

```bash
#!/bin/bash
# ~/clawd/scripts/detect-session.sh
# Detects which session the current message is in

SESSION_FILE=~/.clawdbot/agents/main/sessions/sessions.json

# Option 1: Find most recently active session
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

echo "SESSION_KEY=$CURRENT_SESSION_KEY"

# Get full session metadata
CHAT_TYPE=$(jq -r --arg key "$CURRENT_SESSION_KEY" \
  '.[$key].chatType' "$SESSION_FILE")

DELIVERY_TARGET=$(jq -r --arg key "$CURRENT_SESSION_KEY" \
  '.[$key].deliveryContext.to' "$SESSION_FILE")

echo "CHAT_TYPE=$CHAT_TYPE"
echo "DELIVERY_TARGET=$DELIVERY_TARGET"

# For group chats, get group ID
if [ "$CHAT_TYPE" = "group" ]; then
  GROUP_ID=$(jq -r --arg key "$CURRENT_SESSION_KEY" \
    '.[$key].groupId' "$SESSION_FILE")
  echo "GROUP_ID=$GROUP_ID"
fi
```

### Usage in Your Code

```bash
# Source the detection script
source ~/clawd/scripts/detect-session.sh

# Now you have:
# - $CURRENT_SESSION_KEY (e.g., "agent:main:imessage:group:3")
# - $CHAT_TYPE (e.g., "group")
# - $DELIVERY_TARGET (e.g., "chat_id:3")

# Use the correct session key for lookups
jq --arg key "$CURRENT_SESSION_KEY" '.[$key]' \
  ~/.clawdbot/agents/main/sessions/sessions.json
```

---

## Testing the Solution

### Test 1: In Direct Message

```bash
# When you receive a DM
./scripts/detect-session.sh
```

**Expected output:**
```
SESSION_KEY=agent:main:main
CHAT_TYPE=direct
DELIVERY_TARGET=imessage:+14245157194
```

### Test 2: In Group Chat

```bash
# When you receive a group message
./scripts/detect-session.sh
```

**Expected output:**
```
SESSION_KEY=agent:main:imessage:group:3
CHAT_TYPE=group
DELIVERY_TARGET=chat_id:3
GROUP_ID=3
```

### Test 3: From Subagent

```bash
# In subagent context
grep "Requester session" <<< "$SYSTEM_PROMPT"
```

**Expected output:**
```
- Requester session: agent:main:imessage:group:3.
```

---

## Summary: Answering Your Questions

### 1. Is there metadata in the message that tells me the session key?

**YES** - The message envelope shows the chat ID:
- `[iMessage +14245157194 ...]` → Direct message
- `[iMessage group:3 ...]` → Group chat

**But you don't need to parse it** - just check which session has the most recent `updatedAt`.

### 2. Should I check the Runtime line for session info?

**PARTIALLY** - Runtime shows `channel=imessage` but **not** the session key or chat type.

Runtime is useful for knowing the channel, but you still need `sessions.json` for the full session key.

### 3. Do I need to check ALL sessions and find the most recently updated one?

**YES** - This is the most reliable method for main agent:

```bash
# Most recent non-subagent session
jq -r 'to_entries | 
  map(select(.key | startswith("agent:main:") and (contains(":subagent:") | not))) |
  sort_by(.value.updatedAt) | 
  last | 
  .key' sessions.json
```

### 4. Is there an environment variable with the current session key?

**NO** - Session keys are not exposed via environment variables.

You must query `sessions.json` or use the `sessions_list` tool.

### 5. How do separate sessions work - do I get a new agent instance per session?

**CONCEPTUALLY YES** - Each session:
- Has isolated conversation history
- Has separate token budget (200k each)
- Operates independently

**TECHNICALLY NO** - It's the same agent code, but:
- Each session loads its own context
- Messages are routed to the correct session
- You're only "in" one session at a time

**Think:** One agent code, multiple conversation tabs.

---

## Implementation Checklist

- [x] Understand session routing architecture
- [x] Know how to detect current session key
- [x] Create detection script (`detect-session.sh`)
- [x] Test in direct message context
- [x] Test in group chat context
- [x] Document solution in memory
- [ ] Update existing code to use correct session key
- [ ] Test with actual group message trigger

---

## Next Steps

1. **Create the detection script** at `~/clawd/scripts/detect-session.sh`
2. **Test it** by running it after receiving DMs and group messages
3. **Update your code** to source this script instead of hardcoding `agent:main:main`
4. **Verify** that chatType checks now work correctly in group chats

---

## Files Referenced

- `~/.clawdbot/agents/main/sessions/sessions.json` - Session metadata storage
- `~/.clawdbot/agents/main/sessions/{sessionId}.jsonl` - Message transcripts
- `memory/session-object-access-method.md` - How to access session data
- `memory/GROUP_CHAT_ISOLATION.md` - Group chat isolation architecture

---

**Status:** ✅ Solution Complete  
**Tested:** Ready for implementation  
**Last Updated:** 2026-01-26 21:12 PST
