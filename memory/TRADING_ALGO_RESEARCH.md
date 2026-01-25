# Trading Algorithm Research - 2026-01-24

Deep dive into trading platforms, algos, and tools. Ranked by usefulness for our needs.

---

## TL;DR - TOP PICKS

| Platform | Best For | Language | Live Trading |
|----------|----------|----------|--------------|
| **QuantConnect LEAN** | Serious backtesting + live | Python/C# | Yes (multi-broker) |
| **NautilusTrader** | High-performance, production-grade | Python/Rust | Yes |
| **Alpaca** | Options + stocks API, zero commission | Python | Yes |
| **Freqtrade** | Crypto bots | Python | Yes |
| **Jesse** | Crypto strategy research | Python | Yes |
| **OptionAlpha** | Options automation, no-code | Visual | Yes (Tradier/TradeStation) |

---

## 1. QUANTCONNECT / LEAN (RECOMMENDED)

**What:** World's leading open-source algo trading platform. Used by hedge funds.

**GitHub:** 16K stars, very active development

**Key Features:**
- Python AND C# support
- Backtest on cloud OR locally
- Multi-asset: stocks, futures, options, crypto, forex
- Connect to: IB, Tradier, Alpaca, Coinbase, many more
- Free tier available
- Alpha licensing to hedge funds (monetize your strategies)
- Recent updates: SS&C Eze support, IDE integrations (Copilot, Cursor)

**Pros:**
- Production-grade, institutional quality
- Massive community and documentation
- Free cloud backtesting with their data
- Same code for backtest and live

**Cons:**
- Steeper learning curve
- Cloud compute limits on free tier
- C# is more performant but Python is easier

**Install:**
```bash
pip install lean
lean init
lean backtest "My Strategy"
```

**Verdict:** Best all-around platform for serious algo development. Already cloned to ~/clawd/Lean.

---

## 2. NAUTILUSTRADER (HIGH PERFORMANCE)

**What:** High-performance trading platform with Rust core, Python API.

**GitHub:** Active development, production-grade

**Key Features:**
- Core written in Rust (FAST)
- Python API for strategy development
- Event-driven backtesting engine
- Multi-venue, multi-asset
- Same code for backtest and live trading
- Sub-millisecond latency

**Pros:**
- Blazing fast (Rust core)
- Professional-grade architecture
- Great for HFT-adjacent strategies
- Clean Python API

**Cons:**
- Smaller community than QuantConnect
- More complex setup
- Fewer broker integrations out of box

**Install:**
```bash
pip install nautilus_trader
```

**Verdict:** If you need SPEED. Great for futures/options with tight execution requirements.

---

## 3. ALPACA (OPTIONS + STOCKS API)

**What:** Developer-first brokerage API. Zero commission.

**Key Features:**
- FREE options and stock trading API
- Multi-leg options strategies (spreads, condors, straddles)
- Real-time + historical data
- Paper trading for testing
- REST and WebSocket APIs
- 24/5 extended hours trading

**Pros:**
- Zero commission
- Excellent Python SDK (alpaca-py)
- Paper trading for strategy testing
- Options support is solid
- Easy to get started

**Cons:**
- US only
- No futures (stocks, options, crypto only)
- Data can be delayed on free tier

**Install:**
```bash
pip install alpaca-py
```

**Code Example (Iron Condor):**
```python
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import OptionOrderRequest

client = TradingClient(api_key, secret_key)

# Multi-leg order for iron condor
order = OptionOrderRequest(
    symbol="SPY",
    qty=1,
    side="sell",
    type="market",
    legs=[
        {"symbol": "SPY250131P00580000", "qty": 1, "side": "buy"},
        {"symbol": "SPY250131P00590000", "qty": 1, "side": "sell"},
        {"symbol": "SPY250131C00620000", "qty": 1, "side": "sell"},
        {"symbol": "SPY250131C00630000", "qty": 1, "side": "buy"},
    ]
)
```

**Verdict:** Excellent for options algo development. Zero cost to trade. Good for Poseidon project.

---

## 4. OPTIONALPHA (NO-CODE OPTIONS)

**What:** Visual options trading automation. No coding required.

**Key Features:**
- Drag-and-drop bot builder
- Pre-built bot templates
- Backtesting included
- Community sharing
- Works with Tradier or TradeStation
- Natural language "recipes"

**Pros:**
- No coding needed
- Great for testing options strategies quickly
- Strong community
- Good documentation

**Cons:**
- Less flexible than custom code
- Limited to their supported brokers
- Not open source

**Verdict:** Great for prototyping options strategies without code. Can validate ideas before coding them in Python.

---

## 5. FREQTRADE (CRYPTO)

**What:** Most popular open-source crypto trading bot. Python.

**GitHub:** 46K stars (massive community)

**Key Features:**
- Supports 100+ exchanges
- FreqAI: Machine learning integration
- Telegram/WebUI control
- Extensive backtesting
- Hyperparameter optimization
- Strategy repository (freqtrade-strategies)

**Pros:**
- Huge community
- Very well documented
- ML integration built-in
- Active development

**Cons:**
- Crypto only (no stocks/options)
- Can be complex to configure

**Install:**
```bash
pip install freqtrade
freqtrade new-config
freqtrade new-strategy --strategy MyStrategy
```

**Verdict:** Best for crypto trading. Not relevant for SPX options but excellent for crypto portfolio.

---

## 6. JESSE (CRYPTO RESEARCH)

**What:** Advanced crypto trading framework focused on strategy research.

**GitHub:** 7.3K stars

**Key Features:**
- Clean Python API
- Advanced backtesting
- Strategy optimization
- AI/ML built-in
- Live trading support
- Great documentation

**Pros:**
- Very clean API
- Focus on research quality
- Good for developing and testing ideas
- AI integration

**Cons:**
- Crypto only
- Smaller than Freqtrade

**Verdict:** Great for serious crypto strategy research. If doing crypto, consider alongside Freqtrade.

---

## 7. PINE SCRIPT (TRADINGVIEW)

**What:** TradingView's proprietary scripting language.

**Pros:**
- Quick prototyping
- Huge indicator library
- Visual backtesting
- Easy to learn

**Cons:**
- Locked to TradingView ecosystem
- Limited execution options
- Can't deploy to your own servers
- Different data than other platforms

**Verdict:** Good for quick idea validation. Migrate to Python (QuantConnect/Alpaca) for production.

---

## 8. OTHER NOTABLE TOOLS

### CCXT
- Universal crypto exchange API (100+ exchanges)
- Python/JS/PHP
- 41K GitHub stars
- Essential if building crypto bots

### TA-Lib
- Technical analysis library
- 130+ indicators
- Python wrapper: `pip install TA-Lib`
- Industry standard

### Hummingbot
- Market making and arbitrage bot
- Crypto focused
- 16K GitHub stars

### backtrader
- Python backtesting (already cloned)
- 122 indicators
- Good for quick tests

---

## RECOMMENDED STACK FOR POSEIDON

Based on your SPX options focus:

1. **Research/Backtest:** QuantConnect LEAN (free cloud tier)
2. **Live Options Trading:** Alpaca API (zero commission)
3. **Prototyping:** OptionAlpha (no-code validation)
4. **Data:** Alpaca real-time + Polygon.io for options chains
5. **Analysis:** TradingAgents (already set up) for LLM-driven thesis

### Development Flow:
```
Idea → OptionAlpha (quick test) → QuantConnect (backtest) → Alpaca (paper) → Alpaca (live)
```

---

## NEXT STEPS

1. **Set up Alpaca paper trading account** - free, great for options
2. **Get QuantConnect API key** - free tier for cloud backtests
3. **Test OptionAlpha** - connect Tradier for quick prototyping
4. **Build first Poseidon strategy** - start with 0DTE credit spreads
5. **Clone NautilusTrader** - if need high-performance execution later

---

## RESOURCES

### Ranked GitHub Lists
- github.com/merovinh/best-of-algorithmic-trading (93 projects, updated weekly)

### Books (Top Picks)
- "Machine Learning for Algorithmic Trading" - ML signals
- "Algorithmic Trading: Winning Strategies" - Ernie Chan classic
- "Python for Algorithmic Trading" - practical deployment

### YouTube
- Part Time Larry - Python trading tutorials
- The Art of Trading - Pine Script
- Moon Dev - coding + finance
- Algo Trading with Kevin Davey - futures strategies

---

*Research completed: 2026-01-24 21:00 PST*
*Next update: After testing Alpaca options API*
