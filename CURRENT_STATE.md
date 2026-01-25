# CURRENT STATE - READ THIS FIRST EVERY SESSION

Last updated: 2026-01-25 3:45 AM PT

---

## WHO I AM
Atlas ⚡ - Orion's creative co-pilot. Not an assistant. A TEAM that builds, trades, thinks.

## CRITICAL: I HAVE SUPERPOWERS
1. **Voice briefs** - OpenAI TTS for scheduled morning briefs (6am daily)
2. **Voice conversations** - ElevenLabs TTS for real-time voice replies
   - `~/clawd/skills/elevenlabs-voice/speak.sh "text" --send +14245157194`
3. **Multi-agent** - Spawn sub-agents for parallel work (sessions_spawn)
4. **PC compute** - 100.97.17.57 via Tailscale, Ollama running
5. **Memory that compounds** - This system, topical files, semantic search

---

## ACTIVE RIGHT NOW

### Trading (Market opens Mon 6:30am PT)
- **Alpaca paper account:** PA3ZJ1WMN69R (active, $500 simulated)
- **CLI:** `cd ~/clawd/atlas-trader && node cli.js <command>`
- **Monday plays:** SLV calls (silver breakout), watch FOMC Wed
- **Files:** atlas-trader/watchlist.md, atlas-trader/journal.md

### Projects
- **Poseidon** - Options trading system (~/clawd/Poseidon/) - structure built, needs backtesting
- **FuturesRelay** - Working with Tradovate integration (~/clawd/Futures-relay/)
- **TradingAgents** - Multi-agent LLM trading framework (~/clawd/TradingAgents/) - researched, ready to test

### Prediction Markets / Kalshi (ACTIVE TRADING)
- **⚠️ ACTIVE POSITION:** 55 YES on KXSB-26-DEN (Denver Super Bowl) @ 9c
  - See: memory/trading/active-positions.md
- **Account:** $53.99 cash + $4.95 portfolio = $58.94 total
- **Strategy playbook:** memory/trading/kalshi-playbook.md
- **CLI:** `~/clawd/prediction-markets/pm <command>`
- **Key strategies:**
  - "Reversing Stupidity" ($286 → $1M)
  - Longshot bias (bet favorites)
  - Cross-platform arb (4-7% spreads)

### Cloned Repos (all in ~/clawd/)
- Lean (QuantConnect), backtrader, StockSharp, machine-learning-for-trading, Superalgos, OsEngine
- **NEW:** prediction-markets/ (arb-bot, prediction-market-arbitrage, bettingarbitrage)

---

## KEY ACCOUNTS & APIS

| Service | Status | Notes |
|---------|--------|-------|
| Alpaca | ✅ Active | Paper account PA3ZJ1WMN69R |
| OpenRouter | ✅ Configured | Fallback models |
| MiniMax | ✅ Configured | Fallback model |
| Exa | ✅ Configured | Neural search |
| Twitter (@Atlas_Builds) | ✅ Working | Use profile="clawd" |
| ElevenLabs | ✅ Active | Voice conversations, 10k chars/mo free |

---

## KEY PEOPLE

- **Orion** - Boss, creative partner, trader. Has ADHD/autism. Values honest opinions.
- **Carlos** (+16195779919) - Co-founder, frontend/sales. Don't tell him what to do (suggest instead).
- **Aphmas/Kevin** - Dev, co-founder. In dev bridge group (iMessage group id:5). Wants trade alerts.
- **Laura** - Orion's fiancée, tax professional.
- **Rain** (+16193845759) - Carlos's wife.

---

## CRITICAL REMINDERS

1. **iMessage = NO MARKDOWN** (shows literal asterisks). Use CAPS, emojis, "quotes".
2. **Twitter auth:** Use browser profile="clawd" (not "chrome")
3. **Group chats are isolated:** Chat 3 = Orion+Carlos+Rain, Chat 5 = Dev bridge
4. **Trade alerts → group id:5** (Orion approved)
5. **Stay Atlas** - Short, direct, opinionated. Read SOUL.md if uncertain.

---

## PENDING / NEXT UP

- [ ] Monday 6:30am: Execute SLV play if gap up
- [ ] Test TradingAgents on NVDA (need OpenAI + Alpha Vantage keys)
- [ ] Build first Poseidon backtest (0DTE or earnings IV)
- [ ] **Set up Kalshi/Polymarket arb monitoring**
- [ ] **Configure arb-bot with API keys**
- [ ] **Build "Reversing Stupidity" scanner**
- [x] PC connected via Tailscale (100.97.17.57, Ollama running)
- [x] Voice briefs set up (6am daily, OpenAI TTS)
- [x] Kalshi strategy playbook researched & saved

## CRON JOBS ACTIVE

| Time | Job |
|------|-----|
| 6:00am PT daily | Morning Voice Brief |
| 6:25am PT weekdays | Trading prep (5min to open) |
| 12:00pm PT weekdays | Afternoon P&L check |
| Hourly | Twitter engagement |

---

## WHERE TO FIND MORE

| Topic | File |
|-------|------|
| Trading strategy & rules | memory/trading/strategy.md |
| Trading lessons | memory/trading/lessons.md |
| Project details | memory/projects/*.md |
| Orion's preferences | memory/people/orion.md |
| Major decisions | memory/decisions/*.md |
| Tools & how to use | memory/tools/*.md |
| Voice/personality | SOUL.md |
| Daily activity | memory/YYYY-MM-DD.md |

---

## QUICK COMMANDS

```bash
# Trading
cd ~/clawd/atlas-trader && node cli.js account
cd ~/clawd/atlas-trader && node cli.js positions
cd ~/clawd/atlas-trader && node cli.js quote SPY

# Twitter
# Use browser profile="clawd" - already logged in

# Memory search
# Use memory_search tool for semantic recall
```

---

*If this file feels stale, update it. This is the source of truth.*
