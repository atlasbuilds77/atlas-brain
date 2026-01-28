# EBADF Fix Protocol - PERMANENT SOLUTION

## Problem
`exec` tool dies with "spawn EBADF" after 1-2 calls due to file descriptor exhaustion.

## Root Cause Analysis

### Key Files Examined:
1. `/opt/homebrew/lib/node_modules/clawdbot/dist/process/spawn-utils.js`
2. `/opt/homebrew/lib/node_modules/clawdbot/dist/process/exec.js`

### The Bug:
**`spawn-utils.js` has EBADF retry logic but `exec.js` doesn't use it!**

In `spawn-utils.js`:
```javascript
const DEFAULT_RETRY_CODES = ["EBADF"];  // <-- EBADF retry is built-in!

export async function spawnWithFallback(params) {
    // ... retry logic for EBADF errors
}
```

In `exec.js` (line ~53):
```javascript
// PROBLEM: Uses raw spawn() instead of spawnWithFallback()
const child = spawn(argv[0], argv.slice(1), {
    stdio,
    cwd,
    env: resolvedEnv,
    windowsVerbatimArguments,
});
```

---

## PERMANENT FIX

### File: `/opt/homebrew/lib/node_modules/clawdbot/dist/process/exec.js`

### Change 1: Add import (line 1-2)

**BEFORE:**
```javascript
import { execFile, spawn } from "node:child_process";
```

**AFTER:**
```javascript
import { execFile } from "node:child_process";
import { spawnWithFallback } from "./spawn-utils.js";
```

### Change 2: Replace spawn() call (~line 50-58)

**BEFORE:**
```javascript
    const stdio = resolveCommandStdio({ hasInput, preferInherit: true });
    const child = spawn(argv[0], argv.slice(1), {
        stdio,
        cwd,
        env: resolvedEnv,
        windowsVerbatimArguments,
    });
```

**AFTER:**
```javascript
    const stdio = resolveCommandStdio({ hasInput, preferInherit: true });
    const { child } = await spawnWithFallback({
        argv,
        options: {
            stdio,
            cwd,
            env: resolvedEnv,
            windowsVerbatimArguments,
        },
        fallbacks: [
            { label: "pipe-stdio", options: { stdio: ["pipe", "pipe", "pipe"] } },
        ],
    });
```

---

## Quick Apply (One-liner patch)

```bash
# Backup first
cp /opt/homebrew/lib/node_modules/clawdbot/dist/process/exec.js \
   /opt/homebrew/lib/node_modules/clawdbot/dist/process/exec.js.bak

# Apply fix (use sed or manual edit)
```

---

## Alternative Hotfix (if full fix is too invasive)

Add try-catch with retry around the spawn call:

```javascript
async function spawnWithRetry(argv, options, maxRetries = 3) {
    for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
            const child = spawn(argv[0], argv.slice(1), options);
            await new Promise((resolve, reject) => {
                child.once('spawn', resolve);
                child.once('error', reject);
            });
            return child;
        } catch (err) {
            if (err.code === 'EBADF' && attempt < maxRetries - 1) {
                await new Promise(r => setTimeout(r, 100 * (attempt + 1)));
                continue;
            }
            throw err;
        }
    }
}
```

---

## Why This Happens

EBADF = "Bad File Descriptor"
- Node.js spawn() inherits file descriptors from parent process
- If FDs are closed/invalid during spawn, EBADF occurs
- Usually caused by rapid spawn/close cycles or FD leaks
- The existing `spawn-utils.js` retry logic handles this gracefully

---

## Verification

After applying fix, test with rapid exec calls:
```bash
# Should no longer fail with EBADF
for i in {1..10}; do echo "test $i"; done
```

---

## Status
- [x] Root cause identified
- [x] Fix documented
- [ ] Awaiting application to clawdbot source

**Report:** Ready to apply fix. The issue is that `exec.js` bypasses the existing EBADF retry logic in `spawn-utils.js`.
