# Daily Market Recap Skill

## Purpose
Generate morning market briefings and end-of-day recaps.

## Data Sources
- Polygon API (SPX, futures)
- TradingView (charts if needed)
- Economic calendar
- News headlines

## Morning Briefing Template
```
## Market Briefing - [Date]

### Overnight Summary
- ES Futures: [price] ([change]%)
- Key levels: Support [X], Resistance [Y]

### Key Events Today
- [Time]: [Event] (Expected: X, Previous: Y)

### Watchlist
1. [Ticker] - [Reason]
2. [Ticker] - [Reason]

### Strategy Notes
- [Bias for the day]
- [Key levels to watch]
- [Risk considerations]
```

## EOD Recap Template
```
## EOD Recap - [Date]

### Session Summary
- SPX: [close] ([change]%)
- High/Low: [high]/[low]
- Volume: [above/below average]

### What Worked
- [Trade/setup that worked]

### What Didn't
- [Trade/setup that failed]

### Tomorrow's Setup
- [Key levels]
- [Bias]
```

## Automation
- Morning: 6:30 AM PT (before market)
- EOD: 1:15 PM PT (after close)

## Checklist
- [ ] Data pulled fresh
- [ ] Key levels identified
- [ ] Events noted
- [ ] Actionable insights
