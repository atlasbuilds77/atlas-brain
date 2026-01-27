#!/usr/bin/env python3
import os
import sys
from kalshi_python import Configuration, KalshiClient

# Set up environment
os.environ['KALSHI_API_KEY_ID'] = 'your-key-id-here'  # Need to get this from user
PRIVATE_KEY_PATH = os.path.expanduser("~/.kalshi/private_key.pem")

def test_api():
    # Read private key
    with open(PRIVATE_KEY_PATH, "r") as f:
        private_key = f.read()
    
    # Configuration
    host = "https://api.elections.kalshi.com/trade-api/v2"
    config = Configuration(host=host)
    config.api_key_id = os.environ.get('KALSHI_API_KEY_ID')
    config.private_key_pem = private_key
    
    # Create client
    client = KalshiClient(config)
    
    print("Testing Kalshi API...")
    
    # Test 1: Get balance
    try:
        balance = client.get_balance()
        print(f"Balance: ${balance.balance / 100:.2f}")
        print(f"Available: ${balance.available_balance / 100:.2f}")
    except Exception as e:
        print(f"Error getting balance: {e}")
    
    # Test 2: Get positions
    try:
        positions = client.get_positions()
        print(f"\nPositions response type: {type(positions)}")
        print(f"Positions: {positions.positions}")
        print(f"Cursor: {positions.cursor}")
        
        # Check if positions is None or empty list
        if positions.positions is None:
            print("WARNING: positions.positions is None")
        elif isinstance(positions.positions, list):
            print(f"Number of positions: {len(positions.positions)}")
            for i, pos in enumerate(positions.positions):
                print(f"Position {i}: {pos}")
        else:
            print(f"positions.positions is type: {type(positions.positions)}")
    except Exception as e:
        print(f"Error getting positions: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Get fills (should work according to user)
    try:
        fills = client.get_fills()
        print(f"\nFills response type: {type(fills)}")
        print(f"Number of fills: {len(fills.fills) if fills.fills else 0}")
        if fills.fills and len(fills.fills) > 0:
            print("First fill:", fills.fills[0])
    except Exception as e:
        print(f"Error getting fills: {e}")

if __name__ == "__main__":
    test_api()