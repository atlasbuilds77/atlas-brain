# SPX CHANGES - IN PROGRESS
**Date:** 2026-02-02 17:11 PST
**Task:** Implement SPX position sizing fixes

---

## COMPLETED ✅

### 1. Updated Helios SPX ALGO.txt
- **Action:** Replaced with Zenith v54 content
- **File:** `/Users/atlasbuilds/Desktop/ProjectHelios/Helios SPX ALGO.txt`
- **Status:** DONE

### 2. Modified main.py SPX Configuration
- **SPX_MIN_DTE:** Changed from 1-3 DTE → 1 DTE only
- **SPX_MAX_DTE:** Changed from 3 → 1 DTE
- **SPX_MIN_PREMIUM:** Changed from $4.00 ($400) → $5.00 ($500)
- **SPX_MAX_PREMIUM:** Changed from $25.00 ($2500) → $10.00 ($1000)
- **Added:** SPX_OTM_OFFSET_MIN = 10.0 ($10 OTM minimum)
- **Added:** SPX_OTM_OFFSET_MAX = 15.0 ($15 OTM maximum)
- **Status:** DONE

### 3. Modified SPX Strike Selection Logic
- **Old method:** Delta-based (SPX_TARGET_DELTA = 0.30)
- **New method:** $10-15 OTM offset from spot price
- **Logic:** 
  - Calls: strike = spot + $12.50 (avg of 10-15)
  - Puts: strike = spot - $12.50 (avg of 10-15)
  - Filters contracts within $10-15 OTM range
  - Picks closest to target
- **Fallbacks:** Profile-based → Delta-based if OTM fails
- **File:** `/Users/atlasbuilds/Desktop/ProjectHelios/main.py` lines ~3714-3768
- **Status:** DONE

---

## TODO 🔄

### 4. Profit Alert System (10/20/30/40%)
- **Need:** Discord notifications when SPX positions cross profit thresholds
- **Implementation plan:**
  - Add profit_alerts table to database
  - Track which alerts have been sent per trade_id
  - Check on /positions endpoint or periodic cron
  - Send Discord notification when threshold crossed
- **Status:** NOT STARTED

---

## SUMMARY

**What works now:**
- SPX uses 1DTE only
- Contract price capped at $500-1000
- Strike selection uses $10-15 OTM instead of delta
- Cheaper contracts = smaller losses when wrong

**What's left:**
- Profit notification system (10/20/30/40% alerts)

**Files modified:**
1. `/Users/atlasbuilds/Desktop/ProjectHelios/Helios SPX ALGO.txt` (replaced)
2. `/Users/atlasbuilds/Desktop/ProjectHelios/main.py` (modified lines 70-87, 3714-3768)

⚡
