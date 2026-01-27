# Memory System Upgrade Plan

**Based on:** 10 research sparks analyzing AI memory systems
**Goal:** Streamlined, persistent context across all sessions

---

## CURRENT STATE (What We Have)

- Auto-loaded: SOUL.md, IDENTITY.md, USER.md, HEARTBEAT.md
- Manual recall: memory_search() for memory/*.md files
- Research files: ~/clawd/*.md (flat, unorganized)
- No semantic search (just filename/content grep)
- No automatic summarization
- No forgetting/consolidation

---

## PROPOSED ARCHITECTURE

### Tier 1: INSTANT (Auto-loaded every session)
```
SOUL.md          - Personality (never changes)
IDENTITY.md      - Who I am (rarely changes)
USER.md          - Orion's info (occasionally updated)
CURRENT_STATE.md - What's happening NOW (daily update)
```

### Tier 2: HOT (Check at session start)
```
memory/trading/active-positions.md  - Open trades
memory/today.md                     - Today's notes
memory/yesterday.md                 - Yesterday's context
```

### Tier 3: WARM (Search when needed)
```
memory/trading/     - Trading strategies, research
memory/projects/    - Project-specific context
memory/people/      - Key people details
memory/tools/       - Tool usage notes
memory/decisions/   - Important decisions made
```

### Tier 4: COLD (Deep archive)
```
~/clawd/*.md        - Full research docs
memory/archive/     - Old daily logs
```

---

## KEY UPGRADES TO IMPLEMENT

### 1. CURRENT_STATE.md (Source of Truth)
Create a single file that answers: "What's happening right now?"
- Active positions
- Pending tasks
- Recent decisions
- What I'm waiting on

**Update:** Daily or when major things change

### 2. Automatic Session Start Protocol
Add to HEARTBEAT.md:
```
1. Read CURRENT_STATE.md
2. Check active-positions.md
3. memory_search() for recent context if confused
```

### 3. Memory Consolidation (Weekly)
- Summarize daily logs into weekly summary
- Archive old dailies
- Update CURRENT_STATE.md
- Prune redundant info

### 4. Importance Scoring (What to Remember)
Keep if:
- Orion explicitly says "remember this"
- Financial/trading decision
- Lesson learned from mistake
- Preference or recurring pattern

Forget/summarize if:
- One-off research that's in files
- Routine task completion
- Superseded information

### 5. Tagging System
Add to memory files:
```yaml
---
tags: [trading, kalshi, active]
importance: high
updated: 2026-01-25
---
```

---

## FUTURE UPGRADES (If We Want to Go Deeper)

### Vector Database (Semantic Search)
- **Tool:** Qdrant (free tier) or SQLite-vec
- **Benefit:** Find related memories by meaning, not just keywords
- **Implementation:** mcp-memory-service

### Knowledge Graph
- **Tool:** Graphiti or Neo4j
- **Benefit:** Track relationships (Orion → Carlos → Kronos)
- **Use case:** "Who's involved in project X?"

### MCP Memory Server
- **Tool:** mcp-memory-service
- **Benefit:** 5ms reads, web dashboard, auto-tagging
- **Implementation:** Plug into Clawdbot config

---

## IMMEDIATE ACTIONS

### Today (2026-01-25):
1. ✅ Created INDEX.md for trading
2. ✅ Created MASTER-CRYPTO-PLAYBOOK.md
3. ✅ Created CURRENT_STATE.md
4. ✅ Updated HEARTBEAT.md with boot protocol
5. ✅ Built sleep consolidation system (atlas-sleep.sh)
6. ✅ Built importance scoring system (atlas-consolidate.py)
7. ✅ Set up 3 AM nightly consolidation cron job
8. ✅ Set up 2 PM idle processing cron job (DMN simulation)

### This Week:
- [ ] Add YAML frontmatter to key files
- [ ] Create memory/people/ with key contacts
- [ ] Create memory/decisions/ for important choices
- [ ] Review first sleep consolidation report

### Future:
- [ ] Evaluate mcp-memory-service integration
- [ ] Consider vector DB for semantic search
- [ ] Build knowledge graph for relationships

---

## KEY INSIGHTS FROM RESEARCH

1. **Hierarchical beats flat** - 4 tiers (instant/hot/warm/cold)
2. **Forgetting is essential** - Prevents bloat, keeps context relevant
3. **LLM can self-manage** - I can decide what to remember via tools
4. **Hybrid works best** - Vectors for similarity + structure for relationships
5. **Local-first for privacy** - SQLite-vec over cloud when possible
6. **User control matters** - Orion should see/edit what I remember
7. **Every line must earn its place** - Context tokens are precious

---

## SUCCESS METRICS

- Session start: < 30 seconds to full context
- Memory recall: Find any past decision in < 10 seconds
- No "I forgot" moments on active projects
- Clean, scannable memory files
- Orion can audit what I know

---

*Created: 2026-01-25 from 10 research sparks*
*Research files: ~/clawd/ai_assistants_memory_*.md, ~/clawd/*_research.md*
