# Chrome Stealth Fix - Quick Reference

## TL;DR

**Problem:** Chrome blocks Jupiter extension when Clawdbot controls it (ERR_BLOCKED_BY_CLIENT)  
**Cause:** Automation detection (navigator.webdriver, CDP signatures)  
**Solution:** Two approaches - pick one or use both

---

## Option 1: Extension Profile (EASIEST) ⭐

Use Clawdbot's Chrome extension to control YOUR Chrome (not the managed one).

### Setup (5 minutes)

```bash
# 1. Run the installer
./fix-chrome-stealth.sh
# Choose option 1

# 2. Launch custom Chrome
~/launch-chrome-jupiter.sh

# 3. In that Chrome:
#    - Load Jupiter extension manually
#    - Go to chrome://extensions
#    - Enable Developer mode
#    - Load Clawdbot extension:
clawdbot browser extension install
clawdbot browser extension path
#    - Click Clawdbot icon to attach

# 4. Test
clawdbot browser --browser-profile chrome tabs
```

### Pros/Cons

✅ No system modifications  
✅ Full control over flags  
✅ Survives Clawdbot updates  
⚠️ Manual Chrome launch each time  

---

## Option 2: Patch Clawdbot (AUTOMATIC)

Modify Clawdbot to always launch with stealth flags.

### Setup (2 minutes)

```bash
# 1. Run installer with sudo
./fix-chrome-stealth.sh
# Choose option 2

# 2. Test
clawdbot browser --browser-profile clawd start
clawdbot browser open https://bot.sannysoft.com/
```

### Pros/Cons

✅ Automatic (no manual launch)  
✅ Works with standard workflow  
⚠️ Requires sudo  
⚠️ Lost on Clawdbot updates (re-run script)  

---

## File Locations

| Item | Path |
|------|------|
| Config | `~/.clawdbot/clawdbot.json` |
| Browser profiles | `~/.clawdbot/browser/` |
| Chrome launcher code | `/opt/homebrew/lib/node_modules/clawdbot/dist/browser/chrome.js` |
| Extension | `clawdbot browser extension path` |

---

## Testing Automation Detection

```bash
# Test current setup
clawdbot browser open https://bot.sannysoft.com/
clawdbot browser screenshot --full-page

# Check what fails
# Look for:
# ❌ navigator.webdriver = true
# ❌ Chrome driver detected
# ❌ Automation detected
```

**Goal:** All tests should show ✅ or "false"

---

## Troubleshooting

### Extension won't connect

```bash
# Check relay is running
clawdbot browser status

# Should show:
# controlUrl: http://127.0.0.1:18791
# running: true
```

### Jupiter still blocks

Try combining both methods:
```bash
# 1. Patch Clawdbot
./fix-chrome-stealth.sh  # Option 2

# 2. Also add more flags to your manual launch
~/launch-chrome-jupiter.sh
```

Add to launch script:
```bash
--disable-web-security \
--disable-features=IsolateOrigins,site-per-process \
--disable-site-isolation-trials
```

⚠️ Security warning: Only for testing

### Clawdbot updated and patch lost

```bash
# Re-run patcher
./fix-chrome-stealth.sh  # Option 2
```

---

## Key Commands

```bash
# Browser status
clawdbot browser status

# List profiles
clawdbot config get browser.profiles

# Start clawd profile
clawdbot browser --browser-profile clawd start

# Use extension profile
clawdbot browser --browser-profile chrome tabs

# Test automation detection
clawdbot browser open https://bot.sannysoft.com/
clawdbot browser screenshot --full-page

# Restart gateway
clawdbot gateway restart
```

---

## What Gets Fixed

| Detection Vector | Fix Method |
|------------------|------------|
| navigator.webdriver | `--disable-blink-features=AutomationControlled` |
| Automation indicators | `--disable-automation` |
| CDP detection | Manual Chrome launch (Extension) |
| Chrome flags | Custom launch script |

---

## When to Use Which

### Use Extension Profile if:
- ✅ You want maximum control
- ✅ You don't mind manual Chrome launch
- ✅ You update Clawdbot frequently
- ✅ You need highest stealth (can add more flags)

### Use Code Patch if:
- ✅ You want fire-and-forget
- ✅ You prefer standard Clawdbot workflow
- ✅ You rarely update Clawdbot
- ✅ You have sudo access

### Use Both if:
- ✅ Maximum reliability needed
- ✅ Jupiter is extremely strict
- ✅ You want fallback options

---

## Next Steps After Fix

1. **Test detection:** https://bot.sannysoft.com/
2. **Try Jupiter:** Load wallet and attempt transactions
3. **Monitor errors:** Check Chrome console for blocks
4. **Iterate:** Add more flags if needed (see findings doc)

---

## Support Files

- **Detailed analysis:** `chrome-automation-fix-findings.md`
- **Installer script:** `fix-chrome-stealth.sh`
- **This guide:** `chrome-stealth-quickref.md`

---

## Emergency Rollback

### If Extension method breaks:

```bash
# Just close Chrome and use normal Clawdbot
rm ~/launch-chrome-jupiter.sh
clawdbot browser --browser-profile clawd start
```

### If Code Patch breaks:

```bash
# Restore backup
sudo cp /opt/homebrew/lib/node_modules/clawdbot/dist/browser/chrome.js.backup* \
       /opt/homebrew/lib/node_modules/clawdbot/dist/browser/chrome.js

clawdbot gateway restart
```

---

## Additional Resources

- Clawdbot docs: `/opt/homebrew/lib/node_modules/clawdbot/docs/tools/browser.md`
- Chrome flags: https://peter.sh/experiments/chromium-command-line-switches/
- Detection tests: https://bot.sannysoft.com/

---

**Created:** 2025-01-27  
**For:** Jupiter Perps automation on desktop Chrome
