# Position Sizing for Leverage Trading: Quick Reference

## Core Principle
**Leverage does NOT change position size calculation.** Calculate risk based on actual account balance, not leveraged amount.

## Three Main Methods

### 1. Kelly Criterion (Mathematical Optimal)
**Formula:** `f* = (bp - q) / b` or `Kelly % = (W × R - L) / R`
- `W` = win rate, `L` = 1-W, `R` = avg win/avg loss
- **Example:** 55% win rate, 1.5 reward/risk → 25% Kelly
- **Practical:** Use 25-50% of Full Kelly (Half/Quarter Kelly)

### 2. Fixed Fractional (Simple Percentage)
**Formula:** `Position Size = (Account × Risk%) / Stop Loss Distance`
- **Risk % Guidelines:**
  - 5x leverage: 2% max
  - 10x leverage: 1.5% max  
  - 20x leverage: 1% max
- **Example:** $10k account, 2% risk, $5 stop distance → 40 shares

### 3. Volatility-Based (ATR Method)
**Formula:** `Position Size = (Account × Risk%) / (ATR × Multiplier × Price)`
- **ATR Multiple:** 1-3× (higher for tighter stops)
- **Adjust for volatility:** Reduce size when ATR is high

## Critical Leverage Considerations

### Liquidation Cushions
- 5x: ~20% cushion before liquidation
- 10x: ~10% cushion  
- 20x: ~5% cushion
- **Stop loss MUST be placed before liquidation price**

### Position Size Examples with Different Leverage

**5x Leverage (Conservative):**
- Account: $10,000
- Risk: 2% = $200
- Entry: $50, Stop: $48 ($2 distance)
- Position: 100 shares ($5,000 value)
- Margin: $1,000, Actual leverage: 5x

**10x Leverage (Standard):**
- Account: $10,000  
- Risk: 1.5% = $150
- Entry: $100, Stop: $97 ($3 distance)
- Position: 50 shares ($5,000 value)
- Margin: $500, Actual leverage: 10x

**20x Leverage (Aggressive):**
- Account: $10,000
- Risk: 1% = $100
- Entry: $200, Stop: $196 ($4 distance)
- Position: 25 shares ($5,000 value)
- Margin: $250, Actual leverage: 20x

## Universal Formula
```
Position Size = (Account Balance × Risk Percentage) / |Entry Price - Stop Loss Price|
```

## Recommended Approach for 5-20x Leverage
1. **Start with 1-2% risk** of account balance
2. **Reduce risk as leverage increases:** 5x→2%, 10x→1.5%, 20x→1%
3. **Calculate stop loss** based on technicals or ATR (1-3×)
4. **Verify stop is before liquidation** (calculate liquidation price first)
5. **Use tighter stops** with higher leverage to maintain position size

## Key Takeaways
1. **Never risk more than 3%** per trade regardless of leverage
2. **Higher leverage = smaller risk percentage**
3. **Stop loss placement is critical** - must trigger before liquidation
4. **Position size depends on stop distance, not leverage**
5. **Volatility matters more** with high leverage - reduce size in volatile markets