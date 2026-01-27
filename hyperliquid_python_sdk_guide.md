# Hyperliquid Python SDK - Quick Start Guide

## 1. Installation and Setup

### Prerequisites
- Python 3.10 (recommended - some dependencies have issues with 3.11)
- pip package manager

### Installation
```bash
pip install hyperliquid-python-sdk
```

### Dependencies
The SDK requires:
- `eth-account` for cryptographic operations
- `websocket-client` for real-time communication
- `requests` for HTTP requests
- `msgpack` for data serialization

## 2. Authentication and API Keys

### Wallet Connection
Hyperliquid uses wallet-based authentication rather than traditional API keys. You need:
1. Your wallet's public address (account_address)
2. Your wallet's private key (secret_key)

### Creating API Wallet (Optional but Recommended)
For programmatic trading, it's recommended to create a dedicated API wallet:

1. Go to https://app.hyperliquid.xyz/API
2. Connect your main wallet
3. Generate a new API private key
4. Authorize the API wallet

**Important**: When using an API wallet:
- Set the API wallet's private key as `secret_key` in config
- Set the main wallet's public key as `account_address` (not the API wallet's address)

### Configuration File
Create a `config.json` file:
```json
{
  "account_address": "0xYourMainWalletPublicAddress",
  "secret_key": "YourPrivateKeyOrApiWalletPrivateKey"
}
```

## 3. Core Trading Functions

### Initialization
```python
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants
import json

# Load configuration
with open('config.json') as f:
    config = json.load(f)

# Initialize for testnet (use constants.MAINNET_API_URL for mainnet)
info = Info(constants.TESTNET_API_URL, skip_ws=True)
exchange = Exchange(
    wallet_address=config["account_address"],
    private_key=config["secret_key"],
    base_url=constants.TESTNET_API_URL,
    account_address=config["account_address"]
)
```

### Get User State
```python
# Get user state including positions and balances
user_state = info.user_state(config["account_address"])
print(f"User state: {json.dumps(user_state, indent=2)}")

# Extract positions
positions = []
for position in user_state.get("assetPositions", []):
    positions.append(position["position"])
    
# Extract balances
balances = user_state.get("marginSummary", {}).get("accountValue", "0")
print(f"Account value: ${balances}")
```

### Get Market Data
```python
# Get all market metadata
meta = info.meta()
print(f"Available coins: {[coin for coin in meta['universe']]}")

# Get specific coin metadata
btc_meta = next((item for item in meta['universe'] if item['name'] == 'BTC'), None)
if btc_meta:
    print(f"BTC metadata: {btc_meta}")
```

## 4. Trading Examples

### Market Order
```python
def place_market_order(coin, is_buy, size):
    """Place a market order"""
    order_result = exchange.market_open(
        coin=coin,
        is_buy=is_buy,
        sz=size,
        reduce_only=False
    )
    return order_result

# Example: Buy 0.01 BTC at market price
result = place_market_order("BTC", True, 0.01)
print(f"Market order result: {result}")
```

### Limit Order
```python
def place_limit_order(coin, is_buy, size, price, tif="Gtc"):
    """Place a limit order with specified time-in-force"""
    order_result = exchange.order(
        coin=coin,
        is_buy=is_buy,
        sz=size,
        limit_px=price,
        order_type={"limit": {"tif": tif}},  # Gtc, Ioc, or Alo
        reduce_only=False
    )
    return order_result

# Example: Sell 0.01 BTC at $50,000 limit (Good Til Canceled)
result = place_limit_order("BTC", False, 0.01, 50000, "Gtc")
print(f"Limit order result: {result}")
```

### Setting Leverage
```python
def set_leverage(coin, leverage, is_cross=True):
    """Set leverage for a specific coin"""
    result = exchange.update_leverage(leverage, coin, is_cross)
    return result

# Example: Set cross leverage to 5x for BTC
result = set_leverage("BTC", 5, True)
print(f"Leverage update result: {result}")
```

### Stop Loss Order
```python
def place_stop_loss(coin, is_buy, size, trigger_price, is_market=True):
    """Place a stop loss order"""
    order_result = exchange.order(
        coin=coin,
        is_buy=is_buy,
        sz=size,
        limit_px=trigger_price,  # For stop-market, this is the trigger price
        order_type={
            "trigger": {
                "triggerPx": str(trigger_price),
                "isMarket": is_market,
                "tpsl": "sl"  # "sl" for stop loss, "tp" for take profit
            }
        },
        reduce_only=True  # Stop loss should be reduce-only
    )
    return order_result

# Example: Stop loss to sell 0.01 BTC if price drops to $48,000
result = place_stop_loss("BTC", False, 0.01, 48000, True)
print(f"Stop loss order result: {result}")
```

### Cancel Order
```python
def cancel_order(coin, order_id):
    """Cancel a specific order by order ID"""
    result = exchange.cancel(coin, order_id)
    return result

# Example: Cancel order with ID 123456
result = cancel_order("BTC", 123456)
print(f"Cancel order result: {result}")

# Cancel all orders for a coin
def cancel_all_orders(coin):
    """Cancel all open orders for a specific coin"""
    open_orders = info.open_orders(config["account_address"])
    for order in open_orders:
        if order["coin"] == coin:
            exchange.cancel(coin, order["oid"])
```

### Get Open Positions
```python
def get_open_positions():
    """Get all open positions"""
    user_state = info.user_state(config["account_address"])
    positions = []
    
    for position in user_state.get("assetPositions", []):
        pos = position["position"]
        positions.append({
            "coin": pos["coin"],
            "size": float(pos["szi"]),
            "entry_price": float(pos["entryPx"]),
            "leverage": float(pos["leverage"]),
            "unrealized_pnl": float(pos["unrealizedPnl"]),
            "liquidation_price": float(pos.get("liquidationPx", 0))
        })
    
    return positions

positions = get_open_positions()
for pos in positions:
    print(f"Position: {pos}")
```

## 5. Rate Limits and Best Practices

### Rate Limits
Hyperliquid has two types of rate limits:

1. **IP-based limits** (1200 weight per minute):
   - Most exchange API requests: weight 1 + floor(batch_length / 40)
   - Info requests: typically weight 20
   - Some specific endpoints have different weights

2. **Address-based limits**:
   - 1 request per 1 USDC traded cumulatively
   - Initial buffer: 10,000 requests per address
   - When rate limited: 1 request every 10 seconds
   - Cancels have higher limits to ensure open orders can be canceled

### Best Practices

1. **Use API Wallets**: Create separate API wallets for different trading processes
2. **Batch Requests**: Combine multiple orders/cancels into single requests
3. **Handle Disconnects**: Implement reconnection logic for WebSockets
4. **Use Testnet**: Always test on testnet first (https://api.hyperliquid-testnet.xyz)
5. **Monitor Limits**: Track your request weight consumption
6. **Error Handling**: Implement robust error handling for rate limits

### Batch Processing Example
```python
def batch_orders(orders):
    """Place multiple orders in a single batch"""
    # orders should be a list of order dictionaries
    batch_result = exchange.batch_order(orders)
    return batch_result

# Example batch order
orders = [
    {
        "coin": "BTC",
        "is_buy": True,
        "sz": 0.01,
        "limit_px": 49000,
        "order_type": {"limit": {"tif": "Gtc"}}
    },
    {
        "coin": "ETH",
        "is_buy": True,
        "sz": 0.1,
        "limit_px": 2500,
        "order_type": {"limit": {"tif": "Gtc"}}
    }
]

result = batch_orders(orders)
print(f"Batch order result: {result}")
```

## 6. WebSocket for Real-time Data

### Basic WebSocket Connection
```python
import asyncio
from hyperliquid.utils.websocket import WebsocketManager

async def handle_message(message):
    """Handle incoming WebSocket messages"""
    print(f"Received: {message}")
    
    # Process different message types
    if message.get("channel") == "l2Book":
        # Order book data
        process_orderbook(message["data"])
    elif message.get("channel") == "trades":
        # Trade data
        process_trades(message["data"])
    elif message.get("channel") == "userEvents":
        # User-specific events (fills, orders)
        process_user_events(message["data"])

def process_orderbook(data):
    """Process order book data"""
    coin = data["coin"]
    levels = data["levels"]
    print(f"Order book for {coin}: {levels}")

def process_trades(data):
    """Process trade data"""
    for trade in data:
        print(f"Trade: {trade}")

def process_user_events(data):
    """Process user events (fills, order updates)"""
    print(f"User event: {data}")

# Initialize WebSocket manager
ws_manager = WebsocketManager(
    base_url=constants.TESTNET_API_URL,
    account_address=config["account_address"],
    private_key=config["secret_key"]
)

# Subscribe to channels
async def subscribe_to_channels():
    # Subscribe to BTC order book
    await ws_manager.subscribe({"type": "l2Book", "coin": "BTC"})
    
    # Subscribe to BTC trades
    await ws_manager.subscribe({"type": "trades", "coin": "BTC"})
    
    # Subscribe to user events
    await ws_manager.subscribe({"type": "userEvents", "user": config["account_address"]})

# Run WebSocket client
async def run_websocket():
    await ws_manager.connect()
    await subscribe_to_channels()
    
    # Start listening for messages
    async for message in ws_manager.listen():
        await handle_message(message)

# Run in asyncio event loop
# asyncio.run(run_websocket())
```

### WebSocket Subscription Types
```python
# Available subscription types:
subscriptions = {
    # Order book level 2
    "l2Book": {"type": "l2Book", "coin": "BTC"},
    
    # Recent trades
    "trades": {"type": "trades", "coin": "BTC"},
    
    # All mid prices
    "allMids": {"type": "allMids"},
    
    # User-specific events (requires authentication)
    "userEvents": {"type": "userEvents", "user": config["account_address"]},
    
    # Candle data
    "candle": {"type": "candle", "coin": "BTC", "interval": "1m"}
}
```

### WebSocket Best Practices
1. **Reconnection Logic**: Always implement reconnection with exponential backoff
2. **Heartbeats**: Monitor connection health
3. **Message Queuing**: Use queues to handle message bursts
4. **Snapshot on Reconnect**: Request snapshot data after reconnection
5. **Connection Limits**: Maximum 100 connections, 1000 subscriptions, 10 unique users

## Complete Trading Bot Example

```python
import asyncio
import json
from datetime import datetime
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants

class HyperliquidTradingBot:
    def __init__(self, config_path="config.json"):
        with open(config_path) as f:
            self.config = json.load(f)
        
        self.info = Info(constants.TESTNET_API_URL, skip_ws=True)
        self.exchange = Exchange(
            wallet_address=self.config["account_address"],
            private_key=self.config["secret_key"],
            base_url=constants.TESTNET_API_URL,
            account_address=self.config["account_address"]
        )
        
    def get_account_summary(self):
        """Get account summary including balance and positions"""
        user_state = self.info.user_state(self.config["account_address"])
        
        summary = {
            "account_value": float(user_state.get("marginSummary", {}).get("accountValue", 0)),
            "total_collateral": float(user_state.get("marginSummary", {}).get("totalCollateral", 0)),
            "total_margin_used": float(user_state.get("marginSummary", {}).get("totalMarginUsed", 0)),
            "positions": []
        }
        
        for position in user_state.get("assetPositions", []):
            pos = position["position"]
            summary["positions"].append({
                "coin": pos["coin"],
                "size": float(pos["szi"]),
                "entry_price": float(pos["entryPx"]),
                "leverage": float(pos["leverage"]),
                "pnl": float(pos["unrealizedPnl"])
            })
        
        return summary
    
    def place_trade_with_stop_loss(self, coin, is_buy, size, entry_price=None, stop_loss_pct=0.05):
        """Place a trade with automatic stop loss"""
        
        # Get current price if entry_price not provided
        if entry_price is None:
            meta = self.info.meta()
            coin_meta = next((item for item in meta['universe'] if item['name'] == coin), None)
            if coin_meta:
                entry_price = float(coin_meta.get("markPx", 0))
        
        # Calculate stop loss price
        if is_buy:
            stop_price = entry_price * (1 - stop_loss_pct)
        else:
            stop_price = entry_price * (1 + stop_loss_pct)
        
        # Place main order (market if no entry_price provided)
        if entry_price:
            # Limit order
            order_result = self.exchange.order(
                coin=coin,
                is_buy=is_buy,
                sz=size,
                limit_px=entry_price,
                order_type={"limit": {"tif": "Gtc"}},
                reduce_only=False
            )
        else:
            # Market order
            order_result = self.exchange.market_open(
                coin=coin,
                is_buy=is_buy,
                sz=size,
                reduce_only=False
            )
        
        # Place stop loss
        stop_result = self.exchange.order(
            coin=coin,
            is_buy=not is_buy,  # Opposite direction for stop loss
            sz=size,
            limit_px=stop_price,
            order_type={
                "trigger": {
                    "triggerPx": str(stop_price),
                    "isMarket": True,
                    "tpsl": "sl"
                }
            },
            reduce_only=True
        )
        
        return {
            "main_order": order_result,
            "stop_loss": stop_result
        }
    
    def run_strategy(self):
        """Example trading strategy"""
        print(f"Starting trading bot at {datetime.now()}")
        
        # Get account summary
        summary = self.get_account_summary()
        print(f"Account value: ${summary['account_value']:.2f}")
        
        # Example: Place a BTC trade with 2% stop loss
        if summary['account_value'] > 100:  # Only trade if sufficient balance
            trade_result = self.place_trade_with_stop_loss(
                coin="BTC",
                is_buy=True,
                size=0.001,
                stop_loss_pct=0.02
            )
            print(f"Trade placed: {trade_result}")

# Usage
if __name__ == "__main__":
    bot = HyperliquidTradingBot()
    bot.run_strategy()
```

## Troubleshooting

### Common Issues

1. **Python Version**: Use Python 3.10 for best compatibility
2. **Authentication Errors**: Ensure correct wallet address and private key
3. **Rate Limiting**: Implement request throttling and batching
4. **WebSocket Disconnects**: Add reconnection logic
5. **Testnet vs Mainnet**: Always test on testnet first

### Error Handling
```python
try:
    result = exchange.order(...)
except Exception as e:
    print(f"Order failed: {e}")
    
    # Check for specific error types
    if "rate limit" in str(e).lower():
        print("Rate limited - implement backoff")
    elif "insufficient balance" in str(e).lower():
        print("Insufficient balance")
```

## Resources

- **Official Documentation**: https://hyperliquid.gitbook.io/hyperliquid-docs
- **Python SDK GitHub**: https://github.com/hyperliquid-dex/hyperliquid-python-sdk
- **API Endpoints**: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api
- **Testnet**: https://api.hyperliquid-testnet.xyz
- **Mainnet**: https://api.hyperliquid.xyz

## Security Notes

1. **Never commit private keys** to version control
2. **Use environment variables** for sensitive data
3. **Implement API wallet rotation** periodically
4. **Use separate wallets** for different trading strategies
5. **Monitor for unauthorized activity** regularly

This guide provides a comprehensive starting point for using the Hyperliquid Python SDK. Always refer to the official documentation for the most up-to-date information and best practices.