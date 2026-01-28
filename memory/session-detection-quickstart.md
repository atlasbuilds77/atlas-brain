# Session Detection - Quick Start Guide

**Problem:** Need to know which session (group vs direct) you're currently responding in.

**Solution:** Use `detect-active-session-final.sh`

---

## Usage

### Method 1: Direct Execution

```bash
$ ./scripts/detect-active-session-final.sh
SESSION_KEY=agent:main:imessage:group:10
CHAT_TYPE=group
DELIVERY_TARGET=chat_id:10
GROUP_ID=10
```

### Method 2: Source Variables

```bash
# Export variables to current shell
$ eval "$(./scripts/detect-active-session-final.sh --export)"

# Now use them:
$ echo "Replying to: $CHAT_TYPE"
Replying to: group

$ echo "Session: $SESSION_KEY"
Session: agent:main:imessage:group:10
```

### Method 3: Inline in Scripts

```bash
#!/bin/bash
# Get current session
eval "$(~/clawd/scripts/detect-active-session-final.sh --export)"

if [ "$CHAT_TYPE" = "group" ]; then
  echo "This is a group chat (id: $GROUP_ID)"
  # Do group-specific logic
else
  echo "This is a direct message"
  # Do DM-specific logic
fi

# Access full session data
jq --arg key "$SESSION_KEY" '.[$key]' \
  ~/.clawdbot/agents/main/sessions/sessions.json
```

---

## Variables Exported

| Variable | Example | Description |
|----------|---------|-------------|
| `SESSION_KEY` | `agent:main:imessage:group:10` | Full session key |
| `CHAT_TYPE` | `group` or `direct` | Type of chat |
| `DELIVERY_TARGET` | `chat_id:10` | Where replies go |
| `GROUP_ID` | `10` | Group ID (groups only) |

---

## How It Works

1. **Scans all non-subagent sessions**
2. **Finds most recent user message** across all sessions
3. **Parses the message envelope** (e.g., `[iMessage Group id:10 ...]`)
4. **Determines session type** from envelope content
5. **Returns session metadata**

**Key Insight:** Uses the actual message timestamp, NOT the session `updatedAt` (which gets modified by subagent spawns).

---

## Files

- **Script:** `~/clawd/scripts/detect-active-session-final.sh`
- **Documentation:** `memory/detect-active-session-final.md`
- **Sessions Data:** `~/.clawdbot/agents/main/sessions/sessions.json`

---

## Example Integration

```bash
#!/bin/bash
# example-routing-script.sh

# Detect current session
eval "$(~/clawd/scripts/detect-active-session-final.sh --export)"

echo "=== Current Session ==="
echo "Key: $SESSION_KEY"
echo "Type: $CHAT_TYPE"
echo "Target: $DELIVERY_TARGET"

# Check session-specific data
if [ "$CHAT_TYPE" = "group" ]; then
  echo "Group ID: $GROUP_ID"
  echo ""
  echo "=== Group Session Data ==="
  jq --arg key "$SESSION_KEY" '.[$key] | {
    displayName,
    groupId,
    channel,
    chatType,
    deliveryContext
  }' ~/.clawdbot/agents/main/sessions/sessions.json
else
  echo ""
  echo "=== Direct Message Session Data ==="
  jq --arg key "$SESSION_KEY" '.[$key] | {
    displayName,
    channel,
    chatType,
    deliveryContext
  }' ~/.clawdbot/agents/main/sessions/sessions.json
fi
```

---

**Last Updated:** 2026-01-27  
**Status:** ✅ Production Ready
