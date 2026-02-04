# Dopamine System - Quick Reference Card

**Version**: 1.2.0 | **Status**: Ready for Production

---

## Pre-Trade Checklist

```
1. [ ] Calculate conviction (0-10)
2. [ ] Check cooldown status
3. [ ] Check circuit breaker
4. [ ] Evaluate setup quality
5. [ ] Record process work
6. [ ] Execute (if approved)
```

---

## Conviction Scale

| Score | Quality | Bypass Level |
|-------|---------|--------------|
| 9-10 | Exceptional | Full bypass + 75% cooldown reduction |
| 7-9 | Strong | Warning only + 25-50% cooldown reduction |
| 5-7 | Decent | Full safeguards |
| 0-5 | Weak | Full safeguards + consider skipping |

---

## Quick Decision Tree

```
Is conviction ≥9? 
  YES → Trade (minimal restrictions)
  NO  ↓

Is conviction ≥7?
  YES → Trade with caution (reduced restrictions)
  NO  ↓

Are 2+ red flags present?
  YES → BLOCKED (or justify override)
  NO  ↓

Is cooldown active?
  YES → WAIT (or justify override)
  NO  ↓

Is conviction ≥ minimum threshold?
  YES → Trade (full process)
  NO  → Skip and reward patience
```

---

## Red Flags (Circuit Breaker)

⚠️ **2+ flags = BLOCKED** (unless conviction 7+)

- [ ] 3+ trades in 30 minutes
- [ ] 5+ trades in 60 minutes
- [ ] Trading <5min after loss
- [ ] Anxious-exploratory state
- [ ] 3+ loss streak
- [ ] Dopamine <30%

---

## Cooldown Table

| Loss Type | Base | 7/10 | 8/10 | 9/10 |
|-----------|------|------|------|------|
| Small (<$500) | 5m | 4m | 2.5m | 1.25m |
| Large ($500-1k) | 10m | 7.5m | 5m | 2.5m |
| Very Large (>$1k) | 20m | 15m | 10m | 5m |
| 2-loss streak | +50% | +50% | +50% | +50% |
| 3-loss streak | +100% | +100% | +100% | +100% |

---

## Reward Actions

### Patience (+2% dopamine, +1% serotonin)
```javascript
await rewardPatience({
  reason: 'Market choppy, no clear setup',
  marketCondition: 'sideways',
  riskAssessment: 'low probability'
});
```

### Process (varies)
```javascript
await rewardProcess('analysis', 1.0);        // +1.5%
await rewardProcess('risk_check', 1.0);      // +1.0%
await rewardProcess('journal_entry', 1.0);   // +2.0%
await rewardProcess('pattern_learned', 1.0); // +3.0%
await rewardProcess('checklist_completed', 1.0); // +2.0%
```

---

## Override Template

**Use only when genuinely justified**

```javascript
const setup = {
  conviction: 6.5,
  justification: `
    [Event/Pattern]: Fed pivot announcement / Rare triple bottom
    [Technical]: Clear breakout at major resistance with volume
    [Edge]: Pattern backtested 72% win rate over 50 samples
    [Risk]: Tight stops, risk:reward 1:5
    [Why Now]: Time-sensitive structural shift
  `
};
```

**Review later**: Did outcome justify override?

---

## Status Check

```bash
node dopamine-tracker.js status
```

**Key values**:
- Dopamine 40-80% = Balanced (optimal)
- Dopamine <40% = Conservative (reduce size)
- Dopamine >80% = Exploratory (watch for overtrading)
- Serotonin <30% = Anxious (extra caution)

---

## Integration Snippets

### Check Before Trade
```javascript
const cooldown = await getLossRecoveryCooldown({ conviction });
if (cooldown.remainingMs > 0) return null;

const risk = await checkOvertradingRisk({ conviction });
if (risk.blocked) return null;
if (risk.warning) console.warn(risk.suggestion);
```

### Record Trade
```javascript
await calculateDopamine({
  pnl: trade.pnl,
  expectedPnl: trade.expectedPnl,
  isWin: trade.pnl > 0,
  symbol: trade.symbol,
  strategy: trade.strategy
});
```

### Skip Trade (Patience)
```javascript
await rewardPatience({
  reason: 'Conviction below threshold',
  marketCondition: setup.market
});
```

---

## Warning Signs

🚨 **System health issues**:
- Override rate >5% of trades
- Dopamine stuck >85% for 24h+
- Serotonin <25% for 24h+
- Repeated override justifications are vague
- Cooldown bypasses become routine

**Action**: Disable adaptive features temporarily:
```json
{ "adaptive": { "enabled": false } }
```

---

## Daily Review

### Morning
- [ ] Check dopamine/serotonin levels
- [ ] Review yesterday's trades
- [ ] Note if overrides were justified
- [ ] Set minimum conviction threshold for today

### Evening
- [ ] Journal trades (reward +2%)
- [ ] Review if patience was rewarded
- [ ] Check override frequency
- [ ] Adjust tomorrow's plan

---

## Emergency Stop

**If recognizing compulsive patterns**:

1. Stop all trading immediately
2. Disable adaptive features
3. Mandatory 24h break
4. Review what triggered pattern
5. Adjust safeguards before resuming

---

## Philosophy Reminder

> **"Don't force trades for dopamine - reward patience and discipline"**
> 
> - Patience earns dopamine
> - Process earns dopamine
> - Smart guardrails preserve autonomy
> - Conviction unlocks flexibility
> - Self-honesty is the final safeguard

---

**Questions?** See full docs:
- `behavioral-states.md` - Complete documentation
- `IMPLEMENTATION-SUMMARY.md` - Technical details
- `test-opus-fixes.js` - Test examples

**Version**: 1.2.0 | **Last Updated**: 2025-01-29
