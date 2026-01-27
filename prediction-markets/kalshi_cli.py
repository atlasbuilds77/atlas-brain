#!/usr/bin/env python3
"""Kalshi API CLI - USE WITH arb-bot venv: source ~/clawd/prediction-markets/arb-bot/venv/bin/activate"""
import json
import time
import base64
import sys
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.backends import default_backend
import requests

# Load config
with open("/Users/atlasbuilds/.clawdbot/credentials/kalshi/config.json") as f:
    config = json.load(f)

API_KEY_ID = config["apiKeyId"]
with open(config["privateKeyPath"], "rb") as f:
    PRIVATE_KEY = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())

BASE_URL = "https://api.elections.kalshi.com"

def kalshi_request(method, path, data=None):
    """Make authenticated request to Kalshi API using PSS padding"""
    timestamp = str(int(time.time() * 1000))
    full_path = "/trade-api/v2" + path
    message = f"{timestamp}{method}{full_path}".encode('utf-8')
    
    # IMPORTANT: Use PSS padding, not PKCS1v15!
    signature = PRIVATE_KEY.sign(
        message,
        asym_padding.PSS(
            mgf=asym_padding.MGF1(hashes.SHA256()),
            salt_length=asym_padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    
    headers = {
        "KALSHI-ACCESS-KEY": API_KEY_ID,
        "KALSHI-ACCESS-SIGNATURE": base64.b64encode(signature).decode('utf-8'),
        "KALSHI-ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json"
    }
    
    url = BASE_URL + full_path
    if method == "GET":
        resp = requests.get(url, headers=headers)
    elif method == "POST":
        resp = requests.post(url, headers=headers, json=data)
    elif method == "DELETE":
        resp = requests.delete(url, headers=headers)
    
    return resp.json()

def cmd_balance():
    result = kalshi_request("GET", "/portfolio/balance")
    cash = result.get('balance', 0) / 100
    portfolio = result.get('portfolio_value', 0) / 100
    print(f"💰 Cash: ${cash:.2f}")
    print(f"📊 Portfolio: ${portfolio:.2f}")
    print(f"📈 Total: ${cash + portfolio:.2f}")

def cmd_positions():
    result = kalshi_request("GET", "/portfolio/positions")
    print("=== ACTIVE POSITIONS ===")
    for p in result.get('market_positions', []):
        ticker = p.get('ticker', '')
        pos = p.get('position', 0)
        if pos != 0:
            exposure = p.get('market_exposure', 0) / 100
            avg_price = (exposure / pos * 100) if pos > 0 else 0
            print(f"{ticker}: {pos} contracts @ {avg_price:.0f}c (${exposure:.2f})")

def cmd_market(ticker):
    result = kalshi_request("GET", f"/markets/{ticker}")
    m = result.get('market', {})
    print(f"Ticker: {m.get('ticker')}")
    print(f"Title: {m.get('title')}")
    print(f"Yes: {m.get('yes_bid')}c / {m.get('yes_ask')}c")
    print(f"No: {m.get('no_bid')}c / {m.get('no_ask')}c")
    print(f"Volume: ${m.get('volume', 0)/100:.0f}")
    print(f"Status: {m.get('status')}")

def cmd_order(ticker, side, count, price_cents):
    """Place a limit order. side = 'yes' or 'no'"""
    data = {
        "ticker": ticker,
        "action": "buy",
        "side": side,
        "type": "limit",
        "count": count,
    }
    if side == "yes":
        data["yes_price"] = price_cents
    else:
        data["no_price"] = price_cents
    
    result = kalshi_request("POST", "/portfolio/orders", data)
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
    else:
        order = result.get('order', {})
        print(f"✅ Order placed: {order.get('order_id')}")
        print(f"   {ticker} {side.upper()} x{count} @ {price_cents}c")
        print(f"   Status: {order.get('status')}")

def cmd_orders():
    result = kalshi_request("GET", "/portfolio/orders")
    print("=== OPEN ORDERS ===")
    for o in result.get('orders', []):
        if o.get('status') == 'resting':
            print(f"{o.get('ticker')}: {o.get('side')} x{o.get('remaining_count')} @ {o.get('yes_price') or o.get('no_price')}c")

def cmd_cancel(order_id):
    result = kalshi_request("DELETE", f"/portfolio/orders/{order_id}")
    print(f"Cancelled: {result}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kalshi CLI - Commands:")
        print("  balance              - Show account balance")
        print("  positions            - Show active positions")
        print("  orders               - Show open orders")
        print("  market <ticker>      - Get market details")
        print("  order <ticker> <yes|no> <count> <price_cents>")
        print("  cancel <order_id>    - Cancel an order")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "balance":
        cmd_balance()
    elif cmd == "positions":
        cmd_positions()
    elif cmd == "orders":
        cmd_orders()
    elif cmd == "market" and len(sys.argv) > 2:
        cmd_market(sys.argv[2])
    elif cmd == "order" and len(sys.argv) > 5:
        cmd_order(sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))
    elif cmd == "cancel" and len(sys.argv) > 2:
        cmd_cancel(sys.argv[2])
    else:
        print(f"Unknown command or missing args: {cmd}")
