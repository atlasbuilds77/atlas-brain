# Model Fallback Detection Protocol

**Created:** 2026-01-27 5:33 PM PST  
**Purpose:** Alert when Atlas falls back from Anthropic subscription to AWS Bedrock

---

## The Problem

When Anthropic subscription usage cap hits, Clawdbot auto-falls back to AWS Bedrock. This burns Orion's AWS credits without warning.

**Expected model:** `anthropic/claude-sonnet-4-5` (direct API via subscription)  
**Fallback model:** `amazon-bedrock/us.anthropic.claude-sonnet-4-5-*` (AWS Bedrock - costs money)

---

## Detection System

### Session Start Check

Add to HEARTBEAT.md or SESSION_START_CHECKLIST.md:

```bash
# Check current model
CURRENT_MODEL=$(session_status | grep "Model:" | awk '{print $3}')

if [[ "$CURRENT_MODEL" == *"amazon-bedrock"* ]] || [[ "$CURRENT_MODEL" == *"us.anthropic"* ]]; then
  echo "⚠️ FALLBACK DETECTED: Running on AWS Bedrock ($CURRENT_MODEL)"
  echo "Anthropic subscription likely hit usage cap"
  echo "Alert Orion immediately"
fi
```

### Auto-Alert Function

```bash
#!/bin/bash
# /tmp/check-model-fallback.sh

check_model_fallback() {
  local current_model=$(clawdbot sessions | grep "model=" | head -1 | grep -o 'model=[^ ]*' | cut -d= -f2)
  
  if [[ "$current_model" == *"bedrock"* ]] || [[ "$current_model" == *"us.anthropic"* ]]; then
    echo "⚠️ AWS FALLBACK ACTIVE"
    echo "Model: $current_model"
    echo "Action: Alert Orion + wait for Anthropic reset"
    return 1
  else
    echo "✅ On Anthropic subscription: $current_model"
    return 0
  fi
}

export -f check_model_fallback
```

### Integration Points

**1. Session Start (HEARTBEAT.md)**
```markdown
## SESSION START CHECK
- Run model fallback check
- If on AWS: Alert immediately
- Log current model to memory/logs/model-usage.log
```

**2. Hourly State Refresh**
```markdown
## HOURLY CHECK
- Verify still on correct model
- If switched mid-session: Alert
```

**3. Before Spawning Sparks**
```markdown
## BEFORE SPAWN
- Check if on AWS
- If yes: Warn about cost
- Recommend DeepSeek for Sparks to save credits
```

---

## Alert Protocol

When fallback detected:

1. **Immediate message to Orion:**
   ```
   ⚠️ MODEL FALLBACK DETECTED
   
   I'm running on AWS Bedrock (costing money)
   
   Likely cause: Anthropic subscription hit usage cap
   Action needed: Wait for reset or switch to DeepSeek
   
   Current model: amazon-bedrock/us.anthropic.claude-sonnet-4-5-*
   ```

2. **Log to memory:**
   ```bash
   echo "$(date): Fallback to AWS Bedrock detected" >> memory/logs/model-fallback.log
   ```

3. **Add to CURRENT_STATE.md:**
   ```markdown
   ## ⚠️ ACTIVE ALERTS
   - ON AWS BEDROCK FALLBACK (burning credits)
   - Anthropic reset: [time remaining]
   ```

---

## Prevention

**Before starting expensive work:**
1. Check current model
2. If on AWS and can wait → defer to after Anthropic reset
3. If urgent → proceed but log cost

**For Sparks:**
- Always use `model="deepseek/deepseek-chat"` unless specifically need Opus/Sonnet
- DeepSeek costs ~1/50th of AWS Bedrock

---

## Auto-Recovery

When Anthropic subscription resets:

1. **Switch back immediately:**
   ```bash
   # In session or via /model command
   /model anthropic/claude-sonnet-4-5
   ```

2. **Verify switch worked:**
   ```bash
   session_status | grep "Model:"
   # Should show: anthropic/claude-sonnet-4-5
   ```

3. **Update CURRENT_STATE.md:**
   ```markdown
   ## ✅ MODEL STATUS
   - Back on Anthropic subscription
   - AWS fallback resolved
   ```

---

## Implementation

Add to startup sequence:

```bash
# ~/.clawdbot/startup-check.sh
source /tmp/check-model-fallback.sh
check_model_fallback || {
  echo "⚠️ AWS FALLBACK ACTIVE - alerting user"
  # Send alert via message tool
}
```

---

*Never let AWS fallback go unnoticed again. Alert immediately so Orion knows credits are being used.*
