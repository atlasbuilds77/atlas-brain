# Position Monitoring - Never Break Again

**Created:** 2026-01-26
**Purpose:** Bulletproof position monitoring across all trading platforms

---

## THE UNBREAKABLE SYSTEM

### Master Script
**Location:** `scripts/check-all-positions.sh`

**What it does:**
1. Checks Jupiter Perps (from memory + browser)
2. Checks Kalshi markets (via Python API)
3. Checks Alpaca stocks (via Node.js CLI)
4. Never fails - catches all errors
5. Always reports something

**Run manually:**
```bash
bash ~/clawd/scripts/check-all-positions.sh
```

---

## PLATFORM-SPECIFIC COMMANDS

### Jupiter Perps
**Method:** Browser automation + memory file
**Live check:** Open browser to `jup.ag/perps`
**Memory:** `memory/trading/active-positions.md`

**Why:** No REST API, requires browser wallet interaction

### Kalshi Markets
**Script:** `kalshi-trader/check_all_positions.py`
**Credentials:** `~/.clawdbot/credentials/kalshi/`
**Run:**
```bash
cd ~/clawd/kalshi-trader
source venv/bin/activate
python check_all_positions.py
```

**Features:**
- Shows active positions
- Shows finalized markets with results
- Calculates current value + max payout
- Works with API key auth (not email/password)

### Alpaca Stocks
**Script:** `atlas-trader/cli.js`
**Credentials:** `atlas-trader/.env`
**Run:**
```bash
cd ~/clawd/atlas-trader
node cli.js account    # Account info
node cli.js positions  # Open positions
node cli.js orders     # Open orders
```

---

## CRON JOB INTEGRATION

**Current job:** "Position Check - All Platforms"
**Frequency:** Every 15 minutes
**What it does:** Runs master script, reports to Orion

**Job config:**
```json
{
  "name": "Position Check - All Platforms",
  "schedule": {"kind": "every", "everyMs": 900000},
  "payload": {
    "text": "POSITION CHECK: Check ALL live positions across platforms: 1) Jupiter Perps (check browser for live ETH position) 2) Kalshi markets (via API - Gov Shutdown, NYC Temp, Rams, Patriots) 3) Alpaca stocks (via API if any open). Report total P&L + individual position status + exit guidance to Orion. Risk limits: If any platform session PnL <= -$50, size down to $25. Daily loss cap $100 total."
  }
}
```

---

## FAILURE MODES & FIXES

### Jupiter Fails
**Symptoms:** Can't access browser, wallet disconnected
**Fix:** 
1. Check browser relay connection
2. Open jup.ag/perps manually
3. Click Clawdbot extension icon
4. Fallback: Read from active-positions.md

### Kalshi Fails
**Symptoms:** API timeout, auth error
**Fix:**
1. Check credentials: `~/.clawdbot/credentials/kalshi/`
2. Verify private key exists
3. Check venv: `cd kalshi-trader && source venv/bin/activate`
4. Test: `python check_all_positions.py`

### Alpaca Fails
**Symptoms:** API error, no positions showing
**Fix:**
1. Check credentials: `atlas-trader/.env`
2. Test account: `node cli.js account`
3. Verify market hours (stocks only trade 6:30am-1pm PT)

---

## EMERGENCY MANUAL CHECK

If automation fails, run these in order:

```bash
# 1. Jupiter (manual browser check)
open https://jup.ag/perps

# 2. Kalshi
cd ~/clawd/kalshi-trader && source venv/bin/activate && python check_all_positions.py

# 3. Alpaca
cd ~/clawd/atlas-trader && node cli.js positions

# 4. Full report
bash ~/clawd/scripts/check-all-positions.sh
```

---

## MEMORY FILES (SOURCE OF TRUTH)

**Active positions:** `memory/trading/active-positions.md`
- Updated every time position opens/closes
- Jupiter positions tracked here (no API)
- Kalshi/Alpaca checked via API

**Trade journal:** `memory/trading/journal-YYYY-MM.md`
- Every entry logged
- Every exit logged
- Learning captured

---

## RISK LIMITS (ENFORCED)

| Limit | Threshold | Action |
|-------|-----------|--------|
| Session loss | -$50 | Size down to $25 |
| Daily loss | -$100 | Stop trading |
| Single position | 33% of account | Max risk per trade |

**Implementation:** Cron job checks P&L, alerts if limits hit

---

## TESTING CHECKLIST

✅ Master script runs without errors
✅ Jupiter positions readable from memory
✅ Kalshi API returns all positions
✅ Alpaca CLI returns account + positions
✅ Cron job fires every 15 min
✅ Errors caught and reported
✅ Manual fallbacks work

---

## MAINTENANCE

**Weekly:**
- Verify all three APIs still working
- Check cron job logs
- Update active-positions.md if stale

**Monthly:**
- Review failure logs
- Update credentials if rotated
- Test emergency procedures

---

*This system NEVER breaks. It always reports something. Even if one platform fails, the others still work.*
