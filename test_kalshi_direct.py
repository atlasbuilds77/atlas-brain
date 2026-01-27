#!/usr/bin/env python3
import os
import sys
import time
import hashlib
import base64
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

# Read private key
PRIVATE_KEY_PATH = os.path.expanduser("~/.kalshi/private_key.pem")
API_KEY_ID = os.environ.get("KALSHI_API_KEY_ID")

if not API_KEY_ID:
    print("ERROR: KALSHI_API_KEY_ID not set")
    sys.exit(1)

with open(PRIVATE_KEY_PATH, "r") as f:
    private_key_pem = f.read()

# Load private key
private_key = serialization.load_pem_private_key(
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
    """Make authenticated request to Kalshi API"""
    base_url = "https://api.elections.kalshi.com/trade-api/v2"
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
    signature = sign_message(message_to_sign, private_key)
    
    # Make request
    headers = {
        "KALSHI-ACCESS-KEY": API_KEY_ID,
        "KALSHI-ACCESS-SIGNATURE": signature,
        "KALSHI-ACCESS-TIMESTAMP": timestamp,
    }
    
    response = requests.request(method, url, headers=headers)
    return response

# Test 1: Get balance
print("Testing balance endpoint...")
response = make_kalshi_request("GET", "/portfolio/balance")
print(f"Balance status: {response.status_code}")
if response.status_code == 200:
    print(f"Balance response: {response.json()}")

# Test 2: Get positions with default parameters
print("\nTesting positions endpoint with default parameters...")
response = make_kalshi_request("GET", "/portfolio/positions")
print(f"Positions status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Positions response: {data}")
    print(f"Positions list: {data.get('positions')}")
    print(f"Cursor: {data.get('cursor')}")

# Test 3: Get positions with count_filter parameter (from OpenAPI docs)
print("\nTesting positions endpoint with count_filter='position'...")
response = make_kalshi_request("GET", "/portfolio/positions", {"count_filter": "position"})
print(f"Positions with count_filter status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Positions response: {data}")
    print(f"Positions list: {data.get('positions')}")
    print(f"Cursor: {data.get('cursor')}")

# Test 4: Get positions with count_filter='position,total_traded'
print("\nTesting positions endpoint with count_filter='position,total_traded'...")
response = make_kalshi_request("GET", "/portfolio/positions", {"count_filter": "position,total_traded"})
print(f"Positions with count_filter='position,total_traded' status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Positions response: {data}")
    print(f"Positions list: {data.get('positions')}")
    print(f"Cursor: {data.get('cursor')}")

# Test 5: Get fills (should work)
print("\nTesting fills endpoint...")
response = make_kalshi_request("GET", "/portfolio/fills")
print(f"Fills status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Number of fills: {len(data.get('fills', []))}")
    if data.get('fills'):
        print(f"First fill ticker: {data['fills'][0].get('ticker')}")