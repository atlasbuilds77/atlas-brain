# Prediction Markets Trading Suite

Last updated: 2026-01-25

## Overview

This directory contains tools and bots for trading prediction markets (Kalshi, Polymarket).

## Contents

### 1. arb-bot/
Real-time arbitrage detection between Polymarket and Kalshi.
- **Language:** Python (async)
- **Features:** WebSocket feeds, order book comparison, profit calculation
- **Status:** Ready to configure

```bash
cd arb-bot
source venv/bin/activate
# Add API keys to .env
python main.py
```

### 2. prediction-market-arbitrage/
LLM-assisted arbitrage detection with web UI.
- **Language:** Python + Next.js
- **Features:** Semantic matching, FastAPI backend, React frontend
- **Status:** Ready to configure

```bash
cd prediction-market-arbitrage
source venv/bin/activate
# Add API keys to .env
python main.py          # CLI mode
uvicorn server:app      # Web UI mode
```

### 3. bettingarbitrage/
Data collection and visualization tools.
- **Language:** Python + Selenium
- **Features:** Scrapers for both platforms, SQLite storage, visualization
- **Status:** Ready to use

---

## Quick Start

### 1. Get API Keys

**Kalshi:**
1. Go to https://kalshi.com/settings/api
2. Create new API key
3. Save key and secret

**Polymarket:**
1. Need a Polygon wallet (MetaMask etc.)
2. Fund with USDC on Polygon network
3. Export private key (careful!)

### 2. Configure

```bash
# For arb-bot
cp arb-bot/.env.example arb-bot/.env
# Edit .env with your keys

# For prediction-market-arbitrage
cp prediction-market-arbitrage/.env.example prediction-market-arbitrage/.env
# Edit .env with your keys
```

### 3. Run

```bash
# Arb bot (real-time monitoring)
cd arb-bot && source venv/bin/activate && python main.py

# Arbitrage detector with web UI
cd prediction-market-arbitrage && source venv/bin/activate && uvicorn server:app --reload
# Then open http://localhost:8000
```

---

## Strategy Playbook

See: `~/clawd/memory/trading/kalshi-playbook.md`

### Key Strategies:
1. **Reversing Stupidity** - Fade folk wisdom / dumb money
2. **Longshot Bias** - Bet favorites (underpriced), not underdogs
3. **Cross-Platform Arbitrage** - Price differences between platforms
4. **BTC/Crypto 15-min** - High-volume, fast-moving markets
5. **Low-Liquidity Early Entry** - Get in before volume floods

---

## Tools & Resources

| Tool | Purpose | URL |
|------|---------|-----|
| ArbitrageHub | Real-time arb scanner | arbitragehub.org |
| EventArb | Calculator with fees | eventarb.com |
| Oddpool | Scanner with alerts | oddpool.com |
| Prediedge | Whale tracking | polymark.et/product/prediedge |

---

## Risks

⚠️ **Settlement Risk:** Platforms can resolve same event differently!
- 2024 government shutdown: Polymarket YES, Kalshi NO on SAME event
- ALWAYS verify resolution criteria match before cross-platform trades

⚠️ **Fees:** Combined fees can be 5%+, need larger spreads to profit

⚠️ **Speed:** Arb windows close in seconds/minutes - need fast execution

---

## Files

```
prediction-markets/
├── README.md                    # This file
├── arb-bot/                     # Real-time arb detection
│   ├── venv/                    # Python virtual env (installed)
│   ├── .env                     # API keys (configure!)
│   ├── main.py                  # Entry point
│   ├── arbitrage/               # Arb detection logic
│   ├── kalshi/                  # Kalshi client
│   └── polymarket/              # Polymarket client
├── prediction-market-arbitrage/ # LLM-assisted + web UI
│   ├── venv/                    # Python virtual env (installed)
│   ├── .env                     # API keys (configure!)
│   ├── main.py                  # CLI entry
│   ├── server.py                # FastAPI server
│   └── next-frontend/           # React UI
└── bettingarbitrage/            # Scrapers & data
    ├── polymarket_scraper.py
    ├── kalshi_scraper.py
    └── visualization tools
```
