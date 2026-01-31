# SETUP SEARCH PROTOCOL

## Purpose
When Orion asks "find a setup on [TICKER]", execute this protocol using Atlas Trading System.

## Execution Steps

### 0. ORDER BLOCK CHECK (CRITICAL - ALWAYS FIRST)
```bash
# Run order block detector BEFORE analyzing setup
cd memory/trading/order-blocks/scripts
python pre_trade_check.py --symbol TICKER --direction long/short --entry PRICE
```

**If order block conflict detected:**
- ❌ REJECT TRADE immediately
- Document why (bullish block above short entry / bearish block below long entry)
- DO NOT PROCEED to other layers

**Only if order block check passes → Continue to Layer 1**

### 1. Pull Current Data
```bash
# Get current chart/price data for ticker
# TradingView, market data API, or browser snapshot
```

### 2. IFVG Scan (Layer 1)
- Look for Inverse Fair Value Gap on relevant timeframe
- Identify bullish IFVG (support) or bearish IFVG (resistance)
- Mark the zone on chart

### 3. Retrace Check (Layer 2)
- Has price retraced back INTO the IFVG?
- If not yet → mark as "watching, waiting for retrace"
- If yes → proceed to Layer 3

### 4. Reaction Check (Layer 3)
- Did price REACT from the IFVG?
- Strong candle close, volume increase, momentum shift?
- If weak/no reaction → skip setup
- If strong reaction → proceed to grading

### 5. Grade Setup
**A+ Setup (2 minis):**
- Clean IFVG structure
- Perfect retrace into zone
- Strong, clear reaction
- Higher timeframe alignment
- Multiple confirmations

**A Setup (1 mini):**
- All three layers present
- Minor imperfections (weaker reaction, slight structure noise)
- Still tradeable

**B Setup (skip or practice):**
- Meets criteria but unclear/choppy
- Learning opportunity only

### 6. Define Trade Parameters
- **Entry:** Specific price level (after reaction confirmation)
- **Hard Stop:** Structure invalidation point (SMT)
- **Soft Stop:** FVG/IFVG reaction level (can adjust)
- **Target:** Next structure level / reward:risk ratio
- **Position Size:** 2 minis (A+), 1 mini (A), 0 (B/skip)

### 7. Document & Present
Return to Orion:
```
TICKER: [SPY/QQQ/etc]
SETUP GRADE: [A+/A/B]
DIRECTION: [Long/Short]

ORDER BLOCKS: ✅ Clear / ⚠️ Nearby / ❌ Conflict
IFVG: [price zone]
RETRACE: [confirmed/waiting]
REACTION: [strong/weak/none]

ENTRY: $XXX.XX
HARD STOP: $XXX.XX
SOFT STOP: $XXX.XX
TARGET: $XXX.XX
POSITION: [2 minis / 1 mini / skip]

REASONING: [why this setup qualifies, what makes it A+ vs A, order block context]
```

## Tools & Resources
- TradingView charts
- Market data APIs (if available)
- Browser snapshots for chart analysis
- Raw dog methodology (memory/trading/raw-dog-futures-methodology.md)
- Atlas trading system (memory/trading/atlas-trading-system.md)

## Linked Files
- **Trading System:** memory/trading/atlas-trading-system.md
- **Epiphanies:** memory/trading/trading-epiphanies.md
- **Raw Dog Methodology:** memory/trading/raw-dog-futures-methodology.md

---

*"Find a setup on QQQ" → Execute this protocol and return actionable trade.*
