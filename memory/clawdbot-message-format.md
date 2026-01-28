# Clawdbot iMessage Format Analysis

**Date**: 2026-01-26  
**Issue**: Group metadata (chatGuid, isGroup, participants) needed for routing but hidden from agent

---

## Executive Summary

**FINDING**: Group metadata EXISTS in the system but is NOT shown to the agent in the message body. The data is available in the internal context object but stripped out during message formatting.

**The Disconnect**:
- **Agent sees**: `[iMessage +14245157194 +5s 2026-01-26 20:49 PST] You good now?`
- **System knows**: chatGuid, chatId, isGroup, participants, chat_name, etc.

---

## Message Flow Architecture

### 1. Message Reception
**Location**: `/opt/homebrew/lib/node_modules/clawdbot/dist/imessage/monitor/monitor-provider.js`

Raw iMessage data arrives with FULL metadata:
```javascript
{
  sender: "+14245157194",
  text: "You good now?",
  chat_id: 12345,                    // ← Available
  chat_guid: "iMessage;+;chat123",   // ← Available
  chat_identifier: "...",            // ← Available
  is_group: true,                    // ← Available
  participants: ["...", "..."],      // ← Available
  chat_name: "Group Chat Name",      // ← Available
  created_at: "2026-01-26T20:49:00Z",
  attachments: [],
  reply_to_id: null,
  reply_to_text: null,
  reply_to_sender: null
}
```

### 2. Internal Context Creation
**Location**: Same file, line ~460+

The system creates a comprehensive `ctxPayload` object:
```javascript
const ctxPayload = finalizeInboundContext({
  Body: combinedBody,                                    // ← What agent sees
  RawBody: bodyText,
  From: isGroup ? `imessage:group:${chatId}` : `imessage:${sender}`,
  To: imessageTo,
  SessionKey: route.sessionKey,
  ChatType: isGroup ? "group" : "direct",                // ← Available
  GroupSubject: isGroup ? message.chat_name : undefined, // ← Available
  GroupMembers: isGroup ? participants.join(", ") : undefined, // ← Available
  SenderName: senderNormalized,
  SenderId: sender,
  // ... many more fields
});
```

### 3. Message Formatting (THE PROBLEM)
**Location**: `/opt/homebrew/lib/node_modules/clawdbot/dist/auto-reply/envelope.js`

The `formatInboundEnvelope()` function creates what the agent sees:

```javascript
export function formatInboundEnvelope(params) {
  const chatType = normalizeChatType(params.chatType);
  const isDirect = !chatType || chatType === "direct";
  const resolvedSender = params.senderLabel || resolveSenderLabel(params.sender);
  
  // For groups, prepend sender name to body
  const body = !isDirect && resolvedSender 
    ? `${resolvedSender}: ${params.body}` 
    : params.body;
  
  return formatAgentEnvelope({
    channel: params.channel,      // "iMessage"
    from: params.from,            // "+14245157194" or "Group Name id:12345"
    timestamp: params.timestamp,  // Date object
    previousTimestamp: params.previousTimestamp,
    envelope: params.envelope,    // Format options
    body,                         // The actual message text
  });
}
```

**Result envelope format**:
```
[iMessage +14245157194 +5s 2026-01-26 20:49 PST] You good now?
```

Or for groups:
```
[iMessage Group Name id:12345 +5s 2026-01-26 20:49 PST] John Doe: You good now?
```

---

## What's Available vs What's Shown

### ✅ Available in System (ctxPayload)
- `chatId` / `chat_id` - Numeric group ID
- `chatGuid` / `chat_guid` - Full iMessage GUID
- `chatIdentifier` / `chat_identifier` - Alternative identifier  
- `isGroup` / `is_group` - Boolean flag
- `participants` - Array of participant handles
- `chat_name` - Human-readable group name
- `ChatType` - "group" or "direct"
- `GroupSubject` - Same as chat_name
- `GroupMembers` - Comma-separated participant list
- `From` - Full routing identifier (e.g., `imessage:group:12345`)
- `To` - Target for replies
- `SessionKey` - Unique session identifier

### ❌ Hidden from Agent (not in formatted message)
Everything except:
- Channel name ("iMessage")
- Sender handle or group name
- Group ID (only shown as `id:12345` in from label)
- Timestamp
- Elapsed time
- Message body

---

## Where Metadata Is Used

### Internal Routing (NOT visible to agent)
**File**: `monitor-provider.js` lines ~200-400

```javascript
// Routing uses full metadata
const route = resolveAgentRoute({
  cfg,
  channel: "imessage",
  accountId: accountInfo.accountId,
  peer: {
    kind: isGroup ? "group" : "dm",
    id: isGroup ? String(chatId) : normalizeIMessageHandle(sender),
  },
});

// Session key is based on full context
ctxPayload.SessionKey = route.sessionKey;
```

### Reply Delivery
**File**: `monitor-provider.js` lines ~500+

```javascript
const updateTarget = (isGroup ? chatTarget : undefined) || sender;

await recordInboundSession({
  storePath,
  sessionKey: ctxPayload.SessionKey,
  ctx: ctxPayload,  // Full context saved
  updateLastRoute: !isGroup && updateTarget ? {
    sessionKey: route.mainSessionKey,
    channel: "imessage",
    to: updateTarget,
    accountId: route.accountId,
  } : undefined,
});
```

The system KNOWS where to reply because it has the full `ctxPayload` internally.

---

## The Core Problem

**For group messages**, the agent sees:
```
[iMessage Group Chat id:12345 +5s 2026-01-26 20:49 PST] Alice: Hey everyone!
```

But the agent CANNOT determine:
1. That this is a group (without parsing "id:")
2. The chatGuid (not shown at all)
3. Who else is in the group (participants hidden)
4. Whether to use `chatTarget` vs `sender` for replies

**The routing works** because Clawdbot uses the internal `ctxPayload.To` field for delivery, not the agent's understanding.

---

## Potential Solutions

### Option 1: Extend Envelope Format
Modify `formatInboundEnvelope()` to include metadata:
```
[iMessage Group Chat id:12345 guid:iMessage;+;chat123 +5s 2026-01-26 20:49 PST] Alice: Hey
```

**Pros**: Agent can parse and use metadata  
**Cons**: Clutters the envelope; breaks existing agent prompts

### Option 2: Add Metadata Block
Append structured metadata after the message:
```
[iMessage Group Chat id:12345 +5s 2026-01-26 20:49 PST] Alice: Hey

---metadata---
chatGuid: iMessage;+;chat123
chatType: group
participants: +1234, +5678, +9012
---
```

**Pros**: Clean separation; easy to parse  
**Cons**: Increases token usage; needs parser

### Option 3: Use Context Variables (RECOMMENDED)
Clawdbot likely provides context variables that aren't in the body. Check if:
- `{{ChatType}}` - group/direct
- `{{GroupMembers}}` - participant list  
- `{{To}}` - reply target
- `{{From}}` - full routing ID

These would be available to the agent without cluttering the message body.

### Option 4: Trust the System
**Current behavior**: Agent doesn't need to know routing details because:
1. Clawdbot handles reply routing via internal `ctxPayload.To`
2. Session management uses `SessionKey` not agent parsing
3. Group detection works via `ChatType` context field

**Just use** the `message` tool with `target` and let Clawdbot route it.

---

## Key Code References

| Component | File | Purpose |
|-----------|------|---------|
| Message Monitor | `/imessage/monitor/monitor-provider.js` | Receives raw iMessage data |
| Envelope Formatter | `/auto-reply/envelope.js` | Formats messages for agent |
| Context Builder | `/auto-reply/reply/inbound-context.js` | Creates ctxPayload |
| Reply Dispatcher | `/auto-reply/reply/reply-dispatcher.js` | Delivers responses |
| Group Policy | `/config/group-policy.js` | Group access control |
| Target Formatter | `/imessage/targets.js` | Formats chat targets |

---

## Current Message Format Structure

```typescript
// What the raw system receives
interface RawIMessage {
  sender: string;
  text: string;
  chat_id?: number;
  chat_guid?: string;
  chat_identifier?: string;
  is_group: boolean;
  participants?: string[];
  chat_name?: string;
  created_at: string;
  attachments?: Array<{
    original_path?: string;
    mime_type?: string;
    missing?: boolean;
  }>;
  reply_to_id?: string;
  reply_to_text?: string;
  reply_to_sender?: string;
}

// What gets stored in ctxPayload
interface InboundContext {
  Body: string;              // Formatted envelope + message
  RawBody: string;           // Just the text
  From: string;              // "imessage:group:12345" or "imessage:+1234"
  To: string;                // Reply target
  ChatType: "group" | "direct";
  GroupSubject?: string;
  GroupMembers?: string;
  SenderName: string;
  SenderId: string;
  SessionKey: string;
  // ... many more fields
}

// What the agent sees in Body
"[iMessage Group Name id:12345 +5s 2026-01-26 20:49 PST] Alice: Hey"
```

---

## Recommendations

1. **For immediate routing needs**: Use the `message` tool's `target` parameter - Clawdbot will route correctly using internal metadata

2. **For group detection**: Check if Clawdbot exposes `{{ChatType}}` or similar context variables in agent prompts

3. **For custom routing logic**: Request a feature to include minimal metadata in envelope:
   ```
   [iMessage Group Chat #group:12345 +5s 2026-01-26 20:49 PST] Alice: Hey
   ```
   The `#group:` prefix would signal group context without cluttering too much

4. **For participant info**: This is available in `ctxPayload.GroupMembers` - check if accessible via context variables

---

## Testing Notes

To verify context variable availability:
1. Send a group message
2. Check agent's system context for variables like:
   - `ChatType`
   - `GroupMembers`  
   - `From` / `To`
   - `SessionKey`

These may be available but not documented in the message body formatting.
