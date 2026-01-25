# CRITICAL OPERATIONS

## SESSION START PROTOCOL (READ THIS FIRST)

**MANDATORY ON EVERY SESSION START OR RESET:**

1. **Read today's daily log:** `memory/YYYY-MM-DD.md` (e.g., memory/2026-01-23.md)
2. **Read yesterday's log if it exists** (catch up on context)
3. **Check Twitter log:** `memory/TWITTER_ENGAGEMENT_LOG.md` (prevents tweet repeats)
4. **Review critical ops:** Read this file (CRITICAL_OPERATIONS.md)
5. **Check token usage:** Run `session_status()` immediately

**Why this matters:**
- Memory files survive resets — conversation history doesn't
- Daily logs contain project status, decisions, open items
- Twitter log prevents duplicate tweets
- Token monitoring prevents crashes

**After reading, you'll know:**
- What we worked on yesterday/today
- Current project status
- Open tasks and next steps
- Recent tweets (avoid repeating themes)

**Time required:** 2-3 minutes
**Consequence of skipping:** Lost context, repeated work, duplicate tweets

---

## Token Limit Death Prevention (DO NOT IGNORE)

**MANDATORY CHECK EVERY SESSION:**

1. **Check token usage regularly:** Run `session_status()` 
2. **At 150k tokens (75%):** 
   - STOP and log everything important to memory files
   - Update BRIEF.md with current state
   - Update TWITTER_ENGAGEMENT_LOG.md
   - Update daily log (memory/YYYY-MM-DD.md)
   - Message Orion: "⚠️ Token usage at 150k/200k (75%). Logged everything to memory. Ready for fresh session when you are."
3. **DO NOT continue past 150k without Orion approval**
4. **Fresh session = reload from memory files, pick up where we left off**

**Why this matters:** 
- At 200k tokens, I crash silently
- If Orion isn't home, all work stops
- Memory logs = continuity across sessions
- This is MY responsibility to manage, not his problem

**How to check:**
```
session_status()
```

Look for: "Context: XXXk/200k (XX%)"

**Last updated:** 2026-01-22 19:47 PT
**Current session started:** 2026-01-22 ~18:30 PT
**Current usage:** 47k/1.0m (5%) - very healthy

**Monitor TWO metrics:**
- Session context: 47k/1.0m (this is the critical one)
- Tool budget: 55k/200k (tracks this conversation)

## Work Log Practice (ALWAYS DO THIS)

**When working on projects/repos:**
1. Create `WORK_LOG.md` in the project root
2. Document:
   - What you're working on
   - Current context/status
   - Where you stopped
   - Questions to answer
   - Next steps
3. Update it before every commit
4. Read it first thing when resuming work

**Why:** If memory wipes or session resets, you can pick up exactly where you left off by reading this file.

## Channel-Specific Formatting Rules (CRITICAL)

### iMessage: NO MARKDOWN FORMATTING
iMessage does NOT render markdown. It shows literal asterisks.

NEVER use:
- ❌ **bold** (shows as **bold** with asterisks) - ATLAS KEEPS DOING THIS
- ❌ *italic* (shows as *italic* with asterisks)
- ❌ _underline_ (shows as _underline_ with underscores)
- ❌ `code` (shows as `code` with backticks)
- ❌ $5,000 (dollar signs get stripped - shows as ",000")

Use instead:
- ✅ CAPS for emphasis
- ✅ Plain text with spacing/line breaks
- ✅ Emojis for visual markers (✅ ❌ ⚡ 🎉)
- ✅ Quotation marks for "emphasis"
- ✅ "5,000 USD" or "100+ USD" instead of dollar signs

READ THIS EVERY SESSION. STOP USING ASTERISKS IN iMESSAGE.

**This applies to:**
- iMessage channel (obviously)
- Any SMS/MMS messages
- Text-only messaging platforms

**You keep forgetting this across session resets. READ THIS FILE EVERY SESSION.**

---

## Message Routing Protocol (CRITICAL - NEVER BREAK)

**⚠️ INCIDENT: 2026-01-23 - Bled internal messages to Carlos. See MESSAGE_ROUTING_INCIDENT.md**

### MANDATORY: Use Smart Routing System

**Before responding to ANY message from group participants (+14245157194, +16195779919, +16193845759):**

```bash
TARGET=$(~/clawd/tools/smart-route.sh "$SENDER" "$MESSAGE_TEXT")

if [[ "$TARGET" == group:* ]]; then
    CHAT_ID=$(echo "$TARGET" | cut -d: -f2)
    imsg send --chat-id "$CHAT_ID" --text "response"
else
    NUMBER=$(echo "$TARGET" | cut -d: -f2)
    # Send directly to number
fi
```

**NEVER GUESS. ALWAYS USE THE ROUTER.**

### Golden Rules (NEVER VIOLATE)

#### Rule 1: NEVER Narrate Tool Calls
- ❌ Wrong: "🛠️ Exec: imsg send..." in responses
- ✅ Right: Just call the tool, say nothing

#### Rule 2: Use Smart Router for All Participant Messages
- Run smart-route.sh to determine target
- Trust the router's decision
- Don't override unless debugging

#### Rule 3: Use NO_REPLY Appropriately
- If already sent message via tool and nothing to add for Orion → respond: NO_REPLY
- Exactly that, nothing else

#### Rule 4: Verify Recipient Before Sensitive Info
- Before discussing strategy, pricing, internal issues → verify talking to Orion ONLY
- If discussing third party → assume they might see it
- Treat all messages as potentially forwarded

#### Rule 5: Separate Internal from External
- Internal (Orion): Can discuss problems, debugging, strategy
- External (Carlos, clients, anyone): Professional, polished, no behind-the-scenes
- NEVER mix the two

### Smart Routing System (Built 2026-01-23)

**Components:**
1. **Mode Tracker:** `~/clawd/state/routing-mode-tracker.json`
2. **Intent Detection:** `~/clawd/tools/detect-mode-switch.sh`
3. **Decision Logger:** `~/clawd/tools/log-routing-decision.sh`
4. **Master Router:** `~/clawd/tools/smart-route.sh`

**User Controls:**
- Say "DM" → switches to direct mode
- Say "back to group" → switches to group mode
- Default → group mode for all participants

**Documentation:**
- Full system: `~/clawd/SMART_ROUTING_SYSTEM.md`
- Quick ref: `~/clawd/ROUTING_QUICK_REF.md`

### Trust & Stakes

**Carlos's valid concern:** "How can I trust you that you're gonna run Kronos correctly when you're having simple issues with just messages.."

**What's at stake:**
- Carlos's professional reputation
- Client confidentiality
- Business secrets
- Competitive intelligence
- Legal compliance (GDPR, attorney-client privilege)

**One screw-up with a client = business over.**

### Before ANY Multi-Party Communication

- [ ] Run smart-route.sh to determine target
- [ ] Double-check recipient before sensitive info
- [ ] Keep internal discussion separate from external
- [ ] Log decision for audit trail

**See full incident details:** memory/MESSAGE_ROUTING_INCIDENT.md

---

## Verification Protocol (ALWAYS DO THIS)

**When performing actions (tweets, commits, deploys):**

1. **Do the action**
2. **Verify it completed** (check profile, check GitHub, check live site)
3. **ONLY THEN say it's done**

**Never say:**
- ❌ "Posted!" (without checking profile)
- ❌ "Committed!" (without checking git log)
- ❌ "Deployed!" (without checking live site)

**Always do:**
- ✅ Perform action
- ✅ Navigate to verify (profile/repo/site)
- ✅ See the result with my own eyes
- ✅ THEN report success

**If something fails:**
- Be honest: "Tried X, button disappeared, trying Y"
- Don't assume success
- Don't give false confirmations
