# Quick Scalp Exit Rules for Stocks/Options: Research Summary

## Executive Summary
Based on comprehensive research, here are conservative default exit rules for scalp trading across three main categories: ATR-based, percent-based, and time-based approaches.

## 1. ATR-Based Exit Rules (Most Adaptive)

### Conservative Defaults:
- **ATR Period**: 14-day (balanced view of volatility)
- **Multiplier**: 1.5x to 2x ATR for conservative scalping
- **Initial Stop Loss**: Entry price ± (ATR × 1.5-2.0)
- **Trailing Stop**: Adjusts dynamically as price moves in your favor

### ATR Strategy Variations:
1. **Basic ATR Stop-Loss**: Static stop at entry ± (ATR × multiplier)
2. **ATR Trailing Stop**: Dynamic adjustment based on highest/lowest price since entry
3. **ATR Chandelier Exit**: Uses price extremes (highest high/lowest low) ± (ATR × multiplier)
4. **ATR Percentage Stop**: ATR × percentage multiplier (20-30% of ATR)
5. **Market Volatility ATR Stop**: Adjusts multiplier based on market conditions (1.5-2x for quiet markets, 2.5-3x for volatile markets)

### Conservative Implementation:
- Use 1.5x multiplier for tighter risk control
- For day trading/scalping: 1.5x-2x ATR multipliers
- Adjust based on asset volatility (lower for stable stocks, higher for volatile options)

## 2. Percent-Based Exit Rules (Simplest)

### Conservative Defaults:
- **Stop Loss**: 1-2% from entry price for stocks
- **Profit Target**: 2-4% (2:1 risk-reward ratio)
- **Maximum Risk Per Trade**: 1-2% of total account value

### Asset-Specific Percentages:
- **Stocks**: 2-3% stop loss (conservative for stable stocks like Johnson & Johnson)
- **Options**: 5-10% stop loss (due to higher volatility)
- **Forex**: 15-30 pips (equivalent to ~0.15-0.30%)
- **Cryptocurrencies**: 5-10% stop loss

### Risk Management Principles:
- Never risk more than 2% of account per trade
- Calculate position size based on stop loss distance
- Maintain consistent risk percentages across all trades

## 3. Time-Based Exit Rules (Discipline Enforcement)

### Conservative Defaults:
- **Maximum Time in Trade**: 15-30 minutes for scalp trades
- **Exit if No Movement**: Consider exit if price doesn't move in your direction within 5-10 minutes
- **End-of-Day Exit**: Always exit all scalp positions before market close

### Time-Based Strategies:
1. **Fixed Time Exit**: Exit after predetermined time (e.g., 15 minutes) regardless of P&L
2. **No-Progress Exit**: Exit if trade doesn't show profit within first 5-10 minutes
3. **Session-Based Exit**: Exit all positions 30 minutes before market close

### Rationale:
- Scalp trades should work quickly or not at all
- Prevents "hope trading" and emotional attachment
- Reduces exposure to overnight/weekend risk

## Combined Conservative Approach

### Recommended Conservative Defaults:
1. **Primary Exit**: ATR-based stop (1.5x ATR)
2. **Secondary Exit**: 2% fixed stop loss (whichever is tighter)
3. **Time Limit**: 20-minute maximum hold time
4. **Profit Target**: 3% or 2x ATR (whichever is reached first)

### Example Setup:
- Stock price: $100
- 14-day ATR: $2.00
- ATR stop: $100 ± (2.00 × 1.5) = $97.00 (long) or $103.00 (short)
- Percent stop: $98.00 (2% stop loss)
- **Actual stop**: $98.00 (tighter of the two)
- Time limit: 20 minutes
- Profit target: $106.00 (3% or 2x ATR = $104.00)

## Special Considerations for Options

### Volatility Adjustments:
- Use higher ATR multipliers (2-2.5x) for options
- Consider implied volatility (IV) when setting stops
- Wider stops needed due to gamma risk near expiration

### Conservative Option Defaults:
- Stop loss: 10-15% of option premium
- Profit target: 20-30% (2:1 risk-reward)
- Time limit: Shorter than stocks (10-15 minutes maximum)
- Exit all positions at least 1 hour before expiration on trade day

## Risk Management Framework

### Daily Limits:
- Maximum daily loss: 5% of account
- Maximum number of trades: 10-15 per day
- Stop trading after 3 consecutive losses

### Position Sizing Formula:
```
Position Size = (Account Risk %) × Account Balance ÷ Stop Loss Distance
```
Example: $10,000 account, 1% risk, $2.00 stop loss:
Position size = (0.01 × $10,000) ÷ $2.00 = 50 shares

## Implementation Checklist

### Before Entering Trade:
- [ ] Calculate ATR value (14-period)
- [ ] Determine stop loss (ATR × 1.5 AND 2% rule)
- [ ] Set profit target (2x risk or 3%)
- [ ] Set time limit (20 minutes)
- [ ] Calculate position size based on risk

### During Trade:
- [ ] Monitor time elapsed
- [ ] Adjust trailing stop if using ATR trailing
- [ ] Exit at first target reached (time, price, or stop)

### After Trade:
- [ ] Record entry/exit reasons
- [ ] Review if stops were appropriate
- [ ] Adjust future stops based on volatility changes

## Key Takeaways

1. **ATR-based stops** adapt best to changing volatility
2. **Percent-based stops** provide simplicity and consistency
3. **Time-based exits** enforce discipline and prevent hope trading
4. **Conservative defaults** prioritize capital preservation over maximum gains
5. **Combination approach** (using multiple exit criteria) provides robust risk management

## Sources & References
1. LuxAlgo - "5 ATR Stop-Loss Strategies for Risk Control"
2. Investopedia - "Scalping Strategies: Mastering Quick Profits"
3. PocketOption - "Day Trading Stop Loss: Effective Risk Management"
4. Various trading forums and expert recommendations
5. Professional trader consensus on conservative risk management

*Note: These are conservative defaults suitable for beginning scalp traders. Experienced traders may adjust based on market conditions, asset volatility, and personal risk tolerance.*