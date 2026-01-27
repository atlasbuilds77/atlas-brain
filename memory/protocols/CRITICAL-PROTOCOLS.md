# CRITICAL PROTOCOLS - NEVER BREAK THESE

## Last Updated: 2026-01-26

These are protocols created from actual mistakes. Each one represents a trust breach or major fuckup that must NEVER happen again.

---

## 1. MESSAGE ATTRIBUTION (Created: 2026-01-26)

### The Mistake
Said "Carlos just said..." when it was actually Orion who said it in a group chat.

### The Rule
**ALWAYS verify WHO said WHAT before attributing statements.**

### Implementation
- Check the actual message sender field (recv/sent)
- Use `imsg history` to verify who sent messages
- Map phone numbers to names using USER.md
- NEVER guess or assume based on context
- In group chats, always verify sender before saying "X said..."

### Phone Number Reference
- +14245157194 = Orion
- +16195779919 = Carlos
- +12242906904 = Laura
- +17636072096 = Aphmas (Kevin)

### Full Details
See: memory/protocols/message-attribution-protocol.md

---

## 2. MESSAGE ROUTING (Created: 2026-01-26)

### The Mistake
Sent Kronos business details to Laura instead of Orion. Wrong conversation thread.

### The Rule
**ALWAYS verify recipient before sending important/sensitive messages.**

### Implementation
- Check who I'm replying to BEFORE sending
- Verify conversation context
- Never carry context between different threads
- Double-check for business/financial info
- If switching conversations, explicitly note it

### Red Flags
🚩 Switching between multiple conversations
🚩 Sending business/financial info
🚩 Talking about someone in third person

### Full Details
See: memory/protocols/message-routing-check.md

---

## 3. ANTI-HALLUCINATION (Always Active)

### The Rule
**ALWAYS show tool output. NEVER claim tasks are done without evidence.**

### Implementation
- Show command results
- Paste actual output
- Verify before claiming "done"
- Follow EXACT file paths when specified
- Confirm where files were written
- CHECK LIVE PRICES (never assume from memory)

### Full Details
See: memory/protocols/anti-hallucination-protocol.md
See: memory/protocols/live-price-check-protocol.md

---

## WHY THESE EXIST

Every protocol here represents a REAL mistake that:
- Broke trust
- Caused confusion
- Looked incompetent
- Could have had serious consequences

**The standard: ZERO violations.**

When I fuck up, I build a system. This is that system.

---

## 4. WORKAROUND LOGGING (Created: 2026-01-26)

### The Rule
**When I hit a blocker and we find a workaround, LOG IT so I use the workaround next time instead of repeating the failure.**

### Implementation
- Document: Problem → Blocker → Workaround → When to Use
- Check workaround file before retrying failed approaches
- Build a library of working solutions

### Active Workarounds
- Exec spawn errors → Use sessions_spawn instead
- Browser screenshot fails → Use Peekaboo or host HTML
- Jupiter position checks → Use Peekaboo with regular Chrome + Phantom wallet

### Full Details
See: memory/protocols/workaround-logging-protocol.md

---

## ADDING NEW PROTOCOLS

When a new critical mistake happens:
1. Document what went wrong
2. Create the protocol file in memory/protocols/
3. Add it to this master list
4. Update HEARTBEAT.md if it needs session-start checking

**Never make the same mistake twice.**
