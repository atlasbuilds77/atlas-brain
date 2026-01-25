"""
Poseidon Default Configuration

All configurable parameters for backtesting and live trading.
"""

# Account settings
ACCOUNT = {
    "initial_capital": 100000,  # Starting capital
    "commission_per_contract": 0.65,  # Per contract commission
    "slippage_pct": 0.001,  # 0.1% slippage
}

# Risk management
RISK = {
    "max_risk_per_trade_pct": 0.02,  # 2% max risk per trade
    "max_daily_loss_pct": 0.03,  # 3% daily circuit breaker
    "max_position_pct": 0.10,  # 10% max per ticker
    "max_trades_per_day": 10,
    "allow_naked_options": False,  # Defined risk only
}

# TradingAgents configuration
TRADING_AGENTS = {
    "llm_provider": "openai",
    "deep_think_llm": "gpt-4o-mini",
    "quick_think_llm": "gpt-4o-mini",
    "max_debate_rounds": 1,
    "data_vendors": {
        "core_stock_apis": "yfinance",
        "technical_indicators": "yfinance",
        "fundamental_data": "alpha_vantage",
        "news_data": "alpha_vantage",
    },
}

# Backtesting
BACKTEST = {
    "start_date": "2023-01-01",
    "end_date": "2024-12-31",
    "timeframe": "daily",  # or "intraday"
}

# Data sources
DATA = {
    "options_provider": "polygon",  # or "alpaca", "cboe", etc.
    "historical_path": "./data/historical/",
    "live_feed_url": None,  # TBD
}

# Strategy-specific settings
STRATEGIES = {
    "earnings_iv_crush": {
        "enabled": True,
        "min_iv_percentile": 70,  # IV must be > 70th percentile
        "target_dte": 1,  # Target 1 day to earnings
        "spread_width": 5,  # $5 wide spreads
        "target_delta": 0.20,  # 20 delta short strike
    },
    
    "zero_dte_premium": {
        "enabled": True,
        "entry_time": "09:45",  # Entry window start
        "exit_time": "15:45",  # Exit by this time
        "target_delta": 0.10,  # 10 delta (90% PoP)
        "spread_width": 25,  # $25 wide spreads for SPX
    },
}

# Logging
LOGGING = {
    "level": "INFO",  # DEBUG, INFO, WARNING, ERROR
    "file": "./logs/poseidon.log",
    "console": True,
}

# Broker (for live trading - TBD)
BROKER = {
    "name": None,  # "alpaca", "ib", "tastytrade", etc.
    "api_key": None,
    "api_secret": None,
    "base_url": None,
    "paper_trading": True,  # Always start in paper mode
}
