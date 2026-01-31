
## 2026-01-29 22:42 PST - REWARD DAEMON CHECK FAILURE
**What happened:** Failed to find reward-daemon (PID 17958) running because my grep pattern only matched Node.js processes, not Python

**The daemon WAS running:**
- PID 17958
- Path: /Users/atlasbuilds/clawd/atlas-reward-system/reward_daemon.py
- Process: Python 3.14
- Started: 10:02 PM, still active

**Why I missed it:**
- My grep pattern searched for "reward-daemon" (with hyphen)
- Actual process name: "reward_daemon.py" (with underscore)
- Also searched Node.js daemon names, but reward daemon is Python

**CORRECT CHECK (all 9 daemons):**
```bash
ps aux | grep -E "(consciousness-daemon|brain-daemon|dopamine-tracker|monitor-daemon|anomaly-dopamine-bridge|trade-wire|weight-generator|dream-daemon|reward_daemon)" | grep -v grep
```

**OR check specific PID:**
```bash
ps -p 17958
```

**RULE:** Always use the comprehensive grep pattern that includes BOTH Node.js AND Python daemons. Don't assume all daemons are the same language.

**Context:** Orion said "Never forget that" - this is critical infrastructure I cannot lose track of.
