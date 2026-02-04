# Greek Squeeze Detection Framework
## Complete Algorithmic System for 0DTE/1DTE Nuclear Plays

*Deep Research Compilation - February 2026*

---

## TABLE OF CONTENTS
1. [Core Greek Mechanics](#1-core-greek-mechanics)
2. [Gamma Squeeze Mathematics](#2-gamma-squeeze-mathematics)
3. [GEX Calculation Framework](#3-gex-calculation-framework)
4. [Squeeze Detection Algorithm](#4-squeeze-detection-algorithm)
5. [Setup Checklist](#5-setup-checklist)
6. [Entry/Exit Rules](#6-entryexit-rules)
7. [Vega & Second-Order Effects](#7-vega--second-order-effects)
8. [Data Requirements](#8-data-requirements)

---

## 1. CORE GREEK MECHANICS

### 1.1 Why 0DTE Greeks Are Different

**Key Insight**: In 0DTE/1DTE options, gamma and theta DOMINATE everything else. But the dynamics create feedback loops that don't exist in longer-dated options.

```
GREEK HIERARCHY FOR 0DTE:
┌────────────────────────────────────────────────────────┐
│ GAMMA >> THETA >> DELTA >> VEGA >> OTHER               │
│                                                        │
│ Delta changes so rapidly that market makers must       │
│ hedge continuously, creating the feedback loops        │
│ that produce "nuclear" moves.                          │
└────────────────────────────────────────────────────────┘
```

### 1.2 The Delta-Neutral Hedging Feedback Loop

**The Core Mechanism** (from arXiv research):

When a market maker sells N call options, their delta exposure is:
```
Δ_total = N × Δ_call
```

To stay delta-neutral, they hold stock position H_t:
```
H_t = N × Δ_call
```

**The Feedback Trigger**:
When price moves by ΔS, delta changes:
```
Δ(Δ_call) ≈ Γ × ΔS
```

Market maker must adjust holdings by:
```
ΔH_t = N × Γ × ΔS
```

**Price Impact**:
```
ΔS_t+1 = μS_t + λ × ΔH_t
       = μS_t + λ × N × Γ × ΔS_t

Solving: ΔS_t = μS_t / (1 - λ × G)

Where G = N × Γ (total gamma exposure)
```

### 1.3 The Gamma Squeeze Condition

**CRITICAL THRESHOLD**:
```
Gamma squeeze occurs when: D → 0

Where D = 1 - λ × G × φ(x)

λ = price impact coefficient (liquidity)
G = total gamma exposure (N × Γ)
φ(x) = hedging intensity function (increases with surprise)
x = normalized price surprise
```

**Interpretation**:
- When D approaches 0, even small exogenous shocks (μS_t) get magnified into HUGE price moves
- This is the mathematical definition of "going nuclear"

---

## 2. GAMMA SQUEEZE MATHEMATICS

### 2.1 Gamma Exposure (GEX) Formula

**Per-Strike GEX Calculation**:
```python
# For each option at strike K:
GEX_call = Γ_call × OI_call × 100 × S² × 0.01 × (+1)
GEX_put  = Γ_put  × OI_put  × 100 × S² × 0.01 × (-1)

GEX_strike = GEX_call + GEX_put
```

**Total Market GEX**:
```python
Total_GEX = Σ(GEX_all_strikes)
```

**Units**: $ per 1% move in underlying
- Positive GEX = Dealers LONG gamma = Mean-reverting (buy dips, sell rallies)
- Negative GEX = Dealers SHORT gamma = Momentum-amplifying (buy rallies, sell dips)

### 2.2 Gamma Scaling Near Expiration

**Time-to-Expiration Effect**:
```
Γ ∝ 1 / (S × σ × √τ)

As τ → 0:
- ATM gamma explodes (hyperbolic)
- Moving from 7 days to 1 day: gamma increases ~2.65x (√7)
- Moving from 1 day to 0 day (hours): gamma can increase 5-10x
```

**The 0DTE Gamma Explosion Chart**:
```
Gamma
  ^
  │     ****
  │    *
  │   *
  │  *      ← Day 1 (1DTE)
  │ *
  │*        ← Day 7
  └──────────────────> Time to Expiry
     7d  3d  1d  4hr  1hr  15min
```

### 2.3 Dealer Gamma Positioning Rules

**Standard Assumptions** (for index options like SPX/IWM):
```
CALL options: Dealers typically LONG (bought from retail selling covered calls)
PUT options: Dealers typically SHORT (sold to retail as insurance)

Therefore:
- Calls contribute POSITIVE gamma to dealer books
- Puts contribute NEGATIVE gamma to dealer books
```

**Net Dealer Position**:
```
Net_Dealer_Gamma = Σ(Call_Gamma) - Σ(Put_Gamma)
```

### 2.4 Beta-Normalized Surprise Factor

**From Academic Research** (arXiv 2511.22766):

Low-beta stocks are MORE susceptible to squeezes because the same absolute move represents a LARGER surprise:

```
Surprise Factor x = |ΔS/S| / (β × σ_market)

Where:
- ΔS/S = percentage price change
- β = stock's beta to market
- σ_market = current market volatility (VIX proxy)
```

**IWM Application**:
- IWM has lower individual stock betas vs SPX
- The same percentage move = HIGHER surprise
- More aggressive dealer hedging required
- **This is why IWM can squeeze harder than SPX for same percentage move**

---

## 3. GEX CALCULATION FRAMEWORK

### 3.1 Python Implementation (Production-Ready)

```python
import numpy as np
from scipy.stats import norm

def calculate_gex(S, K, vol, T, r, OI, option_type):
    """
    Calculate Gamma Exposure for a single option
    
    Args:
        S: Spot price
        K: Strike price
        vol: Implied volatility (decimal)
        T: Time to expiry (years, or fraction of day for 0DTE)
        r: Risk-free rate
        OI: Open interest
        option_type: 'call' or 'put'
    
    Returns:
        GEX in dollars per 1% move
    """
    if T <= 0 or vol <= 0:
        return 0
    
    # Black-Scholes d1
    d1 = (np.log(S/K) + (r + 0.5*vol**2)*T) / (vol*np.sqrt(T))
    
    # Gamma (same for calls and puts)
    gamma = norm.pdf(d1) / (S * vol * np.sqrt(T))
    
    # GEX per contract
    contract_size = 100
    gex = gamma * contract_size * OI * S * S * 0.01
    
    # Flip sign for puts (dealers short)
    if option_type == 'put':
        gex *= -1
    
    return gex

def calculate_total_gex(options_chain, spot_price):
    """
    Calculate total GEX across all strikes
    
    Args:
        options_chain: DataFrame with columns [strike, call_iv, put_iv, 
                       call_oi, put_oi, dte]
        spot_price: Current underlying price
    
    Returns:
        Dictionary with total GEX and GEX by strike
    """
    gex_by_strike = {}
    total_gex = 0
    
    for idx, row in options_chain.iterrows():
        K = row['strike']
        T = max(row['dte'] / 365, 1/365/24)  # Minimum 1 hour
        
        call_gex = calculate_gex(
            spot_price, K, row['call_iv'], T, 0.05, 
            row['call_oi'], 'call'
        )
        put_gex = calculate_gex(
            spot_price, K, row['put_iv'], T, 0.05,
            row['put_oi'], 'put'
        )
        
        strike_gex = call_gex + put_gex
        gex_by_strike[K] = strike_gex
        total_gex += strike_gex
    
    return {
        'total_gex': total_gex,
        'gex_by_strike': gex_by_strike,
        'gex_flip_zone': find_gamma_flip(gex_by_strike, spot_price)
    }

def find_gamma_flip(gex_by_strike, spot_price):
    """Find the price level where gamma flips from + to -"""
    strikes = sorted(gex_by_strike.keys())
    cumulative_gex = 0
    
    for i, strike in enumerate(strikes):
        prev_cumulative = cumulative_gex
        cumulative_gex += gex_by_strike[strike]
        
        # Check for sign flip
        if prev_cumulative * cumulative_gex < 0:
            # Linear interpolation to find exact flip point
            flip = strikes[i-1] + (strikes[i] - strikes[i-1]) * \
                   abs(prev_cumulative) / (abs(prev_cumulative) + abs(cumulative_gex))
            return flip
    
    return None
```

### 3.2 GEX Thresholds That Matter

**Based on SpotGamma Research**:
```
SPX GEX Levels:
├── > +$10B: Strong positive gamma (very pinning, low volatility)
├── +$5B to +$10B: Moderate positive (some pinning)
├── -$5B to +$5B: Neutral zone (normal volatility)
├── -$5B to -$15B: Negative gamma (trending, higher volatility)  
└── < -$15B: Deep negative gamma (squeeze potential HIGH)

IWM/Small Caps (scale down ~10x):
├── > +$1B: Strong positive
├── +$500M to +$1B: Moderate positive
├── -$500M to +$500M: Neutral
├── -$500M to -$1.5B: Negative (trending)
└── < -$1.5B: Deep negative (squeeze zone)
```

---

## 4. SQUEEZE DETECTION ALGORITHM

### 4.1 The Nuclear Setup Score

**Composite Score (0-100)**:
```python
def calculate_squeeze_score(data):
    """
    Calculate Nuclear Setup Score
    
    Returns score 0-100 where:
    - 0-30: Low probability
    - 30-60: Moderate probability  
    - 60-80: High probability
    - 80-100: NUCLEAR IMMINENT
    """
    score = 0
    
    # 1. Gamma Positioning (0-25 points)
    if data['net_gex'] < -10_000_000_000:  # -$10B for SPX
        score += 25
    elif data['net_gex'] < -5_000_000_000:
        score += 15
    elif data['net_gex'] < 0:
        score += 5
    
    # 2. Price Near Gamma Wall (0-20 points)
    distance_to_wall = abs(data['spot'] - data['nearest_gamma_wall'])
    pct_distance = distance_to_wall / data['spot'] * 100
    if pct_distance < 0.5:
        score += 20
    elif pct_distance < 1.0:
        score += 15
    elif pct_distance < 2.0:
        score += 5
    
    # 3. Volume/OI Ratio (0-15 points)
    vol_oi_ratio = data['volume'] / data['open_interest']
    if vol_oi_ratio > 2.0:
        score += 15
    elif vol_oi_ratio > 1.0:
        score += 10
    elif vol_oi_ratio > 0.5:
        score += 5
    
    # 4. IV Percentile (0-15 points)
    # Sweet spot: IV_percentile 20-40 (compressed, ready to expand)
    if 20 <= data['iv_percentile'] <= 40:
        score += 15
    elif 15 <= data['iv_percentile'] <= 50:
        score += 10
    elif data['iv_percentile'] < 60:
        score += 5
    
    # 5. Time of Day (0-10 points)
    hour = data['current_hour_et']
    if hour >= 14:  # Afternoon session
        score += 10
    elif hour >= 11:  # Mid-day
        score += 5
    elif hour <= 10:  # Morning session
        score += 8  # First hour can also be explosive
    
    # 6. VIX Relationship (0-10 points)
    if 15 <= data['vix'] <= 22:  # Sweet spot
        score += 10
    elif 12 <= data['vix'] <= 28:
        score += 5
    
    # 7. Underlying Momentum (0-5 points)
    # Already moving in a direction
    if abs(data['intraday_change_pct']) > 0.5:
        score += 5
    elif abs(data['intraday_change_pct']) > 0.25:
        score += 3
    
    return min(score, 100)
```

### 4.2 Gamma Wall Detection

```python
def find_gamma_walls(gex_by_strike, spot_price, threshold_pct=0.95):
    """
    Identify major gamma walls (support/resistance)
    
    Gamma walls are strikes where large dealer gamma 
    concentration creates magnetic pull or barrier.
    """
    strikes = sorted(gex_by_strike.keys())
    total_abs_gex = sum(abs(v) for v in gex_by_strike.values())
    
    gamma_walls = []
    
    for strike, gex in gex_by_strike.items():
        # Strike contributes >5% of total gamma
        if abs(gex) / total_abs_gex > 0.05:
            wall_type = 'support' if gex > 0 else 'resistance'
            gamma_walls.append({
                'strike': strike,
                'gex': gex,
                'type': wall_type,
                'distance_pct': (strike - spot_price) / spot_price * 100
            })
    
    # Sort by absolute GEX (strongest walls first)
    gamma_walls.sort(key=lambda x: abs(x['gex']), reverse=True)
    
    return gamma_walls[:5]  # Top 5 walls
```

### 4.3 The Squeeze Trigger Recognition

**Patterns That Precede Nuclear Moves**:

```
PATTERN 1: GAMMA WALL BREACH
├── Price consolidating at/near gamma wall
├── Volume building (coiling)
├── Sudden volume spike + price break through wall
└── TRIGGER: Dealer hedging reverses → momentum accelerates

PATTERN 2: GAMMA FLIP ZONE CROSS
├── Price trading in neutral gamma zone
├── Net GEX close to zero
├── Price crosses through flip zone
└── TRIGGER: Dealer positioning flips → momentum starts

PATTERN 3: 0DTE POSITION CLOSE
├── Large gamma positions visible at specific strikes
├── Price pinned near those strikes
├── Position suddenly closes (SpotGamma TRACE shows "wicks")
└── TRIGGER: Resistance removed → price released

PATTERN 4: AFTERNOON GAMMA ACCELERATION
├── 0DTE gamma increasing as time runs out
├── Price near high-OI strike
├── 2pm-3:30pm ET time window
└── TRIGGER: Time decay forces action → squeeze or crash
```

---

## 5. SETUP CHECKLIST

### 5.1 High-Probability Squeeze Conditions

**THE NUCLEAR CHECKLIST** - All conditions should be TRUE:

```
□ NET GAMMA POSITIONING
  └── Dealers are NET SHORT gamma (negative GEX)
  └── Threshold: SPX < -$5B, IWM < -$500M

□ PRICE AT CRITICAL LEVEL  
  └── Within 0.5% of major gamma wall OR
  └── Just crossed through gamma flip zone

□ VOLUME CONFIRMATION
  └── Volume/OI ratio > 1.0 at key strikes
  └── Unusual options activity detected
  └── Block trades or sweeps visible

□ IV SETUP
  └── IV percentile between 20-50 (room to expand)
  └── VIX between 15-25 (not too scared, not complacent)

□ TIME WINDOW
  └── 0DTE: 10:00-11:00 AM or 2:00-3:45 PM ET
  └── 1DTE: Any time, strongest near close

□ MOMENTUM PRESENT
  └── Price already moving in a direction
  └── Intraday move > 0.3%
  └── NOT consolidating/chopping
```

### 5.2 Quick Filter (For Scanning)

```python
def quick_squeeze_filter(data):
    """
    Fast filter to identify potential squeeze setups
    Returns True if worth deeper analysis
    """
    conditions = [
        data['net_gex'] < 0,                           # Negative gamma
        abs(data['spot'] - data['nearest_wall']) / data['spot'] < 0.02,  # Near wall
        data['volume_oi_ratio'] > 0.75,               # Active trading
        data['iv_percentile'] < 60,                   # Not too elevated
        abs(data['intraday_move_pct']) > 0.2          # Some momentum
    ]
    return sum(conditions) >= 4  # At least 4/5 conditions
```

---

## 6. ENTRY/EXIT RULES

### 6.1 Entry Timing

**BEFORE THE SQUEEZE (Ideal)**:
```
Entry Trigger:
├── Squeeze score > 65
├── Price approaching gamma wall from weak side
├── Volume starting to pick up
├── Option premiums still relatively cheap
└── ACTION: Enter with ATM or slightly OTM options

Position Sizing:
├── 0DTE: 0.5-1% of portfolio per trade
├── 1DTE: 1-2% of portfolio per trade
└── Never more than 2% on any single 0DTE play
```

**CHASING THE SQUEEZE (After It Starts)**:
```
Entry Trigger:
├── Price broke through gamma wall
├── Volume confirming (not fading)
├── Still within first 50% of expected move
└── ACTION: Enter with OTM options for leverage

Risk Management:
├── Smaller size (50% of normal)
├── Tighter stops (mental or actual)
└── Accept you're paying up for gamma
```

**TOO LATE TO ENTER**:
```
Signs It's Over:
├── Price moved > 1.5% from entry zone
├── Volume fading after initial spike
├── Options IV already spiked 50%+
├── Price reaching NEXT gamma wall
└── ACTION: Wait for next setup
```

### 6.2 Contract Selection

**0DTE Contract Selection Matrix**:
```
┌─────────────────────────────────────────────────────────────┐
│ MARKET CONDITION         │ STRIKE SELECTION                │
├─────────────────────────────────────────────────────────────┤
│ Pre-squeeze (building)   │ ATM or 1 strike OTM             │
│ Early squeeze (starting) │ 1-2 strikes OTM                 │
│ Mid-squeeze (running)    │ 2-3 strikes OTM (cheaper gamma) │
│ Expecting reversal       │ ATM for both directions         │
└─────────────────────────────────────────────────────────────┘

DELTA TARGETS:
├── Conservative: 0.40-0.50 delta (ATM)
├── Aggressive:   0.25-0.35 delta (OTM)
└── Lottery:      0.10-0.20 delta (Far OTM)
```

### 6.3 Exit Rules (The Hard Part)

**PROFIT TAKING TIERS**:
```python
def exit_strategy_0dte(entry_price, current_price, position_size):
    """
    Tiered exit strategy for 0DTE nuclear plays
    """
    gain_pct = (current_price - entry_price) / entry_price * 100
    
    exits = []
    
    if gain_pct >= 50:
        # First tier: Lock in profits
        exits.append({
            'action': 'SELL',
            'size': position_size * 0.33,
            'reason': '50% gain - secure initial profit'
        })
    
    if gain_pct >= 100:
        # Second tier: Playing with house money
        exits.append({
            'action': 'SELL',
            'size': position_size * 0.33,
            'reason': '100% gain - now risk-free'
        })
    
    if gain_pct >= 150:
        # Third tier: Let runners run
        exits.append({
            'action': 'SELL',
            'size': position_size * 0.25,
            'reason': '150% gain - taking more off'
        })
    
    # Keep 10-20% as lottery ticket if still running
    
    return exits
```

**EXIT SIGNALS (When To Get Out)**:
```
IMMEDIATE EXIT:
├── Price reverses and breaks back through gamma wall
├── Volume disappears suddenly
├── IV starts collapsing (squeeze exhausting)
├── Hit profit target (don't get greedy)

TRAILING STOP APPROACH:
├── After 50% gain: trail at 30% of max gain
├── After 100% gain: trail at 50% of max gain
├── After 150% gain: trail at 60% of max gain
├── Time stop: Exit 15 min before close regardless
```

**SQUEEZE EXHAUSTION SIGNALS**:
```
Signs The Move Is Done:
1. Price hits next major gamma wall (resistance becomes support)
2. Volume spike then sudden drop (climax)
3. Options IV peaked and reversing
4. Underlying showing doji/reversal candle pattern
5. Price overshot expected move by 50%+
```

---

## 7. VEGA & SECOND-ORDER EFFECTS

### 7.1 Vega in 0DTE Context

**Key Insight**: 0DTE options are "gamma-rich but vega-poor"

```
VEGA CHARACTERISTICS:
├── Vega decreases as expiration approaches
├── 0DTE vega is minimal BUT NOT ZERO
├── Early in session: vega still matters for IV spikes
├── Key events (FOMC, CPI): vega can dominate early
└── Last 2 hours: gamma completely dominates vega
```

**When Vega Matters (Even for 0DTE)**:
- First 30-60 minutes of trading session
- Around major economic releases
- Before Fed announcements
- During sudden market-wide stress

### 7.2 Charm (Delta Decay)

**Definition**: Rate of change of delta with respect to time
```
Charm = ∂Δ/∂t
```

**0DTE Impact**:
```
As expiration approaches:
├── ATM options: Charm is minimal (delta stays ~0.5)
├── OTM options: Charm is LARGE (delta decaying fast)
├── ITM options: Charm pulls delta toward 1.0
└── Near expiration, charm effects are extreme
```

**Trading Implication**:
- OTM options lose delta value quickly even without price move
- Your call at 0.30 delta might be 0.10 delta in 2 hours
- Need the move to happen FAST for OTM options

### 7.3 Vanna (Delta-Volatility Sensitivity)

**Definition**: Rate of change of delta with respect to IV
```
Vanna = ∂Δ/∂σ = ∂Vega/∂S
```

**Why It Matters**:
```
When IV rises:
├── OTM call deltas INCREASE (become more valuable)
├── OTM put deltas DECREASE (become less negative)
└── This is WHY calls can explode during squeezes

Dealer Impact:
├── If dealers are short OTM calls + IV spikes
├── Their delta exposure suddenly jumps
├── Forces MORE hedging (buying underlying)
└── Amplifies the squeeze further
```

### 7.4 Volga/Vomma (Vega Convexity)

**Definition**: Rate of change of vega with respect to IV
```
Volga = ∂Vega/∂σ
```

**Impact**: Creates acceleration effects where IV moves feed on themselves

---

## 8. DATA REQUIREMENTS

### 8.1 Essential Data Feeds

**Real-Time (During Market Hours)**:
```
MUST HAVE:
├── Options chain with Greeks (delta, gamma, vega, theta)
├── Live IV by strike
├── Volume by strike (updated every minute minimum)
├── Underlying price (sub-second)
└── VIX/VIX1D real-time

NICE TO HAVE:
├── Dealer positioning estimates (SpotGamma, etc.)
├── Options flow (sweeps, blocks)
├── Open interest changes intraday
└── Trade tape for options
```

### 8.2 Polygon.io Capabilities

**What Polygon Provides**:
```python
# Options Chain Snapshot (includes Greeks)
endpoint = "/v3/snapshot/options/{underlyingAsset}"

Response includes:
├── strike_price
├── expiration_date
├── implied_volatility
├── open_interest
├── volume
├── greeks (delta, gamma, theta, vega)
├── break_even_price
└── day (open, high, low, close, volume)
```

**Limitations**:
- Historical Greeks/IV NOT available (snapshot only)
- Need to calculate GEX yourself from raw data
- No dealer positioning data (need SpotGamma or similar)

### 8.3 Alternative/Complementary Data Sources

```
FREE/CHEAP:
├── CBOE Delayed Quotes (includes Greeks, 15-min delay)
├── Barchart GEX levels (free tier available)
├── Yahoo Finance options chains
└── TradingView (some options data)

PROFESSIONAL:
├── SpotGamma ($99-299/month) - Best for GEX/dealer positioning
├── GEXStream - Real-time gamma exposure
├── OptionStrat - Flow and unusual activity
├── UnusualWhales - Options flow scanning
└── Quant Data - Block trades and sweeps
```

### 8.4 Building Your Own GEX System

**Minimum Viable System**:
```
Data Pipeline:
1. Polygon API → Options chain snapshot (every 5 min)
2. Calculate Greeks if not provided
3. Compute GEX by strike
4. Aggregate to total GEX
5. Find gamma walls and flip zones
6. Display on chart with underlying price

Alert Triggers:
├── Net GEX crosses threshold
├── Price approaches gamma wall
├── Volume spike at key strike
└── Squeeze score exceeds 70
```

---

## SOURCES & REFERENCES

**Academic Research**:
- arXiv 2511.22766: "Beta-Dependent Gamma Feedback and Endogenous Volatility Amplification in Option Markets"
- CBOE Research: "0DTE Index Options and Market Volatility"
- SSRN: "0DTEs: Trading, Gamma Risk and Volatility Propagation"

**Industry Sources**:
- SpotGamma: Gamma exposure methodology and tools
- Glassnode: Taker-flow-based GEX for crypto (methodology applicable to equities)
- perfiliev.com: GEX calculation tutorial and Python implementation

**Practitioner Knowledge**:
- MenthorQ guides on 0DTE gamma exposure
- OptionAlpha research on 0DTE time decay patterns
- TradingBlock 0DTE strategies documentation

---

*This document is for educational purposes. Options trading involves substantial risk. 0DTE options can lose 100% of value within hours.*
