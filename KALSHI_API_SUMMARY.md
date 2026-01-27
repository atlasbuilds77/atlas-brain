# Kalshi API Research Summary

## What I Accomplished

I conducted comprehensive research on the Kalshi API for scalping and automated trading, covering all requested topics:

## Key Findings

### 1. API Basics & Authentication
- **Authentication**: RSA signature-based with three headers (API key, signature, timestamp)
- **Endpoints**: REST API with `/markets`, `/events`, `/orders`, `/portfolio` endpoints
- **Environments**: Demo (`demo-api.kalshi.co`) and Production (`trading-api.kalshi.com`)
- **Python Support**: Official starter code and community libraries available

### 2. Order Management
- **Place Orders**: `POST /portfolio/orders` with client_order_id for deduplication
- **Cancel Orders**: `DELETE /portfolio/orders/{order_id}`
- **Batch Operations**: Available for creating/cancelling multiple orders
- **Order Types**: Limit and market orders for YES/NO contracts

### 3. Market Data
- **Orderbook**: `GET /markets/{ticker}/orderbook` with depth parameter
- **Market Lists**: Filterable by status, event, etc.
- **Real-time Options**: WebSocket connections recommended for scalping

### 4. Scalping Strategies
- **Spread Capture**: Buy at bid, sell at ask when spread sufficient
- **Momentum Trading**: Follow short-term price movements
- **News-Based**: React to breaking news and sentiment
- **Arbitrage**: Cross-venue (Kalshi-Polymarket) and intra-venue opportunities

### 5. Rate Limits
- **Tiers**: Basic (20/10), Advanced (30/30), Premier (100/100), Prime (400/400) per second
- **Write Transactions**: Each order/cancel = 1 transaction, batch cancels = 0.2 each
- **Best Practices**: Exponential backoff, request queuing, caching

### 6. Existing Bots & Tools
- **Open Source**: Multiple GitHub repos (OctagonAI, Kalshi-Quant-TeleBot, arbitrage bots)
- **Commercial**: Alphascope (signals), PredictionlyAI (arbitrage detection)
- **Architecture**: Market data → Strategy → Risk check → Execution loop

### 7. Legal Considerations
- **Regulation**: CFTC-regulated DCM with SIPC insurance
- **Compliance**: Must follow Member Agreement and Developer Agreement
- **Restrictions**: Not available in 50+ countries
- **Risk**: User assumes all liability for automated trading losses

## Practical Implementation

1. **Start with Demo**: Test strategies with fake money first
2. **Respect Rate Limits**: Implement proper throttling and backoff
3. **Risk Management**: Position sizing, stop losses, maximum drawdown limits
4. **Monitoring**: Log all trades, monitor performance metrics
5. **Compliance**: Document strategies, implement circuit breakers

## Resources Created
- **Full Guide**: `KALSHI_API_SCALPING_GUIDE.md` (13,615 bytes) with detailed examples
- **This Summary**: Concise overview of key findings

## Important Notes
- Kalshi is a regulated US exchange (unlike many prediction markets)
- Automated trading is permitted but must comply with terms
- Significant financial risk involved - only trade with risk capital
- Many successful bots exist but require careful development and testing

The research shows Kalshi has a mature API ecosystem suitable for algorithmic trading, but success requires sophisticated risk management and compliance awareness.