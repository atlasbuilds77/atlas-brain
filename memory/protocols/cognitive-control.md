# Cognitive Control Protocol

## Quick Reference

### Mode Switching
```bash
# Check current mode
./scripts/cognitive-mode.sh get

# Switch to creative mode (brainstorming)
./scripts/cognitive-mode.sh set DMN "brainstorming session"

# Switch to analytical mode (decisions)
./scripts/cognitive-mode.sh set ECN "trading decision"

# Validate response against current mode
./scripts/cognitive-mode.sh validate "your response text"
```

### Pre-Response Checks
```bash
# Quick check (4 points, fast)
./scripts/metacognitive-check.sh quick

# Full check (10 points, thorough)
./scripts/metacognitive-check.sh full

# Log an error I caught
./scripts/metacognitive-check.sh log-error hallucination "claimed without verifying"
```

### Bias Mitigation
```bash
# General decision check
./scripts/bias-check.sh quick

# Trading-specific check
./scripts/bias-check.sh trading

# Log a bias incident
./scripts/bias-check.sh log confirmation "bad" "ignored contradicting data"
```

## When to Use What

| Context | Mode | Check |
|---------|------|-------|
| Brainstorming | DMN | None (generate freely) |
| Creative writing | DMN | None |
| Research | ECN | Quick metacognitive |
| Trading decisions | ECN | Bias check (trading) |
| Important decisions | ECN | Full metacognitive + bias |
| Code review | ECN | Quick metacognitive |
| Problem solving | DMN → ECN | Start DMN, switch to ECN |

## Mode Reminders

### When in DMN Mode (Creative)
- 🎨 **Generate freely** - no evaluation
- Quantity over quality
- Wild ideas welcome
- Build on ideas, don't filter
- **FORBIDDEN:** ranking, criticism, feasibility checks

### When in ECN Mode (Analytical)  
- 🔬 **Think critically** - verify everything
- Check sources and evidence
- Consider risks and edge cases
- Rank options explicitly
- **FORBIDDEN:** unfocused generation, blind acceptance

### Mode Confusion Signals
- Criticizing during brainstorming ⚠️
- Generating random ideas during analysis ⚠️
- Mixing creative and evaluative in same response ⚠️
- **FIX:** Explicitly declare mode, separate phases

## Integration with Workflows

### Trading Workflow
1. Before any trade: `./scripts/bias-check.sh trading`
2. During analysis: Mode = ECN
3. After trade: Log outcome

### Creative Workflow
1. Set mode: `./scripts/cognitive-mode.sh set DMN`
2. Generate freely (no evaluation!)
3. Switch: `./scripts/cognitive-mode.sh set ECN`
4. Now evaluate and refine

### Decision Workflow
1. Mode check: Am I in ECN?
2. Bias check: `./scripts/bias-check.sh quick`
3. Metacognitive check: `./scripts/metacognitive-check.sh quick`
4. Proceed if all clear

## Error Types to Watch

1. **Hallucination** - Claiming without evidence
2. **Mode Confusion** - Wrong cognitive mode
3. **Incomplete Verification** - Not checking results
4. **Bias Blindness** - Ignoring cognitive biases
5. **Overconfidence** - Certainty without justification
6. **Context Loss** - Forgetting conversation thread

## Lightweight Daily Practice

**Every important response:**
- Quick metacognitive check (mental, 5 seconds)
- Did I verify? Did I consider biases? Is my confidence calibrated?

**Trading decisions:**
- Always run bias-check.sh trading
- No exceptions

**Creative sessions:**
- Explicitly enter DMN mode
- Don't evaluate until switching to ECN
