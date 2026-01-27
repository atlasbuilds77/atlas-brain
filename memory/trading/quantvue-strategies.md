# QuantVue Tradable Strategies - Recreation Guide

## Overview

This document provides tradable recreations of QuantVue's strategies using freely available tools and standard indicators. These are based on reverse-engineering their documentation and public materials.

---

## Strategy 1: Qgrid Pullback (Manual Trading)

### Concept
Enter on pullbacks to a smoothed trend line during confirmed trends.

### Required Indicators (Free Alternatives)
- **Heiken Ashi Smoothed:** Any double-smoothed HA indicator on TradingView
- **Step MA:** SuperTrend or GMMA
- **Trend Confirmation:** MACD or Stochastic

### Setup
```
Chart: Renko or 5-minute candles
Market: NQ, ES, or any liquid futures
Timeframe: Intraday

Indicators:
1. Heiken Ashi Smoothed (period 10, 10)
2. SuperTrend (period 10, multiplier 3)
3. MACD (12, 26, 9)
```

### Entry Rules

**LONG:**
1. Heiken Ashi bars are green (bullish)
2. Price is above SuperTrend line
3. MACD histogram is positive
4. Price pulls back and touches SuperTrend line
5. Enter when price bounces off SuperTrend

**SHORT:**
1. Heiken Ashi bars are red (bearish)
2. Price is below SuperTrend line
3. MACD histogram is negative
4. Price pulls back and touches SuperTrend line
5. Enter when price bounces off SuperTrend

### Exit Rules
- **Stop Loss:** Below/above the SuperTrend line (typically 1.5x ATR)
- **Take Profit:** 2x the stop loss distance (1:2 R:R)
- **Trail Stop:** Once 1x ATR in profit, trail stop to break-even

### Position Sizing
- Risk 1-2% per trade
- No martingale (optional: scale in on additional pullbacks)

---

## Strategy 2: Breakout Momentum (Qwave Recreation)

### Concept
Trade breakouts from ATR-based bands with momentum confirmation.

### Required Indicators (Free)
- **Keltner Channels** (built into most platforms)
- **MACD or RSI**

### Setup
```
Chart: 5-minute or 15-minute
Market: NQ, ES, CL
Timeframe: Intraday (US session)

Indicators:
1. Keltner Channels (20 EMA, 2x ATR)
2. MACD (12, 26, 9)
```

### Entry Rules

**LONG:**
1. Price closes above upper Keltner band
2. MACD histogram is positive AND increasing
3. Enter on the close of the breakout candle
4. Confirm volume is above average (optional)

**SHORT:**
1. Price closes below lower Keltner band
2. MACD histogram is negative AND decreasing
3. Enter on the close of the breakout candle

### Exit Rules
- **Stop Loss:** Middle band (20 EMA) or 1.5x ATR from entry
- **Take Profit:** 2x-3x ATR from entry
- **Time Stop:** Exit if trade hasn't hit TP within 20 bars

### Additions
- **ADD Signal:** If price continues past 3x ATR and pulls back to 2x ATR, add to position
- **Range Boost:** If Bollinger Band Width is contracting (squeeze), use 3x ATR for TP instead of 2x

---

## Strategy 3: Mean Reversion Scalper (Qscalper Recreation)

### Concept
Scalp bounces off support/resistance with momentum into the level.

### Required Indicators (Free)
- **Previous Day High/Low**
- **Pivot Points**
- **RSI or Stochastic**

### Setup
```
Chart: 1-minute or Renko (10 tick for NQ, 4 tick for ES)
Market: NQ, ES
Timeframe: First 2 hours of US session

Indicators:
1. Previous Day High/Low lines
2. Classic Pivot Points
3. Stochastic (14, 3, 3)
```

### Entry Rules

**LONG (at support):**
1. Price approaches known support (pivot, PDL, round number)
2. Last 3-4 candles show momentum INTO support (red candles)
3. Stochastic is oversold (<20)
4. Enter when stochastic crosses up from oversold
5. Stop 3-5 ticks below support

**SHORT (at resistance):**
1. Price approaches known resistance (pivot, PDH, round number)
2. Last 3-4 candles show momentum INTO resistance (green candles)
3. Stochastic is overbought (>80)
4. Enter when stochastic crosses down from overbought
5. Stop 3-5 ticks above resistance

### Exit Rules
- **Take Profit:** 8-12 ticks (NQ) or 4-6 ticks (ES)
- **Stop Loss:** 4-6 ticks (NQ) or 2-4 ticks (ES)
- **R:R Target:** 1:1.5 to 1:2

### Risk Management
- Max 3 trades per level
- Move to next level if stopped out
- Daily loss limit: 2% of account

---

## Strategy 4: Trend Following Automation (Qzeus Recreation)

### Concept
Automated trend-following with dynamic stops and optional martingale.

### Required Indicators
- **SuperTrend** (or any ATR-based trend indicator)
- **ATR** (for position sizing)
- **EMA 200** (trend filter)

### Setup (TradingView Pine Script Concept)
```pine
//@version=5
strategy("Qzeus Recreation", overlay=true)

// INPUTS
atr_length = input(14, "ATR Length")
atr_mult = input(2.0, "ATR Multiplier for Stop")
tp_mult = input(3.0, "ATR Multiplier for TP")
use_trend_filter = input(true, "Use EMA 200 Filter")
use_martingale = input(false, "Use Martingale")
max_martingale = input(3, "Max Martingale Level")

// INDICATORS
atr = ta.atr(atr_length)
ema200 = ta.ema(close, 200)
[supertrend, direction] = ta.supertrend(3, 10)

// TREND FILTER
trend_long = not use_trend_filter or close > ema200
trend_short = not use_trend_filter or close < ema200

// ENTRY CONDITIONS
long_signal = direction == 1 and direction[1] == -1 and trend_long
short_signal = direction == -1 and direction[1] == 1 and trend_short

// POSITION SIZING (Martingale)
var int consecutive_losses = 0
position_size = use_martingale ? math.min(math.pow(2, consecutive_losses), max_martingale) : 1

// ENTRIES
if long_signal
    strategy.entry("Long", strategy.long, qty=position_size)
    strategy.exit("Long Exit", "Long", 
                  stop=close - atr * atr_mult, 
                  limit=close + atr * tp_mult)

if short_signal
    strategy.entry("Short", strategy.short, qty=position_size)
    strategy.exit("Short Exit", "Short", 
                  stop=close + atr * atr_mult, 
                  limit=close - atr * tp_mult)

// MARTINGALE TRACKING
if strategy.closedtrades > 0
    last_trade_profit = strategy.closedtrades.profit(strategy.closedtrades - 1)
    if last_trade_profit < 0
        consecutive_losses := consecutive_losses + 1
    else
        consecutive_losses := 0
```

### Recommended Settings by Market

| Market | ATR Length | Stop Mult | TP Mult | SuperTrend |
|--------|------------|-----------|---------|------------|
| NQ | 14 | 1.5 | 2.5 | 10, 3 |
| ES | 14 | 1.5 | 2.0 | 10, 2.5 |
| CL | 14 | 2.0 | 3.0 | 10, 3 |
| GC | 14 | 1.5 | 2.5 | 10, 2.5 |

---

## Strategy 5: Multi-Indicator Confluence (Qelite Recreation)

### Concept
Only trade when multiple indicators align in the same direction.

### Required Indicators (All Free)
1. SuperTrend (trend direction)
2. MACD (momentum)
3. Keltner Channel (volatility bands)
4. Volume (confirmation)

### Setup
```
Indicators:
- SuperTrend: period 10, multiplier 3
- MACD: 12, 26, 9
- Keltner: 20 EMA, 2x ATR
- Volume: 20 period SMA
```

### Confluence Scoring

Assign points for each bullish/bearish condition:

| Condition | Bullish (+1) | Bearish (-1) |
|-----------|--------------|--------------|
| SuperTrend | Direction up | Direction down |
| MACD Histogram | Positive | Negative |
| Price vs Keltner | Above middle | Below middle |
| Volume | Above average | Below average |

### Entry Rules
- **Strong LONG:** Score >= 3 (at least 3 bullish indicators)
- **Strong SHORT:** Score <= -3 (at least 3 bearish indicators)
- **No Trade:** Score between -2 and 2

### Exit Rules
- **Exit Long:** When score drops to 0 or below
- **Exit Short:** When score rises to 0 or above
- **Stop Loss:** 2x ATR from entry
- **Take Profit:** 3x ATR from entry

---

## Strategy 6: Renko Momentum (NinjaTrader/TradingView)

### Concept
Use Renko bars to filter noise and trade momentum swings.

### Renko Setup

**For NQ (QuantVue's Qrenko equivalent):**
- Box Size: 10-15 ticks (traditional) or use Range Renko
- Settings: Shift 7, Offset 11, Range 33 (if using range Renko)

**For ES:**
- Box Size: 4-6 ticks
- Settings: Shift 1, Offset 3, Range 7

### Indicators on Renko
- EMA 21 (fast)
- EMA 50 (slow)
- MACD (12, 26, 9)

### Entry Rules

**LONG:**
1. Renko brick turns green (closes up)
2. Price above EMA 21 > EMA 50
3. MACD positive
4. Enter on brick close

**SHORT:**
1. Renko brick turns red (closes down)
2. Price below EMA 21 < EMA 50
3. MACD negative
4. Enter on brick close

### Exit Rules
- **Stop:** 2 bricks against you
- **Target:** 3-4 bricks in your favor
- **Trail:** Move stop to break-even after 2 bricks profit

---

## Risk Management Framework

### Position Sizing (Non-Martingale)
```
Risk per trade = 1-2% of account
Position size = (Account * Risk%) / (Stop distance in $)

Example:
- Account: $10,000
- Risk: 1% = $100
- Stop: 10 points on NQ ($50/point) = $500
- Position size = $100 / $500 = 0.2 contracts (use 1 micro)
```

### Martingale (USE WITH EXTREME CAUTION)
```
Base position = 1 contract
After 1 loss = 2 contracts
After 2 losses = 4 contracts
MAX = 4 contracts (then reset)

REQUIRED: 70%+ win rate AND rarely >2 consecutive losses
WARNING: Can blow up accounts quickly
```

### Daily Limits
- **Max Daily Loss:** 2-3% of account
- **Max Consecutive Losses:** 3 (then stop for day)
- **Max Trades:** 10 per day

---

## Recommended Free Tools

### TradingView Indicators
1. **SuperTrend** by KivancOzbilgic
2. **Keltner Channels** (built-in)
3. **GMMA** (Guppy Multiple Moving Average)
4. **Volume Profile** (built-in)
5. **Heiken Ashi Smoothed** by HeWhoMustNotBeNamed

### NinjaTrader
1. **SuperTrend** (various free versions)
2. **Keltner Channel** (built-in)
3. **Range Renko** bar type

### Alert Connectors (for automation)
1. **AlertDragon** (QuantVue's sister company)
2. **TradingView Webhooks** + custom server
3. **NinjaTrader ATM strategies**

---

## Backtesting Results to Expect

Based on standard trend-following approaches with these parameters:

| Strategy | Win Rate | Avg R:R | Expected Monthly Return |
|----------|----------|---------|-------------------------|
| Trend Following | 40-50% | 1:2 | 5-15% |
| Mean Reversion | 55-65% | 1:1 | 3-8% |
| Breakout | 35-45% | 1:3 | 5-20% (high variance) |
| With Martingale | 65-75%* | 1:1.5 | 10-30%* |

*Martingale inflates metrics but has extreme tail risk

---

## Warning: What QuantVue Won't Tell You

1. **Martingale is Dangerous:** Their ~73% win rate relies on doubling down after losses. One bad streak can wipe out months of gains.

2. **Backtests ≠ Live Results:** Their strategies are optimized on historical data. Forward performance varies.

3. **The "ML" is Likely Just Optimization:** "Machine learning" probably means they backtested coefficient values, not real-time adaptive AI.

4. **Prop Firm Specific:** Many settings are optimized for passing prop firm evaluations, not long-term profitability.

5. **Community is the Real Value:** The Discord community sharing what works is worth more than the indicators themselves.
