# Complete EBADF Fix for Clawdbot

## Problem Summary
The exec tool fails with "spawn EBADF" error after 1-2 successful calls, requiring gateway restart. Error: "spawn EBADF syscall=spawn errno=-9".

## Root Causes
1. **Primary Cause**: Using `detached: true` on Unix systems causes file descriptor leaks
2. **Secondary Cause**: Incomplete cleanup of stdio streams (stdout, stderr not destroyed)
3. **Tertiary Cause**: File descriptors accumulate until EBADF occurs

## Complete Solution

### Part 1: Fix `detached` option (Primary Fix)
Change all `detached: process.platform !== "win32"` to `detached: false` in `/opt/homebrew/lib/node_modules/clawdbot/dist/agents/bash-tools.exec.js`

**Three locations to change:**
1. Line ~230 (docker exec spawn)
2. Line ~280 (PTY fallback spawn)  
3. Line ~330 (regular shell spawn)

### Part 2: Add proper stream cleanup (Secondary Fix)
Add code to properly destroy all stdio streams when child process exits.

In `bash-tools.exec.js`, in the `handleExit` function, add:

```javascript
// After markExited call, add:
if (session.child) {
    // Destroy all stdio streams
    if (session.child.stdin) session.child.stdin.destroy();
    if (session.child.stdout) session.child.stdout.destroy();
    if (session.child.stderr) session.child.stderr.destroy();
}
```

### Part 3: Apply the patch

#### Option A: Manual edit
1. Backup the file:
   ```bash
   sudo cp /opt/homebrew/lib/node_modules/clawdbot/dist/agents/bash-tools.exec.js /opt/homebrew/lib/node_modules/clawdbot/dist/agents/bash-tools.exec.js.backup
   ```

2. Edit the file with `sudo nano` or `sudo vim` and make the changes above.

3. Restart gateway:
   ```bash
   clawdbot gateway restart
   ```

#### Option B: Use patch file
```bash
# Create patch file
cat > /tmp/ebadf-complete-fix.patch << 'EOF'
--- bash-tools.exec.js.orig
+++ bash-tools.exec.js.fixed
@@ -227,7 +227,7 @@
             options: {
                 cwd: opts.workdir,
                 env: process.env,
-                detached: process.platform !== "win32",
+                detached: false,
                 stdio: ["pipe", "pipe", "pipe"],
                 windowsHide: true,
             },
@@ -277,7 +277,7 @@
             options: {
                 cwd: opts.workdir,
                 env: opts.env,
-                detached: process.platform !== "win32",
+                detached: false,
                 stdio: ["pipe", "pipe", "pipe"],
                 windowsHide: true,
             },
@@ -327,7 +327,7 @@
             options: {
                 cwd: opts.workdir,
                 env: opts.env,
-                detached: process.platform !== "win32",
+                detached: false,
                 stdio: ["pipe", "pipe", "pipe"],
                 windowsHide: true,
             },
@@ -450,6 +450,12 @@
             const durationMs = Date.now() - startedAt;
             const wasSignal = exitSignal != null;
             const isSuccess = code === 0 && !wasSignal && !timedOut;
             const status = isSuccess ? "completed" : "failed";
             markExited(session, code, exitSignal, status);
+            // Destroy stdio streams to prevent file descriptor leaks
+            if (session.child) {
+                if (session.child.stdin) session.child.stdin.destroy();
+                if (session.child.stdout) session.child.stdout.destroy();
+                if (session.child.stderr) session.child.stderr.destroy();
+            }
             maybeNotifyOnExit(session, status);
EOF

# Apply patch
cd /opt/homebrew/lib/node_modules/clawdbot/dist/agents/
sudo patch -p0 < /tmp/ebadf-complete-fix.patch
```

## Testing Procedure
1. After applying fix, restart gateway
2. Run multiple exec commands:
   ```bash
   for i in {1..10}; do clawdbot exec "echo Test $i"; done
   ```
3. Check logs for EBADF errors:
   ```bash
   grep -i ebadf /tmp/clawdbot/clawdbot-*.log
   ```
4. Monitor file descriptor usage:
   ```bash
   lsof -p $(pgrep -f "clawdbot.*gateway") | wc -l
   ```

## Expected Results
- No EBADF errors in logs
- File descriptor count stable (not continuously increasing)
- Exec tool works reliably without requiring gateway restart

## Fallback Mechanism
The existing fallback to `detached: false` when EBADF occurs will still work as a safety measure, but with the fix applied, it should never be triggered.

## Notes
- The fix changes from `detached: true` to `detached: false` on Unix
- This is acceptable for the exec tool as it doesn't need detached processes
- Proper stream destruction ensures no file descriptor leaks
- Gateway restart required after applying fix