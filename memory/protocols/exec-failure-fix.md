# Exec Failure Fix Protocol

## Problem
`exec` tool returns `spawn EBADF` error - can't run any commands

## Solution
**RESTART GATEWAY**

```
gateway(action="restart", reason="exec failing with spawn EBADF")
```

## After Restart
1. Test exec: `exec(command="echo test && date")`
2. Continue previous task
3. Document what you were doing so you don't lose context

## Prevention
- This happens occasionally, just restart
- No data loss, gateway reconnects automatically
- Session persists

---

*Created: 2026-01-27 12:13 PST*
*Trigger: exec spawn EBADF during SLV/SPX trade execution*
