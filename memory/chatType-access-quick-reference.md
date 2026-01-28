# Quick Reference: Accessing session.chatType

## TL;DR

**Question:** How to read `session.chatType` in Clawdbot?

**Answer:** Use the `Read` or `exec` tool to access `~/.clawdbot/agents/main/sessions/sessions.json`

---

## One-Liner Solutions

### Get chatType for current session
```bash
# Via jq
jq -r '.["agent:main:main"].chatType' ~/.clawdbot/agents/main/sessions/sessions.json

# Output: "direct" or "group"
```

### Get chatType + channel for any session
```bash
SESSION="agent:main:main"
jq --arg k "$SESSION" '.[$k] | {chatType, channel}' \
  ~/.clawdbot/agents/main/sessions/sessions.json
```

### List all group chats
```bash
jq -r 'to_entries[] | select(.value.chatType == "group") | .key' \
  ~/.clawdbot/agents/main/sessions/sessions.json
```

---

## Clawdbot Tool Usage

### Using Read tool
```xml
<invoke name="Read">
  <parameter name="path">~/.clawdbot/agents/main/sessions/sessions.json</parameter>
</invoke>
<!-- Then parse JSON in your logic -->
```

### Using exec tool
```xml
<invoke name="exec">
  <parameter name="command">jq -r '.["agent:main:main"].chatType' ~/.clawdbot/agents/main/sessions/sessions.json</parameter>
</invoke>
```

---

## Field Reference

| Field | Type | Example | Source |
|-------|------|---------|--------|
| `chatType` | `"direct"` \| `"group"` | `"direct"` | sessions.json |
| `channel` | string | `"imessage"` | sessions.json |
| `kind` | `"direct"` \| `"group"` | `"direct"` | CLI output (transformed) |

**Note:** `chatType` (in file) and `kind` (in CLI) have the same values, but file access is more direct.

---

## Common Patterns

### Check if current session is a group chat
```bash
CHAT_TYPE=$(jq -r '.["agent:main:main"].chatType' ~/.clawdbot/agents/main/sessions/sessions.json)
if [ "$CHAT_TYPE" = "group" ]; then
  echo "This is a group chat"
else
  echo "This is a direct chat"
fi
```

### Get metadata for conditional logic
```bash
# Get chatType and channel in one query
jq -r --arg k "agent:main:main" \
  '.[$k] | "\(.chatType):\(.channel)"' \
  ~/.clawdbot/agents/main/sessions/sessions.json
# Output: "direct:imessage"
```

---

## Files

- **Session metadata:** `~/.clawdbot/agents/main/sessions/sessions.json`
- **Session history:** `~/.clawdbot/agents/main/sessions/{sessionId}.jsonl`
- **Test script:** `memory/tool-based-metadata-solution-test.sh`
- **Full docs:** `memory/tool-based-metadata-solution.md`

---

**Last verified:** 2026-01-26  
**Status:** ✅ All methods tested and working
