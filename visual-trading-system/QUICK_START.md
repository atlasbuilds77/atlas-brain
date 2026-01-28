# Atlas Eyes - Quick Start Guide

## What This Does

Gives Atlas "eyes" to visually analyze charts using ICT (Inner Circle Trader) concepts:
- **Order Blocks** (supply/demand zones)
- **Fair Value Gaps** (imbalances to fill)
- **Liquidity** (stop hunts, equal highs/lows)
- **Market Structure** (BOS, ChoCH, trend breaks)

## Immediate Usage (For Atlas)

### 1. Analyze a Chart Screenshot

When you have a chart image (from browser screenshot or user upload):

```python
# Use the image tool with ICT analysis prompt
image(
    image="/path/to/chart.png",
    prompt="""
Analyze this trading chart using ICT/Smart Money Concepts.

Look for:
1. Market Structure - Is price making HH/HL or LH/LL? Any BOS or ChoCH?
2. Order Blocks - Where are the key OBs? Are any being tested?
3. Fair Value Gaps - Any unfilled FVGs? Is price in or near one?
4. Liquidity - Equal highs/lows that might be swept?
5. Momentum - Are candles strong or exhausted? Wicks showing rejection?

Provide:
- BIAS: BULLISH/BEARISH/NEUTRAL
- CONFIDENCE: 1-10
- EXIT_SIGNAL: NONE/SCALE_OUT/FULL_EXIT
- KEY_OBSERVATIONS: Top 3-5 things
- REASONING: Brief explanation
"""
)
```

### 2. Capture Chart via Browser

```python
# Use browser tool to capture TradingView
browser(
    action="screenshot",
    profile="clawd",
    targetUrl="https://www.tradingview.com/chart/?symbol=BINANCE:ETHUSDT.P"
)
# Returns path to screenshot, then analyze with image tool
```

### 3. Quick Exit Check

For an open LONG position:

```python
image(
    image="/path/to/current_chart.png",
    prompt="""
I have an open LONG position. Entry was around $2,911.

Should I EXIT, SCALE OUT, or HOLD?

Look for:
- Signs of momentum exhaustion
- Structure breaks against my position
- Approaching liquidity that might reverse price
- FVGs filled that could cause reversal

Answer: EXIT/SCALE_OUT/HOLD | Confidence: 1-10 | Reason: [brief]
"""
)
```

## Command Line Usage

```bash
cd ~/clawd/visual-trading-system

# One-shot analysis
python3 atlas_eyes.py analyze ETH-PERP --mtf

# Monitor open position (with alerts)
python3 atlas_eyes.py monitor --symbol ETH-PERP --side LONG --entry 2911

# Check existing chart image
python3 atlas_eyes.py quick-check /path/to/chart.png --exit

# Show ICT reference
python3 atlas_eyes.py ict-ref
```

## Why Visual > Data

The ETH trade example:
- **Data said**: +1.41% profit, still running
- **Visual said**: Momentum dying, rejection candles, liquidity above about to reverse

Visual patterns the model looks for:
1. **Shrinking candles** = Momentum exhaustion
2. **Long wicks** = Rejection/absorption
3. **Equal highs ahead** = Liquidity pool trap
4. **FVG filled** = Natural reversal point
5. **Volume drop** = Conviction fading

## File Structure

```
visual-trading-system/
├── atlas_eyes.py       # Main CLI entry point
├── ict_patterns.py     # ICT prompts and patterns
├── visual_analyzer.py  # Chart capture & analysis
├── position_monitor.py # Real-time monitoring
├── config.json         # Settings
├── ARCHITECTURE.md     # Full system design
└── QUICK_START.md      # This file
```

## ICT Pattern Cheat Sheet

| Pattern | What It Looks Like | Signal |
|---------|-------------------|--------|
| **BOS (Break of Structure)** | Price breaks swing high/low WITH trend | Continuation |
| **ChoCH (Change of Character)** | Price breaks structure AGAINST trend | Reversal! |
| **Order Block** | Last opposite candle before strong move | Key level |
| **FVG/Imbalance** | Gap between candle bodies | Price returns |
| **Equal Highs/Lows** | Obvious double tops/bottoms | Liquidity trap |
| **Displacement** | Large body candle | Institutional intent |

## Integration with Drift Bot

The position_monitor.py can run alongside the drift-bot scalper:

1. Scalper opens position
2. Position monitor captures charts every 60s
3. Vision model analyzes for ICT patterns
4. Exit signals sent to Telegram
5. Atlas/user confirms or auto-executes

## Next Steps

1. **Test with real chart**: Screenshot any TradingView chart, run through analyzer
2. **Tune prompts**: Adjust ICT prompts in ict_patterns.py for better signals
3. **Backtest**: Compare visual signals to historical price action
4. **Automate**: Connect to drift-bot for automated exit execution

---

*Atlas Eyes v1.0 - See the market, not just the numbers.*
