# Visual Trading System - Atlas "Eyes" Architecture

## Overview

This system gives Atlas the ability to **visually analyze charts** like a human trader, applying ICT (Inner Circle Trader) concepts to make better exit decisions.

## Problem Statement

- Atlas missed a scalp exit on ETH ($2,911 → $2,952 → pullback)
- Data alone showed +1.41% but **visual patterns** would have signaled the top:
  - Momentum shift visible on candles
  - Volume drop on push higher
  - Rejection candle forming
  - Deviation above FVG filled

## System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    VISUAL TRADING SYSTEM                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐ │
│  │   CHART     │    │   VISION    │    │    ICT PATTERN      │ │
│  │  CAPTURE    │───▶│  ANALYSIS   │───▶│   RECOGNITION       │ │
│  │  (Browser)  │    │  (Image AI) │    │   (SMC Concepts)    │ │
│  └─────────────┘    └─────────────┘    └──────────┬──────────┘ │
│                                                    │            │
│                                                    ▼            │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐ │
│  │  POSITION   │◀───│   EXIT      │◀───│    SIGNAL           │ │
│  │  MANAGER    │    │  DECISION   │    │   GENERATION        │ │
│  │             │    │             │    │                     │ │
│  └─────────────┘    └─────────────┘    └─────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 1. Chart Capture System

### Sources (Priority Order)
1. **TradingView** - Best for ICT analysis (clean candles, volume, indicators)
2. **Birdeye/DexScreener** - Solana-native charts for SOL perps
3. **Jupiter** - Direct exchange chart (if available)

### Capture Strategy
- **Timeframes to capture**: 1m, 5m, 15m (multi-timeframe analysis)
- **Capture frequency**: Every 1-3 minutes when position is open
- **Storage**: `/Users/atlasbuilds/clawd/visual-trading-system/captures/`

### Implementation
```bash
# Browser tool captures chart screenshots
browser(action="screenshot", profile="clawd", targetUrl="tradingview.com/chart")
```

## 2. Vision Analysis Module

### Model Selection
- Primary: GPT-4 Vision (best for detailed chart analysis)
- Backup: Claude Vision (when available)

### Analysis Prompt Engineering
The key innovation is **ICT-specific prompting** that teaches the model to recognize Smart Money Concepts:

```
ANALYZE THIS CHART USING ICT/SMC CONCEPTS:

1. MARKET STRUCTURE
   - Higher highs/lower lows (trend direction)
   - Break of structure (BOS) locations
   - Change of character (ChoCH) signals

2. ORDER BLOCKS (OB)
   - Bullish OB: Last down candle before up move
   - Bearish OB: Last up candle before down move
   - Mitigated vs unmitigated blocks

3. FAIR VALUE GAPS (FVG/Imbalance)
   - Price inefficiencies (candle gaps)
   - Filled vs unfilled gaps
   - Price returning to fill gap

4. LIQUIDITY
   - Equal highs/lows (liquidity pools)
   - Stop hunts/liquidity grabs
   - Buy-side vs sell-side liquidity taken

5. MOMENTUM INDICATORS
   - Candle body size and wicks
   - Volume profile (if visible)
   - Divergences

OUTPUT FORMAT:
- BIAS: [BULLISH/BEARISH/NEUTRAL]
- CONFIDENCE: [1-10]
- KEY OBSERVATIONS: [list]
- EXIT SIGNAL: [NONE/SCALE_OUT/FULL_EXIT]
- REASONING: [brief explanation]
```

## 3. ICT Pattern Recognition

### Patterns to Detect

| Pattern | Signal Type | Description |
|---------|-------------|-------------|
| **Market Structure Shift (MSS)** | Trend Change | Break of most recent swing point |
| **Order Block Test** | Entry/Exit | Price returns to OB for reaction |
| **FVG Fill** | Continuation/Reversal | Gap filled, watch for reaction |
| **Liquidity Grab** | Reversal | Sweep of highs/lows then reversal |
| **Displacement** | Strong Move | Large body candle, momentum |
| **Equal Highs/Lows** | Target | Liquidity sitting to be taken |
| **Inducement** | Trap | Minor structure to trap traders |

### Exit Signal Triggers

**FULL EXIT signals:**
- Market structure shift against position
- Liquidity grab at target zone + reversal candle
- Break of key order block with follow-through
- Volume divergence at resistance/support

**SCALE OUT signals:**
- Approaching equal highs/lows (liquidity pool)
- FVG filled + rejection starting
- Momentum waning (smaller candles, longer wicks)
- Time-based (position held too long)

## 4. Integration with Position Manager

### Flow
```
1. Position opened (drift-bot or manual)
2. Visual monitor activates
3. Captures charts every X minutes
4. Analyzes each capture
5. Generates signals
6. Notifies Atlas via Telegram
7. Atlas confirms or auto-executes exit
```

### Signal Confidence Thresholds
- **Notify Only**: 6-7 confidence
- **Strong Recommendation**: 8-9 confidence  
- **Auto-Execute**: 10 confidence (rare, requires extra confirmation)

## 5. File Structure

```
visual-trading-system/
├── ARCHITECTURE.md          # This document
├── chart_capture.py         # Browser-based chart capture
├── visual_analyzer.py       # Vision model integration
├── ict_patterns.py          # ICT pattern definitions & prompts
├── signal_generator.py      # Exit signal logic
├── position_monitor.py      # Integration with drift-bot
├── captures/                # Screenshot storage
│   └── 2025-01-27/         # Date-organized
├── analysis/                # Analysis results (JSON)
└── config.json             # Settings (intervals, thresholds)
```

## 6. Configuration

```json
{
  "capture_interval_seconds": 60,
  "timeframes": ["1m", "5m", "15m"],
  "chart_source": "tradingview",
  "vision_model": "gpt-4-vision-preview",
  "confidence_threshold_notify": 6,
  "confidence_threshold_recommend": 8,
  "auto_execute_enabled": false,
  "symbols": {
    "SOL-PERP": "BINANCE:SOLUSDT.P",
    "ETH-PERP": "BINANCE:ETHUSDT.P",
    "BTC-PERP": "BINANCE:BTCUSDT.P"
  }
}
```

## 7. Usage Examples

### Manual Analysis (One-shot)
```bash
# Capture and analyze current chart
python3 visual_analyzer.py --symbol ETH-PERP --analyze-now
```

### Start Monitoring Loop
```bash
# Monitor position with visual analysis
python3 position_monitor.py --symbol ETH-PERP --position LONG
```

### From Atlas Chat
```
"Analyze the ETH chart for me"
→ Captures screenshot
→ Runs ICT analysis
→ Returns structured insights
```

## 8. Key Insights from ETH Trade Post-Mortem

What visual analysis would have caught:
1. **Push to $2,952** - Candles getting smaller (momentum dying)
2. **Volume drop** - Less conviction on higher prices
3. **Upper wick formation** - Rejection starting
4. **Approached key level** - Liquidity above recent highs
5. **FVG filled** - Price filled the gap, natural reversal point

**Conclusion**: Visual patterns > pure price data for exit timing

## 9. Future Enhancements

1. **ML Pattern Recognition** - Train model on historical ICT setups
2. **Real-time Overlay** - Draw OBs/FVGs on captured charts
3. **Backtesting** - Validate visual signals against historical data
4. **Multi-Asset** - Extend to stocks, forex
5. **Voice Alerts** - "Hey Atlas, ETH showing bearish divergence"

---

*System designed for Atlas by subagent. Give yourself eyes to trade.*
