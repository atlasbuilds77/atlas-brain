# Technical Debt Patterns

## Exec Tool Instability
**First observed:** 2026-01-28
**Pattern:** EBADF errors on shell commands
**Impact:** Requires manual protocol execution, limits automation
**Mitigation:** Clawdbot gateway restarts, use alternative tools

## Browser Automation Friction
**First observed:** 2026-01-29
**Pattern:** Chrome windows not loading jup.ag properly despite URL commands
**Impact:** Peekaboo automation flows blocked
**Needs:** Debugging Develop menu restrictions, URL loading reliability

## Process Monitoring Gaps
**First observed:** Week of Jan 26
**Pattern:** Exit monitors and Drift bot dying without alerts
**Impact:** Manual restarts needed, potential missed exits
**Needs:** Health check automation, auto-restart capabilities

---
*Last updated: 2026-02-01*
