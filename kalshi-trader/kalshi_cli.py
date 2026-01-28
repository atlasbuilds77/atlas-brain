#!/usr/bin/env python3
"""
Kalshi Trader CLI - Full Trading Capability
Place orders, check positions, manage trades
"""
import os
import sys
import argparse
import json
import urllib.request
import urllib.error
from kalshi_python import Configuration, KalshiClient
from kalshi_python.api.portfolio_api import PortfolioApi
from collections import defaultdict
from datetime import datetime

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

def get_market_raw(ticker):
    """Get market info using raw API (no auth needed for public market data)"""
    try:
        url = f"{API_HOST}/markets/{ticker}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                return data.get('market', {})
    except Exception:
        pass
    return None

def get_positions_raw(client):
    """
    Get positions using raw API response to work around SDK bug.
    The SDK expects 'positions' in response, but API returns 
    'market_positions' and 'event_positions'.
    
    Returns: list of market_position dicts with active positions
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
    
    # Filter to only positions with count > 0
    active = []
    for pos in market_positions:
        if pos.get('position', 0) > 0:
            active.append(pos)
    
    return active


def get_positions_from_fills(client):
    """Legacy: Calculate positions from fills (backup method)"""
    fills_resp = client.get_fills(limit=200)
    positions = defaultdict(lambda: {'count': 0, 'fills': []})
    
    if hasattr(fills_resp, 'fills') and fills_resp.fills:
        for fill in fills_resp.fills:
            ticker = fill.ticker if hasattr(fill, 'ticker') else None
            side = fill.side if hasattr(fill, 'side') else None
            count = fill.count if hasattr(fill, 'count') else 0
            
            if not ticker or not side:
                continue
            
            if side.lower() == 'yes':
                positions[ticker]['count'] += count
            elif side.lower() == 'no':
                positions[ticker]['count'] -= count
    
    return {k: v for k, v in positions.items() if v['count'] != 0}

def cmd_balance(client):
    """Show account balance"""
    balance_resp = client.get_balance()
    balance = balance_resp.balance if hasattr(balance_resp, 'balance') else 0
    print(f"💰 Cash Balance: ${balance / 100:.2f}")
    return balance

def cmd_positions(client):
    """Show all positions (using fixed raw API parsing)"""
    print("=" * 70)
    print("KALSHI POSITIONS (FIXED)")
    print("=" * 70)
    
    balance = cmd_balance(client)
    print()
    
    # Use fixed raw API parsing
    active_positions = get_positions_raw(client)
    
    if not active_positions:
        print("📊 No active positions")
        return
    
    total_value = 0
    total_exposure = 0
    
    for pos in sorted(active_positions, key=lambda x: x.get('ticker', '')):
        ticker = pos.get('ticker', 'Unknown')
        position_count = pos.get('position', 0)
        exposure = pos.get('market_exposure', 0) / 100  # cents to dollars
        
        total_exposure += exposure
        
        market = get_market_raw(ticker)
        if market:
            status = market.get('status', 'unknown')
            title = market.get('title', ticker)
            result = market.get('result')
            yes_bid = market.get('yes_bid', 0)
            yes_ask = market.get('yes_ask', 0)
            
            current_value = position_count * yes_bid / 100
            total_value += current_value
            
            emoji = '📈' if status == 'active' else ('✅' if result == 'yes' else '⏸️')
            
            print(f"{emoji} {ticker}")
            print(f"   {title}")
            print(f"   YES × {position_count} @ {yes_bid}¢/{yes_ask}¢ = ${current_value:.2f}")
            print(f"   Cost Basis: ${exposure:.2f}")
            print(f"   Status: {status}" + (f" Result: {result}" if result else ""))
            print()
        else:
            print(f"📈 {ticker}")
            print(f"   YES × {position_count} contracts")
            print(f"   Cost: ${exposure:.2f}")
            print()
    
    print("-" * 70)
    print(f"Market Value (at bid):  ${total_value:.2f}")
    print(f"Cost Basis:             ${total_exposure:.2f}")
    print(f"Cash Balance:           ${balance / 100:.2f}")
    print(f"Total Portfolio:        ${total_value + balance / 100:.2f}")

def cmd_market(client, ticker):
    """Show market details"""
    market = get_market_raw(ticker)
    if not market:
        print(f"❌ Market {ticker} not found")
        return
    
    print(f"📊 {ticker}")
    print(f"   Title: {market.get('title')}")
    print(f"   Status: {market.get('status')}")
    print(f"   YES: {market.get('yes_bid')}¢ / {market.get('yes_ask')}¢")
    print(f"   NO: {market.get('no_bid')}¢ / {market.get('no_ask')}¢")
    print(f"   Close: {market.get('close_time')}")
    if market.get('result'):
        print(f"   Result: {market.get('result')}")

def cmd_buy(client, ticker, side, count, price):
    """Place a buy order"""
    print(f"🛒 Placing order: BUY {count} {side} @ {price}¢ on {ticker}")
    
    # First check market
    market = get_market_raw(ticker)
    if not market:
        print(f"❌ Market {ticker} not found")
        return
    
    if market.get('status') != 'active':
        print(f"❌ Market is not active (status: {market.get('status')})")
        return
    
    # Check balance
    balance_resp = client.get_balance()
    balance = balance_resp.balance if hasattr(balance_resp, 'balance') else 0
    cost = count * price  # in cents
    
    if balance < cost:
        print(f"❌ Insufficient balance: ${balance/100:.2f} < ${cost/100:.2f} needed")
        return
    
    # Calculate fee: 0.07 * P * (1-P) per contract
    fee_per_contract = 0.07 * (price/100) * (1 - price/100)
    total_fee = fee_per_contract * count
    
    print(f"   Cost: ${cost/100:.2f}")
    print(f"   Fee: ${total_fee:.2f}")
    print(f"   Total: ${cost/100 + total_fee:.2f}")
    
    try:
        # Place order using SDK
        order_resp = client.create_order(
            ticker=ticker,
            side=side.lower(),
            action='buy',
            type='limit',
            count=count,
            yes_price=price if side.upper() == 'YES' else None,
            no_price=price if side.upper() == 'NO' else None
        )
        
        if hasattr(order_resp, 'order'):
            order = order_resp.order
            print(f"✅ Order placed!")
            print(f"   Order ID: {order.order_id if hasattr(order, 'order_id') else 'N/A'}")
            print(f"   Status: {order.status if hasattr(order, 'status') else 'N/A'}")
        else:
            print(f"✅ Order response: {order_resp}")
            
    except Exception as e:
        print(f"❌ Order failed: {e}")

def cmd_sell(client, ticker, side, count, price):
    """Place a sell order (close position)"""
    print(f"💰 Placing order: SELL {count} {side} @ {price}¢ on {ticker}")
    
    try:
        order_resp = client.create_order(
            ticker=ticker,
            side=side.lower(),
            action='sell',
            type='limit',
            count=count,
            yes_price=price if side.upper() == 'YES' else None,
            no_price=price if side.upper() == 'NO' else None
        )
        
        if hasattr(order_resp, 'order'):
            order = order_resp.order
            print(f"✅ Order placed!")
            print(f"   Order ID: {order.order_id if hasattr(order, 'order_id') else 'N/A'}")
        else:
            print(f"✅ Order response: {order_resp}")
            
    except Exception as e:
        print(f"❌ Order failed: {e}")

def cmd_orders(client):
    """Show open orders"""
    try:
        orders_resp = client.get_orders()
        orders = orders_resp.orders if hasattr(orders_resp, 'orders') else []
        
        if not orders:
            print("📋 No open orders")
            return
        
        print(f"📋 Open Orders ({len(orders)}):")
        for order in orders:
            print(f"   {order.ticker}: {order.side} {order.remaining_count}/{order.count} @ {order.yes_price or order.no_price}¢")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def cmd_search(client, query):
    """Search for markets"""
    try:
        markets_resp = client.get_markets(status='active', limit=10)
        markets = markets_resp.markets if hasattr(markets_resp, 'markets') else []
        
        # Filter by query
        matches = [m for m in markets if query.lower() in m.title.lower() or query.lower() in m.ticker.lower()]
        
        if not matches:
            print(f"No markets matching '{query}'")
            return
        
        print(f"🔍 Markets matching '{query}':")
        for m in matches[:10]:
            print(f"   {m.ticker}")
            print(f"      {m.title}")
            print(f"      YES: {m.yes_bid}¢/{m.yes_ask}¢  NO: {m.no_bid}¢/{m.no_ask}¢")
            print()
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    parser = argparse.ArgumentParser(description='Kalshi Trading CLI')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Balance command
    subparsers.add_parser('balance', help='Show account balance')
    
    # Positions command
    subparsers.add_parser('positions', help='Show all positions')
    
    # Market command
    market_parser = subparsers.add_parser('market', help='Show market details')
    market_parser.add_argument('ticker', help='Market ticker')
    
    # Buy command
    buy_parser = subparsers.add_parser('buy', help='Place buy order')
    buy_parser.add_argument('ticker', help='Market ticker')
    buy_parser.add_argument('side', choices=['yes', 'no', 'YES', 'NO'], help='Side (YES or NO)')
    buy_parser.add_argument('count', type=int, help='Number of contracts')
    buy_parser.add_argument('price', type=int, help='Price in cents (1-99)')
    
    # Sell command
    sell_parser = subparsers.add_parser('sell', help='Place sell order')
    sell_parser.add_argument('ticker', help='Market ticker')
    sell_parser.add_argument('side', choices=['yes', 'no', 'YES', 'NO'], help='Side (YES or NO)')
    sell_parser.add_argument('count', type=int, help='Number of contracts')
    sell_parser.add_argument('price', type=int, help='Price in cents (1-99)')
    
    # Orders command
    subparsers.add_parser('orders', help='Show open orders')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search markets')
    search_parser.add_argument('query', help='Search query')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    client = get_client()
    
    if args.command == 'balance':
        cmd_balance(client)
    elif args.command == 'positions':
        cmd_positions(client)
    elif args.command == 'market':
        cmd_market(client, args.ticker)
    elif args.command == 'buy':
        cmd_buy(client, args.ticker, args.side.upper(), args.count, args.price)
    elif args.command == 'sell':
        cmd_sell(client, args.ticker, args.side.upper(), args.count, args.price)
    elif args.command == 'orders':
        cmd_orders(client)
    elif args.command == 'search':
        cmd_search(client, args.query)

if __name__ == "__main__":
    main()
