# Trading Automation Daemons

Three background daemons that continuously monitor the market for trading opportunities during market hours (6:30 AM - 1:00 PM PST, Mon-Fri).

## Daemons

### 1. Setup Scanner (`setup-scanner.py`)
**Purpose**: Proactively hunt for high-quality trade setups  
**Scan Interval**: Every 5 minutes during market hours  
**Watchlist**: SPY, QQQ, AAPL, TSLA, NVDA, AMD, AMZN, GOOGL, META, MSFT

**Criteria for 9/10+ Setups:**
- Order block strength ≥ 8/10
- Order block age < 5 candles (fresh)
- Price within 2% of order block zone
- Uses actual order block detector (`order_block_detector.py`)

**Alerts**: Sends iMessage to group id:10 when strong setup found  
**Logs**: `memory/trading/setup-scanner-log.jsonl`

### 2. Level Watcher (`level-watcher.py`)
**Purpose**: Monitor price levels and alert when crossed  
**Check Interval**: Every 60 seconds during market hours  
**Configuration**: `memory/trading/watch-levels.json`

**Watch Levels Format:**
```json
[
  {
    "symbol": "SPY",
    "level": 580.00,
    "direction": "above",
    "note": "Key resistance breakout",
    "triggered": false
  },
  {
    "symbol": "TSLA",
    "level": 400.00,
    "direction": "below",
    "note": "Support breakdown watch",
    "triggered": false
  }
]
```

**Direction Options:**
- `"above"`: Alert when price crosses above level
- `"below"`: Alert when price crosses below level

**Alerts**: Sends iMessage to group id:10 when level crossed  
**Logs**: `memory/trading/level-alerts.jsonl`

### 3. Order Block Updater (`order-block-updater.py`)
**Purpose**: Keep order block data fresh for all symbols  
**Update Interval**: Every 15 minutes during market hours  
**Watchlist**: Same as Setup Scanner

**Features:**
- Updates order blocks for entire watchlist
- Caches results to `memory/trading/order-blocks/cache/[SYMBOL].json`
- Alerts ONLY when NEW strong block (≥8 strength) detected
- Silent background updates otherwise

**Alerts**: Sends iMessage to group id:10 for new strong blocks  
**Logs**: `memory/trading/order-block-updater-log.jsonl`

## Quick Start

### Start All Daemons
```bash
cd /Users/atlasbuilds/clawd/memory/trading/daemons
chmod +x *.sh
./start-all.sh
```

### Check Status
```bash
./status.sh
```

### Stop All Daemons
```bash
./stop-all.sh
```

## Requirements

### Environment Variables
Must be set before starting daemons:
```bash
export ALPACA_API_KEY="your_key"
export ALPACA_API_SECRET="your_secret"
```

### Python Dependencies
```bash
pip install alpaca-py pandas numpy
```

### iMessage Integration
- Uses `/Users/atlasbuilds/clawd/tools/imsg-enhanced.sh`
- Sends alerts to group `id:10`
- Ensure script is executable

## Logs

All daemons log to `/tmp/trading-daemons/`:
- `setup-scanner.log` - Setup scanner console output
- `level-watcher.log` - Level watcher console output
- `order-block-updater.log` - Order block updater console output

Structured logs (JSONL format):
- `memory/trading/setup-scanner-log.jsonl`
- `memory/trading/level-alerts.jsonl`
- `memory/trading/order-block-updater-log.jsonl`

## Market Hours

**Active**: Monday-Friday, 6:30 AM - 1:00 PM PST  
**Idle**: Weekends and outside market hours (daemons sleep)

Daemons automatically detect market hours and idle when market is closed.

## Graceful Shutdown

All daemons handle `SIGTERM` gracefully:
- Stop daemon with `./stop-all.sh`
- Or manually: `kill <pid>` (not `kill -9`)
- Daemons complete current task before exiting

## Auto-Restart on Crash

Daemons include basic error handling:
- Main loop wrapped in try/catch
- Sleep and retry on error
- Log errors to JSONL

For production auto-restart, use a process manager like `supervisord` or `systemd`.

## Manual Operation

### Start Individual Daemon
```bash
python3 setup-scanner.py &
python3 level-watcher.py &
python3 order-block-updater.py &
```

### Stop Individual Daemon
```bash
pkill -f setup-scanner.py
pkill -f level-watcher.py
pkill -f order-block-updater.py
```

## Adding Watch Levels

Edit `memory/trading/watch-levels.json`:
```json
[
  {
    "symbol": "NVDA",
    "level": 950.00,
    "direction": "above",
    "note": "All-time high breakout",
    "triggered": false
  }
]
```

Daemon picks up changes on next check cycle (no restart needed).

## Troubleshooting

### Daemon won't start
1. Check environment variables: `echo $ALPACA_API_KEY`
2. Check Python dependencies: `pip list | grep alpaca`
3. Check logs in `/tmp/trading-daemons/`

### No alerts received
1. Check iMessage script: `/Users/atlasbuilds/clawd/tools/imsg-enhanced.sh id:10 "test"`
2. Check daemon is running during market hours: `./status.sh`
3. Check structured logs for setup detections

### High CPU/Memory usage
- Daemons are lightweight (Python background processes)
- Typical memory: 50-100MB each
- CPU: <1% when idle, brief spikes during scans

## Integration with Order Block Detector

All daemons use the existing order block detector at:  
`/Users/atlasbuilds/clawd/memory/trading/order-blocks/order_block_detector.py`

No need to maintain separate detection logic - single source of truth.

## Next Steps

1. **Start daemons**: `./start-all.sh`
2. **Add watch levels**: Edit `watch-levels.json`
3. **Monitor**: Check logs and wait for alerts
4. **Refine**: Adjust criteria in daemon source if needed

## Architecture

```
Setup Scanner (5min) ──┐
                       ├──> Order Block Detector ──> Alpaca API
Level Watcher (60s) ───┤
                       │
OB Updater (15min) ────┘

All ──> iMessage Alerts (group id:10)
```

Simple, focused, automated trading intelligence.
