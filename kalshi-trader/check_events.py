#!/usr/bin/env python3
"""
Check Kalshi event positions and portfolio value
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
    print("KALSHI EVENT POSITIONS CHECKER")
    print("=" * 60)
    
    try:
        client = get_client()
        
        # Get recent fills to see what we traded
        print(f"\n📜 RECENT TRADES:")
        fills_resp = client.get_fills(limit=20)
        
        # Track unique tickers
        tickers = set()
        
        if hasattr(fills_resp, 'fills') and fills_resp.fills:
            for fill in fills_resp.fills:
                ticker = fill.ticker if hasattr(fill, 'ticker') else None
                if ticker:
                    tickers.add(ticker)
                    side = fill.side if hasattr(fill, 'side') else 'N/A'
                    count = fill.count if hasattr(fill, 'count') else 0
                    yes_price = fill.yes_price if hasattr(fill, 'yes_price') else 0
                    no_price = fill.no_price if hasattr(fill, 'no_price') else 0
                    created = fill.created_time if hasattr(fill, 'created_time') else 'N/A'
                    
                    print(f"   {ticker}: {side.upper()} {count} @ {yes_price or no_price}¢ ({created})")
        
        # Now check each ticker for current market status
        print(f"\n🎯 MARKET STATUS FOR TRADED TICKERS:")
        for ticker in tickers:
            try:
                market_resp = client.get_market(ticker=ticker)
                if hasattr(market_resp, 'market'):
                    market = market_resp.market
                    title = market.title if hasattr(market, 'title') else ticker
                    status = market.status if hasattr(market, 'status') else 'unknown'
                    yes_bid = market.yes_bid if hasattr(market, 'yes_bid') else 0
                    no_bid = market.no_bid if hasattr(market, 'no_bid') else 0
                    close_time = market.close_time if hasattr(market, 'close_time') else 'N/A'
                    result = market.result if hasattr(market, 'result') else 'pending'
                    
                    print(f"\n   {ticker}:")
                    print(f"     Title: {title}")
                    print(f"     Status: {status}")
                    print(f"     Result: {result}")
                    print(f"     YES bid: {yes_bid}¢  NO bid: {no_bid}¢")
                    print(f"     Closes: {close_time}")
            except Exception as e:
                print(f"   {ticker}: Error - {e}")
        
        # Balance
        balance_resp = client.get_balance()
        print(f"\n💰 Current Balance: ${balance_resp.balance / 100:.2f}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
