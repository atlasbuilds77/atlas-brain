# TITAN Session Level Scanner

Real-time monitoring of key session levels with automated option strike recommendations.

## Features

### 1. Pre-Market Level Puller (6:00 AM PST)
- Pulls QQQ and SPY 5-min data from Polygon API
- Calculates:
  - Pre-market High (4am-9:30am ET)
  - Pre-market Low (4am-9:30am ET)
  - Prior day High/Low
- Saves to `/tmp/titan_levels.json`

### 2. Real-Time Scanner (Every 1 minute)
- Monitors price vs session levels
- Alerts when price within 0.2% of a level
- Tracks touched levels (no re-alerts)

### 3. Option Strike Calculator
- Identifies next target level
- Calculates optimal OTM strike
- Pulls option chain from Tradier
- Returns: strike, bid/ask, delta, position size

### 4. Alert System
- Console alerts
- JSON persistence at `/tmp/titan_alerts.json`
- Format: {time, symbol, level_type, level_price, current_price, suggested_strike, direction}

## Usage

### Pull Session Levels (Run at 6:00 AM)
```bash
python3 session_scanner.py --pull-levels
```

### Display Current Levels
```bash
python3 session_scanner.py --show-levels
```

### Run Single Scan
```bash
python3 session_scanner.py --scan-once
```

### Run Continuous Scanner
```bash
python3 session_scanner.py --continuous --interval 60
```

### Run with PM2 (Automated)
```bash
# Start all TITAN services
pm2 start ecosystem.config.js

# View logs
pm2 logs titan-session-scanner

# Stop scanner
pm2 stop titan-session-scanner
```

## PM2 Configuration

The scanner is configured to run automatically during market hours:
- **titan-level-puller**: Runs at 6:00 AM PST (weekdays only)
- **titan-session-scanner**: Starts at 6:30 AM PST, runs until 1:00 PM PST

## Output Format

```
=== TITAN LEVELS - Feb 14, 2026 ===
QQQ:
  Current:    $600.65
  Pre-High:   $602.28 @ 08:30
  Pre-Low:    $597.42 @ 08:15
  Prior High: $615.81 (2026-02-12)
  Prior Low:  $599.57 (2026-02-12)

SPY:
  Current:    $681.75
  Pre-High:   $683.00 @ 08:30
  Pre-Low:    $678.57 @ 06:30
  Prior High: $695.35 (2026-02-12)
  Prior Low:  $680.37 (2026-02-12)

=== ALERT ===
10:15:32 | QQQ approaching Pre-Low ($597.42) | Current: $597.65
Suggested: Buy QQQ $600 Call | Target: $602.28 | Stop: Below $596.50
  Option Details:
    Strike: $600.0
    Bid/Ask: $3.86 / $3.90
    Delta: 0.4974
    Expiration: 2026-02-17
```

## Files

- `session_scanner.py` - Main scanner application
- `levels.py` - Level calculation logic (Polygon API integration)
- `alerts.py` - Alert management and option strike calculator (Tradier API)
- `ecosystem.config.js` - PM2 configuration

## API Credentials

- **Polygon API**: `h7J74V1cd8_4NQpTxwQpudpqXWaIHMhv`
- **Tradier API**: `jj8L3RuSVG5MUwUpz2XHrjXjAFrq`

## Data Files

- `/tmp/titan_levels.json` - Current session levels
- `/tmp/titan_alerts.json` - Alert history and touched levels

## Troubleshooting

### No levels found
Run the level puller first:
```bash
python3 session_scanner.py --pull-levels
```

### Outside market hours
Scanner automatically pauses when outside 6:30 AM - 1:00 PM PST (weekdays).

### Option chain errors
Verify Tradier API token is valid and account has options data access.

## Market Hours

- **Pre-market**: 4:00 AM - 9:30 AM ET (1:00 AM - 6:30 AM PST)
- **Regular hours**: 9:30 AM - 4:00 PM ET (6:30 AM - 1:00 PM PST)
- **Scanner active**: 6:30 AM - 1:00 PM PST (weekdays only)
