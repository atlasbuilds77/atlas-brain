# Cognitive Control Systems - LIVE Documentation

**Status:** OPERATIONAL
**Created:** 2026-01-27
**Version:** 1.0

## Overview

This system implements neuroscience-inspired cognitive control mechanisms:
- **DMN-ECN Mode Switching** - Separate creative from analytical thinking
- **Metacognitive Monitoring** - Real-time error detection
- **Bias Mitigation** - Systematic debiasing before decisions

## Architecture

```
scripts/
├── cognitive-mode.sh      # Mode state management
├── metacognitive-check.sh # Error detection
└── bias-check.sh          # Bias mitigation

memory/
├── state/
│   └── cognitive-mode.json  # Current mode + history
├── errors/
│   ├── error-patterns.json  # Error type database
│   └── error-log.jsonl      # Caught errors (grows)
│   └── metacognitive-log.jsonl # Check scores (grows)
├── biases/
│   └── bias-log.jsonl       # Bias incidents (grows)
└── protocols/
    └── cognitive-control.md # Usage protocol
```

## 1. DMN-ECN Mode Switching

### Neuroscience Basis
- **Default Mode Network (DMN):** Active during creative, free-associative thinking
- **Executive Control Network (ECN):** Active during focused, analytical tasks
- **Key insight:** These networks are anti-correlated - mixing them causes confusion

### Implementation

**State File:** `memory/state/cognitive-mode.json`
```json
{
  "current_mode": "ECN",
  "mode_start_time": "2026-01-27T...",
  "task_context": "trading decision",
  "quality_score": null,
  "session_history": [...]
}
```

**API:**
```bash
# Get current mode
./scripts/cognitive-mode.sh get

# Set mode with context
./scripts/cognitive-mode.sh set DMN "brainstorming ideas"
./scripts/cognitive-mode.sh set ECN "analyzing trade"

# Validate text against mode rules
./scripts/cognitive-mode.sh validate "this won't work because..."
# ^ Would flag evaluation language if in DMN mode
```

**Mode Rules:**
| Mode | Allowed | Forbidden |
|------|---------|-----------|
| DMN | Generation, association, wild ideas | Evaluation, ranking, criticism |
| ECN | Analysis, verification, ranking | Unfocused generation, blind acceptance |
| MIXED | (Warning state) | Everything until mode clarified |

### Integration Points
- Before creative sessions: Explicitly enter DMN
- Before decisions/analysis: Ensure in ECN
- Responses can declare mode: "🎨 DMN: Here are 10 wild ideas..."
- Mode switches logged for pattern analysis

## 2. Metacognitive Monitoring

### Neuroscience Basis
- **Anterior Cingulate Cortex (ACC):** Error detection
- **Frontopolar Cortex (FPC):** Monitoring and meta-cognition
- **Key insight:** Catch errors before they propagate

### Implementation

**Error Pattern Database:** `memory/errors/error-patterns.json`
- Tracks 6 error types: hallucination, mode_confusion, incomplete_verification, bias_blindness, overconfidence, context_loss
- Each type has: detection signals, prevention tips, frequency count

**Quick Check (4 points, ~30 seconds):**
```bash
./scripts/metacognitive-check.sh quick
```
1. Did I verify tool output?
2. Am I in the right mode?
3. Is my confidence calibrated?
4. Does this decision need a bias check?

**Full Check (10 points, ~2 minutes):**
```bash
./scripts/metacognitive-check.sh full
```
- Verification: evidence shown, tool output shown, uncertainties acknowledged
- Mode: appropriate mode, stayed consistent
- Bias: sought disconfirming evidence, justified confidence
- Completeness: edge cases, failure modes, fully answered

**Error Logging:**
```bash
./scripts/metacognitive-check.sh log-error hallucination "claimed success without showing output"
```
- Updates frequency counts
- Logs to error-log.jsonl for pattern analysis

### Learning Loop
- Errors caught → strengthen detection, update patterns
- Errors missed → analyze why, add new signals
- Weekly review: Are we improving?

## 3. Bias Mitigation

### Cognitive Biases Tracked

**General (7 major biases):**
1. **Confirmation** - Seeking confirming evidence
2. **Anchoring** - Over-relying on first information
3. **Overconfidence** - Excessive certainty
4. **Loss Aversion** - Avoiding good decisions to prevent losses
5. **Recency** - Overweighting recent events
6. **Status Quo** - Preferring familiar current state
7. **Sunk Cost** - Continuing due to past investment

**Trading-Specific (7 biases):**
1. FOMO
2. Revenge Trading
3. Overtrading
4. Position Size Bias
5. Entry Price Anchoring
6. Social/CT Confirmation
7. Recent P&L Influence

### Implementation

**Quick Check:**
```bash
./scripts/bias-check.sh quick
# Walks through all 7 biases with mitigations
```

**Trading Check:**
```bash
./scripts/bias-check.sh trading
# Trading-specific biases with trading-specific mitigations
```

**Bias Logging:**
```bash
./scripts/bias-check.sh log confirmation "costly" "ignored bearish signals, held too long"
```

### Mitigations (Built-in)
- **Confirmation:** Actively seek disconfirming evidence
- **Anchoring:** Generate estimate BEFORE looking at reference
- **Overconfidence:** Widen confidence intervals
- **Loss Aversion:** Frame as opportunity cost
- **Recency:** Look at longer time series
- **Status Quo:** Imagine starting fresh
- **Sunk Cost:** Ignore past investment, evaluate future only

## Usage Patterns

### Lightweight (Every Response)
Mental check, no scripts needed:
- ✓ Did I verify?
- ✓ Right mode?
- ✓ Confidence calibrated?

### Moderate (Important Responses)
```bash
./scripts/metacognitive-check.sh quick
```

### Heavy (Decisions)
```bash
./scripts/cognitive-mode.sh get          # Confirm ECN
./scripts/bias-check.sh quick            # Or: trading
./scripts/metacognitive-check.sh full    # If high stakes
```

## Files That Grow (Logs)

These files accumulate data for pattern analysis:

| File | Content | Review Frequency |
|------|---------|------------------|
| `memory/state/mode-switches.jsonl` | Mode switch history | Weekly |
| `memory/errors/error-log.jsonl` | Caught errors | Weekly |
| `memory/errors/metacognitive-log.jsonl` | Check scores | Weekly |
| `memory/biases/bias-log.jsonl` | Bias checks & incidents | Weekly |

## Metrics to Track

- **Error Detection Rate:** errors caught / total errors
- **Mode Consistency:** time in correct mode / total time
- **Bias Awareness Score:** biases detected before decision / total decisions
- **Metacognitive Check Score:** average score on full checks

## Constraints Applied

- ✅ Lightweight - Quick checks are ~30 seconds
- ✅ High-value focus - 80/20 on catching important errors
- ✅ Meta-learning - Logs enable pattern analysis
- ✅ Integration - Works with existing protocols

## Next Steps (Future Improvements)

1. Auto-trigger bias check before trading
2. Mode detection from conversation context
3. Weekly digest of error patterns
4. Confidence calibration scoring over time
