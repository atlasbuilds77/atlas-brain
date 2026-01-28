# Session Object Access Method - Complete Guide

**Date:** 2026-01-27  
**Purpose:** Document HOW agents access session.chatType and other session metadata at runtime  
**Status:** ✅ COMPLETE

---

## Executive Summary

**THE ANSWER:** Session metadata (including `chatType`) is **NOT directly accessible as a runtime variable** like `session.chatType`. Instead, agents must access it through:

1. **Reading session storage files** (`~/.clawdbot/agents/main/sessions/sessions.json`)
2. **Using the `clawdbot sessions --json` CLI command** via the `exec` tool
3. **Parsing the session context** injected into system prompts
4. **Using specialized session tools** (`session_status`, `sessions_list`)

**CRITICAL FINDING:** There is no `session` object available at runtime. Session data is stored externally and must be explicitly queried.

---

## The Problem Statement

Sparks discovered that session metadata lives in fields like:
- `session.chatType` (in storage: `"direct"` or `"group"`)
- `session.deliveryContext.to` (routing information)
- `session.origin.chatType` (message origin metadata)

But when the agent runs, there is **no `session` object** to access directly.

---

## Solution 1: Direct File Access (Fastest)

### Method: Read sessions.json

Session metadata is stored in: `~/.clawdbot/agents/main/sessions/sessions.json`

**Structure:**
```json
{
  "agent:main:main": {
    "chatType": "direct",
    "channel": "imessage",
    "sessionId": "356267eb-...",
    "deliveryContext": {
      "channel": "imessage",
      "to": "imessage:+14245157194"
    },
    "origin": {
      "chatType": "direct",
      "provider": "imessage",
      "from": "imessage:+14245157194",
      "to": "imessage:+14245157194"
    }
  },
  "agent:main:imessage:group:3": {
    "chatType": "group",
    "channel": "imessage",
    "groupId": "3",
    "sessionId": "68fd7af5-...",
    "deliveryContext": {
      "channel": "imessage",
      "to": "chat_id:3"
    }
  }
}
```

**Agent code to access chatType:**
```bash
# Via exec tool
jq -r '.["agent:main:main"].chatType' \
  ~/.clawdbot/agents/main/sessions/sessions.json
# Returns: "direct"

# For group chat:
jq -r '.["agent:main:imessage:group:3"].chatType' \
  ~/.clawdbot/agents/main/sessions/sessions.json
# Returns: "group"
```

**Access deliveryContext.to:**
```bash
jq -r '.["agent:main:main"].deliveryContext.to' \
  ~/.clawdbot/agents/main/sessions/sessions.json
# Returns: "imessage:+14245157194"
```

---

## Solution 2: CLI Command (Official Interface)

### Method: Use `clawdbot sessions --json`

**Command:**
```bash
clawdbot sessions --json
```

**Output Structure:**
```json
{
  "sessions": [
    {
      "key": "agent:main:main",
      "kind": "direct",
      "sessionId": "356267eb-...",
      "model": "claude-sonnet-4-5",
      "channel": "imessage",
      "deliveryContext": {
        "channel": "imessage",
        "to": "imessage:+14245157194"
      }
    }
  ]
}
```

**Note:** The CLI transforms `chatType` → `kind` for display purposes.

**Agent code:**
```bash
# Get current session metadata
clawdbot sessions --json | \
  jq '.sessions[] | select(.key == "agent:main:main")'

# Get just the chat type
clawdbot sessions --json | \
  jq -r '.sessions[] | select(.key == "agent:main:main") | .kind'
# Returns: "direct"
```

---

## Solution 3: Built-in Tools (Most Reliable)

### Method A: Use `session_status` tool

The `session_status` tool is available to agents and provides session metadata:

**Tool call:**
```xml
<invoke name="session_status">
  <parameter name="sessionKey">agent:main:main</parameter>
</invoke>
```

**Returns:**
```json
{
  "ok": true,
  "sessionKey": "agent:main:main",
  "statusText": "📊 Session Status:\n🤖 Agent: main\n..."
}
```

**Limitations:** Returns formatted text, not structured data. Better for status display than programmatic access.

### Method B: Use `sessions_list` tool

**Tool call:**
```xml
<invoke name="sessions_list">
  <parameter name="kinds">["main", "group"]</parameter>
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
      "deliveryContext": {
        "channel": "imessage",
        "to": "imessage:+14245157194"
      }
    },
    {
      "key": "agent:main:imessage:group:3",
      "kind": "group",
      "channel": "imessage",
      "deliveryContext": {
        "channel": "imessage",
        "to": "chat_id:3"
      }
    }
  ]
}
```

**Advantage:** Returns structured JSON with all session metadata.

---

## Solution 4: Parse Session Context (No Tool Call)

### Method: Extract from System Prompt

For **subagent sessions**, the system prompt includes a "Session Context" block:

```markdown
## Session Context
- Label: session-object-access
- Requester session: agent:main:main.
- Requester channel: imessage.
- Your session: agent:main:subagent:1496cfa7-582d-46f9-852c-a02368188279.
```

**Parsing logic:**
```javascript
// From context block:
const requesterSession = "agent:main:main";
const requesterChannel = "imessage";
const mySession = "agent:main:subagent:1496cfa7-582d-46f9-852c-a02368188279";

// Determine chat type from session key format:
const chatType = requesterSession.includes(':group:') ? 'group' : 'direct';
```

**Advantage:** No tool call needed, available immediately.  
**Limitation:** Only works in subagent context, requires string parsing.

---

## Solution 5: Parse Session Key (Heuristic)

### Method: Decode session key format

Session keys encode the chat type:

**Format patterns:**
```
agent:main:main                          → Direct chat
agent:main:imessage:group:3              → iMessage group chat
agent:main:telegram:group:-1003517...    → Telegram group
agent:main:discord:channel:123456...     → Discord channel
```

**Parsing function:**
```javascript
function getSessionChatType(sessionKey) {
  const parts = sessionKey.split(':');
  
  // Check for group/channel keywords
  if (parts.includes('group')) return 'group';
  if (parts.includes('channel')) return 'channel';
  
  // Main session is direct
  if (sessionKey === 'agent:main:main') return 'direct';
  if (sessionKey.endsWith(':main')) return 'direct';
  
  // Subagent sessions inherit parent type
  if (parts.includes('subagent')) return 'subagent';
  
  // Default to direct
  return 'direct';
}
```

**Usage:**
```javascript
const sessionKey = "agent:main:imessage:group:3";
const chatType = getSessionChatType(sessionKey);
// Returns: "group"
```

**Advantage:** Fast, no file I/O.  
**Limitation:** Heuristic only, may not catch all edge cases.

---

## Where Session Data Lives (Architecture)

### 1. Session Storage Files

**Location:** `~/.clawdbot/agents/{agentId}/sessions/`

**Files:**
- `sessions.json` - Session metadata (chatType, deliveryContext, etc.)
- `{sessionId}.jsonl` - Message transcripts

**Structure in sessions.json:**
```json
{
  "sessionKey": {
    "sessionId": "uuid",
    "chatType": "direct" | "group" | "channel",
    "channel": "imessage" | "telegram" | "discord" | ...,
    "origin": {
      "chatType": "...",
      "provider": "...",
      "from": "...",
      "to": "..."
    },
    "deliveryContext": {
      "channel": "...",
      "to": "...",
      "accountId": "..."
    },
    "groupId": "...",      // For groups
    "displayName": "...",
    "updatedAt": 123456789,
    "model": "...",
    "totalTokens": 12345
  }
}
```

### 2. Runtime Context (ctxPayload)

**Internal Object (not directly accessible):**
```javascript
const ctxPayload = {
  Body: "[iMessage +14245157194 +19s ...] message text",
  RawBody: "message text",
  From: "imessage:group:3" | "imessage:+14245157194",
  To: "chat_id:3" | "imessage:+14245157194",
  ChatType: "group" | "direct",
  GroupSubject: "Dev Team",           // Groups only
  GroupMembers: "+14245..., +16195...", // Groups only
  SenderName: "Orion",
  SenderId: "+14245157194",
  SessionKey: "agent:main:imessage:group:3"
};
```

**This object is used internally** by Clawdbot to:
- Format the message envelope
- Determine routing
- Update session state
- Build the system prompt

**But it is NOT exposed** to the agent as `context.ChatType` or `session.chatType`.

### 3. System Prompt Injection

Session metadata is **partially** injected into the system prompt:

**Runtime section:**
```
Runtime: agent=main | host=... | channel=imessage | ...
```

**Subagent context section:**
```
## Session Context
- Requester session: agent:main:main
- Requester channel: imessage
- Your session: agent:main:subagent:...
```

**But NOT included:**
- `chatType` field
- `deliveryContext` object
- `origin` metadata
- Group details

---

## Best Practices

### ✅ Recommended Approach: Use sessions_list Tool

**Why:**
- Official API designed for this purpose
- Returns structured JSON
- Includes deliveryContext for routing
- Works across all session types

**Example:**
```xml
<invoke name="sessions_list">
  <parameter name="limit">50</parameter>
</invoke>
```

Then filter for your session and access `kind`, `deliveryContext`, etc.

### ✅ Fast Path: Direct File Access

**When:** You need chatType immediately without complex queries

**Example:**
```bash
jq -r '.["agent:main:main"].chatType' \
  ~/.clawdbot/agents/main/sessions/sessions.json
```

### ⚠️ Heuristic Fallback: Parse Session Key

**When:** No file access, need quick check

**Example:**
```javascript
const isGroup = sessionKey.includes(':group:');
```

**Warning:** Not 100% reliable for all edge cases.

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Assuming `session` Object Exists

```javascript
// WRONG - No such object at runtime
const chatType = session.chatType;
const target = session.deliveryContext.to;
```

**Correct:**
```bash
# Read from storage
chatType=$(jq -r '.["agent:main:main"].chatType' \
  ~/.clawdbot/agents/main/sessions/sessions.json)
```

### ❌ Mistake 2: Parsing Message Envelope

```javascript
// WRONG - Envelope format is for display only
const match = message.match(/\[iMessage ([+\d]+)/);
const chatType = match ? "direct" : "unknown";
```

**Correct:**
```xml
<!-- Use proper tool -->
<invoke name="sessions_list">
  <parameter name="limit">1</parameter>
</invoke>
```

### ❌ Mistake 3: Using SenderId for Routing

```javascript
// WRONG - SenderId shows who sent, not where to reply
const target = `imessage:${senderId}`;
```

**Correct:**
```bash
# Get routing target from deliveryContext
target=$(jq -r '.["agent:main:main"].deliveryContext.to' \
  ~/.clawdbot/agents/main/sessions/sessions.json)
```

---

## Complete Working Examples

### Example 1: Check if Current Session is a Group

```bash
#!/bin/bash
SESSION_KEY="agent:main:main"

# Method A: Read from sessions.json
CHAT_TYPE=$(jq -r --arg key "$SESSION_KEY" \
  '.[$key].chatType' \
  ~/.clawdbot/agents/main/sessions/sessions.json)

if [ "$CHAT_TYPE" = "group" ]; then
  echo "This is a group chat"
else
  echo "This is a direct message"
fi

# Method B: Parse session key
if [[ "$SESSION_KEY" == *":group:"* ]]; then
  echo "This is a group chat"
fi
```

### Example 2: Get Routing Target

```bash
#!/bin/bash
SESSION_KEY="agent:main:imessage:group:3"

# Read deliveryContext.to from sessions.json
REPLY_TARGET=$(jq -r --arg key "$SESSION_KEY" \
  '.[$key].deliveryContext.to' \
  ~/.clawdbot/agents/main/sessions/sessions.json)

echo "Reply target: $REPLY_TARGET"
# Output: "chat_id:3"
```

### Example 3: Using sessions_list Tool

```xml
<invoke name="sessions_list">
  <parameter name="kinds">["main", "group"]</parameter>
  <parameter name="limit">10</parameter>
</invoke>
```

Then in the response, find your session and access:
```javascript
const mySession = sessions.find(s => s.key === "agent:main:main");
const chatType = mySession.kind;  // "direct" or "group"
const replyTo = mySession.deliveryContext.to;
```

---

## Summary Table

| Access Method | Speed | Accuracy | Availability | Recommended |
|---------------|-------|----------|--------------|-------------|
| **sessions.json direct read** | ⚡ Fast | ✅ 100% | Always | ✅ Yes (for quick checks) |
| **clawdbot sessions --json** | 🐌 Slow | ✅ 100% | Always | ⚠️ Use if official API needed |
| **sessions_list tool** | 🐌 Slow | ✅ 100% | Always | ✅ Yes (for structured queries) |
| **Parse session context** | ⚡ Instant | ✅ 100% | Subagents only | ✅ Yes (if available) |
| **Parse session key** | ⚡ Instant | ⚠️ ~95% | Always | ⚠️ Fallback only |
| **Assume session object** | ❌ N/A | ❌ 0% | Never | ❌ Never use |

---

## Files and Locations

| Resource | Path | Contains |
|----------|------|----------|
| Session metadata | `~/.clawdbot/agents/main/sessions/sessions.json` | chatType, deliveryContext, origin |
| Message transcripts | `~/.clawdbot/agents/main/sessions/{sessionId}.jsonl` | Full message history |
| Clawdbot source | `/opt/homebrew/lib/node_modules/clawdbot/dist/` | Implementation code |
| System prompt builder | `.../dist/agents/system-prompt.js` | How context is injected |
| Session storage handler | `.../dist/config/sessions/` | How metadata is stored |
| Delivery context utils | `.../dist/utils/delivery-context.js` | deliveryContext handling |

---

## Conclusion

**The Answer:** There is **no runtime `session` object**. Session metadata must be accessed via:

1. **✅ Best: Use `sessions_list` tool** for structured session metadata
2. **✅ Fast: Read sessions.json directly** for quick chatType checks
3. **✅ Fallback: Parse session key** if no file access available

**Key Insight:** Session data is **stored externally** in JSON files and exposed through:
- File system (`sessions.json`)
- CLI commands (`clawdbot sessions`)
- Agent tools (`sessions_list`, `session_status`)

**Not exposed as:** Runtime variables, environment variables, or direct object properties.

---

**Status:** ✅ Complete  
**Next Action:** Implement session metadata checks using recommended methods  
**Reference:** See `memory/tool-based-metadata-solution.md` for detailed examples
