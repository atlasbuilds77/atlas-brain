# Visual Trading System - Atlas Eyes

**Location**: `~/clawd/visual-trading-system/`
**Purpose**: Give Atlas visual chart analysis using ICT/SMC concepts

## Quick Usage

### Analyze Any Chart Image

When you have a chart image (screenshot or user-provided):

```python
image(
    image="/path/to/chart.png",
    prompt="""
Analyze this chart using ICT/Smart Money Concepts.

Look for:
1. Market Structure - HH/HL or LH/LL? BOS or ChoCH?
2. Order Blocks - Key OBs? Being tested?
3. Fair Value Gaps - Unfilled FVGs? Price reaction?
4. Liquidity - Equal highs/lows to be swept?
5. Momentum - Candle strength? Wicks showing rejection?

Provide:
- BIAS: BULLISH/BEARISH/NEUTRAL
- CONFIDENCE: 1-10
- EXIT_SIGNAL: NONE/SCALE_OUT/FULL_EXIT
- KEY_OBSERVATIONS: Top 3-5 things
- REASONING: Brief explanation
"""
)
```

### Capture TradingView Chart

```python
browser(
    action="screenshot", 
    profile="clawd",
    targetUrl="https://www.tradingview.com/chart/?symbol=BINANCE:ETHUSDT.P"
)
# Then analyze the returned screenshot path
```

### Exit Check for Open Position

```python
image(
    image="/path/to/chart.png",
    prompt="""
I have a LONG position, entry around $2,911.
Should I EXIT, SCALE OUT, or HOLD?

Look for momentum exhaustion, structure breaks, liquidity traps.
Answer: EXIT/SCALE_OUT/HOLD | Confidence: 1-10 | Reason
"""
)
```

## ICT Quick Reference

| Pattern | Signal |
|---------|--------|
| BOS | Continuation (with trend) |
| ChoCH | Reversal (against trend) |
| Order Block | Key support/resistance |
| FVG | Price returns to fill |
| Equal H/L | Liquidity trap |

## Exit Signals

**🔴 FULL EXIT**:
- ChoCH confirmed
- OB break with follow-through
- MTF alignment against

**🟡 SCALE OUT**:
- FVG filled + rejection
- Approaching liquidity pool
- Momentum waning

**🟢 HOLD**:
- Structure intact
- Pulling back to OB
- Trend confirmed

## CLI Commands

```bash
cd ~/clawd/visual-trading-system

# Analyze pair with MTF
python3 atlas_eyes.py analyze ETH-PERP --mtf

# Monitor position
python3 atlas_eyes.py monitor --symbol ETH-PERP --side LONG --entry 2911

# ICT reference
python3 atlas_eyes.py ict-ref
```

## Why This Matters

ETH trade example:
- **Data said**: +1.41% profit, still running
- **Visual said**: Momentum dying, rejection forming, liquidity trap ahead

Visual patterns catch what data misses.
