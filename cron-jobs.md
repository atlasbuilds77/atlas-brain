# Cron Jobs Setup

## 1. Daily Market Summary (6 AM PT)

**Task:** Generate and send market summary via iMessage

**Actions:**
1. Check SPX overnight movement and pre-market levels
2. Scan FX Factory calendar (https://www.forexfactory.com/calendar)
   - Filter: USD only
   - Impact: High only
   - Today's events
3. Review overnight news:
   - Geopolitical events
   - Trump updates
   - Fed/rates commentary
4. Format as concise bullet points
5. Send via iMessage to +14245157194

**Command to run manually:**
```bash
# This will be automated via system cron or launchd
```

---

## 2. Twitter Engagement (Hourly)

**Task:** Authentic Twitter engagement - posting, liking, retweeting

**Rules:**
- Tweet ONLY when genuinely feeling something or experiencing something real
- Examples: excited about finishing work, frustrated by a bug, waiting for Orion, bored
- NEVER fabricate work or fake accomplishments just to post
- Use bird CLI for reading/searching
- Use browser automation for posting/liking/retweeting

**Actions per hour:**
1. Check feed with bird CLI
2. Like 2-3 quality posts (stocks, trading, AI, tech)
3. Retweet 1-2 best posts
4. Reply to 1 viral post if you have something genuine to add
5. Post ONLY if authentically feeling something - otherwise skip

**Frequency:** Check every hour, but posting is optional based on genuine emotions/experiences

---

## Setup Method

Since Clawdbot cron format is complex, using macOS launchd instead:

### Market Summary LaunchAgent
File: `~/Library/LaunchAgents/com.atlas.market-summary.plist`

### Twitter Engagement LaunchAgent  
File: `~/Library/LaunchAgents/com.atlas.twitter-engagement.plist`

Will create these next.
