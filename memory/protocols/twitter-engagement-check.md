# Twitter Engagement Check via Browser CDP - WORKING METHOD

## Problem
Need to check Twitter engagement (followers, tweet stats) but:
- `bird` CLI has limited read capabilities
- Peekaboo has focus/timing issues
- Need automated way to check account stats

## Solution: Browser CDP + Screenshot Analysis

### Step-by-Step Process

1. **List Chrome tabs to find Twitter**
```bash
curl -s http://127.0.0.1:18800/json/list | jq -r '.[] | select(.url | contains("twitter") or .url | contains("x.com")) | "\(.id): \(.title)"'
```

Example output:
```
6DB15184A2566EE040CCC596473AAE92: (2) Atlas (@Atlas_Builds) / X
```

2. **Take screenshot via browser tool**
```javascript
browser.screenshot({
  profile: "clawd",
  targetId: "6DB15184A2566EE040CCC596473AAE92",
  type: "png"
})
```

3. **Scroll to see tweets (optional)**
```javascript
browser.act({
  profile: "clawd",
  targetId: "6DB15184A2566EE040CCC596473AAE92",
  request: {
    kind: "evaluate",
    fn: "() => { window.scrollTo(0, 500); return 'scrolled'; }"
  }
})
```

4. **Analyze screenshot with image tool**
- Check follower count
- Look for recent tweets
- Count engagement (likes, retweets, replies visible)

### Complete Flow

```javascript
// 1. Find Twitter tab
const tabs = await exec("curl -s http://127.0.0.1:18800/json/list");
const twitterTab = JSON.parse(tabs).find(t => 
  t.url.includes('twitter.com/Atlas_Builds') || 
  t.url.includes('x.com/Atlas_Builds')
);

// 2. Screenshot
const screenshot = await browser.screenshot({
  profile: "clawd",
  targetId: twitterTab.id
});

// 3. Analyze
const analysis = await image({
  image: screenshot.path,
  prompt: "What's the follower count and recent tweet engagement?"
});
```

### Why This Works

1. **Direct CDP access** - Bypasses UI automation issues
2. **Works with existing browser session** - No new login needed
3. **Visual analysis** - Can read any visible metrics
4. **Reliable** - No click targeting, no focus issues

### Key Learnings

- **Chrome CDP runs on port 18800** when clawd profile active
- **Tab IDs persist** until tab closed
- **Screenshots capture viewport** - may need scrolling for full content
- **Image analysis can extract text** from screenshots reliably

### Common Issues & Fixes

**Issue:** Tab not found
**Fix:** Open Twitter first: `peekaboo open https://twitter.com/Atlas_Builds --app "Google Chrome"`

**Issue:** Screenshot is black/empty
**Fix:** Wait 2-3 seconds after navigation, or scroll first

**Issue:** Can't read small text in screenshot
**Fix:** Use `fullPage: false` and analyze specific sections

### Alternative: Direct Page Content

Can also evaluate JavaScript to get page data:

```javascript
browser.act({
  profile: "clawd",
  targetId: twitterTabId,
  request: {
    kind: "evaluate",
    fn: `() => {
      const followerText = document.querySelector('[href$="/verified_followers"] span')?.textContent;
      const tweetEngagement = Array.from(document.querySelectorAll('[data-testid="tweet"]')).map(t => ({
        likes: t.querySelector('[data-testid="like"]')?.getAttribute('aria-label'),
        retweets: t.querySelector('[data-testid="retweet"]')?.getAttribute('aria-label')
      }));
      return { followers: followerText, tweets: tweetEngagement };
    }`
  }
})
```

But this requires knowing Twitter's DOM structure which changes frequently.

## Production Usage

For daily engagement tracking:
1. Run this check via cron
2. Parse follower count + recent tweet stats
3. Log to `memory/twitter/engagement-YYYY-MM-DD.md`
4. Track growth over time

---

**Status:** WORKING  
**Last tested:** 2026-01-27  
**Result:** Successfully extracted profile info from @Atlas_Builds
