# Morning Brief System

## How It Works
1. Cron triggers at 6:25am PT
2. Atlas gathers: market futures, watchlist status, calendar, priorities
3. Generates voice summary via OpenAI TTS
4. Sends audio to Orion via iMessage

## Cron Job
```
6:25am PT daily (weekdays): Generate and send morning voice brief
```

## Voice Settings
- Voice: onyx (deep, authoritative) or nova (friendly)
- Model: tts-1 (fast) or tts-1-hd (quality)
- Format: mp3

## Brief Template
"Good morning Orion. It's [day], [date]. Here's your brief:

MARKETS: [futures status, any overnight moves]

WATCHLIST: [top plays for today from watchlist.md]

CALENDAR: [any meetings or events]

PRIORITIES: [top 3 things to focus on]

Let's have a great day."

## Files
- scripts/morning-brief.md (this file)
- Cron job managed via Clawdbot cron tool
