#!/usr/bin/env python3
"""
Kalshi Position Checker - Fixed with API Key Auth
Check all open positions and their current status
"""
import os
import sys
from kalshi_python import Configuration, KalshiClient
from collections import defaultdict

# Credentials
API_KEY_ID = "0007b9f0-89c9-42b4-93bd-f98fbf1596b8"
PRIVATE_KEY_PATH = "/Users/atlasbuilds/.clawdbot/credentials/kalshi/private_key.pem"
API_HOST = "https://api.elections.kalshi.com/trade-api/v2"

def get_client():
    """Initialize Kalshi API client"""
    if not os.path.exists(PRIVATE_KEY_PATH):
        print(f"❌ Private key not found at {PRIVATE_KEY_PATH}")
        sys.exit(1)
    
    with open(PRIVATE_KEY_PATH, "r") as f:
        private_key = f.read()
    
    config = Configuration(host=API_HOST)
    config.api_key_id = API_KEY_ID
    config.private_key_pem = private_key
    
    return KalshiClient(config)

def get_positions_from_fills(client):
    """Calculate positions from fills since get_positions() may be broken"""
    fills_resp = client.get_fills(limit=100)
    
    positions = defaultdict(lambda: {'count': 0, 'side': None, 'fills': []})
    
    if hasattr(fills_resp, 'fills') and fills_resp.fills:
        for fill in fills_resp.fills:
            ticker = fill.ticker if hasattr(fill, 'ticker') else None
            side = fill.side if hasattr(fill, 'side') else None
            count = fill.count if hasattr(fill, 'count') else 0
            
            if not ticker or not side:
                continue
            
            positions[ticker]['fills'].append({
                'side': side,
                'count': count,
                'created': fill.created_time if hasattr(fill, 'created_time') else None
            })
            
            # Calculate net position
            if side.lower() == 'yes':
                positions[ticker]['count'] += count
            elif side.lower() == 'no':
                positions[ticker]['count'] -= count
    
    return {k: v for k, v in positions.items() if v['count'] != 0}

def main():
    print("=" * 70)
    print("KALSHI POSITION CHECKER")
    print("=" * 70)
    
    try:
        client = get_client()
        print("\n✅ Connected to Kalshi API")
        
        # Get balance first
        balance_resp = client.get_balance()
        balance = balance_resp.balance if hasattr(balance_resp, 'balance') else 0
        print(f"💰 Cash Balance: ${balance / 100:.2f}\n")
        
        # Try to get positions directly first
        try:
            portfolio_resp = client.get_portfolio()
            print("✅ Portfolio API accessible\n")
            positions_data = portfolio_resp
        except Exception as e:
            print(f"⚠️  Portfolio API error, using fills method: {e}\n")
            positions_data = None
        
        # Calculate from fills
        active_positions = get_positions_from_fills(client)
        
        print(f"📊 ACTIVE POSITIONS ({len(active_positions)}):\n")
        
        if not active_positions:
            print("   No active positions")
            print("\n" + "=" * 70)
            return
        
        total_position_value = 0
        
        for ticker, pos_data in sorted(active_positions.items()):
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
                    yes_ask = market.yes_ask if hasattr(market, 'yes_ask') else 0
                    no_bid = market.no_bid if hasattr(market, 'no_bid') else 0
                    no_ask = market.no_ask if hasattr(market, 'no_ask') else 0
                    close_time = market.close_time if hasattr(market, 'close_time') else 'Unknown'
                    
                    # Calculate current value (use bid for exit price)
                    current_price = yes_bid if side == 'YES' else no_bid
                    current_value = abs_count * current_price / 100
                    max_payout = abs_count  # Max payout is $1 per contract
                    
                    total_position_value += current_value
                    
                    print(f"📈 {ticker}")
                    print(f"   Market: {title}")
                    print(f"   Position: {side} × {abs_count} contracts")
                    print(f"   Current Bid: {current_price}¢ (exit price)")
                    print(f"   Current Value: ${current_value:.2f}")
                    print(f"   Max Payout: ${max_payout:.2f} (if wins)")
                    print(f"   Status: {status}")
                    print(f"   Closes: {close_time}")
                    
                    if status.lower() == 'active':
                        print(f"   Spread: YES {yes_bid}¢/{yes_ask}¢  NO {no_bid}¢/{no_ask}¢")
                    
                    print()
                    
            except Exception as e:
                print(f"❌ {ticker}: {side} {abs_count} contracts (error: {e})")
                print()
        
        print("-" * 70)
        print(f"💵 CASH BALANCE:         ${balance / 100:>10.2f}")
        print(f"📊 POSITION VALUE:       ${total_position_value:>10.2f}")
        print(f"💎 TOTAL ACCOUNT VALUE:  ${total_position_value + balance / 100:>10.2f}")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
