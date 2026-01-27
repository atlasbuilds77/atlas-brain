# Crypto Low-Risk Strategies: Quick Reference

## Key Mathematical Formulas

### 1. Delta-Neutral Position
```
Net Delta = Σ(Position_i × Delta_i) = 0
```
**Example**: Long 1 BTC spot (Δ=+1) + Short 1 BTC perpetual (Δ=-1) = Δ_net=0

### 2. Funding Rate Arbitrage Income
```
Daily Income = Position × Price × Funding Rate × 3 (for 8-hour intervals)
Annualized Return = (Daily Income × 365) / Capital × 100%
```
**Example**: $50,000 position, 0.03% funding rate:
- Daily: $50,000 × 0.0003 × 3 = $45
- Annual: ($45 × 365) / $50,000 = 32.85%

### 3. Cash-and-Carry Arbitrage Profit
```
Profit = (Futures Price - Spot Price) × Position Size - Fees
Annualized Return = (Profit / Spot Investment) × (365 / Days) × 100%
```
**Example**: $30,000 spot, $30,300 futures (90 days):
- Profit: $300 per BTC
- Annualized: ($300/$30,000) × (365/90) = 4.06%

### 4. Grid Trading Profit per Trade
```
Profit per Trade = Grid Size × Position per Grid × Price
```
**Example**: 1% grid, $1,000 per grid, $30,000 BTC:
- Profit: 0.01 × $1,000 × $30,000 = $300 per completed buy-sell cycle

### 5. Protective Put Hedge
```
Maximum Loss = (Buy Price - Strike Price) + Put Premium
Breakeven = Buy Price + Put Premium
```
**Example**: BTC bought at $30,000, $28,000 put costs $500:
- Max loss: ($30,000 - $28,000) + $500 = $2,500
- Breakeven: $30,000 + $500 = $30,500

### 6. Pairs Trading (Statistical Arbitrage)
```
Spread = Price_Y - β × Price_X
Z-score = (Spread - Mean_Spread) / Std_Spread
Hedge Ratio (β) = Cov(X,Y) / Var(X)
```
**Trading Rule**: Buy spread when Z < -2, sell when Z > 2

## Practical Setups

### Setup 1: BTC Funding Rate Farm
**When**: Funding rate consistently positive (>0.01%)
**Action**: 
1. Buy BTC spot on Exchange A
2. Short equivalent BTC perpetual on Exchange B
3. Collect funding every 8 hours
**Risk**: Rate reversal to negative

### Setup 2: ETH Cash-and-Carry
**When**: Futures premium > 2% annualized
**Action**:
1. Buy ETH spot
2. Short ETH quarterly futures
3. Hold to expiry, capture premium
**Risk**: Basis narrowing before expiry

### Setup 3: Dynamic Grid Trading
**Parameters**:
- Grid size: 1-2% (geometric)
- Grid levels: 10-20 each side
- Reset when price breaks range
**Best for**: High volatility, sideways markets

### Setup 4: Protective Put Portfolio
**For**: Long-term holders
**Action**: Buy ATM or OTM puts for core holdings
**Cost**: 2-5% of position per quarter
**Protection**: Limits downside to strike price

## Risk Management Rules

### 1. Position Sizing
- Single strategy: ≤ 20% of capital
- Per trade risk: ≤ 2% of capital
- Use Kelly Criterion for probabilistic strategies

### 2. Stop-Loss Levels
- Funding arbitrage: Exit if rate turns negative
- Grid trading: Stop if price breaks range by >5%
- Delta-neutral: Rebalance if |Δ_net| > 0.1

### 3. Diversification
- Across strategies
- Across exchanges (Binance, Bybit, KuCoin)
- Across assets (BTC, ETH, major alts)

## Monitoring Checklist

### Daily:
- Check funding rates across exchanges
- Monitor portfolio delta
- Review open grid positions

### Weekly:
- Rebalance delta-neutral positions
- Adjust grid parameters if volatility changes
- Review hedging effectiveness

### Monthly:
- Calculate strategy performance
- Adjust capital allocation
- Update risk parameters

## Common Pitfalls & Solutions

### Problem: Funding rate reversal
**Solution**: Set rate-based stop-loss, monitor trend

### Problem: Delta drift in options
**Solution**: Weekly rebalancing, gamma hedging

### Problem: Grid exhaustion in trends
**Solution**: Dynamic grid reset, wider ranges

### Problem: Exchange downtime
**Solution**: Multiple exchange accounts, API redundancy

## Performance Expectations

### Realistic Returns (After Fees):
- Funding rate arbitrage: 15-30% annualized
- Cash-and-carry: 5-15% annualized  
- Grid trading: 10-25% annualized in sideways markets
- Hedging: Reduces drawdown by 30-50%

### Risk Metrics Target:
- Maximum Drawdown: < 20%
- Sharpe Ratio: > 1.5
- Win Rate: > 55%

## Tools & Resources

### Free Tools:
- Coinglass: Funding rate comparisons
- TradingView: Grid backtesting
- Excel/Google Sheets: Portfolio tracking

### Paid Tools:
- 3Commas: Grid trading bots
- Coinrule: Automated strategies
- Custom Python scripts: Advanced arbitrage

## Final Recommendations

1. **Start Small**: Test with 5-10% of capital
2. **Document Everything**: Track all trades, adjustments
3. **Automate Where Possible**: Use bots for execution
4. **Stay Educated**: Markets evolve, strategies need updating
5. **Risk First**: Never risk more than you can afford to lose

*Remember: These are mathematical strategies, not guarantees. Past performance doesn't guarantee future results. Always do your own research and consider consulting a financial advisor.*