# Memory Workflow - Two-Tier System

## Philosophy

**Hot (BRIEF.md):** Active state, always loaded, stay lean  
**Cold (memory/*.md):** Historical archive, search when needed, unlimited growth

---

## Daily Flow

### Morning (6:30 AM)
```
1. Session starts
2. Load BRIEF.md (2kb)
3. Read active projects
4. Generate briefing
5. Update BRIEF.md if needed
```

### During Work
```
Normal conversation:
→ Use BRIEF.md context only
→ Stay under 40k tokens

User references old context:
→ memory_search("relevant keywords")
→ Load specific snippets
→ Answer with historical context
→ Don't keep loaded (ephemeral)
```

### Evening (8:00 PM)
```
1. Summarize day's work
2. Update BRIEF.md with new state
3. Archive if getting large (>3kb)
4. Session reset
```

### Weekly (Sunday 9 PM)
```
1. Review BRIEF.md
2. Move completed projects → memory/projects/
3. Move old decisions → memory/decisions.md
4. Keep BRIEF.md focused on active work
5. Archive preserves everything
```

---

## Memory Search Examples

### User References Old Work

**User:** "Remember that trading bot we built in December?"

**Atlas:**
```javascript
memory_search({
  query: "trading bot December build",
  maxResults: 3
})
```

**Results:**
```
memory/2024-12-15.md (lines 45-67): Trading bot architecture
memory/projects/helios-bot.md (lines 12-34): Implementation details
memory/decisions.md (lines 89-92): Decision to use WebSockets
```

**Atlas:**
```javascript
memory_get({
  path: "memory/projects/helios-bot.md",
  from: 12,
  lines: 22
})
```

**Response:** "Yes, Helios trading bot - we built it with WebSocket feed, EMA crossover strategy..."

---

### User Asks About Old Decision

**User:** "Why did we choose Flask over FastAPI for FuturesRelay?"

**Atlas:**
```javascript
memory_search({
  query: "FuturesRelay Flask FastAPI decision",
  maxResults: 2
})
```

**Results:**
```
memory/2026-01-15.md (lines 78-82): FuturesRelay framework choice
```

**Atlas:**
```javascript
memory_get({
  path: "memory/2026-01-15.md",
  from: 78,
  lines: 5
})
```

**Response:** "We chose Flask for FuturesRelay because: 1) Simpler for webhook receiver, 2) You're already familiar..."

---

## Archival Process (Weekly)

### Before (BRIEF.md getting bloated):
```markdown
# BRIEF.md (4.5kb - too large!)

## Goal
- Optimize Clawdbot for cost
- Monitor SPX trading
- Build FuturesRelay webhook receiver

## Current State
- Clawdbot running with 3-tier models
- FuturesRelay completed (deployed Jan 21)
- Working on voice transcription integration

## Decisions Made
1. 3-tier model system (Jan 21)
2. BRIEF.md + memory archive (Jan 22)
3. FuturesRelay uses Flask (Jan 15)
4. Polygon API for market data (Dec 2025)
5. Morning briefing at 6:30 AM (Jan 20)
...
```

### Janitor Archival Task:
```
"Move completed projects and old decisions (>1 week) from BRIEF.md to memory archive. Keep BRIEF.md under 3kb and focused on active work."
```

### After (BRIEF.md lean):
```markdown
# BRIEF.md (2.1kb - optimized!)

## Goal
- Optimize Clawdbot for cost
- Monitor SPX trading
- Integrate voice transcription

## Current State
- Clawdbot running with 3-tier models
- Working on voice transcription integration
- Testing session resets

## Decisions Made
1. 3-tier model system (Jan 21)
2. BRIEF.md + memory archive (Jan 22)
3. Morning briefing at 6:30 AM (Jan 20)

## Next Steps
1. Test voice transcription with Haiku
2. Monitor cost savings after 3-tier rollout
3. Optimize context thresholds
```

### Archived to memory/projects/futures-relay.md:
```markdown
# FuturesRelay Project

**Status:** Completed Jan 21, 2026  
**Location:** `/Users/orionsolana/Desktop/FuturesRelay`

## Overview
Webhook receiver for TradingView alerts...

## Decisions
- Framework: Flask (simpler for webhook receiver)
- Deployment: Local + ngrok tunnel
- Auth: Token-based

## Implementation
[detailed notes moved from BRIEF.md]
```

### Archived to memory/decisions.md:
```markdown
## Market Data - Polygon API (Dec 2025)
Chose Polygon for SPX data because...

## Morning Briefing Time - 6:30 AM (Jan 20)
Set to 6:30 AM PT to align with pre-market...
```

---

## Size Targets

**BRIEF.md:**
- Target: <2kb
- Warning: >3kb (trigger archival)
- Max: 5kb (force archival)

**memory/*.md:**
- No limit (searchable archive)
- Organized by date/project/topic
- Janitor maintains structure

---

## Cost Impact

### Without Two-Tier:
```
Session reset loads full memory (50kb):
→ 50,000 tokens × $3/M = $0.15 per reset
→ 3 resets/day = $0.45/day
→ Monthly: $13.50
```

### With Two-Tier:
```
Session reset loads BRIEF.md (2kb):
→ 2,000 tokens × $3/M = $0.006 per reset
→ 3 resets/day = $0.018/day
→ Monthly: $0.54

Memory search (when needed, ~5x/week):
→ 5,000 tokens × $3/M = $0.015 per search
→ 5 searches/week = $0.075/week
→ Monthly: $0.30

Total: $0.84/month (vs $13.50)
Savings: $12.66/month
```

---

## Summary

**You get:**
- Full long-term memory (never lose context)
- Fast session resets (cheap)
- Automatic archival (no manual work)
- Smart retrieval (I find what you need)

**I maintain:**
- BRIEF.md stays lean (<2kb)
- memory archive grows unlimited
- Search when you reference old work
- Cost stays minimal

**Result:**
- Best of both worlds
- No context loss
- Maximum cost savings
