# Order Block Quick Reference Card

## What Are Order Blocks?

**Bullish Order Block (Demand Zone)** 🟢
- Last DOWN candle before strong UP move
- Acts as SUPPORT when price returns
- Safe to enter LONG when price reaches it

**Bearish Order Block (Supply Zone)** 🔴
- Last UP candle before strong DOWN move
- Acts as RESISTANCE when price returns
- Safe to enter SHORT when price reaches it

---

## The Golden Rule

### ❌ NEVER ENTER AGAINST A STRONG ORDER BLOCK
- **DON'T** enter LONG at bearish block (supply zone)
- **DON'T** enter SHORT at bullish block (demand zone)
- **Carlos's Mistake:** Ignored this → Lost capital

### ✅ ALWAYS CHECK BEFORE ENTERING
```bash
python order_block_detector.py SYMBOL --timeframe 1h
```

---

## Strength Ratings

| Rating | Meaning | Action |
|--------|---------|--------|
| **8-10** | High probability institutional zone | **MUST RESPECT** - Don't fight it |
| **6-7** | Moderate strength | Monitor closely |
| **4-5** | Weak zone | Use with other confirmation |
| **<4** | Unreliable | Can ignore |

---

## Quick Commands

```bash
# Basic detection
python order_block_detector.py AAPL

# Different timeframe
python order_block_detector.py TSLA --timeframe 4h

# Crypto
python order_block_detector.py BTC/USD --asset-type crypto

# High-strength only
python order_block_detector.py SPY --min-strength 8

# Save to file
python order_block_detector.py NVDA --output nvda.json
```

---

## Pre-Trade Checklist

Before EVERY trade:

1. ✅ Run order block detector for symbol
2. ✅ Check current price vs detected zones
3. ✅ Verify entry doesn't conflict with strength 7+ block
4. ✅ If conflict: REJECT TRADE or wait for breakout
5. ✅ Place stop beyond nearest order block (not inside)

---

## Node.js Integration (atlas-trader)

```javascript
const { OrderBlockValidator } = require('./orderBlockValidator');
const validator = new OrderBlockValidator({ minStrength: 7 });

// Before entering trade
const validation = await validator.validateTrade(symbol, direction, price);

if (!validation.safe) {
  console.error('🚫 BLOCKED:', validation.reason);
  return; // Don't enter trade
}

// Proceed with trade...
```

---

## Python Integration

```python
from order_block_detector import OrderBlockDetector

detector = OrderBlockDetector()

def check_before_trade(symbol, direction, current_price):
    result = detector.detect(symbol, '1h')
    
    for ob in result['order_blocks']:
        in_zone = ob['zone_low'] <= current_price <= ob['zone_high']
        
        # Block dangerous entries
        if direction == 'long' and ob['type'] == 'bearish' and in_zone:
            if ob['adjusted_strength'] >= 7:
                return False, "BLOCKED: Long at bearish block"
        
        if direction == 'short' and ob['type'] == 'bullish' and in_zone:
            if ob['adjusted_strength'] >= 7:
                return False, "BLOCKED: Short at bullish block"
    
    return True, "Safe to enter"
```

---

## Detection Criteria

Order block = Candle meeting ALL of:
- ✅ Strong impulse after (>=2% move)
- ✅ High volume (>=1.5x average)
- ✅ Consolidation before
- ✅ Follow-through continuation

**Strength Score:**
- Volume spike: 0-3 points
- Impulse strength: 0-3 points
- Consolidation: 0-2 points
- Follow-through: 0-2 points
- **Total: 0-10 points**

---

## Common Scenarios

### Scenario 1: Entry at Order Block
**Current:** Long at $185, Bearish block at $184-186 (strength: 8)
**Action:** 🚫 **REJECT** - You're in a supply zone

### Scenario 2: Entry Near Order Block
**Current:** Long at $183, Bearish block at $186-188 (strength: 9)
**Action:** ✅ **APPROVE** - But watch for rejection at $186

### Scenario 3: Breakout Trade
**Current:** Long at $189, Bearish block at $184-186 (strength: 8)
**Action:** ✅ **APPROVE** - Block broken, now support

### Scenario 4: Multiple Blocks
**Current:** Short at $175, Bullish at $172-174 (8), Bearish at $178-180 (9)
**Action:** ✅ **APPROVE** - Setup between blocks (OK)

---

## Stop Loss Placement

### ❌ WRONG: Stop inside order block
```
Entry: $100 (long)
Bullish block: $95-97
Stop: $96 ← BAD (inside block)
```

### ✅ RIGHT: Stop beyond order block
```
Entry: $100 (long)
Bullish block: $95-97
Stop: $94 ← GOOD (below block + buffer)
```

---

## Target Setting

Use opposing order blocks as targets:

**Long Trade:**
- Entry: $180
- Target: Just before nearest bearish block above
- If bearish block at $195-197, target $194

**Short Trade:**
- Entry: $200
- Target: Just before nearest bullish block below
- If bullish block at $185-187, target $188

---

## Timeframe Guide

| Timeframe | Use Case | Strength |
|-----------|----------|----------|
| **1d** | Major institutional zones | Strongest |
| **4h** | Swing trade levels | Strong |
| **1h** | Day trade zones | Moderate |
| **15m** | Scalp levels | Weakest |

**Rule:** Higher timeframe blocks override lower timeframe

---

## Time Decay

Order blocks lose strength over time:
- **0-5 candles:** Full strength (100%)
- **5-20 candles:** Recent (90%)
- **20-50 candles:** Moderate (70%)
- **50+ candles:** Old (50%)

**Fresh blocks are most dangerous!**

---

## API Setup (One-Time)

```bash
# Install
pip install -r requirements.txt

# Configure
export ALPACA_API_KEY="your_key"
export ALPACA_API_SECRET="your_secret"

# Add to shell profile to persist
echo 'export ALPACA_API_KEY="your_key"' >> ~/.zshrc
source ~/.zshrc

# Test
python test_detector.py
```

---

## Daily Routine

**Morning (Before Market Open):**
```bash
# Check watchlist
python order_block_detector.py AAPL --timeframe 1d
python order_block_detector.py SPY --timeframe 1d
python order_block_detector.py TSLA --timeframe 1d
```

**Before Each Trade:**
```bash
python order_block_detector.py SYMBOL --timeframe 1h
```

**Review fresh blocks (age <= 5, strength >= 8):**
These are the most important to respect!

---

## Warning Signs

### 🚨 HIGH RISK - Don't Trade
- Entry price inside 8-10 strength order block
- Direction conflicts with block type
- Multiple strong blocks nearby

### ⚠️ MODERATE RISK - Use Caution
- Entry within 2% of strong order block
- 6-7 strength block in play
- Old block (50+ candles) but still relevant

### ✅ LOW RISK - Proceed
- No conflicting order blocks
- Entry between blocks
- Breakout confirmed above/below block

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No blocks detected | Normal for ranging market / Try longer TF |
| API error | Check credentials, internet connection |
| Import error | `pip install -r requirements.txt` |
| Blocks don't match chart | Adjust parameters / Check timeframe |

---

## Files Location

```
/Users/atlasbuilds/clawd/memory/trading/order-blocks/
├── order_block_detector.py    # Main script
├── orderBlockValidator.js     # Node.js wrapper
├── test_detector.py           # Test suite
└── *.md                       # Documentation
```

---

## Remember

1. **Order blocks = institutional footprints**
2. **Strength 8+ = must respect**
3. **Never trade INTO strong block**
4. **Check BEFORE every trade**
5. **Carlos lost money ignoring this**

---

## Support

- **Theory:** See `1-ORDER-BLOCK-THEORY.md`
- **Technical:** See `2-DETECTION-ALGORITHM.md`
- **Integration:** See `4-INTEGRATION-GUIDE.md`
- **Overview:** See `README.md`

---

**Print this card and keep it visible while trading!**
