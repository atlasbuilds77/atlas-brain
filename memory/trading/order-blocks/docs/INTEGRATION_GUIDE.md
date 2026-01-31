# Order Block Detector - Integration Guide

## Quick Start

### Installation

```bash
cd /Users/atlasbuilds/clawd/memory/trading/order-blocks/scripts
pip install -r requirements.txt
```

### Basic Usage

```bash
# Set Alpaca API credentials
export ALPACA_API_KEY='your_key_here'
export ALPACA_API_SECRET='your_secret_here'

# Run detection
python order_block_detector.py --symbol AAPL --timeframe 1Hour --days 30
```

---

## Integration with atlas-trader

### Method 1: Command Line Integration

Call the detector before any trade entry:

```javascript
// In your atlas-trader code
const { execSync } = require('child_process');

function detectOrderBlocks(symbol, timeframe = '1Hour') {
  const cmd = `python3 /Users/atlasbuilds/clawd/memory/trading/order-blocks/scripts/order_block_detector.py \
    --symbol ${symbol} \
    --timeframe ${timeframe} \
    --days 30 \
    --output /tmp/order_blocks_${symbol}.json`;
  
  execSync(cmd);
  
  const results = JSON.parse(
    fs.readFileSync(`/tmp/order_blocks_${symbol}.json`, 'utf8')
  );
  
  return results;
}

// Before entering a trade
const blocks = detectOrderBlocks('AAPL');
console.log('Bullish blocks:', blocks.bullish_blocks);
console.log('Bearish blocks:', blocks.bearish_blocks);

// Check if current price is near a dangerous zone
const currentPrice = getCurrentPrice('AAPL');
const nearBearishBlock = blocks.bearish_blocks.some(block => 
  currentPrice >= block.start_price && currentPrice <= block.end_price
);

if (nearBearishBlock) {
  console.log('⚠️ WARNING: Price is inside a bearish order block!');
  console.log('Do NOT go long here - wait for break or reversal');
}
```

### Method 2: Python Module Import

Create a wrapper script for your trading bot:

```python
# trading_bot.py
import sys
sys.path.append('/Users/atlasbuilds/clawd/memory/trading/order-blocks/scripts')

from order_block_detector import OrderBlockDetector
import pandas as pd

# Your trading logic
detector = OrderBlockDetector()

# Get your price data
df = get_price_data('AAPL', timeframe='1Hour')

# Detect blocks
blocks = detector.detect_order_blocks(df)

# Check before entry
def is_safe_to_enter_long(current_price, blocks):
    """Check if it's safe to enter a long position"""
    bearish_blocks = [b for b in blocks if b.type == 'bearish' and not b.broken]
    
    for block in bearish_blocks:
        # Is current price inside or just below a bearish block?
        if current_price >= block.start_price and current_price <= block.end_price:
            return False, f"Price inside bearish block {block.start_price:.2f}-{block.end_price:.2f}"
        
        # Is current price just below a strong bearish block?
        if current_price < block.start_price and (block.start_price - current_price) / current_price < 0.02:
            if block.strength >= 7:
                return False, f"Price too close to strong bearish block (strength {block.strength})"
    
    return True, "No bearish blocks detected above"

# Usage
safe, reason = is_safe_to_enter_long(150.50, blocks)
if not safe:
    print(f"❌ DO NOT ENTER: {reason}")
else:
    print(f"✅ Safe to consider long: {reason}")
```

---

## Output Format

### Console Output
```
================================================================================
ORDER BLOCK DETECTION RESULTS
================================================================================

Current Price: $150.25

🟢 BULLISH ORDER BLOCKS (Demand Zones - Support)
--------------------------------------------------------------------------------
1. $148.20 - $149.10
   Strength: 8.5/10 | Volume: 2.3x | Move: 3.2% | Tests: 0 | Broken: No
   Formed: 2024-01-15 14:30

2. $145.80 - $146.50
   Strength: 7.2/10 | Volume: 1.8x | Move: 2.8% | Tests: 1 | Broken: No
   Formed: 2024-01-12 10:15

🔴 BEARISH ORDER BLOCKS (Supply Zones - Resistance)
--------------------------------------------------------------------------------
1. $152.50 - $153.20
   Strength: 9.1/10 | Volume: 2.8x | Move: 4.5% | Tests: 0 | Broken: No
   Formed: 2024-01-16 11:00

⚠️  TRADING RULES:
  1. DO NOT enter against an unbroken order block
  2. Wait for price to BREAK and CLOSE beyond the zone
  3. Use blocks as support/resistance for entries WITH the zone
  4. Higher strength = more reliable zone
================================================================================
```

### JSON Output (--output flag)
```json
{
  "symbol": "AAPL",
  "timeframe": "1Hour",
  "current_price": 150.25,
  "timestamp": "2024-01-17T15:30:00",
  "bullish_blocks": [
    {
      "type": "bullish",
      "price_range": "$148.20 - $149.10",
      "start_price": 148.20,
      "end_price": 149.10,
      "mid_price": 148.65,
      "timestamp": "2024-01-15T14:30:00",
      "volume_ratio": 2.3,
      "price_move_pct": 3.2,
      "strength": 8.5,
      "tests": 0,
      "broken": false
    }
  ],
  "bearish_blocks": [
    {
      "type": "bearish",
      "price_range": "$152.50 - $153.20",
      "start_price": 152.50,
      "end_price": 153.20,
      "mid_price": 152.85,
      "timestamp": "2024-01-16T11:00:00",
      "volume_ratio": 2.8,
      "price_move_pct": 4.5,
      "strength": 9.1,
      "tests": 0,
      "broken": false
    }
  ]
}
```

---

## Trading Workflow Integration

### Pre-Trade Checklist

```python
def pre_trade_checklist(symbol, direction, entry_price):
    """
    Run before EVERY trade
    
    Args:
        symbol: Trading symbol
        direction: 'long' or 'short'
        entry_price: Proposed entry price
    
    Returns:
        (approved: bool, warnings: list)
    """
    # Detect order blocks
    blocks = detect_order_blocks(symbol)
    warnings = []
    approved = True
    
    if direction == 'long':
        # Check for bearish blocks above
        for block in blocks['bearish_blocks']:
            if not block['broken']:
                # Is entry price inside the block?
                if entry_price >= block['start_price'] and entry_price <= block['end_price']:
                    warnings.append(f"CRITICAL: Entry is INSIDE bearish block ${block['price_range']}")
                    approved = False
                
                # Is entry price just below a strong block?
                elif entry_price < block['start_price']:
                    distance_pct = ((block['start_price'] - entry_price) / entry_price) * 100
                    if distance_pct < 2 and block['strength'] >= 7:
                        warnings.append(f"WARNING: Strong resistance {distance_pct:.1f}% above at ${block['price_range']}")
    
    elif direction == 'short':
        # Check for bullish blocks below
        for block in blocks['bullish_blocks']:
            if not block['broken']:
                # Is entry price inside the block?
                if entry_price >= block['start_price'] and entry_price <= block['end_price']:
                    warnings.append(f"CRITICAL: Entry is INSIDE bullish block ${block['price_range']}")
                    approved = False
                
                # Is entry price just above a strong block?
                elif entry_price > block['end_price']:
                    distance_pct = ((entry_price - block['end_price']) / entry_price) * 100
                    if distance_pct < 2 and block['strength'] >= 7:
                        warnings.append(f"WARNING: Strong support {distance_pct:.1f}% below at ${block['price_range']}")
    
    return approved, warnings

# Example usage
approved, warnings = pre_trade_checklist('AAPL', 'long', 150.50)

if not approved:
    print("❌ TRADE REJECTED")
    for w in warnings:
        print(f"   {w}")
    exit(1)

if warnings:
    print("⚠️ TRADE WARNINGS:")
    for w in warnings:
        print(f"   {w}")
    confirm = input("Continue anyway? (yes/no): ")
    if confirm.lower() != 'yes':
        exit(1)

print("✅ TRADE APPROVED - No order block conflicts")
```

---

## Configuration Options

### Detector Parameters

```python
detector = OrderBlockDetector(
    min_volume_ratio=1.5,    # Minimum volume vs average (1.5x default)
    min_price_move=2.0,      # Minimum price move % to consider (2% default)
    lookback_candles=5       # Candles to confirm breakout (5 default)
)
```

**Adjust for different trading styles:**

- **Day Trading:** `min_price_move=1.0`, `lookback_candles=3`
- **Swing Trading:** `min_price_move=2.0`, `lookback_candles=5` (default)
- **Position Trading:** `min_price_move=3.0`, `lookback_candles=10`

### Timeframe Selection

| Trading Style | Recommended Timeframe | Lookback Days |
|--------------|----------------------|---------------|
| Scalping | 1Min, 5Min | 3-7 days |
| Day Trading | 15Min, 1Hour | 7-14 days |
| Swing Trading | 1Hour, 4Hour | 30-60 days |
| Position Trading | 1Day | 90-180 days |

---

## Testing

Run the detector on historical data to verify:

```bash
# Test on AAPL
python order_block_detector.py --symbol AAPL --timeframe 1Hour --days 30

# Test on crypto (if supported)
python order_block_detector.py --symbol BTC/USD --timeframe 1Hour --days 30

# Save results for analysis
python order_block_detector.py --symbol AAPL --timeframe 1Hour --days 30 \
  --output test_results.json
```

---

## Troubleshooting

### Common Issues

**1. No blocks detected**
- Increase lookback days (--days)
- Lower min_volume_ratio threshold
- Check if symbol has sufficient volume
- Verify data quality

**2. Too many blocks detected**
- Increase min_volume_ratio (more selective)
- Increase min_price_move (only strong moves)
- Filter by strength (only use 7+ strength blocks)

**3. API errors**
- Verify Alpaca credentials
- Check API rate limits
- Ensure symbol is valid and traded

---

## Safety Rules (The Carlos Protocol)

**NEVER:**
1. ❌ Enter long inside/below an unbroken bearish order block
2. ❌ Enter short inside/above an unbroken bullish order block
3. ❌ Ignore high-strength blocks (8+/10)
4. ❌ Trade against institutional flow

**ALWAYS:**
1. ✅ Run detector before EVERY trade
2. ✅ Wait for block breaks before entering against them
3. ✅ Use blocks as support/resistance for entries
4. ✅ Respect high-volume, high-strength zones
5. ✅ Combine with other indicators (trend, momentum)

---

## Next Steps

1. **Test the detector** on historical data
2. **Integrate into atlas-trader** using Method 1 or 2
3. **Backtest** your strategy with order block awareness
4. **Monitor live** - run detector before each trade
5. **Refine parameters** based on your trading style

---

## Support & Updates

- Documentation: `/Users/atlasbuilds/clawd/memory/trading/order-blocks/docs/`
- Script location: `/Users/atlasbuilds/clawd/memory/trading/order-blocks/scripts/`
- Issues: Document in trading journal

**Remember:** This system is designed to prevent the mistake that cost Carlos his capital. Use it religiously.

---

*Integration guide for atlas-trader system*
*Priority: Prevent capital loss from order block ignorance*
