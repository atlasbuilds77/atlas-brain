# ROBINHOOD OPTIONS TRADING API ANALYSIS
**Deep Dive Research Report for Helios Scalping System**
*Analysis Date: January 23, 2026*

---

## EXECUTIVE SUMMARY

This report documents a comprehensive reverse-engineering analysis of Robinhood's Android application, focusing on options trading infrastructure, API endpoints, websocket implementation, and order execution logic. The goal is to extract actionable intelligence for building the Helios scalping system targeting SPY/QQQ 0DTE options.

**Key Findings:**
- RESTful API architecture using Retrofit with distinct endpoints for order submission, market data, and account management
- Real-time market data via websocket implementation (MdWebsocketSource) with L2 order book support
- Complex order validation system with multiple pre-flight checks before order submission
- Sophisticated options chain and quote management with real-time streaming capabilities

---

## 1. API ENDPOINT STRUCTURE

### 1.1 Base API Interface: OptionsApi.java

**Location:** `app/sources/com/robinhood/android/api/options/retrofit/OptionsApi.java`

#### Core Trading Endpoints

```kotlin
// ORDER SUBMISSION - PRIMARY ENDPOINT FOR SCALPING
@Headers({"X-Read-Timeout-Seconds-Override: 25", "X-Write-Timeout-Seconds-Override: 25"})
@POST("options/orders/")
@RequiresRegionGate(logIfNotInRegionGate = true, regionGates = {OptionsRegionGate.class})
Object submitOptionOrder(
    @Body ApiOptionOrderRequest orderRequest, 
    Continuation<? super ApiOptionOrder> continuation
);

// ORDER REPLACEMENT - FOR RAPID ORDER MODIFICATION
@Headers({"X-Read-Timeout-Seconds-Override: 25", "X-Write-Timeout-Seconds-Override: 25"})
@PATCH("options/orders/{orderToReplaceId}/")
@RequiresRegionGate(logIfNotInRegionGate = true, regionGates = {OptionsRegionGate.class})
Object replaceOptionOrder(
    @Path("orderToReplaceId") UUID uuid, 
    @Body ApiOptionOrderRequest orderRequest, 
    Continuation<? super ApiOptionOrder> continuation
);

// ORDER CANCELLATION
@POST("options/orders/{orderId}/cancel/")
@RequiresRegionGate(logIfNotInRegionGate = true, regionGates = {OptionsRegionGate.class})
Object cancelOptionOrder(
    @Path("orderId") UUID uuid, 
    @Body ApiOptionCancelOrderRequest cancelOrderRequest, 
    Continuation<? super Unit> continuation
);
```

#### Quote & Market Data Endpoints

```kotlin
// SINGLE OPTION QUOTE - CRITICAL FOR 0DTE SCALPING
@GET("marketdata/options/{optionInstrumentId}/")
@RequiresRegionGate(logIfNotInRegionGate = true, regionGates = {OptionsRegionGate.class})
Object getOptionQuote(
    @Path("optionInstrumentId") UUID uuid, 
    @Query("include_all_sessions") boolean includeAllSessions, 
    Continuation<? super ApiOptionQuote> continuation
);

// BATCH QUOTES - FOR MULTI-STRIKE SCANNING
@GET("marketdata/options/")
@RequiresRegionGate(logIfNotInRegionGate = true, regionGates = {OptionsRegionGate.class})
Object getOptionQuotes(
    @Query("ids") CommaSeparatedList<UUID> instrumentIds, 
    @Query("include_all_sessions") boolean includeAllSessions, 
    @Query("cursor") String paginationCursor, 
    Continuation<? super PaginatedResult<ApiOptionQuote>> continuation
);

// AGGREGATE STRATEGY QUOTES - FOR SPREAD PRICING
@GET("marketdata/options/strategy/quotes/")
@RequiresRegionGate(logIfNotInRegionGate = true, regionGates = {OptionsRegionGate.class})
Object getAggregateOptionQuotes(
    @Query("instruments") String commaSeparatedInstruments, 
    @Query("ratios") String commaSeparatedRatios, 
    @Query("types") String commaSeparatedPositionTypes, 
    @Query("strategy_ids") String commaSeparatedStrategyIds, 
    @Query("include_all_sessions") boolean includeAllSessions, 
    Continuation<? super PaginatedResult<ApiAggregateOptionQuote>> continuation
);
```

#### Options Chain Discovery

```kotlin
// GET ACTIVE OPTIONS FOR CHAIN - SPY/QQQ CHAIN DISCOVERY
@GET("options/instruments/?state=active")
@RequiresRegionGate(logIfNotInRegionGate = true, regionGates = {OptionsRegionGate.class})
Object getActiveOptionInstrumentsForChain(
    @Query("chain_id") UUID chainId,  // SPY or QQQ chain ID
    @Query("type") String optionType,  // "call" or "put"
    @Query("expiration_dates") String expirationDates,  // e.g., "2026-01-23" for 0DTE
    @Query("cursor") String paginationCursor,
    @Query("page_size") int pageSize,
    Continuation<? super PaginatedResult<ApiOptionInstrument>> continuation
);

// GET OPTION CHAINS - RETRIEVE SPY/QQQ CHAIN METADATA
@GET("options/chains/")
@RequiresRegionGate(regionGates = {OptionsRegionGate.class})
Object getOptionChains(
    @Query("cursor") String cursor,
    @Query("ids") String chainIds,
    Continuation<? super PaginatedResult<ApiOptionChain>> continuation
);
```

#### Order Validation & Fee Calculation

```kotlin
// OPTION ORDER FEE CALCULATION - PRE-TRADE
@GET("options/fees/")
@RequiresRegionGate(logIfNotInRegionGate = true, regionGates = {OptionsRegionGate.class})
Object getOptionOrderFee(
    @Query("account_number") String accountNumber,
    @Query("underlying_type") OptionChain.UnderlyingType underlyingType,
    @Query("legs") String legsJson,
    @Query("quantity") BigDecimal quantity,
    @Query("is_gold") Boolean isGold,
    @Query("limit_price") BigDecimal limitPrice,
    @Query("collateral") String collateral,
    @Query("trade_value_multiplier") int tradeValueMultiplier,
    @Query("order_direction") OrderDirection direction,
    @Query("trigger") OrderTrigger trigger,
    @Query("type") OrderType type,
    Continuation<? super ApiOptionOrderFee> continuation
);

// BUYING POWER CHECK - AVAILABLE CONTRACTS
@GET("options/orders/available_contracts/{account_number}/")
@RequiresRegionGate(logIfNotInRegionGate = true, regionGates = {OptionsRegionGate.class})
Object getOptionsOrderAvailableContracts(
    @Path("account_number") String accountNumber,
    @Query("strategy_code") String strategyCode,
    @Query("order_to_replace_id") UUID orderToReplaceId,
    Continuation<? super ApiOptionsDisplayedBuyingPower.NumOfContracts> continuation
);
```

#### Position Management

```kotlin
// GET OPTION POSITIONS - TRACK OPEN POSITIONS
@GET("options/positions/?nonzero=True&default_to_all_accounts=true")
@RequiresRegionGate(regionGates = {OptionsRegionGate.class})
Object getOptionPositions(
    @Query("account_numbers") CommaSeparatedList<String> accountNumbers,
    @Query("chain_ids") CommaSeparatedList<UUID> chainIds,  // Filter by SPY/QQQ
    @Query("cursor") String cursor,
    Continuation<? super PaginatedResult<ApiOptionPosition>> continuation
);

// GET AGGREGATE POSITIONS - MULTI-LEG POSITIONS
@GET("options/aggregate_positions/?nonzero=true&default_to_all_accounts=true")
@RequiresRegionGate(regionGates = {OptionsRegionGate.class})
Object getAggregateOptionPositions(
    @Query("account_numbers") CommaSeparatedList<String> accountNumbers,
    @Query("chain_ids") CommaSeparatedList<String> chainIds,
    @Query("cursor") String cursor,
    Continuation<? super PaginatedResult<ApiAggregateOptionPosition>> continuation
);
```

#### Historical Data

```kotlin
// OPTION HISTORICAL DATA - BACKFILLING
@GET("marketdata/options/historicals/{optionInstrumentId}/")
@RequiresRegionGate(logIfNotInRegionGate = true, regionGates = {OptionsRegionGate.class})
Object getOptionHistorical(
    @Path("optionInstrumentId") UUID instrumentId,
    @Query("interval") String interval,  // "5minute", "10minute", etc.
    @Query("span") String span,          // "day", "week"
    @Query("bounds") String bounds,      // "regular", "extended", "24_7"
    Continuation<? super ApiOptionHistorical> continuation
);
```

### 1.2 API Base URLs

From MdWebsocketSource.java and configuration files:

**REST API Base:**
- Production: `https://api.robinhood.com/`
- Brokeback (legacy): Used for options trading endpoints

**Websocket Base:**
- Market Data: `wss://api.robinhood.com/`

---

## 2. WEBSOCKET REAL-TIME DATA IMPLEMENTATION

### 2.1 Architecture Overview

**Primary Classes:**
- `BaseWebsocketSource<ResponseT, DataT>` - Base websocket management
- `MdWebsocketSource` - Market data specific implementation
- `MdTopic` - Topic subscription interface

### 2.2 Websocket Connection Flow

```java
// From MdWebsocketSource.java
public final class MdWebsocketSource extends BaseWebsocketSource<MdResponse, MarketData> {
    
    // Connection initialization
    addConnectionOpenListener(() -> {
        sendMessage(MdMessages.setupMessage(releaseVersion.getVersionName()));
    });
    
    // Response handler
    private void onResponseReceived(MdResponse response) {
        if (response instanceof MdResponse.Setup) {
            MdResponse.Setup setup = (MdResponse.Setup) response;
            configureKeepAlive(
                setup.getAcceptKeepAliveTimeoutInMs(), 
                setup.getKeepAliveTimeoutInMs()
            );
        } else if (response instanceof MdResponse.AuthState) {
            // Handle authentication
            if (state == UNAUTHORIZED) {
                sendMessage(MdMessages.authMessage("token"));
            } else if (state == AUTHORIZED) {
                sendMessage(MdMessages.getSetupLoggingMessage());
                sendMessage(MdMessages.getOpenFeedChannelMessage());
            }
        } else if (response instanceof MdResponse.ChannelOpened) {
            if (channel == 1) {  // Feed channel
                sendMessage(MdMessages.getFeedSetupMessage());
                onSocketReady();
            }
        } else if (response instanceof MdResponse.KeepAlive) {
            onKeepAliveReceived();
        } else if (response instanceof MdResponse.FeedDataResponse) {
            // Market data updates arrive here
        }
    }
}
```

### 2.3 Market Data Topics for Options

**Level 2 Full Order Book:**
```java
// From MdTopic.java - L2 Full Depth
public static final class EquityL2Full implements Feed<MdFeedData.L2Data> {
    private final String symbol;              // e.g., "SPY"
    private final boolean includeQuoteParams; // Include bid/ask details
    private final Boolean includeInactive;    // Include inactive quotes
    private final Boolean includeBboSource;   // Include best bid/offer source
    private final String bounds;              // "regular", "extended", "24_7"
    
    @Override
    public boolean getCacheLatestValue() {
        return true;  // Cache latest L2 data
    }
}
```

**Quote QBBO (Quote Best Bid/Offer):**
```java
public static final class EquityQuoteQbbo implements Feed<MdFeedData.QuoteData> {
    private final String symbol;
    private final boolean includeQuoteParams;
    private final Boolean includeInactive;
    private final Boolean includeBboSource;
    private final String bounds;
}
```

### 2.4 Subscription Management

```java
// From BaseWebsocketSource.java
public abstract class BaseWebsocketSource<ResponseT, DataT> 
    implements WebsocketSource<DataT> {
    
    // Subscribe to real-time stream
    public <T extends DataT> Flow<T> stream(WebsocketTopic<? extends T> topic) {
        return dataFlowManager.getDataFlow(
            topic, 
            configuration.getDataSubscriptionTimeout(), 
            this
        );
    }
    
    // Subscription state management
    public void onSubscribedChanged(WebsocketTopic<? extends T> topic, boolean subscribed) {
        synchronized (activeSubscriptionState) {
            if (subscribed && !activeSubscriptionState.contains(topic)) {
                activeSubscriptionState.add(topic);
                onActiveSubscriptionsChanged();
            } else if (!subscribed && activeSubscriptionState.contains(topic)) {
                activeSubscriptionState.remove(topic);
                onActiveSubscriptionsChanged();
            }
        }
    }
    
    // Generate subscription messages
    protected void onSubscriptionChanged(
        Set<? extends WebsocketTopic<? extends DataT>> addedTopics,
        Set<? extends WebsocketTopic<? extends DataT>> removedTopics
    ) {
        for (MdMessage message : generateMessagesFromSubscriptionChanged(addedTopics, removedTopics)) {
            sendMessage(message);
        }
    }
}
```

### 2.5 Keep-Alive Mechanism

```java
// Configurable keep-alive for stable connection
public void configureKeepAlive(long clientKeepAliveTimeoutInMs, long serverKeepAliveTimeoutInMs) {
    // Client ping interval
    clientKeepAliveJob.launch(coroutineScope, () -> {
        while (true) {
            delay(clientKeepAliveTimeoutInMs);
            sendMessage(MdMessages.getKeepAliveMessage());
        }
    });
    
    // Server timeout detection
    serverKeepAliveTimeout = serverKeepAliveTimeoutInMs;
    scheduleNextServerKeepAliveCheck();
}
```

---

## 3. ORDER EXECUTION LOGIC

### 3.1 Primary Order Controller: OptionOrderDuxo.java

**Location:** `app/sources/com/robinhood/android/trade/options/OptionOrderDuxo.java`
**Size:** 557KB (3494 lines) - Comprehensive order management

### 3.2 Order Submission Flow

```java
// Main order submission method
public final void submit(
    BrokerageAccountType analyticsAccountType,
    OptionOrderContext optionOrderContext,
    BigDecimal userEnteredLimitPriceForAnalytics,
    String chainSymbol,
    UUID orderId,
    OptionOrderMeta.Source source,
    MarketabilityType marketabilityType
) {
    // 1. Pre-flight validation
    // 2. Order construction
    // 3. API submission
    // 4. Response handling
    // 5. Analytics logging
}
```

### 3.3 Order Validation Pipeline

**Key Validation Steps:**

1. **Buying Power Check**
   - `OptionsBuyingPowerStore` - Verify account has sufficient capital
   - `getOptionsOrderAvailableContracts()` - Check max contracts allowed

2. **Order Check System**
   - `OptionOrderCheckStore` - Server-driven validation
   - Pre-submission checks for risk limits, position limits, etc.
   - Timeout: 5000ms (`OPTION_ORDER_CHECK_TIMEOUT_TIME`)

3. **Fee Calculation**
   - `OptionFeeStore` - Calculate commissions
   - `getOptionOrderFee()` API call

4. **Market Hours Validation**
   - `OptionMarketHoursStore` - Verify market is open
   - Support for extended hours trading

5. **Collateral Check**
   - For spread trades and complex strategies
   - `getOptionsOrderCollateral()` endpoint

### 3.4 Order State Management

```java
public final class OptionOrderViewState {
    // Order configuration
    private final OptionOrderType optionOrderType;  // LIMIT, MARKET, STOP_LIMIT
    private final OrderTimeInForce timeInForce;     // GTC, DAY, IOC, FOK
    private final OrderDirection directionOverride; // BUY_TO_OPEN, SELL_TO_CLOSE, etc.
    
    // Pricing
    private final LimitPriceWithSource limitPrice;
    private final BigDecimal stopPrice;             // For stop-limit orders
    private final BigDecimal quantity;
    
    // Validation state
    private final ApiOptionOrderCheck orderCheck;
    private final ValidationState validationState;
    private final BuyingPowerState buyingPowerState;
    
    // UI state
    private final DefaultOrderState formState;      // EDITING, REVIEWING, SUBMITTING
    private final boolean preserveUserInput;
    private final UiMarketability marketability;
    
    // Analytics
    private final OptionOrderFormSource source;
    private final PerformanceMetricEventData performanceData;
}
```

### 3.5 Order Types & Execution

**Supported Order Types:**
```java
public enum OptionOrderType {
    LIMIT,          // Limit price execution
    MARKET,         // Immediate market execution
    STOP_LIMIT,     // Stop-limit order
    STOP_MARKET     // Stop-market order (if supported)
}
```

**Time-In-Force Options:**
```java
public enum OrderTimeInForce {
    GTC,  // Good 'Til Canceled
    DAY,  // Day order
    IOC,  // Immediate or Cancel
    FOK   // Fill or Kill
}
```

### 3.6 Order Modification (Replace)

```java
// Replace order endpoint usage
public final void replaceOptionOrder(
    UUID orderToReplaceId,
    ApiOptionOrderRequest newOrderRequest
) {
    // Atomic replace operation - cancel + new order
    // Faster than cancel + submit for scalping
    // Maintains priority in some cases
}
```

---

## 4. SCALPING-SPECIFIC INSIGHTS

### 4.1 Latency Optimization

**Evidence from code:**

1. **Timeout Overrides**
   ```java
   @Headers({
       "X-Read-Timeout-Seconds-Override: 25", 
       "X-Write-Timeout-Seconds-Override: 25"
   })
   ```
   - Extended timeouts for order submission (25 seconds)
   - Separate from market data timeouts

2. **Latency Tracking**
   ```java
   @Experiment("OptionsOrderLatencyDecreaseExperiment")
   // Robinhood actively experiments with latency reduction
   ```

3. **Performance Logging**
   ```java
   PerformanceLogger.beginMetric(
       PerformanceMetricEventData.Name.OPTION_ORDER,
       context: PerformanceMetricEventData.Context.Options(chainId)
   );
   ```

### 4.2 Quick Trade Patterns

**Evidence of rapid trading support:**

1. **Order Replacement vs Cancel+Submit**
   - `replaceOptionOrder()` is faster than separate cancel+submit
   - Maintains queue position in some market conditions

2. **Debounced Limit Price Updates**
   ```java
   setDebouncedLimitPrice(BigDecimal limitPrice)
   // Prevents excessive API calls during rapid price adjustments
   ```

3. **Pre-filled Order Templates**
   ```java
   // Support for pre-filled orders
   private final BigDecimal prefilledQuantity;
   private final OptionOrderType prefilledOrderType;
   private final OrderTimeInForce prefilledTimeInForce;
   ```

### 4.3 Market Data Update Frequency

**Websocket Configuration:**
- Real-time streaming for L2 order book data
- Separate channels for quotes vs. order book
- Keep-alive mechanism ensures connection stability
- Automatic reconnection logic with exponential backoff

### 4.4 0DTE-Specific Considerations

**Trade-on-Expiration Settings:**
```java
// From ApiOptionSettings
@PATCH("options/option_settings/{account_number}/")
Object submitTradeOnExpirationRequest(
    @Path("account_number") String accountNumber,
    @Body ApiOptionSettings.TradeOnExpirationRequest request
);
```

**Expiration Date Filtering:**
```java
// Filter for 0DTE options
getActiveOptionInstrumentsForChain(
    chainId: SPY_CHAIN_ID,
    type: "call" | "put",
    expirationDates: LocalDate.now().toString(), // Today's date for 0DTE
    pageSize: 100
);
```

---

## 5. SPY/QQQ TRADING IMPLEMENTATION

### 5.1 Chain ID Discovery

**Step 1: Get Chain Metadata**
```kotlin
// Retrieve SPY and QQQ chain IDs
val chains = getOptionChains(
    cursor = null,
    ids = "SPY,QQQ"  // Symbol-based lookup
)

// Extract chain IDs for subsequent calls
val spyChainId: UUID = chains.find { it.symbol == "SPY" }.id
val qqqChainId: UUID = chains.find { it.symbol == "QQQ" }.id
```

**Step 2: Get Active 0DTE Strikes**
```kotlin
val today = LocalDate.now()
val spyOptions = getActiveOptionInstrumentsForChain(
    chainId = spyChainId,
    type = "call",  // or "put"
    expirationDates = today.toString(),
    cursor = null,
    pageSize = 200  // Get all strikes at once
)
```

### 5.2 Real-Time Quote Streaming

**Setup Websocket Subscriptions:**
```kotlin
// Subscribe to SPY L2 order book
val spyL2Topic = MdTopic.Feed.EquityL2Full(
    symbol = "SPY",
    includeQuoteParams = true,
    includeInactive = false,
    includeBboSource = true,
    bounds = "regular"  // or "extended" for extended hours
)

val spyL2Stream: Flow<MdFeedData.L2Data> = mdWebsocketSource.stream(spyL2Topic)

// Subscribe to individual option quotes
val optionQuoteTopic = MdTopic.Feed.EquityQuoteQbbo(
    symbol = optionInstrument.tradability_symbol,  // e.g., "SPY 260123C00500000"
    includeQuoteParams = true,
    includeInactive = false,
    includeBboSource = true,
    bounds = "regular"
)

val optionQuoteStream: Flow<MdFeedData.QuoteData> = mdWebsocketSource.stream(optionQuoteTopic)
```

### 5.3 Scalping Order Flow Example

```kotlin
// 1. Monitor underlying (SPY) for entry signal
spyL2Stream.collect { l2Data ->
    if (scalpingConditionMet(l2Data)) {
        // 2. Select target option strike
        val targetStrike = selectOptimalStrike(currentSpyPrice, strategy)
        
        // 3. Get current option quote
        val optionQuote = getOptionQuote(
            optionInstrumentId = targetStrike.id,
            includeAllSessions = false
        )
        
        // 4. Calculate entry price
        val entryPrice = calculateEntryPrice(
            bid = optionQuote.bid_price,
            ask = optionQuote.ask_price,
            strategy = "aggressive"  // bid for buys, ask for sells
        )
        
        // 5. Validate buying power
        val availableContracts = getOptionsOrderAvailableContracts(
            accountNumber = account,
            strategyCode = "single_leg",
            orderToReplaceId = null
        )
        
        // 6. Submit order
        val order = submitOptionOrder(
            ApiOptionOrderRequest(
                account = accountUrl,
                legs = listOf(
                    OrderLeg(
                        option = targetStrike.url,
                        side = "buy",  // or "sell"
                        position_effect = "open",
                        ratio_quantity = 1
                    )
                ),
                type = "limit",
                price = entryPrice,
                quantity = min(scalpQuantity, availableContracts),
                time_in_force = "ioc",  // Immediate-or-Cancel for scalping
                trigger = "immediate",
                direction = "debit"
            )
        )
        
        // 7. Monitor for fill
        val fillStream = getOptionsOrder(order.id)
        
        // 8. Set profit target and stop loss
        if (order.state == "filled") {
            val exitPrice = entryPrice + profitTarget
            val stopPrice = entryPrice - stopLoss
            
            // Submit limit sell order
            submitOptionOrder(
                ApiOptionOrderRequest(
                    legs = listOf(OrderLeg(
                        option = targetStrike.url,
                        side = "sell",
                        position_effect = "close",
                        ratio_quantity = order.processed_quantity
                    )),
                    type = "limit",
                    price = exitPrice,
                    quantity = order.processed_quantity,
                    time_in_force = "day"
                )
            )
        }
    }
}
```

---

## 6. RISK MANAGEMENT PATTERNS

### 6.1 Position Limits

```java
// From OptionOrderCheckStore
public class OptionOrderCheck {
    // Server-side risk checks
    public List<ApiOptionOrderCheck.Alert> alerts;
    public int maxOrderSize;
    public boolean isDayTradeWarning;
    public boolean requiresPatternDayTraderStatus;
}
```

**Detected Risk Controls:**
1. Maximum order size enforcement
2. Day trade counter (PDT rule)
3. Buying power validation
4. Position concentration limits
5. Spread collateral requirements

### 6.2 Order Validation Timeout

```java
// 5-second timeout for order validation
public static final long OPTION_ORDER_CHECK_TIMEOUT_TIME = 5000;

// Fallback behavior on timeout
if (orderCheckTimedOut) {
    // Can proceed with caution or abort
    // User configurable in app settings
}
```

### 6.3 Marketability Checks

```java
public enum UiMarketability {
    GOOD_TO_TRADE,
    HARD_TO_EXERCISE,
    HARD_TO_TRADE,
    NOT_TRADABLE,
    LOADING
}

// Real-time marketability monitoring
val marketability = optionMarketabilityStore.getOptionOrderMarketability(
    optionInstrumentId = option.id,
    orderDirection = "buy"
)
```

---

## 7. HELIOS SCALPING SYSTEM RECOMMENDATIONS

### 7.1 API Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    HELIOS CORE ENGINE                        │
├─────────────────────────────────────────────────────────────┤
│  Strategy Layer                                              │
│  ├─ SPY Scalping Strategy                                    │
│  ├─ QQQ Scalping Strategy                                    │
│  └─ Risk Manager                                             │
├─────────────────────────────────────────────────────────────┤
│  Data Layer                                                  │
│  ├─ Websocket Client (MdWebsocketSource pattern)            │
│  │   ├─ SPY L2 Order Book Stream                            │
│  │   ├─ QQQ L2 Order Book Stream                            │
│  │   └─ Option Quote Streams (per position)                 │
│  ├─ REST API Client (OptionsApi pattern)                    │
│  │   ├─ Order Submission                                    │
│  │   ├─ Order Management                                    │
│  │   └─ Position Monitoring                                 │
│  └─ State Manager                                           │
│      ├─ Active Orders                                       │
│      ├─ Open Positions                                      │
│      └─ Account Status                                      │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 Recommended Order Types for Scalping

**Entry Orders:**
- **Type:** `LIMIT`
- **Time-in-Force:** `IOC` (Immediate-or-Cancel)
- **Reason:** Ensures price control while avoiding hanging orders

**Exit Orders (Profit Target):**
- **Type:** `LIMIT`
- **Time-in-Force:** `GTC` or `DAY`
- **Reason:** Allows order to rest in book for favorable fills

**Stop Loss:**
- **Type:** `STOP_LIMIT` or `MARKET` (if available)
- **Time-in-Force:** `DAY`
- **Reason:** Protects against adverse moves

### 7.3 Critical Implementation Details

1. **Pre-flight Optimization**
   - Cache chain IDs for SPY/QQQ (rarely change)
   - Pre-fetch active strikes at market open
   - Maintain persistent websocket connection
   - Pre-validate buying power before entry signals

2. **Order Lifecycle Management**
   ```python
   class ScalpingOrder:
       entry_order_id: UUID
       exit_order_id: Optional[UUID]
       stop_order_id: Optional[UUID]
       
       def submit_entry(self):
           # Submit IOC limit order
           pass
       
       def on_fill(self, fill_data):
           # Immediately submit exit orders
           self.submit_profit_target()
           self.submit_stop_loss()
       
       def on_partial_fill(self, fill_data):
           # Adjust exit order quantities
           pass
       
       def cancel_all(self):
           # Emergency exit - cancel all related orders
           pass
   ```

3. **Latency Reduction Tactics**
   - Use `replaceOptionOrder()` instead of cancel+submit when adjusting prices
   - Batch quote requests when possible
   - Maintain local order book state to reduce API calls
   - Implement request debouncing for rapid price updates

4. **0DTE-Specific Handling**
   - Enable "Trade on Expiration" setting via API
   - Filter option chains by today's date
   - Monitor time decay (theta) acceleration
   - Increase monitoring frequency in final hour

### 7.4 Sample Configuration

```json
{
  "helios_config": {
    "symbols": ["SPY", "QQQ"],
    "order_settings": {
      "entry": {
        "type": "limit",
        "time_in_force": "ioc",
        "price_offset_from_mid": -0.05
      },
      "exit_profit": {
        "type": "limit",
        "time_in_force": "gtc",
        "profit_target_percent": 0.20
      },
      "exit_stop": {
        "type": "stop_limit",
        "time_in_force": "day",
        "stop_loss_percent": 0.10
      }
    },
    "risk_management": {
      "max_position_size": 10,
      "max_daily_trades": 50,
      "max_loss_per_trade": 100.00,
      "max_daily_loss": 500.00
    },
    "websocket": {
      "reconnect_attempts": 5,
      "reconnect_delay_ms": 1000,
      "keep_alive_interval_ms": 30000,
      "subscription_timeout_ms": 5000
    },
    "api": {
      "base_url": "https://api.robinhood.com/",
      "request_timeout_ms": 10000,
      "order_timeout_ms": 25000,
      "rate_limit_per_second": 10
    }
  }
}
```

---

## 8. CODE SNIPPETS & EXAMPLES

### 8.1 Websocket Connection Setup

```kotlin
// Initialize market data websocket
class HeliosWebsocketManager(
    private val releaseVersion: ReleaseVersion,
    private val authToken: String
) {
    private val mdSource = MdWebsocketSource(
        releaseVersion = releaseVersion,
        rootCoroutineScope = CoroutineScope(Dispatchers.IO),
        messageHandler = MdMessageHandler(),
        moshi = LazyMoshi(),
        connectionManager = MdWebsocketConnectionManager(),
        targetBackend = TargetBackend.PRODUCTION
    )
    
    fun subscribeToSPYOrderBook(): Flow<MdFeedData.L2Data> {
        val topic = MdTopic.Feed.EquityL2Full(
            symbol = "SPY",
            includeQuoteParams = true,
            includeInactive = false,
            includeBboSource = true,
            bounds = "regular"
        )
        return mdSource.stream(topic)
    }
    
    fun subscribeToOptionQuote(tradabilitySymbol: String): Flow<MdFeedData.QuoteData> {
        val topic = MdTopic.Feed.EquityQuoteQbbo(
            symbol = tradabilitySymbol,
            includeQuoteParams = true,
            includeInactive = false,
            includeBboSource = true,
            bounds = "regular"
        )
        return mdSource.stream(topic)
    }
}
```

### 8.2 Order Submission with Error Handling

```kotlin
class HeliosOrderManager(
    private val optionsApi: OptionsApi,
    private val accountNumber: String
) {
    suspend fun submitScalpEntry(
        optionInstrument: ApiOptionInstrument,
        quantity: Int,
        limitPrice: BigDecimal,
        side: String  // "buy" or "sell"
    ): Result<ApiOptionOrder> = withContext(Dispatchers.IO) {
        try {
            // 1. Validate buying power
            val availableContracts = optionsApi.getOptionsOrderAvailableContracts(
                accountNumber = accountNumber,
                strategyCode = "single_leg",
                orderToReplaceId = null
            )
            
            if (quantity > availableContracts.numOfContracts) {
                return@withContext Result.failure(
                    InsufficientBuyingPowerException("Requested $quantity, available $availableContracts")
                )
            }
            
            // 2. Calculate fees
            val fees = optionsApi.getOptionOrderFee(
                accountNumber = accountNumber,
                underlyingType = OptionChain.UnderlyingType.EQUITY,
                legs = buildLegsJson(optionInstrument, side, quantity),
                quantity = BigDecimal(quantity),
                isGold = true,  // Assuming Robinhood Gold
                limitPrice = limitPrice,
                collateral = null,
                tradeValueMultiplier = 100,  // Standard options multiplier
                orderDirection = if (side == "buy") OrderDirection.DEBIT else OrderDirection.CREDIT,
                trigger = OrderTrigger.IMMEDIATE,
                type = OrderType.LIMIT
            )
            
            // 3. Submit order
            val orderRequest = ApiOptionOrderRequest(
                account = "https://api.robinhood.com/accounts/$accountNumber/",
                legs = listOf(
                    ApiOptionOrderRequest.Leg(
                        option = optionInstrument.url,
                        side = side,
                        position_effect = "open",
                        ratio_quantity = 1
                    )
                ),
                type = "limit",
                price = limitPrice,
                quantity = quantity,
                time_in_force = "ioc",
                trigger = "immediate",
                direction = if (side == "buy") "debit" else "credit",
                override_day_trade_checks = false,
                override_dtbp_checks = false
            )
            
            val order = optionsApi.submitOptionOrder(orderRequest)
            Result.success(order)
            
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun submitScalpExit(
        optionInstrument: ApiOptionInstrument,
        quantity: Int,
        limitPrice: BigDecimal
    ): Result<ApiOptionOrder> {
        // Similar to entry but with position_effect = "close"
        // and opposite side
    }
    
    suspend fun replaceOrder(
        originalOrderId: UUID,
        newLimitPrice: BigDecimal
    ): Result<ApiOptionOrder> = withContext(Dispatchers.IO) {
        try {
            // Fetch original order
            val originalOrder = optionsApi.getOptionsOrder(originalOrderId)
            
            // Build replacement request
            val replaceRequest = ApiOptionOrderRequest(
                account = originalOrder.account,
                legs = originalOrder.legs,
                type = originalOrder.type,
                price = newLimitPrice,  // Updated price
                quantity = originalOrder.quantity,
                time_in_force = originalOrder.time_in_force,
                trigger = originalOrder.trigger,
                direction = originalOrder.direction
            )
            
            val replacedOrder = optionsApi.replaceOptionOrder(
                orderToReplaceId = originalOrderId,
                orderRequest = replaceRequest
            )
            
            Result.success(replacedOrder)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

### 8.3 Complete Scalping Trade Example

```kotlin
class ScalpingTrade(
    private val orderManager: HeliosOrderManager,
    private val websocketManager: HeliosWebsocketManager,
    private val riskParams: RiskParameters
) {
    private var entryOrder: ApiOptionOrder? = null
    private var exitOrder: ApiOptionOrder? = null
    private var stopOrder: ApiOptionOrder? = null
    
    suspend fun execute(
        optionInstrument: ApiOptionInstrument,
        entrySignal: TradingSignal
    ) {
        // 1. Calculate entry price
        val entryPrice = calculateEntryPrice(
            signal = entrySignal,
            bid = entrySignal.optionBid,
            ask = entrySignal.optionAsk
        )
        
        // 2. Submit entry order
        val entryResult = orderManager.submitScalpEntry(
            optionInstrument = optionInstrument,
            quantity = riskParams.positionSize,
            limitPrice = entryPrice,
            side = "buy"  // or "sell" for short scalps
        )
        
        entryOrder = entryResult.getOrNull() ?: return
        
        // 3. Monitor for fill
        launch {
            monitorOrderFill(entryOrder!!.id) { fillData ->
                onEntryFilled(fillData)
            }
        }
    }
    
    private suspend fun onEntryFilled(fillData: OrderFillData) {
        val filledQuantity = fillData.processedQuantity
        val avgFillPrice = fillData.avgFillPrice
        
        // Calculate exit prices
        val profitTargetPrice = avgFillPrice * (1 + riskParams.profitTargetPercent)
        val stopLossPrice = avgFillPrice * (1 - riskParams.stopLossPercent)
        
        // Submit profit target
        val exitResult = orderManager.submitScalpExit(
            optionInstrument = fillData.optionInstrument,
            quantity = filledQuantity,
            limitPrice = profitTargetPrice
        )
        exitOrder = exitResult.getOrNull()
        
        // Submit stop loss (if supported)
        // Note: May need to use market order or manual monitoring
        
        // Monitor both exit conditions
        launch {
            monitorExitConditions(
                optionQuoteStream = websocketManager.subscribeToOptionQuote(
                    fillData.optionInstrument.tradability_symbol
                ),
                profitTarget = profitTargetPrice,
                stopLoss = stopLossPrice
            )
        }
    }
    
    private suspend fun monitorExitConditions(
        optionQuoteStream: Flow<MdFeedData.QuoteData>,
        profitTarget: BigDecimal,
        stopLoss: BigDecimal
    ) {
        optionQuoteStream.collect { quote ->
            // Check stop loss
            if (quote.bid_price <= stopLoss) {
                cancelProfitTarget()
                submitMarketExit()
            }
            
            // Profit target handled by resting limit order
            // But could manually exit if conditions change
        }
    }
}
```

---

## 9. ADDITIONAL FINDINGS

### 9.1 Undocumented Features

1. **Combo Orders Support**
   ```kotlin
   // Found in: com/robinhood/android/options/combo/api/ApiComboOrder.java
   // Allows multi-leg strategies in single order
   @GET("combo/orders/{orderId}/")
   Object getComboOrder(@Path("orderId") UUID uuid)
   ```

2. **Options Rolling**
   ```kotlin
   // Maximum rollable quantity endpoint
   @GET("options/maximum_rollable_quantity/{strategy_code}/")
   Object getOptionMaxRollableQuantity(
       @Path("strategy_code") String strategyCode,
       @Query("account_number") String accountNumber
   )
   ```

3. **Corporate Actions Tracking**
   ```kotlin
   @GET("options/corp_actions/?default_to_all_accounts=true")
   Object getOptionCorporateActions(
       @Query("cursor") String cursor,
       @Query("updated_at[gte]") LocalDate updatedAt
   )
   ```

### 9.2 Analytics & Logging

Robinhood implements extensive analytics tracking:
- Order submission latency
- Fill quality metrics
- Market impact analysis
- User interaction patterns

**Key Metrics Tracked:**
```java
public class PerformanceMetricEventData {
    public enum Name {
        OPTION_ORDER,
        OPTION_CHAIN_LOAD,
        MARKET_DATA_LATENCY,
        ORDER_FILL_SPEED
    }
}
```

### 9.3 Experiments Framework

Robinhood runs continuous A/B tests:
```java
public static final List<Experiment<SimpleVariant>> sdocImprovementExperiments = listOf(
    Experiments.OptionsOrderPathMaxOrderSizeV2,
    Experiments.OptionsOrderPathAmbiguousOrderDirection,
    Experiments.OptionsOrderPathMarketTradingHours,
    Experiments.OptionsOrderPathStopMarketTradingHours,
    Experiments.OptionsOrderPathBidAskSpread,
    Experiments.OptionsOrderPathNeccMultileg,
    Experiments.OptionsOrderPathMaxOrderSizeV3
);
```

This suggests active optimization of the order flow.

---

## 10. HELIOS IMPLEMENTATION ROADMAP

### Phase 1: Infrastructure (Week 1-2)
- [ ] Implement REST API client based on OptionsApi interface
- [ ] Implement Websocket client based on MdWebsocketSource pattern
- [ ] Build authentication & session management
- [ ] Create order state management system
- [ ] Implement local order book maintenance

### Phase 2: Core Trading Engine (Week 3-4)
- [ ] Develop scalping strategy logic
- [ ] Implement entry signal detection
- [ ] Build exit management (profit targets, stops)
- [ ] Create position sizing algorithm
- [ ] Implement risk management controls

### Phase 3: Real-Time Data Integration (Week 5)
- [ ] SPY/QQQ L2 order book streaming
- [ ] Option quote streaming for active positions
- [ ] Market hours detection
- [ ] Latency monitoring & optimization

### Phase 4: Order Execution (Week 6)
- [ ] Order submission flow
- [ ] Fill monitoring
- [ ] Order replacement logic
- [ ] Emergency exit mechanisms
- [ ] Retry & error handling

### Phase 5: Testing & Optimization (Week 7-8)
- [ ] Paper trading integration
- [ ] Latency benchmarking
- [ ] Strategy backtesting with real API responses
- [ ] Load testing order submission
- [ ] Failover & disaster recovery

### Phase 6: Production Deployment (Week 9-10)
- [ ] Live trading with minimal capital
- [ ] Performance monitoring dashboard
- [ ] Alert system (fills, errors, P&L)
- [ ] Trade reconciliation
- [ ] Daily performance reporting

---

## 11. RISKS & LIMITATIONS

### 11.1 API-Specific Risks

1. **Rate Limiting**
   - Unknown exact rate limits
   - Need to implement exponential backoff
   - Monitor for 429 responses

2. **Authentication Changes**
   - OAuth token expiration handling
   - MFA challenges
   - Device fingerprinting

3. **API Versioning**
   - Endpoints may change without notice
   - Need version detection mechanism
   - Fallback strategies

### 11.2 Trading Risks

1. **Fill Quality**
   - IOC orders may not fill at desired prices
   - Slippage on fast-moving options
   - Partial fills complicate exit management

2. **Market Data Latency**
   - Websocket delays during high volatility
   - Stale quotes on thinly traded strikes
   - Race conditions between quote updates and order submission

3. **0DTE-Specific Risks**
   - Rapid theta decay
   - Wide bid-ask spreads
   - Low liquidity on far OTM strikes
   - Pin risk near expiration

### 11.3 Technical Risks

1. **Connection Stability**
   - Websocket disconnections
   - API downtime
   - Network issues

2. **State Synchronization**
   - Local state vs. server state
   - Order status polling lag
   - Position reconciliation

3. **Error Handling**
   - Unhandled order rejections
   - Failed cancellations
   - Duplicate orders

---

## 12. CONCLUSION

The Robinhood Android decompilation reveals a sophisticated options trading infrastructure with:

✅ **Well-designed REST API** with comprehensive endpoints for options trading
✅ **Real-time websocket implementation** supporting L2 order book data
✅ **Complex order validation pipeline** with risk management built-in
✅ **Support for rapid trading** via order replacement and IOC orders
✅ **Extensive analytics** suggesting latency-conscious design

**Key Takeaways for Helios:**

1. **Use IOC limit orders** for scalping entries to control price and avoid hanging orders
2. **Leverage replaceOptionOrder()** instead of cancel+submit for faster execution
3. **Maintain persistent websocket connections** for SPY/QQQ and active option positions
4. **Pre-validate buying power** before signal generation to reduce latency
5. **Implement local state management** to minimize API calls
6. **Monitor order fill status** aggressively to trigger exit orders immediately

**Estimated Development Time:** 8-10 weeks for full production-ready system

**Recommended Next Steps:**
1. Build minimal REST API client and test order submission
2. Implement websocket connection and verify real-time data quality
3. Develop paper trading version of scalping logic
4. Benchmark latency from signal to order confirmation
5. Gradually increase position sizes as system proves reliable

---

## APPENDIX A: CRITICAL FILE LOCATIONS

```
robinhood-decompiled/
├── app/sources/
│   ├── com/robinhood/android/api/options/
│   │   └── retrofit/
│   │       ├── OptionsApi.java                    # Main API interface
│   │       ├── OptionsBonfireApi.java             # Alternative endpoint
│   │       └── OptionsAccountSwitcherBonfireApi.java
│   ├── com/robinhood/android/trade/options/
│   │   ├── OptionOrderDuxo.java                   # Order controller (557KB)
│   │   ├── OptionOrderViewState.java              # Order state model
│   │   ├── OptionOrderFragment.java               # UI integration
│   │   └── confirmation/                          # Order confirmation flow
│   ├── com/robinhood/android/options/
│   │   ├── contracts/                             # Contract models
│   │   ├── aggregatequotes/                       # Quote aggregation
│   │   └── optionsstring/                         # String formatting
│   ├── com/robinhood/websocket/
│   │   ├── BaseWebsocketSource.java               # Websocket base class
│   │   ├── WebsocketConnectionManager.java        # Connection management
│   │   └── p413md/
│   │       ├── MdWebsocketSource.java             # Market data websocket
│   │       ├── MdTopic.java                       # Topic definitions
│   │       └── MdMessageHandler.java              # Message processing
│   └── com/robinhood/librobinhood/data/store/
│       ├── OptionQuoteStore.java                  # Quote caching
│       ├── OptionOrderStore.java                  # Order management
│       ├── OptionsBuyingPowerStore.java           # Buying power tracking
│       └── OptionMarketHoursStore.java            # Market hours data
```

---

## APPENDIX B: GLOSSARY

| Term | Definition |
|------|------------|
| **0DTE** | Zero Days to Expiration - options expiring today |
| **IOC** | Immediate-or-Cancel - order type that fills immediately or cancels |
| **GTC** | Good-'Til-Canceled - order remains active until filled or manually canceled |
| **L2 Data** | Level 2 market data - full order book depth |
| **QBBO** | Quote Best Bid/Offer - top of book quote data |
| **PDT** | Pattern Day Trader - regulatory designation requiring $25k minimum equity |
| **Marketability** | Measure of how easily an option can be traded |
| **Collateral** | Required capital for spread and complex option strategies |
| **Strategy Code** | Identifier for multi-leg option strategies (e.g., "single_leg", "vertical_spread") |

---

**End of Report**

*This analysis is for educational and research purposes. Trading options involves substantial risk of loss. Always comply with applicable regulations and broker terms of service.*
