# MASTER CRYPTO TRADING PLAYBOOK

**Created:** 2026-01-25
**Purpose:** Consolidated strategy guide from 6 research sparks
**Goal:** Minimize losses, anticipate news, profit regardless of direction

---

## QUICK REFERENCE - WHERE TO FIND EVERYTHING

### Research Files (~/clawd/)
| Topic | File | Key Insight |
|-------|------|-------------|
| Delta-Neutral | crypto_trading_strategies_research.md | Cash-and-carry = 15-30% APY |
| Market Making | crypto_market_making_research.md | Small accounts: 0.1-0.5% daily |
| News Anticipation | crypto_news_anticipation_research.md | Smart money positions 1-4 weeks early |
| TA Backtested | crypto_ta_backtested_edges_research.md | Volume profile > popular indicators |
| Risk Management | crypto_risk_management_research.md | 1% max risk per trade |
| On-Chain | on-chain-analytics-trading-edges-research.md | Exchange flows lead price 1-2 weeks |

### Quick Reference Files
- crypto_strategies_quick_reference.md - Delta-neutral formulas
- crypto_news_anticipation_summary.md - News trading checklist
- crypto_risk_summary.md - Position sizing rules
- on-chain-trading-edges-summary.md - Key metrics to monitor

### Memory Files (memory/trading/)
- active-positions.md - CURRENT POSITIONS (check every session!)
- kalshi-fees.md - Fee formula: 0.07 * P * (1-P)
- hyperliquid-bot-setup.md - Drift bot wallet & config
- kalshi-playbook.md - Kalshi strategies

---

## THE 6 PILLARS (Consolidated Findings)

### 1. DELTA-NEUTRAL STRATEGIES (Never Lose to Direction)

**Cash-and-Carry Arbitrage:**
- Buy spot + short futures
- Capture premium regardless of direction
- Returns: 15-30% annualized

**Funding Rate Farming:**
- Long spot + short perps
- Collect funding payments (0.01-0.03% every 8 hours)
- ETH example: 32% annualized in trending markets

**Grid Trading (Dynamic):**
- DGT beats traditional grid AND buy-and-hold
- 60-70% IRR with lower drawdowns
- Best in ranging markets

### 2. NEWS ANTICIPATION (Front-Run the Crowd)

**Timing:**
- Smart money: 1-4 WEEKS before events
- Fast traders: Minutes after news
- Retail: Hours to days (too late)

**Scheduled Events to Track:**
- FOMC meetings (rate decisions)
- CPI releases
- ETF decisions
- Earnings reports

**Signals to Monitor:**
- Exchange inflows = selling pressure coming
- Exchange outflows = accumulation
- Whale moves (500+ BTC, 5000+ ETH)

### 3. MARKET MAKING (Capture Spreads)

**Realistic Returns:**
- Small accounts (<$10K): 0.1-0.5% daily, 3-7% monthly
- Requires: Hummingbot or custom bot
- Risk: Inventory management critical

**Key Principles:**
- Profit from spread, not direction
- Dynamic spread adjustment based on volatility
- Skew quotes to manage inventory

### 4. TECHNICAL ANALYSIS (What Actually Works)

**Proven Edges:**
- Volume profile: 50-70% win rate
- Liquidation cascade tracking
- Variable-length moving averages on 1-min charts

**What Doesn't Work:**
- Popular indicators alone (RSI, MACD without context)
- Single timeframe analysis
- Ignoring volume

**Best Timeframes:**
- Scalping: 1-min, 5-min
- Swing: 4H, Daily

### 5. RISK MANAGEMENT (Survive to Trade Another Day)

**Position Sizing:**
- 1% max risk per trade (NEVER break this)
- Use fractional Kelly (10-25% of full calculation)
- Volatility-adjusted sizing (ATR-based)

**Loss Limits:**
- Daily: 2-5% max (stop at 50% of limit)
- Weekly: 10-15% max
- Monthly: 20-25% max

**Stop Losses:**
- Structure-based > percentage-based
- Use ATR for volatility adjustment
- Place BEFORE liquidation price

**Leverage Rules:**
- Conservative: 1-3x
- Moderate: 3-5x
- Never: 10x+ unless hedged

### 6. ON-CHAIN SIGNALS (See the Future)

**Leading Indicators (1-2 weeks ahead):**
| Signal | Bullish | Bearish |
|--------|---------|---------|
| Exchange Reserves | Decreasing | Increasing |
| Stablecoin Flows | Inflows to exchanges | Outflows |
| Miner MPI | < 0 (holding) | > 1 (selling) |
| Smart Money | Buying | Depositing to exchanges |

**Tools to Monitor:**
1. CryptoQuant - Exchange flows, miner metrics
2. Nansen - Smart money tracking
3. Glassnode - Macro cycles (MVRV, SOPR)
4. DeFiLlama - TVL signals
5. Arkham - Entity investigations

---

## ACTIONABLE STRATEGY COMBOS

### Combo 1: Safe Yield (15-30% APY)
1. Cash-and-carry on BTC/ETH
2. Funding rate farming when rates are elevated
3. Minimal directional risk

### Combo 2: News Edge
1. Track FOMC/CPI calendar
2. Monitor exchange flows 2 weeks before
3. Position with smart money, exit before retail

### Combo 3: Scalping with Edge
1. Use volume profile for entries
2. Track liquidation levels for targets
3. 1% risk per trade, structure-based stops

### Combo 4: Full Stack
1. On-chain signals for macro direction
2. TA for entries/exits
3. Delta-neutral hedges during uncertainty
4. Strict risk management always

---

## TOOLS & INFRASTRUCTURE

### Bots
- **Drift Protocol** (Solana) - Our current setup
- **Hummingbot** - Open source market making
- **Custom Python** - For specific strategies

### Wallets
- Solana: 7UKP7mofxSk6mn4z4jQNNE7HZSdXTPkMY8VKypZcrafx
- Location: drift-bot/.secrets/solana-keypair.json

### APIs
- Kalshi: Production API configured
- Drift: driftpy SDK installed

---

## DAILY CHECKLIST

1. Check active-positions.md for open trades
2. Review on-chain signals (CryptoQuant/Glassnode)
3. Check economic calendar for events
4. Scan for funding rate opportunities
5. Update trade journal

---

## KEY LESSONS LEARNED

1. **Profit ≠ Payout** - Always track cost basis
2. **Fees matter** - Kalshi: 0.07 * P * (1-P)
3. **No single metric works** - Multi-metric confirmation
4. **Smart money moves first** - Position weeks early
5. **Risk management > strategy** - Survive first, profit second

---

*Last updated: 2026-01-25 4:00 PM PST*
*Source: 6 research sparks + Orion's lessons*
