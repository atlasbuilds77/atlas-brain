#!/usr/bin/env python3
"""Quick Kalshi API client"""
import json
import time
import base64
import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"

def load_credentials():
    with open("/Users/atlasbuilds/.clawdbot/credentials/kalshi/config.json") as f:
        config = json.load(f)
    with open(config["privateKeyPath"], "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())
    return config["apiKeyId"], private_key

def get_auth_headers(method, path, api_key_id, private_key):
    timestamp = str(int(time.time() * 1000))
    msg = f"{timestamp}{method}{path}".encode()
    signature = private_key.sign(msg, padding.PKCS1v15(), hashes.SHA256())
    sig_b64 = base64.b64encode(signature).decode()
    return {
        "KALSHI-ACCESS-KEY": api_key_id,
        "KALSHI-ACCESS-SIGNATURE": sig_b64,
        "KALSHI-ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json"
    }

def api_get(path):
    api_key_id, private_key = load_credentials()
    headers = get_auth_headers("GET", path, api_key_id, private_key)
    resp = requests.get(BASE_URL + path, headers=headers)
    return resp.json()

def api_post(path, data):
    api_key_id, private_key = load_credentials()
    headers = get_auth_headers("POST", path, api_key_id, private_key)
    resp = requests.post(BASE_URL + path, headers=headers, json=data)
    return resp.json()

if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "balance"
    
    if cmd == "balance":
        result = api_get("/portfolio/balance")
        print(json.dumps(result, indent=2))
    elif cmd == "positions":
        result = api_get("/portfolio/positions")
        print(json.dumps(result, indent=2))
    elif cmd == "markets":
        # Get trending markets
        result = api_get("/markets?limit=20&status=open")
        print(json.dumps(result, indent=2))
    elif cmd == "order":
        # Usage: order <ticker> <side> <count> <price_cents>
        ticker = sys.argv[2]
        side = sys.argv[3]  # "yes" or "no"
        count = int(sys.argv[4])
        price = int(sys.argv[5])  # in cents
        order = {
            "ticker": ticker,
            "action": "buy",
            "side": side,
            "type": "limit",
            "count": count,
            "yes_price": price if side == "yes" else None,
            "no_price": price if side == "no" else None
        }
        result = api_post("/portfolio/orders", order)
        print(json.dumps(result, indent=2))
    else:
        print(f"Unknown command: {cmd}")
