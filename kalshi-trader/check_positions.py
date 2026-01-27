#!/usr/bin/env python3
"""
Kalshi Position Checker
Check all open positions and their current status
"""
import os
import requests
from datetime import datetime

API_BASE = "https://api.elections.kalshi.com/trade-api/v2"

def get_auth_token():
    """Get auth token from environment or credentials"""
    email = os.getenv('KALSHI_EMAIL')
    password = os.getenv('KALSHI_PASSWORD')
    
    if not email or not password:
        raise Exception("Set KALSHI_EMAIL and KALSHI_PASSWORD environment variables")
    
    response = requests.post(
        f"{API_BASE}/login",
        json={"email": email, "password": password}
    )
    response.raise_for_status()
    return response.json()['token']

def get_positions(token):
    """Get all open positions"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get portfolio
    response = requests.get(
        f"{API_BASE}/portfolio/positions",
        headers=headers
    )
    response.raise_for_status()
    return response.json()

def get_market_info(token, ticker):
    """Get market details"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{API_BASE}/markets/{ticker}",
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json().get('market', {})
    return None

def main():
    print("=" * 60)
    print("KALSHI POSITION CHECKER")
    print("=" * 60)
    
    try:
        token = get_auth_token()
        print("\n✅ Authenticated\n")
        
        data = get_positions(token)
        positions = data.get('positions', [])
        
        if not positions:
            print("📊 No open positions")
            return
        
        print(f"📊 Found {len(positions)} position(s):\n")
        
        total_invested = 0
        total_value = 0
        
        for pos in positions:
            ticker = pos.get('ticker')
            position = pos.get('position', 0)
            
            if position == 0:
                continue
            
            market_info = get_market_info(token, ticker)
            
            # Get current price from market
            current_price = None
            if market_info:
                if position > 0:  # YES position
                    current_price = market_info.get('yes_ask', market_info.get('yes_bid'))
                else:  # NO position
                    current_price = market_info.get('no_ask', market_info.get('no_bid'))
            
            # Calculate values
            resting_orders_count = pos.get('resting_order_count', 0)
            total_cost = pos.get('total_cost', 0) / 100  # Convert cents to dollars
            fees_paid = pos.get('fees_paid', 0) / 100
            
            current_value = 0
            if current_price:
                current_value = abs(position) * current_price / 100
            
            pnl = current_value - total_cost if current_value > 0 else 0
            
            total_invested += total_cost
            total_value += current_value
            
            print(f"   Ticker: {ticker}")
            print(f"   Position: {position} contracts ({'YES' if position > 0 else 'NO'})")
            print(f"   Total Cost: ${total_cost:.2f}")
            print(f"   Fees Paid: ${fees_paid:.2f}")
            
            if current_price:
                print(f"   Current Price: {current_price}¢")
                print(f"   Current Value: ${current_value:.2f}")
                print(f"   P&L: ${pnl:+.2f}")
            
            if resting_orders_count > 0:
                print(f"   Resting Orders: {resting_orders_count}")
            
            if market_info:
                close_time = market_info.get('close_time')
                if close_time:
                    print(f"   Closes: {close_time}")
            
            print()
        
        print("-" * 60)
        print(f"TOTAL INVESTED: ${total_invested:.2f}")
        print(f"CURRENT VALUE: ${total_value:.2f}")
        print(f"TOTAL P&L: ${total_value - total_invested:+.2f}")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
