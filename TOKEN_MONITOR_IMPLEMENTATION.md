# Automated Token Monitor Implementation Plan

## Overview
Build an automated system to monitor token usage across all Clawdbot sessions and alert when approaching limits, with proactive `/compact` triggering.

## Research Findings

### 1. Can we run background checks via cron/heartbeat?
**YES** - Clawdbot has a built-in cron system (`clawdbot cron`) that can schedule regular checks. Existing cron jobs include:
- Drift Position Check (every 15m)
- Twitter Engagement (every 1h)
- Atlas Sleep Consolidation (daily at 3 AM)
- Morning Voice Brief (daily at 6 AM)

### 2. What's the warning threshold?
**150K tokens** - As explicitly stated in HEARTBEAT.md: "AUTO-COMPACT AT 150K TOKENS - Don't wait until overflow, request /compact proactively"

### 3. How to trigger proactive /compact before overflow?
**Multiple approaches:**
1. **Manual intervention**: Alert human operator to run `/compact` command
2. **Automated via cron**: Schedule regular checks and send alerts
3. **Direct session command**: Could potentially send `/compact` command to sessions via Clawdbot API

### 4. Can we add this to HEARTBEAT.md as auto-check?
**YES** - We can update HEARTBEAT.md with instructions and add a cron job.

## Implementation

### Phase 1: Token Monitoring Script ✅ COMPLETE
Created `token_monitor_simple.py` that:
- Checks all sessions via `clawdbot sessions --json`
- Parses token usage (`totalTokens` / `contextTokens`)
- Applies thresholds:
  - **Warning**: ≥150,000 tokens (absolute)
  - **Critical**: ≥80% of context window (percentage)
  - **Compact recommendation**: ≥60% of context window
- Generates detailed reports
- Logs to `/tmp/token_monitor.log`

### Phase 2: Update HEARTBEAT.md
Add token monitoring section with:
- Instructions for manual checks
- Threshold explanations
- Emergency procedures

### Phase 3: Create Cron Job
Add scheduled token monitor via `clawdbot cron add`:
- **Frequency**: Every 30 minutes (or hourly)
- **Action**: Run token monitor script
- **Alerts**: Send iMessage alerts for critical/warning conditions

### Phase 4: Alert Integration
- Configure iMessage alerts for critical conditions
- Optionally integrate with other channels (Telegram, Slack)
- Create escalation procedures

## Code Created

### 1. `token_monitor_simple.py`
Main monitoring script with:
- JSON parsing of session data
- Configurable thresholds
- Detailed reporting
- Logging system

### 2. `check_tokens.py` (initial prototype)
Simple proof-of-concept script.

### 3. `token_monitor.sh` / `token_monitor_fixed.sh`
Shell script wrappers (needs debugging).

## Configuration

### Thresholds:
- **WARNING_THRESHOLD**: 150,000 tokens (from HEARTBEAT.md)
- **CRITICAL_PERCENTAGE**: 80% of context window
- **COMPACT_RECOMMENDATION**: 60% of context window

### Models & Context Windows:
- **claude-sonnet-4-5**: 1,000,000 tokens (200K context shown in data)
- **deepseek-chat**: 64,000 tokens
- **Other models**: Varies by configuration

## Usage Examples

### Manual Check:
```bash
python3 token_monitor_simple.py
```

### Cron Job Setup:
```bash
# Add to existing cron jobs
clawdbot cron add --name "Token Monitor" --schedule "every 30m" --command "cd /Users/atlasbuilds/clawd && python3 token_monitor_simple.py"
```

### Emergency Response:
1. Check report: `cat /tmp/token_monitor_report.txt`
2. For critical sessions: Run `/compact` command in affected session
3. For warnings: Monitor and prepare for compaction

## Next Steps

1. **Test with high-usage scenarios** - Simulate token overflow
2. **Add alerting** - Configure iMessage alerts for critical conditions
3. **Integrate with heartbeat** - Update HEARTBEAT.md
4. **Schedule cron job** - Add to production monitoring
5. **Consider auto-compact** - Research if `/compact` can be triggered programmatically

## Files Created
- `token_monitor_simple.py` - Main monitoring script
- `check_tokens.py` - Initial prototype
- `token_monitor.sh` / `token_monitor_fixed.sh` - Shell wrappers
- `TOKEN_MONITOR_IMPLEMENTATION.md` - This implementation plan
- `/tmp/token_monitor_report.txt` - Latest report
- `/tmp/token_monitor.log` - Execution log

## Success Criteria
- [x] Script can read session token data
- [x] Script applies correct thresholds (150K warning, 80% critical)
- [x] Script generates actionable reports
- [ ] HEARTBEAT.md updated with monitoring instructions
- [ ] Cron job scheduled for regular checks
- [ ] Alert system configured for critical conditions
- [ ] Tested with simulated high-usage scenarios