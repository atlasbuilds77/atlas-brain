# Clawdbot Context Injection Analysis

**Date:** 2026-01-26  
**Issue:** Agent can't see From/ChatType/GroupSubject fields as template variables  
**Finding:** These fields exist in the system but are NOT template variables—they're programmatically processed

---

## Summary

Clawdbot does NOT use template variables like `{{From}}`, `{{ChatType}}`, or `{{GroupSubject}}`. Instead:

1. **Channel plugins** populate context fields
2. **Context processors** transform these fields into natural language
3. **System prompt builder** injects the transformed text into the agent prompt

The fields exist in the message context object but are never exposed as raw template variables to the agent.

---

## Context Injection Flow

### 1. Channel Plugin Populates Context
**File:** `/opt/homebrew/lib/node_modules/clawdbot/dist/imessage/monitor/monitor-provider.js`  
**Lines:** ~365-395

When a message arrives, the BlueBubbles/iMessage monitor creates a context payload:

```javascript
const ctxPayload = finalizeInboundContext({
    Body: combinedBody,
    RawBody: bodyText,
    CommandBody: bodyText,
    From: isGroup ? `imessage:group:${chatId ?? "unknown"}` : `imessage:${sender}`,
    To: imessageTo,
    SessionKey: route.sessionKey,
    AccountId: route.accountId,
    ChatType: isGroup ? "group" : "direct",                    // ✅ ChatType set here
    ConversationLabel: fromLabel,
    GroupSubject: isGroup ? (message.chat_name ?? undefined) : undefined,  // ✅ GroupSubject set here
    GroupMembers: isGroup ? (message.participants ?? []).filter(Boolean).join(", ") : undefined,
    SenderName: senderNormalized,
    SenderId: sender,
    Provider: "imessage",
    Surface: "imessage",
    MessageSid: message.id ? String(message.id) : undefined,
    // ... more fields
});
```

**Key Fields:**
- `From`: Channel-specific identifier (e.g., `imessage:group:123` or `imessage:+15551234567`)
- `ChatType`: "group" or "direct"
- `GroupSubject`: Group chat name (only for groups)
- `GroupMembers`: Comma-separated participant list
- `SenderName`: Normalized sender handle
- `SenderId`: Raw sender identifier

---

### 2. Context Finalization
**File:** `/opt/homebrew/lib/node_modules/clawdbot/dist/auto-reply/reply/inbound-context.js`  
**Function:** `finalizeInboundContext()`

This function normalizes the context fields but does NOT expose them as template variables:
- Normalizes `ChatType` to "group"/"direct"/"channel"
- Ensures `ConversationLabel` is set
- Formats sender metadata into the body text

---

### 3. Group Context Building
**File:** `/opt/homebrew/lib/node_modules/clawdbot/dist/auto-reply/reply/groups.js`  
**Function:** `buildGroupIntro()`  
**Lines:** ~47-91

This is where `GroupSubject` gets transformed into natural language:

```javascript
export function buildGroupIntro(params) {
    const activation = normalizeGroupActivation(params.sessionEntry?.groupActivation) ?? params.defaultActivation;
    const subject = params.sessionCtx.GroupSubject?.trim();  // ✅ Uses GroupSubject
    const members = params.sessionCtx.GroupMembers?.trim();
    const rawProvider = params.sessionCtx.Provider?.trim();
    
    // Build natural language intro
    const subjectLine = subject
        ? `You are replying inside the ${providerLabel} group "${subject}".`
        : `You are replying inside a ${providerLabel} group chat.`;
    
    const membersLine = members ? `Group members: ${members}.` : undefined;
    
    const activationLine = activation === "always"
        ? "Activation: always-on (you receive every group message)."
        : "Activation: trigger-only (you are invoked only when explicitly mentioned; recent context may be included).";
    
    // ... more context building
    
    return [
        subjectLine,
        membersLine,
        activationLine,
        // ... more lines
    ].filter(Boolean).join(" ");
}
```

**Output Example:**
```
You are replying inside the iMessage group "Family Chat". 
Group members: Alice, Bob, Charlie. 
Activation: trigger-only (you are invoked only when explicitly mentioned; recent context may be included). 
Be a good group participant: mostly lurk and follow the conversation; reply only when directly addressed or you can add clear value.
```

---

### 4. Extra System Prompt Assembly
**File:** `/opt/homebrew/lib/node_modules/clawdbot/dist/auto-reply/reply/get-reply-run.js`  
**Lines:** ~37-46

The group intro and any custom group system prompt are combined:

```javascript
const shouldInjectGroupIntro = Boolean(
    isGroupChat && 
    (isFirstTurnInSession || sessionEntry?.groupActivationNeedsSystemIntro)
);

const groupIntro = shouldInjectGroupIntro
    ? buildGroupIntro({
        cfg,
        sessionCtx,          // ✅ Contains GroupSubject, ChatType, etc.
        sessionEntry,
        defaultActivation,
        silentToken: SILENT_REPLY_TOKEN,
    })
    : "";

const groupSystemPrompt = sessionCtx.GroupSystemPrompt?.trim() ?? "";
const extraSystemPrompt = [groupIntro, groupSystemPrompt].filter(Boolean).join("\n\n");
```

This `extraSystemPrompt` is passed to the agent runner.

---

### 5. System Prompt Injection
**File:** `/opt/homebrew/lib/node_modules/clawdbot/dist/agents/system-prompt.js`  
**Function:** `buildAgentSystemPrompt()`  
**Lines:** ~200+

The `extraSystemPrompt` is injected into the final system prompt:

```javascript
if (extraSystemPrompt) {
    // Use "Subagent Context" header for minimal mode (subagents), 
    // otherwise "Group Chat Context"
    const contextHeader = promptMode === "minimal" 
        ? "## Subagent Context" 
        : "## Group Chat Context";
    
    lines.push(contextHeader, extraSystemPrompt, "");
}
```

**Final System Prompt Section:**
```markdown
## Group Chat Context
You are replying inside the iMessage group "Family Chat". Group members: Alice, Bob, Charlie. Activation: trigger-only (you are invoked only when explicitly mentioned; recent context may be included). Be a good group participant: mostly lurk and follow the conversation; reply only when directly addressed or you can add clear value.
```

---

## Key Findings

### ✅ What Exists
- **Context Fields:** From, ChatType, GroupSubject, GroupMembers, SenderName, SenderId, etc.
- **Programmatic Use:** These fields are used to build natural language context
- **Injection Point:** `extraSystemPrompt` parameter in `buildAgentSystemPrompt()`

### ❌ What Does NOT Exist
- **Template Variables:** No `{{From}}`, `{{ChatType}}`, `{{GroupSubject}}` syntax
- **Raw Field Exposure:** The agent never sees the raw context fields directly
- **Custom Template Engine:** No string interpolation or template processing

---

## Why the Agent Can't See These Fields

The fields like `From`, `ChatType`, and `GroupSubject` are **internal routing and context metadata**. They are:

1. **Consumed by builders** (like `buildGroupIntro()`) to generate human-readable context
2. **Never directly serialized** into the system prompt as key-value pairs
3. **Transformed before injection** into natural language descriptions

The agent sees:
```
You are replying inside the iMessage group "Family Chat".
```

The agent does NOT see:
```
From: imessage:group:123456
ChatType: group
GroupSubject: Family Chat
```

---

## How to Access Context Fields

If you want the agent to have access to specific context fields, you would need to:

### Option 1: Modify `buildGroupIntro()`
Add explicit field reporting:
```javascript
const debugLine = `[Debug: From=${params.sessionCtx.From}, ChatType=${params.sessionCtx.ChatType}]`;
```

### Option 2: Custom `extraSystemPrompt`
Set `GroupSystemPrompt` in the session context or config:
```javascript
sessionCtx.GroupSystemPrompt = `
Context Metadata:
- From: ${sessionCtx.From}
- ChatType: ${sessionCtx.ChatType}
- GroupSubject: ${sessionCtx.GroupSubject}
`;
```

### Option 3: Modify Plugin Context
In the channel plugin, add fields to `Body` or `BodyForAgent`:
```javascript
const contextPrefix = `[From: ${ctxPayload.From} | Type: ${ctxPayload.ChatType}]`;
normalized.BodyForAgent = `${contextPrefix}\n\n${normalized.Body}`;
```

---

## Plugin-Specific Context Variables

Each channel plugin can add custom context fields. For BlueBubbles/iMessage:

**File:** `/opt/homebrew/lib/node_modules/clawdbot/dist/imessage/monitor/monitor-provider.js`

### Standard Fields
- `From`, `To`, `SessionKey`, `AccountId`
- `ChatType`, `ConversationLabel`, `Provider`, `Surface`

### iMessage-Specific Fields
- `GroupSubject`: Chat name (groups only)
- `GroupMembers`: Participant list (groups only)
- `SenderName`: Normalized sender handle
- `SenderId`: Raw sender identifier
- `MessageSid`: Message ID
- `ReplyToId`, `ReplyToBody`, `ReplyToSender`: Reply context
- `MediaPath`, `MediaType`, `MediaUrl`: Attachment metadata
- `MediaPaths`, `MediaTypes`, `MediaUrls`: Multi-image support
- `MediaRemoteHost`: Remote SSH host for media access
- `WasMentioned`: Whether agent was mentioned
- `CommandAuthorized`: Whether sender is authorized for commands

### Other Plugin Fields (Examples)
- **Discord:** `ThreadStarterBody`, `GroupChannel`, `GroupSpace`
- **Slack:** `ThreadId`, `ThreadTimestamp`
- **Signal:** `GroupId`, `GroupName`
- **WhatsApp:** `ChatIdentifier`, `GroupGuid`

---

## Injection Mechanism Summary

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. Channel Plugin (imessage/monitor-provider.js)               │
│    - Receives message from BlueBubbles                          │
│    - Creates ctxPayload with From, ChatType, GroupSubject, etc.│
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. Context Finalization (inbound-context.js)                   │
│    - Normalizes ChatType                                        │
│    - Formats sender metadata into Body                          │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. Group Context Builder (groups.js)                           │
│    - Reads GroupSubject, GroupMembers from sessionCtx          │
│    - Builds natural language intro                             │
│    - Returns: "You are replying inside the iMessage group..."  │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. Extra System Prompt Assembly (get-reply-run.js)             │
│    - Combines groupIntro + groupSystemPrompt                   │
│    - Creates extraSystemPrompt variable                        │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. System Prompt Builder (system-prompt.js)                    │
│    - Receives extraSystemPrompt parameter                      │
│    - Injects under "## Group Chat Context" header             │
│    - Returns full system prompt string                         │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. Agent Execution                                              │
│    - Agent sees final system prompt with natural language      │
│    - No access to raw context fields                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Conclusion

**The Problem:** Agent cannot see From/ChatType/GroupSubject fields

**The Reason:** These fields are internal metadata, not exposed as template variables

**The Solution:** They are transformed into natural language context via:
1. `buildGroupIntro()` for group chats
2. `formatInboundEnvelope()` for message body formatting
3. `extraSystemPrompt` injection into system prompt

**Current Behavior:** Working as designed—context is injected as human-readable text, not raw key-value pairs

**To Change:** Would require modifying `buildGroupIntro()`, `buildAgentSystemPrompt()`, or the channel plugin's context builder to explicitly serialize these fields.

---

## Files to Modify (If Needed)

1. **Group context injection:**  
   `/opt/homebrew/lib/node_modules/clawdbot/dist/auto-reply/reply/groups.js`

2. **System prompt builder:**  
   `/opt/homebrew/lib/node_modules/clawdbot/dist/agents/system-prompt.js`

3. **Channel plugin (iMessage):**  
   `/opt/homebrew/lib/node_modules/clawdbot/dist/imessage/monitor/monitor-provider.js`

4. **Context finalization:**  
   `/opt/homebrew/lib/node_modules/clawdbot/dist/auto-reply/reply/inbound-context.js`

---

**Analysis Complete:** 2026-01-26 21:05 PST
