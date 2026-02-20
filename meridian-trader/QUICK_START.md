# TITAN Session Scanner - Quick Start

## 🏃 Quick Commands

```bash
# Navigate to directory
cd /Users/atlasbuilds/clawd/titan-trader

# Pull today's levels (run at 6am or anytime)
python3 titan_level_scanner.py --pull-levels

# Show current levels
python3 titan_level_scanner.py --show-levels

# Run one scan
python3 titan_level_scanner.py --scan-once

# Run continuous (Ctrl+C to stop)
python3 titan_level_scanner.py --continuous

# Start with PM2 (auto-restart, logging)
pm2 start ecosystem.config.js
pm2 logs titan-session-scanner
```

## 📊 What It Does

1. **6:00 AM PST**: Pulls pre-market levels (SPY, QQQ)
2. **6:30 AM - 1:00 PM**: Scans every minute
3. **When price approaches level** (within 0.2%):
   - Prints alert
   - Calculates optimal option strike
   - Shows entry, target, stop
   - Saves to `/tmp/titan_alerts.json`

## 🎯 Example Output

```
=== TITAN LEVELS - Feb 14, 2026 ===
QQQ:
  Current:    $600.65
  Pre-High:   $602.28 @ 08:30
  Pre-Low:    $597.42 @ 08:15
  Prior High: $615.81 (2026-02-12)
  Prior Low:  $599.57 (2026-02-12)

=== ALERT ===
10:15:32 | QQQ approaching Prior-Low ($599.57)
Current: $600.65

Suggested: Buy QQQ $602 Call
  Target: $602.28
  Stop: Below $596.57
  
Option Details:
  Strike: $602.0
  Bid/Ask: $3.86 / $3.90
  Delta: 0.4974
  Expiration: 2026-02-17
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `titan_level_scanner.py` | Main scanner |
| `levels.py` | Level calculation (Polygon) |
| `alerts.py` | Alert + options (Tradier) |
| `/tmp/titan_levels.json` | Today's levels |
| `/tmp/titan_alerts.json` | Alert history |

## 🔧 Troubleshooting

**No levels found?**
```bash
python3 titan_level_scanner.py --pull-levels
```

**Outside market hours?**
- Scanner auto-pauses outside 6:30am-1pm PST weekdays

**PM2 not starting?**
```bash
pm2 stop all
pm2 start ecosystem.config.js
pm2 logs --lines 50
```

## 📖 Full Docs

- `SESSION_SCANNER_README.md` - Complete documentation
- `SCANNER_BUILD_SUMMARY.md` - Build details & test results
