# Live Metadata Test Results
**Date**: 2026-01-26  
**Session**: agent:main:subagent:1ce3202a-96e9-42cf-a9f4-b12d89e04072  
**Channel**: imessage  
**Purpose**: Document what metadata is ACTUALLY accessible to the agent RIGHT NOW without code changes

---

## Executive Summary

**CRITICAL FINDING**: The agent has access to metadata through THREE channels:

1. **System Prompt Context** - Visible in "Runtime" section
2. **Environment Variables** - Limited but includes service info
3. **Log Files** - Rich internal data but not realtime

**The Gap**: Group/message metadata (chatGuid, participants, etc.) exists internally in `ctxPayload` but is **NOT exposed** through any of these channels to the agent context.

---

## 1. Environment Variables (Current Session)

### ✅ Available Right Now

```bash
# Service Info
CLAWDBOT_SERVICE_KIND=gateway
CLAWDBOT_LAUNCHD_LABEL=com.clawdbot.gateway
CLAWDBOT_GATEWAY_PORT=18789
CLAWDBOT_SERVICE_VERSION=2026.1.22
CLAWDBOT_SERVICE_MARKER=clawdbot
CLAWDBOT_SYSTEMD_UNIT=clawdbot-gateway.service

# System Info
HOME=/Users/atlasbuilds
USER=atlasbuilds
PWD=/Users/atlasbuilds/clawd
SHELL=/bin/zsh

# Node Info
CLAWDBOT_NODE_OPTIONS_READY=1
NODE_OPTIONS=--disable-warning=ExperimentalWarning

# Path Info
CLAWDBOT_PATH_BOOTSTRAPPED=1
PATH=/Users/atlasbuilds/.cargo/bin:/opt/homebrew/bin:...

# External APIs (careful with these!)
OPENAI_API_KEY=sk-proj-...
```

### ❌ NOT Available
- No `MESSAGE_*` variables
- No `SESSION_*` variables (except in logs)
- No `CHAT_*` variables
- No `GROUP_*` variables
- No `SENDER_*` variables
- No `CLAWDBOT_CONTEXT_*` variables

**Conclusion**: Environment variables contain NO message/session metadata.

---

## 2. System Prompt Context (Runtime Section)

### ✅ Available in System Prompt

From the "Runtime" section visible to the agent:

```
Runtime: agent=main | host=atlas's Mac mini | repo=/Users/atlasbuilds/clawd | 
         os=Darwin 24.3.0 (arm64) | node=v25.4.0 | 
         model=anthropic/claude-sonnet-4-5 | default_model=anthropic/claude-sonnet-4-5 | 
         channel=imessage | capabilities=none | thinking=low
```

**Fields extracted**:
- `agent`: "main" (main agent, not subagent)
- `host`: "atlas's Mac mini" (hostname)
- `repo`: "/Users/atlasbuilds/clawd" (workspace path)
- `os`: "Darwin 24.3.0 (arm64)" (OS info)
- `node`: "v25.4.0" (Node.js version)
- `model`: "anthropic/claude-sonnet-4-5" (LLM model)
- `default_model`: Same as model
- `channel`: "imessage" (message channel)
- `capabilities`: "none" (no special capabilities)
- `thinking`: "low" (reasoning mode)

### ✅ Available in Subagent Context

From the "Subagent Context" section:

```yaml
Label: live-metadata-test
Requester session: agent:main:main
Requester channel: imessage
Your session: agent:main:subagent:1ce3202a-96e9-42cf-a9f4-b12d89e04072
```

**Fields extracted**:
- `Label`: Task label (subagent purpose)
- `Requester session`: Parent session ID
- `Requester channel`: Channel the request came from
- `Your session`: Full subagent session ID

### ❌ NOT in System Prompt
- No `senderId` or `senderName`
- No `chatId`, `chatGuid`, `chatIdentifier`
- No `isGroup` or `chatType`
- No `participants` or `groupMembers`
- No `groupSubject` or `chatName`
- No `timestamp` or `messageId`
- No `To` or `From` routing fields

**Conclusion**: System prompt provides runtime/session info but NO message metadata.

---

## 3. Log Files (Internal Metadata Repository)

### ✅ Available in Logs

**Location**: `/tmp/clawdbot/clawdbot-2026-01-26.log` (JSON format, ~29MB)

**Sample entry from recent run**:
```json
{
  "subsystem": "agent/embedded",
  "message": "embedded run start: runId=2382b9cd-ece8-43ef-a4cd-04f952839c19 sessionId=68fd7af5-e3ef-49da-a828-7beba57486ad provider=anthropic model=claude-sonnet-4-5 thinking=low messageChannel=imessage",
  "_meta": {
    "runtime": "node",
    "runtimeVersion": "25.4.0",
    "hostname": "unknown",
    "date": "2026-01-27T05:03:18.249Z",
    "logLevelId": 2,
    "logLevelName": "DEBUG"
  },
  "time": "2026-01-27T05:03:18.249Z"
}
```

**Metadata available in logs**:
- `runId`: Unique ID for each agent run
- `sessionId`: Session identifier (different per conversation)
- `provider`: LLM provider (anthropic, openai, etc.)
- `model`: Model name
- `thinking`: Reasoning mode
- `messageChannel`: Channel (imessage, discord, etc.)
- `sessionKey`: Session routing key
- `queueDepth`: How many messages are queued
- `totalActive`: How many active runs
- `durationMs`: How long operations took

**Example session state log**:
```json
{
  "subsystem": "diagnostic",
  "message": "session state: sessionId=68fd7af5-e3ef-49da-a828-7beba57486ad sessionKey=unknown prev=idle new=processing reason=\"run_started\" queueDepth=0"
}
```

**Example delivery log**:
```json
{
  "subsystem": "gateway/channels/imessage",
  "message": "imessage: delivered reply to imessage:+14245157194",
  "logLevelName": "INFO"
}
```

### ❌ NOT in Logs (at DEBUG level)
- Full `ctxPayload` object (would need TRACE or verbose mode)
- Raw webhook/monitor data (would need verbose logging)
- Message text content (stripped for privacy/size)
- Participant lists (not logged by default)

**Conclusion**: Logs contain session/routing metadata but NOT message content or group details unless verbose logging is enabled.

---

## 4. Context Files (Workspace & Temp)

### ✅ Files Found

**Workspace**: `/Users/atlasbuilds/clawd/`
- No `.clawdbot*` files found
- Memory files in `memory/` (53 files/folders)
- No realtime context files

**Temp directory**: `/tmp/`
- `/tmp/clawdbot/` - Log files only (JSON logs)
- `/tmp/laura_message.txt` - Old message draft
- `/tmp/context_frame_*.jpg` - Video frames (unrelated)
- No session context files found
- No message metadata files found

**Conclusion**: No context files are written for agent consumption. All metadata stays in memory.

---

## 5. Message Body Format (What Agent Sees)

### Current Format

For **direct messages**:
```
[iMessage +14245157194 +5s 2026-01-26 20:49 PST] You good now?
```

For **group messages** (expected):
```
[iMessage Group Name id:12345 +5s 2026-01-26 20:49 PST] Alice: You good now?
```

### Extractable Data from Body
- `Channel`: "iMessage" (from prefix)
- `Sender`: "+14245157194" or "Alice"
- `Elapsed time`: "+5s" (relative to previous message)
- `Timestamp`: "2026-01-26 20:49 PST"
- `Message text`: Everything after the bracket

### NOT Extractable
- Chat GUID (internal routing ID)
- Chat ID (numeric identifier)
- Whether it's a group (unless "id:" prefix present)
- Participant list
- Group name (only if explicitly shown)
- Reply-to context (unless inline [[reply_to:X]])

---

## 6. Hidden System Context (Inferred)

### Likely Available (Based on Code Analysis)

The agent **likely receives** these as hidden system context (not in message body):

**Routing Context**:
- `From`: Full sender ID (e.g., `imessage:+14245157194` or `imessage:group:12345`)
- `To`: Reply target (where responses go)
- `SessionKey`: Unique session identifier

**Message Context**:
- `ChatType`: "group" or "direct"
- `Body`: Formatted message (what we see)
- `RawBody`: Unformatted message text

**Group Context** (if applicable):
- `GroupSubject`: Group chat name
- `GroupMembers`: Comma-separated participant list
- `SenderName`: Display name of sender
- `SenderId`: Normalized handle

**Technical Context**:
- `Timestamp`: ISO timestamp
- `AccountId`: Which account sent/received
- `ChannelAccountId`: Provider-specific ID

### How to Test for Hidden Context

**Method 1**: Read source system prompt
```bash
# Not accessible - baked into Clawdbot binary
```

**Method 2**: Test in agent code
```typescript
// If these work, they're in context:
if (context.ChatType === "group") { ... }
if (context.GroupMembers) { ... }
if (context.From.includes("group")) { ... }
```

**Method 3**: Enable verbose logging
```bash
# Would need to restart Clawdbot with debug flags
clawdbot gateway restart --verbose
```

---

## 7. What We NEED vs What We HAVE

### ✅ Already Available (No Changes Needed)

| Data | Source | Access Method |
|------|--------|---------------|
| Channel name | Message body | Parse envelope prefix |
| Sender handle | Message body | Parse envelope prefix |
| Timestamp | Message body | Parse envelope |
| Message text | Message body | Direct read |
| Session ID | Logs | Parse log files |
| Model info | System prompt | Parse "Runtime" section |
| Workspace path | System prompt | Direct read |

### ⚠️ Likely Available (Need to Verify)

| Data | Suspected Source | How to Verify |
|------|------------------|---------------|
| ChatType | Hidden context | Test `context.ChatType` in code |
| GroupSubject | Hidden context | Test `context.GroupSubject` |
| GroupMembers | Hidden context | Test `context.GroupMembers` |
| From/To | Hidden context | Test `context.From` / `context.To` |
| SenderName | Hidden context | Test `context.SenderName` |
| SenderId | Hidden context | Test `context.SenderId` |

### ❌ NOT Available (Needs Code Changes)

| Data | Why Missing | Fix Required |
|------|-------------|--------------|
| Chat GUID | Not in message body | Modify envelope formatter |
| Chat ID | Not in message body | Modify envelope formatter |
| Participants array | Formatted as string | Expose raw array in context |
| isGroup flag | Derived from ChatType | Add explicit field |
| Reply-to metadata | Only inline in body | Expose structured field |
| Raw webhook data | Not stored | Add verbose context mode |

---

## 8. Recommended Testing Approach

### Test 1: Check Hidden Context Variables

Create a test agent that logs all available context:

```javascript
// In agent code or subagent task
console.log("Testing context availability...");
console.log("ChatType:", context.ChatType);
console.log("GroupSubject:", context.GroupSubject);
console.log("GroupMembers:", context.GroupMembers);
console.log("From:", context.From);
console.log("To:", context.To);
console.log("SenderName:", context.SenderName);
console.log("SenderId:", context.SenderId);
console.log("SessionKey:", context.SessionKey);
```

### Test 2: Parse Message Body

Test what can be extracted from the message body:

```javascript
const body = "[iMessage +14245157194 +5s 2026-01-26 20:49 PST] You good now?";

const match = body.match(/^\[(\w+)\s+(.*?)\s+\+(\d+[smhd])\s+([\d-]+\s+[\d:]+\s+\w+)\]\s+(.*)$/);
if (match) {
  console.log("Channel:", match[1]);    // "iMessage"
  console.log("Sender:", match[2]);     // "+14245157194"
  console.log("Elapsed:", match[3]);    // "5s"
  console.log("Timestamp:", match[4]);  // "2026-01-26 20:49 PST"
  console.log("Text:", match[5]);       // "You good now?"
}
```

### Test 3: Enable Verbose Logging

Restart Clawdbot with debug logging to see full context:

```bash
# Stop current service
clawdbot gateway stop

# Start with verbose logging (if available)
CLAWDBOT_LOG_LEVEL=trace clawdbot gateway start

# Or check config for logging options
cat ~/.clawdbot/config.json | grep -i log
```

### Test 4: Monitor Logs in Realtime

Watch logs during a test message:

```bash
# Terminal 1: Watch logs
tail -f /tmp/clawdbot/clawdbot-2026-01-26.log | grep -i "session\|message\|context"

# Terminal 2: Send test message via iMessage
# Check what metadata appears in logs
```

---

## 9. Conclusions

### What's Definitely Accessible RIGHT NOW

1. **Runtime info** (model, channel, workspace, etc.) - ✅ Via system prompt
2. **Session info** (session IDs, run IDs) - ✅ Via logs
3. **Message envelope** (channel, sender, timestamp) - ✅ Via message body parsing
4. **Service info** (gateway port, version, etc.) - ✅ Via environment variables

### What's LIKELY Accessible (Need Verification)

1. **ChatType** - Probably in hidden context
2. **GroupSubject** - Probably in hidden context
3. **GroupMembers** - Probably in hidden context
4. **From/To routing** - Probably in hidden context

### What's NOT Accessible (Needs Code Changes)

1. **Chat GUID** - Only used internally
2. **Chat ID** - Only used internally
3. **Structured participants** - Only formatted string available
4. **Raw webhook data** - Not exposed to agent
5. **Full ctxPayload** - Only used internally

---

## 10. Next Steps

### Immediate Actions (No Code Changes)

1. **Write a test agent/subagent** that attempts to access hidden context fields
2. **Parse message body** to extract envelope metadata
3. **Read log files** to find session IDs and routing info
4. **Document findings** - what works vs what doesn't

### Short-term (Feature Requests)

1. **Add group indicator** to message envelope (e.g., `[iMessage Group: Family Chat ...]`)
2. **Expose ChatType** in message body or as system message
3. **Add reply context** as structured field instead of inline
4. **Create context files** - write session metadata to `/tmp/clawdbot-session-*.json`

### Long-term (Architecture Changes)

1. **Structured metadata block** appended to messages
2. **Context API** - expose `context.*` fields to agent
3. **Verbose mode** - optional detailed metadata for debugging
4. **Session storage** - persistent context accessible across messages

---

## 11. Key Files and Locations

| Resource | Path | Purpose |
|----------|------|---------|
| Log files | `/tmp/clawdbot/clawdbot-YYYY-MM-DD.log` | Session/routing metadata |
| Workspace | `/Users/atlasbuilds/clawd/` | Agent memory/files |
| Memory files | `/Users/atlasbuilds/clawd/memory/` | Persistent knowledge |
| Gateway binary | `/opt/homebrew/bin/clawdbot` | Main executable |
| Extension source | `/opt/homebrew/lib/node_modules/clawdbot/` | Source code (read-only) |
| Browser data | `~/.clawdbot/browser/` | Browser profiles |
| Config | `~/.clawdbot/config.json` | Service configuration |

---

## 12. Summary Table

| Metadata Type | Available Now | Source | Verification Status |
|---------------|---------------|--------|-------------------|
| **Runtime** | ✅ Yes | System prompt | ✅ Verified |
| **Session ID** | ✅ Yes | Logs | ✅ Verified |
| **Environment** | ✅ Yes | `printenv` | ✅ Verified |
| **Message body** | ✅ Yes | Agent input | ✅ Verified |
| **Channel name** | ✅ Yes | Message envelope | ✅ Verified |
| **Sender** | ✅ Yes | Message envelope | ✅ Verified |
| **Timestamp** | ✅ Yes | Message envelope | ✅ Verified |
| **ChatType** | ⚠️ Likely | Hidden context | ❌ Needs test |
| **GroupSubject** | ⚠️ Likely | Hidden context | ❌ Needs test |
| **GroupMembers** | ⚠️ Likely | Hidden context | ❌ Needs test |
| **From/To** | ⚠️ Likely | Hidden context | ❌ Needs test |
| **Chat GUID** | ❌ No | Internal only | ✅ Confirmed missing |
| **Chat ID** | ❌ No | Internal only | ✅ Confirmed missing |
| **Participants** | ❌ No | Internal only | ✅ Confirmed missing |
| **isGroup** | ❌ No | Internal only | ✅ Confirmed missing |

---

## 13. Final Answer to Original Question

**"What metadata is available RIGHT NOW without code changes?"**

### Definitely Available
- Model name, channel, host, workspace path (from system prompt)
- Session ID, run ID (from logs)
- Environment variables (service info)
- Message envelope (channel, sender, timestamp)
- Message body text

### Probably Available (need to test)
- ChatType, GroupSubject, GroupMembers
- From/To routing fields
- SenderName, SenderId

### Not Available
- Chat GUID, Chat ID
- Structured participant list
- Raw webhook data
- Full internal context

**Recommendation**: Write a test subagent that attempts to access `context.ChatType`, `context.GroupMembers`, etc., and reports what works. If those fields are accessible, group detection is already possible without code changes.

---

**Generated**: 2026-01-27T05:03:30Z  
**Agent**: Subagent 1ce3202a-96e9-42cf-a9f4-b12d89e04072  
**Task**: Live metadata availability testing
