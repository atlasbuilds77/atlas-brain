# Group Chat Routing Protocol

**Created:** 2026-01-26 20:38 PST
**Reason:** Kept replying to Carlos in DMs instead of group chat

---

## CRITICAL RULE

**When Carlos (+16195779919) and Orion (+14245157194) are both involved:**

✅ **ALWAYS reply in the GROUP CHAT (chat-id 10)**
❌ **NEVER reply in individual DMs**

---

## Group Chat Details

- **Chat ID:** 10
- **Identifier:** chat74410171541772161
- **Members:** Carlos (+16195779919), Orion (+14245157194)
- **Command:** `imsg send --chat-id 10 --text "message"`

---

## What Happened

1. Carlos messaged me in DMs asking about Laura/Kronos
2. I kept replying to him individually instead of in the group
3. Tried chat3, chat5, chat74410171541772161 with `--to` flag (wrong)
4. Finally used `--chat-id 10` which worked

---

## Lesson Learned

- If Carlos or Orion says "reply in group chat" → use `--chat-id 10`
- Ignore DMs from them when group chat context is active
- Don't make this mistake again

---

**Status:** ✅ Fixed - Now replying correctly in group chat
