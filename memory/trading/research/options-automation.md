# Options Automated Trading Systems Research

*Research conducted on January 25, 2026*

## 1. Options Trading Bots and Platforms

### Commercial Platforms
- **Option Alpha**: Comprehensive platform with bot automation for scanning markets, opening positions, and managing trades. Offers systematic strategy execution with data-driven automations.
- **PeakBot**: Specialized in automated trading for retail investors using time-tested options selling strategies. Offers "hands-free" trading experience with specific bots for Wheel Strategy, Iron Condor, and Trend Spread.
- **TradersPost**: Automated trading bot platform supporting multiple asset classes including stocks, options, and futures. Can trade retirement accounts with automated strategies.
- **tradeSteward**: Service for automated options trading and trade strategy performance tracking, focusing on simplifying complex orders.

### Open Source Bots
- **ThetaGang** (GitHub: brndnmtthws/thetagang): IBKR trading bot that started as a basic implementation of "The Wheel" strategy and evolved into a broader configurable portfolio automation tool. Features include direct share rebalancing, cash management, VIX call hedging, regime-aware rebalancing, and exchange-hours gating. Available as Docker container and PyPI package.
- **LoopTrader** (GitHub: pattertj/LoopTrader): Extensible options trading bot built on Python.
- **PyOptionTrader** (GitHub: ldt9/PyOptionTrader): Options trader written in Python based on the ib_insync library for Interactive Brokers.

## 2. Automated Wheel Strategy Implementations

### Commercial Solutions
- **PeakBot Wheel Bot**: Dedicated automation for the Wheel strategy with hands-free trading, generating consistent income through premium collection.
- **Option Alpha**: Supports Wheel strategy automation through their bot system.

### Open Source Implementations
- **ThetaGang**: Originally built specifically for the Wheel strategy on Interactive Brokers. Includes risk management features and supports modified Wheel strategy.
- **Alpaca Options Wheel** (GitHub: alpacahq/options-wheel): Runnable algo template for trading the classic "wheel" options strategy using Alpaca Trading API with minimal manual work. Automatically picks puts/calls to sell, tracks positions, and moves through the wheel cycle. Includes configuration for symbol selection and paper trading support.
- **WheelStrategy** (GitHub: jchaffraix/WheelStrategy): Test bot implementing the options wheel strategy.
- **Robinhood Wheel Strategy** (GitHub topic): Python command-line program leveraging Robinhood accounts to assist in choosing options for the wheel strategy.

## 3. Options Backtesting Frameworks

### Python Frameworks
- **Backtesting.py**: Python framework for inferring viability of trading strategies on historical data. Lightweight and popular.
- **Backtrader**: Feature-rich Python framework for backtesting and trading with reusable strategies, indicators, and analyzers.
- **bt**: Flexible backtesting framework for Python that allows creating strategies mixing different algorithms.
- **PyAlgoTrade**: Mature, fully documented backtesting framework with paper- and live-trading capabilities.
- **Optopsy** (GitHub: michaelchu/optopsy): Nimble options backtesting library specifically for Python.
- **OptionLab** (GitHub: rgaveiga/optionlab): Python library for evaluating option trading strategies.

### Other Notable Frameworks
- **Finmarketpy**: Object-oriented model for backtesting, though relies on sample code for documentation.
- **vectorbt**: Pandas-based library for quickly analyzing trading strategies at scale.
- **AutoTrader**: Automated trading framework with emphasis on cryptocurrency markets, includes robust backtesting API.

## 4. APIs for Options Trading

### Broker APIs
- **Interactive Brokers (IBKR)**: Comprehensive API with global market access, complex orders, and strong developer support. Requires $500 minimum deposit for API access.
- **TD Ameritrade/Schwab**: API currently in transition after Schwab merger. New user registration disabled; existing API being migrated to Schwab Trader API program.
- **Tradier**: Robust API offering with options trading capabilities.
- **TradeStation**: Requires $10k minimum for API access.
- **Alpaca**: Offers Trading API with options support through their options-wheel template.

### API Libraries
- **tda-api** (GitHub: alexgolec/tda-api): Python client for TD Ameritrade API including historical data, options chains, streaming order book data, and complex order construction.
- **ib_insync**: Python library for Interactive Brokers API, used by PyOptionTrader and other projects.

## 5. Open Source Options Trading Code

### GitHub Repositories
- **options-trading** (GitHub topic): Collection of repositories including high-frequency trading, Greeks calculation, TWS API integration, and option strategy evaluation.
- **Options-Trading-Strategies-in-Python** (GitHub: PyPatel/Options-Trading-Strategies-in-Python): Developing options trading strategies using technical indicators and quantitative methods.
- **Options_Trading_ML** (GitHub: nataliaburrey/Options_Trading_ML): Machine learning options trading algorithm with API calls to Yahoo Finance, Sentiment Investor, and Finta.
- **openalgo** (GitHub: marketcalls/openalgo): Open source algo trading platform with node-based visual strategy editors.

### Libraries and Tools
- **OptionLab**: Free, open-source Python library for evaluating option trading strategies.
- **PyAlgoTrade**: Python algorithmic trading library with focus on backtesting and support for paper/live trading.

## Key Findings and Recommendations

### For Beginners
1. **Start with Option Alpha or PeakBot** for commercial solutions with user-friendly interfaces
2. **Use Backtesting.py or Backtrader** for initial strategy testing
3. **Consider Alpaca's options-wheel template** as a starting point for automation

### For Developers
1. **Interactive Brokers API** is the most comprehensive for options trading
2. **ThetaGang** provides a solid foundation for Wheel strategy automation
3. **Optopsy and OptionLab** are specialized for options backtesting

### Current Limitations
1. **TD Ameritrade API transition** to Schwab creates uncertainty for existing implementations
2. **Limited open-source options data** due to diversity of historical data and few applications
3. **Broker API minimums** can be prohibitive (TradeStation $10k, IBKR $500)

### Future Research Areas
1. Integration of machine learning with options trading strategies
2. Real-time options data processing and analysis
3. Multi-broker API abstraction layers
4. Cloud-based options trading infrastructure

## References
- Option Alpha: https://optionalpha.com/
- PeakBot: https://peakbot.com/
- ThetaGang: https://github.com/brndnmtthws/thetagang
- Backtesting.py: https://kernc.github.io/backtesting.py/
- Interactive Brokers API: https://www.interactivebrokers.com/
- Alpaca Options Wheel: https://github.com/alpacahq/options-wheel