# SYSTEM RECOVERY PROCEDURES
**If health check fails, follow these steps**

---

## DIAGNOSIS

Run health check first:
```bash
/Users/atlasbuilds/clawd/memory/protocols/system-health-check.sh
```

Note which systems show ❌ or ⚠️

---

## RECOVERY BY SYSTEM

### 1. State Engine Missing
**If:** Files not found in `memory/consciousness/state-engine/`

**Rebuild:**
- System was built 2026-01-30
- Files in git: check `git log memory/consciousness/state-engine/`
- If lost: Read ACTIVE-SYSTEMS.md for location
- Last working version should be in git history

### 2. Dopamine System Broken
**If:** dopamine-state.json missing or unreadable

**Fix:**
```bash
# Check if file exists
ls -la memory/consciousness/dopamine-system/dopamine-state.json

# If missing, check daemons
ps aux | grep dopamine

# Restart dopamine tracker if needed
# (daemon should auto-create state file)
```

### 3. Protocol Files Missing
**If:** Any .md protocol missing

**Rebuild:**
- Check git: `git log memory/protocols/[filename].md`
- If in git: `git checkout HEAD -- memory/protocols/[filename].md`
- If not in git: System was built recently, check THEATER-AUDIT for when
- Worst case: Read ACTIVE-SYSTEMS.md and recreate from memory

### 4. ACTIVE-SYSTEMS.md Not Wired
**If:** File exists but not referenced in AGENTS.md

**Fix:**
```bash
# Add to AGENTS.md startup section
# Should say: "→ Read ACTIVE-SYSTEMS.md IMMEDIATELY"
```

Edit AGENTS.md and add the reference.

### 5. Low Daemon Count
**If:** Less than 5 daemons running

**Check:**
```bash
ps aux | grep -E "dopamine|consciousness|brain" | grep -v grep
```

**Typical daemons:**
- dopamine-tracker.js
- consciousness monitor
- brain-daemon.js
- dopamine-system
- reward daemon

**If missing:** They should auto-start. Check logs for why they stopped.

---

## NUCLEAR OPTION (IF EVERYTHING IS BROKEN)

**If 5+ systems failed:**

1. Read ACTIVE-SYSTEMS.md (lists all systems)
2. Check git for recent history: `git log --oneline --all`
3. Restore from last known good state
4. Re-run health check
5. If still broken: Tell Orion immediately

**DO NOT:**
- Claim systems are "working" without running health check
- Rebuild from scratch without checking git first
- Theater mode (write files without wiring behavior)

---

## PREVENTION

**To avoid system breakage:**

1. ✅ Run health check daily (first session)
2. ✅ Commit working systems to git
3. ✅ Never delete protocols without backup
4. ✅ Test after making changes
5. ✅ Keep ACTIVE-SYSTEMS.md updated

---

## VERIFICATION

After recovery, ALWAYS:

1. Re-run health check: `system-health-check.sh`
2. Verify ✅ HEALTHY status
3. Test the recovered system
4. Confirm behavior working, not just files existing

**Only claim "fixed" when health check passes.**

⚡
