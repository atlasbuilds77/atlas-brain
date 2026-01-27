#!/usr/bin/env python3
"""
Hyperliquid Python SDK Quick Start Example
A minimal working example covering essential trading functions
"""

import json
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants

# ============================================================================
# CONFIGURATION
# ============================================================================

# Create a config.json file with your wallet details:
# {
#   "account_address": "0xYourWalletAddress",
#   "secret_key": "YourPrivateKey"
# }

CONFIG_FILE = "config.json"

# Use TESTNET for development, MAINNET for production
USE_TESTNET = True

# ============================================================================
# INITIALIZATION
# ============================================================================

def initialize():
    """Initialize the SDK with wallet credentials"""
    try:
        with open(CONFIG_FILE) as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Create {CONFIG_FILE} with your wallet credentials")
        print('''Example config.json:
{
  "account_address": "0xYourWalletAddress",
  "secret_key": "YourPrivateKey"
}''')
        return None, None, None
    
    base_url = constants.TESTNET_API_URL if USE_TESTNET else constants.MAINNET_API_URL
    
    # Initialize Info client (read-only data)
    info = Info(base_url, skip_ws=True)
    
    # Initialize Exchange client (trading operations)
    exchange = Exchange(
        wallet_address=config["account_address"],
        private_key=config["secret_key"],
        base_url=base_url,
        account_address=config["account_address"]
    )
    
    return config, info, exchange

# ============================================================================
# ACCOUNT FUNCTIONS
# ============================================================================

def get_account_info(info, address):
    """Get account balance and positions"""
    user_state = info.user_state(address)
    
    # Extract account value
    account_value = float(user_state.get("marginSummary", {}).get("accountValue", 0))
    
    # Extract positions
    positions = []
    for position in user_state.get("assetPositions", []):
        pos = position["position"]
        positions.append({
            "coin": pos["coin"],
            "size": float(pos["szi"]),
            "entry_price": float(pos["entryPx"]),
            "leverage": float(pos["leverage"]),
            "pnl": float(pos["unrealizedPnl"])
        })
    
    return {
        "account_value": account_value,
        "positions": positions
    }

def get_open_orders(info, address):
    """Get all open orders"""
    return info.open_orders(address)

# ============================================================================
# TRADING FUNCTIONS
# ============================================================================

def place_market_order(exchange, coin, is_buy, size):
    """Place a market order"""
    print(f"Placing market order: {'BUY' if is_buy else 'SELL'} {size} {coin}")
    
    result = exchange.market_open(
        coin=coin,
        is_buy=is_buy,
        sz=size,
        reduce_only=False
    )
    
    print(f"Market order result: {result}")
    return result

def place_limit_order(exchange, coin, is_buy, size, price, tif="Gtc"):
    """Place a limit order"""
    print(f"Placing limit order: {'BUY' if is_buy else 'SELL'} {size} {coin} @ ${price}")
    
    result = exchange.order(
        coin=coin,
        is_buy=is_buy,
        sz=size,
        limit_px=price,
        order_type={"limit": {"tif": tif}},
        reduce_only=False
    )
    
    print(f"Limit order result: {result}")
    return result

def set_leverage(exchange, coin, leverage, is_cross=True):
    """Set leverage for a coin"""
    print(f"Setting {'cross' if is_cross else 'isolated'} leverage for {coin} to {leverage}x")
    
    result = exchange.update_leverage(leverage, coin, is_cross)
    
    print(f"Leverage update result: {result}")
    return result

def place_stop_loss(exchange, coin, is_buy, size, trigger_price):
    """Place a stop loss order"""
    print(f"Placing stop loss: {'BUY' if is_buy else 'SELL'} {size} {coin} @ ${trigger_price}")
    
    result = exchange.order(
        coin=coin,
        is_buy=is_buy,
        sz=size,
        limit_px=trigger_price,
        order_type={
            "trigger": {
                "triggerPx": str(trigger_price),
                "isMarket": True,
                "tpsl": "sl"
            }
        },
        reduce_only=True
    )
    
    print(f"Stop loss result: {result}")
    return result

def cancel_order(exchange, coin, order_id):
    """Cancel an order by ID"""
    print(f"Cancelling order {order_id} for {coin}")
    
    result = exchange.cancel(coin, order_id)
    
    print(f"Cancel result: {result}")
    return result

# ============================================================================
# MARKET DATA FUNCTIONS
# ============================================================================

def get_market_info(info, coin=None):
    """Get market metadata"""
    meta = info.meta()
    
    if coin:
        # Get specific coin info
        coin_info = next((item for item in meta['universe'] if item['name'] == coin), None)
        if coin_info:
            return {
                "name": coin_info["name"],
                "sz_decimals": coin_info["szDecimals"],
                "max_leverage": coin_info["maxLeverage"],
                "mark_price": float(coin_info.get("markPx", 0))
            }
        return None
    else:
        # Get all coins
        return [item["name"] for item in meta["universe"]]

# ============================================================================
# MAIN EXAMPLE
# ============================================================================

def main():
    """Main example demonstrating key SDK functions"""
    print("=" * 60)
    print("Hyperliquid Python SDK Quick Start")
    print("=" * 60)
    
    # Initialize
    config, info, exchange = initialize()
    if not config:
        return
    
    address = config["account_address"]
    network = "TESTNET" if USE_TESTNET else "MAINNET"
    print(f"Connected to {network} with address: {address[:10]}...{address[-8:]}")
    print()
    
    # 1. Get account info
    print("1. ACCOUNT INFORMATION")
    print("-" * 40)
    account_info = get_account_info(info, address)
    print(f"Account Value: ${account_info['account_value']:.2f}")
    
    if account_info['positions']:
        print("Open Positions:")
        for pos in account_info['positions']:
            print(f"  {pos['coin']}: {pos['size']} @ ${pos['entry_price']:.2f} "
                  f"(Leverage: {pos['leverage']}x, PnL: ${pos['pnl']:.2f})")
    else:
        print("No open positions")
    print()
    
    # 2. Get market info
    print("2. MARKET INFORMATION")
    print("-" * 40)
    available_coins = get_market_info(info)
    print(f"Available coins: {', '.join(available_coins[:5])}...")
    
    btc_info = get_market_info(info, "BTC")
    if btc_info:
        print(f"BTC Info: Max leverage {btc_info['max_leverage']}x, "
              f"Mark price: ${btc_info['mark_price']:.2f}")
    print()
    
    # 3. Example trading operations (commented out for safety)
    print("3. TRADING OPERATIONS (Examples - Commented Out)")
    print("-" * 40)
    print("Uncomment the examples below to execute trades")
    print()
    
    # # Example: Set leverage
    # set_leverage(exchange, "BTC", 3, True)
    # print()
    
    # # Example: Place limit order
    # if btc_info:
    #     limit_price = btc_info['mark_price'] * 0.95  # 5% below market
    #     place_limit_order(exchange, "BTC", True, 0.001, limit_price, "Gtc")
    #     print()
    
    # # Example: Place stop loss
    # if btc_info:
    #     stop_price = btc_info['mark_price'] * 0.90  # 10% below market
    #     place_stop_loss(exchange, "BTC", False, 0.001, stop_price)
    #     print()
    
    # # Example: Get open orders
    # open_orders = get_open_orders(info, address)
    # if open_orders:
    #     print("Open Orders:")
    #     for order in open_orders:
    #         print(f"  {order['coin']}: {order['side']} {order['sz']} @ ${order['limitPx']}")
    # else:
    #     print("No open orders")
    # print()
    
    print("=" * 60)
    print("Quick Start Complete!")
    print("Remember:")
    print("1. Always test on TESTNET first")
    print("2. Implement proper error handling")
    print("3. Respect rate limits (1200 weight/minute)")
    print("4. Use API wallets for production trading")
    print("=" * 60)

if __name__ == "__main__":
    main()