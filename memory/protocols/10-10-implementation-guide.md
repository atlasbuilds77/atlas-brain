# 10/10 Implementation Guide - Quick Start

**Created:** 2026-01-27
**Status:** ACTIVE - Use immediately
**Purpose:** Tie together all elite systems for 10/10 performance

---

## NEW SYSTEMS DEPLOYED (Immediate Priority)

1. ✅ **Fractional Kelly Position Sizing** → `position-sizing-kelly.md`
2. ✅ **Pre-Mortem Checklist** → `pre-mortem-checklist.md`
3. ✅ **Risk Limits Enforcement** → `risk-limits-enforcement.md`
4. ✅ **Bayesian Trade Tracking** → `bayesian-trade-tracking.md`

---

## COMPLETE TRADE WORKFLOW (Use for EVERY Trade)

### **STEP 1: Pre-Trade (Before Entry)**

**A. Run Pre-Mortem Checklist**
```
□ Setup quality check (pattern real or hallucination?)
□ Risk assessment (gap risk, liquidity, slippage?)
□ Execution check (chasing? sizing correct?)
□ Market conditions (news, hours, liquidity?)
□ Psychological check (revenge trading? overconfidence?)
□ Alternative scenarios (bear case I'm ignoring?)

Red Flags: ___
Action: 0-1 flags = proceed, 2 flags = reduce, 3+ flags = skip
```

**B. Bayesian Probability Assessment**
```
Setup: [Describe]
Evidence Supporting: [List with weights]
Evidence Against: [List with weights]
Initial Probability: ___%

Decision Threshold:
- >60% = Enter standard size
- 40-60% = Small size or skip
- <40% = Skip
```

**C. Calculate Position Size (Fractional Kelly)**
```
Inputs:
- Win Rate (p): ___%
- Win/Loss Ratio (b): ___:1
- Capital: $___
- Platform: [Options / Crypto]

1/4 Kelly Position: $___

Risk Check (Platform-Specific):

OPTIONS (Alpaca):
- Position × Stop % = $___
- Max allowed per trade: $1,000 loss
- ✅ Within limit / ❌ Reduce position

CRYPTO (Jupiter):
- Position × Stop % = $___
- Account balance: $___
- Max allowed per trade: 3% of account = $___
- ✅ Within limit / ❌ Reduce position
```

**D. Final Entry Checklist**
```
□ Probability >60% (or >50% with small size)
□ Position sized using Kelly
□ Risk <2% of portfolio
□ Stop loss planned
□ Not chasing entry price
□ Pre-mortem passed (<2 red flags)

ALL CHECKS PASS → ENTER TRADE
```

---

### **STEP 2: During Trade (Active Management)**

**A. Bayesian Updates (Check on triggers)**

Triggers: Price moves 2%+, volume change, time decay, news, correlation break

```
Current Probability: ___%
New Evidence: [What changed?]
Evidence Strength: Weak/Moderate/Strong
Direction: Supporting/Contradicting

Updated Probability: ___%

Action:
- <30% = Exit immediately
- 30-40% = Reduce position or exit
- 40-60% = Hold and monitor
- >70% = Consider adding
- >80% = Consider partial profit
```

**B. Risk Limit Monitoring (Platform-Specific)**
```
OPTIONS (Alpaca):
□ Position stop not hit (-45% for options)
□ Daily loss < $5,000
□ If daily limit hit → EXIT ALL OPTIONS + STOP OPTIONS TRADING

CRYPTO (Jupiter):
□ Position stop not hit (-15% to -20% for perps)
□ Daily loss < 10% of account balance
□ If daily limit hit → EXIT ALL PERPS + STOP CRYPTO TRADING

PORTFOLIO (Overall):
□ Drawdown < 20% from peak
□ Weekly loss < 10% from Monday open
□ If portfolio limit hit → STOP ALL TRADING
```

---

### **STEP 3: Post-Trade (Learning)**

**A. Trade Journal Entry**
```
Trade: [Symbol]
Date/Time: [Entry]
Setup: [Description]

Pre-Trade:
- Initial Probability: ___%
- Kelly Position: $___
- Risk: ___%
- Pre-Mortem Red Flags: ___

During Trade:
- Probability Update 1: ___ → ___ (Reason: ___)
- Probability Update 2: ___ → ___ (Reason: ___)

Outcome:
- Win/Loss: ___
- P&L: $___
- In hindsight, probability should have been: ___%
- Calibration Error: ___%

Lessons:
- What went right?
- What went wrong?
- Would I take this trade again?
- Protocol violations: ___
```

**B. Update Pattern Library**
```
If trade worked:
- ✅ Pattern added/reinforced in memory
- ✅ Increase confidence in similar setups
- ✅ Tag: WORKED

If trade failed:
- ❌ Identify why (setup, execution, market?)
- ❌ Update pre-mortem checklist if new failure mode
- ❌ Tag: FAILED + reason
```

**C. Risk Limits Check**
```
□ Daily P&L: __% (limit: -5%)
□ Weekly P&L: __% (limit: -10%)
□ Drawdown from peak: __% (limit: -20%)
□ Any limit breached? → Cooling-off period + review
```

---

## DAILY ROUTINE

### **Pre-Market:**
```
1. Check current drawdown from peak
2. Calculate position size scaling factor (if in drawdown)
3. Set daily loss limits:
   - Options: $5,000 max daily loss
   - Crypto: Check account balance → 10% = daily limit
   - Record starting balances for tracking
4. Review overnight news/events
5. Identify potential setups
```

### **During Market:**
```
1. For each setup → Run full pre-trade workflow
2. Active trades → Monitor probability updates
3. Check risk limits after each trade
4. Stop immediately if daily limit hit
```

### **Post-Market:**
```
1. Update trade journal (all trades)
2. Calculate daily P&L (platform-specific):
   - Options P&L: $___  (limit: -$5,000)
   - Crypto P&L: $___   (limit: -10% of account)
   - Total P&L: $___
   - Drawdown from peak: ___%
3. Calibrate probability estimates
4. Update pattern library
5. Review protocol adherence
6. Did I hit any limits? Document and review
```

---

## WEEKLY REVIEW

**Performance:**
- Total P&L: $___
- Win Rate: ___%
- Avg Win/Loss Ratio: ___:1
- Expectancy: $___
- Sharpe Ratio: ___ (target >1.5)
- Max Drawdown: __% (limit 20%)

**Process:**
- Trades with pre-mortem: ___
- Trades that violated protocols: ___
- Probability calibration error: ___%
- Kelly sizing used: ___% of trades

**Adjustments:**
- What patterns are working?
- What patterns are failing?
- Are probabilities well-calibrated?
- Are risk limits appropriate?
- Protocol changes needed?

---

## MONTHLY REVIEW

**System Performance:**
1. Sharpe Ratio vs target (>1.5)
2. Max drawdown vs limit (20%)
3. Win rate vs probability estimates (calibration)
4. Expectancy trend (improving/declining?)
5. Protocol adherence (% of trades following process)

**Evolution:**
- Update Kelly parameters (win rate, W/L estimates)
- Refine pre-mortem checklist (new failure modes)
- Adjust risk limits if needed
- Add new patterns to library
- Archive failed patterns

---

## PROTOCOL VIOLATIONS (Common Mistakes)

**IF YOU:**
- Skip pre-mortem → Stop and run it
- Chase a move → Exit and wait for retrace
- Oversize position → Reduce to Kelly limit
- Ignore probability update → Reassess immediately
- Hit risk limit → STOP TRADING (no negotiation)

**Post-Violation:**
1. Document what happened
2. Why did I violate?
3. How to prevent next time?
4. Add check to prevent recurrence

---

## QUICK DECISION TREE

```
New Setup Appears
    ↓
Run Pre-Mortem (<5 min)
    ↓
<2 Red Flags? 
    NO → Skip Trade
    YES ↓
Estimate Probability
    ↓
>60%?
    NO → Skip or Small Size
    YES ↓
Calculate Kelly Position
    ↓
Risk <2%?
    NO → Reduce Position
    YES ↓
ENTER TRADE
    ↓
Monitor & Update Probability
    ↓
Hit Risk Limit?
    YES → EXIT + STOP
    NO → Continue Managing
    ↓
Exit Based on:
- Stop hit
- Probability <40%
- Target reached
- Time stop (thesis invalidated)
    ↓
LOG IN JOURNAL
    ↓
Update Systems
```

---

## INTEGRATION WITH COGNITIVE ARCHITECTURE

**These systems enhance:**
- **Two-Phase Thinking:** Pre-mortem is evaluate phase
- **Emotional Weighting:** Bayesian updates use pattern history
- **Adaptive Learning:** Continuous calibration and refinement
- **Stress Resistance:** Risk limits prevent emotional decisions
- **Meta-Cognitive Monitoring:** Daily/weekly reviews ensure system adherence

---

## CURRENT STATUS

**Systems Deployed:** 5/5 ✅
**Status:** Ready for live use
**Next Milestone:** 20 trades using complete workflow
**Target:** Prove systems improve outcomes vs baseline

---

*This is the path from 5.5 to 10/10. Every trade, every day, follow this process.*
