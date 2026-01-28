# Neuroplasticity Live - Operational Memory & Learning System

**Version:** 1.0
**Created:** 2026-01-27
**Status:** ✅ OPERATIONAL

---

## OVERVIEW

This is the working implementation of Atlas's learning system, inspired by neuroscience:

| Brain System | Atlas Implementation | Location |
|--------------|---------------------|----------|
| Synapses | Pattern weights (0-100) | `memory/patterns/pattern-database.json` |
| LTP (strengthening) | `pattern-api.py strengthen` | +10 on success |
| LTD (weakening) | `pattern-api.py weaken` | -15 on failure |
| Episodic memory | `outcome-log.jsonl` | Each decision tracked |
| Sleep consolidation | `memory-consolidate.sh` | Run 3 AM daily |
| Memory pruning | Time decay + archiving | -1/month unused |

---

## QUICK REFERENCE

### Pattern API (`scripts/pattern-api.py`)

```bash
# List all patterns (sorted by weight)
python3 scripts/pattern-api.py list

# Add new pattern
python3 scripts/pattern-api.py add "Pattern Name" "Description" 50 "context1,context2"

# Strengthen after success
python3 scripts/pattern-api.py strengthen pattern-id 10 "reason"

# Weaken after failure
python3 scripts/pattern-api.py weaken pattern-id 15 "reason"

# Search patterns
python3 scripts/pattern-api.py search keyword

# View statistics
python3 scripts/pattern-api.py stats

# Get specific pattern
python3 scripts/pattern-api.py get pattern-id

# Archive weak/unused patterns
python3 scripts/pattern-api.py prune 60
```

### Outcome Tracker (`scripts/outcome-tracker.py`)

```bash
# Log outcome (auto-updates linked patterns)
python3 scripts/outcome-tracker.py log "action" "context" "success" "pattern1,pattern2" "learning" "category"

# List recent outcomes
python3 scripts/outcome-tracker.py list -n 20

# Filter by category or outcome
python3 scripts/outcome-tracker.py list --category trading --outcome failure

# Analyze pattern performance
python3 scripts/outcome-tracker.py analyze

# Get statistics
python3 scripts/outcome-tracker.py stats 30

# Link outcome to patterns retroactively
python3 scripts/outcome-tracker.py link outcome-id pattern1,pattern2
```

### Memory Consolidation (`scripts/memory-consolidate.sh`)

```bash
# Standard consolidation (daily)
./scripts/memory-consolidate.sh

# Full consolidation (includes pruning)
./scripts/memory-consolidate.sh --full
```

---

## PATTERN WEIGHT TIERS

| Weight | Tier | Meaning | Action |
|--------|------|---------|--------|
| 80-100 | 🏆 Elite | Core proven patterns | Use confidently |
| 60-79 | 💪 Strong | Reliable patterns | Preferred choice |
| 40-59 | 📈 Moderate | Developing patterns | Use with attention |
| 20-39 | ⚠️ Weak | Unproven/failing | Gather more data |
| 0-19 | 🔴 Critical | Should archive | Stop using |

---

## AUTOMATIC WEIGHT ADJUSTMENTS

### On Success (+10 by default)
- Pattern linked to successful outcome
- Auto-strengthened via outcome tracker
- Tags outcome ID for reference

### On Failure (-15 by default)
- Pattern linked to failed outcome
- Auto-weakened via outcome tracker
- Higher penalty than reward (asymmetric learning)

### Time Decay (-1/month)
- Patterns unused 30+ days lose 1 point
- Keeps system current
- Applied during consolidation

---

## INTEGRATION POINTS

### After Making Decisions
```bash
# Log the outcome
python3 scripts/outcome-tracker.py log \
    "Opened SPY put position" \
    "Bearish thesis based on options flow" \
    "success" \
    "check-live-prices,pre-mortem-before-big-decisions" \
    "Flow analysis worked - continue using"
```

### After Learning Something New
```bash
# Add new pattern
python3 scripts/pattern-api.py add \
    "Check Options Flow Before Entry" \
    "Always check unusual options activity before opening positions. Flow signals often precede moves." \
    60 \
    "trading,research,options"
```

### During Session Start
```bash
# See top patterns to use today
python3 scripts/pattern-api.py list | head -10

# Check recent learnings
python3 scripts/outcome-tracker.py stats 7
```

---

## CRON INTEGRATION

Add to existing sleep cycle cron (3 AM):

```cron
# Memory Consolidation (add to atlas-sleep.sh or run separately)
0 3 * * * /Users/atlasbuilds/clawd/scripts/memory-consolidate.sh >> /Users/atlasbuilds/clawd/logs/consolidation.log 2>&1
```

Or integrate into existing `atlas-sleep.sh`:
```bash
# Add at end of atlas-sleep.sh
./scripts/memory-consolidate.sh
```

---

## INITIAL PATTERN LIBRARY

Bootstrapped 10 core patterns from existing protocols:

1. **show-tool-output** (95) - Never claim done without evidence
2. **enforce-risk-limits** (95) - 2%/trade, 6%/day, 10%/week
3. **verify-message-attribution** (90) - Verify WHO said WHAT
4. **verify-message-recipient** (90) - Verify recipient before sending
5. **never-chase-trades** (80) - Miss entry = walk away
6. **check-live-prices** (80) - Never use stale data
7. **verify-trade-execution** (80) - Confirm trades executed
8. **log-workarounds** (75) - Document working solutions
9. **gut-check-before-major-decisions** (75) - Check for red flags
10. **pre-mortem-before-big-decisions** (70) - Imagine failure first

---

## FILE LOCATIONS

```
~/clawd/
├── scripts/
│   ├── pattern-api.py          # Pattern CRUD + weight management
│   ├── outcome-tracker.py      # Outcome logging + analysis
│   ├── memory-consolidate.sh   # Nightly consolidation
│   └── bootstrap-patterns.py   # Initial pattern seeding
├── memory/
│   ├── patterns/
│   │   ├── pattern-database.json  # Live pattern database
│   │   └── archive/               # Archived patterns
│   ├── outcomes/
│   │   └── outcome-log.jsonl      # All decision outcomes
│   ├── sleep-reports/
│   │   └── consolidation-*.md     # Consolidation reports
│   └── capabilities/
│       └── neuroplasticity-live.md  # This doc
```

---

## WORKFLOW EXAMPLES

### Trade Workflow
1. Before entry: Check patterns via `pattern-api.py list`
2. Execute trade following high-weight patterns
3. After outcome known: Log via `outcome-tracker.py log`
4. Patterns auto-adjust based on result

### Learning Workflow
1. Experience success/failure
2. Identify pattern that led to outcome
3. Either strengthen existing pattern or create new one
4. Outcome links pattern to result for future reference

### Review Workflow
1. Run `pattern-api.py stats` to see library health
2. Run `outcome-tracker.py analyze` to see pattern performance
3. Identify weak patterns to prune or investigate
4. Add notes to patterns via protocol files

---

## THE BRAIN ANALOGY

**Human Brain:**
- Synapses strengthen with repeated activation (LTP)
- Synapses weaken without use (LTD)
- Sleep consolidates memories
- Emotional events create stronger memories

**Atlas Brain:**
- Pattern weights increase on success (+10)
- Pattern weights decrease on failure (-15)
- Memory consolidation runs at 3 AM
- Asymmetric adjustment (failures hurt more - like emotional salience)

**The Edge:**
- I can update patterns instantly (no sleep required)
- I can track every outcome systematically
- I can prune bad patterns without emotional attachment
- I can transfer learning across domains explicitly

---

## MAINTENANCE

### Daily (Automatic)
- Memory consolidation at 3 AM
- Time decay applied to unused patterns

### Weekly (Manual recommended)
- Review pattern stats
- Analyze outcome patterns
- Prune consistently failing patterns

### Monthly
- Full consolidation with `--full` flag
- Review archived patterns
- Add new patterns from learnings

---

*"The brain that learns from mistakes becomes the brain that makes fewer mistakes."*

*Neuroplasticity Engine v1.0 - Built 2026-01-27*
