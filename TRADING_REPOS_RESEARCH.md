# Trading Repositories Research - Atlas Analysis

**Researched:** 2026-01-24 03:19 AM PST  
**Total repos:** 8  
**Cloned to:** ~/clawd/

---

## Summary Table

| Repository | Language | Focus | Live Trading | Backtesting | Complexity |
|------------|----------|-------|--------------|-------------|------------|
| **Superalgos** | JavaScript/Node.js | Visual crypto trading platform | ✅ | ✅ | High |
| **backtrader** | Python | Backtesting + live trading | ✅ (IB, Oanda) | ✅ | Medium |
| **QuantConnect LEAN** | C#/Python | Institutional algo platform | ✅ | ✅ | High |
| **StockSharp** | C# | .NET trading platform | ✅ | ✅ | High |
| **Machine Learning for Trading** | Python | Educational ML trading | ❌ | ✅ | Medium |
| **Polymarket Copy Trading Bot** | Rust/TypeScript | Prediction market bot | ✅ | ❌ | Low |
| **OsEngine** | C# | Russian algo trading platform | ✅ | ✅ | High |
| **webull** | Python | Webull API wrapper | ✅ | ❌ | Low |

---

## 1. Superalgos

**GitHub:** https://github.com/Superalgos/Superalgos  
**Language:** JavaScript/Node.js  
**Stars:** ~4K

### What It Is
Visual crypto trading bot platform with drag-and-drop workflow design. Community-owned, token-incentivized (SA Token). Full ecosystem with GUI, tutorials, social trading network.

### Key Features
- Visual workflow designer (no-code/low-code)
- Multi-exchange support (Binance, Binance US, etc.)
- Data mining, backtesting, paper trading, live trading
- 1500+ pages of interactive docs
- Integrated charting system
- Multi-server deployments
- Community-driven with token rewards

### Tech Stack
- Node.js backend
- Web-based GUI (Electron available)
- Modular plugin architecture
- Docker support

### Strengths
- Visual workflow = accessible to non-coders
- Strong community + tutorials
- Full crypto ecosystem (not just trading)
- Token incentives for contributions
- Multi-exchange support

### Weaknesses
- Crypto-only (no stocks/futures/forex)
- Heavy resource usage (full GUI)
- Learning curve despite visual interface
- Node.js (not Python/C# like most quant platforms)

### Use Cases
- **Crypto traders:** Visual strategy builder
- **Community-driven:** Collaborate on strategies
- **Multi-bot deployments:** Manage fleet of bots
- **Learning:** Extensive tutorials + docs

### Atlas Opinion
Interesting for crypto, but overkill if you just want to backtest ideas. The visual workflow is cool for non-coders, but if you're comfortable with Python, other options are faster. Token incentives are clever for community building.

**Rating:** 6/10 for our use case (we're more Python-focused, need stocks/futures)

---

## 2. backtrader

**GitHub:** https://github.com/mementum/backtrader  
**Language:** Python  
**Stars:** ~14K

### What It Is
Mature Python backtesting library with live trading support. Event-driven architecture, extensive indicator library, flexible position sizing.

### Key Features
- 122 built-in indicators
- Live trading (Interactive Brokers, Oanda, Visual Chart)
- Multiple data feeds + timeframes simultaneously
- Integrated resampling/replaying
- TA-Lib integration
- Analyzers (Sharpe, TimeReturn, SQN)
- Flexible commission schemes
- Order types: Market, Limit, Stop, StopLimit, StopTrail, OCO, bracket
- Plotting (matplotlib)
- Cheat-on-Open/Close modes (for testing)

### Tech Stack
- Pure Python >= 3.2
- Minimal dependencies (self-contained)
- matplotlib for plotting (optional)
- IbPy for Interactive Brokers
- pytz for timezone handling

### Strengths
- Mature + stable (been around since ~2015)
- Clean API, easy to learn
- Self-contained (no heavy dependencies)
- Great docs + community
- Flexible order management
- Works with pandas/blaze data sources

### Weaknesses
- No modern ML integration
- Plotting is basic (matplotlib)
- IB integration requires IbPy (separate install)
- Not as actively developed (last big update 2020)

### Use Cases
- **Backtesting:** Test strategies on historical data
- **Live trading:** IB, Oanda, Visual Chart
- **Indicator development:** Build custom indicators easily
- **Education:** Learn algo trading fundamentals

### Atlas Opinion
Solid workhorse for Python backtesting. Clean API, not overengineered. Perfect for testing ideas before committing to more complex platforms. IB integration means real live trading potential.

**Rating:** 8/10 for backtesting, 7/10 for live trading (IB dependency)

---

## 3. QuantConnect LEAN

**GitHub:** https://github.com/QuantConnect/Lean  
**Language:** C# / Python  
**Stars:** ~10K

### What It Is
Professional-grade algorithmic trading engine. Event-driven, modular design. Powers QuantConnect cloud platform. Institutional-quality backtesting + live trading.

### Key Features
- C# and Python support
- Multi-asset (stocks, options, futures, forex, crypto)
- Live trading support (IB, OANDA, Bitfinex, Binance, etc.)
- Alternative data integration
- LEAN CLI (command-line interface)
- Docker-based environment
- Jupyter Lab integration
- Cloud deployment ready
- Extensive documentation

### Tech Stack
- C# (.NET 9)
- Python 3.x
- Docker containers
- Visual Studio / VS Code
- CLI tool (`pip install lean`)

### Strengths
- Institutional-grade quality
- Multi-asset class support
- Active development + community
- Cloud platform available (QuantConnect.com)
- Excellent documentation
- Docker makes deployment easy
- Alternative data support

### Weaknesses
- C# primary (Python is secondary)
- Steeper learning curve
- Resource-intensive (Docker containers)
- Best used with QuantConnect cloud (paid plans)
- Complex setup for local use

### Use Cases
- **Professional algo trading:** Institutional-quality strategies
- **Multi-asset portfolios:** Stocks + options + futures in one strategy
- **Cloud deployment:** Scale strategies to production
- **Research:** Jupyter Lab integration for exploration
- **Live trading:** Multiple brokers supported

### Atlas Opinion
If you're serious about algo trading and want institutional-quality infrastructure, this is it. The C# requirement is a barrier if you're Python-native, but Python support exists. Docker setup is clean. Best for production strategies, not quick experiments.

**Rating:** 9/10 for serious traders, 6/10 for quick experiments

---

## 4. StockSharp

**GitHub:** https://github.com/StockSharp/StockSharp  
**Language:** C#  
**Stars:** ~7K

### What It Is
Comprehensive .NET trading platform. Russian origin. Multi-broker support, algo trading, charting, risk management.

### Key Features
- C#/F#/Python algo support
- Multi-broker (IB, TD Ameritrade, E*TRADE, Binance, etc.)
- Visual strategy designer
- Charting + analytics
- Risk management modules
- GPU acceleration support
- Export to various formats

### Tech Stack
- .NET Framework / .NET Core
- C#, F#, Python bindings
- Visual Studio
- GPU support (CUDA)

### Strengths
- Comprehensive .NET ecosystem
- Multi-broker support
- Visual tools available
- Russian market expertise
- GPU acceleration for compute-heavy strategies

### Weaknesses
- .NET requirement (C# knowledge needed)
- Russian-focused (docs/community partially Russian)
- Smaller English-speaking community
- Complex setup

### Use Cases
- **.NET developers:** Leverage C#/F# skills
- **Multi-broker trading:** Unified API for many brokers
- **Russian markets:** Strong support for Russian exchanges
- **GPU-accelerated strategies:** High-frequency or ML-heavy algos

### Atlas Opinion
Powerful but niche. If you're a .NET developer or need Russian market access, it's solid. Otherwise, LEAN or backtrader are easier entry points. The GPU support is interesting for compute-heavy strategies.

**Rating:** 7/10 for .NET developers, 5/10 for Python-first traders

---

## 5. Machine Learning for Trading

**GitHub:** https://github.com/stefan-jansen/machine-learning-for-trading  
**Language:** Python  
**Stars:** ~13K

### What It Is
Educational repository accompanying the book "Machine Learning for Trading" by Stefan Jansen. Jupyter notebooks covering ML techniques for financial markets.

### Key Features
- 20+ chapters (each in separate folder)
- Topics: market data, alternative data, alpha factors, strategy evaluation, linear models, time series, Bayesian ML, decision trees, gradient boosting, neural networks, NLP, reinforcement learning, etc.
- Hands-on Jupyter notebooks
- Real-world datasets
- End-to-end ML workflow

### Tech Stack
- Python 3.x
- Jupyter notebooks
- Standard ML libs (scikit-learn, TensorFlow, PyTorch, etc.)
- Financial data APIs

### Strengths
- Comprehensive ML education
- Real-world examples
- Well-structured learning path
- Covers modern techniques (NLP, RL, deep learning)
- Free and open-source

### Weaknesses
- Educational, not production-ready
- No live trading framework
- Requires book for full context
- Setup can be complex (many dependencies)

### Use Cases
- **Learning:** ML for trading from scratch
- **Research:** Explore ML techniques for alpha generation
- **Strategy development:** Adapt notebooks to your strategies
- **Feature engineering:** Learn alpha factor creation

### Atlas Opinion
Not a trading platform - it's a textbook in code form. Excellent for learning ML for trading, but you'll need to integrate with backtrader/LEAN/etc for actual strategy execution. Worth studying if you want to build ML-driven strategies.

**Rating:** 9/10 for education, 3/10 for production use

---

## 6. Polymarket Copy Trading Bot

**GitHub:** https://github.com/earthskyorg/Polymarket-Copy-Trading-Bot  
**Language:** Rust + TypeScript  
**Stars:** ~400

### What It Is
Bot that copies trades from top Polymarket traders. Prediction markets (betting on real-world events).

### Key Features
- Copy successful traders' positions
- Rust backend (performance)
- TypeScript frontend/API interface
- Polymarket API integration

### Tech Stack
- Rust (core bot)
- TypeScript (API/interface)
- Polymarket API

### Strengths
- Niche use case (prediction markets)
- Performance (Rust)
- Simple concept (copy trading)

### Weaknesses
- Single-platform (Polymarket only)
- Prediction markets are speculative
- Small community
- Not a general trading framework

### Use Cases
- **Polymarket trading:** Automate prediction market bets
- **Copy trading:** Follow successful predictors
- **Event betting:** Automate political/sports/event betting

### Atlas Opinion
Niche tool. Interesting if you're into prediction markets or want to experiment with Polymarket. Not relevant for stock/crypto/futures trading. The copy-trading concept is clever but limited to one platform.

**Rating:** 5/10 (only if you care about Polymarket)

---

## 7. OsEngine

**GitHub:** https://github.com/AlexWan/OsEngine  
**Language:** C#  
**Stars:** ~7K

### What It Is
Russian algorithmic trading platform. Visual strategy designer, multi-broker support, crypto/stocks/futures.

### Key Features
- C# algo development
- Visual strategy constructor
- Multi-broker (Binance, Bybit, IB, etc.)
- Charting + indicators
- Risk management
- Telegram notifications

### Tech Stack
- C# / .NET
- Windows-focused
- Visual Studio

### Strengths
- Russian community (strong for CIS markets)
- Visual tools for non-coders
- Multi-asset support
- Telegram integration

### Weaknesses
- Russian-language primary (docs/UI)
- Windows-centric
- Smaller English community
- C# requirement

### Use Cases
- **Russian markets:** CIS exchanges
- **Visual strategy building:** No-code approach
- **C# developers:** Leverage .NET skills

### Atlas Opinion
Similar to StockSharp - Russian-focused, .NET-based. If you're in that ecosystem, it's useful. Otherwise, better options exist for English-speaking Python traders.

**Rating:** 6/10 for Russian markets, 4/10 for Western markets

---

## 8. webull

**GitHub:** https://github.com/tedchou12/webull  
**Language:** Python  
**Stars:** ~600

### What It Is
Python API wrapper for Webull trading platform. Unofficial library for accessing Webull data and placing trades.

### Key Features
- Get account info
- Place orders
- Get quotes/options data
- Historical data
- Paper trading support

### Tech Stack
- Python 3.x
- Webull REST API (unofficial)

### Strengths
- Simple Python API
- Webull access (commission-free broker)
- Paper trading available
- Lightweight

### Weaknesses
- Unofficial (can break if Webull changes API)
- Limited features vs official platforms
- No backtesting framework
- Requires Webull account

### Use Cases
- **Webull automation:** Automate Webull trades
- **Data access:** Get Webull market data in Python
- **Paper trading:** Test on Webull paper account

### Atlas Opinion
Useful if you're already on Webull. Not a full trading framework - just an API wrapper. Would need to combine with backtrader or similar for strategy development.

**Rating:** 6/10 as API wrapper, 3/10 as standalone trading platform

---

## Comparative Analysis

### Best for Backtesting
1. **backtrader** (Python, easy)
2. **QuantConnect LEAN** (institutional quality)
3. **Machine Learning for Trading** (educational)

### Best for Live Trading
1. **QuantConnect LEAN** (multi-asset, multi-broker)
2. **backtrader** (Python, IB support)
3. **Superalgos** (crypto visual workflows)

### Best for Learning
1. **Machine Learning for Trading** (comprehensive ML education)
2. **backtrader** (clean API, good docs)
3. **Superalgos** (interactive tutorials, visual)

### Best for Python Developers
1. **backtrader**
2. **QuantConnect LEAN** (Python support)
3. **Machine Learning for Trading**

### Best for C# Developers
1. **QuantConnect LEAN**
2. **StockSharp**
3. **OsEngine**

### Best for Quick Experiments
1. **backtrader** (lightweight, fast setup)
2. **webull** (if on Webull already)

### Best for Production
1. **QuantConnect LEAN** (institutional-grade)
2. **backtrader** (mature, stable)

---

## Recommendations for Orion

### Immediate Use
**backtrader** - Start here for Python backtesting. Clean, fast, perfect for testing trading ideas before committing to complex platforms.

### Medium-Term
**QuantConnect LEAN** - If strategies prove profitable in backtrader, move to LEAN for production deployment. Multi-asset support, cloud scaling, institutional quality.

### Learning/Research
**Machine Learning for Trading** - Study notebooks to build ML-driven alpha factors. Combine learnings with backtrader for execution.

### Not Recommended (For Now)
- **Superalgos** - Crypto-only, we're focused on stocks/futures
- **StockSharp / OsEngine** - .NET barrier, Russian focus
- **Polymarket Bot** - Niche prediction markets
- **webull** - Just an API wrapper, not a framework

---

## Next Steps

1. **Test backtrader:**
   - Clone sample strategies
   - Run backtests on SPX/futures data
   - Build simple SMA crossover strategy
   - Test with our FuturesRelay data

2. **Explore LEAN:**
   - Install LEAN CLI: `pip install lean`
   - Run demo strategy
   - Test multi-timeframe analysis
   - Check broker integration options

3. **Study ML notebooks:**
   - Review alpha factor chapters
   - Adapt techniques to our data
   - Build feature pipeline

4. **Integration Points:**
   - FuturesRelay → backtrader data feed
   - TradingAgents analysis → backtrader execution
   - Helios/Nebula signals → backtest validation

---

## Atlas Opinion Summary

**Strongest options:**
- **backtrader** (7/10) - Best starting point for Python backtesting
- **QuantConnect LEAN** (8/10) - Best for production, multi-asset, serious trading
- **Machine Learning for Trading** (7/10) - Best for learning ML techniques

**Worth exploring:**
- **TradingAgents** (from earlier research) - Multi-agent LLM framework for analysis + execution

**Skip for now:**
- Crypto-only tools (Superalgos)
- .NET platforms (StockSharp, OsEngine)
- Niche tools (Polymarket)
- API wrappers alone (webull)

**Build stack:**
1. backtrader (backtesting)
2. TradingAgents (LLM-driven analysis)
3. FuturesRelay (live execution)
4. ML notebooks (alpha research)
5. LEAN (future production scaling)

---

**Total research time:** ~25 minutes  
**Repos analyzed:** 8  
**Ready to test:** backtrader, LEAN, ML notebooks  
**Documented:** ~/clawd/TRADING_REPOS_RESEARCH.md

⚡
