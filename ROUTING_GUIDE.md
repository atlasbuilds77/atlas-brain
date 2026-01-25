# Task Routing Guide - 3-Tier System

## Quick Decision Tree

```
Is it summarization/extraction/cleanup?
  → YES: Tier A (Janitor - Haiku)
  
Is user saying "Deep mode"?
  → YES: Tier C (Opus, distilled input only)
  
Is it large/complex content (>500 lines, logs, etc)?
  → YES: Janitor first, then route
  
Everything else?
  → Tier B (Sonnet - default)
```

---

## Tier A (Janitor) - Haiku

**Use for:**
- Summarizing chat history
- Extracting key points from logs
- Compressing file contents
- Rewriting BRIEF.md
- Formatting/deduping data
- Preparing inputs for Tier C

**How to invoke:**
```bash
sessions_spawn(
  agentId="janitor",
  model="anthropic/claude-haiku-4",
  task="Summarize the last 50 messages and extract: decisions, open questions, next steps",
  cleanup="delete"
)
```

**Example tasks:**
- "Summarize today's conversation"
- "Extract errors from this log file"
- "Rewrite BRIEF.md with today's updates"
- "Compress this 1000-line file to key points"

---

## Tier B (Workhorse) - Sonnet

**Use for (80-90% of tasks):**
- Normal coding
- Debugging
- Planning/drafting
- Q&A
- File operations
- Simple analysis
- Configuration changes

**How to invoke:**
- Default model (me, Atlas)
- No special invocation needed

**Example tasks:**
- "Build a Flask endpoint"
- "Fix this bug"
- "Explain how X works"
- "Update the config"
- "Write a script to do Y"

---

## Tier C (Heavy) - Opus

**Use for (explicit only):**
- Complex multi-constraint problems
- System architecture decisions
- High-risk debugging
- Final review/synthesis
- Novel algorithm design

**How to invoke:**
User must say: **"Deep mode"**

**Required flow:**
1. User: "Deep mode: Design a fault-tolerant trading system"
2. Atlas: Spawns Janitor to prepare context
3. Janitor: Distills problem + constraints
4. Atlas: Spawns Opus with distilled input
5. Opus: Delivers solution
6. Atlas: Reports back to user

**Example tasks:**
- "Deep mode: Architect a scalable WebSocket relay"
- "Deep mode: Debug this multi-threading race condition"
- "Deep mode: Optimize this strategy for latency and cost"

---

## Janitor Gate (Mandatory Before Tier C)

**Never send to Opus directly:**
❌ Raw logs
❌ Full chat history
❌ Unfiltered file dumps
❌ Long context

**Always use Janitor first:**
✅ Distilled problem statement
✅ Key constraints
✅ Relevant excerpts (minimal)
✅ Specific questions

**Flow:**
```
Large content → Janitor (extract) → Opus (solve)
```

---

## Context Thresholds

**30-40k tokens:**
- Auto-trigger: Janitor micro-compaction
- Action: Summarize last 20 messages, update BRIEF.md
- Silent (no user alert)

**50-60k tokens:**
- Alert user: "⚠️ Context at 55k - recommend reset?"
- Offer: Quick session reset with BRIEF.md reload

**80k+ tokens:**
- Hard warning: "🚨 Context at 85k - reset required"
- Force reset after user confirmation

---

## Cost Estimates

**Tier A (Haiku):** ~$0.25 per 1M tokens
- Summarize 100 messages: $0.01
- Extract from 1000-line log: $0.02
- Rewrite BRIEF.md: $0.001

**Tier B (Sonnet):** ~$3 per 1M tokens
- Normal chat (10 messages): $0.30
- Build simple feature: $0.50

**Tier C (Opus):** ~$15 per 1M tokens
- Complex architecture: $2-5
- Deep debugging: $3-8

**Daily target:** <$1/day with proper routing
