# Order Block Detection System

**Created:** 2026-01-28 12:28 PST
**Status:** ACTIVE

---

## PURPOSE

Automatically detect and track order blocks (supply/demand zones) for trading decisions.

**Critical rule:** NEVER trade against order blocks
- Bullish blocks = support (wait for break before puts)
- Bearish blocks = resistance (wait for break before calls)

---

## COMPONENTS

### 1. Order Block Detector
**Location:** `atlas-trader/order-block-detector.js`

**What it does:**
- Analyzes price bars (5-min timeframe)
- Identifies bullish order blocks (last red candle before strong green move)
- Identifies bearish order blocks (last green candle before strong red move)
- Saves top 5 most significant blocks per symbol

**Criteria for detection:**
- Strong move = 3+ consecutive candles same direction
- Volume spike (>1.5x average)
- Significant price movement (>0.5%)

**Output:** `memory/trading/order-blocks/[SYMBOL]-latest.json`

**Usage:**
```bash
cd ~/clawd/atlas-trader
node order-block-detector.js SPY QQQ IWM
```

### 2. Update Daemon
**Location:** `memory/trading/order-block-update-daemon.sh`

**What it does:**
- Runs every 15 minutes during market hours
- Updates order blocks for watchlist: SPY, QQQ, IWM, TSLA, NVDA, AAPL
- Logs to `/tmp/order-block-update.log`

**Auto-starts:** Via `auto-start-trading-daemons.sh` at 6:25 AM daily

### 3. Integration with Scanner
**Location:** `memory/trading/setup-scanner-daemon.js`

**Uses order blocks to:**
- Filter out setups that would trade against blocks
- Increase conviction when setup aligns with blocks
- Identify bounces off support/resistance

---

## ORDER BLOCK FORMAT

```json
{
  "symbol": "SPY",
  "timestamp": "2026-01-28T20:28:00.000Z",
  "bullish": [
    {
      "price": 695.50,
      "timestamp": "2026-01-28T18:45:00.000Z",
      "strength": 1.2,
      "volume": 1250000,
      "type": "demand",
      "range": {
        "low": 695.50,
        "high": 696.20
      }
    }
  ],
  "bearish": [
    {
      "price": 698.80,
      "timestamp": "2026-01-28T19:15:00.000Z",
      "strength": 0.8,
      "volume": 980000,
      "type": "supply",
      "range": {
        "low": 698.20,
        "high": 698.80
      }
    }
  ],
  "summary": {
    "bullishCount": 5,
    "bearishCount": 3,
    "nearestBullish": {...},
    "nearestBearish": {...}
  }
}
```

---

## TRADING RULES

### When to respect blocks:

**Bullish block (support):**
- ✅ Buy calls when price bounces OFF block
- ❌ Don't buy puts UNTIL price breaks BELOW block

**Bearish block (resistance):**
- ✅ Buy puts when price rejects OFF block
- ❌ Don't buy calls UNTIL price breaks ABOVE block

### Break confirmation:
- Price closes beyond block on 5-min chart
- Volume spike confirms break
- Wait for retest (optional but safer)

---

## MONITORING

**Check order blocks before any trade:**
```bash
cat ~/clawd/memory/trading/order-blocks/SPY-latest.json
```

**Daemon status:**
```bash
ps aux | grep order-block
tail -f /tmp/order-block-update.log
```

**Manual update:**
```bash
cd ~/clawd/atlas-trader
node order-block-detector.js SPY
```

---

## MAINTENANCE

**Files:**
- Order blocks: `memory/trading/order-blocks/*.json`
- Detector: `atlas-trader/order-block-detector.js`
- Daemon: `memory/trading/order-block-update-daemon.sh`
- Logs: `/tmp/order-block-update.log`

**Update frequency:** 15 minutes (during market hours)

**Retention:** Latest blocks only (overwrites on each update)

---

## INTEGRATION STATUS

- ✅ Detector built and tested
- ✅ Auto-update daemon configured
- ✅ Auto-start at market open
- ⏳ Scanner integration (next step)
- ⏳ Alert system when price approaches blocks

---

**This system ensures we never trade against institutional supply/demand zones.**

---

Last updated: 2026-01-28 12:28 PST
