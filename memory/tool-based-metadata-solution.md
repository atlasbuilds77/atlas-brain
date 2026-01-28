# Tool-Based Session Metadata Access Solution

**Date:** 2026-01-26  
**Task:** Design a tool-based solution to access session metadata (specifically `session.chatType`)

## Executive Summary

✅ **SOLUTION FOUND**: `chatType` is **directly stored** in `sessions.json` and accessible via multiple methods!

**Key Discovery:** `session.chatType` exists and can be read using:
1. **Best:** Direct file access to `~/.clawdbot/agents/main/sessions/sessions.json`
2. **Alternative:** `clawdbot sessions --json` CLI (transforms `chatType` → `kind`)
3. **Fallback:** Parse session key format or read from subagent context

**Answer to core question: "Can we use tools to read session.chatType?"**
- ✅ **YES** - via `Read` tool on sessions.json file
- ✅ **YES** - via `exec` tool with `jq` query
- ✅ **YES** - via `exec` tool with `clawdbot sessions` CLI

---

## 1. Available Tools for Session Metadata

### ✅ Primary Solution: `clawdbot sessions` Command

**Command:** `clawdbot sessions --json`

**What it provides:**
```json
{
  "key": "agent:main:main",
  "kind": "direct",
  "sessionId": "356267eb-e1ee-415b-956e-d10e9adf4449",
  "updatedAt": 1769490485213,
  "model": "claude-sonnet-4-5",
  "totalTokens": 63432
}
```

**Key Fields:**
- `key`: Session identifier (format: `agent:{agent}:{channel}:{chatId}`)
- `kind`: `"direct"` or `"group"` (correlates to chatType)
- `sessionId`: Unique session UUID
- `model`: Model being used
- `totalTokens`: Token usage

**How to use in agent code:**
```bash
# Get all sessions as JSON
clawdbot sessions --json | jq '.sessions[]'

# Find current session (from context)
clawdbot sessions --json | jq '.sessions[] | select(.key == "agent:main:main")'

# Filter by kind/chatType
clawdbot sessions --json | jq '.sessions[] | select(.kind == "group")'
```

---

## 2. Session Key Format Analysis

Session keys encode the channel and chat type:

### Format Patterns:
```
agent:{agentName}:main                           # Main direct chat
agent:{agentName}:{channel}:group:{groupId}      # Group chat  
agent:{agentName}:subagent:{uuid}                # Subagent session
agent:{agentName}:{channel}:group:{id}:topic:{n} # Forum topic
```

### Examples:
- `agent:main:main` → Direct chat with main agent
- `agent:main:telegram:group:-1003517215733` → Telegram group
- `agent:main:imessage:group:5` → iMessage group chat
- `agent:main:subagent:c5a7ff71-...` → Subagent session

### Parsing Logic:
```javascript
function parseSessionKey(key) {
  const parts = key.split(':');
  return {
    agent: parts[1],
    channel: parts[2],
    chatType: parts[3] === 'group' ? 'group' : 'direct',
    chatId: parts.slice(3).join(':')
  };
}
```

---

## 3. Session Context Block (Alternative)

**Available in subagent/runtime context:**

```markdown
## Session Context
- Label: tool-based-metadata-access
- Requester session: agent:main:main.
- Requester channel: imessage.
- Your session: agent:main:subagent:c5a7ff71-93c1-4f7b-818f-8eab864ba136.
```

**Advantages:**
- ✅ Already injected into context (no tool call needed)
- ✅ Provides `Requester channel` explicitly
- ✅ Available in all subagent contexts

**Limitations:**
- ❌ Only available in subagent sessions (not main agent)
- ❌ Requires parsing context instead of structured data
- ❌ Not queryable/filterable

---

## 4. Comparison: chatType Field vs kind Field

| Field | Values | Source | Purpose |
|-------|--------|--------|---------|
| `chatType` | `"direct"`, `"group"` | **sessions.json (direct file access)** | **✅ STORED DIRECTLY** |
| `kind` | `"direct"`, `"group"` | `clawdbot sessions --json` output | Computed for CLI display |
| Session key | `agent:X:channel:...` | Session identifier | Encodes channel + chat info |

**CRITICAL FINDING:** `chatType` **IS stored** in the raw `sessions.json` file but is **transformed to `kind`** in the CLI output!

### Evidence:
```json
// From ~/.clawdbot/agents/main/sessions/sessions.json
"agent:main:main": {
  "chatType": "direct",
  "channel": "imessage",
  ...
}

"agent:main:imessage:group:3": {
  "chatType": "group",
  "channel": "imessage",
  "groupId": "3",
  ...
}
```

---

## 5. Recommended Implementation

### For accessing current session's chatType:

**✅ RECOMMENDED: Option A - Read sessions.json directly (fastest, most accurate)**
```bash
# Direct file access - chatType is stored natively
cat ~/.clawdbot/agents/main/sessions/sessions.json | \
  jq '.["agent:main:main"].chatType'
# Output: "direct"

# Or with variables
SESSION_KEY="agent:main:main"
jq -r --arg key "$SESSION_KEY" '.[$key].chatType' \
  ~/.clawdbot/agents/main/sessions/sessions.json
```

**Option B: Use clawdbot sessions CLI (friendly but transforms chatType → kind)**
```bash
# Get current session metadata
CURRENT_SESSION="agent:main:main"
clawdbot sessions --json | jq --arg key "$CURRENT_SESSION" \
  '.sessions[] | select(.key == $key) | {key, kind, channel: (.key | split(":")[2])}'
# Output: {"key": "agent:main:main", "kind": "direct", "channel": "main"}
```

**Option C: Parse session context (fastest, no tool call, but less reliable)**
```typescript
// Read from injected context block
const requesterChannel = "imessage";  // From "Requester channel: imessage"
const sessionKey = "agent:main:main"; // From "Requester session: agent:main:main"
const chatType = sessionKey.includes(':group:') ? 'group' : 'direct';
```

### Complete Working Example (via exec tool):
```xml
<invoke name="exec">
  <parameter name="command">
    jq -r '.["agent:main:main"].chatType' \
      ~/.clawdbot/agents/main/sessions/sessions.json
  

---

## 6. Proposed Custom Tool Design

If a dedicated tool were to be implemented:

```typescript
interface SessionMetadataTool {
  name: "get_session_metadata";
  parameters: {
    sessionKey?: string;  // Optional: defaults to current session
  };
  returns: {
    sessionKey: string;
    kind: "direct" | "group";
    channel: string;      // Extracted from key
    sessionId: string;
    model: string;
    totalTokens: number;
    updatedAt: number;
  };
}
```

**Implementation:**
```bash
# Would wrap the existing CLI command
clawdbot sessions --json | jq --arg key "$sessionKey" \
  '.sessions[] | select(.key == $key)'
```

---

## 7. Workarounds Using Existing Tools

### ✅ Workaround 1: Use `exec` tool to call `clawdbot sessions`
```xml
<invoke name="exec">
  <parameter name="command">clawdbot sessions --json | jq '.sessions[] | select(.key == "agent:main:main")'
---

## 8. Verified Working Implementation

### ✅ TESTED & CONFIRMED WORKING

All methods have been tested and verified (see `tool-based-metadata-solution-test.sh`):

**Method 1: Direct File Read (FASTEST)**
```bash
# Read chatType
jq -r '.["agent:main:main"].chatType' \
  ~/.clawdbot/agents/main/sessions/sessions.json
# Output: "direct"

# Read channel
jq -r '.["agent:main:main"].channel' \
  ~/.clawdbot/agents/main/sessions/sessions.json
# Output: "imessage"
```

**Method 2: CLI Command**
```bash
# Get kind (same as chatType)
clawdbot sessions --json | \
  jq -r '.sessions[] | select(.key == "agent:main:main") | .kind'
# Output: "direct"
```

**Method 3: Via Clawdbot Tools**
```xml
<!-- Using Read tool -->
<invoke name="Read">
  <parameter name="path">~/.clawdbot/agents/main/sessions/sessions.json</parameter>
</invoke>
<!-- Then parse JSON for specific session -->

<!-- Using exec tool -->
<invoke name="exec">
  <parameter name="command">
    jq -r '.["agent:main:main"].chatType' \
      ~/.clawdbot/agents/main/sessions/sessions.json
  </parameter>
</invoke>
```

### Real Output Examples:

**Direct chat session:**
```json
{
  "chatType": "direct",
  "channel": "imessage",
  "sessionId": "356267eb-e1ee-415b-956e-d10e9adf4449",
  "model": "claude-sonnet-4-5",
  "totalTokens": 65219
}
```

**Group chat session:**
```json
{
  "chatType": "group",
  "channel": "imessage",
  "groupId": "3",
  "displayName": "imessage:g-3"
}
```

---

## 9. Final Recommendations

### For Production Use:

1. **Primary Method:** Use `Read` tool + JSON parsing
   - Most reliable
   - Works in all contexts
   - Returns native `chatType` field

2. **Quick Checks:** Use `exec` + `jq` one-liner
   - Fast for simple queries
   - Good for conditional logic

3. **Batch Queries:** Use `clawdbot sessions --json`
   - Best for listing multiple sessions
   - Note: returns `kind` instead of `chatType`

### Code Template:
```typescript
// Pseudocode for accessing chatType in a Clawdbot agent

async function getCurrentChatType(sessionKey: string): Promise<string> {
  // Option 1: Read file directly
  const sessionsFile = await read('~/.clawdbot/agents/main/sessions/sessions.json');
  const sessions = JSON.parse(sessionsFile);
  return sessions[sessionKey]?.chatType || 'unknown';
  
  // Option 2: Use exec
  const result = await exec(`
    jq -r '.["${sessionKey}"].chatType' \
      ~/.clawdbot/agents/main/sessions/sessions.json
  `);
  return result.trim();
}

// Usage
const chatType = await getCurrentChatType('agent:main:main');
if (chatType === 'group') {
  // Handle group chat logic
} else {
  // Handle direct chat logic
}
```

---

## 10. Summary

**Question:** Can we use tools to read session.chatType?

**Answer:** ✅ **YES - Multiple ways!**

| Method | Tool | Speed | Accuracy | Recommended |
|--------|------|-------|----------|-------------|
| Read sessions.json | `Read` | ⚡️⚡️⚡️ | ✅ Native | ✅ Best |
| exec + jq | `exec` | ⚡️⚡️ | ✅ Native | ✅ Good |
| clawdbot sessions | `exec` | ⚡️ | ⚠️ Transforms to `kind` | ⚠️ OK |
| Parse context | None | ⚡️⚡️⚡️ | ⚠️ Heuristic | ⚠️ Fallback |

**Recommendation:** Use `Read` tool to access `sessions.json` directly - it's fast, reliable, and returns the native `chatType` field.

