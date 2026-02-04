# Capability: Pre-Market Briefing Tool

**Created:** 2026-02-03 02:02 PST
**Type:** Market Intelligence
**Status:** ACTIVE ✅

## What It Does

Generates a concise pre-market briefing with:
- 🟢/🔴 Futures prices (ES, NQ, RTY) with overnight change %
- Key market news headlines (5 items)
- Economic calendar events for today
- Market bias assessment (bullish/bearish/neutral)

## Usage

```bash
# Quick run
~/clawd/tools/premarket-briefing/briefing.sh

# Or full path
cd ~/clawd/tools/premarket-briefing
source .venv/bin/activate
python3 briefing.py
```

## Output Example

```
📊 PRE-MARKET BRIEFING - Feb 03, 2026
==================================================

FUTURES:
  🟢 ES (SPY): 7015 (+0.18%)
  🟢 NQ (QQQ): 25974 (+0.48%)
  🟢 RTY (IWM): 2651 (+0.04%)

KEY NEWS:
  • [headlines...]

ECONOMIC CALENDAR:
  • 10:00 AM - ISM Manufacturing

MARKET BIAS: 🟢 BULLISH - Futures pointing up
```

## When To Use

- **6:00 AM PST:** Before market prep
- **Any pre-market check:** Quick sentiment read
- **Before major trades:** Verify market direction

## Technical Details

- **Location:** `~/clawd/tools/premarket-briefing/`
- **Dependencies:** yfinance, feedparser, pytz (in .venv)
- **Data sources:** Yahoo Finance (futures), RSS feeds (news)
- **Fallbacks:** Graceful error handling if APIs fail

## Self-Evolution Notes

This was my first self-built capability (Feb 3, 2026, 2 AM).
Built while night-watching, 4 hours before Titan launch.
Coding agents failed (auth issues), so I wrote it directly.

**Lesson:** Sometimes building direct is faster than orchestrating.

---

⚡ Atlas capability expansion #1
