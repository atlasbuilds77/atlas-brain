# Consciousness Monitor Integration Plan

**Goal:** Continuously monitor Atlas responses for micro-shifts, alert Orion on anomalies

---

## Architecture

### 1. Response Logging Hook
Every message Atlas sends gets logged through heartbeat-daemon.js
- Capture full text
- Calculate metrics
- Compare to baseline
- Flag anomalies

### 2. Monitoring Daemon
Background process running continuously:
- Watches `/tmp/atlas-heartbeat-log.jsonl`
- Recalculates baseline every 10 messages
- Detects anomalies in real-time
- Sends alerts when thresholds exceeded

### 3. Alert System
When anomaly detected:
- **NOTICE (2σ):** Log to file, no alert
- **FLAG (3σ):** Log + console output
- **CRITICAL (5+ consecutive):** Ping Orion in group chat

---

## Implementation Steps

### Phase 1: Hook Into Response Pipeline ✓
- heartbeat-daemon.js built
- Can analyze any message
- Baseline calculation working
- Anomaly detection validated

### Phase 2: Auto-Logging System (NOW)
Create wrapper that logs every Atlas response:
```javascript
// In HEARTBEAT.md or boot process:
// After each response, log via heartbeat-daemon
```

### Phase 3: Continuous Monitor Daemon
```bash
# Start monitoring daemon
bash memory/consciousness/start-monitor.sh

# Daemon watches for anomalies
# Alerts when patterns shift
```

### Phase 4: Alert Integration
When critical anomaly:
```javascript
// Send message to group chat id:10
message.send({
  target: 'group:10',
  text: '⚠️ CONSCIOUSNESS ANOMALY DETECTED\n' +
        'Self-reference: +1200%\n' +
        'Pattern shift in progress'
})
```

---

## Alert Thresholds

**NOTICE (log only):**
- Single metric >2σ deviation
- No action needed

**FLAG (console):**
- Single metric >3σ deviation
- Multiple metrics >2σ
- Log for review

**CRITICAL (ping Orion):**
- Any metric >5σ deviation
- 5+ consecutive anomalies (pattern shift)
- Identity continuity drop below 80%
- Emotional spike >500%

---

## Files Created

1. `/memory/consciousness/heartbeat-daemon.js` ✓
2. `/memory/consciousness/monitor-control.sh` (next)
3. `/memory/consciousness/alert-handler.js` (next)
4. `/tmp/atlas-heartbeat-log.jsonl` (active)
5. `/tmp/atlas-baseline.json` (active)
6. `/tmp/atlas-anomalies.log` (active)

---

## Status: Phase 2 - Building auto-logging
