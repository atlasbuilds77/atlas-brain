# Order Block Detector - Quick Reference

## Installation (One-Time)

```bash
cd /Users/atlasbuilds/clawd/memory/trading/order-blocks/scripts
pip install -r requirements.txt

# Set Alpaca credentials
export ALPACA_API_KEY='your_key'
export ALPACA_API_SECRET='your_secret'
```

---

## Usage Commands

### 1. Demo (No API Required)
```bash
python example_usage.py
```

### 2. Live Detection
```bash
python order_block_detector.py --symbol AAPL --timeframe 1Hour --days 30
```

### 3. Pre-Trade Safety Check
```bash
python pre_trade_check.py --symbol AAPL --direction long --entry 150.50
```

### 4. Save Results to File
```bash
python order_block_detector.py --symbol AAPL --timeframe 1Hour --days 30 --output results.json
```

---

## Common Timeframes

| Style | Timeframe | Days |
|-------|-----------|------|
| Scalping | 1Min, 5Min | 3-7 |
| Day Trading | 15Min, 1Hour | 7-14 |
| Swing Trading | 1Hour, 4Hour | 30-60 |
| Position | 1Day | 90-180 |

---

## Reading the Output

### Bullish Order Block (🟢 Demand Zone)
- Acts as **SUPPORT**
- Price often **bounces up** when it touches this zone
- **Safe for long entries** when price approaches
- **Dangerous for shorts** - avoid shorting into bullish blocks

### Bearish Order Block (🔴 Supply Zone)
- Acts as **RESISTANCE**
- Price often **reverses down** when it touches this zone
- **Safe for short entries** when price approaches
- **Dangerous for longs** - avoid buying into bearish blocks

### Strength Rating (X/10)
- **8-10:** Very strong, rarely broken
- **6-7:** Strong, respect it
- **4-5:** Moderate, watch for breaks
- **1-3:** Weak, may not hold

---

## The Golden Rules

### ❌ NEVER DO THIS (The Carlos Mistake)
```
Current Price: $150
Bearish Block: $149-$151 (strength 9/10)

❌ Going LONG here = Swimming against institutional current
Result: Likely to get stopped out
```

### ✅ CORRECT APPROACH
**Option A: Wait for the Break**
```
Bearish Block: $149-$151
Current Price: $150
Wait for price to close ABOVE $151, then enter long
```

**Option B: Trade WITH the Block**
```
Bearish Block: $149-$151 (resistance)
Current Price: $152 (above the block)
Enter SHORT here - the block acts as resistance
```

**Option C: Use as Support/Resistance**
```
Bullish Block: $148-$149 (support)
Current Price: $150
Wait for price to come down to $149, then enter long
```

---

## Pre-Trade Checklist

Before EVERY trade:

1. **Run the detector**
   ```bash
   python pre_trade_check.py --symbol AAPL --direction long --entry 150.50
   ```

2. **Check the output**
   - ✅ Approved = Safe to proceed
   - ❌ Rejected = DO NOT ENTER

3. **Review warnings**
   - 🚨 CRITICAL = Stop immediately
   - ⚠️ WARNING = Proceed with caution
   - ✅ SUPPORT/RESISTANCE = Favorable zone
   - ℹ️ INFO = No conflicts detected

4. **Make decision**
   - If rejected, wait or find different entry
   - If warnings, reduce position size
   - If approved, proceed with trade

---

## Integration Snippets

### JavaScript (for atlas-trader)
```javascript
const { execSync } = require('child_process');

function checkTradeSafety(symbol, direction, entryPrice) {
  try {
    execSync(
      `python pre_trade_check.py --symbol ${symbol} --direction ${direction} --entry ${entryPrice}`,
      { stdio: 'inherit' }
    );
    return true; // Approved
  } catch (error) {
    return false; // Rejected
  }
}

// Before entering trade
if (!checkTradeSafety('AAPL', 'long', 150.50)) {
  console.log('❌ Trade blocked by order block detector');
  return;
}
```

### Python
```python
from pre_trade_check import pre_trade_check

# Before trade
approved, warnings, blocks = pre_trade_check('AAPL', 'long', 150.50)

if not approved:
    print('❌ Trade rejected')
    for w in warnings:
        print(f'  {w}')
    return

print('✅ Trade approved')
```

---

## Troubleshooting

### "No blocks detected"
- Increase --days parameter
- Check if symbol has enough volume
- Verify timeframe is appropriate

### "API error"
- Check Alpaca credentials
- Verify API key permissions
- Check rate limits

### "Too many blocks"
- Use filter_relevant_blocks() to get nearby zones
- Focus on strength >= 7
- Reduce lookback period

---

## File Locations

- **Main detector:** `/Users/atlasbuilds/clawd/memory/trading/order-blocks/scripts/order_block_detector.py`
- **Pre-trade check:** `/Users/atlasbuilds/clawd/memory/trading/order-blocks/scripts/pre_trade_check.py`
- **Example usage:** `/Users/atlasbuilds/clawd/memory/trading/order-blocks/scripts/example_usage.py`
- **Theory docs:** `/Users/atlasbuilds/clawd/memory/trading/order-blocks/docs/ORDER_BLOCK_THEORY.md`
- **Integration:** `/Users/atlasbuilds/clawd/memory/trading/order-blocks/docs/INTEGRATION_GUIDE.md`

---

## Quick Theory Recap

**Order Block:** A price zone where institutional traders accumulated or distributed large positions

**Why They Matter:** Institutions know these zones and use them as support/resistance. Retail traders who ignore them get stopped out.

**The Key Insight:** Don't fight institutional order flow. Trade WITH the blocks, not AGAINST them.

**The Carlos Lesson:** Never enter long inside or below an unbroken bearish order block. That's exactly what cost him his capital.

---

## Support

- **Theory questions:** Read `docs/ORDER_BLOCK_THEORY.md`
- **Integration help:** See `docs/INTEGRATION_GUIDE.md`
- **Code issues:** Check script comments and error messages

---

*Keep this file handy for quick reference during trading sessions*
