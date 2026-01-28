# KALSHI API SETUP & USAGE PROTOCOL

**Last Updated:** 2026-01-26 11:14 PM PST  
**Version:** 1.0  
**Status:** In Progress (needs API key)  
**Affects Cron Jobs:** Position Check, Trade Research

---

## SETUP STATUS

✅ **Private Key:** `~/.kalshi/private_key.pem` (exists)  
✅ **Python SDK:** `kalshi-python 2.1.4` (installed)  
✅ **Script Created:** `~/clawd/scripts/kalshi/check_positions.py`  
❌ **API Key:** Not set (needs KALSHI_API_KEY env var)  
❌ **Email/Password:** Not configured (needs KALSHI_EMAIL, KALSHI_PASSWORD)

---

## REQUIRED CREDENTIALS

### Get From Kalshi Account

1. Log in to https://kalshi.com
2. Navigate to API settings
3. Generate API key
4. Note email and password for account

### Set Environment Variables

Add to gateway config or `.zshrc`:

```bash
export KALSHI_API_KEY="your_api_key_here"
export KALSHI_EMAIL="your_email@example.com"
export KALSHI_PASSWORD="your_password"
```

**OR** add to gateway config:

```json
{
  "env": {
    "KALSHI_API_KEY": "...",
    "KALSHI_EMAIL": "...",
    "KALSHI_PASSWORD": "..."
  }
}
```

---

## USAGE

### Check All Positions

```bash
python3 ~/clawd/scripts/kalshi/check_positions.py
```

**Output:**
```
💰 BALANCE: $X.XX

📊 POSITIONS: N open
--------------------------------------------------------------------------------

✅ KXGOVSHUT-26JAN27
   Title: Government shutdown on Saturday?
   Side: YES
   Contracts: 44
   Entry: 80¢
   Current: 85¢
   Cost Basis: $35.20
   Current Value: $37.40
   P&L: +$2.20 (+6.3%)
   Closes: 2026-01-27T12:00:00Z

❌ KXHIGHNY-26JAN26-B31.5
   Title: NYC High Temp 31-32°F
   Side: YES
   Contracts: 38
   Entry: 16¢
   Current: 12¢
   Cost Basis: $6.08
   Current Value: $4.56
   P&L: -$1.52 (-25.0%)
   Result: NO (resolved)

--------------------------------------------------------------------------------
💵 TOTAL P&L: +$0.68
```

### Show Recent Trades

```bash
python3 ~/clawd/scripts/kalshi/check_positions.py --trades
```

### Show More Trades

```bash
python3 ~/clawd/scripts/kalshi/check_positions.py --trades --limit 20
```

---

## SCRIPT FEATURES

### `check_positions.py`

**What it does:**
- Connects to Kalshi API with credentials
- Gets account balance
- Lists all open positions with:
  - Market title and ticker
  - Side (YES/NO)
  - Contracts held
  - Entry price and current price
  - Cost basis and current value
  - P&L ($ and %)
  - Resolution info if closed
- Calculates total P&L across all positions
- Optionally shows recent trade history

**Requirements:**
- `kalshi-python` package (installed)
- `KALSHI_API_KEY` environment variable
- `KALSHI_EMAIL` environment variable (optional)
- `KALSHI_PASSWORD` environment variable (optional)
- Private key at `~/.kalshi/private_key.pem`

---

## INTEGRATION WITH CRON JOBS

### Position Check Cron

**Current text:**
```
POSITION CHECK: Check ALL live positions. 
PROTOCOLS: 
1) Jupiter Perps - Use browser tool. See memory/protocols/jupiter-position-check-complete.md
2) Kalshi - Check memory/trading/active-positions.md for last known status
3) Alpaca - Check memory file
```

**After API setup:**
```
POSITION CHECK: Check ALL live positions. 
PROTOCOLS: 
1) Jupiter Perps - Use browser tool. See memory/protocols/jupiter-position-check-complete.md
2) Kalshi - Run python3 ~/clawd/scripts/kalshi/check_positions.py. See memory/protocols/trading/kalshi-api-setup.md
3) Alpaca - Check memory file
Report total P&L + status + exit guidance.
```

---

## ERROR HANDLING

### Missing API Key

```
ERROR: KALSHI_API_KEY not set in environment
Set it with: export KALSHI_API_KEY='your_key_here'
```

**Fix:** Set environment variable or add to gateway config

### Missing Private Key

```
ERROR: Private key not found at ~/.kalshi/private_key.pem
```

**Fix:** Generate private key from Kalshi account, save to `~/.kalshi/private_key.pem`

### Authentication Failed

```
ERROR: 401 Unauthorized
```

**Fix:** Verify API key, email, and password are correct

---

## POSITION DATA STRUCTURE

### Market Fields
- `ticker`: Market ticker (e.g., KXGOVSHUT-26JAN27)
- `title`: Human-readable title
- `last_price`: Current price (cents)
- `yes_bid`: Bid price for YES
- `close_time`: When market resolves
- `result`: Resolution (YES/NO/null)

### Position Fields
- `market_ticker`: Which market
- `position`: Number of contracts (positive=long, negative=short)
- `total_cost`: Total paid for position (cents)

### Calculated Fields
- `current_value`: position × current_price / 100
- `pnl`: current_value - (total_cost / 100)
- `pnl_pct`: (pnl / cost_basis) × 100

---

## TESTING CHECKLIST

Once credentials are set:

1. [ ] Test basic balance check: `python3 ~/clawd/scripts/kalshi/check_positions.py`
2. [ ] Verify positions show correct P&L
3. [ ] Test trade history: `--trades` flag
4. [ ] Run from cron job context (check env vars available)
5. [ ] Update cron job with new protocol
6. [ ] Test cron job runs successfully
7. [ ] Update `memory/trading/active-positions.md` with live data

---

## NEXT STEPS (TO COMPLETE SETUP)

1. **Get Kalshi API credentials** from Orion
2. **Add to gateway config** or environment
3. **Test script** manually
4. **Update position check cron job** to use script
5. **Update active-positions.md** with live data
6. **Schedule regular updates** (every 15 min via cron)

---

## API DOCUMENTATION

**Official Docs:** https://trading-api.readme.io/docs  
**Python SDK:** https://github.com/Kalshi/kalshi-python  
**Endpoints Used:**
- `GET /balance` - Account balance
- `GET /positions` - All open positions
- `GET /markets/{ticker}` - Market details
- `GET /fills` - Trade history

---

**Status:** Ready for testing once credentials provided  
**Next Update:** After successful API connection test  
**Priority:** HIGH (needed for position monitoring)
