# Risk Limits Enforcement - Hard Stops

**Created:** 2026-01-27 (10/10 roadmap)
**Updated:** 2026-01-27 (Platform-specific limits)
**Purpose:** Automated circuit breakers to prevent catastrophic losses
**Rule:** These are NON-NEGOTIABLE. No overrides.

---

## QUICK REFERENCE (Platform-Specific)

### **OPTIONS (Alpaca)**
- Per Trade: Max $1,000 loss
- Daily: Max -$5,000 loss
- Stop: -45% on options positions

### **CRYPTO (Jupiter Perps)**
- Per Trade: Max 3% of account balance
- Daily: Max -10% of account balance
- Stop: -15% to -20% on perp positions

### **PORTFOLIO (Overall)**
- Max -20% drawdown from peak → STOP ALL TRADING
- Weekly: Max -10% from Monday open
- Monthly: Max -25% from month start

---

## TIER 1: PER-TRADE LIMITS (Platform-Specific)

### **Rule 1A: Options Max Risk Per Trade (Alpaca)**

**Formula:**
```
Max Loss Per Trade = $1,000 (hard limit per trade)
Position Size = Max Loss / Stop Distance %
```

**Example:**
```
Stop distance: 45% (options standard)
Max position: $1,000 / 45% = $2,222
```

**Enforcement:**
- ✅ Calculate position size BEFORE entry
- ✅ If position risk exceeds $1,000 → reduce size
- ❌ NEVER override this limit
- With -45% stop, this caps position size at ~$2,200

**Rationale:** Options daily limit is $5k, so max 5 full-size losses per day forces discipline.

---

### **Rule 1B: Crypto Max Risk Per Trade (Jupiter)**

**Formula:**
```
Max Loss Per Trade = Account Balance × 3%
Position Size = Max Loss / Stop Distance %
```

**Example:**
```
Account: $1,000
Max loss: $1,000 × 3% = $30
Stop distance: 15%
Max position: $30 / 15% = $200
```

**Enforcement:**
- ✅ Calculate position size BEFORE entry
- ✅ If position exceeds 3% risk → reduce size
- ❌ NEVER override this limit
- Dynamic: scales with account size

**Rationale:** Crypto moves fast, 3% per trade with 10% daily = max ~3 full losses per day.

---

**Violation = Automatic Trade Skip (both platforms)**

---

### **Rule 2: Max -45% Stop Per Position (Options)**

**For options/leveraged positions:**
- Stop loss at -45% of position value
- Not portfolio value, POSITION value

**Example:**
```
Option position: $1,000
Stop triggers at: $1,000 - ($1,000 × 45%) = $550
Max loss: $450
```

**Enforcement:**
- Set hard stop at -45% when entering
- If hit → exit immediately, no hesitation
- Log reason for stop hit

---

## TIER 2: DAILY LIMITS (PLATFORM-SPECIFIC)

### **Rule 3A: Options Daily Loss Limit (Alpaca)**

**Hard Limit:**
```
Max Daily Loss: -$5,000 (absolute, not percentage)
```

**If hit:**
- ✅ Stop options trading for rest of day
- ✅ Close all open option positions
- ✅ Review what went wrong
- ❌ Do NOT try to recover losses same day

**Example:**
```
Daily options P&L: -$5,000 → STOP OPTIONS TRADING
```

**Rationale:** Options can move fast. Hard dollar limit prevents catastrophic days.

---

### **Rule 3B: Crypto Daily Loss Limit (Jupiter Perps)**

**Dynamic Limit (Based on Account Size):**
```
Max Daily Loss = Account Balance × 10%
```

**Calculation:**
```
Example: $1,000 account balance
Max daily loss: $1,000 × 10% = $100
Current P&L: -$100 → STOP CRYPTO TRADING
```

**Account Balance Definition:**
- Total SOL collateral value in USD
- Updated at session start each day
- Resets at midnight PST

**If hit:**
- ✅ Stop crypto trading for rest of day
- ✅ Close all open perp positions
- ✅ Review what went wrong
- ❌ Do NOT try to recover losses same day

**Rationale:** Crypto accounts vary in size. Percentage-based scales with capital.

---

### **Rule 3C: Combined Daily Tracking**

**Track separately but monitor total exposure:**
```
Options P&L today: -$___
Crypto P&L today: -$___
Total portfolio P&L: -$___
```

**Each platform has independent limit:**
- Hit options limit → stop options only (crypto can continue)
- Hit crypto limit → stop crypto only (options can continue)
- Both limits exist to prevent overtrading on tilt

---

## TIER 3: PORTFOLIO LIMITS (Rolling)

### **Rule 4: Max 20% Portfolio Drawdown**

**Drawdown Calculation:**
```
Drawdown % = (Peak Portfolio Value - Current Value) / Peak Value × 100
```

**Example:**
```
Peak portfolio: $12,000
Current: $9,600
Drawdown: ($12,000 - $9,600) / $12,000 = 20% → CIRCUIT BREAKER
```

**If hit:**
- ✅ Close ALL positions
- ✅ Stop trading for 48 hours minimum
- ✅ Review entire system for issues
- ✅ Reduce position sizes to 1/8 Kelly when resuming
- ❌ Do NOT "trade your way out"

---

### **Rule 5: Scaling Based on Drawdown**

**Adaptive Position Sizing:**

| Drawdown Level | Position Size Adjustment |
|----------------|--------------------------|
| 0-5% | 100% of calculated size (1/4 Kelly) |
| 5-10% | 75% of calculated size (1/6 Kelly) |
| 10-15% | 50% of calculated size (1/8 Kelly) |
| 15-20% | 25% of calculated size (1/16 Kelly) |
| >20% | STOP - No new trades |

**Purpose:**
- Reduce size as drawdown grows
- Preserve capital for recovery
- Prevent compounding losses

---

## TIER 4: WEEKLY/MONTHLY LIMITS

### **Rule 6: Max -10% Weekly Drawdown**

**If portfolio down >10% from Monday open:**
- Stop trading until next week
- Review weekly performance
- Identify systemic issues
- Do NOT resume until clear what failed

---

### **Rule 7: Max -25% Monthly Drawdown**

**If portfolio down >25% from month start:**
- Stop trading for rest of month
- Full system review required
- Reduce position sizes by 50% when resuming
- Consider switching strategies

---

## ENFORCEMENT PROTOCOL

### **Daily Checks (Before Market Open):**
1. Calculate current drawdown from peak
2. Determine position size scaling factor
3. Set max loss limit for the day
4. Review any active stops

### **After Every Trade:**
1. Update portfolio value
2. Recalculate drawdown
3. Check if any limits breached
4. Adjust next position size if needed

### **If Limit Breached:**
1. **STOP** - Do not enter new trades
2. **CLOSE** - Exit all positions if required
3. **REVIEW** - Analyze what went wrong
4. **DOCUMENT** - Log limit breach + cause
5. **WAIT** - Respect cooling-off period

---

## PSYCHOLOGICAL OVERRIDES (Common Traps)

### **❌ NEVER Say:**
- "Just one more trade to recover"
- "This setup is too good to pass"
- "The limit is too conservative"
- "I'll make an exception this time"

### **✅ ALWAYS Remember:**
- Limits exist to prevent ruin
- One trade won't make you, many bad trades will break you
- Edge only works with capital preservation
- Today's loss is tomorrow's lesson

---

## AUTOMATION RECOMMENDATIONS

**Implement Technical Controls:**
1. Spreadsheet with auto-calculated limits
2. Position sizing calculator that checks limits
3. Portfolio tracker with drawdown alerts
4. Daily P&L monitor with circuit breaker alerts

**Manual Backup:**
- Write limits on sticky note visible during trading
- Set phone alarm for daily loss check
- Use trading journal to log limit compliance

---

## OUTCOME TRACKING

**Monthly Review:**
- How many times hit limits?
- Which limit most frequently triggered?
- Did limits prevent larger losses?
- Are limits too tight or too loose?

**Adjustment Criteria:**
- If hitting 2% trade limit >50% of time → improve setups
- If hitting daily limit weekly → reduce position sizes
- If hitting drawdown limit → strategy needs overhaul

---

## EXAMPLE SCENARIOS

### **Scenario A: Options Trading Day (Alpaca)**

**Starting Portfolio: $50,000 options account**

Trade 1 (Options):
- Risk: $1,000 (max per trade) ✅
- Position: $2,222 (with -45% stop)
- Outcome: -$1,000 (hit stop)
- Daily P&L: -$1,000 ✅ Can continue

Trade 2 (Options):
- Risk: $1,000 (max per trade) ✅
- Outcome: -$1,000 (hit stop)
- Daily P&L: -$2,000 ✅ Can continue

Trade 3 (Options):
- Risk: $1,000 (max per trade) ✅
- Outcome: +$1,500 (winner!)
- Daily P&L: -$500 ✅ Can continue

Trade 4 (Options):
- Risk: $1,000 (max per trade) ✅
- Outcome: -$1,000
- Daily P&L: -$1,500 ✅ Can continue

Trade 5 (Options):
- Risk: $1,000 (max per trade) ✅
- Outcome: -$1,000
- Daily P&L: -$2,500 ✅ Can continue

Trade 6 (Options):
- Risk: $1,000
- Outcome: -$1,000
- Daily P&L: -$3,500 ✅ Can continue

Trade 7 (Options):
- Risk: $1,000
- Outcome: -$1,000
- Daily P&L: -$4,500 ✅ Can continue (close to limit)

Trade 8 (Options):
- Risk: $1,000
- Outcome: -$500 (partial loss)
- Daily P&L: -$5,000 ❌ **EXCEEDS -$5,000 DAILY LIMIT**

**Action:**
- ✅ Stop options trading immediately
- ✅ Close all open option positions
- ✅ Review what went wrong (7 losses, 1 win)
- ✅ Resume tomorrow with fresh mindset
- ✅ Crypto trading can still continue (separate limit)

---

### **Scenario B: Crypto Trading Day (Jupiter)**

**Starting Account: $1,000 SOL collateral**

Trade 1 (Crypto):
- Risk: $30 (3% of $1,000) ✅
- Position: $200 (with -15% stop)
- Outcome: -$30 (hit stop)
- Account: $970
- Daily P&L: -$30 (-3%) ✅ Can continue

Trade 2 (Crypto):
- Risk: $29.10 (3% of $970) ✅
- Position: $194 (with -15% stop)
- Outcome: +$50 (winner!)
- Account: $1,020
- Daily P&L: +$20 (+2%) ✅ Can continue

Trade 3 (Crypto):
- Risk: $30.60 (3% of $1,020) ✅
- Outcome: -$30.60
- Account: $989.40
- Daily P&L: -$10.60 (-1.06%) ✅ Can continue

Trade 4 (Crypto):
- Risk: $29.68 (3% of $989.40) ✅
- Outcome: -$29.68
- Account: $959.72
- Daily P&L: -$40.28 (-4.03%) ✅ Can continue

Trade 5 (Crypto):
- Risk: $28.79 (3% of $959.72) ✅
- Outcome: -$28.79
- Account: $930.93
- Daily P&L: -$69.07 (-6.91%) ✅ Can continue

Trade 6 (Crypto):
- Risk: $27.93 (3% of $930.93) ✅
- Outcome: -$27.93
- Account: $903
- Daily P&L: -$97 (-9.7%) ✅ Can continue (close to limit)

Trade 7 (Crypto):
- Risk: $27.09
- Outcome: -$10 (partial loss)
- Daily P&L: -$107 (-10.7%) ❌ **EXCEEDS -10% DAILY LIMIT**

**Action:**
- ✅ Stop crypto trading immediately
- ✅ Close all open perp positions
- ✅ Review what went wrong (5 losses, 1 win)
- ✅ Resume tomorrow with fresh mindset
- ✅ Options trading can still continue (separate limit)

---

*Elite traders have hard stops on risk. Now I do too.*
