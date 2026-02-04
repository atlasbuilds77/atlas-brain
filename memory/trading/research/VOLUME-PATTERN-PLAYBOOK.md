# Volume Pattern Playbook
## Reading Options Flow for Nuclear 0DTE/1DTE Plays

*Deep Research Compilation - February 2026*

---

## TABLE OF CONTENTS
1. [Understanding "Unusual" Volume](#1-understanding-unusual-volume)
2. [Volume/OI Analysis](#2-volumeoi-analysis)
3. [Order Flow Types](#3-order-flow-types)
4. [Pre-Squeeze Patterns](#4-pre-squeeze-patterns)
5. [Real-Time Flow Reading](#5-real-time-flow-reading)
6. [Scanning Algorithms](#6-scanning-algorithms)
7. [Tools & Platforms](#7-tools--platforms)

---

## 1. UNDERSTANDING "UNUSUAL" VOLUME

### 1.1 What "Unusual" Actually Means

**Key Insight**: Unusual isn't just "big" - it's big RELATIVE to normal activity

```
UNUSUAL VOLUME DEFINITION:
┌─────────────────────────────────────────────────────────────┐
│ Volume is "unusual" when:                                   │
│                                                             │
│ Today's Volume > (Average Volume × Threshold Multiplier)    │
│                                                             │
│ Common thresholds:                                          │
│ ├── 2x average = Notable                                    │
│ ├── 5x average = Unusual                                    │
│ ├── 10x average = Highly unusual                            │
│ └── 20x+ average = SOMETHING IS HAPPENING                   │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 The Sizzle Index

**ThinkOrSwim's Sizzle Index**:
```
Sizzle = Today's Option Volume / Average Daily Option Volume

Interpretation:
├── Sizzle < 1.0: Below average activity
├── Sizzle 1.0-2.0: Normal activity  
├── Sizzle 2.0-3.0: Elevated (pay attention)
├── Sizzle 3.0-5.0: Unusual (investigate)
└── Sizzle > 5.0: HIGHLY unusual (likely something brewing)
```

### 1.3 Strike-Specific Unusual Activity

**More Precise Detection**:
```
For each strike, calculate:
├── Current day volume
├── 20-day average volume for that strike
├── Ratio = Today / Average
└── Flag if ratio > 3.0

CRITICAL: Filter for NEAR-MONEY strikes
├── OTM options seeing unusual volume near current price = SIGNAL
├── Far OTM options seeing unusual volume = Often noise
└── Focus on strikes within 2-3% of current price
```

### 1.4 Volume Timing Patterns

**Intraday Volume Distribution (Normal Day)**:
```
Volume
  ^
  │  **               **
  │ *  *             *  *
  │*    *           *    *
  │      ***********
  └──────────────────────────> Time
  9:30  11:00  12:30  2:00  4:00

The "U-Curve":
├── High volume 9:30-10:30 AM (opening action)
├── Low volume 11:30 AM-2:00 PM (lunch lull)
└── High volume 2:30-4:00 PM (closing push)
```

**Pre-Squeeze Volume Pattern**:
```
Volume
  ^
  │                   ****
  │           **     *    
  │  **      *  *   *      
  │ *  *    *    ***        
  │*    ****                 
  └──────────────────────────> Time
  9:30  11:00  12:30  2:00  4:00

DEVIATION FROM NORMAL:
├── Volume builds during lull period (11-2)
├── Coiling/accumulation phase
├── Then EXPLOSION in afternoon
└── This is the "spring loading" pattern
```

---

## 2. VOLUME/OI ANALYSIS

### 2.1 The Volume/OI Ratio

**Core Concept**:
```
Volume/OI Ratio = Today's Volume / Open Interest

Interpretation:
├── < 0.25: Low activity (not interesting)
├── 0.25-0.50: Moderate activity
├── 0.50-1.0: Active (worth watching)
├── 1.0-2.0: HIGHLY active (something happening)
└── > 2.0: NEW POSITIONS being established (ALERT)
```

**Why This Matters**:
```
If Volume > Open Interest:
├── New positions are being opened
├── Not just churning existing positions
├── Someone has CONVICTION
└── Potential for larger move

If Volume << Open Interest:
├── Just trading existing positions
├── Less conviction
└── May be rolling or adjusting
```

### 2.2 OI Changes and Their Meaning

**Overnight OI Change Analysis**:
```
┌─────────────────────────────────────────────────────────────┐
│ Price UP + OI UP     = New longs entering (bullish)         │
│ Price UP + OI DOWN   = Shorts covering (bullish, but weak)  │
│ Price DOWN + OI UP   = New shorts entering (bearish)        │
│ Price DOWN + OI DOWN = Longs exiting (bearish, but weak)    │
└─────────────────────────────────────────────────────────────┘
```

**Intraday OI Implications**:
```
(Note: OI updates are typically overnight, but volume
gives real-time hints about what OI will show tomorrow)

High Volume at Strike + Price Moving Toward Strike:
└── OI likely to increase = Strong positioning

High Volume at Strike + Price Moving Away:
└── Could be profit-taking = Position unwinding
```

### 2.3 The Call/Put Volume Ratio

**Simple Sentiment**:
```
Call Volume / Put Volume:

├── > 2.0: Very bullish sentiment
├── 1.5-2.0: Bullish sentiment
├── 0.67-1.5: Neutral
├── 0.5-0.67: Bearish sentiment
└── < 0.5: Very bearish sentiment

FOR 0DTE SQUEEZE DETECTION:
├── Rising call/put ratio + price coiling = Bullish squeeze setup
├── Falling call/put ratio + price coiling = Bearish squeeze setup
└── Extreme readings (>3 or <0.3) often precede reversals
```

### 2.4 Put/Call OI Ratio at Strikes

**Gamma Wall Identification**:
```
At each strike, calculate:
Put_OI / Call_OI

├── > 2.0: Mostly puts = Potential support (dealers short puts)
├── 1.0-2.0: Put-heavy but mixed
├── 0.5-1.0: Call-heavy but mixed
├── < 0.5: Mostly calls = Potential resistance (dealers long calls)

Combined with GEX:
├── High put OI + Negative GEX = Strong support
├── High call OI + Positive GEX = Strong resistance
```

---

## 3. ORDER FLOW TYPES

### 3.1 Block Trades

**Definition**: 
Large trades executed as single orders, typically negotiated privately and printed to tape.

```
BLOCK TRADE CHARACTERISTICS:
├── Single print, large size (500+ contracts for liquid names)
├── Often at NBBO midpoint
├── Executed off-exchange (dark pool) then reported
├── Indicates institutional positioning
└── High conviction (paying full premium)

DETECTION:
├── Size >> average trade size
├── Single timestamp, single print
├── May be flagged with "Block" code
```

**Block Trade Significance**:
```
BULLISH BLOCKS (Calls at Ask, Puts at Bid):
├── Buyer paying up = Urgency
├── Larger blocks = Higher conviction
└── Near-money blocks = Expect imminent move

BEARISH BLOCKS (Calls at Bid, Puts at Ask):
├── Seller taking less = Urgency to exit/short
├── Could be profit-taking OR new short
└── Context matters (what happened before?)
```

### 3.2 Sweep Orders

**Definition**:
Orders that aggressively take liquidity across multiple price levels and/or exchanges to get filled quickly.

```
SWEEP ORDER CHARACTERISTICS:
├── Multiple smaller prints in rapid succession
├── Takes out multiple price levels
├── Shows URGENCY (willing to pay higher prices)
├── Often algo-reconstructed from tape
└── Strongest signal of conviction

DETECTION:
├── Series of trades within seconds
├── Progressive price levels (walking the book)
├── Total size significant
├── Flagged as "Sweep" by platforms
```

**Sweep Order Example**:
```
10:15:00.100  AAPL 150C  Buy 100 @ 2.10
10:15:00.105  AAPL 150C  Buy 150 @ 2.11  
10:15:00.108  AAPL 150C  Buy 200 @ 2.12
10:15:00.112  AAPL 150C  Buy 100 @ 2.14
────────────────────────────────────────
SWEEP DETECTED: 550 contracts, walked up $0.04
```

### 3.3 Split Orders

**Definition**:
Large orders broken into smaller pieces and executed over time to minimize market impact.

```
SPLIT ORDER CHARACTERISTICS:
├── Similar size prints over extended period
├── Same strike/expiry
├── Attempting to hide size
├── Still indicates institutional activity
└── Less urgency than sweeps but still conviction

DETECTION:
├── Pattern recognition across time
├── Consistent size "signature"
├── Algorithmic detection required
```

### 3.4 The Flow Sentiment Matrix

```
┌──────────────────────────────────────────────────────────────────┐
│ ORDER TYPE    │ TRADE SIDE     │ MEANING                        │
├──────────────────────────────────────────────────────────────────┤
│ Block Call    │ At Ask (Buy)   │ Very bullish, institutional    │
│ Block Call    │ At Bid (Sell)  │ Selling calls, could be cover  │
│ Block Put     │ At Ask (Buy)   │ Very bearish, institutional    │
│ Block Put     │ At Bid (Sell)  │ Selling puts, could be bullish │
├──────────────────────────────────────────────────────────────────┤
│ Sweep Call    │ At Ask (Buy)   │ EXTREMELY bullish, urgent      │
│ Sweep Call    │ At Bid (Sell)  │ Urgent exit, bearish           │
│ Sweep Put     │ At Ask (Buy)   │ EXTREMELY bearish, urgent      │
│ Sweep Put     │ At Bid (Sell)  │ Urgent exit, could be bullish  │
└──────────────────────────────────────────────────────────────────┘

NUCLEAR SIGNAL:
├── Sweep + Near Money + 0DTE/1DTE + Large Size = 💥
└── Especially if multiple sweeps in same direction
```

### 3.5 The "Golden Sweep"

**Definition** (per InsiderFinance):
```
Golden Sweep = Sweep > $1M premium + Top Position

Criteria:
├── Premium > $1,000,000
├── Sweep execution (urgent)
├── Among top positions for that ticker
└── Often determines short-term direction

0DTE Application:
├── Even $500K+ sweeps are significant for 0DTE
├── Speed of execution matters more than size
└── Multiple smaller sweeps = equivalent signal
```

---

## 4. PRE-SQUEEZE PATTERNS

### 4.1 The Coiling Pattern

**Visual Recognition**:
```
Price
  ^
  │     ╱╲       ╱╲
  │    ╱  ╲     ╱  ╲    Narrowing range
  │   ╱    ╲   ╱    ╲   = Coiling
  │  ╱      ╲ ╱      ╲
  │ ╱        ╳        ╲
  │╱                   ╲════════ Breakout imminent
  └──────────────────────────> Time

VOLUME DURING COIL:
├── Overall volume declining (compression)
├── BUT options volume steady or rising
└── Divergence = Spring loading
```

### 4.2 Volume Shelf Pattern

**Definition**: Visible "wall" of volume at specific strikes

```
Open Interest by Strike
  ^
  │                    ████
  │         ████       ████
  │    ██   ████  ██   ████
  │   ███   ████ ███   ████
  │  ████   ████ ████  ████
  └──────────────────────────> Strike
     195  200  205  210  215

VOLUME SHELF:
├── Visible concentration at specific strikes
├── Often round numbers ($200, $210, etc.)
├── Creates gamma walls
└── Price tends to gravitate toward OR repel from these
```

### 4.3 The Unusual Activity Cluster

**Pattern Recognition**:
```
UNUSUAL ACTIVITY CLUSTER:
├── Multiple strikes showing unusual volume
├── All in same direction (calls or puts)
├── Concentrated in near-money or slightly OTM
├── Building over 30-60 minutes
└── Often precedes directional move

EXAMPLE:
Time     Strike   Type   Volume   Avg     Ratio
10:15    210C     Call   5,000    500     10x ⚠️
10:22    212C     Call   3,500    400     8.75x ⚠️
10:31    215C     Call   8,000    600     13.3x ⚠️
10:45    210C     Call   4,000    500     8x ⚠️
────────────────────────────────────────────────
CLUSTER DETECTED: Bullish call buying across strikes
```

### 4.4 The Position Buildup → Close Pattern

**From SpotGamma Research**:
```
TIMELINE:
1. Position Opens (10:30 AM example)
   └── Large gamma appears at strike
   └── Price pins to that area

2. Position Grows (10:30 AM - 12:00 PM)
   └── Gamma increases at strike
   └── Price remains "stuck"

3. Position Closes (12:00 PM)
   └── Gamma disappears (TRACE shows "wick")
   └── Price RELEASED

4. Squeeze Occurs (12:00 PM - 1:00 PM)
   └── Without resistance, price runs
   └── Next gamma wall becomes target

TRADING IMPLICATION:
├── Monitor for large gamma positions
├── Wait for position to close
├── Enter AS IT CLOSES or immediately after
└── Target next gamma wall
```

### 4.5 The Afternoon Gamma Acceleration

**0DTE Specific Pattern**:
```
Time of Day vs Gamma Intensity
  ^
  │                          ****
  │                      ****
  │                  ****
  │              ****
  │**********
  └──────────────────────────────> Time (ET)
  9:30   11:00   1:00   3:00   4:00

After 2:00 PM:
├── 0DTE gamma increases exponentially
├── Small price moves = Big delta changes
├── Dealers forced to hedge aggressively
└── Squeeze potential maximizes

KEY WINDOW: 2:00 PM - 3:30 PM ET
├── Gamma at peak
├── Time decay forcing action
├── Volume typically increasing
└── Most "nuclear" moves happen here
```

---

## 5. REAL-TIME FLOW READING

### 5.1 Flow Dashboard Setup

**What To Monitor**:
```
SCREEN 1: Options Flow Feed
├── Real-time trades
├── Filtered for: Premium > $25K, 0DTE/1DTE
├── Color coded: Green = Calls at Ask, Red = Puts at Ask
└── Sweep/Block flags visible

SCREEN 2: Volume Heatmap
├── Strikes on Y-axis
├── Time on X-axis
├── Color intensity = Volume
└── Quickly spot where action is

SCREEN 3: GEX Profile
├── Current GEX by strike
├── Gamma walls highlighted
├── Flip zone marked
└── Updated every 5-10 minutes

SCREEN 4: Underlying Price
├── 1-min or 5-min chart
├── Key levels marked
├── Volume bars
└── VWAP and key MAs
```

### 5.2 Flow Reading Process

**5-Minute Check Routine**:
```
STEP 1: Check Net Flow Direction
└── More calls at ask or puts at ask?
└── Is sentiment shifting?

STEP 2: Identify Largest Trades
└── Any sweeps > $100K in last 5 min?
└── What strikes are being targeted?

STEP 3: Compare to GEX Levels
└── Is flow pushing toward or away from gamma walls?
└── Are we near the flip zone?

STEP 4: Check Volume/OI at Key Strikes
└── Is volume building at specific strikes?
└── Any unusual ratios emerging?

STEP 5: Make Decision
└── Setup forming? → Prepare entry
└── Already in? → Manage position
└── Nothing happening? → Wait
```

### 5.3 Flow Interpretation Examples

**BULLISH SQUEEZE SETUP**:
```
Observations:
├── Multiple call sweeps at 210-215 strikes
├── Premium > $50K each
├── All executed at ask
├── Volume/OI > 1.5 at these strikes
├── Price currently at 208
├── GEX shows negative gamma zone 208-212
└── Time: 2:15 PM

Interpretation:
├── Smart money aggressively buying calls
├── Targeting strikes just above current price
├── GEX supports breakout (negative = amplifying)
├── Afternoon gamma acceleration in effect
└── ACTION: Buy 210 or 212 calls
```

**BEARISH SQUEEZE SETUP**:
```
Observations:
├── Large put blocks at 200 and 198 strikes
├── Executed at ask (buying puts)
├── Volume/OI > 2.0
├── Price currently at 204
├── GEX shows gamma wall support at 200
├── But massive put buying suggests wall will break
└── Time: 10:30 AM

Interpretation:
├── Institutional put buying
├── Targeting support zone
├── May overwhelm gamma wall
├── Early in day = time for move to develop
└── ACTION: Buy 200 or 198 puts
```

### 5.4 Flow Traps To Avoid

**FALSE SIGNALS**:
```
1. SPREAD TRADES
├── Looks like big call buying
├── Actually one leg of a spread
├── Net exposure may be neutral
└── Check for paired trades at other strikes

2. ROLL TRADES
├── Closing near-term, opening far-term
├── Volume at both expirations
├── Not a directional bet
└── Check for offsetting trades

3. HEDGING ACTIVITY
├── Options bought to hedge stock position
├── May look bullish (call buying)
├── But actually reducing exposure
└── Context of underlying position matters

4. DELTA-NEUTRAL TRADES
├── Buying calls AND selling stock
├── Or buying puts AND buying stock
├── Market-making activity
└── No directional signal
```

---

## 6. SCANNING ALGORITHMS

### 6.1 Unusual Volume Scanner

```python
def scan_unusual_volume(options_data, threshold=3.0):
    """
    Scan for unusual options volume
    
    Args:
        options_data: DataFrame with current and historical volume
        threshold: Multiplier for "unusual" (default 3x)
    
    Returns:
        List of unusual activity
    """
    unusual = []
    
    for idx, row in options_data.iterrows():
        if row['avg_volume_20d'] > 0:
            ratio = row['current_volume'] / row['avg_volume_20d']
            
            if ratio >= threshold:
                unusual.append({
                    'symbol': row['symbol'],
                    'strike': row['strike'],
                    'expiry': row['expiry'],
                    'type': row['option_type'],
                    'volume': row['current_volume'],
                    'avg_volume': row['avg_volume_20d'],
                    'ratio': ratio,
                    'oi': row['open_interest'],
                    'vol_oi': row['current_volume'] / row['open_interest']
                })
    
    # Sort by ratio descending
    unusual.sort(key=lambda x: x['ratio'], reverse=True)
    
    return unusual
```

### 6.2 Sweep Detector

```python
def detect_sweeps(trade_tape, time_window_sec=5, min_contracts=200):
    """
    Detect sweep orders from trade tape
    
    Args:
        trade_tape: List of trades with timestamp, price, size
        time_window_sec: Window to group trades
        min_contracts: Minimum size to consider sweep
    
    Returns:
        List of detected sweeps
    """
    sweeps = []
    
    # Group trades by option contract
    grouped = {}
    for trade in trade_tape:
        key = f"{trade['strike']}_{trade['type']}_{trade['expiry']}"
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(trade)
    
    for key, trades in grouped.items():
        # Sort by timestamp
        trades.sort(key=lambda x: x['timestamp'])
        
        # Find clusters within time window
        i = 0
        while i < len(trades):
            cluster = [trades[i]]
            j = i + 1
            
            while j < len(trades):
                time_diff = (trades[j]['timestamp'] - trades[i]['timestamp']).total_seconds()
                if time_diff <= time_window_sec:
                    cluster.append(trades[j])
                    j += 1
                else:
                    break
            
            # Check if cluster qualifies as sweep
            total_size = sum(t['size'] for t in cluster)
            if total_size >= min_contracts and len(cluster) >= 3:
                # Check for price progression (walking the book)
                prices = [t['price'] for t in cluster]
                if prices[-1] > prices[0]:  # Buying (prices rising)
                    direction = 'BUY'
                elif prices[-1] < prices[0]:  # Selling
                    direction = 'SELL'
                else:
                    direction = 'NEUTRAL'
                
                sweeps.append({
                    'contract': key,
                    'total_size': total_size,
                    'num_trades': len(cluster),
                    'price_start': prices[0],
                    'price_end': prices[-1],
                    'direction': direction,
                    'timestamp': cluster[0]['timestamp'],
                    'premium': total_size * 100 * prices[-1]
                })
            
            i = j
    
    return sweeps
```

### 6.3 Gamma Wall Breach Alert

```python
def check_gamma_wall_breach(current_price, previous_price, gamma_walls):
    """
    Check if price is approaching or breaching gamma walls
    
    Args:
        current_price: Current underlying price
        previous_price: Price from last check (e.g., 5 min ago)
        gamma_walls: List of gamma wall levels
    
    Returns:
        Alert if breach detected
    """
    alerts = []
    
    for wall in gamma_walls:
        wall_price = wall['strike']
        wall_type = wall['type']  # 'support' or 'resistance'
        
        # Approaching wall
        distance_pct = abs(current_price - wall_price) / current_price * 100
        if distance_pct < 0.5:  # Within 0.5%
            alerts.append({
                'type': 'APPROACHING',
                'wall': wall_price,
                'wall_type': wall_type,
                'distance_pct': distance_pct
            })
        
        # Breaching wall
        if wall_type == 'resistance':
            if previous_price < wall_price <= current_price:
                alerts.append({
                    'type': 'BREACH_UP',
                    'wall': wall_price,
                    'action': 'BUY CALLS - Resistance broken'
                })
        elif wall_type == 'support':
            if previous_price > wall_price >= current_price:
                alerts.append({
                    'type': 'BREACH_DOWN',
                    'wall': wall_price,
                    'action': 'BUY PUTS - Support broken'
                })
    
    return alerts
```

### 6.4 Nuclear Setup Scanner

```python
def scan_nuclear_setups(tickers, data_provider):
    """
    Comprehensive scanner for nuclear squeeze setups
    
    Args:
        tickers: List of tickers to scan (e.g., ['SPY', 'IWM', 'QQQ'])
        data_provider: Data source object
    
    Returns:
        Ranked list of setups
    """
    setups = []
    
    for ticker in tickers:
        # Get options data
        chain = data_provider.get_options_chain(ticker, dte_max=1)
        spot = data_provider.get_spot_price(ticker)
        
        # Calculate GEX
        gex_data = calculate_total_gex(chain, spot)
        
        # Get unusual volume
        unusual = scan_unusual_volume(chain, threshold=2.0)
        
        # Get sweeps in last 30 min
        tape = data_provider.get_trade_tape(ticker, minutes=30)
        sweeps = detect_sweeps(tape)
        
        # Find gamma walls
        walls = find_gamma_walls(gex_data['gex_by_strike'], spot)
        
        # Calculate squeeze score
        score_data = {
            'net_gex': gex_data['total_gex'],
            'spot': spot,
            'nearest_gamma_wall': walls[0]['strike'] if walls else spot,
            'volume': sum(c['volume'] for c in chain if abs(c['strike'] - spot) / spot < 0.03),
            'open_interest': sum(c['oi'] for c in chain if abs(c['strike'] - spot) / spot < 0.03),
            'iv_percentile': get_iv_percentile(ticker),
            'current_hour_et': get_current_hour_et(),
            'vix': get_vix(),
            'intraday_change_pct': get_intraday_change(ticker)
        }
        
        score = calculate_squeeze_score(score_data)
        
        if score >= 50:  # Only report setups with score >= 50
            setups.append({
                'ticker': ticker,
                'score': score,
                'gex': gex_data['total_gex'],
                'nearest_wall': walls[0] if walls else None,
                'unusual_count': len(unusual),
                'sweeps': sweeps,
                'direction': 'BULLISH' if sum(s['direction'] == 'BUY' and 'C' in s['contract'] for s in sweeps) > len(sweeps)/2 else 'BEARISH'
            })
    
    # Sort by score
    setups.sort(key=lambda x: x['score'], reverse=True)
    
    return setups
```

---

## 7. TOOLS & PLATFORMS

### 7.1 Free/Low-Cost Options

```
BARCHART.COM (Free Tier)
├── Unusual Options Activity page
├── Options Flow feed
├── GEX levels (basic)
└── Good for scanning, limited real-time

YAHOO FINANCE
├── Options chains
├── Volume data
├── No Greeks or flow
└── Good for basic OI analysis

TRADINGVIEW
├── Options data on some symbols
├── Volume profile tools
├── Custom indicators possible
└── Good for charting with levels

CBOE DELAYED QUOTES
├── Full options chains
├── Includes Greeks
├── 15-minute delay
└── Good for end-of-day analysis
```

### 7.2 Professional Platforms

```
SPOTGAMMA ($99-299/month)
├── Real-time GEX levels
├── TRACE tool for 0DTE flow
├── Gamma walls and flip zones
├── TAPE for trade analysis
└── BEST for gamma-focused trading

UNUSUALWHALES ($50-100/month)
├── Flow scanner
├── Sweep detection
├── Historical flow
├── Good UI
└── Good for flow-focused trading

OPTIONSTRAT ($25-50/month)
├── Options flow
├── Strategy builder
├── Position analysis
└── Good for strategy construction

QUANTDATA ($50/month)
├── Blocks, sweeps, splits
├── Algorithmic detection
├── Clean feed
└── Good for pure flow reading

FLOWALGO ($100/month)
├── Real-time flow
├── Dark pool data
├── Sweep detection
└── Established platform
```

### 7.3 Data APIs

```
POLYGON.IO
├── Options chains with Greeks
├── Real-time trades/quotes
├── WebSocket streaming
├── $99-299/month for options
└── Good for building custom tools

TRADIER
├── Options API
├── Streaming quotes
├── Lower cost
└── Good for brokerage integration

CBOE DATA SHOP
├── Historical data
├── Institutional quality
├── Expensive
└── For serious research
```

### 7.4 Recommended Stack for Hunting

**MINIMAL VIABLE STACK**:
```
1. SpotGamma or GEXStream (GEX levels)
2. TradingView (charting with levels)
3. Free flow scanner (Barchart or OptionStrat free tier)
4. Your broker's options chain
```

**FULL HUNTER STACK**:
```
1. SpotGamma Alpha (GEX + TRACE + TAPE)
2. OptionStrat or UnusualWhales (flow)
3. TradingView Premium (charting)
4. Polygon API (custom analysis)
5. Custom alerting system
```

---

## QUICK REFERENCE CARD

```
┌─────────────────────────────────────────────────────────────────┐
│                    VOLUME PATTERN CHEAT SHEET                   │
├─────────────────────────────────────────────────────────────────┤
│ UNUSUAL VOLUME:                                                 │
│ • Volume > 3x average = Unusual                                 │
│ • Volume > OI = New positions                                   │
│ • Focus on near-money strikes                                   │
├─────────────────────────────────────────────────────────────────┤
│ ORDER TYPES:                                                    │
│ • Block at Ask = Bullish conviction                             │
│ • Sweep = URGENT, strongest signal                              │
│ • Golden Sweep (>$1M) = Pay attention                           │
├─────────────────────────────────────────────────────────────────┤
│ PRE-SQUEEZE PATTERNS:                                           │
│ • Coiling price + building options volume                       │
│ • Unusual activity cluster at nearby strikes                    │
│ • Large position close = Release imminent                       │
│ • Afternoon gamma acceleration (2-3:30 PM)                      │
├─────────────────────────────────────────────────────────────────┤
│ KEY TIMES:                                                      │
│ • 10:00-10:30 AM: First setups emerge                          │
│ • 11:00-1:00 PM: Coiling/accumulation phase                    │
│ • 2:00-3:30 PM: Peak gamma, highest probability                │
│ • 3:45-4:00 PM: Expiration pin or final squeeze                │
└─────────────────────────────────────────────────────────────────┘
```

---

*This document is for educational purposes. Options trading involves substantial risk.*
