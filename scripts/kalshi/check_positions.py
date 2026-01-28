#!/usr/bin/env python3
"""
Kalshi Position Checker
Uses kalshi-python SDK to check live positions and portfolio
"""

import os
import sys
from pathlib import Path
from kalshi_python import ApiInstance, Configuration

def get_kalshi_client():
    """Initialize Kalshi API client with credentials from environment or config"""
    # Check for API key in environment
    api_key = os.getenv('KALSHI_API_KEY')
    if not api_key:
        print("ERROR: KALSHI_API_KEY not set in environment", file=sys.stderr)
        print("Set it with: export KALSHI_API_KEY='your_key_here'", file=sys.stderr)
        sys.exit(1)
    
    # Check for private key file
    private_key_path = Path.home() / '.kalshi' / 'private_key.pem'
    if not private_key_path.exists():
        print(f"ERROR: Private key not found at {private_key_path}", file=sys.stderr)
        sys.exit(1)
    
    # Initialize client
    config = Configuration(
        host='https://trading-api.kalshi.com/trade-api/v2',
    )
    
    # Create API instance
    client = ApiInstance(
        email=os.getenv('KALSHI_EMAIL', ''),
        password=os.getenv('KALSHI_PASSWORD', ''),
        configuration=config
    )
    
    return client

def get_portfolio():
    """Get portfolio balance and positions"""
    client = get_kalshi_client()
    
    try:
        # Get balance
        balance = client.get_balance()
        print(f"\n💰 BALANCE: ${balance.balance / 100:.2f}")
        
        # Get positions
        positions = client.get_positions()
        
        if not positions.positions:
            print("\n📊 POSITIONS: None open")
            return
        
        print(f"\n📊 POSITIONS: {len(positions.positions)} open")
        print("-" * 80)
        
        for pos in positions.positions:
            market = client.get_market(pos.market_ticker)
            
            # Calculate P&L
            current_price = market.last_price if market.last_price else market.yes_bid
            cost_basis = pos.total_cost / 100
            current_value = (pos.position * current_price) / 100
            pnl = current_value - cost_basis
            pnl_pct = (pnl / cost_basis * 100) if cost_basis > 0 else 0
            
            # Status emoji
            status = "✅" if pnl > 0 else "❌" if pnl < 0 else "⚖️"
            
            print(f"\n{status} {market.ticker}")
            print(f"   Title: {market.title}")
            print(f"   Side: {'YES' if pos.position > 0 else 'NO'}")
            print(f"   Contracts: {abs(pos.position)}")
            print(f"   Entry: {pos.total_cost / pos.position:.0f}¢" if pos.position != 0 else "   Entry: N/A")
            print(f"   Current: {current_price}¢")
            print(f"   Cost Basis: ${cost_basis:.2f}")
            print(f"   Current Value: ${current_value:.2f}")
            print(f"   P&L: ${pnl:+.2f} ({pnl_pct:+.1f}%)")
            
            # Resolution info
            if market.close_time:
                print(f"   Closes: {market.close_time}")
            if market.result:
                print(f"   Result: {market.result}")
        
        print("\n" + "-" * 80)
        
        # Calculate total P&L
        total_pnl = sum([
            ((pos.position * (client.get_market(pos.market_ticker).last_price or 
                             client.get_market(pos.market_ticker).yes_bid)) / 100) - 
            (pos.total_cost / 100)
            for pos in positions.positions
        ])
        
        print(f"💵 TOTAL P&L: ${total_pnl:+.2f}")
        
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

def get_recent_trades(limit=10):
    """Get recent fills/trades"""
    client = get_kalshi_client()
    
    try:
        fills = client.get_fills(limit=limit)
        
        if not fills.fills:
            print("\n📝 RECENT TRADES: None")
            return
        
        print(f"\n📝 RECENT {len(fills.fills)} TRADES:")
        print("-" * 80)
        
        for fill in fills.fills:
            side = "BUY YES" if fill.side == "yes" else "SELL NO" if fill.side == "no" else fill.side
            print(f"{fill.created_time} | {fill.ticker} | {side} | {fill.count} @ {fill.yes_price}¢ = ${fill.count * fill.yes_price / 100:.2f}")
        
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Check Kalshi positions and portfolio")
    parser.add_argument('--trades', action='store_true', help='Show recent trades')
    parser.add_argument('--limit', type=int, default=10, help='Number of recent trades to show')
    
    args = parser.parse_args()
    
    get_portfolio()
    
    if args.trades:
        get_recent_trades(limit=args.limit)
