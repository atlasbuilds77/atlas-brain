#!/usr/bin/env python3
"""
Kalshi Trading Bot - Atlas's Trading Tool - FIXED VERSION

Fixed issue: get_positions() returns empty when user has active positions
Root cause: kalshi-python library uses deprecated parameters (count_down, count_up)
instead of correct count_filter parameter.

Usage: python kalshi-trader-fixed.py <command> [args]

Commands:
  balance              - Show account balance
  markets <query>      - Search markets
  buy <ticker> <qty>   - Buy YES contracts
  sell <ticker> <qty>  - Sell/Buy NO contracts
  positions            - Show current positions (FIXED)
  order <ticker> <side> <qty> <price> - Place limit order
"""

import os
import sys
import json
import time
import requests
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

# Configuration - Set these environment variables or edit directly
API_KEY_ID = os.environ.get("KALSHI_API_KEY_ID", "")
PRIVATE_KEY_PATH = os.environ.get("KALSHI_PRIVATE_KEY_PATH", os.path.expanduser("~/.kalshi/private_key.pem"))

# Use demo API for testing
USE_DEMO = os.environ.get("KALSHI_USE_DEMO", "false").lower() == "true"

def get_private_key():
    """Load private key from file"""
    if not os.path.exists(PRIVATE_KEY_PATH):
        print(f"ERROR: Private key not found at {PRIVATE_KEY_PATH}")
        print("Generate API keys at: https://kalshi.com/account/api")
        sys.exit(1)
    
    with open(PRIVATE_KEY_PATH, "r") as f:
        private_key_pem = f.read()
    
    return serialization.load_pem_private_key(
        private_key_pem.encode(),
        password=None
    )

def sign_message(message, private_key):
    """Sign a message with RSA private key"""
    signature = private_key.sign(
        message.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode()

def make_kalshi_request(method, endpoint, params=None):
    """Make authenticated request to Kalshi API directly"""
    base_url = "https://demo-api.kalshi.co/trade-api/v2" if USE_DEMO else "https://api.elections.kalshi.com/trade-api/v2"
    url = f"{base_url}{endpoint}"
    
    # Add query parameters if any
    if params:
        query_string = "&".join([f"{k}={v}" for k, v in params.items() if v is not None])
        if query_string:
            url = f"{url}?{query_string}"
    
    timestamp = str(int(time.time()))
    
    # Create message to sign: timestamp + method + endpoint
    message_to_sign = f"{timestamp}{method.upper()}{endpoint}"
    
    # Sign the message
    private_key = get_private_key()
    signature = sign_message(message_to_sign, private_key)
    
    # Make request
    headers = {
        "KALSHI-ACCESS-KEY": API_KEY_ID,
        "KALSHI-ACCESS-SIGNATURE": signature,
        "KALSHI-ACCESS-TIMESTAMP": timestamp,
    }
    
    response = requests.request(method, url, headers=headers)
    
    if response.status_code not in range(200, 299):
        print(f"API Error {response.status_code}: {response.text}")
        return None
    
    return response.json()

def show_balance():
    """Show account balance using direct API call"""
    data = make_kalshi_request("GET", "/portfolio/balance")
    if data:
        balance_cents = data.get('balance', 0)
        available_cents = data.get('available_balance', 0)
        print(f"Balance: ${balance_cents / 100:.2f}")
        print(f"Available: ${available_cents / 100:.2f}")

def search_markets(query):
    """Search for markets using direct API call"""
    data = make_kalshi_request("GET", "/markets", {"query": query, "limit": 10})
    if data and 'markets' in data:
        for m in data['markets']:
            print(f"{m.get('ticker', 'N/A')}: {m.get('title', 'N/A')}")
            yes_ask = m.get('yes_ask', 0)
            no_ask = m.get('no_ask', 0)
            print(f"  YES: {yes_ask}¢ | NO: {no_ask}¢")
            print()

def show_positions():
    """Show current positions - FIXED VERSION
    
    Uses direct API call with count_filter='position,total_traded' parameter
    to ensure all positions are returned, not just those with non-zero values.
    """
    print("Getting positions (using count_filter='position,total_traded')...")
    
    # The count_filter parameter is required to get positions with zero values
    # Without it, the API filters out positions where both position and total_traded are 0
    data = make_kalshi_request("GET", "/portfolio/positions", {
        "count_filter": "position,total_traded"
    })
    
    if not data:
        print("Failed to get positions")
        return
    
    positions = data.get('positions', [])
    
    if not positions:
        print("No open positions")
        return
    
    print(f"Found {len(positions)} position(s):")
    print("-" * 60)
    
    total_value = 0
    for pos in positions:
        ticker = pos.get('ticker', 'N/A')
        position_val = pos.get('position', 0)
        total_traded = pos.get('total_traded', 0)
        avg_price = pos.get('average_price', 0)
        realized_pnl = pos.get('realized_pnl', 0) / 10000.0  # Convert from centi-cents to dollars
        fees_paid = pos.get('fees_paid', 0) / 10000.0  # Convert from centi-cents to dollars
        
        # Calculate position value
        position_value = (position_val * avg_price) / 10000.0  # Convert from centi-cents to dollars
        total_value += position_value
        
        print(f"Market: {ticker}")
        print(f"  Position: {position_val} contracts")
        print(f"  Average Price: {avg_price}¢")
        print(f"  Position Value: ${position_value:.2f}")
        print(f"  Total Traded: {total_traded} contracts")
        print(f"  Realized P&L: ${realized_pnl:.2f}")
        print(f"  Fees Paid: ${fees_paid:.2f}")
        print()
    
    print(f"Total Positions Value: ${total_value:.2f}")
    print("-" * 60)

def place_order(ticker, side, quantity, price_cents=None):
    """Place an order using direct API call"""
    order_data = {
        "ticker": ticker,
        "side": side,  # "yes" or "no"
        "count": int(quantity),
        "type": "market" if price_cents is None else "limit",
    }
    
    if price_cents:
        if side == "yes":
            order_data["yes_price"] = int(price_cents)
        else:
            order_data["no_price"] = int(price_cents)
    
    data = make_kalshi_request("POST", "/portfolio/orders", order_data)
    if data and 'order' in data:
        order = data['order']
        print(f"Order placed: {order.get('order_id', 'N/A')}")
        print(f"Status: {order.get('status', 'N/A')}")
        print(f"Ticker: {order.get('ticker', 'N/A')}")
        print(f"Side: {order.get('side', 'N/A')}")
        print(f"Count: {order.get('count', 0)}")
        if price_cents:
            print(f"Price: {price_cents}¢")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    
    if not API_KEY_ID:
        print("ERROR: KALSHI_API_KEY_ID not set")
        print("Set it with: export KALSHI_API_KEY_ID='your-key-id'")
        sys.exit(1)
    
    cmd = sys.argv[1].lower()
    
    if cmd == "balance":
        show_balance()
    elif cmd == "markets" and len(sys.argv) > 2:
        search_markets(" ".join(sys.argv[2:]))
    elif cmd == "positions":
        show_positions()
    elif cmd == "buy" and len(sys.argv) >= 4:
        place_order(sys.argv[2], "yes", sys.argv[3])
    elif cmd == "sell" and len(sys.argv) >= 4:
        place_order(sys.argv[2], "no", sys.argv[3])
    elif cmd == "order" and len(sys.argv) >= 5:
        price = int(sys.argv[5]) if len(sys.argv) > 5 else None
        place_order(sys.argv[2], sys.argv[3], sys.argv[4], price)
    else:
        print(__doc__)

if __name__ == "__main__":
    main()