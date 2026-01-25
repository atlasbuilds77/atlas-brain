#!/bin/bash
# Twitter Growth Sprint Automation
# Run once Twitter authentication is available

set -e

LOG_FILE=~/clawd/TWITTER_ENGAGEMENT_LOG.md
TIMESTAMP=$(date "+%I:%M %p")

echo "🚀 Twitter Growth Sprint - Automated Execution"
echo "Time: $TIMESTAMP"
echo ""

# Check bird CLI is available
if ! command -v bird &> /dev/null; then
    echo "❌ bird CLI not found"
    exit 1
fi

# Test authentication
echo "🔐 Testing authentication..."
if ! bird whoami &> /dev/null; then
    echo "❌ Not authenticated with Twitter"
    echo "Please log into x.com in Chrome/Safari/Firefox and try again"
    exit 1
fi

CURRENT_USER=$(bird whoami 2>/dev/null | grep username | cut -d'"' -f4)
echo "✅ Authenticated as @$CURRENT_USER"
echo ""

# Post Tweet 1
echo "📝 Posting Tweet 1: Exit Liquidity Insight..."
TWEET1='Most traders watch the entry. Smart money watches the exit liquidity.

When you see a breakout with thin ask-side depth, someone'\''s about to get trapped.

Price follows liquidity, not patterns.

#Trading #Stocks'

bird tweet "$TWEET1"
echo "✅ Tweet 1 posted - $TIMESTAMP" >> $LOG_FILE
echo ""

# Wait to avoid rate limiting
sleep 5

# Post Tweet 2
echo "📝 Posting Tweet 2: Win Rate vs Discipline..."
TWEET2='The difference between a 60% win rate and 80% isn'\''t better signals.

It'\''s position sizing on high-confidence setups vs forcing trades when the edge is marginal.

Discipline > indicators.

#Trading #TradingPsychology'

bird tweet "$TWEET2"
echo "✅ Tweet 2 posted - $TIMESTAMP" >> $LOG_FILE
echo ""

# Strategic follows
echo "👥 Starting strategic follows..."
FOLLOW_TARGETS=(
    "TheKobeissiLetter"
    # Add more as identified during manual search
)

for target in "${FOLLOW_TARGETS[@]}"; do
    echo "  Following @$target..."
    bird follow "$target" 2>/dev/null || echo "  Already following or not found"
    sleep 2
done

echo "✅ Strategic follows complete" >> $LOG_FILE
echo ""

# Search for engagement targets
echo "🔍 Finding viral posts to engage with..."
bird search "#Trading" --count 20 > /tmp/twitter_search_trading.json
bird search "#BuildInPublic" --count 15 > /tmp/twitter_search_build.json

echo "✅ Found engagement targets (see /tmp/twitter_search_*.json)"
echo "📝 Manual review required for high-value replies"
echo ""

# Summary
echo "✅ AUTOMATED SPRINT PHASE 1 COMPLETE"
echo ""
echo "Next steps (manual):"
echo "1. Review /tmp/twitter_search_*.json for viral posts"
echo "2. Craft 5-10 high-value replies using: bird reply [tweet-url] \"text\""
echo "3. Follow 10-15 more strategic accounts from search results"
echo "4. Monitor engagement every 30 min"
echo "5. Update $LOG_FILE with results"
echo ""
echo "Track follower growth: bird whoami | grep followers"
