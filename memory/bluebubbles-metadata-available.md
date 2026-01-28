# BlueBubbles Metadata Analysis

**Date**: 2026-01-26  
**Purpose**: Document what metadata BlueBubbles webhooks provide and how it flows in Clawdbot's message pipeline

---

## Executive Summary

**CRITICAL FINDING**: BlueBubbles webhooks provide **extensive** group metadata (chatGuid, isGroup, participants, chatId, chatIdentifier, chatName) but this data is **AVAILABLE INTERNALLY** and **NOT exposed to the agent context in a visible way**.

The metadata exists and is used for routing/allowlisting, but the agent only sees simplified log output like:
```
[iMessage +14245157194 +5s 2026-01-26 20:49 PST] You good now?
```

---

## 1. Webhook Payload Structure

### What BlueBubbles Sends

The webhook receives a JSON payload with this structure:

```typescript
{
  type: "new-message" | "updated-message" | "message-reaction" | "reaction",
  data: {
    message: {
      // Core identification
      guid: string,                    // Message UUID
      
      // Chat metadata
      chatGuid: string,                // Format: "service;+/-;identifier"
      chatId: number,                  // Numeric chat ID
      chatIdentifier: string,          // Chat identifier (part of chatGuid)
      chatName: string,                // Group name (if set)
      isGroup: boolean,                // Explicit group flag
      
      // Sender info
      handle: {
        address: string,               // Phone/email
        displayName: string,           // Contact name
        id: string
      },
      
      // Participants (for groups)
      participants: [
        {
          address: string,             // Phone/email
          displayName: string,         // Contact name
          id: string
        }
      ],
      
      // Message content
      text: string,
      attachments: [...],
      
      // Reply/reaction metadata
      replyToMessageGuid: string,
      associatedMessageGuid: string,
      associatedMessageType: number,
      associatedMessageEmoji: string,
      
      // Additional fields
      fromMe: boolean,
      date: number,                    // Timestamp
      balloonBundleId: string         // For stickers
    }
  }
}
```

---

## 2. Normalized Message Structure

**File**: `/opt/homebrew/lib/node_modules/clawdbot/extensions/bluebubbles/src/monitor.ts`

The `normalizeWebhookMessage()` function extracts ALL metadata into:

```typescript
type NormalizedWebhookMessage = {
  // Message content
  text: string,
  senderId: string,
  senderName?: string,
  messageId?: string,
  timestamp?: number,
  
  // GROUP METADATA - ALL AVAILABLE
  isGroup: boolean,                   // ✅ PRESENT
  chatId?: number,                    // ✅ PRESENT
  chatGuid?: string,                  // ✅ PRESENT
  chatIdentifier?: string,            // ✅ PRESENT
  chatName?: string,                  // ✅ PRESENT (group display name)
  participants?: BlueBubblesParticipant[], // ✅ PRESENT
  
  // Additional metadata
  fromMe?: boolean,
  attachments?: BlueBubblesAttachment[],
  balloonBundleId?: string,
  
  // Reply/reaction data
  replyToId?: string,
  replyToBody?: string,
  replyToSender?: string,
  associatedMessageGuid?: string,
  associatedMessageType?: number,
  associatedMessageEmoji?: string,
  isTapback?: boolean
}
```

### Participant Structure

```typescript
type BlueBubblesParticipant = {
  id: string,      // Normalized phone/email
  name?: string    // Contact display name
}
```

---

## 3. How Group Detection Works

### Method 1: Parse chatGuid

**Location**: `monitor.ts` → `resolveGroupFlagFromChatGuid()`

```typescript
// Chat GUID format: "service;+/-;identifier"
// Examples:
//   DM:    "iMessage;-;+14245157194"
//   Group: "iMessage;+;chat660250192681427962"

function resolveGroupFlagFromChatGuid(chatGuid?: string): boolean | undefined {
  const parts = chatGuid?.split(";");
  if (parts.length >= 3) {
    if (parts[1] === "+") return true;   // Group
    if (parts[1] === "-") return false;  // DM
  }
  return undefined;
}
```

### Method 2: Explicit isGroup flag

BlueBubbles can send `isGroup: true/false` directly in the payload.

### Method 3: Participant count

If neither of the above are available, the code checks:
```typescript
const isGroup = participantsCount > 2 ? true : false;
```

### Priority Order

1. `groupFromChatGuid` (parsed from chatGuid)
2. `explicitIsGroup` (webhook's `isGroup` field)
3. `participantsCount > 2` (fallback)

---

## 4. Where Metadata Flows in the Pipeline

### Stage 1: Webhook Reception (monitor.ts)

```typescript
const message = normalizeWebhookMessage(payload);
// ✅ All metadata extracted here:
//    - isGroup
//    - chatGuid
//    - chatId  
//    - chatIdentifier
//    - chatName
//    - participants[]
```

### Stage 2: Security Checks

**Uses metadata for allowlisting**:

```typescript
// Group allowlist check
const allowed = isAllowedBlueBubblesSender({
  allowFrom: effectiveGroupAllowFrom,
  sender: message.senderId,
  chatId: message.chatId,           // ✅ USED
  chatGuid: message.chatGuid,       // ✅ USED
  chatIdentifier: message.chatIdentifier // ✅ USED
});
```

### Stage 3: Routing

**Uses metadata for session routing**:

```typescript
const peerId = isGroup
  ? chatGuid ?? chatIdentifier ?? (chatId ? String(chatId) : "group")
  : message.senderId;

const route = core.channel.routing.resolveAgentRoute({
  cfg: config,
  channel: "bluebubbles",
  accountId: account.accountId,
  peer: {
    kind: isGroup ? "group" : "dm",  // ✅ USED
    id: peerId                        // ✅ USED
  }
});
```

### Stage 4: Context Building

**Builds agent context payload**:

```typescript
const ctxPayload = {
  // Visible in logs/context
  Body: body,
  RawBody: rawBody,
  From: isGroup ? `group:${peerId}` : `bluebubbles:${message.senderId}`,
  To: `bluebubbles:${outboundTarget}`,
  SessionKey: route.sessionKey,
  ChatType: isGroup ? "group" : "direct",  // ✅ USED
  
  // Group-specific fields (PARTIALLY VISIBLE)
  GroupSubject: groupSubject,          // ✅ chatName
  GroupMembers: groupMembers,          // ✅ formatted participants
  
  // Sender info
  SenderName: message.senderName,
  SenderId: message.senderId,
  
  // NOT DIRECTLY EXPOSED TO AGENT:
  // - chatGuid (used internally for outbound routing)
  // - chatId (used internally)
  // - chatIdentifier (used internally)
  // - isGroup (used for ChatType but not exposed as separate field)
  // - participants[] (formatted into GroupMembers string)
};
```

**Key formatting**:

```typescript
// GroupMembers is formatted as:
"Tyler (+14245157194), Jane (jane@icloud.com), Bob (+15551234567)"

// GroupSubject is just the chatName:
"Family Group Chat"
```

### Stage 5: What the Agent Sees

The agent receives context fields like:

```typescript
{
  Body: "[[reply_to:5]] You good now?",
  ChatType: "group",                    // ✅ Tells agent it's a group
  GroupSubject: "Family Group Chat",    // ✅ Group name
  GroupMembers: "Tyler (+14245157194), Jane (jane@icloud.com)", // ✅ Participants
  From: "group:iMessage;+;chat660250192681427962", // ✅ Group ID
  SenderName: "Tyler",                  // ✅ Who sent it
  SenderId: "+14245157194"              // ✅ Sender phone
}
```

**BUT** these are used internally for message handling, not shown in the chat log output.

---

## 5. The Logging Problem

### What You Currently See

```
[iMessage +14245157194 +5s 2026-01-26 20:49 PST] You good now?
```

### Why It's Missing Group Info

The log format is controlled by the **envelope formatting** system:

**Location**: Clawdbot core SDK → `channel.reply.formatAgentEnvelope()`

```typescript
const body = core.channel.reply.formatAgentEnvelope({
  channel: "BlueBubbles",
  from: fromLabel,           // Only sender name, not group context
  timestamp: message.timestamp,
  previousTimestamp,
  envelope: envelopeOptions,
  body: baseBody
});
```

The `fromLabel` for groups is `undefined`:

```typescript
const fromLabel = isGroup ? undefined : message.senderName || `user:${message.senderId}`;
```

This means the envelope formatter doesn't get group context in the `from` field.

---

## 6. Where Group Context IS Available

### Internal Fields (Used for Logic)

✅ **Available in code**:
- `message.isGroup` (boolean)
- `message.chatGuid` (full GUID)
- `message.chatId` (numeric ID)
- `message.chatIdentifier` (identifier string)
- `message.chatName` (group display name)
- `message.participants[]` (array of participant objects)

✅ **Used for**:
- Allowlist matching
- Session routing
- Mention detection
- Outbound message targeting

### Context Payload Fields

✅ **Available to agent** (but not in logs):
- `ChatType: "group" | "direct"`
- `GroupSubject: string` (group name)
- `GroupMembers: string` (formatted participant list)
- `From: string` (includes group ID)

### Verbose Logging

If you enable verbose logging, you'll see:

```
[bluebubbles] msg sender=+14245157194 group=true textLen=15 attachments=0 
chatGuid=iMessage;+;chat660250192681427962 chatId=
```

---

## 7. How to Expose Group Data to Agent

### Option 1: Enhance Envelope Formatting

Modify the `fromLabel` to include group context:

```typescript
// Current:
const fromLabel = isGroup ? undefined : message.senderName || `user:${message.senderId}`;

// Enhanced:
const fromLabel = isGroup 
  ? `${message.senderName || message.senderId} in ${message.chatName || "group"}`
  : message.senderName || `user:${message.senderId}`;
```

### Option 2: Add to Agent Context

Expose group fields directly in the context:

```typescript
const ctxPayload = {
  // ... existing fields ...
  
  // New explicit group fields:
  ChatGuid: message.chatGuid,
  ChatId: message.chatId,
  ChatIdentifier: message.chatIdentifier,
  IsGroup: message.isGroup,
  Participants: message.participants  // Raw array
};
```

### Option 3: Custom Log Prefix

Add group info to the log output:

```typescript
const groupPrefix = isGroup 
  ? `[Group: ${message.chatName || peerId}] `
  : "";

const body = `${groupPrefix}${baseBody}`;
```

---

## 8. Practical Detection in Your Code

### Check if Message is from a Group

```typescript
// In agent context:
if (context.ChatType === "group") {
  // It's a group message
}
```

### Get Group Name

```typescript
const groupName = context.GroupSubject; // e.g., "Family Group Chat"
```

### Get Group Members

```typescript
const members = context.GroupMembers; 
// e.g., "Tyler (+14245157194), Jane (jane@icloud.com)"
```

### Get Group ID for Targeting

```typescript
const groupId = context.From; 
// e.g., "group:iMessage;+;chat660250192681427962"

// Or extract the chatGuid portion:
const chatGuid = context.From.replace(/^group:/, "");
```

---

## 9. Why Group Detection "Works in Theory but Not Practice"

### Theory ✅

- BlueBubbles **sends** all group metadata
- Clawdbot **parses** all group metadata  
- Clawdbot **uses** metadata for routing/security
- Clawdbot **passes** `ChatType`, `GroupSubject`, `GroupMembers` to agent

### Practice ❌

- Log output **doesn't show** group context
- Agent sees: `[iMessage +14245157194 ...]` (looks like DM)
- No visual indication it's a group in the chat history
- Metadata is "hidden" in context fields not displayed in logs

### The Gap

The metadata exists in `ctxPayload` but isn't surfaced in:
1. **Envelope formatting** (the `[iMessage ...]` prefix)
2. **Agent's visible message history**
3. **System event logs** (unless verbose logging is on)

---

## 10. Recommended Fixes

### Immediate: Check Context Fields

In your agent logic, **always check**:

```typescript
if (context.ChatType === "group") {
  console.log(`Group message in: ${context.GroupSubject}`);
  console.log(`From: ${context.SenderName} (${context.SenderId})`);
  console.log(`Members: ${context.GroupMembers}`);
}
```

### Short-term: Add Group Info to Logs

Modify `monitor.ts` → `processMessage()`:

```typescript
const groupInfo = isGroup ? ` [group:${message.chatName || peerId}]` : "";
const fromLabel = isGroup 
  ? `${message.senderName || message.senderId}${groupInfo}`
  : message.senderName || `user:${message.senderId}`;
```

### Long-term: Enhance Agent Context

Add explicit group fields to `ctxPayload`:

```typescript
const ctxPayload = {
  // ... existing fields ...
  
  // Explicit group metadata
  ChatGuid: message.chatGuid,
  ChatId: message.chatId,
  ChatIdentifier: message.chatIdentifier,
  IsGroupChat: message.isGroup,
  ParticipantIds: message.participants?.map(p => p.id),
  ParticipantNames: message.participants?.map(p => p.name).filter(Boolean)
};
```

---

## 11. Summary of Available Fields

| Field | Source | Available in Code | Passed to Agent | Visible in Logs |
|-------|--------|------------------|-----------------|-----------------|
| `isGroup` | Webhook | ✅ Yes | ❌ No (via ChatType) | ❌ No |
| `chatGuid` | Webhook | ✅ Yes | ❌ No | ❌ No |
| `chatId` | Webhook | ✅ Yes | ❌ No | ❌ No |
| `chatIdentifier` | Webhook | ✅ Yes | ❌ No | ❌ No |
| `chatName` | Webhook | ✅ Yes | ✅ Yes (GroupSubject) | ❌ No |
| `participants[]` | Webhook | ✅ Yes | ✅ Yes (GroupMembers) | ❌ No |
| `senderId` | Webhook | ✅ Yes | ✅ Yes (SenderId) | ✅ Yes |
| `senderName` | Webhook | ✅ Yes | ✅ Yes (SenderName) | ❌ No |
| `ChatType` | Derived | ✅ Yes | ✅ Yes | ❌ No |

**Key Insight**: All metadata exists and flows through the system, but most of it is only used internally for routing/security and isn't surfaced in logs or easily accessible to agent logic.

---

## 12. Next Steps

1. **Verify context fields** are accessible in your agent code
2. **Test detection** using `context.ChatType === "group"`
3. **Extract group info** from `GroupSubject` and `GroupMembers`
4. **Optionally modify** envelope formatting to show group context in logs
5. **Consider adding** explicit `ChatGuid` field to agent context for easier targeting

---

## Files Analyzed

- `/opt/homebrew/lib/node_modules/clawdbot/extensions/bluebubbles/src/monitor.ts` (message processing)
- `/opt/homebrew/lib/node_modules/clawdbot/extensions/bluebubbles/src/types.ts` (data structures)
- `/opt/homebrew/lib/node_modules/clawdbot/extensions/bluebubbles/src/targets.ts` (GUID parsing)
- `/opt/homebrew/lib/node_modules/clawdbot/extensions/bluebubbles/src/channel.ts` (plugin configuration)

**Total webhook payload fields extracted**: 20+  
**Fields passed to agent context**: 15+  
**Fields visible in chat logs**: 2-3 (sender, timestamp, body)
