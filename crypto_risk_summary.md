# Crypto Risk Management - Key Findings

## 1. KELLY CRITERION FOR CRYPTO
- **Never use Full Kelly** - too risky for crypto volatility
- **Fractional Kelly**: 10-25% of full calculation (Quarter to One-Tenth Kelly)
- **Formula**: Kelly % = W - [(1-W)/R] where W=win rate, R=risk-reward ratio
- **Example**: 40% win rate, 2:1 R:R → Full Kelly = 10% → Quarter Kelly = 2.5% risk/trade

## 2. OPTIMAL LEVERAGE LEVELS
- **Conservative**: 1-3x (experienced traders)
- **Moderate**: 3-5x (proven strategies)
- **Key Rule**: Maintain same dollar risk regardless of leverage
- **At 5x leverage**: 20% price drop = 100% loss (liquidation)

## 3. STOP LOSS STRATEGIES
### A. ATR-Based Stops (Volatility-Adjusted)
- Stop Distance = ATR × Multiplier
- Multipliers: Scalping 1.0-1.5x, Day trading 1.5-2.0x, Swing 2.0-3.0x

### B. Structure-Based Stops
- Place below support/above resistance
- Distance: 1.5-4% below support based on strength

### C. Trailing Stops
- Fixed %: Simple for trends
- ATR-Based: Adapts to volatility
- Acceleration: Start wide (8%), tighten as profits grow (5%→3%)

## 4. PORTFOLIO CORRELATION MANAGEMENT
- **High correlation** during bear markets
- **Decoupling** during alt-seasons
- **Strategies**: Beta weighting, Risk parity, Clustering
- **Rule**: Max 20-30% in single crypto sector

## 5. PROFESSIONAL TRADER RULES
### Risk Limits:
- **Per trade**: 0.25-2% of account (typically 1%)
- **Daily loss**: 2-5% (stop at 50% of limit)
- **Weekly**: 10-15% max drawdown
- **Monthly**: 20-25% max drawdown

### Position Sizing Formula:
```
Position Size = (Account × Risk %) / (Entry - Stop Loss)
```

### Key Practices:
1. **Always use hard stops** (not mental stops)
2. **Move to breakeven** after 1.5-2× risk achieved
3. **Reduce leverage** during high volatility
4. **Stop trading** after hitting daily loss limit
5. **Weekly review** of all trades and statistics

## 6. IMPLEMENTATION FRAMEWORK
1. **Pre-trade**: Check ATR, support/resistance, correlation
2. **Sizing**: Calculate based on risk % and stop distance
3. **Execution**: Set hard stop, enter trade
4. **Management**: Trail stop, take partial profits
5. **Review**: Update statistics, adjust future sizing

## 7. STARTING PARAMETERS (New Traders)
- Risk/trade: 0.5-1%
- Daily limit: 3%
- Leverage: 1-2x max
- Stop: 2× ATR
- Kelly: One-tenth (10% of full)
- Sector limit: 25% max

## 8. CRITICAL PITFOLIO PROTECTION RULES
1. **Never risk more than 1% on any single trade**
2. **Set and respect daily loss limits** (stop at 50% of limit)
3. **Use volatility-adjusted position sizing** (ATR-based)
4. **Diversify across uncorrelated assets/sectors**
5. **Reduce position size during losing streaks**
6. **Never move stops further away** once set
7. **Take partial profits** at predetermined levels
8. **Keep detailed trade journal** for continuous improvement