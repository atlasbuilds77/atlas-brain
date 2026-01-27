# Kalshi API Scalping Guide: Practical Guide for Prediction Market Trading

## 1. Kalshi API Basics

### Authentication
Kalshi uses RSA signature-based authentication with three headers:
- `KALSHI-ACCESS-KEY`: Your API key ID
- `KALSHI-ACCESS-SIGNATURE`: RSA-PSS signature of the request
- `KALSHI-ACCESS-TIMESTAMP`: Request timestamp in milliseconds

**Key Endpoints:**
- Base URL (Production): `https://trading-api.kalshi.com/trade-api/v2/`
- Base URL (Demo): `https://demo-api.kalshi.co/trade-api/v2/`

### Getting API Keys
1. Create a Kalshi account
2. Navigate to API settings to generate keys
3. Use demo environment for testing first (`KALSHI_USE_DEMO=true`)

### Python Authentication Example
```python
import requests
import uuid
import datetime
import hashlib
import hmac
import base64

def create_signature(private_key, timestamp, method, path):
    """Create RSA signature for Kalshi API"""
    message = f"{timestamp}{method}{path}"
    # Implementation depends on your RSA library
    # Use cryptography or similar for actual signing
    return signature

def post(private_key, api_key_id, path, data, base_url="https://demo-api.kalshi.co/trade-api/v2/"):
    timestamp = str(int(datetime.datetime.now().timestamp() * 1000))
    signature = create_signature(private_key, timestamp, "POST", path)
    
    headers = {
        'KALSHI-ACCESS-KEY': api_key_id,
        'KALSHI-ACCESS-SIGNATURE': signature,
        'KALSHI-ACCESS-TIMESTAMP': timestamp,
        'Content-Type': 'application/json'
    }
    
    return requests.post(base_url + path, headers=headers, json=data)
```

## 2. Order Placement and Cancellation

### Creating Orders
**Endpoint:** `POST /portfolio/orders`

**Order Parameters:**
```python
order_data = {
    "ticker": "MARKET-TICKER",  # e.g., "FEDRATE-25DEC15-T50"
    "action": "buy",  # or "sell"
    "side": "yes",  # or "no"
    "count": 1,  # number of contracts
    "type": "limit",  # or "market"
    "yes_price": 50,  # price in cents (1-99)
    "client_order_id": str(uuid.uuid4())  # Unique ID for deduplication
}
```

**Example Order Placement:**
```python
# Find an open market first
response = requests.get('https://demo-api.kalshi.co/trade-api/v2/markets?limit=1&status=open')
market = response.json()['markets'][0]

# Place order
order_response = post(private_key, API_KEY_ID, '/trade-api/v2/portfolio/orders', order_data)

if order_response.status_code == 201:
    order = order_response.json()['order']
    print(f"Order ID: {order['order_id']}")
    print(f"Status: {order['status']}")
```

### Cancelling Orders
**Endpoint:** `DELETE /portfolio/orders/{order_id}`

**Batch Operations:**
- `POST /portfolio/batch-create-orders`: Create multiple orders
- `POST /portfolio/batch-cancel-orders`: Cancel multiple orders
- Each cancel in batch counts as 0.2 transactions for rate limits

### Order Management Endpoints
- `GET /portfolio/orders`: List all orders
- `GET /portfolio/orders/{order_id}`: Get specific order
- `PUT /portfolio/orders/{order_id}`: Amend order price/quantity
- `DELETE /portfolio/orders/{order_id}`: Cancel order

## 3. Market Data Access

### Orderbook Data
**Endpoint:** `GET /markets/{ticker}/orderbook`

**Parameters:**
- `ticker`: Market identifier
- `depth`: Depth to retrieve (0 for all levels, 1-100 for specific depth)

**Example:**
```python
def get_orderbook(ticker, depth=0):
    response = requests.get(
        f"https://demo-api.kalshi.co/trade-api/v2/markets/{ticker}/orderbook?depth={depth}"
    )
    return response.json()
```

### Market Information
**Endpoints:**
- `GET /markets`: List all markets with filters (status, limit, etc.)
- `GET /markets/{ticker}`: Get specific market details
- `GET /events`: List events
- `GET /events/{event_ticker}/markets`: Get markets for specific event

**Market Data Fields:**
- Current bid/ask prices
- Volume and open interest
- Market status (open, closed, settled)
- Resolution criteria and deadlines

### Real-time Data Considerations
For scalping, consider:
1. **WebSocket connections** for real-time updates
2. **Polling orderbook** at appropriate intervals (respect rate limits)
3. **Caching** frequently accessed data to reduce API calls

## 4. Scalping Strategies for Prediction Markets

### Core Scalping Concepts
1. **Buy Low, Sell Before Resolution**: Purchase contracts when probability is undervalued, sell when market corrects
2. **Market Making**: Place both buy and sell orders to capture spreads
3. **Momentum Trading**: Follow short-term price movements
4. **Arbitrage**: Exploit price differences between related markets

### Strategy Implementation

**1. Spread Capture Strategy:**
```python
def spread_capture_strategy(ticker, min_spread=2):
    """Buy at bid, sell at ask when spread is sufficient"""
    orderbook = get_orderbook(ticker)
    
    best_bid = orderbook['yes']['bids'][0]['price']  # Highest buy price
    best_ask = orderbook['yes']['asks'][0]['price']  # Lowest sell price
    
    spread = best_ask - best_bid
    
    if spread >= min_spread:
        # Place buy order at best_bid + 1 (to get priority)
        # Place sell order at best_ask - 1
        return True
    return False
```

**2. Momentum Scalping:**
```python
class MomentumScalper:
    def __init__(self, lookback_period=5):
        self.price_history = []
        self.lookback = lookback_period
    
    def analyze_trend(self, current_price):
        self.price_history.append(current_price)
        if len(self.price_history) > self.lookback:
            self.price_history.pop(0)
        
        if len(self.price_history) == self.lookback:
            # Simple moving average crossover
            sma = sum(self.price_history) / self.lookback
            if current_price > sma * 1.01:  # 1% above SMA
                return "BUY"
            elif current_price < sma * 0.99:  # 1% below SMA
                return "SELL"
        return "HOLD"
```

**3. News-Based Scalping:**
- Monitor news sources for event updates
- React quickly to breaking news
- Use sentiment analysis to predict market movements

### Risk Management for Scalping
1. **Position Sizing**: Limit exposure per trade (e.g., 1-5% of capital)
2. **Stop Losses**: Automatic exit at predetermined loss levels
3. **Take Profits**: Lock in gains at target levels
4. **Maximum Drawdown Limits**: Stop trading if losses exceed threshold

## 5. Rate Limits and Restrictions

### API Tiers and Limits
| Tier | Read Limit | Write Limit | Qualification |
|------|------------|-------------|---------------|
| Basic | 20/sec | 10/sec | Account signup |
| Advanced | 30/sec | 30/sec | Application |
| Premier | 100/sec | 100/sec | 3.75% exchange volume |
| Prime | 400/sec | 400/sec | 7.5% exchange volume |

### Write API Transactions Count
- `CreateOrder`: 1 transaction
- `CancelOrder`: 1 transaction  
- `BatchCancelOrders`: Each cancel = 0.2 transactions
- `BatchCreateOrders`: Each order = 1 transaction

### Best Practices for Rate Limits
1. **Implement Exponential Backoff**: When hitting 429 errors
2. **Queue Requests**: Spread operations over time
3. **Cache Responses**: Store market data locally
4. **Monitor Usage**: Track API calls to stay within limits
5. **Use Client Order IDs**: Prevent duplicate orders on retries

### Technical Requirements for Higher Tiers
- Knowledge of API security practices
- Real-time monitoring capabilities
- Self-limiting mechanisms
- Legal/compliance awareness

## 6. Existing Bots and Tools

### Open Source Trading Bots

**1. Kalshi Deep Trading Bot (OctagonAI)**
- Uses AI for market analysis
- Integrates with Octagon Deep Research
- Supports demo and live trading
- Features: hedging, risk management

**2. Kalshi-Quant-TeleBot**
- Enterprise-grade automated trading
- Telegram interface for monitoring
- Real-time market analysis
- Professional risk management

**3. Polymarket-Kalshi Arbitrage Bot**
- Cross-venue arbitrage between Kalshi and Polymarket
- Identifies price discrepancies
- Automated execution

**4. kalshi-market-making**
- Market making strategies
- Order book analysis
- Position management

### Commercial Tools
- **Alphascope**: News-based signal generation
- **PredictionlyAI**: Real-time arbitrage detection
- **FinFeedAPI**: Unified prediction market data API

### Building Your Own Bot
**Recommended Architecture:**
```python
class ScalpingBot:
    def __init__(self, config):
        self.api_client = KalshiClient(config)
        self.strategy = MomentumStrategy()
        self.risk_manager = RiskManager()
        self.order_manager = OrderManager()
    
    def run(self):
        while True:
            # 1. Fetch market data
            markets = self.api_client.get_open_markets()
            
            # 2. Analyze opportunities
            for market in markets:
                signal = self.strategy.analyze(market)
                
                # 3. Risk check
                if self.risk_manager.approve_trade(signal):
                    # 4. Execute trade
                    self.order_manager.execute(signal)
            
            # 5. Manage existing positions
            self.order_manager.manage_positions()
            
            # 6. Sleep to respect rate limits
            time.sleep(1)
```

## 7. Legal Considerations

### Regulatory Compliance
1. **CFTC Regulation**: Kalshi is a registered Designated Contract Market (DCM)
2. **Member Agreement**: Must comply with Kalshi's terms
3. **Developer Agreement**: Specific terms for API usage
4. **Geographic Restrictions**: Not available in 50+ countries

### Automated Trading Rules
1. **Terms of Service Compliance**: Automated trading must follow Kalshi's terms
2. **Market Manipulation**: Avoid practices that could be considered manipulative
3. **Fair Access**: Don't attempt to gain unfair advantage
4. **System Integrity**: Ensure your bot doesn't disrupt exchange operations

### Risk Disclosures Required
- Trading involves significant financial risk
- Past performance doesn't guarantee future results
- Automated trading can amplify losses
- Technical failures can result in substantial losses

### Best Practices for Compliance
1. **Document Your Strategy**: Keep records of trading logic
2. **Implement Circuit Breakers**: Automatic shutdown on abnormal behavior
3. **Regular Testing**: Test in demo environment before live trading
4. **Monitor for Errors**: Log all trades and errors
5. **Stay Within Limits**: Respect position and trading limits

### Insurance and Liability
- Kalshi provides SIPC insurance up to $500,000
- No liability for trading losses from API usage
- User assumes all risk for automated trading

## 8. Practical Implementation Checklist

### Setup Phase
- [ ] Create Kalshi account
- [ ] Generate API keys
- [ ] Set up demo environment
- [ ] Install required libraries (requests, cryptography, etc.)
- [ ] Implement authentication functions

### Development Phase
- [ ] Build market data fetcher
- [ ] Implement order placement/cancellation
- [ ] Develop trading strategy
- [ ] Add risk management
- [ ] Create error handling
- [ ] Implement logging

### Testing Phase
- [ ] Test in demo environment
- [ ] Validate rate limit handling
- [ ] Test error scenarios
- [ ] Backtest strategy with historical data
- [ ] Paper trade for 2-4 weeks

### Deployment Phase
- [ ] Monitor initial trades closely
- [ ] Start with small position sizes
- [ ] Gradually increase exposure
- [ ] Continuously monitor performance
- [ ] Regularly update and optimize

### Ongoing Maintenance
- [ ] Monitor API changes
- [ ] Update for new market types
- [ ] Optimize strategy parameters
- [ ] Review risk management rules
- [ ] Keep compliance documentation current

## 9. Common Pitfalls and Solutions

### Technical Issues
1. **Rate Limit Exceeded**: Implement exponential backoff and request queuing
2. **Network Timeouts**: Add retry logic with jitter
3. **Order Duplication**: Use client_order_id for deduplication
4. **Data Inconsistency**: Implement data validation checks

### Trading Issues
1. **Slippage**: Use limit orders instead of market orders
2. **Low Liquidity**: Avoid illiquid markets for scalping
3. **Fast Market Conditions**: Reduce position sizes during volatility
4. **Overtrading**: Implement daily trade limits

### Risk Management Issues
1. **Concentration Risk**: Diversify across multiple markets
2. **Black Swan Events**: Implement maximum loss per day
3. **Strategy Decay**: Regularly review and adjust strategies
4. **Emotional Trading**: Stick to automated rules

## 10. Resources and Community

### Official Resources
- [Kalshi API Documentation](https://docs.kalshi.com/)
- [Python Starter Code](https://github.com/Kalshi/kalshi-starter-code-python)
- [Kalshi Discord](https://discord.gg/kalshi) - #dev and #support channels
- [Kalshi Help Center](https://help.kalshi.com/kalshi-api)

### Community Resources
- **Reddit**: r/Kalshi, r/algotrading
- **GitHub**: Search for "kalshi" repositories
- **DEV Community**: Tutorials and guides
- **Medium**: Technical articles on prediction market trading

### Monitoring Tools
- **Custom Dashboards**: Build with Grafana/Prometheus
- **Logging**: Use structured logging (JSON format)
- **Alerting**: Set up alerts for abnormal behavior
- **Performance Tracking**: Monitor Sharpe ratio, win rate, drawdown

---

**Disclaimer**: This guide is for educational purposes only. Trading prediction markets involves significant risk. Past performance is not indicative of future results. Always test strategies thoroughly in demo environments before trading with real money. Consult with financial and legal professionals before engaging in automated trading.