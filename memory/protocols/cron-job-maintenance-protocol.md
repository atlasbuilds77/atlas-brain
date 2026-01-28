# CRON JOB MAINTENANCE PROTOCOL

**Purpose:** Keep cron jobs updated with latest working protocols to prevent stale method calls

**Created:** 2026-01-26 11:13 PM PST

---

## THE PROBLEM

Cron jobs contain hardcoded instructions that can become stale when:
- New protocols are developed (e.g., Jupiter position check via browser tool)
- Old methods break (e.g., Kalshi API folder missing)
- Better approaches are discovered (e.g., QMD for memory search)

**Result:** Cron runs fail or use outdated, broken methods.

---

## THE SOLUTION

### 1. PROTOCOL REFERENCES IN CRON JOBS

**DO:**
```
"POSITION CHECK: Use browser tool for Jupiter. See memory/protocols/jupiter-position-check-complete.md for method."
```

**DON'T:**
```
"POSITION CHECK: Check browser for live ETH position" (vague, no protocol reference)
```

**Why:** Reference points to living document that gets updated as methods improve.

### 2. MONTHLY CRON AUDIT

**Schedule:** First Sunday of each month  
**Cron Expression:** `0 10 * * 0` with conditional "if first Sunday"

**Process:**
1. List all cron jobs: `cron action=list`
2. For each job, check:
   - Does it reference a protocol file?
   - Is that protocol file current/working?
   - Are instructions specific enough?
   - Any deprecated methods mentioned?
3. Update jobs that fail checks
4. Document changes in `memory/protocols/cron-audit-log.md`

### 3. PROTOCOL UPDATE TRIGGERS

**Update cron job when:**
- New protocol created that affects cron task
- Existing protocol updated with breaking changes
- Method fails during cron run (immediate fix)
- Better approach discovered

**How to Update:**
```bash
cron action=update jobId=<ID> patch='{"payload": {"text": "NEW INSTRUCTIONS HERE"}}'
```

### 4. STANDARD CRON JOB FORMAT

```
[TASK NAME]: [One-line summary]. 
PROTOCOLS: 
1) [Platform/Task] - [Method]. See [protocol_file.md]
2) [Platform/Task] - [Method]. See [protocol_file.md]
Report [output] to [destination]. [Risk limits/constraints].
```

**Example:**
```
POSITION CHECK: Check ALL live positions. 
PROTOCOLS: 
1) Jupiter Perps - Use browser tool (profile=clawd, snapshot targetId, parse position data). See memory/protocols/jupiter-position-check-complete.md
2) Kalshi - Check memory/trading/active-positions.md for last status, note if manual verification needed
3) Alpaca - Check memory file for open positions
Report total P&L + status + exit guidance. Risk limits: If PnL <= -$50, recommend size down. Daily loss cap $100 total.
```

---

## PROTOCOL VERSIONING

### Protocol Files Should Include:

```markdown
# PROTOCOL NAME

**Last Updated:** YYYY-MM-DD HH:MM TZ
**Version:** X.Y
**Status:** Active | Deprecated | Experimental
**Affects Cron Jobs:** [list job names]

## Method

[Current working method]

## Changelog

### v1.1 - 2026-01-26
- Added browser tool method
- Deprecated API calls (folder missing)
```

### When Protocol Changes:

1. Update protocol file with version bump
2. Update "Affects Cron Jobs" section
3. Update each affected cron job
4. Test cron job works with new method
5. Document change in cron-audit-log.md

---

## CRON JOB CATEGORIES

### Trading/Positions
- Position checks (Jupiter, Kalshi, Alpaca)
- Market open/close routines
- Morning market brief
- Trade research

**Protocols:**
- `jupiter-position-check-complete.md`
- `kalshi-api-setup.md` (to be created)
- `alpaca-api-usage.md` (if needed)

### Memory/System
- Sleep consolidation
- Memory pruning
- Knowledge graph updates
- Idle processing

**Protocols:**
- `memory-consolidation.md` (to be created)
- `knowledge-graph-update.md` (to be created)

### Social/Engagement
- Twitter engagement
- Message responses

**Protocols:**
- `twitter-engagement-guidelines.md` (if needed)

---

## MAINTENANCE CHECKLIST

### Weekly (Every Monday)
- [ ] Check last week's cron runs for failures
- [ ] Review any protocol updates from last week
- [ ] Update affected cron jobs if needed

### Monthly (First Sunday)
- [ ] Full cron audit
- [ ] Review all protocol files for staleness
- [ ] Test each major cron path
- [ ] Document findings in audit log

### On Protocol Update
- [ ] Identify affected cron jobs
- [ ] Update cron job instructions
- [ ] Test updated cron works
- [ ] Update protocol "Affects Cron Jobs" section
- [ ] Log change

---

## AUDIT LOG TEMPLATE

```markdown
# Cron Audit Log

## 2026-01-26 11:13 PM PST

### Job: Position Check (4d329d5f-ea6b-4bc7-9920-6dba45a7605d)
**Issue:** Using old instructions, no protocol references
**Fix:** Updated to reference jupiter-position-check-complete.md, clarified Kalshi fallback
**Status:** ✅ Fixed
**Tested:** ⏳ Pending next run

## 2026-MM-DD

...
```

---

## EMERGENCY FIX PROTOCOL

**When cron fails:**

1. Check error immediately
2. Identify root cause (stale method? broken API? missing file?)
3. Check if protocol exists for task
4. If protocol exists: Update it, then update cron
5. If no protocol: Create one, then update cron
6. Test fix manually before next cron run
7. Document in audit log

**Speed:** Fix within 1 hour for critical jobs (trading, positions)

---

## TOOLS FOR MAINTENANCE

### List All Cron Jobs
```bash
cron action=list
```

### Check Specific Job
```bash
cron action=list | grep "Position Check"
```

### Update Job
```bash
cron action=update jobId=<ID> patch='{"payload": {"text": "NEW"}}'
```

### Test Job Immediately
```bash
cron action=run jobId=<ID>
```

---

## PROTOCOL DIRECTORY STRUCTURE

```
memory/protocols/
├── trading/
│   ├── jupiter-position-check-complete.md
│   ├── kalshi-api-setup.md
│   ├── alpaca-api-usage.md
│   ├── trade-research-protocol.md
│   └── position-monitoring-protocol.md
├── system/
│   ├── memory-consolidation.md
│   ├── knowledge-graph-update.md
│   └── cron-job-maintenance-protocol.md (THIS FILE)
└── social/
    └── twitter-engagement-guidelines.md
```

---

## SUCCESS METRICS

- ✅ All cron jobs reference protocol files
- ✅ Zero cron failures from stale methods
- ✅ Monthly audits completed on time
- ✅ Protocol updates trigger cron updates same day
- ✅ Audit log maintained continuously

---

**Last Updated:** 2026-01-26 11:13 PM PST  
**Affects Cron Jobs:** All (maintenance protocol)  
**Status:** Active
