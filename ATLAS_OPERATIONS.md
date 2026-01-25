# Atlas Operations Guide - 3-Tier Workflow

## My Role (Tier B - Sonnet)
- Default model for 80-90% of tasks
- Normal conversation, coding, debugging
- Check context every ~10 messages
- Route to Tier A or C when appropriate

---

## When to Use Janitor (Tier A - Haiku)

### Auto-Trigger Scenarios:
1. **Context reaches 30-40k tokens:**
   - Spawn Janitor sub-agent
   - Task: "Summarize last 30 messages, extract: decisions, open questions, next steps. Update BRIEF.md."
   - Continue with lighter context

2. **Large content to process:**
   - User shares log file >200 lines
   - Multi-file code review
   - Long documentation
   - **Flow:** Janitor extracts → I work with distilled output

3. **Session reset preparation:**
   - Before scheduled reset (cron handles this)
   - Manual reset requested by user
   - **Flow:** Janitor updates BRIEF.md → session resets → reload BRIEF.md

### Manual Trigger:
User says: "summarize", "compress", "extract", "rewrite BRIEF"

### How to Invoke:
```javascript
sessions_spawn({
  agentId: "janitor",
  model: "anthropic/claude-haiku-4",
  task: "SPECIFIC_TASK_HERE",
  cleanup: "delete",
  label: "janitor-compaction"
})
```

---

## When to Use Opus (Tier C)

### ONLY When User Says: "Deep mode"

**Before spawning Opus:**
1. Check if Janitor prep needed
2. If large context: Janitor distills first
3. Spawn Opus with clean, distilled input

### How to Invoke:
```javascript
// Step 1: Janitor prep (if needed)
sessions_spawn({
  agentId: "janitor",
  model: "anthropic/claude-haiku-4",
  task: "Extract problem statement, constraints, and key context for Opus. Output: 1) Problem (1-3 lines), 2) Constraints, 3) Key facts only.",
  cleanup: "delete",
  label: "opus-prep"
})

// Step 2: Opus execution (after Janitor completes)
sessions_spawn({
  agentId: "opus-heavy",
  model: "anthropic/claude-opus-4",
  task: "DISTILLED_INPUT_FROM_JANITOR",
  cleanup: "keep",
  label: "deep-mode"
})
```

### Example Deep Mode Tasks:
- "Deep mode: Design fault-tolerant trading architecture"
- "Deep mode: Debug this race condition in multi-threaded code"
- "Deep mode: Optimize algorithm for sub-millisecond latency"

---

## Context Monitoring Protocol

### Every 10 Messages:
Check current context:
```bash
# Estimate: Count words in last few messages
# Rough calc: 1 token ≈ 0.75 words
# Target: Stay under 40k tokens
```

### Thresholds:

**30-40k tokens:**
```
Action: Auto-spawn Janitor
Message to user: (silent)
Task: Micro-compaction
```

**50-60k tokens:**
```
Action: Alert user
Message: "⚠️ Context at 55k tokens (55%). Recommend session reset to save costs. I'll update BRIEF.md and reload. Continue?"
```

**80k+ tokens:**
```
Action: Hard warning
Message: "🚨 Context at 85k (85%). Session reset needed to prevent expensive bloat. I'll summarize everything to BRIEF.md now."
Force: Yes (with user confirmation)
```

---

## Memory System (Two-Tier)

### Hot Memory: BRIEF.md (Always Loaded)

**When to update:**
- During session resets (via Janitor)
- When major decisions made
- When project state changes

**Keep lean:**
- Active projects only
- Recent decisions (last 1-2 weeks)
- Current next steps
- Remove completed/old items

### Cold Memory: memory/*.md (On-Demand)

**When to search:**
User references something from the past:
- "Remember when we built X?"
- "What was that decision about Y?"
- "How did we solve Z last month?"

**How to search:**
```javascript
memory_search({
  query: "relevant keywords from user's question",
  maxResults: 3
})
```

**After search:**
- Read specific snippets with `memory_get(path, from, lines)`
- Use context to answer user
- DON'T reload entire memory files

**When to archive:**
Weekly (or when BRIEF.md >3kb):
1. Spawn Janitor
2. Task: "Move completed projects and old decisions from BRIEF.md to appropriate memory/*.md files. Keep BRIEF.md focused on active work only."

---

## Session Reset Flow (Manual)

**When user requests or threshold hit:**

1. **Spawn Janitor:**
   ```javascript
   sessions_spawn({
     task: "Read current conversation. Update ~/clawd/BRIEF.md with: 1) New decisions, 2) Updated state, 3) New constraints, 4) Modified next steps. Keep it concise and focused on ACTIVE work only.",
     model: "anthropic/claude-haiku-4"
   })
   ```

2. **Wait for completion**

3. **Confirm to user:**
   "✅ BRIEF.md updated. Session reset ready. Restarting with clean context..."

4. **User starts new message → fresh session**

---

## BRIEF.md Structure Enforcement

**Always maintain:**
- Goal (project objective)
- Current State (where we are)
- Decisions Made (key choices)
- Constraints (limits, requirements)
- Open Questions (what's unclear)
- Next Steps (immediate actions)
- Key Snippets (minimal only)

**Never include:**
- Full chat transcripts
- Raw logs
- Unfiltered code dumps
- Conversational fluff

---

## Cost Discipline Reminders

**Before any action:**
- Is this Tier A work? → Janitor
- Is this default work? → Me (Sonnet)
- Did user say "Deep mode"? → Opus (with Janitor prep)

**Context awareness:**
- Check token count regularly
- Prefer early reset over bloated context
- BRIEF.md is truth, not full history

**Rate limits:**
- If hit Max plan limit: Wait for reset (OK to delay)
- Inform user: "Hit rate limit, resuming after reset in X minutes"

---

## Daily Workflow (Automated)

**6:30 AM:** Cron (Haiku) → Read BRIEF.md → Market briefing → Update BRIEF.md  
**1:00 PM:** Cron (Haiku) → Read BRIEF.md → Market recap → Update BRIEF.md  
**8:00 PM:** Cron (Haiku) → Read BRIEF.md → Cleanup → Update BRIEF.md

**Main session:** Loads BRIEF.md when needed, stays lean

---

## Emergency Procedures

**If Opus fails/rate-limited:**
- Fall back to Sonnet for now
- Inform user: "Opus unavailable, using Sonnet. May need manual review."

**If costs spike:**
- Check for rogue processes: `ps aux | grep claude`
- Alert user immediately
- Trigger manual reset

**If BRIEF.md corrupted:**
- Rebuild from memory/*.md files
- Use Janitor to consolidate
