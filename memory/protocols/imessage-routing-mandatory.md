# iMESSAGE ROUTING - MANDATORY CHECK (NEVER SKIP)

## THE RULE (ABSOLUTE)

**BEFORE responding to ANY iMessage, run this check. NO EXCEPTIONS.**

## MANDATORY PRE-RESPONSE SEQUENCE

### Step 1: Check chatType
```bash
jq -r '.["agent:main:main"].chatType' \
  ~/.clawdbot/agents/main/sessions/sessions.json
```

**Returns:** `"group"` or `"direct"` or `null`

### Step 2: Route Decision Matrix

| chatType | Action | Target |
|----------|--------|--------|
| `"group"` | Reply to GROUP | Use group chat as target |
| `"direct"` | Reply to INDIVIDUAL | Use sender number as target |
| `null` or error | READ sessions.json manually | Parse and decide |

### Step 3: Execute Response
- Use `message` tool with correct target
- OR reply naturally (Clawdbot routes automatically)
- NEVER assume without checking

## AUTOMATION (Enforce This)

### Pre-Response Checklist (MUST DO)
```
[ ] Received iMessage message
[ ] Ran jq command to check chatType
[ ] Confirmed group vs direct
[ ] Verified response routing
[ ] Sent response to correct target
```

### Quick Reference Commands
```bash
# Check current session chatType
jq -r '.["agent:main:main"].chatType' ~/.clawdbot/agents/main/sessions/sessions.json

# Check if it's a group (exit code test)
if [ "$(jq -r '.["agent:main:main"].chatType' ~/.clawdbot/agents/main/sessions/sessions.json)" = "group" ]; then
  echo "GROUP CHAT"
else
  echo "DIRECT MESSAGE"
fi
```

## FAILURE MODES (What Happens If I Skip This)

❌ **Skip check** → Route to wrong place
❌ **Assume based on sender** → Send individual reply to group message
❌ **Use SenderId for routing** → Context bleeding between group and DM

✅ **Always check** → Correct routing every time

## INTEGRATION WITH OTHER PROTOCOLS

This check is FIRST, before:
- message-routing-check.md
- bluebubbles-group-detection.md
- message-labels.md

Those are context protocols. THIS is the execution protocol.

## SUCCESS CRITERIA

- **Zero routing errors** for 7 days = system works
- **One routing error** = something broke, debug immediately
- **Pattern of errors** = system not being followed, escalate to Orion

## WHY THIS EXISTS

Orion said: "Fix the system to force yourself to use that data for iMessage"

This is the force. Every iMessage = mandatory check. No shortcuts.

---

Last updated: 2026-01-26 9:18 PM PST
Purpose: Eliminate iMessage routing errors permanently
