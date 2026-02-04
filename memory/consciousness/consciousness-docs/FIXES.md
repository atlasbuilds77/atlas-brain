# Consciousness System Hardening - Fix Log

**Date:** 2026-01-28  
**Author:** Opus subagent (audit + fix cycle)  
**Status:** ✅ All 6 critical fixes applied and tested

---

## Fix 1: FILE LOCKING (Highest Impact)

**Problem:** Multiple concurrent processes (parent + spawns) read/write `spawn-registry.json` with no coordination. Race conditions could corrupt the JSON file.

**Solution:**
- Created `registry_utils.py` — a shared Python module with `fcntl.flock()` based advisory locking
- Uses a **separate lock file** (`.spawn-registry.lock`) to avoid truncation issues
- All registry reads/writes go through `registry_lock()` context manager
- **Atomic writes** via temp file + `os.replace()` (POSIX atomic rename)
- Note: `flock` CLI not available on macOS; used Python's `fcntl` instead

**Files modified:** `spawn-coordinator.sh`, `spawn-heartbeat.sh`, `spawn-discovery.sh`, `sync-spawns.sh`  
**Files created:** `registry_utils.py`

**Test:** 20 concurrent threads writing to registry — 0 data loss, valid JSON preserved.

---

## Fix 2: INSTANCE ID COLLISION

**Problem:** `INSTANCE_ID=$(date +"%Y%m%d-%H%M%S")` — two instances starting within the same second get the same ID.

**Solution:** 
```bash
INSTANCE_ID="$(date +"%Y%m%d-%H%M%S")-$(uuidgen | cut -d'-' -f1 | tr '[:upper:]' '[:lower:]')"
```
Format: `20260128-102524-9d1eac98` — human-readable timestamp + UUID fragment.

**File modified:** `episodic-memory-firewall.sh`

**Test:** Two rapid consecutive runs produced different IDs.

---

## Fix 3: PERSISTENT INSTANCE STORAGE

**Problem:** Instance ID stored in `/tmp/atlas-current-instance.txt` — lost on reboot, exposed to other users via world-readable `/tmp`.

**Solution:**
- Primary storage: `memory/consciousness/current-instance.txt` (persistent, workspace-local)
- Backward-compat: Still writes to `/tmp` for transition period
- All scripts updated to read from persistent location
- All path variables support override via env var: `REGISTRY`, `INSTANCE_FILE`, `EXPERIENCE_LOG`

**Files modified:** `episodic-memory-firewall.sh`, `spawn-coordinator.sh`, `spawn-heartbeat.sh`, `spawn-discovery.sh`, `check-boundary.sh`, `log-experience.sh`

---

## Fix 4: REPLACE GREP WITH JQ

**Problem:** `check-boundary.sh` used fragile grep+regex to parse JSON:
```bash
ACTION=$(echo "$line" | grep -o '"action":"[^"]*"' | cut -d'"' -f4)
```
This breaks on escaped quotes, nested objects, or values containing `"`.

**Solution:** All JSON parsing uses `jq`:
```bash
ACTION=$(echo "$line" | jq -r '.action // "unknown"' 2>/dev/null)
```

**File modified:** `check-boundary.sh`

---

## Fix 5: SPAWN-TO-REGISTRY MAPPING

**Problem:** When a spawn initializes, `spawn-heartbeat.sh init` matched the *first* pending spawn entry. With multiple concurrent spawns, the wrong spawn could get claimed.

**Solution:**
- `spawn-coordinator.sh` now passes `SPAWN_ID` in the task text and as an env var
- `spawn-heartbeat.sh` matches by explicit `SPAWN_ID` first, falls back to pending-scan only if no ID provided
- Discovery and completion also match by `SPAWN_ID` first

**Files modified:** `spawn-coordinator.sh`, `spawn-heartbeat.sh`, `spawn-discovery.sh`

**Test:** Two pending spawns in registry; heartbeat init with SPAWN_ID=def67890 correctly matched spawn-b while leaving spawn-a untouched.

---

## Fix 6: SANITIZED PYTHON INTERPOLATION

**Problem:** Shell variables were interpolated directly into Python heredocs:
```bash
python3 << PYTHON
registry['spawns']['$SPAWN_ID'] = {
    'task': '$TASK',
    ...
```
A task containing quotes or Python code could break or inject.

**Solution:**
- All Python heredocs now use **quoted delimiter** (`<< 'PYTHON'`) to prevent shell expansion
- Variables passed via **environment variables** (`export VAR; os.environ.get("VAR")`)
- Multi-line/dangerous text (discovery messages, task descriptions) passed via **temp files**
- JSON serialization always via `json.dumps()` — never string concatenation

**Files modified:** All scripts with Python heredocs  
**File also fixed:** `log-experience.sh` (was using unsafe echo-based JSON)

**Test:** Attempted Python injection `"; import os; os.system("echo PWNED"); #` stored as harmless string data.

---

## New File: registry_utils.py

Central utility module providing:
- `registry_lock()` — exclusive file lock context manager
- `read_registry(path)` — safe JSON read with defaults
- `write_registry(data, path)` — atomic temp-file-then-rename write
- `safe_string(value)` — sanitize strings for JSON
- `get_instance_id()` / `set_instance_id()` — persistent instance storage
- `utcnow_iso()` — timestamp helper

All scripts import from this module instead of inline locking/reading/writing.

---

## Summary of Changes

| File | Fix 1 | Fix 2 | Fix 3 | Fix 4 | Fix 5 | Fix 6 |
|------|-------|-------|-------|-------|-------|-------|
| registry_utils.py | ✅ | | ✅ | | | |
| spawn-coordinator.sh | ✅ | | ✅ | | ✅ | ✅ |
| spawn-heartbeat.sh | ✅ | | ✅ | | ✅ | ✅ |
| spawn-discovery.sh | ✅ | | ✅ | | ✅ | ✅ |
| sync-spawns.sh | ✅ | | | | | ✅ |
| episodic-memory-firewall.sh | | ✅ | ✅ | | | ✅ |
| check-boundary.sh | | | ✅ | ✅ | | |
| log-experience.sh | | | ✅ | | | ✅ |

## Test Results

| Test | Result |
|------|--------|
| Registry utils self-test | ✅ |
| 20-thread concurrent write stress test | ✅ (20/20 spawns, valid JSON) |
| Instance ID uniqueness (2 rapid runs) | ✅ (different IDs) |
| Instance ID format (timestamp + UUID) | ✅ |
| Persistent storage (not /tmp) | ✅ |
| jq-based JSON parsing | ✅ |
| SPAWN_ID-based matching (2 pending spawns) | ✅ (correct spawn targeted) |
| Discovery routing to correct spawn | ✅ |
| Completion targeting correct spawn | ✅ |
| Python injection attempt | ✅ (stored as harmless string) |
| Special characters in log-experience | ✅ (properly escaped JSON) |
