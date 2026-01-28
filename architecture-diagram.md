# Chrome Automation Architecture & Solutions

## Current Architecture (PROBLEM)

```
┌─────────────────────────────────────────────────────────────┐
│                      CLAWDBOT AGENT                         │
│                                                             │
│  Agent wants to control Chrome for Jupiter trading         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
         ┌─────────────────────────┐
         │   Browser Tool (agent)  │
         └────────────┬─────────────┘
                      │
                      ↓
      ┌───────────────────────────────────┐
      │  Browser Control Server           │
      │  (http://127.0.0.1:18791)        │
      └───────────────┬───────────────────┘
                      │
                      ↓
      ┌───────────────────────────────────┐
      │  Playwright CDP Connection        │
      │  (connects to Chrome)             │
      └───────────────┬───────────────────┘
                      │
                      ↓
      ┌───────────────────────────────────────────────┐
      │  Chrome Launch (chrome.js)                    │
      │                                               │
      │  Launch flags:                                │
      │  ❌ --remote-debugging-port=18800             │
      │  ❌ --user-data-dir=~/.clawdbot/browser/clawd │
      │  ❌ --no-first-run                            │
      │  ❌ --disable-sync                            │
      │  ⚠️  MISSING: --disable-blink-features=...    │
      │  ⚠️  MISSING: --disable-automation            │
      │                                               │
      │  Result: navigator.webdriver = TRUE           │
      └───────────────┬───────────────────────────────┘
                      │
                      ↓
      ┌───────────────────────────────────────────────┐
      │           CHROME BROWSER                      │
      │                                               │
      │  🚫 Jupiter Wallet: BLOCKED                   │
      │     ERR_BLOCKED_BY_CLIENT                     │
      │     Reason: Automation detected               │
      └───────────────────────────────────────────────┘
```

---

## Solution 1: Extension Profile (WORKAROUND)

```
┌─────────────────────────────────────────────────────────────┐
│                      CLAWDBOT AGENT                         │
│                                                             │
│  Agent wants to control Chrome for Jupiter trading         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
         ┌─────────────────────────┐
         │   Browser Tool (agent)  │
         │   profile="chrome"      │  ← USE CHROME PROFILE
         └────────────┬─────────────┘
                      │
                      ↓
      ┌───────────────────────────────────┐
      │  Browser Control Server           │
      │  (http://127.0.0.1:18791)        │
      └───────────────┬───────────────────┘
                      │
                      ↓
      ┌───────────────────────────────────┐
      │  Chrome Extension Relay           │
      │  (http://127.0.0.1:18792)        │
      │  Connects to manually-launched    │
      │  Chrome via extension             │
      └───────────────┬───────────────────┘
                      │
                      ↓
      ┌───────────────────────────────────────────────┐
      │  YOUR CHROME (Manually Launched)              │
      │                                               │
      │  👤 YOU launched Chrome with:                 │
      │  ✅ --disable-blink-features=AutomationCtrl'd │
      │  ✅ --disable-automation                      │
      │  ✅ --remote-debugging-port=9222              │
      │  ✅ --user-data-dir=$HOME/.chrome-stealth     │
      │                                               │
      │  Result: navigator.webdriver = UNDEFINED      │
      │                                               │
      │  Extensions loaded:                           │
      │  1. Jupiter Wallet (manual)                   │
      │  2. Clawdbot Extension (attached)             │
      └───────────────┬───────────────────────────────┘
                      │
                      ↓
      ┌───────────────────────────────────────────────┐
      │          AUTOMATION SUCCESSFUL                │
      │                                               │
      │  ✅ Jupiter Wallet: WORKING                   │
      │     No automation detected                    │
      └───────────────────────────────────────────────┘

PROS: 
• No Clawdbot modifications
• Full control over Chrome flags
• Can add unlimited stealth measures
• Survives Clawdbot updates

CONS:
• Must manually launch Chrome each time
• Must manually attach extension
```

---

## Solution 2: Code Patch (DIRECT FIX)

```
┌─────────────────────────────────────────────────────────────┐
│                      CLAWDBOT AGENT                         │
│                                                             │
│  Agent wants to control Chrome for Jupiter trading         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
         ┌─────────────────────────┐
         │   Browser Tool (agent)  │
         │   profile="clawd"       │  ← USE CLAWD PROFILE
         └────────────┬─────────────┘
                      │
                      ↓
      ┌───────────────────────────────────┐
      │  Browser Control Server           │
      │  (http://127.0.0.1:18791)        │
      └───────────────┬───────────────────┘
                      │
                      ↓
      ┌───────────────────────────────────┐
      │  Playwright CDP Connection        │
      │  (connects to Chrome)             │
      └───────────────┬───────────────────┘
                      │
                      ↓
      ┌───────────────────────────────────────────────┐
      │  Chrome Launch (chrome.js) ← PATCHED          │
      │                                               │
      │  Launch flags:                                │
      │  ✅ --remote-debugging-port=18800             │
      │  ✅ --user-data-dir=~/.clawdbot/browser/clawd │
      │  ✅ --no-first-run                            │
      │  ✅ --disable-sync                            │
      │  ✅ --disable-blink-features=AutomationCtrl'd │ ← ADDED
      │  ✅ --disable-automation                      │ ← ADDED
      │                                               │
      │  Result: navigator.webdriver = UNDEFINED      │
      └───────────────┬───────────────────────────────┘
                      │
                      ↓
      ┌───────────────────────────────────────────────┐
      │           CHROME BROWSER                      │
      │                                               │
      │  ✅ Jupiter Wallet: WORKING                   │
      │     No automation detected                    │
      └───────────────────────────────────────────────┘

PROS:
• Automatic (fire-and-forget)
• Standard Clawdbot workflow
• No manual launches

CONS:
• Requires sudo
• Lost on Clawdbot updates (must re-patch)
• Modifies system package
```

---

## Detection Mechanisms Explained

```
┌──────────────────────────────────────────────────────────┐
│            WEBSITE AUTOMATION DETECTION                  │
│                                                          │
│  How sites detect bots:                                 │
│                                                          │
│  1. JavaScript Properties                               │
│     if (navigator.webdriver === true) {                 │
│         blockUser(); // BOT DETECTED                    │
│     }                                                   │
│     ↑ Fixed by: --disable-blink-features               │
│                                                          │
│  2. Chrome DevTools Protocol                            │
│     • Detects active CDP connection                     │
│     • Checks for debugger ports                         │
│     ↑ Hard to bypass (CDP is needed for automation)     │
│                                                          │
│  3. Missing Browser Features                            │
│     • window.chrome missing                             │
│     • Permissions API inconsistencies                   │
│     • Plugin fingerprinting                             │
│     ↑ Fixed by: Proper Chrome flags + manual launch     │
│                                                          │
│  4. Behavioral Analysis                                 │
│     • Mouse movement patterns                           │
│     • Typing speed                                      │
│     • Click timing                                      │
│     ↑ Harder to detect with good automation             │
│                                                          │
│  5. TLS Fingerprinting                                  │
│     • TLS handshake analysis                            │
│     • HTTP/2 fingerprinting                             │
│     ↑ Not affected by automation flags                  │
└──────────────────────────────────────────────────────────┘

JUPITER'S DETECTION:
Likely checking #1 (navigator.webdriver) and #3 (missing features)
Our fixes target these directly.
```

---

## File Structure

```
/Users/atlasbuilds/clawd/
├── SUMMARY.md                          ← This summary
├── chrome-automation-fix-findings.md   ← Technical deep dive (12KB)
├── chrome-stealth-quickref.md          ← Quick commands (5KB)
├── fix-chrome-stealth.sh               ← Installer script (6KB)
└── architecture-diagram.md             ← This file

~/.clawdbot/
├── clawdbot.json                       ← Config
└── browser/
    ├── clawd/                          ← Managed profile
    │   └── user-data/                  ← Chrome profile data
    └── chrome-extension/               ← Extension files

/opt/homebrew/lib/node_modules/clawdbot/
└── dist/
    └── browser/
        ├── chrome.js                   ← PATCH TARGET
        ├── config.js
        ├── pw-session.js
        └── extension-relay.js
```

---

## Configuration Options (Current State)

```json
// ~/.clawdbot/clawdbot.json
{
  "browser": {
    "enabled": true,                  // ✅ Configurable
    "controlUrl": "http://...",      // ✅ Configurable
    "defaultProfile": "clawd",       // ✅ Configurable
    "executablePath": "/path/chrome", // ✅ Configurable
    "headless": false,                // ✅ Configurable
    "noSandbox": false,               // ✅ Configurable
    "attachOnly": false,              // ✅ Configurable
    
    // ❌ NOT AVAILABLE:
    "launchOptions": {
      "args": [                       // ❌ NOT IMPLEMENTED
        "--disable-blink-features=AutomationControlled",
        "--disable-automation"
      ]
    },
    
    "profiles": {
      "clawd": {                      // ✅ Can configure
        "cdpPort": 18800,
        "color": "#FF4500"
      },
      "chrome": {                     // ✅ Built-in extension profile
        "driver": "extension",
        "cdpUrl": "http://127.0.0.1:18792",
        "color": "#00AA00"
      }
    }
  }
}
```

---

## Command Flow Comparison

### Standard Clawdbot (Blocked):
```bash
clawdbot browser --browser-profile clawd start
# → Chrome launches with standard flags
# → navigator.webdriver = true
# → Jupiter blocks

clawdbot browser open https://jup.ag/perps
# → ERR_BLOCKED_BY_CLIENT
```

### Solution 1: Extension Profile (Works):
```bash
~/launch-chrome-jupiter.sh
# → Chrome launches with YOUR flags
# → navigator.webdriver = undefined
# → Jupiter works

clawdbot browser --browser-profile chrome tabs
# → Connects to your Chrome via extension
# → Full automation capability

clawdbot browser open https://jup.ag/perps
# → Success! No blocking
```

### Solution 2: Code Patch (Works):
```bash
# After patching chrome.js
clawdbot browser --browser-profile clawd start
# → Chrome launches with PATCHED flags
# → navigator.webdriver = undefined
# → Jupiter works

clawdbot browser open https://jup.ag/perps
# → Success! No blocking
```

---

## Testing Workflow

```
Step 1: Apply Fix
├─ Option A: Extension
│  └─ ./fix-chrome-stealth.sh (choose 1)
│     └─ ~/launch-chrome-jupiter.sh
│        └─ Load extensions
│           └─ Attach Clawdbot
│
└─ Option B: Code Patch
   └─ ./fix-chrome-stealth.sh (choose 2)
      └─ Restart gateway
         └─ Start browser

Step 2: Test Detection
└─ Open: https://bot.sannysoft.com/
   ├─ Check: navigator.webdriver → should be UNDEFINED
   ├─ Check: Chrome driver → should be NOT DETECTED
   └─ Check: Automation → should be NOT DETECTED

Step 3: Test Jupiter
└─ Open: https://jup.ag/perps
   ├─ Check: Wallet loads
   ├─ Check: No ERR_BLOCKED_BY_CLIENT
   └─ Try: Test transaction

Step 4: Production Use
└─ If successful:
   ├─ Document workflow
   ├─ Create automation scripts
   └─ Monitor for any new blocks
```

---

## Decision Matrix

```
┌─────────────────────┬──────────────┬──────────────┬──────────┐
│ Criteria            │ Extension    │ Code Patch   │ Winner   │
├─────────────────────┼──────────────┼──────────────┼──────────┤
│ Stealth Level       │ ⭐⭐⭐⭐⭐   │ ⭐⭐⭐⭐     │ Extension│
│ Ease of Setup       │ ⭐⭐⭐       │ ⭐⭐⭐⭐⭐   │ Patch    │
│ Maintenance         │ ⭐⭐⭐⭐⭐   │ ⭐⭐⭐       │ Extension│
│ Automation Level    │ ⭐⭐⭐       │ ⭐⭐⭐⭐⭐   │ Patch    │
│ Risk Level          │ ⭐⭐⭐⭐⭐   │ ⭐⭐⭐       │ Extension│
│ Flexibility         │ ⭐⭐⭐⭐⭐   │ ⭐⭐         │ Extension│
│ Update Resilience   │ ⭐⭐⭐⭐⭐   │ ⭐           │ Extension│
└─────────────────────┴──────────────┴──────────────┴──────────┘

RECOMMENDATION: Start with Extension, add Patch if needed for convenience
```

---

## Why Phone Works but Desktop Doesn't

```
PHONE (Works):
┌─────────────────────────────┐
│  Clawdbot on Phone          │
│  ↓                          │
│  Uses native automation     │
│  (iOS/Android APIs)         │
│  ↓                          │
│  Jupiter can't detect       │
│  ✅ No CDP                  │
│  ✅ No webdriver flag       │
│  ✅ Real browser            │
└─────────────────────────────┘

DESKTOP (Blocked):
┌─────────────────────────────┐
│  Clawdbot on Desktop        │
│  ↓                          │
│  Uses CDP automation        │
│  (Chrome DevTools Protocol) │
│  ↓                          │
│  Jupiter detects:           │
│  ❌ CDP active              │
│  ❌ webdriver = true        │
│  ❌ Automation signals      │
└─────────────────────────────┘

FIX: Hide the automation signals
```

---

**Created:** 2025-01-27  
**Purpose:** Visual guide to Chrome automation detection & fixes  
**Status:** Ready for implementation
