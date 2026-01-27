#!/usr/bin/env python3
"""
Kalshi Detailed Position & Portfolio Checker
"""
import os
import sys
from kalshi_python import Configuration, KalshiClient

API_KEY_ID = "0007b9f0-89c9-42b4-93bd-f98fbf1596b8"
PRIVATE_KEY_PATH = os.path.expanduser("~/.kalshi/private_key.pem")
API_HOST = "https://api.elections.kalshi.com/trade-api/v2"

def get_client():
    if not os.path.exists(PRIVATE_KEY_PATH):
        print(f"❌ Private key not found at {PRIVATE_KEY_PATH}")
        sys.exit(1)
    
    with open(PRIVATE_KEY_PATH, "r") as f:
        private_key = f.read()
    
    config = Configuration(host=API_HOST)
    config.api_key_id = API_KEY_ID
    config.private_key_pem = private_key
    
    return KalshiClient(config)

def main():
    print("=" * 60)
    print("KALSHI DETAILED CHECKER")
    print("=" * 60)
    
    try:
        client = get_client()
        
        # Balance
        balance_resp = client.get_balance()
        print(f"\n💰 BALANCE:")
        print(f"   Balance: ${balance_resp.balance / 100:.2f}")
        
        # Positions
        print(f"\n📊 POSITIONS:")
        positions_resp = client.get_positions()
        
        print(f"   Raw response type: {type(positions_resp)}")
        print(f"   Has positions attr: {hasattr(positions_resp, 'positions')}")
        
        if hasattr(positions_resp, 'positions'):
            positions = positions_resp.positions
            print(f"   Positions value: {positions}")
            print(f"   Positions type: {type(positions)}")
            
            if positions is not None:
                print(f"   Positions count: {len(positions)}")
                for i, pos in enumerate(positions):
                    print(f"\n   Position {i+1}:")
                    print(f"     Ticker: {pos.ticker if hasattr(pos, 'ticker') else 'N/A'}")
                    print(f"     Position: {pos.position if hasattr(pos, 'position') else 'N/A'}")
                    print(f"     Type: {type(pos)}")
            else:
                print("   Positions is None")
        
        # Check all attributes of response
        print(f"\n   All response attributes:")
        for attr in dir(positions_resp):
            if not attr.startswith('_'):
                val = getattr(positions_resp, attr, None)
                if not callable(val):
                    print(f"     {attr}: {val}")
        
        # Try fills
        print(f"\n📜 RECENT FILLS:")
        try:
            fills_resp = client.get_fills(limit=10)
            if hasattr(fills_resp, 'fills'):
                fills = fills_resp.fills
                print(f"   Found {len(fills)} recent fills")
                for fill in fills[:5]:
                    print(f"   - {fill.ticker if hasattr(fill, 'ticker') else 'N/A'}: {fill.side if hasattr(fill, 'side') else 'N/A'} {fill.count if hasattr(fill, 'count') else 'N/A'} @ {fill.yes_price if hasattr(fill, 'yes_price') else 'N/A'}¢")
        except Exception as e:
            print(f"   Error getting fills: {e}")
        
        # Portfolio snapshot
        print(f"\n🎯 PORTFOLIO SNAPSHOT:")
        try:
            portfolio = client.get_portfolio()
            print(f"   Raw response: {portfolio}")
        except AttributeError:
            print("   get_portfolio() not available")
        except Exception as e:
            print(f"   Error: {e}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
