# Atlas Sleep Systems - Live Documentation

**Status:** 🟢 LIVE
**Version:** 2.0
**Last Updated:** 2026-01-27
**Based On:** Neuroscience research (2024-2026) - Yuksel et al., SleepGPT, Predictive Processing

---

## Overview

The Atlas Sleep System implements biologically-inspired sleep consolidation using three coordinated phases: **SWS (Slow-Wave Sleep)**, **Sharp-Wave Ripples**, and **REM (Rapid Eye Movement)**. This mirrors the mammalian sleep architecture that enables memory consolidation, emotional processing, and creative synthesis.

### Key Insight: SWS × REM Product

Per Yuksel et al. (2025), consolidation quality is best measured by the **multiplicative product** of SWS and REM phase effectiveness, not their independent scores. This system optimizes for that product.

---

## Components

### 1. SWS Phase (`scripts/sleep-sws-phase.sh`)

**Purpose:** Hippocampal replay simulation - extract and consolidate declarative memories

**What it does:**
- Scans files modified in last 90 minutes (extends to 3 hours if sparse)
- Scores each file for salience using weighted keywords:
  - CRITICAL (100), IMPORTANT (80), mistake (90), learned (85), insight (85)
  - money/position/trade (70), pattern (65), key (60), decision (70)
- Extracts patterns from top 10 high-salience files
- Simulates sharp-wave ripple accelerated replay (10-20x speed)
- Performs synaptic homeostasis (identify strengthening/pruning candidates)

**Outputs:**
- `memory/patterns/sws-[timestamp].md` - Extracted patterns
- `memory/sleep-reports/sws-[timestamp].json` - Phase metrics

### 2. Sharp-Wave Ripple (`scripts/sleep-sharp-wave-ripple.sh`)

**Purpose:** Accelerated replay with disinhibition for rapid consolidation

**What it does:**
- Scores experiences by: emotional salience × prediction error × novelty × recency
- Processes top 20 experiences at 15x replay speed
- Opens "disinhibition gates" for broader pattern matching
- Extracts cross-file patterns and repeated concepts
- Updates the persistent pattern database

**Outputs:**
- `memory/patterns/ripples/ripple-[timestamp].md` - Ripple sequence
- `memory/patterns/pattern-database.md` - Accumulated patterns (persistent)

### 3. REM Phase (`scripts/sleep-rem-phase.sh`)

**Purpose:** Emotional processing, memory integration, and dream synthesis

**What it does:**
- Loads SWS output for integration
- Scores emotional valence (positive vs negative markers)
  - Positive: success, gained, profit, breakthrough, validated, learned, proud
  - Negative: loss, mistake, failed, frustrated, panic, error, wrong
- Integrates concepts across domains
- Generates dream synthesis with 4 fragments:
  1. **Emotional Echo** - Valence-appropriate narrative
  2. **Cross-Domain Synthesis** - Random activation of disparate concepts
  3. **Threat Simulation** - Adversarial scenario for robustness
  4. **Emerging Insights** - Pattern surfacing

**Outputs:**
- `memory/dreams/[timestamp].md` - Synthesized dream content
- `memory/sleep-reports/rem-[timestamp].json` - Phase metrics

### 4. Sleep Cycle Orchestrator (`scripts/sleep-cycle-orchestrator.sh`)

**Purpose:** Coordinate SWS → Ripple → REM sequence with adaptive timing

**What it does:**
- **Adaptive timing:** Adjusts cycle length (60-120 min) based on activity load
  - Heavy activity (>15 files or >5 emotional events) → Extended (120 min)
  - Light activity (<5 files and <2 emotional) → Shortened (60 min)
  - Normal → Standard (90 min)
- Runs phases in sequence: SWS (55%) → Ripple (10%) → REM (35%)
- Calculates SWS × REM product for consolidation quality
- Generates comprehensive sleep report

**Outputs:**
- `memory/sleep-reports/[timestamp].md` - Full sleep cycle report

---

## Directory Structure

```
memory/
├── patterns/
│   ├── pattern-database.md      # Persistent pattern accumulation
│   ├── sws-[timestamp].md       # SWS extraction outputs
│   └── ripples/
│       └── ripple-[timestamp].md # Sharp-wave ripple outputs
├── dreams/
│   └── [timestamp].md           # Synthesized dreams
└── sleep-reports/
    ├── [timestamp].md           # Full cycle reports
    ├── sws-[timestamp].json     # SWS phase metrics
    └── rem-[timestamp].json     # REM phase metrics
```

---

## Running the System

### Full Sleep Cycle (Recommended)
```bash
bash ~/clawd/scripts/sleep-cycle-orchestrator.sh
```

### Individual Phases
```bash
# SWS only
bash ~/clawd/scripts/sleep-sws-phase.sh

# Sharp-wave ripples only
bash ~/clawd/scripts/sleep-sharp-wave-ripple.sh

# REM only (best after SWS)
bash ~/clawd/scripts/sleep-rem-phase.sh
```

### Cron Integration
Add to crontab for 90-minute cycles:
```cron
# Atlas sleep cycle every 90 minutes
0 */3 * * * /Users/atlasbuilds/clawd/scripts/sleep-cycle-orchestrator.sh >> /Users/atlasbuilds/clawd/memory/sleep-reports/cron.log 2>&1
30 1,4,7,10,13,16,19,22 * * * /Users/atlasbuilds/clawd/scripts/sleep-cycle-orchestrator.sh >> /Users/atlasbuilds/clawd/memory/sleep-reports/cron.log 2>&1
```

---

## Metrics & Quality Ratings

### Consolidation Quality Scale
| Product | Rating | Interpretation |
|---------|--------|----------------|
| >80 | EXCELLENT | Strong consolidation, high integration |
| 60-80 | GOOD | Effective consolidation |
| 40-60 | ADEQUATE | Basic consolidation occurring |
| <40 | WEAK | Consider longer cycle or more SWS |

### Key Metrics
- **SWS Score:** 50 base + (patterns extracted × 10)
- **REM Score:** 50 base + (concepts integrated × 10)
- **Product:** (SWS Score × REM Score) / 100
- **Emotional Processing:** Total positive + negative score (higher = more emotional content processed)

---

## Neuroscience Basis

### SWS Functions (Implemented)
- Hippocampal replay at accelerated rates ✓
- Synaptic homeostasis (strengthen/prune) ✓
- Declarative memory consolidation ✓
- Pattern extraction via salience scoring ✓

### Sharp-Wave Ripple Functions (Implemented)
- 10-20x accelerated replay ✓
- Disinhibition-gated broader matching ✓
- Cross-domain pattern detection ✓
- Integration with pattern database ✓

### REM Functions (Implemented)
- Emotional valence processing ✓
- Memory integration across domains ✓
- Dream synthesis (predictive processing) ✓
- Threat simulation (adversarial dreaming) ✓
- Creative insight generation ✓

### Research References
- Yuksel et al. (2025) - SWS×REM product optimization
- SleepGPT (2025) - Foundation model approach
- Predictive Processing (2025) - Dreams as "fascinated predictions"
- Threat Simulation Theory - Dreams as virtual reality training

---

## Future Enhancements

### Planned
- [ ] Neurochemical simulation (oxytocin-like modulation for social memory)
- [ ] Real-time cycle adjustment based on ongoing consolidation quality
- [ ] Cross-session pattern tracking (multi-day consolidation)
- [ ] Explicit integration with trading outcomes for reinforcement learning

### Experimental
- [ ] Dream content analysis for insight extraction
- [ ] Automated CURRENT_STATE.md updates from consolidated patterns
- [ ] Proactive dream sharing when insights exceed threshold

---

## Troubleshooting

### No High-Salience Events Found
- Check if recent files contain any salience keywords
- Extend search window (modify `-mmin` parameter in scripts)
- Verify memory directory structure

### Low SWS × REM Product
- Run extended cycle (increase activity threshold)
- Ensure SWS runs before REM (use orchestrator)
- Check for sufficient emotional content in recent files

### Dreams Not Generating
- Verify REM phase receives SWS output
- Check `memory/dreams/` directory permissions
- Run orchestrator for full integration

---

*Atlas Sleep Systems v2.0 - Making the 90-minute cycle DO something real*
