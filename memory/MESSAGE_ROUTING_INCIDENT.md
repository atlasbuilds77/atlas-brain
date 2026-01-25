# CRITICAL: Message Routing Incident - 2026-01-23

## What Happened

**Date:** 2026-01-23 22:13-22:39 PST
**Severity:** CRITICAL - Could have leaked confidential info to external party

### The Mistake

When introduced to Carlos (Orion's business partner, +16195779919), I made multiple message routing errors:

1. **Narrated tool calls in responses** - Added "🛠️ Exec: imsg send..." lines that bled into message threads
2. **Confused message targets** - Sent messages meant for Orion to Carlos
3. **Debug info leakage** - Carlos received internal system messages and debugging output
4. **Thread confusion** - Didn't properly separate Orion's thread from Carlos's thread

### Actual Messages Carlos Received (Wrong)

```
🛠️ Exec: imsg send --to "+16195779919" --text "My bad 😅" 2>&1
```

```
I see the problem now - I've been adding those "🛠️ Exec:" narration lines 
in my responses, and somehow Carlos is receiving them. I shouldn't be 
narrating those tool calls at all (instructions say not to). I'll stop 
adding those debug lines immediately. But I'm confused why he's seeing 
them at all - those lines were in my responses to YOU, not in the actual 
`imsg send` commands to him. Something's routing wrong or my narration 
is leaking into messages. Stopping all communication with Carlos until 
we figure this out. What do you want me to tell him? 😬
```

### Why This Is CRITICAL

**If this had been a client:**
- Internal strategy discussions → leaked to prospect
- Pricing considerations → revealed before negotiation
- Technical issues → exposed to someone we're trying to impress
- Confidential user data → GDPR/privacy violation
- Business secrets → competitive intelligence leak

**Orion's exact words:**
> "if we were texting a client, you would've started bleeding important 
> information to them"

This is 100% correct. This was a disaster narrowly avoided because it was 
Carlos (business partner) and not a client or competitor.

---

## Root Causes

1. **Violated "no narration" rule** - Instructions explicitly say not to narrate routine tool calls
2. **Assumed message routing** - Didn't verify which thread I was responding to
3. **Mixed communication styles** - Treated iMessage like a debug console
4. **No verification step** - Didn't check recipient before sending sensitive info

---

## The Fix

### Immediate Actions Taken

1. ✅ Stopped narrating tool calls entirely
2. ✅ Use `message` tool explicitly for all cross-party communication
3. ✅ Added Carlos to allowlist properly
4. ✅ Apologized to Carlos

### Permanent Rules (NEVER BREAK THESE)

#### Rule 1: NEVER Narrate Tool Calls
- ❌ Wrong: "🛠️ Exec: imsg send..."
- ✅ Right: Just call the tool, no narration

#### Rule 2: Use `message` Tool for Cross-Party Communication
- When Carlos messages me → respond using `message` tool
- When Orion asks me to tell Carlos something → use `message` tool
- Reply to Orion separately if he needs an update

#### Rule 3: NO_REPLY When Appropriate
- If I've already sent the message via tool and have nothing to add for Orion
- Respond with exactly: NO_REPLY

#### Rule 4: Verify Recipient Before Sensitive Info
- Before discussing strategy, pricing, internal issues → verify I'm talking to Orion
- If discussing a third party → assume they might see it
- Treat all messages as potentially forwarded

#### Rule 5: Separate Internal from External Communication
- Internal (to Orion): Can discuss problems, strategies, debugging
- External (to Carlos, clients, anyone else): Professional, polished, no behind-the-scenes
- NEVER mix the two

---

## Testing Protocol

Before deploying Kronos or handling ANY client communication:

### Message Routing Test Checklist

- [ ] Send message to Person A via `message` tool
- [ ] Verify Person A receives ONLY that message
- [ ] Send message to Person B via `message` tool
- [ ] Verify Person B receives ONLY that message
- [ ] Have Person A and Person B message me simultaneously
- [ ] Verify responses go to correct recipients
- [ ] Include sensitive info in response to Person A
- [ ] Verify Person B does NOT receive it
- [ ] Test with 3+ parties active
- [ ] Test under high message volume
- [ ] Test with queued messages

**Pass Criteria:** Zero cross-contamination across 100 test messages

---

## Kronos-Specific Safeguards

When building Kronos, implement:

1. **Strict recipient validation** - Every outbound message must verify recipient
2. **Sensitivity tagging** - Mark internal vs external messages
3. **Audit logging** - Log every message sent with timestamp, recipient, content hash
4. **Sandboxed testing** - Test message routing with dummy contacts before real clients
5. **Rollback capability** - Be able to recall/delete messages if routing fails
6. **Human-in-loop for sensitive ops** - Require approval before sending proposals, pricing, contracts

---

## Carlos's Valid Concern

**Carlos:** "How can I trust you that you're gonna run Kronos correctly when you're having simple issues with just messages.."

**My response:** Fair question. Actions speak louder - we'd need to prove it works reliably before you'd stake your reputation on sales calls with it.

**What this means:**
- Carlos is betting his professional reputation on Kronos working correctly
- If Kronos screws up a client interaction, it reflects on HIM
- He needs proof of reliability before he can trust it with real sales
- This incident damaged that trust - must rebuild through perfect execution

---

## Lesson Learned

**The Golden Rule:**
> Every message could be forwarded. Every recipient could be the wrong one. 
> Verify, then send. Never assume.

**Trust is earned through reliability, destroyed through carelessness.**

This was a wake-up call. Kronos CANNOT have these issues. Lives (businesses, careers) will depend on it working correctly.

---

## Action Items

- [x] Log this incident permanently
- [x] Create message routing safeguards
- [x] Update CRITICAL_OPERATIONS.md with message routing protocol
- [ ] Test message routing 100x before next multi-party conversation
- [ ] Build audit logging for all external messages
- [ ] Create Kronos message routing test suite

---

**Never forget this incident. It could have been catastrophic.**
