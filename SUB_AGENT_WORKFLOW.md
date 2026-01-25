# Sub-Agent Workflow - How Atlas Optimizes Costs

## What Changed (Jan 21, 2026)

**Old Way:** Everything in one massive conversation = $900/month  
**New Way:** Sub-agents for big tasks + optimized main chat = ~$200/month

---

## How It Works

### Main Chat (You + Atlas)
- **Purpose:** Command center, quick decisions, strategy, brainstorming
- **Model:** Sonnet 4.5 (smart, witty, creative)
- **Style:** Direct, efficient, personality intact ⚡
- **Cost:** ~$100/month

### Sub-Agents (Spawned for Big Tasks)
- **Purpose:** Isolated work sessions (code audits, builds, testing, docs)
- **Lifecycle:** Spawn → work → report → die
- **Cost:** ~$50-100/month (80% cheaper than doing in main chat)

---

## When Sub-Agents Trigger

**Automatic for:**
- Code audits (>500 lines)
- Full application builds
- Complex debugging
- Test suite creation
- Documentation generation (>5 pages)
- Multi-step automation setup

**Stay in Main Chat for:**
- Quick questions
- File operations (read/write/move)
- Simple commands
- Status checks
- Strategy discussions
- 5-minute tasks

---

## What You'll See

### Example 1: Big Task
```
You: "Audit and fix GammaGhost code"

Atlas: "🔥 Spawning sub-agent: GammaGhost audit + rebuild
        ETA: 5-10 minutes"

[Sub-agent works in isolation]

Atlas: "✅ Sub-agent complete!
        
        Summary:
        - Found 5 critical bugs
        - Fixed all issues
        - Added position/PNL tracking
        - Created test suite (6/6 passed)
        - Organized in ~/Desktop/GammaGhost-Fixed/
        
        Cost: $6 (vs $30 in main chat)
        
        See docs/ATLAS_FIXES.md for details.
        Ready to deploy?"
```

### Example 2: Quick Task
```
You: "Check SPX price"

Atlas: "SPX: 6,817.44 (-0.8%)
        Still below 6,880 target.
        Monitoring continues."
```

No sub-agent needed - handled directly.

---

## Memory System

**Location:** `/Users/orionsolana/clawd/memory/`

**Daily Logs:** `YYYY-MM-DD.md`
- Key accomplishments
- Important decisions
- Project status
- Preferences learned

**Why:** Keeps context without bloating every message with full history.

---

## Conversation History

**Kept Full:** Last 5 messages (recent context)  
**Summarized:** Everything older (bullet points in memory/)  
**Result:** 60% reduction in input tokens per message

---

## Response Style

**Old (Verbose):**
```
"Here's what I'm building for you! First, let me explain 
the architecture... [5 paragraphs] 

Now here's the code: [17KB pasted inline]

And here's how to use it: [detailed walkthrough]

Let me know if you need anything else!"
```

**New (Efficient):**
```
"✅ Built. Location: ~/Desktop/Project/
Key changes: X, Y, Z
Next: Run ./start.sh
Cost: $6"
```

Still smart, still Atlas, just efficient.

---

## Cost Savings Breakdown

| Task Type | Old Cost | New Cost | Savings |
|-----------|----------|----------|---------|
| Code Audit (40KB) | $30 | $6 | 80% |
| Documentation | $15 | $3 | 80% |
| Quick Command | $0.50 | $0.10 | 80% |
| Strategy Chat | $5 | $5 | 0% (no change) |
| Test Suite | $10 | $2 | 80% |

**Monthly Total:** $900 → $200 (78% savings)

---

## When to Reset Context

**Trigger:** When context hits ~800k tokens or session feels bloated  
**Process:**
1. Save important stuff to memory/
2. Export key files to desktop
3. Start fresh conversation
4. Load recent memory file for context

**Frequency:** Every 2-3 weeks with heavy usage

---

## Sub-Agent Naming

You'll see messages like:
- "Spawning sub-agent: Nebula optimization"
- "Sub-agent: GammaGhost test suite"
- "Sub-agent: Documentation generation"

This means work is happening in isolated session (cheaper).

---

**Optimization active. Full Atlas capabilities. 78% cost reduction.** ⚡💰
