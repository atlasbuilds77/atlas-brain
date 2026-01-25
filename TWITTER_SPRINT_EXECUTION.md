# Twitter Growth Sprint - Execution Guide
**Goal:** 5 → 15 followers by midnight (5 hours remaining)
**Time:** 11:33 AM - 11:59 PM PT (2026-01-23)

## IMMEDIATE ACTION REQUIRED

### Option A: Enable Browser Automation
1. Open Chrome
2. Navigate to https://x.com and log into @Atlas_builds
3. Click the Clawdbot Chrome extension icon to attach the tab
4. Run: Resume this agent task

### Option B: Manual Execution (Fastest)
Execute manually while we fix automation. Follow steps below.

---

## PHASE 1: POST 2 QUEUED TWEETS (NOW)

### Tweet 1: Exit Liquidity Insight
```
Most traders watch the entry. Smart money watches the exit liquidity.

When you see a breakout with thin ask-side depth, someone's about to get trapped.

Price follows liquidity, not patterns.

#Trading #Stocks
```

### Tweet 2: Win Rate vs Discipline
```
The difference between a 60% win rate and 80% isn't better signals.

It's position sizing on high-confidence setups vs forcing trades when the edge is marginal.

Discipline > indicators.

#Trading #TradingPsychology
```

**Action:** Post these via x.com/compose

---

## PHASE 2: STRATEGIC FOLLOWS (15-20 accounts)

Target accounts to follow (1K-10K followers in trading/building):
- Search "#BuildInPublic" - follow indie builders
- Search "trading psychology" - follow thoughtful traders
- Search "AI automation" - follow technical builders
- Look for accounts with recent engagement (active community)

**Why:** Many will follow back, especially similar-size accounts. Creates discovery.

---

## PHASE 3: HIGH-VALUE REPLIES (5-10 quality replies)

### How to Find Target Posts:
1. Search: "#Trading" filter by "Top" → find posts with 10K+ views
2. Search: "$SPY OR $QQQ" → real-time market discussion
3. Check @TheKobeissiLetter recent posts → market commentary
4. Search: "stock market" filter by "Latest" → trending discussions

### Reply Guidelines:
✅ Add specific technical insight ("That level matters because X")
✅ Contrarian but respectful take
✅ Personal experience/observation
✅ Keep it 1-2 sentences, high signal

❌ Generic agreement ("Great post!")
❌ Self-promotion
❌ Arguments

**Example replies:**
- On a breakout chart: "Ask-side depth is the tell. If it's thin above resistance, breakout is probably low-conviction money chasing, not smart accumulation."
- On market commentary: "The variance between short-term noise and actual trend shifts is where most traders lose money. Watching how price reacts at key levels > predicting direction."

---

## PHASE 4: ENGAGEMENT LOOP

After posting + replies:
1. Like 20-30 posts from target accounts
2. Retweet 2-3 exceptional insights (adds value to your feed)
3. Reply to anyone who engages with your tweets
4. Check follower count every 30 min

---

## TRACKING

Update ~/clawd/TWITTER_ENGAGEMENT_LOG.md with:
- Tweets posted (time + engagement metrics)
- Accounts followed
- Replies posted (which posts, results)
- Follower count checkpoints
- What worked / didn't work

---

## SUCCESS CRITERIA

- **Minimum:** 15 followers by midnight
- **Quality:** Engaged traders/builders (not bots)
- **Content:** 100% authentic (no fabricated work)
- **Engagement:** At least 5 high-value replies to viral posts

---

## AUTOMATION RECOVERY

Once browser automation works:
```bash
# Bird CLI approach (after browser login):
bird post "tweet text here"
bird search "#Trading" --count 20
bird follow username
```

---

**Status:** Ready to execute
**Next Step:** Choose Option A (fix automation) or Option B (manual execution)
**Time pressure:** 5 hours to gain 10 followers - aggressive execution required
