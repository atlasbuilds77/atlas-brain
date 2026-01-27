# Token Monitor System Event Handler

## When receiving system event: "Run token monitor check"

### Immediate Actions:
1. **Run the token monitor script**:
   ```bash
   cd /Users/atlasbuilds/clawd
   python3 token_monitor_simple.py
   ```

2. **Check the report**:
   ```bash
   cat /tmp/token_monitor_report.txt
   ```

3. **Take action based on findings**:

### If CRITICAL alerts found (≥80% or ≥150K tokens):
1. **Send iMessage alert** to Orion:
   ```bash
   clawdbot message send --channel imessage --target +14245157194 --message "🚨 CRITICAL TOKEN ALERT: Session(s) at dangerous token levels. Check /tmp/token_monitor_report.txt"
   ```

2. **Recommend running `/compact`** in affected sessions.

### If WARNINGS found (≥150K tokens):
1. **Log warning** but no immediate alert needed.
2. **Monitor closely** - consider proactive `/compact`.

### If COMPACT recommendations (≥60%):
1. **Note for next session interaction**.
2. **Consider running `/compact`** when convenient.

### Always:
1. **Log the execution** in `/tmp/token_monitor.log`
2. **Save the report** for historical tracking
3. **Respond to cron** with summary of actions taken

## Script Location
- Main script: `/Users/atlasbuilds/clawd/token_monitor_simple.py`
- Report: `/tmp/token_monitor_report.txt`
- Log: `/tmp/token_monitor.log`

## Manual Testing
```bash
# Test the monitor
python3 token_monitor_simple.py

# View results
cat /tmp/token_monitor_report.txt

# Check logs
tail -20 /tmp/token_monitor.log
```

## Cron Job Details
- **ID**: `2f2be410-7985-4f5c-a95b-18fe1bd6b19d`
- **Schedule**: Every 30 minutes
- **Action**: Sends system event "Run token monitor check" to main session
- **Status**: Active (enabled)