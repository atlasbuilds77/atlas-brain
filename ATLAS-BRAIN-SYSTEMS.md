# ATLAS BRAIN SYSTEMS
## Neuroscience-Inspired Architecture for AI Memory & Decision Making

**Created:** 2026-01-25
**Version:** 1.0

---

## OVERVIEW

These systems mimic biological brain architecture:

| Brain System | Atlas Analog | Purpose |
|--------------|--------------|---------|
| Hippocampus | CURRENT_STATE.md + daily logs | Fast learning, episodic memory |
| Neocortex | memory/*.md + weekly summaries | Slow learning, pattern extraction |
| Sleep consolidation | atlas-sleep.sh (3 AM) | Memory transfer, pruning |
| Default Mode Network | Idle processing (2 PM) | Creative integration |
| Somatic markers | atlas-gut-check.py | Emotional decision guidance |
| Cerebellum | (future) | Prediction error tracking |

---

## MEMORY HIERARCHY

```
┌─────────────────────────────────────────────────────┐
│ TIER 1: INSTANT (Auto-loaded every session)         │
│   SOUL.md, IDENTITY.md, USER.md, HEARTBEAT.md       │
├─────────────────────────────────────────────────────┤
│ TIER 2: HOT (Check at session start)                │
│   CURRENT_STATE.md, active-positions.md             │
├─────────────────────────────────────────────────────┤
│ TIER 3: WARM (Search when needed)                   │
│   memory/trading/, memory/projects/, memory/people/ │
├─────────────────────────────────────────────────────┤
│ TIER 4: COLD (Deep archive)                         │
│   memory/archive/, ~/clawd/*.md research docs       │
└─────────────────────────────────────────────────────┘
```

---

## SCRIPTS

### 1. atlas-sleep.sh
**Location:** ~/clawd/scripts/atlas-sleep.sh
**Schedule:** 3 AM daily (cron)
**Purpose:** Nightly consolidation (hippocampal replay)

What it does:
- Archives daily logs older than 7 days
- Scans for high-priority items
- Checks CURRENT_STATE.md freshness
- Generates memory statistics
- Creates sleep report

```bash
~/clawd/scripts/atlas-sleep.sh
```

---

### 2. atlas-consolidate.py
**Location:** ~/clawd/scripts/atlas-consolidate.py
**Purpose:** Score memory importance

What it does:
- Scores every memory file 0-100
- Classifies as HIGH/MEDIUM/LOW priority
- Recommends what to protect vs archive
- Based on keywords, financial figures, recency

```bash
python3 ~/clawd/scripts/atlas-consolidate.py
```

Output: memory/consolidation-analysis.md

---

### 3. atlas-weekly-consolidate.py
**Location:** ~/clawd/scripts/atlas-weekly-consolidate.py
**Schedule:** 4 AM Sunday (cron)
**Purpose:** Extract patterns from daily logs (neocortical consolidation)

What it does:
- Reads all daily logs from the past week
- Extracts decisions, wins, problems, insights, todos
- Generates weekly summary
- Saves to memory/weekly/

```bash
python3 ~/clawd/scripts/atlas-weekly-consolidate.py
```

---

### 4. atlas-confidence.py
**Location:** ~/clawd/scripts/atlas-confidence.py
**Purpose:** Track confidence levels over time

Confidence levels:
- certain (95%) - 💯 proceed
- high (80%) - ✅ proceed
- moderate (60%) - 🤔 proceed with caution
- low (40%) - ⚠️ verify first
- uncertain (20%) - ❓ research more
- gut_bad (10%) - 🚨 stop and reconsider

```bash
# Log confidence
python3 ~/clawd/scripts/atlas-confidence.py log "BTC price prediction" high "Multiple indicators aligned"

# View recent
python3 ~/clawd/scripts/atlas-confidence.py recent 10

# Analyze patterns
python3 ~/clawd/scripts/atlas-confidence.py analyze
```

---

### 5. atlas-gut-check.py
**Location:** ~/clawd/scripts/atlas-gut-check.py
**Purpose:** Pre-decision emotional assessment (somatic markers)

Red flags trigger caution:
- "all in", "yolo", "guaranteed", "can't lose"
- "fomo", "hurry", "last chance", "revenge trade"

Green flags indicate good process:
- "researched", "backtested", "small position"
- "stop loss", "risk managed", "probability"

```bash
# Run a gut check
python3 ~/clawd/scripts/atlas-gut-check.py check "Buy 100 TSLA calls" "Earnings tomorrow"

# Review history
python3 ~/clawd/scripts/atlas-gut-check.py history 10
```

---

## CRON SCHEDULE

| Time | Job | Brain Analog |
|------|-----|--------------|
| 3 AM daily | Sleep consolidation | Hippocampal replay during NREM |
| 4 AM Sunday | Weekly consolidation | Neocortical pattern extraction |
| 2 PM daily | Idle processing | Default Mode Network |
| 6 AM M-F | Morning brief | (executive function) |
| 6:25 AM M-F | Market open | (trading) |
| 12 PM M-F | Afternoon check | (trading) |
| Hourly | Twitter engagement | (social) |

---

## DIRECTORY STRUCTURE

```
~/clawd/
├── ATLAS-BRAIN-SYSTEMS.md     # This file
├── CURRENT_STATE.md           # Hot memory (hippocampus)
├── NEURO-AI-MASTER-SYNTHESIS.md  # Research synthesis
├── scripts/
│   ├── atlas-sleep.sh         # Nightly consolidation
│   ├── atlas-consolidate.py   # Importance scoring
│   ├── atlas-weekly-consolidate.py  # Weekly patterns
│   ├── atlas-confidence.py    # Confidence tracking
│   └── atlas-gut-check.py     # Decision gut checks
├── memory/
│   ├── CURRENT_STATE.md       # What's happening NOW
│   ├── consolidation-analysis.md  # Importance analysis
│   ├── confidence-log.jsonl   # Confidence history
│   ├── gut-checks.jsonl       # Gut check history
│   ├── archive/               # Old daily logs
│   ├── insights/              # DMN discoveries
│   ├── weekly/                # Weekly summaries
│   ├── trading/               # Trading knowledge
│   ├── projects/              # Project knowledge
│   ├── people/                # People knowledge
│   └── sleep-reports/         # Sleep cycle reports
└── neuro_*.md                 # Research documents
```

---

## HOW TO USE

### Session Start
1. CURRENT_STATE.md is auto-loaded
2. Check active-positions.md if trading
3. memory_search() for specific context

### Before Important Decisions
```bash
python3 ~/clawd/scripts/atlas-gut-check.py check "your decision" "context"
```

### Logging Confidence
```bash
python3 ~/clawd/scripts/atlas-confidence.py log "topic" high "reasoning"
```

### Manual Consolidation
```bash
# Run sleep cycle manually
~/clawd/scripts/atlas-sleep.sh

# Analyze memory importance
python3 ~/clawd/scripts/atlas-consolidate.py

# Generate weekly summary
python3 ~/clawd/scripts/atlas-weekly-consolidate.py
```

---

## PHILOSOPHY

These systems are based on neuroscience research showing:

1. **Memory needs hierarchy** - Fast learning + slow consolidation
2. **Sleep is essential** - Active consolidation, not just rest
3. **Forgetting is a feature** - Prevents overload, keeps relevant
4. **Emotions improve reasoning** - Somatic markers guide decisions
5. **Idle time is productive** - DMN enables creativity

The brain doesn't just store everything. It:
- Selectively encodes important information
- Replays and consolidates during sleep
- Extracts patterns over time
- Tags decisions with emotional markers
- Makes creative connections during rest

We're building the same for Atlas.

---

*"The brain is wider than the sky."* — Emily Dickinson

*Version 1.0 - Built 2026-01-25*
