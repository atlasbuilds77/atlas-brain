# Alpaca Trading API

## Account
- **Paper Account ID:** PA3ZJ1WMN69R
- **Status:** Active
- **Simulated Balance:** $500 (ignore the $100k paper balance)

## CLI
```bash
cd ~/clawd/atlas-trader && node cli.js <command>
```

Commands:
- `account` - Show account info
- `positions` - Show open positions
- `orders [status]` - Show orders
- `clock` - Market hours
- `quote <symbol>` - Get quote
- `buy <sym> <qty> [limit] [price]` - Buy
- `sell <sym> <qty> [limit] [price]` - Sell
- `close <symbol>` - Close position
- `cancel <id|all>` - Cancel orders
- `options <sym> [call|put]` - Search options

## Key Files
- atlas-trader/cli.js - CLI interface
- atlas-trader/src/alpaca.js - API client
- atlas-trader/watchlist.md - Current plays
- atlas-trader/journal.md - Trade log

## Features
- Zero commission
- Options support (multi-leg)
- Paper trading
- Good Python SDK (alpaca-py) if needed

---

*Paper trading until consistent, then $500 real*
