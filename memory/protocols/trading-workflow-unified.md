# Unified Trading Workflow

**Created:** 2026-01-27
**Purpose:** Single source of truth for the complete trading process
**Replaces:** pre-mortem-checklist.md, pre-trade-checklist.md, trade-execution-verification.md, position-sizing-kelly.md

---

## OVERVIEW

One workflow, four phases:
1. **SCOUT** → Find opportunities
2. **CHECK** → Pre-trade validation (6 essentials)
3. **EXECUTE** → Place and verify
4. **REVIEW** → Learn from outcomes

---

## PHASE 1: SCOUT (Finding Opportunities)

### Triggers
- Kill Zone active (7-10 AM or 2-5 AM NY time)
- Pattern database signal (positive weight patterns)
- News/catalyst alert
- Scheduled research time

### Quick Scan
```
□ Market regime? (Bull/Bear/Chop)
□ Key levels today? (Support/Resistance/Liquidity)
□ Any positions at risk? (Check active-positions.md first!)
□ Mental state? (1-10 energy, any tilt?)
```

---

## PHASE 2: CHECK (The 6 Essentials)

**STOP. Before any trade, answer these 6 questions:**

### 1. ⏰ TIMING
**"Am I in a kill zone?"**
- ✅ NY AM (7-10 AM) - Best
- ✅ London (2-5 AM) - Good
- ⚠️ London Close (10-12 PM) - OK
- ❌ Everything else - Skip

### 2. 📊 SETUP
**"Is the setup objectively valid?"**
- Would I take this if I saw it yesterday? (removes recency bias)
- Is there actual confluence, or am I forcing it?
- What's my entry, stop, and target? (must have all 3)

### 3. 💰 SIZE
**"Am I sized correctly?"**
```
Quick Size Calc:
- Risk Amount = Account × 2%
- Position Size = Risk Amount ÷ Stop Distance
- Max: 1/4 Kelly or 2% risk (whichever smaller)
```

### 4. 🎯 EDGE
**"Why does this trade have positive expectancy?"**
- Historical win rate for this pattern?
- Risk/Reward ratio? (minimum 2:1)
- What's the pattern weight? (positive = green light)

### 5. 🧠 MENTAL
**"Am I trading process or emotion?"**
- Recent loss → revenge trading? ❌
- Recent win → overconfidence? ❌
- Following checklist → ✅

### 6. ⚠️ RISK
**"What could go wrong?"**
- Gap risk (overnight/weekend)?
- News event in next 30 min?
- Already correlated positions?
- Total exposure within limits?

---

### CHECK SCORING

| Red Flags | Action |
|-----------|--------|
| 0 | ✅ Proceed |
| 1 | ⚠️ Reduce size by 50% |
| 2+ | ❌ SKIP - Find better setup |

**A red flag = Any "no" or uncertain answer**

---

## PHASE 3: EXECUTE (The Verification Loop)

### Step 1: Place Order
```bash
# Record BEFORE placing
echo "$(date): Planning $SYMBOL $DIRECTION $SIZE @ $PRICE" >> trade-log.txt

# Place order
node cli.js buy SYMBOL QTY [limit PRICE]
# or whatever broker command
```

### Step 2: Verify Acceptance
```bash
# Check order exists
node cli.js orders open

# MUST see order ID before proceeding
```

### Step 3: Confirm Fill (for market orders)
```bash
# Check position
node cli.js positions

# MUST see position before announcing
```

### Step 4: Announce ONLY After Verification
```
Format for unfilled:
📋 ORDER PLACED:
- Symbol: X
- Size: Y
- Price: Z (limit)
- Order ID: [actual ID]
- Status: PENDING

Format for filled:
✅ POSITION OPENED:
- Symbol: X
- Size: Y
- Fill Price: Z (actual)
- Cost: $A
- Stop: $B
- Target: $C
```

### CRITICAL RULES
- ❌ NEVER say "executed" before verification
- ❌ NEVER skip the order ID check
- ❌ NEVER announce from memory (always re-check)
- ✅ ALWAYS show actual CLI output
- ✅ ALWAYS update active-positions.md

---

## PHASE 4: REVIEW (Learning Loop)

### Immediate (Within 1 Hour)
- [ ] Position logged in active-positions.md
- [ ] Entry documented with reasoning
- [ ] Alerts set for stop and target

### Daily (End of Trading Day)
- [ ] Check all positions
- [ ] Note unrealized P&L
- [ ] Update pattern observations

### On Close (When Position Exits)
```
POST-MORTEM TEMPLATE:
━━━━━━━━━━━━━━━━━━━━━━
Trade: [SYMBOL] [DIRECTION]
Entry: $X → Exit: $Y
P&L: $Z (X%)

What worked:
- 

What didn't:
-

Pattern tags:
- [ ] fomo_entry
- [ ] proper_sizing
- [ ] stop_honored
- [ ] target_reached
- [ ] revenge_trade

Weight update:
- Pattern X: +0.1 (if successful)
- Pattern Y: -0.1 (if failed)
━━━━━━━━━━━━━━━━━━━━━━
```

### Weekly (Sunday Review)
- Total trades: X
- Win rate: Y%
- Avg R multiple: Z
- Patterns to strengthen:
- Patterns to avoid:

---

## QUICK REFERENCE CARD

```
┌─────────────────────────────────────────────────────────┐
│                  ATLAS TRADING FLOW                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  SCOUT → CHECK → EXECUTE → REVIEW                       │
│                                                         │
│  THE 6 ESSENTIALS:                                      │
│  □ 1. Timing (Kill Zone?)                               │
│  □ 2. Setup (Valid? Entry/Stop/Target?)                 │
│  □ 3. Size (2% max risk, 1/4 Kelly)                     │
│  □ 4. Edge (Win rate? R:R > 2:1?)                       │
│  □ 5. Mental (Process not emotion?)                     │
│  □ 6. Risk (Gaps? News? Correlation?)                   │
│                                                         │
│  0 red flags → GO                                       │
│  1 red flag → REDUCE 50%                                │
│  2+ red flags → SKIP                                    │
│                                                         │
│  VERIFY BEFORE ANNOUNCE:                                │
│  Order ID exists → Position shows → THEN speak          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## POSITION TRACKING

### Active Positions File Structure
```markdown
# Active Positions - Updated [TIMESTAMP]

## [BROKER NAME] Positions

### Position 1: [SYMBOL] [DIRECTION]
- Entry: $X at [TIME]
- Size: Y contracts/shares
- Stop: $A (X% risk)
- Target: $B (Y R:R)
- Status: OPEN
- P&L: $Z (unrealized)
- Notes: [reasoning, observations]
```

### Risk Calculator
```
Total Portfolio: $X
Max Single Trade Risk: 2% = $Y
Current Exposure: $Z
Remaining Risk Budget: $Y - $Z = $W

⚠️ If Current Exposure > 6% total → NO NEW TRADES
```

---

## INTEGRATION POINTS

- **Pattern Database:** Check weight before trading
- **Cognitive State:** Mental energy affects check #5
- **Anomaly Detection:** Alerts if behavior deviates
- **Voice System:** Announces major fills/exits

---

*One workflow. No exceptions. Every trade.*
