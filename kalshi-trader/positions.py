#!/usr/bin/env python3
"""
Kalshi Position Tracker - Manual tracking from fills
Since get_positions() is broken, we track from fills
"""
import os
import sys
from kalshi_python import Configuration, KalshiClient
from collections import defaultdict

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
    print("KALSHI POSITION TRACKER")
    print("=" * 60)
    
    try:
        client = get_client()
        
        # Get all fills
        fills_resp = client.get_fills(limit=100)
        
        # Track net position per ticker
        positions = defaultdict(lambda: {'count': 0, 'side': None, 'fills': []})
        
        if hasattr(fills_resp, 'fills') and fills_resp.fills:
            for fill in fills_resp.fills:
                ticker = fill.ticker if hasattr(fill, 'ticker') else None
                side = fill.side if hasattr(fill, 'side') else None
                count = fill.count if hasattr(fill, 'count') else 0
                
                if not ticker or not side:
                    continue
                
                # Track fills
                positions[ticker]['fills'].append({
                    'side': side,
                    'count': count,
                    'created': fill.created_time if hasattr(fill, 'created_time') else None
                })
                
                # Calculate net position
                if side.lower() == 'yes':
                    positions[ticker]['count'] += count
                    positions[ticker]['side'] = 'YES'
                elif side.lower() == 'no':
                    positions[ticker]['count'] -= count
                    positions[ticker]['side'] = 'NO'
        
        # Filter to non-zero positions
        active_positions = {k: v for k, v in positions.items() if v['count'] != 0}
        
        print(f"\n📊 ACTIVE POSITIONS ({len(active_positions)}):\n")
        
        if not active_positions:
            print("   No active positions")
            return
        
        total_value = 0
        
        for ticker, pos_data in active_positions.items():
            net_count = pos_data['count']
            side = 'YES' if net_count > 0 else 'NO'
            abs_count = abs(net_count)
            
            # Get current market data
            try:
                market_resp = client.get_market(ticker=ticker)
                if hasattr(market_resp, 'market'):
                    market = market_resp.market
                    title = market.title if hasattr(market, 'title') else ticker
                    status = market.status if hasattr(market, 'status') else 'unknown'
                    yes_bid = market.yes_bid if hasattr(market, 'yes_bid') else 0
                    no_bid = market.no_bid if hasattr(market, 'no_bid') else 0
                    close_time = market.close_time if hasattr(market, 'close_time') else 'Unknown'
                    
                    # Calculate current value
                    current_price = yes_bid if side == 'YES' else no_bid
                    current_value = abs_count * current_price / 100
                    total_value += current_value
                    
                    print(f"   {ticker}")
                    print(f"     Market: {title}")
                    print(f"     Position: {side} {abs_count} contracts")
                    print(f"     Current Price: {current_price}¢")
                    print(f"     Current Value: ${current_value:.2f}")
                    print(f"     Status: {status}")
                    print(f"     Closes: {close_time}")
                    print()
                    
            except Exception as e:
                print(f"   {ticker}: {side} {abs_count} contracts (error getting market: {e})")
                print()
        
        # Balance
        balance_resp = client.get_balance()
        balance = balance_resp.balance if hasattr(balance_resp, 'balance') else 0
        
        print("-" * 60)
        print(f"TOTAL POSITION VALUE: ${total_value:.2f}")
        print(f"CASH BALANCE: ${balance / 100:.2f}")
        print(f"TOTAL ACCOUNT VALUE: ${total_value + balance / 100:.2f}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
