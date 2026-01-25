# Crypto Scalping Frameworks - Quick Reference

## Framework Comparison Summary

| Aspect | Freqtrade | Jesse | Passivbot | CCXT (Custom) |
|--------|-----------|-------|-----------|---------------|
| **Best For** | General scalping (1m-15m) | Algorithmic research | Market-making scalping | Custom HFT |
| **Setup Speed** | Medium (2-4 hours) | Fast (1-2 hours) | Medium (2-3 hours) | Slow (days-weeks) |
| **Scalping Suitability** | Good | Good | Excellent | Excellent |
| **Perpetuals Support** | Good | Good | Excellent | Excellent |
| **Latency** | Moderate | Moderate | Good | Best |
| **Learning Curve** | Medium | Easy-Medium | Medium | Hard |
| **Community** | Large | Medium | Medium | Large |
| **Cost** | Free | Free | Free | Free (dev time) |

## Quick Setup Recommendations

### 1. For Beginners Wanting to Start Quickly
**Choose: Jesse**
- Simple Python strategies
- Good tutorials and examples
- Built-in AI assistant (JesseGPT)
- Faster to productive trading

### 2. For Perpetual Futures Market Making
**Choose: Passivbot**
- Specifically built for perpetuals
- Grid trading optimized
- Minimal ongoing management
- Good for capturing small spreads

### 3. For Versatile Scalping Strategies
**Choose: Freqtrade**
- Most strategy flexibility
- Largest community support
- Good documentation
- Suitable for various timeframes

### 4. For Professional/Advanced Scalping
**Choose: CCXT Custom Build**
- Maximum control
- Lowest possible latency
- Custom risk management
- Professional-grade systems

## Minimum Requirements for Scalping

### Hardware/Infrastructure
- **VPS/Cloud Server:** $10-50/month (close to exchange)
- **Memory:** 4GB+ RAM
- **Storage:** 20GB+ SSD
- **Connection:** Low-latency, stable internet

### Technical Skills Required
- **Freqtrade:** Intermediate Python, basic Linux
- **Jesse:** Basic Python, basic Linux
- **Passivbot:** Intermediate Python, basic Rust, Linux
- **CCXT:** Advanced programming, system architecture

### Risk Management Essentials
1. **Position Sizing:** 1-5% per trade maximum
2. **Stop-losses:** Always use, test thoroughly
3. **Leverage:** Start low (2-5x), increase gradually
4. **Monitoring:** Real-time alerts (Telegram/Discord)
5. **Backtesting:** Minimum 3 months data, multiple market conditions

## Exchange Recommendations for Scalping

### Best for Low Fees & Liquidity
1. **Binance Futures** (USDT-M)
2. **Bybit** (Perpetuals)
3. **OKX** (Perpetuals)
4. **Bitget** (Perpetuals)

### Considerations
- **Fee Structure:** Maker/taker fees, rebates
- **API Limits:** Rate limits for high frequency
- **Liquidity:** Depth for minimal slippage
- **Reliability:** Uptime and stability

## Getting Started Checklist

### Phase 1: Preparation
- [ ] Choose framework based on needs
- [ ] Set up VPS/cloud server
- [ ] Install required dependencies
- [ ] Get exchange API keys (read-only first)

### Phase 2: Testing
- [ ] Run in dry-run/paper trading mode
- [ ] Test basic strategies
- [ ] Verify order execution
- [ ] Monitor for 1-2 weeks

### Phase 3: Live Trading
- [ ] Start with small capital
- [ ] Use low leverage initially
- [ ] Implement strict risk management
- [ ] Monitor closely, adjust as needed

## Common Pitfalls to Avoid

1. **Over-leveraging:** Start with 2-3x, not 20x
2. **Insufficient testing:** Paper trade for weeks, not days
3. **Ignoring fees:** Account for trading and funding fees
4. **No stop-losses:** Always have risk management
5. **Chasing losses:** Stick to strategy, don't revenge trade
6. **Poor infrastructure:** Don't run on home computer

## Performance Expectations

### Realistic Scalping Returns
- **Conservative:** 1-5% monthly (compounded)
- **Moderate:** 5-15% monthly (with good strategy)
- **Aggressive:** 15-30% monthly (higher risk)
- **Note:** Past performance ≠ future results

### Key Metrics to Track
- **Win Rate:** 40-60% typical for scalping
- **Profit Factor:** >1.5 target
- **Max Drawdown:** Keep under 20%
- **Sharpe Ratio:** >1.0 target
- **Average Trade Duration:** Seconds to minutes

## Final Recommendation

For most traders starting with crypto scalping on perpetual futures:

**Start with Freqtrade** if you want versatility and community support.

**Choose Passivbot** if you specifically want market-making grid strategies.

**Build with CCXT** only if you have advanced programming skills and need maximum control.

Remember: Scalping with leverage is high-risk. Never trade with money you can't afford to lose, and always test thoroughly before going live.