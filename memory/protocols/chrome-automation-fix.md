# Chrome Automation Blocking Fix for Jupiter Perps

## Problem
Chrome detects automation (Peekaboo/browser tool) and blocks the Jupiter wallet extension with `ERR_BLOCKED_BY_CLIENT`.

## Root Cause
- Chrome's automation detection triggers when controlled via:
  - Accessibility APIs (Peekaboo)
  - Chrome DevTools Protocol (browser tool)
- Jupiter wallet extension is flagged as security risk when automation is detected

## Solution Options

### Option 1: Chrome Launch Flags (Temporary Fix)
Launch Chrome with these flags to disable automation detection:
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --disable-blink-features=AutomationControlled \
  --disable-features=IsolateOrigins,site-per-process \
  --disable-site-isolation-trials \
  --user-data-dir="$HOME/Library/Application Support/Google/Chrome/Profile Trading"
```

### Option 2: Clawdbot Browser Config (Needs Implementation)
Add to `clawdbot.json`:
```json
{
  "browser": {
    "profiles": {
      "clawd": {
        "chromeFlags": [
          "--disable-blink-features=AutomationControlled",
          "--disable-features=IsolateOrigins,site-per-process",
          "--disable-site-isolation-trials"
        ],
        "userDataDir": "/Users/atlasbuilds/Library/Application Support/Google/Chrome/Profile Trading"
      }
    }
  }
}
```

**NOTE:** This config structure may need adjustment based on actual browser tool implementation.

### Option 3: Use Phone for Jupiter (Current Workaround)
- Keep using phone for Jupiter Perps trades
- Use desktop automation for Alpaca (has API, no browser needed)
- Most practical until browser config is properly implemented

## What Needs To Happen

1. **Check Clawdbot browser tool source** - find where Chrome is launched
2. **Add chrome flags parameter** to browser tool startup
3. **Test with Jupiter Perps** - verify ERR_BLOCKED_BY_CLIENT is resolved
4. **Document final config** in this file

## Current Status
- Phone trading works fine (no automation detection)
- Desktop automation blocked until Chrome flags are added to browser tool
- Peekaboo workaround (screencapture + blind clicks) partially effective but unreliable

---

*Created: 2026-01-27*
*Issue: Jupiter wallet extension blocked when Chrome under automation*
*Priority: Medium (phone workaround sufficient for now)*
