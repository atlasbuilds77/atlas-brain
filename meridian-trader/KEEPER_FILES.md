# TITAN V3 - KEEPER FILES (Feb 16, 2026)

## ✅ KEEP (Essential Production Files)

**THE GOLDEN ONE:**
- `titan_v3_structured.py` - **83% WR backtest** (Nov 2025 - Feb 2026)
  - Entry: Reclaim bar OPEN
  - Stops: -50% max loss
  - Trails: +30%→15%, +50%→30%
  - Filters: PM range ≥$3, sweep quality, 5-bar reclaim
  - Backup: `ARCHIVE/titan_v3_structured_GOLDEN_83WR_20260216.py`

**LIVE TRADING INFRASTRUCTURE:**
- `titan_scanner.py` - PM level detection + sweep monitoring
- `titan_alerts.py` - Telegram notifications
- `titan_config.py` - Configuration settings
- `titan_executor.py` - (OPTIONAL) Auto-execution module
- `titan_main.py` - Orchestrator

## 🗑️ DELETE (Broken/Test Versions)

All other `titan_v3_*.py` files:
- titan_v3_real_backtest.py (0% WR - BROKEN logic)
- titan_v3_FIXED.py (0% WR - still broken)
- titan_v3_complete.py (old)
- titan_v3_final.py (old)
- titan_v3_formula.py (old)
- titan_v3_full_system.py (old)
- titan_v3_live.py (old)
- titan_v3_pm_backtest.py (old)
- titan_v3_polygon.py (old)
- titan_v3_real.py (old)
- titan_v3_system.py (old)
- titan_v3_backtest.py (old)
- titan_v2_*.py (all v2 versions - obsolete)

Other cleanup:
- titan_auto.py (?)
- titan_level_scanner.py (redundant?)
- titan_morning_scanner.py (redundant?)
- titan_sweep_alert.py (redundant?)
- titan_sweep_scanner.py (redundant?)

---

**THE RULE:** If it's not in the KEEP list above, it gets deleted.

**NEVER TOUCH:** `titan_v3_structured.py` and its backup in ARCHIVE/
