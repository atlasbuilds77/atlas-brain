# EBADF Patch - Exact Changes

## File: `/opt/homebrew/lib/node_modules/clawdbot/dist/agents/bash-tools.exec.js`

### Change 1: Docker exec spawn (around line 230)
**Find:**
```javascript
                detached: process.platform !== "win32",
```

**Replace with:**
```javascript
                detached: false,
```

### Change 2: PTY fallback spawn (around line 280)
**Find:**
```javascript
                detached: process.platform !== "win32",
```

**Replace with:**
```javascript
                detached: false,
```

### Change 3: Regular shell spawn (around line 330)
**Find:**
```javascript
                detached: process.platform !== "win32",
```

**Replace with:**
```javascript
                detached: false,
```

## Verification
After applying these changes, restart the gateway:
```bash
clawdbot gateway restart
```

## Testing
Test with multiple exec calls:
```bash
clawdbot exec "echo test1"
clawdbot exec "echo test2"
clawdbot exec "echo test3"
clawdbot exec "echo test4"
clawdbot exec "echo test5"
```

All should succeed without EBADF errors.

## Alternative: Complete Patch File
If you want to create a patch file:

```bash
cat > /tmp/ebadf-fix.patch << 'EOF'
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
EOF

# Apply the patch
cd /opt/homebrew/lib/node_modules/clawdbot/dist/agents/
sudo patch -p0 < /tmp/ebadf-fix.patch
```

## Root Cause Explanation
The `detached: true` option on Unix systems causes child processes to run in a new process group. This can lead to file descriptor leaks when stdio streams are not properly managed. After multiple spawns, file descriptors accumulate and eventually cause EBADF (Bad File Descriptor) errors.

Using `detached: false` avoids these issues while still allowing proper process management for the exec tool's use case.