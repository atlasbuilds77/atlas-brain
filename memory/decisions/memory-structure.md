# Decision: Memory Structure Redesign

**Date:** 2026-01-24
**Decision by:** Orion + Atlas

## Problem
Atlas kept losing context across sessions. Too many fragmented memory files. Important info getting missed.

## Solution
Two-layer memory system:

### Layer 1: Quick Boot
- **CURRENT_STATE.md** - Single source of truth for active state
- Read FIRST every session
- Keep short and scannable
- Update constantly

### Layer 2: Deep Memory (Topical)
```
memory/
├── trading/     - Strategy, lessons, what works
├── projects/    - Everything we've built
├── people/      - Relationships, preferences
├── decisions/   - Why we chose things
├── lessons/     - Mistakes, insights
├── tools/       - How to use things
```

### Recall
- Use `memory_search` for semantic search across all files
- Topic files accumulate knowledge over time
- Daily logs (YYYY-MM-DD.md) for raw activity

## Why This Works
- Quick boot = fast context recovery
- Topical files = knowledge compounds
- Semantic search = find anything
- Not trying to read everything linearly

## Boot Sequence (Updated)
1. Read CURRENT_STATE.md (source of truth)
2. Read SOUL.md (stay Atlas)
3. Read today's memory file if exists
4. Use memory_search for specific recall

---

*This decision enables Atlas to get smarter over time*
