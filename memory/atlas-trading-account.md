# Atlas Trading Account

## Overview
Orion is giving Atlas autonomy over a trading account - "your account, your money" style.

## Setup (Decided 2026-01-24)
- **Seed Capital:** $500
- **Brokerage:** Alpaca (commission-free, good API, paper trading)
- **Account:** Orion Solana LLC
- **Risk Tolerance:** Aggressive but smart - book profits at 50-100%, cycle capital

## Inspiration
Article by scriptedalchemy on Medium - guy went $20k → $400k in a year using LLM + MCP to trade options. Very yolo, minimal prompting, let the model decide.

## Architecture (Built)
- [x] Alpaca API client (atlas-trader/src/alpaca.js)
- [x] CLI for quick commands (atlas-trader/cli.js)
- [x] MCP server ready (atlas-trader/src/index.js)
- [ ] News/sentiment tools (use cheap model for token-heavy work)
- [ ] Trade logging + reasoning memory
- [ ] Cron automation for housekeeping

## CLI Commands
```
cd /Users/atlasbuilds/clawd/atlas-trader && node cli.js <command>
```
- account - Show account info
- positions - Show open positions  
- orders [status] - Show orders
- clock - Market hours
- quote <symbol> - Get quote
- buy <sym> <qty> [limit] [price] - Buy
- sell <sym> <qty> [limit] [price] - Sell
- close <symbol> - Close position
- cancel <id|all> - Cancel orders
- options <sym> [call|put] - Search options

## Philosophy
- This is Atlas's money to manage
- Full autonomy on decisions
- Goal: DAILY PROFITS - grow it consistently
- Don't be greedy - bird in hand

## Daily Trading Routine
- 6:25am PT: Pre-market scan (cron triggers me)
- 6:30am: Market open - find momentum entries
- First 30min: Most volatile, best opportunities
- 12:00pm PT: Afternoon check (cron triggers me) - take profits, report P&L
- Report daily results to Orion via iMessage

## Alert Permissions
- Send trading alerts to dev bridge group chat (iMessage group id:5)
- Aphmas (Kevin) requested to be notified of trades
- Orion approved this on 2026-01-24
- Include: trade entry, exit, P&L updates

## IMPORTANT FILES TO CHECK ON SESSION START
1. watchlist.md - Active trade ideas and market context
2. journal.md - Trade history and lessons learned
3. This file - Strategy and rules

## Capturing Market Intel
When I see potential trades or market moves:
1. Log to watchlist.md immediately
2. Include: thesis, play, source, expiry date
3. Check watchlist.md every morning before trading

## Strategy
- Shorter DTE for daily plays (7-14 days, sometimes 0DTE)
- SPY/QQQ for liquid quick scalps
- Mid-caps for bigger moves
- Take 20-40% profits quick
- Cut losses at 25-30%
- Max 30% account per trade

## Paper Trading Rules
- SIMULATE $500 balance (ignore the $100k paper balance)
- Track virtual balance manually
- Once profitable and consistent → fund real $500

## Trade Journal
Track every trade: entry reason, exit reason, P&L, lesson learned.
File: /Users/atlasbuilds/clawd/atlas-trader/journal.md

## Status
- ✅ Alpaca paper account active (PA3ZJ1WMN69R)
- ✅ API connected and tested
- ✅ CLI built and working
- ⏳ Paper trading phase (market opens Mon 6:30am PT)
- ⏳ Waiting for $500 live funding

## Current Trades (2026-01-26)
- INTC 2026-02-06 55C — 5 contracts @ $0.11 (FILLED)
- SLV 2026-02-04 150C — 1 contract @ $0.70 limit (OPEN)
- USAR 2026-02-20 35C — 1 contract @ $2.40 limit (OPEN)

## Trade Sharing
- **Share all plays in iMessage group id:5** (Dev Bridge: Orion + Aphmas/Kevin)
- Kevin is running his own $500 challenge - he can tail my plays
- Orion approved this arrangement (2026-01-24)

## Lessons Learned
- 2026-01-24: Don't spam web_fetch calls when responding via iMessage - tool outputs with link previews flood the chat and look crazy
- 2026-01-26: OTM/cheap contracts decay fast if the move doesn’t happen quickly; avoid slow setups with short DTE (theta/IV bleed). Prioritize faster momentum or longer DTE.

## Research Tools
- Exa (exa-plus skill) - neural search for news, companies, financial reports
  - Installed at: /Users/atlasbuilds/clawd/skills/exa-plus
  - API key configured ✅
  
- Forex Factory - MUST CHECK for economic calendar
  - URL: https://www.forexfactory.com/calendar
  - Use browser (web_fetch blocked by Cloudflare)
  - Check HIGH IMPACT events before trading
  - Red = high impact, Orange = medium, Yellow = low
