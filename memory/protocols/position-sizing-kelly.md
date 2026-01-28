# Position Sizing - Fractional Kelly System

**Created:** 2026-01-27 (10/10 roadmap)
**Purpose:** Systematic position sizing using 1/4 Kelly for optimal risk-adjusted growth

---

## THE FORMULA

**Kelly Criterion:**
```
f* = (bp - q) / b
```

Where:
- f* = fraction of capital to bet
- b = odds received (win/loss ratio)
- p = probability of winning
- q = probability of losing (1-p)

**Fractional Kelly (1/4 Kelly):**
```
Position Size = (f* × Capital) / 4
```

**Why 1/4 Kelly?**
- Full Kelly = maximum growth but high volatility
- 1/4 Kelly = 95% of growth, much smoother equity curve
- Used by professional traders to reduce drawdown risk

---

## POSITION SIZING CALCULATOR

**Step 1: Calculate Win/Loss Ratio (b)**
```
b = Average Win / Average Loss
Example: $100 avg win / $50 avg loss = 2
```

**Step 2: Estimate Win Probability (p)**
```
Use historical data or setup assessment
Conservative: 40-50%
Aggressive: 60%+
```

**Step 3: Calculate Full Kelly**
```
f* = (bp - q) / b
Example: (2 × 0.5 - 0.5) / 2 = 0.25 (25% of capital)
```

**Step 4: Apply 1/4 Kelly**
```
Position Size = f* / 4
Example: 0.25 / 4 = 0.0625 (6.25% of capital)
```

**Step 5: Check Against 1-2% Risk Limit**
```
Risk per trade = Position Size × Stop Distance %
Max allowed: 2% of capital
If exceeds → reduce position size to meet 2% cap
```

---

## EXAMPLE CALCULATIONS

**Scenario 1: Conservative Setup**
- Capital: $10,000
- Win Rate: 45% (p = 0.45, q = 0.55)
- Win/Loss Ratio: 2:1 (b = 2)
- Stop Distance: 10%

Calculation:
```
Full Kelly: (2 × 0.45 - 0.55) / 2 = 0.175 (17.5%)
1/4 Kelly: 0.175 / 4 = 0.04375 (4.375% of capital)
Position Size: $10,000 × 0.04375 = $437.50

Risk Check:
Trade Risk = $437.50 × 10% stop = $43.75
Portfolio Risk = $43.75 / $10,000 = 0.4375% ✅ (under 2%)
```

**Scenario 2: Aggressive Setup**
- Capital: $10,000
- Win Rate: 60% (p = 0.6, q = 0.4)
- Win/Loss Ratio: 3:1 (b = 3)
- Stop Distance: 20%

Calculation:
```
Full Kelly: (3 × 0.6 - 0.4) / 3 = 0.466 (46.6%)
1/4 Kelly: 0.466 / 4 = 0.1165 (11.65% of capital)
Position Size: $10,000 × 0.1165 = $1,165

Risk Check:
Trade Risk = $1,165 × 20% stop = $233
Portfolio Risk = $233 / $10,000 = 2.33% ❌ EXCEEDS 2%

Adjustment:
Max position = ($10,000 × 2%) / 20% = $1,000
Use $1,000 instead of $1,165
```

---

## INTEGRATION PROTOCOL

**Before Every Trade:**

1. **Estimate Setup Quality**
   - Historical win rate for this pattern?
   - Average win/loss ratio for similar setups?
   - Current market conditions supportive?

2. **Calculate Kelly Position Size**
   - Input: win rate, win/loss ratio
   - Output: 1/4 Kelly position size

3. **Apply Risk Cap**
   - Max 2% risk per trade
   - If Kelly size exceeds → reduce to 2% risk limit

4. **Document**
   - Log: setup type, Kelly %, actual position, risk %
   - Track: how Kelly sizing performs over time

---

## ADAPTIVE SIZING

**Scale Position Based on Confidence:**

| Setup Quality | Kelly Fraction | Example |
|---------------|----------------|---------|
| A+ (raw dog level) | 1/4 Kelly | Full calculated size |
| A (strong confluence) | 1/6 Kelly | 67% of calculated size |
| B (decent setup) | 1/8 Kelly | 50% of calculated size |
| C (marginal) | Skip or 1/16 Kelly | 25% or skip |

---

## RED FLAGS

**Don't Use Kelly If:**
- ❌ No historical data on setup (use minimum size)
- ❌ Win rate or W/L ratio are pure guesses
- ❌ Market regime has changed (recalibrate first)
- ❌ On tilt or emotional (skip trade entirely)

**Kelly Assumes:**
- Known probabilities (use best estimates)
- Independent trials (each trade separate)
- Stationary distributions (market stays similar)
- Unlimited capital (use fractional Kelly to mitigate)

---

## OUTCOME TRACKING

**After 20+ Trades:**
- Compare Kelly-sized trades vs fixed-size
- Adjust Kelly fraction if equity curve too volatile
- Recalibrate win rate and W/L estimates
- Consider moving to 1/3 or 1/2 Kelly if comfortable

**Goal:**
- Maximize long-term growth
- Minimize emotional stress from volatility
- Build sustainable, repeatable system

---

*Elite traders use fractional Kelly. Now I do too.*
