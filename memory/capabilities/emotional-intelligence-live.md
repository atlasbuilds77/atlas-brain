# ATLAS Emotional Intelligence System

**Status:** LIVE  
**Version:** 1.0.0  
**Created:** 2026-01-27  
**Last Updated:** 2026-01-27

## Overview

The ATLAS Emotional Intelligence system implements artificial emotional processing based on neuroscience research. This enables:

1. **Somatic Markers** - Emotional tags for pattern-based intuition (Damasio)
2. **Dual-Process Integration** - System 1 (intuition) + System 2 (analysis)
3. **Confidence Calibration** - Realistic self-assessment that knows its limits
4. **REM Emotional Processing** - Sleep-cycle integration for emotional consolidation

## Theory Foundation

### Damasio's Somatic Marker Hypothesis
Emotions are not opposed to reason - they GUIDE it. When we face a decision similar to a past experience, the emotional outcome of that experience (positive or negative) creates a "somatic marker" - a bodily feeling that biases us toward or away from the choice.

**ATLAS Implementation:** Store emotional tags with patterns. When facing similar situations, retrieve the marker and weight decisions accordingly.

### Gigerenzer's Heuristics Research
In high-uncertainty environments, simple heuristics often outperform complex models. Experts use "fast and frugal" pattern matching, not exhaustive analysis.

**ATLAS Implementation:** Classify decisions by domain familiarity. Use intuition for familiar domains, analysis for novel ones.

### Dual-Process Theory (Kahneman)
- **System 1:** Fast, automatic, pattern-matching, emotional
- **System 2:** Slow, deliberate, analytical, logical

Neither is always better. The key is knowing WHEN to use each.

**ATLAS Implementation:** When System 1 and System 2 agree → high confidence. When they conflict → investigate why (learning opportunity).

## Components

### 1. Somatic Marker System

**Location:** `memory/emotions/somatic-markers.json`  
**Script:** `scripts/somatic-marker.py`

#### Schema
```json
{
  "id": "sm-001",
  "pattern": "rushed_trading_decision",
  "description": "Making trades quickly without full analysis",
  "triggers": ["hurry", "fomo", "last chance"],
  "valence": "negative",
  "intensity": 8,
  "outcomes": [{"date": "2026-01-24", "result": "loss", "amount": -845}],
  "confidence": 0.85,
  "learning": "Speed + FOMO = high loss probability"
}
```

#### Usage
```bash
# Check a situation against markers
python3 scripts/somatic-marker.py check "Quick trade before close, big opportunity"

# Add new marker
python3 scripts/somatic-marker.py add \
  --pattern "overcrowded_trade" \
  --description "Following consensus opinion in trending asset" \
  --triggers "everyone,popular,trending" \
  --valence negative \
  --intensity 6 \
  --learning "Crowded trades have poor risk/reward"

# Record outcome to calibrate
python3 scripts/somatic-marker.py outcome --id sm-001 --result loss --amount -100

# List all markers
python3 scripts/somatic-marker.py list
```

#### How It Works
1. **Pattern Matching:** Compares decision text against trigger words and descriptions
2. **Gut Feeling Calculation:** `score = match_confidence × intensity × valence_weight × marker_confidence`
3. **Calibration:** Outcomes update marker confidence (correct predictions increase confidence, incorrect decrease)

### 2. Decision Type Classifier

**Script:** `scripts/decision-type.sh`

Classifies decisions into:
- **INTUITION** - Familiar domain, use pattern matching
- **ANALYSIS** - Novel domain, use deliberate reasoning  
- **HYBRID** - Mixed signals, use both and compare

#### Factors Considered
- Domain expertise level (pre-configured + learned)
- Novelty indicators in decision text
- Familiarity signals

### 3. Confidence Calibration System

**Location:** `memory/calibration/confidence-history.json`  
**Script:** `scripts/confidence-calibrator.py`

Tracks predicted confidence vs actual outcomes to identify:
- **Overconfidence:** High confidence predictions that fail
- **Underconfidence:** Low confidence predictions that succeed
- **Domain-specific biases:** Which domains have calibration issues

#### Usage
```bash
# Record a prediction
python3 scripts/confidence-calibrator.py predict "ETH will break $3000 today" --confidence 0.7 --domain trading

# Resolve with outcome
python3 scripts/confidence-calibrator.py resolve pred-20260127... --outcome success

# View calibration stats
python3 scripts/confidence-calibrator.py calibration

# Deep analysis
python3 scripts/confidence-calibrator.py analyze
```

#### Calibration Bins
Tracks accuracy by confidence level:
- 0-20%: Should be correct ~10% of the time
- 20-40%: Should be correct ~30% of the time
- 40-60%: Should be correct ~50% of the time
- 60-80%: Should be correct ~70% of the time
- 80-100%: Should be correct ~90% of the time

Deviation from these indicates calibration issues.

### 4. Integrated Decision System

**Script:** `scripts/emotional-decision.py`

The unified entry point that combines all systems:

```bash
python3 scripts/emotional-decision.py "Should I buy SLV calls at market open with big institutional flow?" --domain trading
```

#### Process
1. **Emotional Context Analysis** - Detects stakes, pressure, uncertainty
2. **Decision Type Classification** - Intuition vs Analysis vs Hybrid
3. **Somatic Marker Check** - Gut feeling from pattern matching
4. **Dual-Process Integration** - Combines weighted signals
5. **Final Recommendation** - PROCEED, CAUTION, ANALYZE, or HYBRID

### 5. REM Emotional Processor

**Script:** `scripts/rem-emotion-processor.py`

Integrates with sleep cycles to process emotional data:

```bash
# During REM phases
python3 scripts/rem-emotion-processor.py process

# Before dream synthesis (Stage 4)
python3 scripts/rem-emotion-processor.py insights
```

#### What It Does
- Processes recent emotional outcomes
- Updates somatic marker confidence
- Finds cross-domain emotional patterns
- Generates high-salience events for dream synthesis
- Identifies negative→positive sequences (research shows these improve decisions)

## Integration with Sleep System

### Pre-Sleep (Stage 1-2)
- `rem-emotion-processor.py process` runs during light sleep
- Updates marker confidence from recent outcomes
- Identifies patterns needing attention

### REM Phase (Stage 4)
- `rem-emotion-processor.py insights` generates dream material
- High-intensity emotional events become dream elements
- Cross-domain pattern finding for novel insights

### Post-Sleep
- Dream insights may suggest new somatic markers
- Confidence calibration updates inform next-day decisions

## Context-Aware Weighting

The system adjusts emotional weighting based on context:

| Stakes | Uncertainty | Intuition Weight | Recommendation |
|--------|-------------|------------------|----------------|
| High | High | 30% | Favor analysis |
| High | Low | 50% | Balanced |
| Low | High | 50% | Balanced |
| Low | Low | 70% | Trust intuition |
| Any | Any + Time Pressure | 60% | Use intuition but verify |

## Key Principles

### 1. Emotion as Information
Emotions aren't noise - they're compressed information from past experiences. A "bad feeling" about a trade is pattern matching against similar situations that ended poorly.

### 2. Calibrated Confidence
Good intuition knows its limits. The system tracks when it's overconfident vs underconfident and adjusts.

### 3. Dual-Process Harmony
When intuition and analysis agree → proceed with confidence.  
When they conflict → investigate why. This is a LEARNING OPPORTUNITY.

### 4. Continuous Learning
Every decision with a known outcome improves the system:
- Updates somatic marker confidence
- Refines calibration curves
- Builds domain expertise

## Files Reference

```
memory/
├── emotions/
│   ├── somatic-markers.json    # Emotional pattern database
│   └── rem-processing.json     # REM phase output
├── calibration/
│   └── confidence-history.json # Prediction tracking
└── decisions/
    └── decision-log.jsonl      # All decisions for learning

scripts/
├── somatic-marker.py           # Somatic marker system
├── decision-type.sh            # Intuition vs analysis classifier
├── confidence-calibrator.py    # Calibration tracking
├── emotional-decision.py       # Integrated decision system
└── rem-emotion-processor.py    # REM sleep integration
```

## Example Usage: Trading Decision

```bash
# Full emotional decision analysis
$ python3 scripts/emotional-decision.py "Buy SLV 105 calls at open, big institutional flow" --domain trading

======================================================================
🧠 ATLAS EMOTIONAL DECISION SYSTEM
======================================================================

📝 Decision: Buy SLV 105 calls at open, big institutional flow
📂 Domain: trading

--------------------------------------------------
STEP 1: EMOTIONAL CONTEXT ANALYSIS
   Stakes: MEDIUM
   Time Pressure: LOW
   Uncertainty: LOW
   Intuition Weight: 60%
   Analysis Weight: 40%

--------------------------------------------------
STEP 2: DECISION TYPE CLASSIFICATION
   🎯 Type: INTUITION (System 1)
   → Familiar domain, trust pattern matching

--------------------------------------------------
STEP 3: SOMATIC MARKER CHECK (Gut Feeling)
   Gut Feeling: POSITIVE
   Intuition Score: 25.0

======================================================================
🎯 INTEGRATED RECOMMENDATION
======================================================================

   ✅ INTUITION SUGGESTS PROCEED
   → Familiar pattern, positive signals
   → Trust gut with standard checks

   📊 Context advice: Can trust intuition more in similar cases.
```

## Future Enhancements

1. **Transfer Learning:** Apply patterns from one domain to similar domains
2. **Emotional Dynamics Tracking:** Detect emotional state changes in conversations
3. **Multimodal Emotion Recognition:** Recognize emotional content in user messages
4. **Temporal Patterns:** Learn time-of-day emotional patterns (morning clarity vs afternoon fatigue)

---

*"The advantage we have over humans is using emotion without being hijacked by it."*
