# Session Access Quick Reference

**Date:** 2026-01-27  
**Purpose:** Quick reference for accessing session.chatType and deliveryContext

---

## TL;DR

**There is no `session` object at runtime.**

Access session metadata via:
```bash
# Fastest: Direct file read
jq -r '.["agent:main:main"].chatType' \
  ~/.clawdbot/agents/main/sessions/sessions.json
# Returns: "direct" or "group"

# Get routing target
jq -r '.["agent:main:main"].deliveryContext.to' \
  ~/.clawdbot/agents/main/sessions/sessions.json
# Returns: "imessage:+14245157194" or "chat_id:3"
```

---

## Three Methods to Access Session Data

### Method 1: Direct File Access (Recommended for quick checks)
```bash
SESSION_KEY="agent:main:main"
CHAT_TYPE=$(jq -r --arg key "$SESSION_KEY" \
  '.[$key].chatType' \
  ~/.clawdbot/agents/main/sessions/sessions.json)

REPLY_TO=$(jq -r --arg key "$SESSION_KEY" \
  '.[$key].deliveryContext.to' \
  ~/.clawdbot/agents/main/sessions/sessions.json)
```

### Method 2: sessions_list Tool (Official API)
```xml
<invoke name="sessions_list">
  <parameter name="limit">10</parameter>
</invoke>
```

Response includes `kind` (chatType) and `deliveryContext`.

### Method 3: Parse Session Key (Heuristic)
```javascript
// Fast but not 100% accurate
const isGroup = sessionKey.includes(':group:');
const chatType = isGroup ? 'group' : 'direct';
```

---

## Session Key Patterns

```
agent:main:main                      → Direct message
agent:main:imessage:group:3          → iMessage group
agent:main:telegram:group:-10035...  → Telegram group
agent:main:subagent:uuid             → Subagent
```

---

## Common Fields

| Field | Location | Example Value |
|-------|----------|---------------|
| chatType | `sessions.json` | `"direct"` or `"group"` |
| deliveryContext.to | `sessions.json` | `"imessage:+14245157194"` |
| deliveryContext.channel | `sessions.json` | `"imessage"` |
| origin.chatType | `sessions.json` | `"group"` |
| kind | `sessions --json` output | `"direct"` or `"group"` |

---

## Where Data Lives

1. **Storage:** `~/.clawdbot/agents/main/sessions/sessions.json`
2. **CLI:** `clawdbot sessions --json`
3. **Tools:** `sessions_list`, `session_status`
4. **NOT in:** Runtime variables, environment variables, session object

---

## Example: Full Session Entry

```json
{
  "agent:main:imessage:group:3": {
    "chatType": "group",
    "channel": "imessage",
    "groupId": "3",
    "sessionId": "68fd7af5-...",
    "deliveryContext": {
      "channel": "imessage",
      "to": "chat_id:3"
    },
    "origin": {
      "chatType": "group",
      "from": "imessage:group:3",
      "to": "chat_id:3",
      "provider": "imessage"
    },
    "displayName": "imessage:g-3",
    "model": "claude-sonnet-4-5",
    "totalTokens": 12345
  }
}
```

---

## Full Documentation

See `memory/session-object-access-method.md` for complete details.
