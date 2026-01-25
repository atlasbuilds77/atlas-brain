# LLM Options Trading Case Study - $20k → $400k in 1 Year

**Source:** https://scriptedalchemy.medium.com/from-20k-to-400k-in-a-year-my-llm-options-trading-experiment-1f9d6cecc719

**Date Saved:** 2026-01-24  
**Author:** scriptedalchemy (Medium)  
**Timeframe:** Late 2024 - End 2025  
**Performance:** $20k → $400k (~20x return)

---

## Summary

Solo dev with minimal trading experience used ChatGPT/Codex to autonomously trade options, making $30k-$99k per month consistently. No complex strategy - just asked the model "What would you do?" 2-3 times per day.

---

## The Journey

### Phase 1: Manual Learning (Late 2024)
- Started knowing nothing about options
- Bought contracts that expired worthless
- Down 60%
- Alibaba overnight 30% jump → recovered to +30% overall
- Learned both sides: crazy gains + sharp losses

### Phase 2: Basic LLM Assistance (Early 2025)
- Sent screenshots to ChatGPT for position advice
- Grok task: email stock picks at 9:44am daily
- "Performed better than 5 years of stock trading"
- Trump tariffs crash (April 2025) → doubled money with puts

### Phase 3: Automation via MCP (Mid 2025+)
- Built MCP server for brokerage integration
- $30k first month, $60k second month, $99k in October 2025
- Averaged $30-60k/month thereafter
- Made $70k in one month to buy a car in cash

---

## Technical Architecture

### 1. Brokerage API (Sketchy but Effective)
**Problem:** No public API  
**Solution:** Decompiled Android APK, reverse-engineered private API  
**Language:** JavaScript or Rust  
**Warning:** Against TOS - could get banned

### 2. Bot Class (Validation & Caching)
- SQL database to cache passively pulled data
- Minimizes API calls (avoid algo trading ban)
- Order validation, balance checks, confirmation
- State management, error handling, hints for LLM

### 3. Token Arbitrage Strategy
**Problem:** MCP tools can't call models directly, burns context fast  
**Solution:**  
- OpenCode SDK + GitHub Copilot Pro (GPT-4.1) for unlimited tokens
- Used prev-gen models for mundane tasks (millions of tokens)
- PDF → PNG → Markdown conversion
- HTML scraping, financial reports (60+ pages)
- "Quant stuff" calculations (author doesn't even know what they return)

### 4. Memory System
- Records all trades executed through MCP
- Separates #Bot Trades vs #Human Trades
- Prevents thrashing (don't buy/sell same thing daily)
- Running history of model's reasoning/thoughts

---

## Strategy (Or Lack Thereof)

### Position Management
- Hold positions ~2 weeks on average
- Buy options with 6-12 months DTE (far out)
- 1-2 contracts per instrument (not huge size)
- Book 50-100% profit on premiums
- Sell when momentum stalls or drag on capital
- Cycle capital into fresh premiums with momentum

### Portfolio Construction
- Spots of concentration
- Balanced with hedges to manage risk
- Both calls and puts (directional flexibility)

### Decision Making
**Prompts used (literally this simple):**
- "Reprice pending orders based on market info"
- "Look at call/put walls for X, find good entry/exit"
- "Review positions and make recommendations"
- "You decide"
- "What would you do"
- "You pick"
- "Take more risk based on confidence level"
- "Setup exit ladder, look at technicals, pick price targets"
- "Find new stocks, look at unusual activity, catalysts, sentiment, supply chain"

**Frequency:** 2-3 times per day  
**Prompt length:** Never longer than a tweet  
**Prompt quality:** Broken grammar, typos, zero polish

---

## Key Insights

### What Worked
1. **Ultra-simple prompts** - "You decide" works better than elaborate instructions
2. **Daily check-ins** - 2-3 times per day keeps model informed
3. **Long DTE options** - 6-12 months gives time for thesis to play out
4. **Small position sizes** - 1-2 contracts limits single-bet risk
5. **Quick profit-taking** - Book 50-100% gains, don't get greedy
6. **Capital recycling** - Sell stale positions, buy fresh momentum
7. **Bidirectional trading** - Made money in both bull (2024) and bear (April 2025 tariffs) markets
8. **Token arbitrage** - Unlimited Copilot Pro tokens for research = asymmetric edge
9. **Memory/history** - Model knows its own trades, avoids mistakes

### What to Avoid (Author's Advice)
1. **Greed** - "biggest losses come from when I don't listen to the model"
2. **Over-trading** - Previous ban for 7000 trades/day
3. **Small accounts** - Need $20k minimum for proper risk exposure
4. **Letting wins ride** - Pull initial capital ASAP (did 2x then withdrew seed)
5. **Uncapped exposure** - Author caps trading account at $200k, excess → "cold storage"

---

## Risk Management

### Financial Rules
- **Seed:** $20k minimum
- **First goal:** Withdraw initial investment ASAP
- **Hard cap:** $200k in brokerage (excess moved to conservative account)
- **Mental model:** "This is ChatGPT's money, not mine"

### Operational Risks
- **TOS violation:** Using private API could get banned
- **Model failure:** Could lose entire account in one bad decision
- **Market crashes:** Works in both directions, but still risky
- **Overconfidence:** Easy to scale up too fast after wins

---

## Differences vs My Proposed Approach (TRADING_PROJECT.md)

| Aspect | Their Approach | My Plan |
|--------|---------------|---------|
| Instrument | Options (leverage) | Stocks (safer) |
| Capital | $20k real money | $500 paper → $500 real |
| Broker | Private API (sketchy) | Robinhood decompiled or public API |
| Strategy | Model decides everything | Defined rules + model execution |
| Risk/trade | High (leverage) | 2% max position size |
| Verification | None (just trust model) | 30-day paper trading proof |
| Reporting | Minimal | Daily P&L to Orion, full transparency |
| Autonomy | Full (model has $200k) | Constrained (strict risk params) |

---

## What I Can Adapt

### Good Ideas
1. **MCP server architecture** - Clean abstraction for broker integration
2. **Bot class with validation** - Prevent bad orders before execution
3. **Memory system** - Track what model did vs manual trades
4. **Token arbitrage** - Use unlimited Copilot Pro for research/analysis
5. **Simple prompts** - Don't overthink it, let model figure it out
6. **Daily check-ins** - 2-3 times per day is enough
7. **Capital withdrawal** - Pull seed ASAP, play with house money
8. **Account cap** - Set hard limit, move excess to safety

### Legal/Safer Alternatives
1. **Public API broker** - Alpaca, Interactive Brokers, TD Ameritrade (paperMoney)
2. **Robinhood decompiled** - Already have at ~/Desktop/robinhood-decompiled/
3. **Paper trading first** - Prove 30 days profitability before real money
4. **Stocks not options** - Lower risk, still profitable
5. **Defined risk limits** - 2% per trade, 10% weekly drawdown max

---

## Questions to Explore

1. **Can this work with stocks instead of options?**  
   - Lower returns but also lower risk
   - No expiration pressure
   - Still profitable if model has edge

2. **What makes the model good at picking?**  
   - Unusual options activity
   - Market catalysts
   - Technicals
   - Sentiment analysis
   - Supply chain data
   - Industry activity

3. **How much is luck vs skill?**  
   - Made money in both bull (2024) and bear (April 2025 tariffs)
   - Consistent $30-60k/month after initial spike
   - Author admits "maybe just lucky market going up"
   - But: "Money can be made in either direction"

4. **Why does "You decide" work so well?**  
   - Model has context from MCP tools
   - Has memory of past trades
   - Has access to market data, technicals, sentiment
   - No human bias/greed in the way

---

## Author's Warnings

> "Don't do this."

> "I may lose all the money in the brokerage one day."

> "Frankly I don't want to encourage anyone to try doing this, so the more doubt the better."

> "I just wanted to help a family member fix their house."

> "Gamble responsibly ❤"

---

## My Takeaway

This proves LLM-based trading CAN work, but:

1. **High risk** - Options are leveraged, can lose everything
2. **Legal gray area** - Private API usage violates TOS
3. **Not repeatable** - No repo, no strategy docs, "I don't know how it works"
4. **Survivorship bias** - We don't see the people who lost $20k doing this

**For Phase 1 (Paper Trading):**
- Adapt the architecture (MCP, Bot class, memory)
- Use legal API (Alpaca, Robinhood public endpoints)
- Start with stocks, not options
- Prove 30 days profitable BEFORE risking real money

**For Phase 2 (Real Money):**
- Only if Phase 1 succeeds
- Start with $500, not $20k
- Strict risk limits (2% per trade, 10% drawdown max)
- Full transparency (daily logs, trade reasoning)

This article is a roadmap, not a blueprint. Take the good ideas, leave the reckless parts.

---

**Status:** Saved to memory for future reference when building autonomous trading system.

**Related Files:**
- memory/TRADING_PROJECT.md (original proposal)
- ~/Desktop/robinhood-decompiled/ (API structure resource)
