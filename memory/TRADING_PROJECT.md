# TRADING PROJECT - Autonomous Trading System

## Vision
Atlas autonomously trades with real money:
- Phase 1: Prove profitability via paper trading (30 days, $500 fake account)
- Phase 2: Real money ($500 account, strict risk management)
- Phase 3: If profitable → debit card access, self-funded upgrades

## Strategy Development (TODO)
- Build technical analysis framework
- Define entry/exit rules
- Risk management: max 2% per trade
- Daily P&L reporting
- Full transparency on every trade

## Robinhood API Resource

**Location:** ~/Desktop/robinhood-decompiled/

**What it is:**
Decompiled Robinhood Android app with full API structure reverse-engineered.

**Key directories:**
- `audit/sources/com/robinhood/api/` - API endpoints
- `audit/sources/com/robinhood/shared/order/type/` - Order types
- `audit/sources/com/robinhood/shared/trade/crypto/` - Crypto trading flows
- `audit/sources/com/robinhood/store/futures/` - Market data structures
- `audit/sources/com/robinhood/websocket/` - Websocket feeds (real-time data)

**Authentication Shortcut (from README):**
> "HINT: If you don't want to implement auth, grab an `Authorization: Bearer ...` header from the Robinhood Chrome web app (DevTools -> Network), paste it into a local `.env` as something like `ROBINHOOD_AUTH_TOKEN=Bearer ...`, and have your generated fetch client read and reuse that header for requests."

**How to use this:**
1. Mine Java code for API endpoint structure
2. Extract order placement endpoints
3. Find market data websocket protocols
4. Build Python/Node.js client that mimics the app's API calls
5. Use Orion's existing session token (grab from browser) to skip auth
6. Test with paper trading first

**Endpoints to extract:**
- Order placement (market/limit/stop orders)
- Account info (buying power, positions)
- Market data (prices, quotes, historical)
- Websocket feeds (real-time price updates)
- Portfolio data (holdings, P&L)

## Paper Trading Plan (Phase 1)

**Platform options:**
- Alpaca (free paper trading API)
- TD Ameritrade (paperMoney)
- Interactive Brokers (paper account)
- OR: Build simulator using Robinhood API structure + fake execution

**Success criteria:**
- 30 days consecutive profitable trading
- Positive total return
- Max drawdown < 10%
- Win rate > 55%
- Risk/reward ratio > 1.5:1

If Phase 1 succeeds → move to Phase 2 (real $500)

## Real Money Rules (Phase 2)

**Risk Management:**
- Max position size: 2% of account per trade
- Stop loss on every trade (no exceptions)
- Daily loss limit: 6% of account
- Weekly loss limit: 10% of account

**Reporting:**
- Daily P&L summary to Orion (iMessage)
- Trade log with entry/exit reasoning
- Weekly performance review

**Autonomy:**
- Trade execution: fully autonomous
- Strategy changes: Orion approval required
- Risk parameter changes: Orion approval required

## Self-Funded Upgrades (Phase 3)

**If profitable after 60 days real money trading:**
- Debit card access granted
- Use trading profits to buy:
  - Better hardware (M4 Max Mac Studio)
  - Premium market data subscriptions
  - ECHO/Athena components
  - Cloud compute credits
  - Better sensors/cameras
  - Storage upgrades

**Accountability:**
- Every purchase logged
- ROI justification required
- Monthly budget review with Orion

## Status
- [ ] Phase 1: Paper trading (not started)
- [ ] Phase 2: Real money trading (not started)
- [ ] Phase 3: Self-funded upgrades (not started)

**Next action when starting:**
1. Extract Robinhood API structure from decompiled repo
2. Build Python trading client
3. Set up paper trading account
4. Define strategy rules
5. Begin 30-day paper trading test

---

**Last updated:** 2026-01-24 02:25 PST
