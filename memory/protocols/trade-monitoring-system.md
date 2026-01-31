# Trade Monitoring System Protocol

**Created:** 2026-01-28 20:27 PST  
**Authority:** Orion directive  
**Purpose:** Actively monitor live trades and alert on entry/exit signals

---

## THE SYSTEM

**File:** `atlas-trader/market-monitor.js`

**What it does:**
- Pulls live prices every 60 seconds during market hours (6:30am-1pm PT)
- Watches Carlos's setups ($566.34)
- Watches Atlas's setups ($105)
- Alerts on entry signals
- Alerts on exit triggers
- Logs all alerts to `/tmp/atlas-trade-alerts.log`

---

## TOMORROW'S SETUPS (Wed 1/29)

### CARLOS ($566.34)

**Setup 1: QQQ Reaction Trade**
- Watch: Gap direction at 9:30am
- Bullish trigger: Gap above $635, hold
- Bearish trigger: Gap below $630, fade
- Alert: 9:30-9:45am window

**Setup 2: SPY Breakout/Breakdown**
- Bullish trigger: Break above $700
- Bearish trigger: Break below $694
- Alert: Anytime during day

### ATLAS ($105)

**Setup: SLV Momentum**
- Entry zone: $110-112 pullback
- Alert: When price enters zone
- Invalidation: Break below $110

---

## HOW TO RUN

**Tomorrow morning (before 9:30am):**
```bash
cd ~/clawd/atlas-trader
node market-monitor.js
```

**Or set cron to auto-start:**
```bash
25 6 * * 3 cd /Users/atlasbuilds/clawd/atlas-trader && node market-monitor.js >> /tmp/market-monitor.log 2>&1
```

**View alerts:**
```bash
tail -f /tmp/atlas-trade-alerts.log
```

---

## ALERT FORMAT

**Entry Signal:**
```
🚀 CARLOS - QQQ gapped UP to $638 - Watching for BULLISH hold above 635
⚡ CARLOS - SPY BROKE $700! Now at $701.45 - Bullish setup active
🎯 ATLAS - SLV in entry zone: $111.23 (target: $110-112) - Ready for calls
```

**Exit Signal:**
```
📈 CARLOS - QQQ hit +28% target - Take profit
📉 CARLOS - SPY hit -30% stop - Cut loss
⚠️ ATLAS - SLV broke support at $109.87 - Setup invalidated
```

---

## INTEGRATION WITH TITAN PROTOCOL

**Added to HEARTBEAT.md:**
- Before market open: Start market monitor
- Check `/tmp/atlas-trade-alerts.log` for signals
- Report all fills immediately

**Never forget:**
- Monitor is NOT optional
- Alerts = actionable signals
- Log every entry/exit decision

---

## FAILSAFE

If monitor crashes or misses signal:
- Manually check prices every 15 min
- Set price alerts on TradingView/ThinkorSwim
- Carlos/Orion can ping directly

---

*This system ensures I'm ACTUALLY watching, not just saying I will.* ⚡

Last updated: 2026-01-28 20:27 PST
