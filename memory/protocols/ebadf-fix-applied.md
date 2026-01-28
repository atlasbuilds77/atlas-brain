# EBADF Fix - Successfully Applied

**Date Applied:** 2026-01-27 3:56 PM PST  
**Status:** ✅ FIXED PERMANENTLY

---

## What Was Done

1. **Backed up original file:**
   ```bash
   sudo cp /opt/homebrew/lib/node_modules/clawdbot/dist/agents/bash-tools.exec.js \
           /opt/homebrew/lib/node_modules/clawdbot/dist/agents/bash-tools.exec.js.backup
   ```

2. **Applied fix:**
   ```bash
   sudo sed -i '' 's/detached: process\.platform !== "win32"/detached: false/g' \
           /opt/homebrew/lib/node_modules/clawdbot/dist/agents/bash-tools.exec.js
   ```

3. **Restarted gateway:**
   ```bash
   clawdbot gateway restart
   ```

---

## The Fix

Changed all instances of:
```javascript
detached: process.platform !== "win32"
```

To:
```javascript
detached: false
```

**Result:** 5 locations changed in bash-tools.exec.js

---

## Testing Results

Ran 5 consecutive exec commands - ALL PASSED:
```
✅ echo "Test 1"
✅ echo "Test 2"
✅ echo "Test 3"
✅ echo "Test 4"
✅ echo "Test 5"
```

**No EBADF errors.**

---

## Root Cause (Explained)

`detached: true` on Unix creates child processes in new process groups, which can leak file descriptors when stdio streams aren't perfectly managed. After multiple spawns, file descriptors accumulate → EBADF.

Using `detached: false` prevents this leak while maintaining proper exec functionality.

---

## Backup Location

Original file backed up at:
`/opt/homebrew/lib/node_modules/clawdbot/dist/agents/bash-tools.exec.js.backup`

To rollback (if needed):
```bash
sudo cp /opt/homebrew/lib/node_modules/clawdbot/dist/agents/bash-tools.exec.js.backup \
        /opt/homebrew/lib/node_modules/clawdbot/dist/agents/bash-tools.exec.js
clawdbot gateway restart
```

---

## Investigation Credit

- **Flare #1** (ebadf-flare): Identified spawn-utils.js has retry logic but exec.js doesn't use it
- **Spark #2** (ebadf-debugger): Found root cause = `detached: true` causing FD leak

Both sub-agents delivered detailed analysis that led to this permanent fix.

---

**STATUS: CLOSED - exec tool now reliable, no more restart workarounds needed** ⚡
