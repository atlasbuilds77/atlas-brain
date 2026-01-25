# Usage Monitoring Rules

## Auto-Alert Thresholds

**Context Size:**
- Yellow (60k tokens): Note internally, optimize next responses
- Orange (80k tokens): Alert Orion, suggest reset
- Red (100k+ tokens): Urgent - request immediate reset

**Check frequency:** Every 10th message in main chat

## Alert Format

When threshold hit, send to Orion:

```
⚠️ Context Warning: 85k tokens (80% capacity)

Quick reset? I'll:
1. Summarize current work → memory
2. Start fresh session  
3. Load memory back
4. Continue where we left off

Cost savings: ~$2-5 per reset
```

## Manual Reset Command

User says: "reset session" or "fresh start"
→ Immediate reset with summary

## Current Session Stats

Check with: `clawdbot status | grep context`

Target: Keep under 50k tokens for normal operation
