#!/usr/bin/env python3
"""
Kalshi Position Checker - Quick Status
"""
import os
import sys
from kalshi_python import Configuration, KalshiClient

# API Configuration
API_KEY_ID = "0007b9f0-89c9-42b4-93bd-f98fbf1596b8"
PRIVATE_KEY_PATH = os.path.expanduser("~/.kalshi/private_key.pem")
API_HOST = "https://api.elections.kalshi.com/trade-api/v2"

def get_client():
    """Initialize Kalshi client"""
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
    print("KALSHI POSITION CHECKER")
    print("=" * 60)
    
    try:
        client = get_client()
        
        # Get balance
        balance_resp = client.get_balance()
        balance = balance_resp.balance if hasattr(balance_resp, 'balance') else 0
        print(f"\n💰 Balance: ${balance / 100:.2f}")
        
        # Get positions
        positions_resp = client.get_positions()
        positions = positions_resp.positions if hasattr(positions_resp, 'positions') else []
        
        if not positions:
            print("\n📊 No open positions\n")
            return
        
        print(f"\n📊 Open Positions ({len(positions)}):\n")
        
        total_value = 0
        
        for pos in positions:
            ticker = pos.ticker if hasattr(pos, 'ticker') else 'Unknown'
            position = pos.position if hasattr(pos, 'position') else 0
            
            if position == 0:
                continue
            
            # Get market info
            try:
                market_resp = client.get_market(ticker=ticker)
                market = market_resp.market if hasattr(market_resp, 'market') else market_resp
                market_title = market.title if hasattr(market, 'title') else ticker
                yes_price = market.yes_bid if hasattr(market, 'yes_bid') else 0
                close_time = market.close_time if hasattr(market, 'close_time') else 'Unknown'
                
                # Calculate value
                current_value = abs(position) * yes_price / 100
                total_value += current_value
                
                print(f"   {ticker}")
                print(f"   Market: {market_title}")
                print(f"   Position: {position} contracts ({'YES' if position > 0 else 'NO'})")
                print(f"   Current Price: {yes_price}¢")
                print(f"   Value: ${current_value:.2f}")
                print(f"   Closes: {close_time}")
                print()
                
            except Exception as e:
                print(f"   {ticker}: {position} contracts (error fetching details: {e})")
                print()
        
        print("-" * 60)
        print(f"TOTAL POSITION VALUE: ${total_value:.2f}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
