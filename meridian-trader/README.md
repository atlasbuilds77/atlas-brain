# TITAN V3 - QQQ/SPY Options Trading System

**Status:** VALIDATED (83% WR over 3 months)  
**Last Updated:** Feb 16, 2026  
**Mode:** Alert Bot Ready

---

## 🏆 THE GOLDEN FILE

**`titan_v3_structured.py`**
- Backtest: 83% WR (20/24 trades)
- Period: Nov 2025 - Feb 2026
- Total P&L: +$7,195
- **NEVER DELETE THIS FILE**
- Backup: `ARCHIVE/titan_v3_structured_GOLDEN_83WR_20260216.py`

---

## 📁 PRODUCTION FILES (CLEAN)

### Core System
1. **`titan_v3_structured.py`** - The golden backtest system
2. **`titan_scanner.py`** - Live PM level detection + sweep monitoring
3. **`titan_alerts.py`** - Telegram notifications
4. **`titan_config.py`** - Configuration settings
5. **`titan_executor.py`** - (OPTIONAL) Auto-execution
6. **`titan_main.py`** - Orchestrator

---

## 🎯 SYSTEM RULES (FROM GOLDEN VERSION)

### Entry Requirements
1. **PM Range ≥ $3** (skip tight/weak days)
2. **Sweep + 5-bar reclaim** (level must be reclaimed within 5 minutes)
3. **No absorption** (skip if level swept 2+ times in 15 min)
4. **Entry:** Reclaim bar OPEN price

### Position Management
- **80% in 0DTE** (same-day expiration, quick scalp)
- **20% in 1DTE** (next-day expiration, runner)
- **Strikes:** $3 OTM (out of the money)
- **Max Loss:** -50% hard stop
- **Trailing Stops:**
  - +30% gain → trail at +15%
  - +50% gain → trail at +30%

### Trading Window
- **9:30-10:30 AM ET** (first hour only)
- **Tradier API** for execution
- **Polygon.io** for historical data (backtesting)

---

## 📊 BACKTEST RESULTS (VERIFIED)

### Full 3-Month Test (Nov 2025 - Feb 2026)
- **24 trades total**
- **20 wins, 4 losses**
- **83.3% win rate**
- **+$7,195 total P&L**

### Recent 3-Day Test (Feb 12-14, 2026)
- **2 trades (both Feb 13)**
- **2 wins, 0 losses**
- **100% win rate**
- **+$480 total P&L** (+24% on $2k)

**Selectivity is key:** Only traded when valid setups appeared, skipped bad days.

---

## 🗑️ ARCHIVE FOLDER

Contains all deleted/broken versions:
- `titan_v3_real_backtest.py` (0% WR - broken logic)
- `titan_v3_FIXED.py` (still broken)
- All old v2 and v3 test versions
- Redundant scanner files

**DO NOT USE FILES FROM ARCHIVE**

---

## 🚀 DEPLOYMENT OPTIONS

### Option 1: Alert Bot (RECOMMENDED for learning)
- Run `titan_scanner.py` + `titan_alerts.py`
- Receive Telegram alerts when setups trigger
- Manually decide to execute (human filter)
- Learn the system before auto-trading

### Option 2: Full Auto (HIGH RISK)
- Run `titan_main.py` with executor enabled
- Fully automated entry and exit
- Requires live Tradier account with margin
- Not recommended until thoroughly paper-tested

---

## ⚠️ CRITICAL WARNINGS

1. **NEVER modify `titan_v3_structured.py`** without backing up first
2. **Test changes on COPIES only**
3. **Paper trade for 30 days minimum** before live capital
4. **Markets change** - 83% WR in Nov-Feb may not hold in Mar-Apr
5. **Options expire** - 0DTE options can go to $0 in minutes

---

## 🛡️ BACKUP PROTOCOL

**Automatic backup created:** Feb 16, 2026  
**Location:** `ARCHIVE/titan_v3_structured_GOLDEN_83WR_20260216.py`

**To restore golden version:**
```bash
cd /Users/atlasbuilds/clawd/titan-trader
cp ARCHIVE/titan_v3_structured_GOLDEN_83WR_20260216.py titan_v3_structured.py
```

---

## 📞 NEXT STEPS

1. **Name the system** (current ideas: Ambush, Recoil, False Break, Sweep Reclaim)
2. **Set up Telegram alerts** (configure titan_alerts.py)
3. **Paper trade 30 days** (track results, validate edge)
4. **Scale slowly** (start with $500/trade, not $1000)
5. **Review weekly** (win rate, exit reasons, market conditions)

---

**Last Verified:** Feb 16, 2026 01:17 AM PST  
**System Status:** ✅ CLEAN AND READY
