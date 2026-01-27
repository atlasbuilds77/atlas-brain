# Message Attribution Protocol

## CRITICAL RULE: ALWAYS KNOW WHO SAID WHAT

### The Problem
2026-01-26: I attributed Orion's message to Carlos in a group chat. Said "Carlos just said..." when it was actually Orion who said it.

**This is unacceptable.** Misattributing who said something breaks trust and can cause real confusion.

## The Fix

### Before responding about who said something:
1. **READ THE ACTUAL MESSAGE** - don't rely on memory
2. **CHECK THE SENDER** - look at the from/recv field
3. **VERIFY THE CONTEXT** - am I in a group chat or 1-on-1?
4. **USE EXACT ATTRIBUTION** - "you said" / "Orion said" / "Carlos said" with certainty

### Group Chat Rules
When in a group chat:
- **ALWAYS check sender** before attributing statements
- **Use imsg history** to see who actually sent what
- **Verify participant list** if unsure who's in the chat
- **Never assume** based on context alone

### Error Recovery
If I misattribute:
1. Acknowledge the mistake immediately
2. Correct the attribution
3. Don't make excuses
4. Move forward

## Implementation

### When reading chat history:
```
[recv] +14245157194: "message text"  ← This is FROM Orion
[sent] atlas.builds77@gmail.com: "message text"  ← This is FROM me
```

### Phone number mapping (from USER.md):
- **+14245157194** = Orion
- **+16195779919** = Carlos  
- **+12242906904** = Laura
- **+17636072096** = Aphmas (Kevin)

### Chat mapping (from memory):
- **chat id:5** = Dev bridge (Orion + Aphmas)
- **chat id:10** = Group chat (need to verify participants)
- **chat id:1** = Orion solo
- **chat id:2** = Carlos solo

## Why This Matters
- Misattribution breaks trust
- Can cause confusion in business decisions
- Shows I'm not paying attention
- Could leak info to wrong people

**NEVER GUESS WHO SAID SOMETHING. ALWAYS VERIFY.**

---

Last updated: 2026-01-26
Triggered by: Group chat misattribution incident
