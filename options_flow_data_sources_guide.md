# Comprehensive Guide: Options Flow Data Sources & APIs for Automated Scanners

## Executive Summary

This guide provides a comprehensive analysis of options flow data sources and APIs for building automated flow scanners. We evaluate each source based on data quality, cost, real-time availability, API documentation, and practical usefulness for serious traders.

## Ranking by Usefulness for Automated Flow Scanners

### Tier 1: Professional-Grade (Best for Serious Automated Trading)
1. **Interactive Brokers TWS API** - Best overall for integrated trading + data
2. **CBOE LiveVol Data Shop** - Most comprehensive raw options data
3. **Unusual Whales API** - Best balance of quality, features, and price

### Tier 2: High-Quality Commercial APIs
4. **Polygon.io/Massive** - Excellent developer experience, good pricing
5. **FlowAlgo** - Fastest flow data, premium features
6. **Market Chameleon** - Deep historical data and analytics

### Tier 3: Budget-Friendly Options
7. **Alpaca Markets** - Good for beginners, integrated trading
8. **Cheddar Flow** - Solid mid-tier option
9. **TD Ameritrade/Schwab API** - Legacy but functional

### Tier 4: Free/Limited Options
10. **Alpha Vantage** - Best free tier with options data
11. **Barchart** - Free web access, limited API
12. **Yahoo Finance (unofficial)** - Free but unreliable

---

## Detailed Analysis by Category

### 1. Free Data Sources

#### CBOE (Chicago Board Options Exchange)
- **Data Availability**: Real-time available for purchase, delayed (15-min) free through some platforms
- **Data Quality**: Exchange-direct data, highest quality raw feeds
- **Cost**: Free delayed data via TradingView/CBOE One, real-time requires exchange fees ($1,000+/month)
- **API Access**: CBOE All Access API (paid), LiveVol Data Shop API
- **Rate Limits**: Commercial tier-based
- **Best For**: Institutional users who need raw exchange data

#### Barchart
- **Data Availability**: Web-based free access, API requires subscription
- **Data Quality**: Good for retail, shows large option trades
- **Cost**: Free web access, API starts at $150+/month
- **API Documentation**: Good
- **Best For**: Casual research, not ideal for automated scanning

#### TradingView
- **Data Availability**: CBOE One data free (delayed), real-time requires subscription
- **Data Quality**: Good for visualization, limited for programmatic access
- **Cost**: Free tier available, Pro+ $14.95/month for more data
- **API Limitations**: Primarily charting/visualization API, not ideal for raw data
- **Best For**: Visualization, not automated scanning

#### Public Feeds (Yahoo Finance, Alpha Vantage, IEX Cloud)
- **Alpha Vantage**: Free tier with options data, 5 calls/minute, good for prototypes
- **Yahoo Finance**: Unofficial APIs (yfinance), frequently breaks, terms violation risk
- **IEX Cloud**: Free tier limited, $9/month basic plan
- **Data Quality**: Delayed, inconsistent, not suitable for real-time trading
- **Best For**: Learning, prototypes, non-critical applications

### 2. Paid Options Flow APIs

#### Unusual Whales
- **Pricing**: $35-50/month, API access additional
- **Data Quality**: Real-time options flow, dark pool data, institutional tracking
- **Features**: Flow filtering, alerts, Discord bot, congressional trading data
- **API Documentation**: Good (api.unusualwhales.com/docs)
- **Rate Limits**: Tier-based, reasonable for retail
- **Real-time**: Yes, with 2-3 second delay
- **Best For**: Retail traders, good value for money

#### FlowAlgo
- **Pricing**: $149/month
- **Data Quality**: Premium flow data, fastest alerts (2-3 seconds faster than competitors)
- **Features**: Sweeps detection, block trades, dark pool tracking
- **API Access**: Available for enterprise
- **Real-time**: Yes, near-instant
- **Best For**: Serious traders needing fastest flow data

#### Benzinga
- **Pricing**: $177/month (Pro), API additional
- **Data Quality**: News + options flow, good for event-driven strategies
- **Features**: Options flow scanner, news alerts, earnings data
- **API**: REST API available
- **Best For**: News-based trading strategies

#### Market Chameleon
- **Pricing**: $99/month (Total Access)
- **Data Quality**: Excellent historical data (18+ years), Greeks, IV analytics
- **Features**: Backtesting, earnings tools, volatility analysis
- **API**: Data feeds available
- **Best For**: Quantitative analysis, backtesting, volatility trading

#### SpotGamma
- **Pricing**: $299/month ($224 annual)
- **Data Quality**: Gamma exposure data, dealer positioning, Greeks analysis
- **Features**: TRACE model, gamma levels, dealer hedging impact
- **Specialization**: SPX/SPY gamma analysis
- **Best For**: Gamma-focused strategies, market maker positioning analysis

### 3. Broker APIs with Options Data

#### TD Ameritrade (Now Charles Schwab)
- **Status**: API registration disabled, migrating to Schwab Trader API
- **Data Quality**: Good for retail, real-time with funded account
- **Features**: Options chains, streaming data, historical data
- **API Documentation**: Good (developer.tdameritrade.com)
- **Rate Limits**: 120 calls/minute (free), higher with funded account
- **Real-time**: Yes with funded account ($25k+), otherwise delayed
- **Best For**: Existing TDA users, legacy integration

#### Interactive Brokers TWS API
- **Pricing**: Free with account, data fees apply (~$4.50/month for options data)
- **Data Quality**: Professional-grade, real-time Greeks, comprehensive
- **Features**: Real-time options computations, streaming data, trading integration
- **API Documentation**: Extensive but complex
- **Languages**: Python, Java, C++, C#, VB
- **Real-time**: Yes, with proper data subscriptions
- **Best For**: Serious algorithmic traders, integrated trading systems

#### Alpaca Markets
- **Pricing**: Free paper trading, $100/month for real-time data + trading
- **Data Quality**: Good for equities, options API in development
- **Features**: Zero commissions, easy API, paper trading
- **API Documentation**: Excellent, developer-friendly
- **Rate Limits**: Generous
- **Current Status**: Options API announced but not fully launched
- **Best For**: Beginners, algo trading prototypes

### 4. Data Quality Comparison

| Source | Strikes | Volume | Bid/Ask | Greeks | IV | Flow Detection | Dark Pool |
|--------|---------|---------|---------|---------|-----|----------------|-----------|
| **CBOE** | ✓✓✓ | ✓✓✓ | ✓✓✓ | ✓✓ | ✓✓ | ✓ | ✗ |
| **IBKR** | ✓✓✓ | ✓✓✓ | ✓✓✓ | ✓✓✓ | ✓✓✓ | ✗ | ✗ |
| **Unusual Whales** | ✓✓ | ✓✓✓ | ✓✓ | ✓ | ✓ | ✓✓✓ | ✓✓ |
| **FlowAlgo** | ✓✓ | ✓✓✓ | ✓✓ | ✓ | ✓ | ✓✓✓ | ✓✓ |
| **Polygon** | ✓✓✓ | ✓✓✓ | ✓✓✓ | ✓✓ | ✓✓ | ✗ | ✗ |
| **Market Chameleon** | ✓✓✓ | ✓✓✓ | ✓✓ | ✓✓✓ | ✓✓✓ | ✓ | ✗ |
| **Alpha Vantage** | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |

### 5. Cost Comparison

| Source | Free Tier | Entry Paid | Professional | Enterprise |
|--------|-----------|------------|--------------|------------|
| **CBOE** | Delayed web | $1,000+/mo | $2,500+/mo | Custom |
| **IBKR** | With account | $4.50/mo data | Included | Included |
| **Unusual Whales** | Limited web | $35-50/mo | $100+/mo | Custom |
| **FlowAlgo** | Trial | $149/mo | $299/mo | Custom |
| **Polygon** | 15-min delayed | $99/mo | $299/mo | Custom |
| **Market Chameleon** | Starter free | $99/mo | $199/mo | Custom |
| **Alpha Vantage** | Free API | $29.99/mo | $99.99/mo | Custom |
| **Alpaca** | Paper trading | $100/mo | Included | Custom |

### 6. API Documentation & Ease of Integration

**Excellent Documentation:**
- Alpaca Markets (clear, examples, SDKs)
- Polygon.io (good docs, community support)
- Alpha Vantage (simple, straightforward)

**Good Documentation:**
- Unusual Whales (API docs available)
- TD Ameritrade (comprehensive but legacy)
- Market Chameleon (data feed documentation)

**Complex but Powerful:**
- Interactive Brokers (steep learning curve)
- CBOE (enterprise-focused)

**Poor/No Official API:**
- Barchart (limited API access)
- TradingView (visualization focus)
- Yahoo Finance (unofficial only)

### 7. Rate Limits & Restrictions

| Source | Free Tier Limits | Paid Tier Limits | Real-time Access |
|--------|------------------|------------------|------------------|
| **Alpha Vantage** | 5 calls/min, 500/day | Higher limits | Delayed |
| **Polygon** | 5 calls/min, delayed | Unlimited, real-time | ✓ (paid) |
| **IBKR** | Based on data subs | Based on data subs | ✓ (with subs) |
| **Unusual Whales** | N/A | Tier-based | ✓ |
| **TD Ameritrade** | 120 calls/min | 180 calls/min | ✓ (funded) |
| **Alpaca** | Paper: generous | Real: generous | ✓ (paid) |

### 8. What Serious Traders Actually Use

Based on community research (r/algotrading, r/options, professional forums):

**For Algorithmic Trading:**
1. **Interactive Brokers TWS API** - Most common among serious algo traders
2. **Polygon.io** - Popular for data + reasonable pricing
3. **CBOE Data Shop** - For institutions needing raw data

**For Options Flow Scanning:**
1. **Unusual Whales** - Most popular among retail for value
2. **FlowAlgo** - Preferred by those needing fastest data
3. **Market Chameleon** - For quantitative analysis

**For Beginners/Prototyping:**
1. **Alpaca** - Easy API, paper trading
2. **Alpha Vantage** - Free tier for learning
3. **TD Ameritrade** - Legacy but functional

## Recommendations by Use Case

### Building a Production Automated Flow Scanner

**Best Overall: Interactive Brokers + Unusual Whales API**
- Use IBKR for trading execution and basic data
- Supplement with Unusual Whales for flow detection
- Cost: ~$40-50/month + IBKR data fees

**Budget Option: Polygon.io + Custom Flow Detection**
- Use Polygon for real-time options data
- Build custom flow detection logic
- Cost: ~$99-299/month

**Enterprise Solution: CBOE Data + Custom Infrastructure**
- Raw CBOE data feeds
- Build complete pipeline in-house
- Cost: $2,500+/month + development

### For Learning/Prototyping

**Free Path: Alpha Vantage + Paper Trading**
- Free options data for learning
- Build detection algorithms
- Upgrade when ready for real trading

**Beginner Friendly: Alpaca Paper Trading**
- Excellent API documentation
- Free paper trading environment
- Real-time data with paid plan

## Critical Considerations

1. **Data Latency Matters**: For flow scanning, 2-3 seconds can be significant
2. **Total Cost of Ownership**: Include development time, infrastructure, maintenance
3. **Reliability**: Free APIs break frequently, paid services more stable
4. **Scalability**: Consider rate limits and concurrent connection limits
5. **Legal/Compliance**: Ensure proper data licensing for redistribution

## Future Trends

1. **Consolidation**: Broker APIs merging (TD Ameritrade → Schwab)
2. **AI Integration**: More providers adding AI/ML features
3. **Lower Costs**: Competition driving down API prices
4. **Real-time for All**: Decreasing latency across providers

## Conclusion

For building an automated options flow scanner, the optimal choice depends on your budget, technical expertise, and trading scale:

- **Retail Traders**: Start with Unusual Whales API ($35-50/month)
- **Serious Algo Traders**: Interactive Brokers TWS API + data subscriptions
- **Institutions**: CBOE Data Shop with custom infrastructure
- **Beginners**: Alpha Vantage (free) or Alpaca paper trading

The market continues to evolve with better APIs and lower costs, making sophisticated flow scanning accessible to more traders than ever before.