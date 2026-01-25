# Kalshi & Prediction Market Strategy Playbook

Last updated: 2026-01-25

---

## STRATEGY 1: "Reversing Stupidity" ($286 → $1M)

**Source:** Trader "Semi" on Polymarket

**Core principle:** Bet against folk wisdom / dumb money

### Examples that worked:
- **Pope market:** Top 3 candidates priced at 75% combined, but 150 cardinals could win. Bet NO on all favorites without knowing anything about cardinals.
- **Post-Trump election:** MAGA money pushed irrational bets. "Tax on tips in 100 days" was impossible (Congress in recess, bills take 6-8 months). Easy fade.
- **OKC Thunder:** "Too young to win" folk wisdom. Numbers said amazing team. Bet on them, they won championship.
- **Iran/Strait:** When Israel-Iran conflict hyped, people bet on chaos. Bet status quo - Iran closing strait would be suicidal (25% of GDP from oil exports).

**Quote:** "In betting, if you're reversing stupidity, you're kind of becoming smart"

---

## STRATEGY 2: Longshot Bias Exploitation

**Source:** Quantpedia research, academic studies

**The pattern:** People overpay for underdogs hoping for big payoffs

**The data:** 
- Betting on favorites: -3.64% average loss
- Betting on underdogs: -26.08% average loss
- **Favorites are UNDERPRICED, underdogs OVERPRICED**

**Application:** Bet on heavy favorites at "boring" prices - math works out better

---

## STRATEGY 3: Intra-Market Arbitrage

When YES + NO prices don't sum to $1.00:

- **Buy-all arb:** Sum < $1 → buy everything, guaranteed profit
- **Sell-all arb:** Sum > $1 → sell everything, guaranteed profit
- PredictIt had 55% profit opportunities before they fixed it
- Requires speed - windows close in seconds/minutes

---

## STRATEGY 4: Cross-Platform Arbitrage

Polymarket vs Kalshi price differences:

- Same event, different prices
- Polymarket leads (higher liquidity) 
- Kalshi lags by seconds/minutes
- Spreads of 4-7% documented

### ⚠️ CRITICAL RISK: Different settlement rules!
2024 government shutdown: Polymarket said YES, Kalshi said NO on SAME event due to different resolution criteria. ALWAYS verify settlement rules match.

### Tools:
- ArbitrageHub.org - Real-time scanner
- EventArb.com - Calculator with fees
- Oddpool.com - Scanner with alerts

---

## STRATEGY 5: BTC/Crypto Predictions

**Source:** X/Twitter traders

- One wallet: **$443k profit in ONE MONTH** on Bitcoin up/down
- Another: **$140k/month** with BTC/ETH prediction bot
- Simple binary predictions, high volume
- **Kalshi 15-minute crypto markets** = fast opportunities

---

## STRATEGY 6: Low-Liquidity Edge

**Source:** Reddit r/Kalshi, X traders

- Focus on **low-liquidity political/event markets BEFORE volume floods in**
- Track **probability drift from breaking news or Twitter sentiment**
- Get in early when prices are wrong, exit when volume corrects

---

## STRATEGY 7: Supertrader Approach (Iabvek - $1M+ on Kalshi)

1. **Start with "sharp conventional wisdom"** as baseline
2. **Find what market ISN'T pricing** - weird factors others miss
3. **Read voter files / early vote data** - caught Mamdani's youth surge before polls
4. **Collaboration** - team catches blind spots
5. **Read comment sections** - 10 ideas garbage, 11th might be gold
6. **GO BIG** (within what you can lose) - small bets delude you into thinking you have edge
7. **Kelly criterion** - but understand it doesn't scale perfectly with liquidity

---

## GITHUB REPOS

| Repo | Description | Language |
|------|-------------|----------|
| jtdoherty/arb-bot | Advanced Polymarket-Kalshi arb bot | - |
| dmitryk4/prediction-market-arbitrage | Arb detector | Python |
| earthskyorg/Polymarket-Kalshi-Arbitrage-Bot | Production-ready package | Python |
| CarlosIbCu/polymarket-kalshi-btc-arbitrage-bot | BTC 1-hour arb | - |
| rohitdayanand/bettingarbitrage | Scraping/visualization | Python |
| TopTrenDev/polymarket-kalshi-arbitrage-bot | Arb detection | Rust |
| realfishsam/prediction-market-arbitrage-bot | Auto buy low/sell high | - |

---

## TOOLS & PLATFORMS

| Tool | Purpose | URL |
|------|---------|-----|
| ArbitrageHub | Real-time arb scanner | arbitragehub.org |
| EventArb | Calculator with fees | eventarb.com |
| Oddpool | Scanner with alerts | oddpool.com |
| Prediedge | Whale tracking | polymark.et/product/prediedge |
| Kalshi API | Direct trading | kalshi.com/api |
| Polymarket API | Direct trading | polymarket.com |

---

## KEY INSIGHTS

1. **$40M+ extracted** from Polymarket arbitrage (academic study)
2. **Top 3 arb wallets earned $4.2M combined**
3. **Political markets** = biggest spreads, most profit
4. **Speed matters** - VPS with low latency essential for arb
5. **Fees eat profits** - need 5-6%+ spreads to profit after fees
6. **Settlement risk** - platforms can resolve same event differently

---

## RESEARCH SOURCES

- [Prediction Market Arbitrage Guide 2026](https://newyorkcityservers.com/blog/prediction-market-arbitrage-guide)
- [Kalshi Supertrader Interview](https://news.kalshi.com/p/interview-kalshi-trader-iabvek-new-york-mayor-race)
- [$286 to $1M Reversing Stupidity](https://news.polymarket.com/p/286-to-1m-from-reversing-stupidity)
- [Quantpedia: Systematic Edges](https://quantpedia.com/systematic-edges-in-prediction-markets/)
- [IMDEA $40M Arbitrage Study](https://arxiv.org/abs/2508.03474)

---

## NEXT STEPS

1. [ ] Clone and test arb bots
2. [ ] Set up real-time monitoring
3. [ ] Build probability estimation models
4. [ ] Track breaking news → probability drift
5. [ ] Develop "reversing stupidity" scanner
6. [ ] Create position sizing (Kelly) calculator
