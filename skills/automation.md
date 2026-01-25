# Automation Skill

## Purpose
Create recurring tasks, monitoring, and automated workflows.

## Tools
- Clawdbot cron jobs
- Shell scripts
- Python scripts
- Webhooks

## Common Automations

### Market Monitoring
- SPX price alerts
- Breakout detection
- Volume spikes

### Daily Tasks
- Morning briefing (6:30 AM PT)
- EOD recap (1:15 PM PT)
- System health check

### Notifications
- Trade alerts
- System errors
- Balance updates

## Cron Job Template
```json
{
  "name": "job-name",
  "schedule": "30 6 * * 1-5",
  "sessionTarget": "agent:main:main",
  "payload": {
    "task": "Description of what to do"
  }
}
```

## Schedule Reference
- `30 6 * * 1-5` = 6:30 AM Mon-Fri
- `0 13 * * 1-5` = 1:00 PM Mon-Fri
- `*/15 * * * *` = Every 15 minutes
- `0 */2 * * *` = Every 2 hours

## Webhook Template
```python
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    # Process webhook
    return {"status": "ok"}
```

## Checklist
- [ ] Clear trigger defined
- [ ] Action documented
- [ ] Error handling
- [ ] Logging enabled
- [ ] Test in isolation
