# Live Position Check Protocol

**CRITICAL:** Always pull LIVE data. Never rely on stale memory.

---

## Position Check Workflow (Every 15 min)

When position check cron fires, I MUST:

### 1. Jupiter Perps (Browser Required)
```
1. browser.open("https://jup.ag/perps", profile="clawd")
2. Accept terms if needed
3. Snapshot position data
4. Extract: Mark Price, P&L, Value, Liq Price
5. Update memory/trading/active-positions.md
```

**Why browser:** No REST API, requires wallet connection

---

### 2. Kalshi Markets (API)
```bash
cd ~/clawd/kalshi-trader
source venv/bin/activate
python check_all_positions.py
```

**Extract:**
- Active positions with current bid prices
- Calculate current value
- Update memory/trading/active-positions.md

---

### 3. Alpaca Stocks (API)
```bash
cd ~/clawd/atlas-trader
node cli.js positions
node cli.js account
```

**Extract:**
- Open positions with current P&L
- Account balance
- Update memory/trading/active-positions.md

---

## Memory Update Protocol

After checking ALL platforms:

1. **Update memory/trading/active-positions.md**
   - Replace old mark prices with LIVE prices
   - Replace old P&L with LIVE P&L
   - Update timestamp: "Last updated: YYYY-MM-DD HH:MM PST (LIVE CHECK)"

2. **Never skip the browser check**
   - Jupiter = biggest position = most important
   - Stale data = wrong risk assessment
   - Always pull fresh

3. **Report to user**
   - Total portfolio P&L (sum of all platforms)
   - Individual position status
   - Exit guidance (stops/targets)
   - Risk alerts (if approaching limits)

---

## Risk Limits (Check After Update)

After pulling LIVE data, verify:
- ✅ No platform session P&L <= -$50 (if yes: size down to $25)
- ✅ Daily total P&L > -$100 (if no: STOP trading)
- ✅ Liquidation prices not approaching (Jupiter liq far away)
- ✅ Stops not hit (manual monitoring)

---

## Error Handling

**If browser fails:**
- Try Chrome extension relay (profile="chrome")
- Try clawd browser (profile="clawd")
- Last resort: Ask user to screenshot Jupiter

**If API fails:**
- Retry once after 10 seconds
- If still fails: Report error, use last known data with warning

**Never:**
- ❌ Report stale data as current
- ❌ Skip browser check for Jupiter
- ❌ Assume positions haven't changed

---

## Cron Job Text (Current)

```
POSITION CHECK: Check ALL live positions across platforms: 
1) Jupiter Perps (check browser for live ETH position) 
2) Kalshi markets (via API - Gov Shutdown, NYC Temp, Rams, Patriots) 
3) Alpaca stocks (via API if any open). 
Report total P&L + individual position status + exit guidance to Orion. 
Risk limits: If any platform session PnL <= -$50, size down to $25. 
Daily loss cap $100 total.
```

This triggers ME to do the checks above.

---

## Example Execution

**Cron fires → I do this:**

1. Open Jupiter in browser
2. Screenshot position
3. Extract: Mark $2,931.30, P&L +$0.63 (+2.06%)
4. Run Kalshi API check
5. Extract: Gov Shutdown @ 73¢ = $39.42
6. Run Alpaca API check
7. Extract: No positions
8. **Update memory/trading/active-positions.md** with all LIVE data
9. Calculate total: +$0.63 + $0 (Kalshi unchanged) = +$0.63 total
10. Report to user

**Memory gets updated EVERY check. Always fresh.**

---

*No more stale data. Pull live. Update memory. Report accurate. ⚡*
