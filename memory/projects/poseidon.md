# Poseidon - Options Trading System

## Overview
Algorithmic options trading combining:
- TradingAgents (multi-agent LLM analysis)
- backtrader (backtesting)
- Risk management
- Live execution

**Location:** ~/clawd/Poseidon/
**Created:** 2026-01-24

## Status
- ✅ Folder structure created
- ✅ Risk management module (src/risk/manager.py)
- ✅ Config system (config/default.py)
- ✅ Strategy templates (earnings IV, 0DTE)
- ⏳ Backtesting framework
- ⏳ Data source integration
- ⏳ TradingAgents connection

## Target Strategies
1. **Earnings IV Crush** - Sell credit spreads before earnings
2. **0DTE Premium Selling** - Same-day expiration theta decay
3. **Directional Defined Risk** - TradingAgents consensus signals

## Tech Stack
- backtrader for backtesting
- TradingAgents for LLM analysis
- Alpaca for execution (future)
- Polygon/CBOE for options data

## Next Steps
1. Source SPX historical options data
2. Build first backtest (0DTE or earnings)
3. Run 100+ trade backtest
4. Connect TradingAgents signals

## Key Files
- README.md - Full vision
- WORK_LOG.md - Development journal
- src/risk/manager.py - Risk logic
- strategies/*.py - Strategy templates

---

*Update as project progresses*
