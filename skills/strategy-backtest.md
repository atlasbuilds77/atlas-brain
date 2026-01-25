# Strategy Backtest Skill

## Purpose
Analyze and optimize trading strategies (Nebula, Helios, etc.)

## Tools
- TradingView Pine Script (primary)
- Python backtesting libraries (secondary)
- Historical data from Polygon

## Analysis Framework

### 1. Performance Metrics
- Win rate (target: >55%)
- Profit factor (target: >1.5)
- Max drawdown (limit: <20%)
- Sharpe ratio (target: >1.0)
- Average win vs average loss

### 2. Trade Analysis
- Best performing setups
- Worst performing setups
- Time of day performance
- Day of week patterns
- Volatility impact

### 3. Optimization Areas
- Entry conditions
- Exit conditions
- Position sizing
- Stop loss placement
- Take profit levels
- Filters (trend, volatility)

## Pine Script Review Checklist
- [ ] Logic matches intended strategy
- [ ] No look-ahead bias
- [ ] Proper order execution
- [ ] Realistic slippage/commission
- [ ] Alert conditions correct

## Reporting Template
```
## Strategy Analysis: [Name]

### Summary
- Period: [dates]
- Total trades: [N]
- Win rate: [X]%
- Profit factor: [Y]

### Strengths
- [What's working]

### Weaknesses
- [What's not working]

### Recommendations
1. [Specific change]
2. [Specific change]

### Code Changes (if any)
[Pine Script diff or modifications]
```
