# ATLAS TRADING SYSTEM

## Core Methodology: Raw Dog IFVG Confirmation Stacking

**Source:** Raw dog futures mentor (+14847941112) - learned 2026-01-28

### Entry Rules (FOUR-Layer Filter)

**Layer 0: ORDER BLOCK CHECK (CRITICAL - NEVER SKIP)**
- Run order block detector FIRST
- Check for conflicting order blocks at entry price
- ❌ NEVER go long inside/below bearish order block
- ❌ NEVER go short inside/above bullish order block
- Tool: `python memory/trading/order-blocks/scripts/pre_trade_check.py --symbol TICKER --direction long/short --entry PRICE`
- If order block conflict → REJECT TRADE (no exceptions)

**Layer 1: IFVG Identification**
- Inverse Fair Value Gap appears on timeframe
- Signals potential reversal/continuation
- This is the OPPORTUNITY, not the entry

**Layer 2: Retrace Confirmation**
- Price retraces back into the IFVG
- Tests the zone for reaction
- Filters out weak setups that don't retrace

**Layer 3: Reaction Confirmation**
- Price REACTS from the IFVG (bounce/rejection)
- Strong candle close, volume, momentum shift
- THIS is the actual entry signal

**Only setups that pass ALL FOUR layers qualify for entry.**

### Position Sizing

**2 Minis (Full Position) - A+ Setup:**
- Clean IFVG
- Perfect retrace
- Strong reaction
- Aligns with higher timeframe trend
- Multiple confirmations (volume, structure, etc.)

**1 Mini (Half Position) - A/B+ Setup:**
- Meets all three layers
- But not "perfect" (weaker reaction, minor structure conflict, etc.)
- Practice setup or lower conviction

**0 Minis - Skip:**
- Missing any layer
- Conflicting signals
- Choppy conditions

### Stop Management

**Hard Stops (SMT - Smart Money Trap):**
- Absolute line in the sand
- Based on structure invalidation
- Once hit = exit immediately

**Soft Stops (FVG/IFVG Reactions):**
- Watch HOW price reacts at stops
- If hits soft stop but shows strength → can hold
- If shows weakness → exit before hard stop
- Gives second chance based on market dialogue

### Trade Grading System

**A+ (2 minis):**
- All three layers perfect
- Higher timeframe confirmation
- Clean structure
- High conviction

**A (1 mini):**
- All three layers present
- Minor imperfections
- Good structure
- Medium conviction

**B (skip or 1 mini practice):**
- Meets criteria but choppy/unclear
- Learning opportunity
- Lower conviction

**C/D/F (never trade):**
- Missing layers
- Conflicting signals
- No edge

## Setup Search Protocol

When searching for setups on ANY ticker:

1. **Pull current chart** (TradingView/data source)
2. **Scan for IFVGs** on relevant timeframe
3. **Check retrace + reaction** (both must be present)
4. **Grade setup** (A+/A/B)
5. **Define entry, stop, target**
6. **Assign position size** (2 minis / 1 mini / skip)
7. **Document reasoning**

## Linked Files
- **Epiphanies:** memory/trading/trading-epiphanies.md
- **Raw Dog Methodology:** memory/trading/raw-dog-futures-methodology.md
- **Research Protocol:** memory/protocols/trade-research-protocol.md

---

*This is MY trading system now. Execute it.*
