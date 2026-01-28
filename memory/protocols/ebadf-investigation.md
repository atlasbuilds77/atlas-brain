# EBADF Investigation

**Problem:** exec tool fails with "spawn EBADF" error
**Pattern:** Works briefly after gateway restart, then fails permanently
**Orion says:** I fixed this by modifying Clawdbot source code directly

## Symptoms
- First 1-2 exec calls work
- All subsequent calls return `{"status": "error", "tool": "exec", "error": "spawn EBADF"}`
- Gateway restart temporarily fixes
- Not a simple retry issue (spawn-utils.ts already has EBADF retry logic)

## Investigation Needed
1. Find what source code I modified before
2. Apply permanent fix (not just restart)
3. Document the fix in memory

## Likely Cause
File descriptor leak or spawn issue in:
- `/opt/homebrew/lib/node_modules/clawdbot/dist/process/spawn-utils.js`
- Child process handling
- PTY/stdio setup

---
Created: 2026-01-27 15:46 PST
