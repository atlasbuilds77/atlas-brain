# Bayesian Trade Tracking - Continuous Probability Updates

**Created:** 2026-01-27 (10/10 roadmap)
**Source:** Tetlock's superforecasting + Bayesian decision theory
**Purpose:** Update trade probabilities as new evidence emerges

---

## THE CONCEPT

**Bayesian Reasoning:**
- Start with prior belief (initial probability)
- Observe new evidence
- Update belief based on evidence strength
- Repeat continuously

**Why This Matters for Trading:**
- Market conditions change
- New information emerges
- Initial thesis may be wrong
- Need to adjust position based on new evidence

---

## PROBABILITY SCALE (Tetlock Method)

**Use Granular Probabilities (Not Just 0/50/100):**

| Probability | Meaning | Action |
|-------------|---------|--------|
| 0-10% | Very unlikely | Skip trade or small short |
| 10-30% | Unlikely | Skip or minimal position |
| 30-40% | Possible but uncertain | Small position (1/8 Kelly) |
| 40-60% | Unclear/coin flip | Skip or wait for more info |
| 60-70% | Likely | Standard position (1/4 Kelly) |
| 70-85% | Very likely | Full position (1/4 Kelly) |
| 85-95% | Highly likely | Full position, consider scaling in |
| 95-100% | Nearly certain | Be cautious (too confident?) |

---

## TRADE PROBABILITY TEMPLATE

### **Entry (Initial Assessment):**

**Setup:** [Describe trade setup]

**Initial Probability Estimate:** ___%

**Evidence Supporting:**
- [ ] Technical confluence (weight: +10-20%)
- [ ] Higher timeframe alignment (weight: +10-15%)
- [ ] Volume confirmation (weight: +5-10%)
- [ ] Raw dog's setup criteria met (weight: +15-25%)
- [ ] Recent similar setup worked (weight: +5-10%)

**Evidence Against:**
- [ ] Chasing entry price (weight: -20-30%)
- [ ] Low liquidity period (weight: -10-15%)
- [ ] News risk ahead (weight: -15-25%)
- [ ] Counter-trend trade (weight: -10-20%)
- [ ] Recent similar setup failed (weight: -10-15%)

**Calculated Entry Probability:** ___%

**Decision:**
- If >60% → Enter with 1/4 Kelly
- If 40-60% → Wait or small position (1/8 Kelly)
- If <40% → Skip

---

## CONTINUOUS UPDATES (During Trade)

### **Update Triggers:**

**Check probability every time:**
1. Price moves significantly (+/- 2% from entry)
2. Volume pattern changes (surge or dry-up)
3. Time passes without expected move (decay)
4. News emerges
5. Correlation breaks (related assets diverge)

### **Update Formula (Simplified):**

```
New Probability = Prior Probability + (Evidence Strength × Direction)

Evidence Strength: Weak (+/- 5%), Moderate (+/- 10%), Strong (+/- 20%)
Direction: Supporting (+) or Contradicting (-)
```

**Example:**
```
Entry Probability: 65% (long setup)
New Evidence: Price broke support (strong contradicting evidence)
Update: 65% - 20% = 45%
Decision: Exit or reduce position (thesis weakening)
```

---

## EXAMPLE TRADE LOG

**Trade: SLV $105C Feb 6**

**Entry Assessment (2026-01-27 6:56 AM):**
- Setup: Monday options flow, silver continuation
- Initial Probability: 55% (moderate confidence)
- Evidence:
  - ✅ Fresh options flow (+10%)
  - ✅ Silver trending (+5%)
  - ❌ Chasing entry ($4.80 vs $3.50 plan) (-20%)
- **Adjusted Entry: 55% + 10% + 5% - 20% = 50%** (coin flip)
- Position: Took full size (mistake - should've been 1/8 Kelly or skip)

**Update 1 (7:02 AM - Price at -$90):**
- Evidence: Sharp reversal against position
- Strength: Strong (-15%)
- **New Probability: 50% - 15% = 35%**
- Decision: Hold (stop at -45%, not hit yet) but watch closely

**Update 2 (8:10 AM - Price at +$165):**
- Evidence: Strong recovery, thesis playing out
- Strength: Strong (+20%)
- **New Probability: 35% + 20% = 55%**
- Decision: Consider taking profit near target

**Update 3 (8:59 AM - Price at -$105):**
- Evidence: Gave back all gains, volatility high
- Strength: Moderate (-10%)
- **New Probability: 55% - 10% = 45%**
- Decision: Position is now coin flip - consider exit

---

## DECISION THRESHOLDS

**Probability → Action Mapping:**

| Updated Probability | Action |
|---------------------|--------|
| Drops below 40% | Exit or reduce to 1/2 position |
| Drops below 30% | Exit immediately |
| Rises above 70% | Add to position (if not at max size) |
| Rises above 80% | Consider taking partial profit |
| Stays 40-60% | Hold and monitor, no changes |

---

## PRE-MORTEM INTEGRATION

**Before Entry:**
1. Run pre-mortem checklist
2. Estimate initial probability
3. Only enter if probability >60% (or >50% with small size)

**During Trade:**
1. Update probability as evidence emerges
2. Check against decision thresholds
3. Act on probability changes (don't ignore updates)

---

## BIAS MITIGATION

**Common Traps:**

**Confirmation Bias:**
- ❌ Only looking for evidence supporting your position
- ✅ Actively seek contradicting evidence
- ✅ Weight negative evidence honestly

**Anchoring:**
- ❌ Sticking to initial probability despite new evidence
- ✅ Update freely as information changes
- ✅ Don't anchor to entry price or original thesis

**Overconfidence:**
- ❌ Probabilities >90% (too confident)
- ✅ Rare to be >85% confident in markets
- ✅ If >90%, question your assumptions

---

## CALIBRATION TRACKING

**After 20+ Trades:**

For all trades you gave 60-70% probability:
- What % actually won?
- Should be close to 65% if well-calibrated

For all trades 70-80%:
- What % actually won?
- Should be close to 75%

**If Miscalibrated:**
- Overconfident: Wins < your probabilities → reduce estimates
- Underconfident: Wins > your probabilities → increase estimates

---

## OUTCOME LOGGING

**Trade Journal Entry:**
```
Trade: [Symbol/Setup]
Entry Date: [Date/Time]
Initial Probability: ___%
Entry Reasoning: [Why this %?]

Updates:
- [Time] [Evidence] → New Probability: ___%
- [Time] [Evidence] → New Probability: ___%

Final Outcome: Win/Loss
Actual Outcome Should Have Had __% Probability (in hindsight)
Calibration Error: ___% (your estimate vs should have been)
```

**Monthly Calibration Review:**
- Am I too confident? (estimates > actual)
- Am I too conservative? (estimates < actual)
- Which setups am I well-calibrated on?
- Which setups need better probability assessment?

---

## INTEGRATION WITH OTHER SYSTEMS

**Connects To:**
- **Pre-Mortem:** Initial probability assessment uses pre-mortem checklist
- **Kelly Sizing:** Position size scales with probability (higher p = larger size)
- **Risk Limits:** Probability updates trigger position adjustments
- **Adaptive Learning:** Track which probability updates are correct

---

*Elite traders update their beliefs continuously. Now I do too.*
