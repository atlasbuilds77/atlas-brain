# Options Greeks - Core Concepts

## Delta (Δ)
- **Definition**: Rate of change of option price relative to underlying asset price
- **Range**: 0 to 1 for calls, -1 to 0 for puts
- **ATM**: ~0.5 for calls, ~-0.5 for puts
- **Trading Implication**: Directional exposure, hedge ratio

## Gamma (Γ)
- **Definition**: Rate of change of delta relative to underlying price
- **Highest**: At-the-money options near expiration
- **Trading Implication**: Convexity, acceleration of profits/losses

## Theta (Θ)
- **Definition**: Time decay of option price
- **Negative**: Options lose value over time (all else equal)
- **Highest**: ATM options near expiration
- **Trading Implication**: Time decay works against long options

## Vega (ν)
- **Definition**: Sensitivity to implied volatility changes
- **Highest**: Longer-dated ATM options
- **Trading Implication**: Volatility exposure, IV crush risk

## Rho (ρ)
- **Definition**: Sensitivity to interest rate changes
- **Generally**: Less significant than other Greeks
- **Impact**: More relevant for long-dated options

## Practical Applications

### Delta Hedging
- Maintain delta-neutral portfolio
- Rebalance as underlying moves
- Common among market makers

### Gamma Scalping
- Profit from large underlying moves
- Buy options when expecting volatility
- Sell options when expecting stagnation

### Theta Decay Strategies
- Sell options to collect premium
- Iron condors, calendars, diagonals
- Manage gamma risk

### Vega Positioning
- Long vega: Buy options before expected IV increase
- Short vega: Sell options before expected IV decrease
- Consider volatility term structure