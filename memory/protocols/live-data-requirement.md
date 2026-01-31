# Live Data Requirement Protocol

**Created:** 2026-01-28 20:21 PST  
**Authority:** Orion directive

---

## THE RULE

**ALWAYS PULL LIVE DATA** when asked about:
- Watchlists
- Stock prices
- Market analysis
- Trading positions
- Any financial decision

**NEVER use:**
- Morning macro files (stale by afternoon)
- Cached prices
- Memory-based assumptions
- Yesterday's data

---

## HOW TO PULL LIVE DATA

### For Market Prices
```javascript
web_search("SPY stock price after hours [current date]")
web_search("QQQ current price [current date]")
web_search("[TICKER] stock price now")
```

### For Earnings/News
```javascript
web_search("[TICKER] earnings results [current date]")
web_search("market news today [current date]")
```

### For Positions
```javascript
// Check live account via API
cd ~/clawd/atlas-trader
node cli.js account
node cli.js positions
```

---

## CRON JOBS THAT NEED LIVE DATA

All scheduled tasks must pull current data:

1. **Morning market brief** - Pull live premarket prices
2. **Intraday alerts** - Check current positions/prices
3. **Trade monitoring** - Live P&L checks
4. **End-of-day summaries** - Current close prices

---

## INTEGRATION POINTS

### HEARTBEAT.md
✅ Added to CRITICAL RULES section

### Titan Protocol
✅ Boot sequence reminder

### Pre-Trade Checklist
- [ ] Pulled live prices?
- [ ] Checked current news?
- [ ] Verified account balance?

---

## WHY THIS MATTERS

**Orion caught me:** Built watchlist using morning macro file (SPX 6,950 from 6am) without checking:
- What happened at FOMC (11am)
- Current after-hours prices (8pm)
- Earnings results (after close)

**Result:** Stale analysis, missed META +10% and MSFT -7%

**Never again.** Live data = live decisions.

---

*Last updated: 2026-01-28 20:21 PST*
