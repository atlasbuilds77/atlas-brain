# Practical Example: Using chatType in Agent Logic

## Scenario: Different behavior for group vs direct chats

An agent might want to respond differently based on whether it's in a group chat or direct message.

---

## Example 1: Check chatType Before Responding

### Agent Logic (Pseudocode)
```typescript
async function handleMessage(message: string, sessionKey: string) {
  // Get the chat type
  const chatType = await getChatType(sessionKey);
  
  if (chatType === 'group') {
    // In group chats, be more concise and formal
    return generateGroupResponse(message);
  } else {
    // In direct chats, be more detailed and conversational
    return generateDirectResponse(message);
  }
}

async function getChatType(sessionKey: string): Promise<string> {
  const result = await exec(`
    jq -r '.["${sessionKey}"].chatType' \
      ~/.clawdbot/agents/main/sessions/sessions.json
  `);
  return result.trim();
}
```

---

## Example 2: Conditional Tool Usage

### Use Case: Only use certain tools in direct chats

```xml
<!-- Step 1: Check chat type -->
<invoke name="exec">
  <parameter name="command">
    jq -r '.["agent:main:main"].chatType' \
      ~/.clawdbot/agents/main/sessions/sessions.json
  </parameter>
</invoke>

<!-- Response: "direct" -->

<!-- Step 2: Conditional logic based on response -->
<!-- If chatType is "direct", allow screenshot sharing -->
<invoke name="nodes">
  <parameter name="action">camera_snap</parameter>
  <parameter name="facing">front</parameter>
</invoke>

<!-- If chatType is "group", skip sensitive actions -->
```

---

## Example 3: Session Metadata Dashboard

### Command to view current session context
```bash
#!/bin/bash
# show-session-context.sh

SESSION_KEY="agent:main:main"

echo "=== Current Session Context ==="
jq --arg k "$SESSION_KEY" '
  .[$k] | {
    chatType,
    channel,
    sessionId,
    model,
    totalTokens,
    lastChannel,
    updatedAt: (.updatedAt / 1000 | strftime("%Y-%m-%d %H:%M:%S"))
  }
' ~/.clawdbot/agents/main/sessions/sessions.json
```

### Output:
```json
{
  "chatType": "direct",
  "channel": "imessage",
  "sessionId": "356267eb-e1ee-415b-956e-d10e9adf4449",
  "model": "claude-sonnet-4-5",
  "totalTokens": 65219,
  "lastChannel": "imessage",
  "updatedAt": "2026-01-26 12:34:45"
}
```

---

## Example 4: Multi-Session Analysis

### Find all active group chats in the last hour

```bash
#!/bin/bash
# active-group-chats.sh

# Get timestamp for 1 hour ago
ONE_HOUR_AGO=$(($(date +%s) * 1000 - 3600000))

echo "Active group chats in last hour:"
jq -r --arg ts "$ONE_HOUR_AGO" '
  to_entries[] 
  | select(
      .value.chatType == "group" and 
      .value.updatedAt > ($ts | tonumber)
    )
  | "\(.key) - \(.value.channel) - \(.value.displayName // "unnamed")"
' ~/.clawdbot/agents/main/sessions/sessions.json
```

---

## Example 5: Smart Greeting Based on Context

### Agent startup greeting that adapts to chat type

```typescript
async function generateGreeting(sessionKey: string): Promise<string> {
  // Get session metadata
  const metadata = await exec(`
    jq --arg k "${sessionKey}" \
      '.[$k] | {chatType, channel, groupId}' \
      ~/.clawdbot/agents/main/sessions/sessions.json
  `);
  
  const session = JSON.parse(metadata);
  
  if (session.chatType === 'group') {
    return `👋 Hello everyone! I'm here to help the group.`;
  } else if (session.channel === 'telegram') {
    return `Hey! Ready to assist you via Telegram.`;
  } else if (session.channel === 'imessage') {
    return `Hi! What can I help you with today?`;
  } else {
    return `Hello! How can I assist you?`;
  }
}
```

---

## Example 6: Permission Check

### Restrict sensitive commands to direct chats only

```typescript
async function canExecuteSensitiveCommand(sessionKey: string): Promise<boolean> {
  const chatType = await exec(`
    jq -r '.["${sessionKey}"].chatType' \
      ~/.clawdbot/agents/main/sessions/sessions.json
  `).then(r => r.trim());
  
  // Only allow in direct chats
  return chatType === 'direct';
}

async function handleCommand(command: string, sessionKey: string) {
  if (command === '/screenshot' || command === '/location') {
    const allowed = await canExecuteSensitiveCommand(sessionKey);
    
    if (!allowed) {
      return "⚠️ This command is only available in direct messages for privacy reasons.";
    }
    
    // Execute sensitive command
    return executeSensitiveCommand(command);
  }
  
  // Execute normal command
  return executeCommand(command);
}
```

---

## Example 7: Logging with Context

### Enhanced logging that includes session metadata

```typescript
async function logMessage(level: string, message: string, sessionKey: string) {
  // Get session context
  const metadata = await exec(`
    jq -r --arg k "${sessionKey}" \
      '.[$k] | "\(.chatType):\(.channel)"' \
      ~/.clawdbot/agents/main/sessions/sessions.json
  `).then(r => r.trim());
  
  const [chatType, channel] = metadata.split(':');
  
  // Log with context
  console.log(JSON.stringify({
    timestamp: new Date().toISOString(),
    level,
    message,
    session: {
      key: sessionKey,
      chatType,
      channel
    }
  }));
}

// Usage
await logMessage('info', 'User requested screenshot', 'agent:main:main');
// Output: {"timestamp":"2026-01-26T20:34:45.000Z","level":"info","message":"User requested screenshot","session":{"key":"agent:main:main","chatType":"direct","channel":"imessage"}}
```

---

## Summary

**Common Use Cases:**
1. ✅ Conditional responses (verbose vs concise)
2. ✅ Permission checks (direct-only features)
3. ✅ UI customization (group vs DM behavior)
4. ✅ Analytics & logging
5. ✅ Rate limiting per chat type
6. ✅ Feature flags by channel

**Key Pattern:**
```bash
# Always start with this query
CHAT_TYPE=$(jq -r '.["$SESSION_KEY"].chatType' \
  ~/.clawdbot/agents/main/sessions/sessions.json)

# Then branch logic
case "$CHAT_TYPE" in
  group)   handle_group_logic ;;
  direct)  handle_direct_logic ;;
  *)       handle_unknown ;;
esac
```

---

**Files:**
- Full solution: `memory/tool-based-metadata-solution.md`
- Quick reference: `memory/chatType-access-quick-reference.md`
- Test script: `memory/tool-based-metadata-solution-test.sh`
