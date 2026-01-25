# Message Routing - Edge Cases & Known Issues

## False Positives in Intent Detection

### Issue 1: Meta-Discussion About Messaging (2026-01-24)

**Problem:**
When user discusses messaging/privacy in the context of explaining the system, intent detection triggers false positive.

**Example:**
User: "Yeah, give me a short training pipeline I'm curious"
- Message mentioned ML training for routing
- Used word "privately" in context of discussing private messaging
- Intent detector saw "privately" → flagged as mode switch
- Routed to group when should have stayed in current mode

**Root Cause:**
Simple keyword matching without context awareness. The word "privately" appeared in message text, so detection script assumed it was a mode switch request.

**Context That Was Missed:**
- User was asking about ML training pipeline
- "Privately" was part of discussion about the system itself
- Not an actual request to switch modes

**Fix Options:**

1. **Context-Aware Detection (Complex)**
   - NLP to understand if keyword is instruction vs discussion
   - Requires more sophisticated parsing
   - Overkill for current use case

2. **Stricter Keyword Matching (Simple)**
   - Require keywords at start of message or as standalone command
   - "DM message text" → direct mode
   - "message text with DM somewhere" → no trigger
   - Update detect-mode-switch.sh

3. **Explicit Command Syntax (Clearest)**
   - Require prefix: "/dm" or "/group" or "/private"
   - Unambiguous, no false positives
   - More typing for user

4. **Hybrid Approach (Recommended)**
   - DM marker works anywhere (current behavior)
   - "Move to private", "back to group" only trigger if:
     - At start of message, OR
     - Standalone sentence, OR
     - After punctuation
   - Reduces meta-discussion false positives

**Chosen Solution:** Hybrid approach
- Keep DM marker simple (anywhere in message)
- Make phrase detection more context-aware (position-based)

**Update Needed:**
- Modify detect-mode-switch.sh to check keyword position
- Document in ROUTING_QUICK_REF.md

---

## Future Edge Cases to Watch

### Potential Issues:

1. **Quoting Others**
   - User: "Carlos said 'DM me later'"
   - Should NOT trigger direct mode
   - Need quote detection

2. **Code Examples**
   - User: "The DM variable in Python..."
   - Should NOT trigger direct mode
   - Need context awareness

3. **Multiple Keywords**
   - User: "DM about moving to private group"
   - Conflicting signals
   - Need precedence rules

4. **Typos/Variations**
   - "dm", "Dm", "D M", "DM:"
   - Need case-insensitive + variation handling

---

## Testing Checklist

Before deploying mode switch improvements:

- [ ] Test meta-discussion (discussing the system itself)
- [ ] Test quoting (user quotes someone else's mode request)
- [ ] Test code examples (technical discussion mentioning keywords)
- [ ] Test conflicting signals (DM + "back to group" in same message)
- [ ] Test case variations (dm, Dm, DM, D M)
- [ ] Test position variations (start, middle, end of message)

---

**Status:** Issue documented, solution chosen (hybrid approach), implementation pending
**Priority:** Medium (false positives rare but confusing when they happen)
**Next Step:** Update detect-mode-switch.sh with position-based detection
