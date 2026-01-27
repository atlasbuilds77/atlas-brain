# QuantVue Trading System - Comprehensive Analysis

## Executive Summary

QuantVue is a Tampa, FL-based trading tools company that provides automated trading strategies, indicators, and an automated trading suite (ATS) primarily for futures markets. They target intermediate to advanced traders and charge between $197-$447/month for their tools, with their premium ATS program costing several thousand dollars.

**Key Finding:** QuantVue's "edge" is not a revolutionary algorithm, but rather a well-packaged combination of:
1. Standard technical indicators with proprietary naming
2. Renko-based trading systems optimized for futures
3. Aggressive money management (martingale) that amplifies their base ~70% win rate
4. Excellent marketing and community support

---

## Company Overview

### Background
- **Founded:** Based in Tampa, FL
- **Team:** Claims "former hedge fund system devs"
- **User Base:** 20,000+ users claimed
- **Platforms:** TradingView, NinjaTrader, Sierra Chart
- **Primary Markets:** Futures (NQ, ES, CL, GC, YM)
- **Business Model:** Subscription + High-ticket ATS Program

### Pricing Structure
| Plan | Monthly | Yearly |
|------|---------|--------|
| Pro (Manual Trading) | $197 | $1,497 ($124/mo) |
| Elite (Automated) | $447 | $2,897 ($241/mo) |
| ATS Program | Custom (est. $5-10k) | Lifetime |

### Products Offered
1. **TradingView Indicators (10+):** Qpro, Qgrid, Qelite, Qwave, Qline, Qcloud, Qbands, Qsmc, Qmomentum, Moneyball, Qcvd
2. **NinjaTrader Tools (8+):** Qgrid, Qdirector, Qwave, Qrenko bar type, Qcloud, Moneyball, QZeus strategy
3. **Automated Strategies (7+):** Qzeus, Qkronos_EVO, Qkronos, Qgrid_ELITE, Qscalper, Qsumo, Qcloud strategy
4. **ATS Program:** Custom Python-based automation platform with "machine learning"

---

## Technical Analysis: What Are They Actually Selling?

### Indicator Breakdown

#### 1. Qcloud (Step Moving Average)
**What they claim:** "Unique step moving average cloud with individually changing strings"
**What it actually is:** Multiple SMAs/EMAs with visual threshold changes (step-based smoothing)
**Comparable to:** Ichimoku cloud concept, GMMA (Guppy Multiple Moving Average)
**Reddit claim:** "Big Beluga Smooth Cloud with setting = 5"

#### 2. Qgrid (Pullback Position Adder)
**What they claim:** "Pull-back position adding indicator for trend following"
**What it actually is:** 
- Dual Heiken Ashi smoothing
- Step Moving Average overlay
- Generates "BULL/BEAR" flags and "ADD" signals on pullbacks
**Technical implementation:**
- HA Smooth Period 1 (adjustable)
- HA Smooth Period 2 (adjustable)
- Step MA sensitivity parameter

#### 3. Qwave (Breakout Alerts)
**What they claim:** "Over/under style alert indicator"
**What it actually is:** Keltner Channel variant with ATR-based bands
**Parameters:**
- Qwave Bands Deviation (adjusts band width)
- APB Number Of Bars Back (smoothing)

#### 4. Qline (Trend Ribbon)
**What they claim:** "Adaptive trend tracing ribbon"
**What it actually is:** Supertrend variant with customizable sensitivity
**Parameters:**
- Length (base period)
- Multiplier (ATR multiplier)
- Reactivity (color change threshold)

#### 5. Qbands (Adaptive Bands)
**What they claim:** "Adaptive price action bands for reversal detection"
**What it actually is:** Keltner Channels with trend line
**Parameters:**
- Length
- Band Deviation
- Trend Period

#### 6. Moneyball Oscillator
**What they claim:** "Most powerful indicator - sees subtle momentum changes"
**What it actually is:** MACD variant with enhanced visualization
**Parameters:**
- Period (sensitivity adjustment)
**Reddit claim:** "Basic MACD dressed up as something special"

#### 7. Qmomentum
**What they claim:** "Advanced divergence finding indicator"
**What it actually is:** RSI variant with divergence detection
**Parameters:**
- MA Type (EMA, SMA, RMA, WMA, VWMA, ALMA)
- Length

#### 8. Qcvd
**What they claim:** "Our take on Cumulative Volume Delta"
**What it actually is:** Standard CVD oscillator

#### 9. Qsmc (Smart Money Concepts)
**What they claim:** "All-in-one SMC toolkit"
**Features:**
- BOS (Break of Structure)
- CHoCH (Change of Character)
- Fair Value Gaps
- Order Blocks
- Liquidity Sweeps
- Market Session Boxes
**What it actually is:** Standard ICT/SMC indicators packaged together

---

## Strategy Analysis

### Core Automated Strategies

#### 1. Qzeus ("Set and Forget")
**Claimed win rate:** ~73%
**Entry Logic:** Proprietary (hidden)
**Exit Logic:**
- Static Take Profit Multiplier
- Stop Multiplier
**Special Features:**
- Martingale betting (doubles position after loss)
- Long Boost (doubles contracts on certain long conditions)
- Range Boost (increases take profit on range conditions)
- Max Contract Limit
- Time-based trading restrictions

#### 2. Qkronos_EVO (Adjustable Algorithm)
**Key Innovation:** Volatility multiplier that adjusts stops/TPs dynamically
**Volatility Calculation:** Proprietary formula based on:
1. Technical factor #1
2. Technical factor #2  
3. "Machine learning/data analytics" factor
**Entry Methods:**
- Original (fewer entries)
- Expanded (more entries)
- Always-In (continuous market exposure)
**Exit Methods:**
- Static Take Profit
- Trailing Stop
- Trailing with Tiered Exits
**Special Features:**
- Heiken Ashi smoothing option
- Qgrid confluence integration
- Pullback entry option with limit orders
- Martingale

#### 3. Qscalper (Multiple Scalping Types)
**Types:**
1. **Regular/Fast Scalpers:** Trade off Qwave/Qline support/resistance
   - Box lookback
   - Strength coefficient (% of boxes moving same direction)
   - Proximity coefficient (S/R boundary)
2. **Velox:** 
   - Sensitivity Factor
   - Sliding trail stop
   - Higher timeframe Qcloud confluence
3. **MB/CVD:**
   - Moneyball + CVD confluence
   - Static profit multiplier

#### 4. Qgrid_ELITE
**Purpose:** Grid-style scaling strategy
**Logic:** Add to positions on pullbacks to step MA

---

## The "Volatility Multiplier" - Their Secret Sauce?

Based on documentation, QuantVue's volatility multiplier appears to be:

```
volatility_multiplier = f(technical_1, technical_2, ml_factor)
```

**Likely components:**
1. **Technical Factor 1:** ATR-based (standard volatility measure)
2. **Technical Factor 2:** Price range/standard deviation
3. **ML Factor:** Likely historical optimization of multiplier values

**How it's used:**
- Stop Loss = Entry ± (volatility_multiplier × stop_coefficient)
- Take Profit = Entry ± (volatility_multiplier × tp_coefficient)
- Trail Offset = volatility_multiplier × trail_coefficient

This is similar to ATR-based position sizing (standard practice) with additional "secret sauce" coefficients.

---

## Renko Configuration

### Qrenko (NinjaTrader Custom Bar Type)
**Parameters:**
- Shift
- Offset
- Range

**Recommended Settings:**
| Market | Shift | Offset | Range |
|--------|-------|--------|-------|
| NQ | 7 | 11 | 33 |
| ES | 1 | 3 | 7 |

---

## Risk Management Approach

### Martingale Implementation
- Used in Qzeus and Qkronos_EVO
- Doubles position size after losses
- Justified by claiming 70%+ win rate with rarely >2 consecutive losses
- Max Contract Limit to cap exposure

### Range Boost
- Detects low-volatility ranging conditions
- Increases take profit multiplier during ranges
- "Almost no downside" per documentation

### Time-Based Controls
- Trading Time String (when to enter)
- Force Close options (when to exit)
- Trade Count Limits per day

---

## Automation Infrastructure

### TradingView → Broker Connection
- **AlertDragon:** Their sister company for alert routing
- **QuantLynk:** Their connector for copy trading
- Execution speeds claimed: <40-50ms

### ATS Program
- Custom Python-based platform
- Direct data feeds
- Machine learning strategies (proprietary)
- Runs on VPS

---

## Competitive Analysis

### What QuantVue Does Well
1. **Packaging:** Well-branded, consistent naming
2. **Documentation:** Comprehensive user manual
3. **Community:** Active Discord with 20,000+ members
4. **Support:** 24/7, responsive
5. **Marketing:** Professional, trustworthy appearance

### What's Not Unique
1. Indicators are repackaged versions of standard tools
2. "Machine learning" claims are vague
3. Core concepts (Renko, ATR bands, trend ribbons) are public domain
4. Martingale is a dangerous strategy that works until it doesn't

---

## Verdict

**QuantVue is NOT a scam** - they provide functional tools with good support.

**QuantVue is NOT revolutionary** - the underlying indicators and strategies are well-known concepts with proprietary naming and optimized parameters.

**Their actual edge (if any):**
1. Pre-optimized settings for futures markets
2. Well-integrated tool ecosystem
3. Community knowledge sharing
4. Automation infrastructure

**Risk factors:**
1. Martingale can lead to catastrophic losses
2. High cost for repackaged indicators
3. "Machine learning" claims are unverified
4. Past performance ≠ future results

---

## Sources
- docs.quantvue.io (official documentation)
- quantvue.io (main website)
- TradingView public scripts by QuantVue
- Reddit r/FuturesTrading, r/Daytrading discussions
- Business Insider press release (June 2024)
