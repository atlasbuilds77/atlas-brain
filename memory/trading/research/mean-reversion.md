# Mean Reversion Trading Strategies Research

**Research Date:** January 25, 2026  
**Sources:** Web search via Exa/Brave Search API  
**Compiled by:** Clawdbot Subagent

## Table of Contents
1. [Introduction to Mean Reversion](#introduction-to-mean-reversion)
2. [Mean Reversion Strategies for Stocks](#mean-reversion-strategies-for-stocks)
3. [Statistical Arbitrage & Pairs Trading](#statistical-arbitrage--pairs-trading)
4. [RSI Oversold/Overbought Strategies](#rsi-oversoldoverbought-strategies)
5. [Bollinger Band Strategies](#bollinger-band-strategies)
6. [Mean Reversion Backtesting Results](#mean-reversion-backtesting-results)
7. [Key Performance Metrics](#key-performance-metrics)
8. [Risk Management Considerations](#risk-management-considerations)
9. [References](#references)

---

## Introduction to Mean Reversion

Mean reversion is a financial theory suggesting that asset prices and historical returns eventually revert to their long-term mean or average. This phenomenon occurs because markets tend to overreact to news and events, causing prices to move away from their intrinsic values, but over time they correct themselves and move back toward the average.

### Key Principles:
- Prices fluctuate around historical averages
- Significant deviations from the mean create trading opportunities
- Overbought conditions (prices too high) signal potential selling opportunities
- Oversold conditions (prices too low) signal potential buying opportunities
- Works across various asset classes: stocks, commodities, currencies, bonds

---

## Mean Reversion Strategies for Stocks

### 1. **Moving Average Crossover Strategy**
- **Concept:** Compare short-term and long-term Simple Moving Averages (SMAs)
- **Entry Signal:** Short-term SMA crosses above long-term SMA (buy signal)
- **Exit Signal:** Short-term SMA crosses below long-term SMA (sell signal)
- **Timeframes:** Can be adapted from intraday to long-term investments

### 2. **Z-Score Based Strategies**
- **Concept:** Measure how many standard deviations a price is from its mean
- **Formula:** Z = (Price - Mean) / Standard Deviation
- **Typical Thresholds:** 
  - Buy when Z < -2 (oversold)
  - Sell when Z > 2 (overbought)
- **Advantage:** Statistically robust, quantifiable signals

### 3. **Ornstein-Uhlenbeck (OU) Model Strategies**
- **Concept:** Mathematical model for mean-reverting processes
- **Parameters:** Long-term mean, speed of reversion, volatility
- **Application:** Used in quantitative finance for pairs trading and statistical arbitrage
- **Trading Rule:** Enter positions when price deviates significantly from long-term mean

### 4. **High-Performance Example Strategy** (from Reddit/Quantitativo)
- **Indicator:** IBS (Internal Bar Strength) = (Close - Low) / (High - Low)
- **Rules:**
  1. Compute rolling mean of High minus Low over last 25 days
  2. Compute lower band as rolling High over last 10 days minus 2.5 × rolling mean
  3. Go long when SPY closes under lower band AND IBS < 0.3
  4. Close trade when SPY close > yesterday's high
- **Logic:** Market tends to bounce back after dropping too low from recent highs

---

## Statistical Arbitrage & Pairs Trading

### 1. **Pairs Trading Fundamentals**
- **Concept:** Trade two correlated assets when their price relationship deviates
- **Method:** Short the outperforming asset, long the underperforming asset
- **Assumption:** Prices will converge/revert to historical relationship
- **Example Pairs:** Google/Microsoft, Facebook/Twitter, sector peers

### 2. **Cointegration vs Correlation**
- **Correlation:** Measures if prices move in same/opposite direction
- **Cointegration:** Statistical property where linear combination of prices is stationary
- **Key Difference:** Correlated assets may drift apart; cointegrated assets maintain stable relationship
- **Test:** Augmented Dickey-Fuller (ADF) test for stationarity

### 3. **Implementation Steps** (QuantInsti Example)
1. **Pair Selection:** Choose assets with similar fundamentals (sector, market cap)
2. **Cointegration Test:** Use ADF test on price ratio/spread
3. **Signal Generation:** Calculate z-score of normalized ratio
4. **Entry/Exit:** 
   - Enter when z-score crosses ±2 standard deviations
   - Exit when z-score returns to mean
5. **Risk Management:** Set stop-loss at ±3 standard deviations

### 4. **Statistical Arbitrage Variants**
- **PCA-Based:** Use Principal Component Analysis to identify mean-reverting portfolios
- **Machine Learning:** Reinforcement learning for optimal entry/exit timing
- **Multi-Asset:** Extend beyond pairs to triplets or larger portfolios

---

## RSI Oversold/Overbought Strategies

### 1. **Basic RSI Mean Reversion**
- **Standard Levels:** 
  - Overbought: RSI > 70
  - Oversold: RSI < 30
- **Trading Rules:**
  - Sell when RSI crosses above 70 (overbought)
  - Buy when RSI crosses below 30 (oversold)
- **Time Period:** Typically 14-day RSI

### 2. **Advanced RSI Techniques**
- **RSI Divergence:** Price makes new high/low but RSI doesn't confirm
  - Bullish divergence: Price makes lower low, RSI makes higher low
  - Bearish divergence: Price makes higher high, RSI makes lower high
- **RSI Range Adjustment:** 
  - In strong trends: Use 80/20 levels instead of 70/30
  - For mean reversion: Some traders use 75/25 levels

### 3. **Combination Strategies**
- **RSI + Moving Average:** Use RSI for timing, MA for trend confirmation
- **RSI + Bollinger Bands:** RSI < 35 + price touches lower Bollinger Band
- **RSI + Volume:** Confirm oversold/overbought with volume spikes

### 4. **Risk Considerations**
- **False Signals:** RSI can stay extended in strong trends
- **Lagging Indicator:** Reacts to price movements, doesn't predict
- **Confirmation Needed:** Always use with other indicators/analysis

---

## Bollinger Band Strategies

### 1. **Basic Bollinger Band Mean Reversion**
- **Components:** 
  - Middle band: 20-day Simple Moving Average
  - Upper band: SMA + (2 × standard deviation)
  - Lower band: SMA - (2 × standard deviation)
- **Trading Rules:**
  - Buy when price touches or crosses below lower band
  - Sell when price touches or crosses above upper band
  - Exit when price returns to middle band

### 2. **Bollinger Band Squeeze**
- **Concept:** Periods of low volatility (bands contract) often precede big moves
- **Signal:** Bands narrow significantly after expansion
- **Strategy:** Prepare for breakout, then trade reversion after expansion

### 3. **Advanced Bollinger Band Techniques**
- **Band Width:** Monitor band width for volatility changes
- **%b Indicator:** Measures where price is within bands
  - %b = (Price - Lower Band) / (Upper Band - Lower Band)
  - %b < 0: Price below lower band (oversold)
  - %b > 1: Price above upper band (overbought)
- **Multiple Timeframes:** Use daily bands for direction, hourly for entry

### 4. **Combination Strategies**
- **Bollinger Bands + RSI:** Price at band extreme + RSI confirmation
- **Bollinger Bands + MACD:** Band touch + MACD divergence
- **Bollinger Bands + Volume:** Band extreme + volume confirmation

---

## Mean Reversion Backtesting Results

### 1. **High-Performance Strategy Example**
**Source:** Reddit r/algotrading post "A Mean Reversion Strategy with 2.11 Sharpe"

**Backtest Period:** 25 years  
**Asset:** QQQ/SPY  
**Performance Metrics:**
- **Sharpe Ratio:** 2.11
- **Annualized Returns:** 13.0% (vs. 9.2% Buy & Hold)
- **Maximum Drawdown:** 20.3% (vs. 83% B&H)
- **Number of Trades:** 414
- **Average Return/Trade:** 0.79%
- **Win Rate:** 69%
- **Profit Factor:** 1.98

**Strategy Logic:**
- Uses IBS (Internal Bar Strength) indicator
- Combines price level relative to rolling high with volatility bands
- Dynamic stop-loss implementation

### 2. **Pairs Trading Backtest Results**
**Source:** Various quantitative studies

**Typical Performance Range:**
- **Sharpe Ratio:** 1.0 - 2.5
- **Annual Returns:** 5% - 15%
- **Win Rate:** 55% - 70%
- **Maximum Drawdown:** 10% - 25%

**Key Success Factors:**
- Proper cointegration testing
- Adequate lookback period for mean calculation
- Effective risk management (stop-losses)
- Transaction cost consideration

### 3. **RSI Strategy Performance**
**Source:** Various trading communities and backtests

**Findings:**
- Simple RSI oversold/overbought strategies often underperform
- **Reddit finding:** "Tested RSI oversold strategy on 5000 trades - it failed hard"
- **Better approach:** Combine RSI with other indicators
- **Optimized parameters:** Some traders use 75/25 or 80/20 levels instead of 70/30

### 4. **Bollinger Band Strategy Performance**
**Source:** QuantifiedStrategies and trading communities

**Reported Results:**
- **Win Rate:** 60% - 75% for basic band touch strategies
- **Sharpe Ratio:** 0.8 - 1.5 for well-optimized strategies
- **Key Insight:** Works best in ranging markets, suffers in strong trends
- **Improvement:** Adding filters (volume, RSI) improves performance

---

## Key Performance Metrics

### 1. **Sharpe Ratio**
- **Definition:** (Return - Risk-Free Rate) / Standard Deviation
- **Interpretation:**
  - < 0.5: Poor risk-adjusted returns
  - 0.5 - 1.0: Acceptable
  - 1.0 - 2.0: Good
  - > 2.0: Excellent
- **Mean Reversion Targets:** Aim for > 1.0, exceptional strategies > 2.0

### 2. **Maximum Drawdown**
- **Definition:** Largest peak-to-trough decline
- **Acceptable Levels:** 
  - < 20%: Excellent
  - 20% - 30%: Acceptable for mean reversion
  - > 30%: Concerning
- **Comparison:** Should be significantly lower than buy-and-hold

### 3. **Win Rate & Profit Factor**
- **Win Rate:** Percentage of profitable trades
  - Target: 55% - 70% for mean reversion
- **Profit Factor:** Gross Profits / Gross Losses
  - Target: > 1.5 (good), > 2.0 (excellent)
- **Average Win/Loss Ratio:** Should be > 1.0

### 4. **Annualized Returns**
- **Realistic Targets:** 8% - 15% for equity mean reversion
- **Comparison:** Should outperform buy-and-hold with lower risk
- **Consistency:** Look for stable returns across market regimes

---

## Risk Management Considerations

### 1. **Position Sizing**
- **Kelly Criterion:** Optimal bet sizing based on edge
- **Fixed Fractional:** Risk fixed percentage of capital per trade
- **Volatility-Based:** Adjust position size based on asset volatility

### 2. **Stop-Loss Strategies**
- **Fixed Percentage:** e.g., 2% per trade
- **ATR-Based:** Multiple of Average True Range
- **Statistical:** e.g., 3 standard deviations from entry
- **Time-Based:** Exit after fixed holding period

### 3. **Diversification**
- **Across Assets:** Trade multiple uncorrelated pairs/strategies
- **Across Timeframes:** Combine daily, hourly strategies
- **Across Strategies:** Mix mean reversion with trend following

### 4. **Market Regime Awareness**
- **Range-Bound Markets:** Mean reversion excels
- **Trending Markets:** Mean reversion suffers, reduce position sizes
- **Volatility Regimes:** Adjust parameters for changing volatility

### 5. **Transaction Costs**
- **Impact:** More significant for high-frequency mean reversion
- **Optimization:** Consider costs in backtesting
- **Filters:** Avoid trading near support/resistance where slippage is high

---

## References

### Primary Sources:
1. **QuantInsti Blog** - "Mean Reversion Strategies: Introduction, Trading, Strategies and More"
2. **TIOmarkets** - "How to Use Relative Strength Index (RSI) in Mean Reversion Trading?"
3. **Reddit r/algotrading** - "A Mean Reversion Strategy with 2.11 Sharpe"
4. **Quantitativo Substack** - Various mean reversion strategy analyses
5. **arXiv Papers** - Statistical arbitrage and mean reversion research

### Key Concepts from Research:
- **Statistical Arbitrage:** Gatev et al. (2006) - pairs trading when spread exceeds 2 standard deviations
- **OU Model:** Leung and Li (2015, 2016) - parameter estimation for mean reversion trading
- **Cointegration:** Essential for pairs trading success
- **Z-score Normalization:** Standard approach for measuring deviations

### Recommended Further Reading:
1. **Books:** 
   - "Quantitative Trading" by Ernest P. Chan
   - "Algorithmic Trading: Winning Strategies and Their Rationale" by Ernest P. Chan
2. **Courses:** QuantInsti's Mean Reversion Strategies course
3. **Platforms:** QuantConnect for backtesting mean reversion strategies

---

## Conclusion

Mean reversion trading offers statistically grounded approaches to capitalize on temporary market inefficiencies. Key findings from this research:

1. **Effectiveness:** Well-designed mean reversion strategies can achieve Sharpe ratios > 2.0 with controlled drawdowns
2. **Diversity:** Multiple approaches exist - from simple indicator-based to sophisticated statistical arbitrage
3. **Risk Management:** Critical for success due to potential for extended deviations
4. **Market Dependency:** Performance varies by market regime; works best in ranging markets
5. **Continuous Optimization:** Parameters need regular review and adjustment

The most successful implementations combine solid statistical foundations with robust risk management and adapt to changing market conditions.

**Next Steps for Implementation:**
1. Start with simple strategies (RSI/Bollinger Bands)
2. Progress to pairs trading with proper cointegration testing
3. Incorporate machine learning for parameter optimization
4. Always backtest thoroughly before live trading
5. Maintain discipline in risk management