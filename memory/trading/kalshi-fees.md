# Kalshi Fee Structure

## Taker Fee Formula
```
Fee = 0.07 × P × (1-P)
```
Where P = contract price (0.16 for 16c)

## Fee by Price Point
| Price | Fee/Contract |
|-------|-------------|
| 5c | 0.33c |
| 10c | 0.63c |
| 16c | 0.94c |
| 25c | 1.31c |
| 50c | 1.75c (MAX) |
| 75c | 1.31c |
| 80c | 1.12c |
| 90c | 0.63c |
| 95c | 0.33c |

## Key Insights

### 1. Fees are LOWEST at the tails
- Trading longshots (5-15c) or near-locks (85-95c) = cheaper
- 50c contracts = most expensive to trade

### 2. Maker vs Taker
- **Taker:** Hits existing orders, pays full fee
- **Maker:** Posts limit orders, may pay lower/no fee
- To reduce fees: Post limit orders and let them fill

### 3. Spread Costs
- Bid/ask spread is ANOTHER cost on top of fees
- Wide spreads hurt round-trip profitability
- Check spread before trading

### 4. Interest on Positions
- Kalshi pays ~4% APY on position value
- Helps offset costs for longer-term holds

## Trading Implications

1. **For scalping:** Prefer tail prices, be a maker when possible
2. **For longshots:** Fee structure favors these trades
3. **For market making:** Post both sides, collect spread, minimize fees
4. **Avoid:** Frequently trading 50c contracts (max fees)

## Example: My NYC Temp Trade
- 38 contracts @ 16c
- Fee per contract: 0.94c
- Total fees: ~36c
- Cost basis: $6.08 + $0.36 = $6.44

---
*Learned: 2026-01-25 via Orion feedback*
