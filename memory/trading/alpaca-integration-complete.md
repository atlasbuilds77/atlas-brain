# Alpaca Integration Complete

**Status:** ✅ FULLY OPERATIONAL  
**Last Verified:** 2026-01-26

---

## Account Summary

| Field | Value |
|-------|-------|
| Account ID | PA3ZJ1WMN69R |
| Type | Paper Trading |
| Status | ACTIVE |
| Cash | $98,749.99 |
| Buying Power | $197,499.98 |
| Options Level | 3 (spreads allowed) |
| Open Positions | None |
| Open Orders | None |

---

## Credentials Location

```
~/clawd/atlas-trader/.env
```

Contents:
- `ALPACA_API_KEY` - API key
- `ALPACA_API_SECRET` - Secret key
- `ALPACA_BASE_URL` - https://paper-api.alpaca.markets
- `ALPACA_DATA_URL` - https://data.alpaca.markets

**Note:** Currently paper trading. Switch to `https://api.alpaca.markets` for live.

---

## CLI Usage

```bash
cd ~/clawd/atlas-trader && node cli.js <command>
```

### Quick Reference

| Command | Description |
|---------|-------------|
| `account` | Account info, cash, buying power |
| `positions` | Open positions with P&L |
| `orders [status]` | Orders (open/closed/all) |
| `clock` | Market hours |
| `quote <SYM>` | Get bid/ask quote |
| `buy <SYM> <QTY>` | Market buy |
| `buy <SYM> <QTY> limit <PRICE>` | Limit buy |
| `sell <SYM> <QTY>` | Market sell |
| `sell <SYM> <QTY> limit <PRICE>` | Limit sell |
| `close <SYM>` | Close entire position |
| `cancel <ID\|all>` | Cancel order(s) |
| `options <SYM> [call\|put]` | Search options chain |

### Trade Examples

```bash
# Buy 10 shares of AAPL at market
node cli.js buy AAPL 10

# Buy 5 TSLA with limit at $250
node cli.js buy TSLA 5 limit 250

# Sell 10 AAPL at market  
node cli.js sell AAPL 10

# Close entire NVDA position
node cli.js close NVDA

# Cancel all open orders
node cli.js cancel all
```

---

## API Client

**File:** `atlas-trader/src/alpaca.js`

### Available Functions

```javascript
// Account
getAccount()

// Positions
getPositions()
getPosition(symbol)
closePosition(symbol, qty?)

// Orders
getOrders(status?, limit?)
createOrder(order)
cancelOrder(orderId)
cancelAllOrders()

// Market Data
getStockQuote(symbol)
getStockBars(symbol, timeframe?, limit?)
getStockSnapshot(symbol)

// Options
getOptionsContracts(params)
getOptionQuote(symbol)

// Utilities
getClock()
getCalendar(start, end)
getAssets(params)
```

### Direct API Usage (Node.js)

```javascript
import * as alpaca from './src/alpaca.js';

// Get account
const account = await alpaca.getAccount();

// Place order
const order = await alpaca.createOrder({
  symbol: 'AAPL',
  qty: '10',
  side: 'buy',
  type: 'limit',
  limit_price: '200',
  time_in_force: 'day'
});
```

---

## Trading Protocol

### Pre-Trade Checklist
1. Check `clock` - Is market open?
2. Check `account` - Sufficient buying power?
3. Check `quote <SYM>` - Current prices
4. Execute trade
5. Verify with `orders` or `positions`

### Order Types
- **market** - Execute immediately at best price
- **limit** - Execute at specified price or better
- **time_in_force:** day (default), gtc, ioc, fok

### Risk Management
- Paper account: $100K simulated (treat as $500 real)
- Position sizing: Max 10% per trade
- Always use limit orders for entries
- Set mental stops, options for defined risk

---

## Integration Verified

✅ Credentials found and working  
✅ CLI operational  
✅ Account accessible  
✅ Positions queryable  
✅ Orders can be placed  
✅ Orders can be cancelled  
✅ Market data available  
✅ Options chain accessible  

---

## Related Files

- `atlas-trader/cli.js` - CLI interface
- `atlas-trader/src/alpaca.js` - API client
- `atlas-trader/watchlist.md` - Current watchlist
- `atlas-trader/journal.md` - Trade journal
- `memory/tools/alpaca.md` - Quick reference
- `memory/credentials.md` - Master credentials list

---

*Integration completed by Orion subagent 2026-01-26*
