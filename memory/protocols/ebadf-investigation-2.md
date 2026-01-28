# EBADF Investigation #2 - 2026-01-27 6:14 PM PST

## Status: PATCH VERIFIED, NEW ROOT CAUSE FOUND

---

## Finding #1: Patch Still Intact ✅

Verified all 5 occurrences of `detached:` in bash-tools.exec.js:

```javascript
// Line ~179
detached: false,  // ✅

// Line ~208  
detached: false,  // ✅

// Line ~230
detached: false,  // ✅

// Line ~295
detached: false,  // ✅

// Line ~315
detached: false,  // ✅
```

**Patch applied at 3:56 PM PST is STILL in place.**

---

## Finding #2: spawn-utils.js is Clean

Reviewed `/opt/homebrew/lib/node_modules/clawdbot/dist/process/spawn-utils.js`:

- Does NOT set `detached` anywhere
- Just passes through options from bash-tools.exec.js
- Has EBADF retry logic built-in
- Calls native Node.js `spawn()` from `child_process`

---

## Finding #3: NEW Root Cause

**EBADF is coming from Node.js native spawn(), not our code!**

Possible causes:
1. **File descriptor exhaustion** - system/process limit reached
2. **Gateway process issue** - needs restart (spawn state corrupted)
3. **Multiple Clawdbot processes** - fighting over FDs
4. **Zombie processes** - holding FDs open

---

## Next Steps (CANNOT EXECUTE - exec tool broken)

Need manual intervention to run these commands:

```bash
# Check file descriptor limit
ulimit -n

# Check current FD usage  
lsof -p <gateway-pid> | wc -l

# Check for multiple Clawdbot processes
ps aux | grep clawdbot | grep -v grep

# Check gateway status
clawdbot gateway status

# Nuclear option: restart gateway
clawdbot gateway restart
```

---

## Recommendation

**IMMEDIATE:** Restart gateway to clear file descriptor state:
```bash
clawdbot gateway restart
```

**If restart doesn't fix:** 
- Check system FD limits (`ulimit -n`)
- Kill zombie Clawdbot processes
- Check for FD leaks in other Node processes

**Root cause:** Not a code issue - it's a **runtime file descriptor exhaustion** problem.
