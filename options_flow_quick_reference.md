# Options Flow Data Sources: Quick Reference

## Top Picks by Category

### 🥇 Best Overall for Automated Scanner
**Interactive Brokers TWS API**
- Cost: Free with account + $4.50/month options data
- Real-time: Yes
- Pros: Integrated trading, professional data, real-time Greeks
- Cons: Complex API, steep learning curve

### 💰 Best Value for Money
**Unusual Whales API**
- Cost: $35-50/month + API fees
- Real-time: Yes (2-3 sec delay)
- Pros: Comprehensive flow data, dark pool tracking, good API
- Cons: Not as fast as premium options

### ⚡ Fastest Flow Data
**FlowAlgo**
- Cost: $149/month
- Real-time: Yes (fastest available)
- Pros: 2-3 seconds faster than competitors, premium features
- Cons: Expensive

### 🚀 Best for Developers
**Polygon.io (Massive)**
- Cost: $99-299/month
- Real-time: Yes (paid)
- Pros: Excellent documentation, good pricing, reliable
- Cons: No built-in flow detection

### 🆓 Best Free Option
**Alpha Vantage**
- Cost: Free (5 calls/min)
- Real-time: Delayed
- Pros: Free options data, good for learning
- Cons: Rate limited, delayed data

### 🎯 Best for Quantitative Analysis
**Market Chameleon**
- Cost: $99/month
- Real-time: Yes
- Pros: 18+ years historical data, excellent Greeks/IV analytics
- Cons: Less focus on real-time flow

## Cost Comparison Matrix

| Provider | Free Tier | Entry Paid | Real-time | Flow Detection |
|----------|-----------|------------|-----------|----------------|
| **Alpha Vantage** | ✓ (limited) | $29.99/mo | ✗ | ✗ |
| **Polygon.io** | ✓ (15-min delay) | $99/mo | ✓ | ✗ |
| **Unusual Whales** | Limited web | $35-50/mo | ✓ | ✓✓✓ |
| **FlowAlgo** | Trial | $149/mo | ✓ | ✓✓✓ |
| **Market Chameleon** | Starter free | $99/mo | ✓ | ✓ |
| **IBKR** | With account | +$4.50/mo | ✓ | ✗ |
| **CBOE** | Delayed web | $1,000+/mo | ✓ | ✗ |

## Data Quality Comparison

### Essential Features for Flow Scanning:
1. **Real-time trade data** - Minimum requirement
2. **Bid/ask spreads** - For price context
3. **Volume/open interest** - For significance filtering
4. **Greeks data** - For strategy analysis
5. **Flow detection** - Built-in or need to build

### Provider Capabilities:

**✅ Excellent:**
- Interactive Brokers (all except flow detection)
- CBOE (raw data, need custom detection)
- Polygon.io (raw data, need custom detection)

**✅ Good:**
- Unusual Whales (flow detection included)
- FlowAlgo (flow detection included)
- Market Chameleon (analytics focus)

**⚠️ Limited:**
- Alpha Vantage (delayed, basic data)
- Barchart (web focus, limited API)
- Yahoo Finance (unofficial, unreliable)

## Implementation Recommendations

### Phase 1: Prototyping (0-3 months)
- Use **Alpha Vantage** (free) for data
- Build basic detection algorithms
- Test with paper trading

### Phase 2: Development (3-6 months)
- Upgrade to **Polygon.io** ($99/month)
- Implement real-time data pipeline
- Add custom flow detection logic

### Phase 3: Production (6+ months)
- **Option A**: Interactive Brokers + Unusual Whales API
- **Option B**: CBOE Data + custom infrastructure (enterprise)
- **Option C**: FlowAlgo API (premium solution)

## Critical Success Factors

1. **Latency**: <5 seconds for effective flow trading
2. **Reliability**: 99.9%+ uptime required
3. **Scalability**: Handle market open spikes
4. **Cost Control**: Predictable monthly expenses
5. **Maintenance**: API changes, data format updates

## Common Pitfalls to Avoid

1. ❌ Using free APIs for production trading
2. ❌ Underestimating data licensing costs
3. ❌ Ignoring rate limits and throttling
4. ❌ Not planning for API deprecation
5. ❌ Overlooking total cost of ownership

## Quick Start Checklist

- [ ] Define budget ($50-500/month typical)
- [ ] Determine required data latency
- [ ] Evaluate technical expertise needed
- [ ] Test free tiers first
- [ ] Plan scalability from day 1
- [ ] Consider backup data sources
- [ ] Review legal/data licensing terms

## Final Recommendation

For most automated flow scanner projects:

**Start with:** Unusual Whales API ($35-50/month)
- Good balance of features and cost
- Includes flow detection
- Reasonable API access

**Scale to:** Interactive Brokers + supplemental data
- Professional trading integration
- Add custom analytics as needed
- Most flexible long-term solution

**Avoid:** Building everything from raw CBOE data
- Unless you have enterprise budget ($2,500+/month)
- And significant development resources
- And need absolute lowest latency