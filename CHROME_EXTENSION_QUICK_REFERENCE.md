# Chrome Extension Relay - Quick Reference

## Installation (One-Time Setup)

```bash
# 1. Install extension files
clawdbot browser extension install

# 2. Get extension path
clawdbot browser extension path

# 3. Chrome → chrome://extensions → Enable Developer mode → Load unpacked
# 4. Select the directory from step 2
# 5. Pin extension to toolbar
```

## Daily Usage

### Attaching a Tab
1. Open Chrome tab you want to control
2. Click **Clawdbot Browser Relay** toolbar icon
3. Badge shows `ON` when attached
4. Click again to detach

### CLI Commands
```bash
# List attached tabs
clawdbot browser --browser-profile chrome tabs

# Open URL in attached browser
clawdbot browser --browser-profile chrome open https://example.com

# Take snapshot (for UI automation)
clawdbot browser --browser-profile chrome snapshot

# Take screenshot
clawdbot browser --browser-profile chrome screenshot

# Click element (ref from snapshot)
clawdbot browser --browser-profile chrome click 12

# Type text
clawdbot browser --browser-profile chrome type 23 "hello"
```

### Agent Tool Usage
```javascript
// Always use profile="chrome"
browser({
  action: "snapshot",
  profile: "chrome"
})

// For actions
browser({
  action: "act",
  profile: "chrome",
  request: {
    kind: "click",
    ref: "12"  // from snapshot
  }
})
```

## Troubleshooting

### Badge States
- `ON` = Connected ✓
- `…` = Connecting
- `!` = Relay not reachable

### Common Fixes

**Extension shows `!`:**
```bash
# Check Gateway status
clawdbot gateway status

# Start Gateway if needed
clawdbot gateway start
```

**"No attached tabs" error:**
- Click extension icon on the tab
- Badge must show `ON`

**After Clawdbot upgrade:**
```bash
clawdbot browser extension install
# Then reload extension in chrome://extensions
```

## Configuration Notes

### Default Config (usually works)
```json5
{
  browser: {
    enabled: true,
    defaultProfile: "chrome"  // Built-in extension profile
  }
}
```

### Sandboxed Sessions
If agent is sandboxed, add to config:
```json5
{
  agents: {
    defaults: {
      sandbox: {
        browser: {
          allowHostControl: true
        }
      }
    }
  }
}
```

Then use `target="host"` in browser tool calls.

## Security Reminder
⚠️ Extension gives agent full control of attached tabs
- Use separate Chrome profile for agent work
- Only attach tabs intentionally
- Detach when done
- Never expose control server publicly

## Remote Setup (Gateway on different machine)

**On browser machine:**
```bash
clawdbot browser serve --bind 127.0.0.1 --port 18791 --token <token>
```

**On Gateway machine config:**
```json5
{
  browser: {
    controlUrl: "http://browser-machine:18791",
    controlToken: "<token>"
  }
}
```

---

*Keep this reference in your workspace for quick access*
*Full guide: CHROME_EXTENSION_RELAY_GUIDE.md*