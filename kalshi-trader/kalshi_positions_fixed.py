#!/usr/bin/env python3
"""
Kalshi Positions - FIXED VERSION
The kalshi-python SDK has a bug: it expects 'positions' in response,
but API returns 'market_positions' and 'event_positions'.

This script properly parses the raw API response.
"""
import os
import sys
import json
from kalshi_python import Configuration, KalshiClient
from kalshi_python.api.portfolio_api import PortfolioApi

# Credentials
API_KEY_ID = "0007b9f0-89c9-42b4-93bd-f98fbf1596b8"
PRIVATE_KEY_PATH = os.path.expanduser("~/.kalshi/private_key.pem")
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


def get_positions_raw(client):
    """
    Get positions using raw API response to work around SDK bug.
    Returns (market_positions, event_positions) as parsed dicts.
    """
    portfolio_api = PortfolioApi(client.api_client)
    
    # Get response with HTTP info to access raw_data
    response = portfolio_api.get_positions_with_http_info()
    
    # Parse the raw JSON response
    raw_data = response.raw_data
    if isinstance(raw_data, bytes):
        raw_data = raw_data.decode('utf-8')
    
    data = json.loads(raw_data)
    
    market_positions = data.get('market_positions', [])
    event_positions = data.get('event_positions', [])
    
    return market_positions, event_positions


def get_balance(client):
    """Get account balance"""
    balance_resp = client.get_balance()
    return balance_resp.balance / 100  # Convert cents to dollars


def get_market_info(client, ticker):
    """Get market info (current prices, status, etc)"""
    try:
        market_resp = client.get_market(ticker)
        return market_resp.market if hasattr(market_resp, 'market') else market_resp
    except Exception:
        return None


def display_positions():
    """Display all positions with current values"""
    client = get_client()
    
    print("=" * 70)
    print("KALSHI PORTFOLIO - FIXED POSITIONS VIEW")
    print("=" * 70)
    
    # Get balance
    balance = get_balance(client)
    print(f"\n💰 Cash Balance: ${balance:.2f}")
    
    # Get positions using raw API
    market_positions, event_positions = get_positions_raw(client)
    
    # Display active positions
    print(f"\n📊 Active Positions ({len([p for p in market_positions if p.get('position', 0) > 0])}):")
    print("-" * 70)
    
    total_exposure = 0
    active_count = 0
    
    for pos in market_positions:
        position_count = pos.get('position', 0)
        if position_count <= 0:
            continue
        
        active_count += 1
        ticker = pos.get('ticker', 'Unknown')
        exposure = pos.get('market_exposure', 0) / 100  # cents to dollars
        exposure_str = pos.get('market_exposure_dollars', f"${exposure:.2f}")
        realized_pnl = pos.get('realized_pnl_dollars', '0.00')
        fees = pos.get('fees_paid_dollars', '0.00')
        
        total_exposure += exposure
        
        # Get current market price
        market = get_market_info(client, ticker)
        if market:
            yes_bid = market.yes_bid if hasattr(market, 'yes_bid') else 0
            yes_ask = market.yes_ask if hasattr(market, 'yes_ask') else 0
            status = market.status if hasattr(market, 'status') else 'unknown'
            title = market.title if hasattr(market, 'title') else ticker
            
            current_value = position_count * yes_bid / 100
            
            print(f"\n📈 {ticker}")
            print(f"   {title}")
            print(f"   Position: {position_count} YES contracts")
            print(f"   Cost Basis: ${exposure_str}")
            print(f"   Current Bid: {yes_bid}¢  (Ask: {yes_ask}¢)")
            print(f"   Market Value: ${current_value:.2f}")
            print(f"   Status: {status}")
            if float(realized_pnl) != 0:
                print(f"   Realized P&L: ${realized_pnl}")
        else:
            print(f"\n📈 {ticker}")
            print(f"   Position: {position_count} contracts")
            print(f"   Cost: ${exposure_str}")
    
    if active_count == 0:
        print("   No active positions")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Cash Balance:     ${balance:.2f}")
    print(f"Position Value:   ${total_exposure:.2f}")
    print(f"Total Portfolio:  ${balance + total_exposure:.2f}")
    
    # Event-level summary
    print(f"\n📊 Event Summary:")
    for event in event_positions:
        event_ticker = event.get('event_ticker', 'Unknown')
        exposure = event.get('event_exposure_dollars', '0.00')
        if float(exposure) > 0:
            print(f"   {event_ticker}: ${exposure}")
    
    return market_positions, event_positions


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--json':
            client = get_client()
            market_positions, event_positions = get_positions_raw(client)
            balance = get_balance(client)
            print(json.dumps({
                'balance': balance,
                'market_positions': market_positions,
                'event_positions': event_positions
            }, indent=2))
        elif sys.argv[1] == '--raw':
            client = get_client()
            market_positions, event_positions = get_positions_raw(client)
            print("Market Positions:")
            for p in market_positions:
                print(f"  {p}")
            print("\nEvent Positions:")
            for e in event_positions:
                print(f"  {e}")
        else:
            print(f"Usage: {sys.argv[0]} [--json|--raw]")
    else:
        display_positions()


if __name__ == "__main__":
    main()
