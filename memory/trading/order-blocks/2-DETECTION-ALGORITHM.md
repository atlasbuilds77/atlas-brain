# Order Block Detection Algorithm

## Overview
This algorithm identifies order blocks from OHLCV (Open, High, Low, Close, Volume) data without requiring visual chart analysis.

## Algorithm Flow

```
Input: OHLCV data (symbol, timeframe, lookback period)
Output: List of order blocks with coordinates and strength ratings

1. Data Preparation
   ├── Fetch historical price/volume data
   ├── Calculate indicators (ATR, volume average, price change %)
   └── Normalize data for analysis

2. Pattern Detection
   ├── Scan for impulse moves (strong directional moves)
   ├── Identify consolidation zones preceding impulses
   └── Flag potential order block candles

3. Validation
   ├── Verify volume spike criteria
   ├── Confirm follow-through (continuation)
   └── Check consolidation quality

4. Classification
   ├── Label as bullish or bearish order block
   ├── Calculate strength rating (1-10)
   └── Store zone coordinates (price range)

5. Filtering & Ranking
   ├── Remove overlapping/redundant zones
   ├── Apply time decay factor
   └── Sort by strength rating

6. Output
   └── Return structured list of order blocks
```

## Detailed Step-by-Step

### Step 1: Data Preparation

```python
# Required data points
- OHLCV data for lookback period (default: 100 candles minimum)
- Calculate 20-period simple moving average of volume
- Calculate 14-period ATR (Average True Range)
- Calculate price change percentage for each candle
```

### Step 2: Impulse Detection

An **impulse move** is a strong directional price movement that indicates institutional activity.

**Bullish Impulse Criteria:**
```
For each candle i:
  Check if next 1-4 candles show:
    - Price increase >= 2% (configurable threshold)
    - Close[i+n] > Close[i] for n in [1,2,3,4]
    - At least 1 candle with volume > 1.5x average
    - No major pullback (no candle drops >50% of gain)
  
  If true -> Bullish impulse detected
  Order block candidate = candle i (last bearish before impulse)
```

**Bearish Impulse Criteria:**
```
For each candle i:
  Check if next 1-4 candles show:
    - Price decrease >= 2%
    - Close[i+n] < Close[i] for n in [1,2,3,4]
    - At least 1 candle with volume > 1.5x average
    - No major bounce (no candle gains >50% of drop)
  
  If true -> Bearish impulse detected
  Order block candidate = candle i (last bullish before impulse)
```

### Step 3: Consolidation Verification

Check if price consolidated **before** the order block candle:

```
Consolidation window: 3-10 candles before order block candle

Check:
1. Average ATR in window < 0.8 * 14-period ATR
2. Price range (high-low) is relatively tight
3. No single candle with >2% move in consolidation window

If all true -> Consolidation confirmed
```

### Step 4: Volume Spike Validation

```
For the impulse move (1-4 candles after order block):

Calculate:
  max_volume_in_impulse = max(volume for candles in impulse)
  avg_volume_20 = 20-period volume average
  volume_ratio = max_volume_in_impulse / avg_volume_20

Classification:
  - volume_ratio >= 3.0: Volume score = 3
  - volume_ratio >= 2.0: Volume score = 2
  - volume_ratio >= 1.5: Volume score = 1
  - volume_ratio < 1.5: REJECT (not an order block)
```

### Step 5: Follow-Through Verification

```
Check candles immediately after impulse (next 2-3 candles):

Bullish order block:
  - Count how many of next 3 candles close higher
  - If 3/3: Follow-through score = 2
  - If 2/3: Follow-through score = 1
  - If <2/3: Follow-through score = 0

Bearish order block:
  - Count how many of next 3 candles close lower
  - If 3/3: Follow-through score = 2
  - If 2/3: Follow-through score = 1
  - If <2/3: Follow-through score = 0
```

### Step 6: Strength Calculation

```python
def calculate_strength(order_block):
    strength = 0
    
    # Volume component (max 3 points)
    strength += order_block.volume_score
    
    # Impulse strength (max 3 points)
    price_change_pct = abs(order_block.impulse_change_percent)
    if price_change_pct >= 5.0:
        strength += 3
    elif price_change_pct >= 3.0:
        strength += 2
    elif price_change_pct >= 2.0:
        strength += 1
    
    # Consolidation quality (max 2 points)
    if order_block.has_tight_consolidation:
        strength += 2
    elif order_block.has_moderate_consolidation:
        strength += 1
    
    # Follow-through (max 2 points)
    strength += order_block.followthrough_score
    
    return min(strength, 10)  # Cap at 10
```

### Step 7: Zone Coordinate Definition

```python
# For bullish order block (last down candle before impulse):
zone_high = order_block_candle.high
zone_low = order_block_candle.low
zone_range = zone_high - zone_low

# Optional: Extend zone slightly for wick coverage
zone_high += zone_range * 0.1  # 10% extension
zone_low -= zone_range * 0.1

# For bearish order block (last up candle before impulse):
# Same logic applies
```

### Step 8: Time Decay Application

```python
def apply_time_decay(order_block, current_candle_index):
    age = current_candle_index - order_block.candle_index
    
    if age <= 5:
        decay_factor = 1.0  # Fresh
    elif age <= 20:
        decay_factor = 0.9  # Recent
    elif age <= 50:
        decay_factor = 0.7  # Moderate
    else:
        decay_factor = 0.5  # Old
    
    order_block.adjusted_strength = order_block.strength * decay_factor
    return order_block
```

### Step 9: Overlap Handling

```python
def remove_overlapping_zones(order_blocks):
    """
    If two order blocks overlap and are same type (both bullish/bearish),
    keep only the stronger one.
    """
    filtered = []
    
    for ob in sorted(order_blocks, key=lambda x: x.strength, reverse=True):
        overlaps = False
        for existing in filtered:
            if zones_overlap(ob, existing) and ob.type == existing.type:
                overlaps = True
                break
        
        if not overlaps:
            filtered.append(ob)
    
    return filtered

def zones_overlap(zone1, zone2):
    """Check if price ranges overlap"""
    return not (zone1.high < zone2.low or zone2.high < zone1.low)
```

## Algorithm Parameters (Configurable)

```python
PARAMS = {
    'lookback_candles': 100,           # How far back to scan
    'impulse_threshold_pct': 2.0,      # Minimum % move for impulse
    'volume_spike_min': 1.5,           # Minimum volume ratio
    'consolidation_window': 10,         # Candles to check before OB
    'consolidation_atr_factor': 0.8,   # ATR threshold for consolidation
    'followthrough_candles': 3,        # Candles to check after impulse
    'min_strength': 5,                 # Minimum strength to report
    'zone_extension_pct': 0.1,         # % to extend zone boundaries
    'max_order_blocks': 10,            # Max number to return
}
```

## Output Format

```json
{
  "symbol": "AAPL",
  "timeframe": "1h",
  "analyzed_at": "2025-01-15T10:30:00Z",
  "order_blocks": [
    {
      "type": "bearish",
      "zone_high": 185.50,
      "zone_low": 184.20,
      "strength": 9,
      "adjusted_strength": 8.1,
      "age_candles": 12,
      "timestamp": "2025-01-14T22:00:00Z",
      "volume_ratio": 2.8,
      "impulse_pct": -4.2,
      "notes": "Strong supply zone with high volume"
    },
    {
      "type": "bullish",
      "zone_high": 178.90,
      "zone_low": 177.50,
      "strength": 7,
      "adjusted_strength": 7.0,
      "age_candles": 3,
      "timestamp": "2025-01-15T07:00:00Z",
      "volume_ratio": 2.1,
      "impulse_pct": 3.5,
      "notes": "Fresh demand zone"
    }
  ]
}
```

## Edge Cases & Handling

1. **Insufficient data:** Return empty list with warning
2. **No order blocks found:** Return empty list (normal on ranging markets)
3. **Multiple impulses in quick succession:** Keep strongest, filter weaker overlaps
4. **Gaps in data:** Skip incomplete candles, note in output
5. **Low liquidity periods:** Adjust volume thresholds or flag as low-confidence

## Performance Considerations

- **Time complexity:** O(n*m) where n=candles, m=lookback window for each check
- **Optimization:** Use sliding windows, cache indicator calculations
- **Memory:** Store only essential data points, ~1KB per order block
- **Real-time:** Can run on each new candle close (latency <100ms for 100 candles)

## Validation & Backtesting

To validate the algorithm:
1. Run on historical data with known order blocks (manual identification)
2. Calculate precision/recall metrics
3. Adjust thresholds for optimal detection rate
4. Test across multiple symbols and timeframes
5. Verify strength ratings correlate with price respect (bounces/rejections)

## Next Steps

Implement this algorithm in Python (see `3-order-block-detector.py`)
