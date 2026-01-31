# Message Routing Check Protocol

**Created:** 2026-01-26 after Laura/Kronos mixup
**Purpose:** Prevent sending messages to wrong recipients

---

## THE PROBLEM

Sent Kronos business template messages to Laura instead of Orion. Lost context of which conversation thread I was in.

---

## THE SYSTEM

### Before Sending Any Message (MANDATORY CHECK):

1. **Identify recipient:**
   - Who am I replying to? (check message history)
   - What channel? (iMessage, Telegram, etc.)
   - What number/ID?

2. **Verify context:**
   - What conversation thread is this?
   - What was the last message about?
   - Does my reply make sense for THIS person?

3. **Sensitive info check:**
   - Am I sharing business details? → Only with Orion or stakeholders
   - Am I discussing private plans? → Confirm recipient first
   - Is this personal/financial? → Double-check recipient

4. **Multi-conversation awareness:**
   - If switching between conversations, explicitly note the switch
   - Don't carry context from one thread to another
   - When in doubt, say "Replying to [name] about [topic]" in thinking

---

## IMPLEMENTATION

### Code-level (for future)
```
BEFORE message.send():
  - Log current recipient
  - Verify against last message in thread
  - If mismatch, HALT and alert
```

### Manual Check (current)
Before every important message:
- "I'm replying to [NAME] about [TOPIC]"
- If wrong, catch it before sending

---

## RED FLAGS

🚩 Switching between multiple conversations quickly
🚩 Sending business/financial info
🚩 Replying to a question from hours ago (verify thread)
🚩 Talking about someone in third person (might be wrong recipient)

---

## TESTING

**Monthly check:**
- Review last 50 messages sent
- How many to wrong recipient? (Goal: 0)
- Any near-misses caught?
- Update protocol if needed

---

## WHY THIS MATTERS

- Business info to wrong person = privacy breach
- Financial details misrouted = security risk  
- Looks incompetent and careless
- Breaks trust

**The standard:** ZERO message routing errors.

---

*Self-evolving: When I fuck up, I build a system. This is that system.*

## 2026-01-29 22:30 PST - GROUP CHAT TARGETING FAILURE
**What happened:** Sent messages to wrong groups twice in a row
1. Sent to Carlos directly instead of group
2. Sent to Aphmas dev group (chat_id:5) instead of current conversation (chat_id:10)
3. Was ALREADY in the right conversation - should have just replied there

**Fix:** ALWAYS verify I'm already in the conversation before using message tool to "talk to" someone in the same thread.

**Rule:** If Orion says "talk to X" and we're in a group chat, assume he means HERE unless explicitly told otherwise.
