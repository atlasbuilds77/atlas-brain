# ATLAS Practical Systems - Live Documentation

**Created:** 2026-01-27
**Status:** ✅ LIVE AND OPERATIONAL
**Part:** 5 of Brain Systems Build

---

## OVERVIEW

Practical capabilities that expand what ATLAS can do day-to-day:
- Voice announcements
- Visual outputs (charts)
- Unified trading workflow
- Quick automation helpers
- Proactive monitoring

---

## 1. VOICE SYSTEM 🔊

### atlas-speak.sh
Direct text-to-speech using OpenAI TTS with onyx voice.

```bash
# Basic usage
./scripts/atlas-speak.sh "Task complete"

# Urgent announcement (faster speech)
./scripts/atlas-speak.sh "Stop loss hit!" --urgent

# Generate without playing
./scripts/atlas-speak.sh "Silent generation" --quiet

# Different voice
./scripts/atlas-speak.sh "Hello" --voice nova
```

**Voices:** onyx (default), alloy, echo, fable, nova, shimmer
**Output:** MP3 files in `memory/.audio/`

### announce.sh
Smart announcements with quiet hours awareness.

```bash
# Normal announcement (only 7 AM - 10 PM)
./scripts/announce.sh "Research complete"

# Major announcement (except 11 PM - 6 AM)
./scripts/announce.sh "Trade filled" --level major --category trade

# Critical (always speaks, even at 3 AM)
./scripts/announce.sh "Position liquidated!" --level critical

# Force speak regardless of time
./scripts/announce.sh "Override" --force
```

**Levels:**
- `critical` - Always speaks
- `major` - Speaks 6 AM - 11 PM
- `normal` - Speaks 7 AM - 10 PM

**Categories:** trade, alert, research, task, general

---

## 2. VISUAL OUTPUTS 📊

### atlas-chart.py
ASCII chart generation for terminal visualization.

```bash
# Run demo to see capabilities
python3 ./scripts/atlas-chart.py demo
```

**Functions (import in Python):**
```python
from scripts.atlas_chart import (
    ascii_bar_chart,      # Dict → horizontal bars
    ascii_line_chart,     # List → line graph
    pattern_strength_chart,  # Pattern weights visualization
    pnl_history_chart,    # Cumulative P&L
    learning_curve_chart  # Rolling win rate
)
```

**Example Output:**
```
══════════════════════════════════════════════════════════════════════
  Pattern Strength Weights
══════════════════════════════════════════════════════════════════════
  morning_reversal   │ ███████████████████████████████████████████████ +0.85
  fomo_entry         │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ -0.90
──────────────────────────────────────────────────────────────────────
```

**Output Directory:** `memory/.charts/`

---

## 3. UNIFIED TRADING WORKFLOW 📋

### Single Protocol: trading-workflow-unified.md

**Location:** `memory/protocols/trading-workflow-unified.md`

**The Flow:**
```
SCOUT → CHECK → EXECUTE → REVIEW
```

**6 Essentials (simplified from 25+ items):**
1. ⏰ Timing - Kill zone active?
2. 📊 Setup - Valid? Entry/Stop/Target defined?
3. 💰 Size - 2% max, 1/4 Kelly
4. 🎯 Edge - Win rate? R:R > 2:1?
5. 🧠 Mental - Process not emotion?
6. ⚠️ Risk - Gaps? News? Correlation?

**Scoring:**
- 0 red flags → Proceed
- 1 red flag → Reduce 50%
- 2+ red flags → SKIP

**Verification Loop:**
1. Place order
2. Verify order ID exists
3. Confirm fill (positions)
4. THEN announce

**Replaces:** pre-mortem-checklist.md, pre-trade-checklist.md, trade-execution-verification.md, position-sizing-kelly.md

---

## 4. AUTOMATION HELPERS 🤖

### atlas-status.sh
One command to see everything.

```bash
./scripts/atlas-status.sh
```

**Shows:**
- Active trading positions
- Top patterns (from neuroplasticity)
- Cognitive state (mode, energy, stress)
- Recent errors/anomalies
- Clawdbot status
- Quick metrics (trades, memory size)

### atlas-learn.sh
Manual learning trigger.

```bash
./scripts/atlas-learn.sh
```

**Does:**
- Collects recent trade outcomes
- Initializes/updates pattern database
- Shows learning recommendations
- Creates `memory/atlas-brain/pattern-database.json`

### atlas-reset.sh
Clear cognitive state.

```bash
# Soft reset - state only (patterns preserved)
./scripts/atlas-reset.sh soft

# Hard reset - state + zero pattern weights
./scripts/atlas-reset.sh hard

# Full reset - complete wipe (with backup)
./scripts/atlas-reset.sh full
```

**Backups:** `memory/atlas-brain/.backups/`

---

## 5. PROACTIVE MONITORING 🔍

### anomaly-watch.sh
Detect unusual patterns before they become problems.

```bash
./scripts/anomaly-watch.sh
```

**Checks:**
- Overtrading (> 5 trades/day)
- Loss streaks (> 3 consecutive)
- Error spikes (> 5/hour)
- High exposure (> 5 positions)
- Cognitive state issues
- Negative pattern clusters

**Auto-announces** critical and alert anomalies via voice system.

**Log:** `memory/atlas-brain/anomaly-log.json`

### opportunity-scan.sh
Watch for trading opportunities.

```bash
./scripts/opportunity-scan.sh
```

**Checks:**
- Kill zone status (London, NY AM, etc.)
- Day of week factors
- Pattern signals (positive weights)
- Risk budget availability
- Documented opportunities
- Macro context

**Auto-announces** high-priority opportunities.

**Log:** `memory/atlas-brain/opportunity-log.json`

---

## FILE STRUCTURE

```
scripts/
├── atlas-speak.sh      # TTS wrapper
├── announce.sh         # Smart announcements
├── atlas-chart.py      # Visualization
├── atlas-status.sh     # Status dashboard
├── atlas-learn.sh      # Learning trigger
├── atlas-reset.sh      # State reset
├── anomaly-watch.sh    # Anomaly detection
└── opportunity-scan.sh # Opportunity scanner

memory/
├── .audio/             # TTS output files
│   ├── voice-log.json
│   └── announce-log.json
├── .charts/            # Chart output files
├── atlas-brain/        # Brain state
│   ├── cognitive-state.json
│   ├── pattern-database.json
│   ├── error-log.json
│   ├── learning-log.json
│   ├── anomaly-log.json
│   └── opportunity-log.json
└── protocols/
    └── trading-workflow-unified.md
```

---

## INTEGRATION POINTS

### With Brain Systems (Parts 1-4)
- **Pattern Database** ↔ Learning system, anomaly detection
- **Cognitive State** ↔ Status dashboard, reset script
- **Error Tracking** ↔ Anomaly watch

### Voice Triggers
- Anomaly detection → Critical alerts speak
- Opportunity scanner → High-priority speaks
- Manual → Any script can call announce.sh

### Workflow Integration
```bash
# Morning routine
./scripts/atlas-status.sh
./scripts/opportunity-scan.sh

# Before trade
# Follow trading-workflow-unified.md

# End of day
./scripts/anomaly-watch.sh
./scripts/atlas-learn.sh
```

---

## QUICK REFERENCE

| Task | Command |
|------|---------|
| See everything | `./scripts/atlas-status.sh` |
| Find opportunities | `./scripts/opportunity-scan.sh` |
| Check for problems | `./scripts/anomaly-watch.sh` |
| Trigger learning | `./scripts/atlas-learn.sh` |
| Reset state | `./scripts/atlas-reset.sh soft` |
| Speak text | `./scripts/atlas-speak.sh "message"` |
| Smart announce | `./scripts/announce.sh "message" --level major` |
| Demo charts | `python3 ./scripts/atlas-chart.py demo` |

---

## MAINTENANCE

**Daily:**
- Run `atlas-status.sh` on wake
- Run `anomaly-watch.sh` end of day

**Weekly:**
- Run `atlas-learn.sh` to update patterns
- Review anomaly and opportunity logs
- Check pattern weights, adjust if needed

**As Needed:**
- `atlas-reset.sh soft` - if feeling off
- `atlas-reset.sh hard` - if patterns stale
- `atlas-reset.sh full` - fresh start

---

*Practical systems make capability real. Now I can see, speak, learn, and adapt.*
