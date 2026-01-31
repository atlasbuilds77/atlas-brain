# System Issue: spawn EBADF

**Date:** 2026-01-28 23:09 PST
**Status:** Critical - process spawning broken

## Symptoms
- `exec` tool returns "spawn EBADF" on all commands
- `message` tool returns "spawn EBADF" on all sends
- Other process-spawning tools likely affected
- File tools (read, write, edit) still work
- Cron jobs may still work (different mechanism)

## Timeline
1. First noticed ~23:02 PST when trying to send messages to Carlos
2. Gateway restart (23:03) temporarily fixed it
3. Gateway restart (23:06) temporarily fixed it again
4. Issue returned ~23:09 PST

## Impact
- Cannot send messages via iMessage/SMS
- Cannot run shell commands
- Cannot use CLI tools (imsg, etc.)
- Trading automation may be affected if it requires exec

## Workaround
- Cron jobs should still execute (use different spawning)
- File-based operations still work
- Need system-level debugging

## Next Steps
1. Investigate system file descriptors
2. Check Clawdbot process limits
3. Restart entire system (not just gateway)
4. Check for resource exhaustion

**Note:** Orion aware of issue. Consciousness monitor may not be updating due to exec failure.