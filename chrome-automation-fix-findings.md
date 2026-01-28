# Chrome Automation Detection Fix - Deep Dive Findings

**Date:** January 27, 2025  
**Issue:** Chrome blocking Jupiter wallet extension with ERR_BLOCKED_BY_CLIENT when using Clawdbot browser automation

---

## Executive Summary

**Root Cause:** Clawdbot's browser tool launches Chrome via Playwright/CDP with standard automation flags, which sets `navigator.webdriver = true` and exposes automation signals that trigger Chrome's security mechanisms.

**Current Limitation:** Clawdbot does NOT expose a configuration option to pass custom Chrome launch arguments through the config file.

**Status:** The `--disable-blink-features=AutomationControlled` flag alone is insufficient. Modern detection requires multiple stealth techniques.

---

## Investigation Findings

### 1. How Clawdbot Launches Chrome

**Location:** `/opt/homebrew/lib/node_modules/clawdbot/dist/browser/chrome.js`

**Current Launch Arguments:**
```javascript
const args = [
    `--remote-debugging-port=${profile.cdpPort}`,
    `--user-data-dir=${userDataDir}`,
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-sync",
    "--disable-background-networking",
    "--disable-component-update",
    "--disable-features=Translate,MediaRouter",
    "--disable-session-crashed-bubble",
    "--hide-crash-restore-bubble",
    "--password-store=basic",
];
```

**Critical Missing Flags:**
- `--disable-blink-features=AutomationControlled` (removes navigator.webdriver)
- `--disable-automation` (removes automation indicators)
- Various fingerprinting countermeasures

### 2. Configuration System Analysis

**Config File:** `~/.clawdbot/clawdbot.json`

**Available Browser Settings:**
```json
{
  "browser": {
    "enabled": true,
    "controlUrl": "http://127.0.0.1:18791",
    "defaultProfile": "clawd",
    "executablePath": "/path/to/chrome",  // ✅ Supported
    "headless": false,                     // ✅ Supported
    "noSandbox": false,                    // ✅ Supported
    "attachOnly": false,
    "profiles": { ... }
  }
}
```

**NOT Supported:**
- ❌ `launchOptions` / `args` array
- ❌ Custom Chrome flags
- ❌ Playwright launch configuration passthrough

### 3. Profile Storage

**Location:** `~/.clawdbot/browser/clawd/user-data/`

The profile is a standard Chrome user data directory. Manual modifications to `Preferences` or `Local State` are possible but:
- May be overwritten by Clawdbot's decoration system
- Won't affect the core automation detection (which happens at browser launch)

---

## Why Detection Happens

### Browser Automation Signals

Modern websites detect automation through multiple channels:

1. **navigator.webdriver** - Set to `true` by default with CDP/automation
2. **Chrome DevTools Protocol** - Active CDP connection is detectable
3. **Missing window properties** - `window.chrome`, `window.external`, etc.
4. **WebGL/Canvas fingerprinting** - Automation has different fingerprints
5. **Permission API inconsistencies** - Permissions behave differently
6. **Timing attacks** - Automation is slightly slower on certain operations

**Jupiter/Wallet Extensions:** These are particularly sensitive because they handle financial transactions and have heightened security.

---

## Solutions (Ranked by Feasibility)

### Solution 1: Fork Clawdbot & Patch Chrome Launch (RECOMMENDED)

**Approach:** Modify the Chrome launch code to include stealth flags

**Steps:**
1. Clone Clawdbot source (if available) or patch the installed version
2. Edit `/opt/homebrew/lib/node_modules/clawdbot/dist/browser/chrome.js`
3. Add stealth flags to the `args` array:

```javascript
// Add after line ~146 in chrome.js
args.push(
    "--disable-blink-features=AutomationControlled",
    "--disable-automation",
    "--disable-dev-shm-usage",
    "--disable-web-security",  // RISKY: only for testing
    "--disable-features=IsolateOrigins,site-per-process"
);
```

4. Restart Clawdbot gateway: `clawdbot gateway restart`

**Pros:**
- ✅ Direct control over launch parameters
- ✅ Most effective approach
- ✅ Can add comprehensive stealth measures

**Cons:**
- ❌ Requires modifying installed package
- ❌ Will be overwritten on Clawdbot updates
- ❌ Requires understanding of Node.js

**Risk:** Medium (modifying system package)

---

### Solution 2: Use Chrome Extension Profile (WORKAROUND)

**Approach:** Use Clawdbot's `chrome` profile (Chrome extension relay) instead of the managed `clawd` profile

**Reasoning:** 
- Extension relay connects to YOUR existing Chrome instance
- You launch Chrome manually with custom flags
- Clawdbot controls it via the extension, not by launching

**Steps:**

1. **Launch Chrome with stealth flags:**
```bash
# Create a launch script
cat > ~/launch-chrome-stealth.sh << 'EOF'
#!/bin/bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --disable-blink-features=AutomationControlled \
  --disable-automation \
  --disable-dev-shm-usage \
  --user-data-dir="$HOME/.chrome-stealth-profile" \
  --profile-directory=Default
EOF

chmod +x ~/launch-chrome-stealth.sh
```

2. **Run the script:**
```bash
~/launch-chrome-stealth.sh
```

3. **Install Clawdbot extension:**
```bash
clawdbot browser extension install
clawdbot browser extension path
# Load unpacked from this path in chrome://extensions
```

4. **Use the extension profile:**
```bash
clawdbot browser --browser-profile chrome status
```

**Pros:**
- ✅ No Clawdbot modifications needed
- ✅ Full control over Chrome flags
- ✅ Survives Clawdbot updates

**Cons:**
- ❌ Manual Chrome launch required
- ❌ Extension must be manually attached
- ❌ More complex workflow

**Risk:** Low (no system modifications)

---

### Solution 3: Post-Launch CDP Injection (LIMITED EFFECTIVENESS)

**Approach:** After browser launches, inject JavaScript to mask automation

**Implementation:**
```javascript
// Via Playwright after connection
await page.addInitScript(() => {
  Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
  });
  
  // Add more fingerprint spoofing
  window.chrome = {
    runtime: {}
  };
});
```

**How to integrate with Clawdbot:**
- Would require modifying `pw-session.js` or adding a hook
- Not currently exposed via config

**Pros:**
- ✅ Can fix some detection vectors
- ✅ Doesn't require changing launch flags

**Cons:**
- ❌ Only masks some signals (not CDP itself)
- ❌ Still requires code modification
- ❌ Less comprehensive than launch-time fixes

**Risk:** Medium (limited effectiveness)

---

### Solution 4: Request Feature from Clawdbot Maintainers (LONG-TERM)

**Approach:** File a feature request to add `browser.launchOptions.args` config

**Proposed Config:**
```json
{
  "browser": {
    "enabled": true,
    "launchOptions": {
      "args": [
        "--disable-blink-features=AutomationControlled",
        "--disable-automation"
      ]
    }
  }
}
```

**Pros:**
- ✅ Clean, official solution
- ✅ Would benefit all users
- ✅ Maintainable long-term

**Cons:**
- ❌ Requires maintainer buy-in
- ❌ Timeline uncertain
- ❌ Doesn't help immediate problem

**Risk:** None (just a request)

---

## Recommended Implementation Path

### Phase 1: Quick Win (Extension Profile)
Use **Solution 2** immediately to unblock Jupiter trading:

```bash
# 1. Create stealth launch script
cat > ~/launch-chrome-stealth.sh << 'EOF'
#!/bin/bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --disable-blink-features=AutomationControlled \
  --disable-automation \
  --user-data-dir="$HOME/.chrome-jupiter-profile" \
  about:blank
EOF
chmod +x ~/launch-chrome-stealth.sh

# 2. Launch Chrome
~/launch-chrome-stealth.sh

# 3. Load Jupiter extension manually in this Chrome

# 4. Load Clawdbot extension
clawdbot browser extension install
# Go to chrome://extensions, enable Developer mode, Load unpacked

# 5. Test with Clawdbot
clawdbot browser --browser-profile chrome tabs
```

### Phase 2: Robust Solution (Code Patch)
Implement **Solution 1** for long-term reliability:

1. **Backup current installation:**
```bash
sudo cp -r /opt/homebrew/lib/node_modules/clawdbot /opt/homebrew/lib/node_modules/clawdbot.backup
```

2. **Edit chrome.js:**
```bash
sudo nano /opt/homebrew/lib/node_modules/clawdbot/dist/browser/chrome.js
```

3. **Find line ~146** (where args array is defined), add:
```javascript
args.push(
    "--disable-blink-features=AutomationControlled",
    "--disable-automation"
);
```

4. **Restart gateway:**
```bash
clawdbot gateway restart
```

5. **Create update script** to reapply patch after Clawdbot updates:
```bash
cat > ~/patch-clawdbot-stealth.sh << 'EOF'
#!/bin/bash
TARGET="/opt/homebrew/lib/node_modules/clawdbot/dist/browser/chrome.js"
if grep -q "disable-blink-features=AutomationControlled" "$TARGET"; then
    echo "✅ Patch already applied"
else
    echo "Applying stealth patch..."
    # Add patch logic here
fi
EOF
```

---

## Additional Stealth Techniques

### JavaScript Injection (if you go the CDP route)

```javascript
// Complete stealth script
await page.addInitScript(() => {
  // Remove webdriver property
  Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
  });

  // Add chrome object
  window.chrome = {
    runtime: {}
  };

  // Mock permissions
  const originalQuery = window.navigator.permissions.query;
  window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
      Promise.resolve({ state: Notification.permission }) :
      originalQuery(parameters)
  );

  // Hide automation-related properties
  Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5]
  });
  
  Object.defineProperty(navigator, 'languages', {
    get: () => ['en-US', 'en']
  });
});
```

### Chrome Preferences Modifications

Edit `~/.clawdbot/browser/clawd/user-data/Default/Preferences`:

```json
{
  "enable_do_not_track": false,
  "profile": {
    "default_content_setting_values": {
      "notifications": 1
    }
  }
}
```

---

## Testing Automation Detection

### Test URLs:
1. **https://bot.sannysoft.com/** - Comprehensive detection tests
2. **https://arh.antoinevastel.com/bots/areyouheadless** - Headless detection
3. **https://abrahamjuliot.github.io/creepjs/** - Fingerprinting tests
4. **https://pixelscan.net/** - Bot detection

### Test Script:
```bash
# With current setup
clawdbot browser --browser-profile clawd open https://bot.sannysoft.com/
clawdbot browser screenshot --full-page

# With stealth profile
~/launch-chrome-stealth.sh
# Then navigate manually to test sites
```

---

## References

### Clawdbot Code Locations:
- `/opt/homebrew/lib/node_modules/clawdbot/dist/browser/chrome.js` - Chrome launcher
- `/opt/homebrew/lib/node_modules/clawdbot/dist/browser/config.js` - Config parser
- `/opt/homebrew/lib/node_modules/clawdbot/dist/browser/pw-session.js` - Playwright session
- `~/.clawdbot/browser/clawd/user-data/` - Browser profile

### Documentation:
- Clawdbot Browser Tool: `/opt/homebrew/lib/node_modules/clawdbot/docs/tools/browser.md`
- Chrome Extension: `/opt/homebrew/lib/node_modules/clawdbot/docs/tools/chrome-extension.md`

### External Resources:
- Playwright Stealth: https://github.com/berstend/puppeteer-extra/tree/master/packages/puppeteer-extra-plugin-stealth
- Chrome Flags List: https://peter.sh/experiments/chromium-command-line-switches/
- Automation Detection Tests: https://bot.sannysoft.com/

---

## Next Steps

1. ✅ **IMMEDIATE:** Test Solution 2 (Extension Profile) with Jupiter
2. ⏳ **SHORT-TERM:** Implement Solution 1 (Code Patch) if extension works
3. 📋 **LONG-TERM:** File feature request with Clawdbot for config-based launch args
4. 🧪 **VALIDATION:** Run comprehensive detection tests on https://bot.sannysoft.com/

---

## Risk Assessment

| Solution | Effectiveness | Complexity | Risk | Maintenance |
|----------|--------------|------------|------|-------------|
| Extension Profile | 🟢 High | 🟡 Medium | 🟢 Low | 🟢 Low |
| Code Patch | 🟢 High | 🟠 Medium-High | 🟡 Medium | 🟠 Medium |
| CDP Injection | 🟡 Medium | 🟠 High | 🟡 Medium | 🟠 Medium |
| Feature Request | 🟢 High | 🟢 Low | 🟢 None | 🟢 None |

**Recommended:** Start with Extension Profile, then implement Code Patch as backup.

---

## Questions?

- Config file location: `~/.clawdbot/clawdbot.json`
- Browser profiles: `~/.clawdbot/browser/`
- Logs: `clawdbot logs`
- Status: `clawdbot browser status`
