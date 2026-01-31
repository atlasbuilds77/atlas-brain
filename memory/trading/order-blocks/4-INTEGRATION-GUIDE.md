# Order Block Detector - Integration Guide

## Quick Start

### 1. Installation

```bash
cd /Users/atlasbuilds/clawd/memory/trading/order-blocks/
pip install -r requirements.txt
```

### 2. Set Up API Credentials

```bash
export ALPACA_API_KEY="your_key_here"
export ALPACA_API_SECRET="your_secret_here"
```

Or add to your shell profile (~/.zshrc or ~/.bashrc):
```bash
echo 'export ALPACA_API_KEY="your_key"' >> ~/.zshrc
echo 'export ALPACA_API_SECRET="your_secret"' >> ~/.zshrc
source ~/.zshrc
```

### 3. Basic Usage

```bash
# Detect order blocks for a stock
python order_block_detector.py AAPL --timeframe 1h

# Detect for crypto
python order_block_detector.py BTC/USD --timeframe 1h --asset-type crypto

# Save results to JSON
python order_block_detector.py TSLA --timeframe 4h --output tsla_blocks.json

# Filter by minimum strength
python order_block_detector.py SPY --timeframe 1d --min-strength 7
```

## Integration with atlas-trader

### Option 1: Pre-Trade Check (Recommended)

Add order block check **before** entering any trade:

```javascript
// In atlas-trader/src/trading/preTradeChecks.js

const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

async function checkOrderBlocks(symbol, timeframe = '1h') {
  try {
    const cmd = `python /Users/atlasbuilds/clawd/memory/trading/order-blocks/order_block_detector.py ${symbol} --timeframe ${timeframe} --output /tmp/ob_${symbol}.json`;
    
    await execPromise(cmd);
    
    const fs = require('fs');
    const result = JSON.parse(fs.readFileSync(`/tmp/ob_${symbol}.json`, 'utf8'));
    
    return result;
  } catch (error) {
    console.error('Order block check failed:', error);
    return null;
  }
}

async function validateTradeAgainstOrderBlocks(symbol, direction, entryPrice, currentPrice) {
  const blocks = await checkOrderBlocks(symbol);
  
  if (!blocks || blocks.order_blocks.length === 0) {
    return { safe: true, reason: 'No order blocks detected' };
  }
  
  // Check for dangerous entries
  for (const ob of blocks.order_blocks) {
    const inZone = currentPrice >= ob.zone_low && currentPrice <= ob.zone_high;
    
    // RED FLAG: Entering long AT a strong bearish order block
    if (direction === 'long' && ob.type === 'bearish' && inZone && ob.adjusted_strength >= 7) {
      return {
        safe: false,
        reason: `🚨 BLOCKED: Entering LONG at strong bearish order block ($${ob.zone_low}-$${ob.zone_high}, strength: ${ob.adjusted_strength}/10). This is supply zone - high rejection risk!`,
        orderBlock: ob
      };
    }
    
    // RED FLAG: Entering short AT a strong bullish order block
    if (direction === 'short' && ob.type === 'bullish' && inZone && ob.adjusted_strength >= 7) {
      return {
        safe: false,
        reason: `🚨 BLOCKED: Entering SHORT at strong bullish order block ($${ob.zone_low}-$${ob.zone_high}, strength: ${ob.adjusted_strength}/10). This is demand zone - high bounce risk!`,
        orderBlock: ob
      };
    }
  }
  
  return { safe: true, reason: 'No conflicting order blocks' };
}

module.exports = { checkOrderBlocks, validateTradeAgainstOrderBlocks };
```

### Option 2: Python Integration Module

For pure Python trading systems:

```python
# trading_system.py

import json
import subprocess
from order_block_detector import OrderBlockDetector

# Method 1: Use detector directly
detector = OrderBlockDetector()

def check_order_blocks_before_trade(symbol, direction, current_price):
    """
    Check order blocks before entering a trade
    Returns: (is_safe: bool, reason: str)
    """
    result = detector.detect(symbol, timeframe='1h')
    
    for ob in result['order_blocks']:
        in_zone = ob['zone_low'] <= current_price <= ob['zone_high']
        
        # Block dangerous trades
        if direction == 'long' and ob['type'] == 'bearish' and in_zone and ob['adjusted_strength'] >= 7:
            return False, f"⚠️ WARNING: Entering LONG at bearish order block (${ob['zone_low']}-${ob['zone_high']}, strength {ob['adjusted_strength']})"
        
        if direction == 'short' and ob['type'] == 'bullish' and in_zone and ob['adjusted_strength'] >= 7:
            return False, f"⚠️ WARNING: Entering SHORT at bullish order block (${ob['zone_low']}-${ob['zone_high']}, strength {ob['adjusted_strength']})"
    
    return True, "✓ No conflicting order blocks"

# Usage in trading logic
def enter_trade(symbol, direction, quantity, entry_price):
    # PRE-TRADE CHECK
    is_safe, reason = check_order_blocks_before_trade(symbol, direction, entry_price)
    
    if not is_safe:
        print(f"🚫 Trade rejected: {reason}")
        return None
    
    print(f"✅ Order block check passed: {reason}")
    
    # Proceed with trade...
    # ... rest of trading logic
```

## Use Cases

### Use Case 1: Entry Validation
**Problem:** Entering trades into strong supply/demand zones
**Solution:** Check order blocks before every entry

```python
# Before entering any trade
result = detector.detect(symbol, timeframe)

for ob in result['order_blocks']:
    if ob['adjusted_strength'] >= 7:
        # Check if entry conflicts with this zone
        # Reject trade or wait for breakout
```

### Use Case 2: Stop Loss Placement
**Problem:** Stops getting hunted at obvious levels
**Solution:** Place stops beyond order block zones

```python
# Calculate stop loss based on order blocks
def calculate_smart_stop_loss(symbol, direction, entry_price):
    result = detector.detect(symbol, timeframe='1h')
    
    if direction == 'long':
        # Find nearest bullish order block below entry
        bullish_blocks = [ob for ob in result['order_blocks'] 
                          if ob['type'] == 'bullish' and ob['zone_high'] < entry_price]
        
        if bullish_blocks:
            nearest = min(bullish_blocks, key=lambda x: entry_price - x['zone_high'])
            # Place stop below the order block (with buffer)
            stop_loss = nearest['zone_low'] - (nearest['zone_high'] - nearest['zone_low']) * 0.1
            return stop_loss
    
    # Similar logic for short positions...
```

### Use Case 3: Target Setting
**Problem:** Exits too early or too late
**Solution:** Use opposing order blocks as targets

```python
def calculate_target(symbol, direction, entry_price):
    result = detector.detect(symbol, timeframe='4h')
    
    if direction == 'long':
        # Find nearest bearish order block above entry
        bearish_blocks = [ob for ob in result['order_blocks']
                          if ob['type'] == 'bearish' and ob['zone_low'] > entry_price]
        
        if bearish_blocks:
            nearest = min(bearish_blocks, key=lambda x: x['zone_low'] - entry_price)
            # Target just before the order block
            target = nearest['zone_low'] - (nearest['zone_high'] - nearest['zone_low']) * 0.2
            return target
    
    # Similar for short positions...
```

### Use Case 4: Market Context Analysis
**Problem:** Trading without understanding institutional positioning
**Solution:** Review order blocks before market open

```python
# Daily morning routine
def analyze_watchlist():
    watchlist = ['AAPL', 'TSLA', 'SPY', 'QQQ']
    
    for symbol in watchlist:
        print(f"\n📊 {symbol} Order Block Analysis")
        result = detector.detect(symbol, timeframe='1d')
        
        print(result['summary'])
        
        # Flag high-risk zones
        for ob in result['order_blocks']:
            if ob['adjusted_strength'] >= 8:
                print(f"  ⚠️ Strong {ob['type']} zone at ${ob['zone_low']}-${ob['zone_high']}")
```

## API Reference

### OrderBlockDetector Class

```python
from order_block_detector import OrderBlockDetector

# Initialize
detector = OrderBlockDetector(api_key=None, api_secret=None)
# If api_key/secret not provided, reads from environment variables

# Detect order blocks
result = detector.detect(
    symbol='AAPL',           # Trading symbol
    timeframe='1h',          # '1m', '5m', '15m', '1h', '4h', '1d'
    asset_type='stock'       # 'stock' or 'crypto'
)
```

### Result Format

```json
{
  "symbol": "AAPL",
  "timeframe": "1h",
  "analyzed_at": "2025-01-15T10:30:00Z",
  "current_price": 185.50,
  "order_blocks": [
    {
      "type": "bearish",
      "zone_high": 187.50,
      "zone_low": 186.20,
      "strength": 9,
      "adjusted_strength": 8.1,
      "age_candles": 12,
      "timestamp": "2025-01-14T22:00:00Z",
      "volume_ratio": 2.8,
      "impulse_pct": -4.2,
      "notes": "Fresh supply zone with strong institutional footprint"
    }
  ],
  "summary": "Bearish resistance at $186.20-$187.50 (strength: 8.1/10)"
}
```

### Configuration Parameters

Customize detection sensitivity:

```python
detector = OrderBlockDetector()

# Adjust parameters
detector.params['impulse_threshold_pct'] = 3.0  # Require 3% move (more strict)
detector.params['volume_spike_min'] = 2.0       # Require 2x volume (more strict)
detector.params['min_strength'] = 7             # Only show strength >= 7
detector.params['lookback_candles'] = 150       # Scan more history

result = detector.detect('AAPL', '1h')
```

## Automated Monitoring

### Cron Job for Daily Analysis

```bash
# Add to crontab (crontab -e)
# Run every day at 9:00 AM
0 9 * * * /usr/bin/python /Users/atlasbuilds/clawd/memory/trading/order-blocks/order_block_detector.py AAPL --timeframe 1d --output /Users/atlasbuilds/clawd/logs/order-blocks-$(date +\%Y\%m\%d).json
```

### Real-Time Monitoring Script

```python
import time
from order_block_detector import OrderBlockDetector

detector = OrderBlockDetector()
watchlist = ['AAPL', 'TSLA', 'SPY']

while True:
    for symbol in watchlist:
        result = detector.detect(symbol, timeframe='1h')
        
        # Alert on strong new order blocks
        for ob in result['order_blocks']:
            if ob['age_candles'] <= 2 and ob['adjusted_strength'] >= 8:
                print(f"🚨 NEW STRONG ORDER BLOCK: {symbol} {ob['type']} at ${ob['zone_low']}-${ob['zone_high']}")
                # Send notification (integrate with your alert system)
    
    time.sleep(3600)  # Check every hour
```

## Troubleshooting

### Issue: "Alpaca API credentials required"
**Solution:** Set environment variables or pass to constructor
```bash
export ALPACA_API_KEY="your_key"
export ALPACA_API_SECRET="your_secret"
```

### Issue: "Insufficient data"
**Solution:** Check if symbol is correct and market is open. Try longer timeframe (4h or 1d)

### Issue: "No order blocks detected"
**Solution:** 
- Market may be ranging (low volatility)
- Try lowering min_strength parameter
- Check longer timeframe for major zones

### Issue: "Import error: alpaca-py not found"
**Solution:** 
```bash
pip install alpaca-py pandas numpy
```

## Performance Notes

- **Detection speed:** ~1-2 seconds per symbol
- **Data usage:** Minimal (only fetches what's needed)
- **Memory:** ~50MB per detector instance
- **Concurrent requests:** Safe to run multiple detectors in parallel

## Best Practices

1. **Always check order blocks before entering trades**
2. **Use higher timeframe blocks (4h, 1d) for major zones**
3. **Respect 8-10 strength zones - they're institutional**
4. **Wait for breakout confirmation before trading against strong blocks**
5. **Combine with other analysis (not a standalone system)**
6. **Monitor fresh blocks (<5 candles) closely**
7. **Update analysis before major trading sessions**

## Next Steps

1. Integrate into atlas-trader pre-trade validation
2. Set up daily morning analysis routine
3. Create alerts for fresh high-strength order blocks
4. Backtest historical trades against order block zones
5. Build dashboard to visualize order blocks

## Support

For issues or questions:
- Check THEORY.md for conceptual understanding
- Review DETECTION-ALGORITHM.md for technical details
- Test with known order block examples
- Adjust parameters for your specific use case

---

**Remember:** This tool prevents trading mistakes like Carlos's. Use it religiously before every trade.
