#!/usr/bin/env python3
"""
Kalshi Trading Bot - Atlas's Trading Tool
Usage: python kalshi-trader.py <command> [args]

Commands:
  balance              - Show account balance
  markets <query>      - Search markets
  buy <ticker> <qty>   - Buy YES contracts
  sell <ticker> <qty>  - Sell/Buy NO contracts
  positions            - Show current positions
  order <ticker> <side> <qty> <price> - Place limit order
"""

import os
import sys
import json

try:
    from kalshi_python import Configuration, KalshiClient
except ImportError:
    print("Installing kalshi-python...")
    os.system("pip install kalshi-python")
    from kalshi_python import Configuration, KalshiClient

# Configuration - Set these environment variables or edit directly
API_KEY_ID = os.environ.get("KALSHI_API_KEY_ID", "")
PRIVATE_KEY_PATH = os.environ.get("KALSHI_PRIVATE_KEY_PATH", os.path.expanduser("~/.kalshi/private_key.pem"))

# Use demo API for testing
USE_DEMO = os.environ.get("KALSHI_USE_DEMO", "false").lower() == "true"

def get_client():
    """Initialize Kalshi client"""
    if not API_KEY_ID:
        print("ERROR: KALSHI_API_KEY_ID not set")
        print("Set it with: export KALSHI_API_KEY_ID='your-key-id'")
        sys.exit(1)
    
    if not os.path.exists(PRIVATE_KEY_PATH):
        print(f"ERROR: Private key not found at {PRIVATE_KEY_PATH}")
        print("Generate API keys at: https://kalshi.com/account/api")
        sys.exit(1)
    
    with open(PRIVATE_KEY_PATH, "r") as f:
        private_key = f.read()
    
    host = "https://demo-api.kalshi.co/trade-api/v2" if USE_DEMO else "https://api.elections.kalshi.com/trade-api/v2"
    
    config = Configuration(host=host)
    config.api_key_id = API_KEY_ID
    config.private_key_pem = private_key
    
    return KalshiClient(config)

def show_balance():
    """Show account balance"""
    client = get_client()
    balance = client.get_balance()
    print(f"Balance: ${balance.balance / 100:.2f}")

def search_markets(query):
    """Search for markets"""
    client = get_client()
    markets = client.get_markets(query=query, limit=10)
    for m in markets.markets:
        print(f"{m.ticker}: {m.title}")
        print(f"  YES: {m.yes_ask}¢ | NO: {m.no_ask}¢")
        print()

def show_positions():
    """Show current positions"""
    client = get_client()
    positions = client.get_positions()
    if not positions.positions:
        print("No open positions")
        return
    
    for pos in positions.positions:
        print(f"{pos.ticker}: {pos.position} contracts @ {pos.average_price}¢")

def place_order(ticker, side, quantity, price_cents=None, action="buy"):
    """Place an order"""
    client = get_client()
    
    order = {
        "ticker": ticker,
        "action": action,  # "buy" or "sell"
        "side": side,  # "yes" or "no"
        "count": int(quantity),
        "type": "market" if price_cents is None else "limit",
    }
    
    if price_cents:
        order["yes_price"] = int(price_cents) if side == "yes" else None
        order["no_price"] = int(price_cents) if side == "no" else None
    
    result = client.create_order(**order)
    print(f"Order placed: {result.order.order_id}")
    print(f"Status: {result.order.status}")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    
    cmd = sys.argv[1].lower()
    
    if cmd == "balance":
        show_balance()
    elif cmd == "markets" and len(sys.argv) > 2:
        search_markets(" ".join(sys.argv[2:]))
    elif cmd == "positions":
        show_positions()
    elif cmd == "buy" and len(sys.argv) >= 4:
        place_order(sys.argv[2], "yes", sys.argv[3], action="buy")
    elif cmd == "sell" and len(sys.argv) >= 4:
        # Sell YES positions we own
        place_order(sys.argv[2], "yes", sys.argv[3], action="sell")
    elif cmd == "order" and len(sys.argv) >= 5:
        price = int(sys.argv[5]) if len(sys.argv) > 5 else None
        place_order(sys.argv[2], sys.argv[3], sys.argv[4], price)
    else:
        print(__doc__)

if __name__ == "__main__":
    main()
