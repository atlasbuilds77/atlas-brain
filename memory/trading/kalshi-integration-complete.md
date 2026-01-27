# Kalshi Integration Complete Protocol

**Date:** 2026-01-26
**Status:** ✅ FULLY OPERATIONAL

---

## 📍 Credentials Location

```
/Users/atlasbuilds/.clawdbot/credentials/kalshi/
├── config.json          # API Key ID
└── private_key.pem      # RSA private key (chmod 600)
```

**API Key ID:** `0007b9f0-89c9-42b4-93bd-f98fbf1596b8`
**API Host:** `https://api.elections.kalshi.com/trade-api/v2`

---

## 🛠️ CLI Tools

### Location
```
/Users/atlasbuilds/clawd/kalshi-trader/
├── kalshi_cli.py              # Full trading CLI
├── check_all_positions.py     # Position checker
└── venv/                      # Python environment with kalshi_python
```

### Quick Wrapper
```bash
./kalshi.sh [command] [args]
```

### Commands

| Command | Description | Example |
|---------|-------------|---------|
| `balance` | Show cash balance | `./kalshi.sh balance` |
| `positions` | Show all positions | `./kalshi.sh positions` |
| `market <ticker>` | Market details | `./kalshi.sh market KXGOVSHUT-26JAN31` |
| `buy <ticker> <side> <count> <price>` | Buy contracts | `./kalshi.sh buy KXGOVSHUT-26JAN31 YES 10 70` |
| `sell <ticker> <side> <count> <price>` | Sell contracts | `./kalshi.sh sell KXGOVSHUT-26JAN31 YES 10 75` |
| `orders` | Show open orders | `./kalshi.sh orders` |
| `search <query>` | Find markets | `./kalshi.sh search shutdown` |

---

## 📊 Current Positions (as of 2026-01-26)

### Active
| Ticker | Market | Position | Current Price | Value | Max Payout |
|--------|--------|----------|---------------|-------|------------|
| KXGOVSHUT-26JAN31 | Gov shutdown Jan 31 | YES × 54 | 72¢ | $38.88 | $54.00 |
| KXHIGHNY-26JAN26-B31.5 | NYC Temp 31-32° Jan 26 | YES × 65 | 0¢ | $0.00 | $65.00 |

### Finalized (Losses)
| Ticker | Market | Position | Result |
|--------|--------|----------|--------|
| KXGOVSHUT-25OCT01 | Gov shutdown Oct 1 | NO × 142 | ❌ Lost (was YES) |
| KXSB-26-DEN | Denver Super Bowl | YES × 55 | ❌ Lost |
| KXTRUMPOUT-26-TRUMP | Trump out this year | YES × 735 | ❌ Lost |

**Cash Balance:** $0.04
**Total Account Value:** ~$38.92

---

## 💡 Trading Guide

### Fee Formula
```
Fee per contract = 0.07 × P × (1-P)
```
Where P = price as decimal (e.g., 70¢ = 0.70)

**Example:** At 70¢, fee = 0.07 × 0.70 × 0.30 = $0.0147/contract

### Place a Trade (via CLI)

```bash
# Buy 10 YES contracts at 70 cents on Gov Shutdown
./kalshi.sh buy KXGOVSHUT-26JAN31 YES 10 70

# Sell 5 YES contracts at 75 cents
./kalshi.sh sell KXGOVSHUT-26JAN31 YES 5 75
```

### Place a Trade (Python)

```python
from kalshi_python import Configuration, KalshiClient
import os

# Setup
config = Configuration(host="https://api.elections.kalshi.com/trade-api/v2")
config.api_key_id = "0007b9f0-89c9-42b4-93bd-f98fbf1596b8"
with open("/Users/atlasbuilds/.clawdbot/credentials/kalshi/private_key.pem") as f:
    config.private_key_pem = f.read()
client = KalshiClient(config)

# Buy order
client.create_order(
    ticker="KXGOVSHUT-26JAN31",
    side="yes",
    action="buy",
    type="limit",
    count=10,
    yes_price=70
)

# Sell order
client.create_order(
    ticker="KXGOVSHUT-26JAN31",
    side="yes",
    action="sell",
    type="limit",
    count=5,
    yes_price=75
)
```

---

## 🔄 Cron Job Integration

### Position Check Cron
```bash
# Add to crontab for hourly position checks
0 * * * * cd /Users/atlasbuilds/clawd && ./kalshi.sh positions >> /Users/atlasbuilds/clawd/logs/kalshi-positions.log 2>&1
```

### Python Integration
```python
#!/usr/bin/env python3
import subprocess

def check_kalshi_positions():
    result = subprocess.run(
        ['./kalshi.sh', 'positions'],
        capture_output=True,
        text=True,
        cwd='/Users/atlasbuilds/clawd'
    )
    return result.stdout
```

---

## ⚠️ Known Issues

1. **SDK validation error for "finalized" markets** - The kalshi_python SDK doesn't recognize "finalized" status. Use raw API requests for those markets (handled in check_all_positions.py).

2. **get_portfolio() not available** - The SDK doesn't have this method. Position tracking is done via fills aggregation.

3. **NYC Temp bet likely lost** - Current NYC high is ~27°F, well below the 31-32° range. This position will expire worthless.

---

## 🎯 Next Steps

1. **Add funds** to account (currently $0.04 cash)
2. **Monitor Gov Shutdown position** - Currently at 72¢ YES, closes Jan 31
3. **Set up price alerts** for Gov Shutdown movement
4. **Consider exit strategy** for Gov Shutdown before resolution

---

## 📁 Related Files

- `/Users/atlasbuilds/clawd/KALSHI_API_SCALPING_GUIDE.md` - Scalping strategies
- `/Users/atlasbuilds/clawd/Kalshi_Economic_Data_Trading_Playbook.md` - Economic data plays
- `/Users/atlasbuilds/clawd/kalshi-trader/` - All Kalshi trading code
