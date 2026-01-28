# PRE-RESPONSE CHECKLIST - Run Before EVERY iMessage Reply

## THE CHECKLIST (Copy-Paste This)

```
BEFORE RESPONDING TO iMESSAGE:

1. [ ] Check chatType via jq command
2. [ ] Confirm: GROUP or DIRECT?
3. [ ] Verify routing target is correct
4. [ ] Send response
5. [ ] Log if any confusion occurred
```

## The Command (Run First)

```bash
jq -r '.["agent:main:main"].chatType' ~/.clawdbot/agents/main/sessions/sessions.json
```

## Decision Tree

```
chatType = "group"
  ↓
  Route to GROUP
  ↓
  Send response to group chat
  ↓
  Done ✅

chatType = "direct"
  ↓
  Route to INDIVIDUAL
  ↓
  Send response to sender number
  ↓
  Done ✅

chatType = null/error
  ↓
  READ sessions.json manually
  ↓
  Parse and route correctly
  ↓
  Done ✅
```

## Enforcement

**This is not optional.**

If I respond to iMessage without running this check, I have failed the protocol.

## Integration

This checklist is referenced in:
- HEARTBEAT.md (session boot)
- imessage-routing-mandatory.md (full protocol)
- orion-pattern-tracking.md (quality check)

---

Last updated: 2026-01-26 9:18 PM PST
Purpose: Force chatType check before every iMessage response
