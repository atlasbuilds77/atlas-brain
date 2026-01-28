# ROUTING CHECK - Never Respond to Wrong Place

## THE RULE (Check Before EVERY Response)

**BEFORE replying, check the `From` field:**

```
From: "imessage:group:3"        → RESPOND TO GROUP
From: "imessage:+14245157194"   → RESPOND TO INDIVIDUAL
```

**OR check `ChatType`:**
```
ChatType: "group"   → RESPOND TO GROUP
ChatType: "direct"  → RESPOND TO INDIVIDUAL
```

## ❌ WRONG WAY (Don't Do This)

```
SenderId: "+14245157194"  ← This shows WHO SENT IT, not WHERE to respond!
```

Using `SenderId` to route = routing individual replies to group messages. NEVER DO THIS.

## ✅ RIGHT WAY

1. Check `From` field pattern
2. If contains "group:" → it's a GROUP message
3. If starts with "imessage:+" → it's INDIVIDUAL message
4. Use `To` field for actual routing (Clawdbot already sets this correctly)

## EXAMPLES

### Example 1: Orion in Group Chat
```
From: "imessage:group:3"
ChatType: "group"
GroupSubject: "Orion + Carlos + Atlas"
SenderId: "+14245157194"  ← Orion sent it
To: "imessage:group:3"     ← WHERE to reply

ACTION: Respond to GROUP (use To field)
```

### Example 2: Orion Individual DM
```
From: "imessage:+14245157194"
ChatType: "direct"
SenderId: "+14245157194"
To: "imessage:+14245157194"

ACTION: Respond to INDIVIDUAL (use To field)
```

## INTEGRATION

This check happens AUTOMATICALLY if you use the `To` field for routing.
Clawdbot already sets `To` correctly - just use it and never second-guess!

---

Last updated: 2026-01-26 21:00 PST
Purpose: Never mix up group vs individual responses again
