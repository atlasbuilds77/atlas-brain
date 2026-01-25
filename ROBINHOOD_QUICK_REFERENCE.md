# ROBINHOOD API QUICK REFERENCE
**Quick lookup for Helios scalping implementation**

## CRITICAL ENDPOINTS

### Order Submission
```
POST /options/orders/
Headers: X-Read-Timeout-Seconds-Override: 25, X-Write-Timeout-Seconds-Override: 25
Body: ApiOptionOrderRequest
Returns: ApiOptionOrder
```

### Order Replacement (FASTEST for scalping)
```
PATCH /options/orders/{orderId}/
Headers: X-Read-Timeout-Seconds-Override: 25, X-Write-Timeout-Seconds-Override: 25
Body: ApiOptionOrderRequest
Returns: ApiOptionOrder
```

### Order Cancellation
```
POST /options/orders/{orderId}/cancel/
Body: ApiOptionCancelOrderRequest
Returns: void
```

### Real-Time Quote (Single Option)
```
GET /marketdata/options/{optionInstrumentId}/
Query: include_all_sessions=false
Returns: ApiOptionQuote
```

### Batch Quotes
```
GET /marketdata/options/
Query: ids=<comma_separated_uuids>, include_all_sessions=false, cursor=<pagination>
Returns: PaginatedResult<ApiOptionQuote>
```

### Get 0DTE Options
```
GET /options/instruments/?state=active
Query: 
  - chain_id=<SPY_or_QQQ_chain_id>
  - type=call|put
  - expiration_dates=2026-01-23 (today's date)
  - page_size=200
Returns: PaginatedResult<ApiOptionInstrument>
```

### Buying Power Check
```
GET /options/orders/available_contracts/{account_number}/
Query: strategy_code=single_leg, order_to_replace_id=null
Returns: ApiOptionsDisplayedBuyingPower.NumOfContracts
```

### Fee Calculation
```
GET /options/fees/
Query: account_number, underlying_type, legs, quantity, is_gold, limit_price, 
       collateral, trade_value_multiplier, order_direction, trigger, type
Returns: ApiOptionOrderFee
```

## WEBSOCKET TOPICS

### SPY/QQQ L2 Order Book
```kotlin
MdTopic.Feed.EquityL2Full(
    symbol = "SPY",  // or "QQQ"
    includeQuoteParams = true,
    includeInactive = false,
    includeBboSource = true,
    bounds = "regular"
)
```

### Option Quote Stream
```kotlin
MdTopic.Feed.EquityQuoteQbbo(
    symbol = optionInstrument.tradability_symbol,  // e.g., "SPY 260123C00500000"
    includeQuoteParams = true,
    includeInactive = false,
    includeBboSource = true,
    bounds = "regular"
)
```

## ORDER REQUEST STRUCTURE

### Scalping Entry (Buy-to-Open)
```json
{
  "account": "https://api.robinhood.com/accounts/{account_number}/",
  "legs": [
    {
      "option": "https://api.robinhood.com/options/instruments/{uuid}/",
      "side": "buy",
      "position_effect": "open",
      "ratio_quantity": 1
    }
  ],
  "type": "limit",
  "price": "1.50",
  "quantity": 10,
  "time_in_force": "ioc",
  "trigger": "immediate",
  "direction": "debit",
  "override_day_trade_checks": false,
  "override_dtbp_checks": false
}
```

### Scalping Exit (Sell-to-Close)
```json
{
  "account": "https://api.robinhood.com/accounts/{account_number}/",
  "legs": [
    {
      "option": "https://api.robinhood.com/options/instruments/{uuid}/",
      "side": "sell",
      "position_effect": "close",
      "ratio_quantity": 1
    }
  ],
  "type": "limit",
  "price": "1.80",
  "quantity": 10,
  "time_in_force": "gtc",
  "trigger": "immediate",
  "direction": "credit"
}
```

## ORDER TYPES & TIME-IN-FORCE

### Order Types
- `limit` - Limit price (RECOMMENDED for scalping)
- `market` - Market order (use with caution)
- `stop_limit` - Stop-limit order

### Time-in-Force
- `ioc` - Immediate-or-Cancel (BEST for entries)
- `gtc` - Good-'Til-Canceled (BEST for exits)
- `day` - Day order
- `fok` - Fill-or-Kill

### Position Effects
- `open` - Open new position
- `close` - Close existing position

### Sides
- `buy` - Buy contracts
- `sell` - Sell contracts

## WEBSOCKET CONNECTION FLOW

1. **Connect** to `wss://api.robinhood.com/`
2. **Send Setup Message** with app version
3. **Authenticate** when prompted
4. **Open Feed Channel** (channel 1)
5. **Subscribe to Topics** (SPY, QQQ, option quotes)
6. **Send Keep-Alive** every 30 seconds
7. **Monitor for Server Keep-Alive** (timeout detection)

## SPY/QQQ CHAIN IDS

**How to Get:**
```
GET /options/chains/?ids=SPY,QQQ
Returns: List of chains with UUIDs
```

**Cache These:** Chain IDs rarely change

## RECOMMENDED SCALPING PARAMETERS

### Entry Orders
- **Type:** `limit`
- **Time-in-Force:** `ioc`
- **Price:** Mid-market or slightly aggressive

### Exit Orders (Profit)
- **Type:** `limit`
- **Time-in-Force:** `gtc` or `day`
- **Price:** Entry + target profit (e.g., 20%)

### Exit Orders (Stop)
- **Type:** `market` (if supported) or monitor manually
- **Time-in-Force:** `day`
- **Trigger:** Entry - max loss (e.g., 10%)

## LATENCY OPTIMIZATION

1. **Use replaceOptionOrder()** instead of cancel + submit
2. **Pre-validate buying power** before signal
3. **Cache chain IDs** for SPY/QQQ
4. **Maintain persistent websocket** connection
5. **Debounce rapid price updates** (avoid API spam)
6. **Local order book state** to reduce API calls

## ERROR CODES TO WATCH

- `429` - Rate limit exceeded
- `400` - Bad request (check order parameters)
- `401` - Authentication failed
- `403` - Insufficient permissions
- `404` - Resource not found (invalid option ID)
- `500` - Server error (retry with backoff)

## VALIDATION CHECKLIST

Before submitting order:
- [ ] Buying power available
- [ ] Valid option instrument ID
- [ ] Reasonable limit price (within bid-ask spread)
- [ ] Quantity > 0
- [ ] Market hours check (if required)
- [ ] Account has options trading enabled
- [ ] Not exceeding PDT limits

## MONITORING CHECKLIST

After order submission:
- [ ] Order ID captured
- [ ] Monitor order status (every 100ms)
- [ ] Detect fills immediately
- [ ] Submit exit orders on fill
- [ ] Track position in local state
- [ ] Log all actions for reconciliation

## EMERGENCY PROCEDURES

### Cancel All Orders
```
For each active order:
  POST /options/orders/{order_id}/cancel/
```

### Close All Positions (Market Exit)
```
For each open position:
  Submit market sell order with position_effect="close"
```

### Websocket Reconnection
```
1. Close existing connection
2. Wait 1 second (exponential backoff)
3. Reconnect
4. Re-authenticate
5. Re-subscribe to all topics
```

## DEBUGGING TIPS

1. **Enable verbose logging** for all API calls
2. **Track request/response times** for latency analysis
3. **Log websocket messages** for data quality verification
4. **Compare local state** vs. server state regularly
5. **Monitor fill quality** (fill price vs. limit price)

## USEFUL CALCULATIONS

### Option Tradability Symbol Format
```
Format: {SYMBOL} {YYMMDD}{C|P}{STRIKE*1000}
Example: SPY 260123C00500000
  - SPY = Symbol
  - 260123 = Jan 23, 2026
  - C = Call (P for Put)
  - 00500000 = $500.00 strike
```

### Profit Target Calculation
```
Entry Price: $1.50
Profit Target: 20%
Exit Price: $1.50 * 1.20 = $1.80
```

### Stop Loss Calculation
```
Entry Price: $1.50
Stop Loss: 10%
Stop Price: $1.50 * 0.90 = $1.35
```

### Position Sizing
```
Account Risk Per Trade: $100
Entry Price: $1.50
Stop Loss: $1.35
Risk Per Contract: ($1.50 - $1.35) * 100 = $15
Position Size: $100 / $15 = 6.67 contracts (round to 6)
```

## TESTING ENDPOINTS

Before going live:
1. Test with $1 limit orders on liquid options
2. Verify order cancellation works
3. Test order replacement latency
4. Verify websocket data quality
5. Test partial fill handling
6. Verify position reconciliation

---

**Last Updated:** January 23, 2026
**Status:** Ready for implementation
