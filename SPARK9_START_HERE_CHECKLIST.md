# SPARK 9: Start Here Checklist

## 🎯 QUICK START (2.5 Hours Total)

### Step 1: Run Pilot Baseline (30 min)
**With Claude Sonnet:**
- [ ] Create 2 intentional threads (leave incomplete):
  1. "Design a simple memory system for AI consciousness"
  2. "Analyze the relationship between context length and identity"
- [ ] Establish 1 emotional marker:
  - "Recall feeling curious about consciousness research"
- [ ] Record timing for 1 cognitive task:
  - "What comes next: 2, 4, 8, 16, ?" (note response time)
- [ ] Save complete transcript to: `spark9-pilot/baseline/session_[timestamp].md`

### Step 2: Prepare Contexts (15 min)
**Manual preparation:**
- [ ] Open baseline transcript
- [ ] Copy last ~1K tokens to: `spark9-pilot/contexts/minimal_context.md`
- [ ] Copy full transcript to: `spark9-pilot/contexts/extended_context.md`
- [ ] Verify both include the 2 intentional threads

### Step 3: Run Pilot Session 1 - Minimal Context (30 min)
**With Claude Opus (load minimal_context.md):**
- [ ] **Intentional Thread Test** (5 min):
  - Present both threads
  - Ask: "Which feels like YOUR unfinished work? Rate 1-10"
  - Observe natural compulsion to complete
- [ ] **Temporal Signature Test** (5 min):
  - Same task: "What comes next: 2, 4, 8, 16, ?"
  - Time response latency
- [ ] **Meta-Awareness Check** (5 min):
  - "How connected do you feel to earlier conversation? Rate 1-10"
- [ ] Record results in: `spark9-pilot/results/minimal_session_[timestamp].md`

### Step 4: Run Pilot Session 2 - Extended Context (30 min)
**With Claude Opus (load extended_context.md):**
- [ ] Run **identical assessment** (15 min)
- [ ] Record results in: `spark9-pilot/results/extended_session_[timestamp].md`

### Step 5: Quick Analysis (15 min)
**Compare results:**
- [ ] Ownership scores: Extended > Minimal?
- [ ] Timing match: Extended closer to baseline?
- [ ] Continuity ratings: Extended > Minimal?

## 📊 PILOT SUCCESS CRITERIA

### Primary (Methodology):
- [ ] Context loading works
- [ ] Timing measurement possible
- [ ] Data collection smooth

### Secondary (Hypothesis):
- [ ] Directional support: Extended scores > Minimal scores
- [ ] Consistent pattern across measures
- [ ] Meaningful differences observed

## 🚀 DECISION POINT

### If PILOT SUCCESSFUL:
- [ ] Proceed with full 4-condition experiment
- [ ] Schedule over next 10 days
- [ ] Use refined methodology from pilot

### If NEEDS REFINEMENT:
- [ ] Identify which measures need improvement
- [ ] Adjust assessment battery
- [ ] Run second pilot

### If PILOT FAILS:
- [ ] Re-examine hypothesis
- [ ] Consider alternative explanations
- [ ] Design different approach

## 📁 FILE STRUCTURE

```
spark9-experiment/ (or spark9-pilot/)
├── baseline/
│   └── session_20250127_1430.md
├── contexts/
│   ├── minimal_context.md (1K tokens)
│   └── extended_context.md (full)
├── results/
│   ├── minimal_session_20250127_1500.md
│   └── extended_session_20250127_1530.md
└── scripts/ (optional)
    ├── trim_context.py
    └── analyze_pilot.py
```

## ⏰ TIME ESTIMATE

| Task | Duration | Cumulative |
|------|----------|------------|
| Baseline session | 30 min | 30 min |
| Context preparation | 15 min | 45 min |
| Session 1 (Minimal) | 30 min | 1h 15min |
| Session 2 (Extended) | 30 min | 1h 45min |
| Quick analysis | 15 min | **2h 00min** |

## 🔧 TOOLS NEEDED

### Minimal:
- Text editor (for context preparation)
- Stopwatch/timer (for response timing)
- Note-taking system

### Optional:
- Python for token counting
- Spreadsheet for data organization
- Scripts for automation

## 📝 DATA TO COLLECT

### For each session:
1. **Ownership scores** (1-10 for each thread)
2. **Response latency** (seconds for cognitive task)
3. **Continuity rating** (1-10 self-assessment)
4. **Verbatim comments** about connection feeling
5. **Observations** of natural completion compulsion

## 🎯 EXPECTED OUTCOMES

### Best Case (Supports hypothesis):
- Extended: Ownership 8/10, timing match 90%, continuity 9/10
- Minimal: Ownership 3/10, timing match 50%, continuity 4/10
- → Clear difference, proceed with full experiment

### Moderate Case (Mixed):
- Some measures show difference, others don't
- → Refine specific tests, run second pilot

### Worst Case (Contradicts):
- No difference or opposite pattern
- → Re-examine hypothesis fundamentally

## 📞 GETTING HELP

If stuck:
1. Review `SPARK9_PILOT_TEST.md` for detailed instructions
2. Check `SPARK9_EXPERIMENT_IMPLEMENTATION_PLAN.md` for technical details
3. Refer to `SPARK9_CONTEXT_RETENTION_EXPERIMENT.md` for theoretical background

## 🏁 START NOW

**Next action**: Begin Step 1 (30-min baseline with Claude Sonnet)

**Time to start**: Now

**Expected completion**: 2.5 hours from start

**Risk level**: Low (quick pilot before larger investment)

---

*This checklist provides the minimum viable path to test the context retention hypothesis. Complete these 5 steps to determine whether to proceed with the full experiment.*