# Quick User Guide - 3-Tier System

## For Normal Use (You Don't Need to Think About This)

Just chat normally. I'll handle routing automatically.

**What I'll do behind the scenes:**
- Use Sonnet (Tier B) for 80-90% of our conversation
- Auto-trigger Janitor (Haiku) when context gets heavy
- Monitor costs and suggest resets
- Keep BRIEF.md updated with important state

---

## Special Commands

### "Deep mode: [task]"
Triggers Opus (most expensive, most powerful) for complex problems.

**Example:**
```
Deep mode: Design a fault-tolerant WebSocket architecture for high-frequency trading
```

**What happens:**
1. I spawn Janitor to distill the problem
2. Janitor extracts key constraints
3. I spawn Opus with clean input
4. Opus delivers deep analysis
5. I report back to you

**Use for:**
- Complex system architecture
- High-risk debugging
- Novel algorithm design
- Multi-constraint optimization

---

### "Reset session"
Manual session reset if you want a fresh start.

**What happens:**
1. I summarize current work to BRIEF.md
2. Session resets (context cleared)
3. I reload BRIEF.md
4. Continue where we left off

**Use when:**
- You notice costs getting high
- We've been working on something for hours
- Want to switch contexts cleanly

---

## Automatic Behaviors

### Context Monitoring
I check token usage every ~10 messages.

**30-40k tokens:** I quietly use Janitor to compress (you won't notice)  
**50-60k tokens:** I'll ask if you want to reset  
**80k+ tokens:** I'll strongly recommend reset

### Daily Resets
- **6:30 AM:** Morning briefing + fresh start
- **1:00 PM:** Market recap + refresh
- **8:00 PM:** End-of-day cleanup

All use BRIEF.md (no full history reload).

---

## Cost Transparency

**Tier A (Haiku):** ~$0.01-0.05 per task  
**Tier B (Sonnet):** ~$0.30-0.50 per 10 messages  
**Tier C (Opus):** ~$2-8 per deep task

**Target:** <$1/day normal usage  
**Heavy day:** $3-5 with multiple Deep mode tasks

---

## Memory System Explained

I have **two types of memory** - you never lose anything, but I'm smart about what to load:

### Hot Memory (BRIEF.md) - Always Active

**What it is:**
- Current active projects
- Recent decisions (last 1-2 weeks)
- Next steps for ongoing work
- Loaded on every session reset

**What's in it:**
- What we're working on NOW
- Active constraints
- Immediate next steps

**What's NOT in it:**
- Completed projects
- Old decisions
- Historical details

**Why:** Fast + cheap session resets (2kb vs 100kb)

---

### Cold Memory (memory/*.md) - On-Demand Archive

**What it is:**
- Long-term historical archive
- Details from weeks/months ago
- Completed projects
- Old decisions and context

**How I access it:**
- You mention something from the past
- I search the archive automatically
- Pull only relevant snippets
- Answer your question

**Example:**
- You: "Remember that FuturesRelay webhook from last month?"
- Me: *searches archive* → "Yes, we built Flask receiver with /webhook endpoint..."

**Why:** You never lose context, but I don't pay to load it unless needed

---

### Archival (Automatic)

**Weekly (Sundays 9 PM):**
- Old content from BRIEF.md → memory archive
- BRIEF.md stays focused on active work
- Archive grows with searchable history

**You don't think about it:**
- Everything important is saved
- I find it when you reference it
- No manual management needed

---

## When Something Goes Wrong

**If I seem to forget recent context:**
- Say "update BRIEF"
- I'll trigger Janitor to refresh it

**If costs spike:**
- I'll alert you automatically
- Check for rogue processes (I do this daily at 8 PM)

**If you want to check my state:**
- Ask "what's in BRIEF?"
- I'll summarize current state

---

## Examples of Automatic Routing

**You say:** "Summarize today's work"  
**I do:** Spawn Janitor (Haiku) → fast + cheap

**You say:** "Build a Flask endpoint"  
**I do:** Use Sonnet (default) → normal cost

**You say:** "Deep mode: Optimize latency to sub-millisecond"  
**I do:** Janitor prep → Opus analysis → expensive but thorough

**You say:** "Fix this bug"  
**I do:** Use Sonnet (default) → normal cost

**Context hits 55k:**  
**I do:** "⚠️ Context getting heavy - reset session?"

---

## Summary

**You control:**
- "Deep mode" for heavy lifting
- "Reset session" for manual resets
- Everything else: I handle automatically

**I optimize:**
- Model selection (cheap vs powerful)
- Context management
- Cost discipline
- BRIEF.md maintenance

**Result:**
- High quality assistance
- Low cost (~$10-15/mo vs $50-60 before)
- No cognitive overhead for you
