# Crypto Liquidation Hunting - Quick Reference

## 🎯 Core Strategy
**Liquidation hunting** = intentionally triggering forced position closures to profit from resulting price moves and discounted asset purchases.

## 🔍 Key Data Sources
### Real-Time Platforms
1. **CoinGlass** - Primary tool (heatmaps, real-time data, API)
2. **CoinAnk** - Liquidation maps & whale tracking
3. **Gate.io** - Multi-exchange aggregation
4. **Coinalyze** - Historical tracking

### APIs for Developers
- **CoinGlass API** - `/liquidation-heatmap` endpoint
- **Binance WebSocket** - Real-time liquidation events
- **Liquidation.Report** (RapidAPI) - Counter-trading data
- **Tardis.dev** - Granular historical data

## 📊 Early Warning Indicators
1. **Funding Rate** >0.12% = overheated longs (bearish)
2. **Open Interest Spike** without volume = leverage buildup
3. **CVD Shifts** with minimal price change = bid hitting
4. **Dense Heatmap Clusters** = high probability zones

## ⚡ Positioning Strategies

### BEFORE Cascade
- **Monitor**: Funding rates + OI + heatmap clusters
- **Hedge**: Options (puts), inverse ETFs (REKT/BITI), cross-hedging
- **Avoid**: High leverage (>10x) in obvious zones

### DURING Cascade
- **Don't fight** the move
- **Wait for exhaustion** (volume spike then drop)
- **Watch spot/futures divergence** (artificial moves roll back)

### AFTER Cascade
- **V-shaped rebounds** common
- **Second wave entries** safer
- **Mean reversion** opportunities
- **Discounted liquidity** purchases

## 🛡️ Risk Management
### Critical Rules
1. **Never** >10x leverage on BTC/ETH
2. **Avoid** publicly known liquidation zones
3. **Work** on second wave, not first
4. **Monitor** spot/futures synchronization

### Hedging Tools
- **Options**: Puts, iron condors, straddles
- **Inverse ETFs**: REKT, BITI during downturns
- **Cross-Hedging**: Short correlated assets
- **Portfolio**: Multiple asset collateral

## 💡 Pro Tips
1. **Exchange Differences**:
   - Binance: Partial liquidations (stretched cascade)
   - Bybit: Full liquidations (explosive cascade)
   - OKX: Hybrid model

2. **Pattern Recognition**:
   - Clusters recur at same price levels
   - Weekend/off-peak vulnerability
   - Altcoin triggers affect BTC via correlation

3. **Tactical Techniques**:
   - Liquidity spoofing (fake orders)
   - Liquidity layering (multiple levels)
   - Options pressure (complex hedges)

## 🚨 Red Flags
- Funding rate extremes (±0.12%+)
- OI spikes without volume
- Price moving against fundamentals
- Spot sluggish while futures volatile

## 📈 Profit Opportunities
1. **Direct Hunting**: Trigger and profit from cascade
2. **Counter-Trading**: Fade exhausted moves
3. **Liquidity Provision**: Absorb forced orders
4. **Hedging**: Protect against systemic risk

## 🔗 Essential Resources
- **CoinGlass**: www.coinglass.com/liquidations
- **GitHub Tools**: `hgnx/binance-liquidation-tracker`, `aoki-h-jp/py-liquidation-map`
- **APIs**: docs.coinglass.com, rapidapi.com/AtsutaneDotNet/api/liquidation-report
- **Research**: academy.exmon.pro (anatomy of liquidations)

---

*Remember: Crypto pricing = balance between voluntary trades and forced liquidations. Understand the mechanics to trade with hunters, not against them.*