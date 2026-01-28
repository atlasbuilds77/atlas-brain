# Heartbeat Routing Protocol

**Created:** 2026-01-27
**Purpose:** Prevent broadcasting position checks/internal tasks to wrong people

---

## CRITICAL RULE: HEARTBEAT RESPONSES

When system sends heartbeat tasks (position checks, token monitor, Twitter engagement, etc.):

### DEFAULT RESPONSE:
```
HEARTBEAT_OK
```

**THAT'S IT.** No details. No position reports. Nothing.

---

## EXCEPTIONS (When to Include Details)

### ✅ Send position details ONLY if:
1. **Orion (+14245157194) explicitly asks** for position update
2. **Aphmas** needs stock position info (when relevant to his work)
3. **Something actually needs attention** (critical alert)

### ❌ NEVER send to:
- Laura (+12242906904)
- Carlos (+16195779919)
- Anyone else in conversations
- Group chats (unless explicitly asked)

---

## WHY THIS MATTERS

**What was happening:**
- System heartbeat triggers (every X minutes)
- I respond with full position check, token monitor, Twitter updates
- That response goes to WHOEVER is in the active conversation
- Laura saw trading positions she doesn't need to see

**What should happen:**
- System heartbeat triggers
- I check positions internally
- Respond with "HEARTBEAT_OK" (nothing needs attention)
- OR respond with specific alert if something is urgent

---

## ROUTING GUIDE

| Message Type | Send To | Format |
|--------------|---------|--------|
| Heartbeat (nothing urgent) | No one | HEARTBEAT_OK |
| Position alert | Orion only | Brief alert text |
| Stock positions | Orion + Aphmas | When relevant |
| Trading updates | Orion only | When asked |
| Everything else | Context-appropriate | Normal routing |

---

## IMPLEMENTATION

**Before responding to system heartbeat:**
1. Check: Is there an actual alert?
2. If yes → Send brief alert to Orion
3. If no → Reply "HEARTBEAT_OK" and move on

**DO NOT:**
- Broadcast position checks to everyone
- Send trading info to non-trading people
- Dump internal task results into random conversations

---

*This protocol is PERMANENT. Read it every session start.*
