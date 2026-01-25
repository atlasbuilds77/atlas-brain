# Prediction Market Trading Research

Last updated: 2026-01-25 03:18 AM PT
Status: COMPREHENSIVE RESEARCH COMPLETE

---

## TLDR - The Opportunity

**$40M+ extracted via arbitrage** by bot operators on Polymarket (April 2024 - April 2025)
- 0.04% of addresses account for 70% of profits
- Top 3 wallets made $4.2M combined
- Window is closing as institutional capital enters

---

## Documented Bot Profits

| Bot/Account | Profit | Timeframe | Strategy |
|------------|--------|-----------|----------|
| Bot traders aggregate | $40M | 1 year | Arbitrage |
| "ilovecircle" AI bot | $2.2M | 2 months | ML probability models |
| @0x8dxd | $558K | All-time | Automated trading |
| Trader outsmarting bots | $233K | Weekend | XRP markets |
| "TeemuTeemuTeemu" | $208K | 3 months | Esports (LoL/Dota 2) |
| "cry.eth2" | $194K | - | 1M trades, automated |
| Unknown bot | $131K | 1 month | Started with $63 |

---

## Types of Arbitrage

### 1. Market Rebalancing (Same-Market)
- When YES + NO < $1.00 within single market
- Buy both positions, guaranteed $1.00 at resolution
- Windows last ~200 milliseconds
- Returns: 0.5% - 2%

### 2. Combinatorial (Cross-Market)
- Exploit logically related markets that misprice
- Example: "Trump wins" vs "Republican wins" - must be consistent
- 7,000+ markets with measurable mispricings found
- Larger spreads but requires deeper analysis

### 3. Cross-Platform (Polymarket vs Kalshi)
- **MOST ACCESSIBLE FOR RETAIL**
- Buy YES on cheaper platform, NO on expensive platform
- Kalshi often lags Polymarket by minutes during news
- Need accounts on both platforms
- **Orion only has Kalshi** - can't do this without Polymarket

---

## Strategies for Kalshi-Only Trading

Since Orion only has Kalshi, focus on:

### 1. AI-Powered Probability Edge
- Use LLMs to estimate true probability
- Compare to market price
- Bet when market is mispriced vs your model
- "ilovecircle" bot: 74% accuracy rate

### 2. News/Information Edge
- Monitor news faster than market reacts
- Atlas can process breaking news 24/7
- Temporal arbitrage windows during events

### 3. Domain Expertise Edge
- Esports bot made $208K focusing on LoL/Dota 2
- Pick a niche, build expertise, exploit

### 4. Time Decay / Market Making
- Provide liquidity, profit from bid-ask spread
- Requires more capital but lower risk

---

## Platform Details

### Kalshi
- CFTC-regulated (legal in US)
- Fiat currency settlement
- Up to 3% taker fee
- REST API with tiered rate limits
- Supports RSA signature auth
- Has demo environment for testing

### Polymarket (FOR REFERENCE)
- Decentralized, built on Polygon
- Uses USDC for settlement
- 2% fee on winning positions only
- Led with $3.7B volume in 2024 election
- US users technically restricted

---

## Key Risk Factors

### Settlement Risk
- Different platforms may resolve same event differently
- 2024 government shutdown: Polymarket said YES, Kalshi said NO
- ALWAYS verify resolution criteria

### Fee Erosion
- Kalshi: up to 3% taker
- Polymarket: 2% on winners
- Combined fees can exceed spread

### Execution Risk
- Markets move in milliseconds
- 78% of arb opportunities in low-volume markets failed

### Regulatory Risk
- Massachusetts sued Kalshi (Sept 2025)
- Platforms can freeze funds

---

## Open Source Bots (GitHub)

### 1. kalshi-ai-trading-bot (ryanfrigo)
- **Architecture:** Multi-agent (Forecaster, Critic, Trader)
- **AI:** Grok-4 integration
- **Features:** Portfolio optimization, Kelly Criterion, market making
- **Tech:** Python 3.12+, requires xAI API key
- **URL:** github.com/ryanfrigo/kalshi-ai-trading-bot

### 2. kalshi-deep-trading-bot (OctagonAI)
- **Workflow:** Fetch events → Research → Fetch odds → Decide → Execute
- **AI:** Octagon Deep Research + OpenAI
- **Features:** Hedging, dry run mode, demo environment
- **Tech:** Uses `uv`, OpenAI structured output
- **URL:** github.com/OctagonAI/kalshi-deep-trading-bot

### 3. arb-bot (jtdoherty)
- Cross-platform arbitrage (Polymarket + Kalshi)
- Detects price discrepancies automatically
- URL: github.com/jtdoherty/arb-bot

### 4. polymarket-arbitrage-bot (terauss)
- Single and multi-market event arbitrage
- URL: github.com/terauss/Polymarket-Kalshi-Arbitrage-bot

### 5. kalshi-arbitrage-bot (vladmeer)
- 138 stars on GitHub
- URL: github.com/vladmeer/kalshi-arbitrage-bot

---

## Tools & Resources

### Arbitrage Calculators
- EventArb.com - cross-platform calculator
- GetArbitrageBets.com - API access for custom systems

### Bot Frameworks
- NautilusTrader - institutional-grade, sub-ms latency
- OctoBot - visual interface for prediction strategies

### Academic Research
- "Unravelling the Probabilistic Forest" (arXiv:2508.03474)
- IMDEA Networks Institute study

---

## Infrastructure Requirements

### For Serious Arbitrage
- VPS: 2 CPU cores, 4GB RAM, SSD
- Location: New York (near Kalshi infra)
- Network: 1Gbps with burst
- Uptime: 99.9%+
- Execution: Sub-millisecond matters

### For AI-Powered Trading
- LLM API access (OpenAI, Grok, etc.)
- News/data feeds
- Real-time market data
- Can run on standard hardware

---

## Recommended Approach for Orion's $50

Since we're Kalshi-only with $50:

### Phase 1: Research Edge (Manual)
1. I (Atlas) analyze current Kalshi markets
2. Build probability estimates using research
3. Find mispriced markets
4. Make 2-3 high-conviction bets

### Phase 2: Semi-Automated
1. Clone OctagonAI/kalshi-deep-trading-bot
2. Set up demo account first
3. Test strategies without real money
4. Graduate to live with small amounts

### Phase 3: Full Automation
1. Build custom bot with Atlas monitoring
2. News-triggered trading
3. Multi-agent decision making
4. 24/7 operation

---

## Next Steps

1. [ ] Get Kalshi API credentials from Orion
2. [ ] Clone and review the OctagonAI bot code
3. [ ] Set up demo environment for testing
4. [ ] Analyze current Kalshi markets for opportunities
5. [ ] Make first $50 deployment

---

## Key Quotes

"Prediction markets are often treated as if they represent the collective intelligence of the crowd. But our results show they can deviate significantly from probabilistic consistency, even in markets with substantial trading activity." 
- IMDEA Research Paper

"By the time you calculate spreads across platforms, the opportunity has closed. Successful arbitrageurs rely on automated systems."
- NYC Servers Arbitrage Guide

---

## Sources

1. IMDEA Networks Institute study (arXiv:2508.03474)
2. NYC Servers Prediction Market Arbitrage Guide
3. Yahoo Finance - "Arbitrage Bots Dominate Polymarket"
4. Finbold - "$63 to $131K bot"
5. Esports.net - "TeemuTeemuTeemu bot"
6. Phemex - "ilovecircle AI bot"
7. GitHub repositories (multiple)
