# Chrome Extension Relay Setup Guide

## Overview

The Clawdbot Chrome extension relay allows the agent to control your **existing Chrome tabs** (your normal Chrome browser) instead of launching a separate, isolated browser profile. This is useful when you want the agent to interact with websites where you're already logged in or have specific session data.

## Key Concepts

- **`clawd` profile**: Isolated, managed browser (separate Chrome instance)
- **`chrome` profile**: Extension relay to your system browser (requires Chrome extension)
- **Profile selection**: Use `profile="chrome"` in the browser tool to control your existing Chrome tabs

## Prerequisites

1. Clawdbot installed and running
2. Chrome browser installed (or any Chromium-based browser: Brave, Edge, etc.)
3. Gateway running on the same machine as Chrome (for local setup)

## Step-by-Step Installation Guide

### Step 1: Install the Chrome Extension Files

Run the built-in installer to copy extension files to a stable location:

```bash
clawdbot browser extension install
```

This copies the extension files to your Clawdbot state directory.

### Step 2: Get the Extension Path

Check where the extension was installed:

```bash
clawdbot browser extension path
```

This will print something like:
```
/Users/yourusername/.clawdbot/browser-extension/1.2.3/
```

### Step 3: Load the Extension in Chrome

1. Open Chrome and go to `chrome://extensions`
2. Enable **"Developer mode"** (toggle in top-right corner)
3. Click **"Load unpacked"** button
4. Navigate to and select the directory printed in Step 2
5. **Pin the extension** to your toolbar for easy access

### Step 4: Verify Gateway is Running

For local setup (Gateway on same machine as Chrome), ensure the Gateway is running:

```bash
clawdbot gateway status
```

If not running, start it:

```bash
clawdbot gateway start
```

### Step 5: Attach a Tab for Control

1. Open the Chrome tab you want Clawdbot to control
2. Click the **Clawdbot Browser Relay** extension icon in your toolbar
3. The badge should show **`ON`** when successfully attached
4. To detach, click the extension icon again

**Important**: The extension only controls tabs you explicitly attach. It does NOT auto-attach to all tabs.

## Configuration

### Default Configuration

Clawdbot ships with a built-in `chrome` profile that targets the extension relay. No additional configuration is needed for basic usage.

### Custom Profile (Optional)

If you want a custom name or different relay port, create your own profile:

```bash
clawdbot browser create-profile \
  --name my-chrome \
  --driver extension \
  --cdp-url http://127.0.0.1:18792 \
  --color "#00AA00"
```

### Browser Configuration File

The browser settings live in `~/.clawdbot/clawdbot.json`. Default browser configuration:

```json5
{
  browser: {
    enabled: true,
    controlUrl: "http://127.0.0.1:18791",
    defaultProfile: "chrome",  // Uses extension relay by default
    profiles: {
      clawd: { cdpPort: 18800, color: "#FF4500" },
      // 'chrome' profile is built-in for extension relay
    }
  }
}
```

## Usage

### Command Line Interface

```bash
# List tabs in your attached Chrome browser
clawdbot browser --browser-profile chrome tabs

# Open a new tab
clawdbot browser --browser-profile chrome open https://example.com

# Take a snapshot of the current page
clawdbot browser --browser-profile chrome snapshot

# Take a screenshot
clawdbot browser --browser-profile chrome screenshot
```

### Agent Tool Usage

When using the `browser` tool in the agent, always specify `profile="chrome"`:

```javascript
// Example agent tool call
browser({
  action: "snapshot",
  profile: "chrome"
})
```

Or for actions:

```javascript
browser({
  action: "act",
  profile: "chrome",
  request: {
    kind: "click",
    ref: "12"  // ref from snapshot
  }
})
```

## Troubleshooting

### Extension Badge States

- **`ON`**: Successfully attached and connected to relay
- **`…`**: Connecting to local relay
- **`!`**: Relay not reachable (most common issue)

### Common Issues & Solutions

#### 1. Extension shows `!` (Relay not reachable)

**Cause**: Browser relay server isn't running on your machine.

**Solutions**:
- Ensure Gateway is running: `clawdbot gateway status`
- If Gateway is remote, run `clawdbot browser serve` locally (see Remote Setup below)
- Check extension Options page for connection status

#### 2. "No attached tabs" error

**Cause**: No tab has been attached via the extension toolbar button.

**Solution**:
- Open the tab you want to control
- Click the Clawdbot Browser Relay extension icon
- Verify badge shows `ON`

#### 3. Sandboxed sessions can't access host browser

**Cause**: By default, sandboxed sessions target the sandbox browser, not host Chrome.

**Solutions**:
- Use a non-sandboxed session for extension relay
- Or enable host browser control in config:

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

#### 4. Extension needs reloading after Clawdbot upgrade

**Solution**:
- Re-run: `clawdbot browser extension install`
- Chrome → `chrome://extensions` → Click "Reload" on the extension

## Remote Gateway Setup

If your Gateway runs on a different machine than Chrome:

### On the Browser Machine (where Chrome runs):

```bash
# Start browser control server
clawdbot browser serve --bind 127.0.0.1 --port 18791 --token <your-token>

# Optional: Publish via Tailscale Serve for HTTPS
tailscale serve https / http://127.0.0.1:18791
```

### On the Gateway Machine:

Set `browser.controlUrl` to point to the browser machine:

```json5
{
  browser: {
    enabled: true,
    controlUrl: "http://browser-machine:18791",  # or HTTPS Tailscale URL
    controlToken: "<your-token>"
  }
}
```

Or set token via environment variable:
```bash
export CLAWDBOT_BROWSER_CONTROL_TOKEN="<your-token>"
```

## Security Considerations

⚠️ **Important**: The Chrome extension relay gives the agent direct control over your browser tabs. This is powerful but risky:

1. **Not isolated**: The agent can access whatever the tab's logged-in session can access
2. **Use dedicated profile**: Consider using a separate Chrome profile for agent control
3. **Keep control server private**: Never expose `browser.controlUrl` to public internet
4. **Use tokens**: Always use authentication tokens for remote control
5. **Tailnet-only**: Prefer Tailscale for remote access over public exposure

## Best Practices

1. **Dedicated Chrome Profile**: Create a separate Chrome profile for agent work
2. **Explicit Attachment**: Only attach tabs you intend to control
3. **Detach When Done**: Click extension icon to detach when finished
4. **Monitor Activity**: Keep an eye on what the agent is doing with your browser
5. **Regular Updates**: Reinstall extension after Clawdbot upgrades

## Reference: Browser Tool Parameters

When using the `browser` tool for Chrome extension relay:

```javascript
// Required: profile="chrome"
browser({
  action: "snapshot",
  profile: "chrome",  // ← This is crucial
  target: "host",     // Required for sandboxed sessions with allowHostControl
  // ... other parameters
})
```

## Maintenance

### Updating the Extension

After upgrading Clawdbot:
```bash
clawdbot browser extension install
```
Then reload the extension in Chrome.

### Checking Extension Status

```bash
# Check browser status
clawdbot browser --browser-profile chrome status

# List available tabs
clawdbot browser --browser-profile chrome tabs
```

## Additional Resources

- [Official Chrome Extension Documentation](/tools/chrome-extension)
- [Browser Tool Documentation](/tools/browser)
- [Security Guidelines](/gateway/security)
- [Remote Access Setup](/gateway/remote)

---

*Last Updated: Based on Clawdbot documentation review*
*Documentation Source: `/opt/homebrew/lib/node_modules/clawdbot/docs/`*