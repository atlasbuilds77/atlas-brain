#!/usr/bin/env python3
"""
Pre-Trade Safety Check
Run this before EVERY trade to check for order block conflicts
"""

import sys
import json
from datetime import datetime
from order_block_detector import OrderBlockDetector
import pandas as pd


def pre_trade_check(symbol: str, direction: str, entry_price: float, 
                    timeframe: str = '1Hour', days: int = 30) -> tuple:
    """
    Check if a trade is safe based on order block analysis
    
    Args:
        symbol: Trading symbol (e.g., 'AAPL')
        direction: 'long' or 'short'
        entry_price: Proposed entry price
        timeframe: Candlestick timeframe
        days: Days of historical data
    
    Returns:
        (approved: bool, warnings: list, blocks: dict)
    """
    import os
    
    # Get API credentials
    api_key = os.environ.get('ALPACA_API_KEY')
    api_secret = os.environ.get('ALPACA_API_SECRET')
    
    if not api_key or not api_secret:
        return False, ["ERROR: Alpaca API credentials not set"], {}
    
    try:
        from alpaca_trade_api import REST
        from datetime import timedelta
        
        # Fetch data
        alpaca = REST(api_key, api_secret, base_url='https://paper-api.alpaca.markets')
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        bars = alpaca.get_bars(
            symbol,
            timeframe,
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            feed='iex'
        ).df
        
        # Prepare dataframe
        df = pd.DataFrame({
            'timestamp': bars.index,
            'open': bars['open'],
            'high': bars['high'],
            'low': bars['low'],
            'close': bars['close'],
            'volume': bars['volume']
        })
        
    except Exception as e:
        return False, [f"ERROR fetching data: {str(e)}"], {}
    
    # Detect order blocks
    detector = OrderBlockDetector()
    all_blocks = detector.detect_order_blocks(df)
    
    # Filter to relevant blocks
    bullish_blocks = [ob for ob in all_blocks if ob.type == 'bullish' and not ob.broken]
    bearish_blocks = [ob for ob in all_blocks if ob.type == 'bearish' and not ob.broken]
    
    bullish_blocks = detector.filter_relevant_blocks(bullish_blocks, entry_price, max_distance_pct=10)
    bearish_blocks = detector.filter_relevant_blocks(bearish_blocks, entry_price, max_distance_pct=10)
    
    # Check for conflicts
    warnings = []
    approved = True
    
    if direction.lower() == 'long':
        # Check bearish blocks (resistance)
        for block in bearish_blocks:
            # Inside the block?
            if entry_price >= block.start_price and entry_price <= block.end_price:
                warnings.append(
                    f"🚨 CRITICAL: Entry ${entry_price:.2f} is INSIDE bearish order block "
                    f"${block.start_price:.2f}-${block.end_price:.2f} (strength {block.strength}/10)"
                )
                approved = False
            
            # Just below strong resistance?
            elif entry_price < block.start_price:
                distance_pct = ((block.start_price - entry_price) / entry_price) * 100
                if distance_pct < 2 and block.strength >= 7:
                    warnings.append(
                        f"⚠️  WARNING: Strong resistance {distance_pct:.1f}% above at "
                        f"${block.start_price:.2f}-${block.end_price:.2f} (strength {block.strength}/10)"
                    )
                    # Don't reject, but warn
                elif distance_pct < 5 and block.strength >= 8:
                    warnings.append(
                        f"⚠️  WARNING: Very strong resistance {distance_pct:.1f}% above at "
                        f"${block.start_price:.2f}-${block.end_price:.2f} (strength {block.strength}/10)"
                    )
        
        # Check bullish blocks (support)
        support_found = False
        for block in bullish_blocks:
            if entry_price >= block.start_price and entry_price <= block.end_price + (block.end_price * 0.02):
                warnings.append(
                    f"✅ SUPPORT: Bullish order block nearby at "
                    f"${block.start_price:.2f}-${block.end_price:.2f} (strength {block.strength}/10)"
                )
                support_found = True
        
        if not support_found and not warnings:
            warnings.append("ℹ️  INFO: No significant support or resistance detected nearby")
    
    elif direction.lower() == 'short':
        # Check bullish blocks (support)
        for block in bullish_blocks:
            # Inside the block?
            if entry_price >= block.start_price and entry_price <= block.end_price:
                warnings.append(
                    f"🚨 CRITICAL: Entry ${entry_price:.2f} is INSIDE bullish order block "
                    f"${block.start_price:.2f}-${block.end_price:.2f} (strength {block.strength}/10)"
                )
                approved = False
            
            # Just above strong support?
            elif entry_price > block.end_price:
                distance_pct = ((entry_price - block.end_price) / entry_price) * 100
                if distance_pct < 2 and block.strength >= 7:
                    warnings.append(
                        f"⚠️  WARNING: Strong support {distance_pct:.1f}% below at "
                        f"${block.start_price:.2f}-${block.end_price:.2f} (strength {block.strength}/10)"
                    )
                elif distance_pct < 5 and block.strength >= 8:
                    warnings.append(
                        f"⚠️  WARNING: Very strong support {distance_pct:.1f}% below at "
                        f"${block.start_price:.2f}-${block.end_price:.2f} (strength {block.strength}/10)"
                    )
        
        # Check bearish blocks (resistance)
        resistance_found = False
        for block in bearish_blocks:
            if entry_price <= block.end_price and entry_price >= block.start_price - (block.start_price * 0.02):
                warnings.append(
                    f"✅ RESISTANCE: Bearish order block nearby at "
                    f"${block.start_price:.2f}-${block.end_price:.2f} (strength {block.strength}/10)"
                )
                resistance_found = True
        
        if not resistance_found and not warnings:
            warnings.append("ℹ️  INFO: No significant support or resistance detected nearby")
    
    # Package results
    blocks_data = {
        'bullish_blocks': [ob.to_dict() for ob in bullish_blocks],
        'bearish_blocks': [ob.to_dict() for ob in bearish_blocks]
    }
    
    return approved, warnings, blocks_data


def main():
    """CLI interface for pre-trade check"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Pre-trade safety check')
    parser.add_argument('--symbol', type=str, required=True, help='Trading symbol')
    parser.add_argument('--direction', type=str, required=True, choices=['long', 'short'],
                       help='Trade direction')
    parser.add_argument('--entry', type=float, required=True, help='Entry price')
    parser.add_argument('--timeframe', type=str, default='1Hour', help='Timeframe')
    parser.add_argument('--days', type=int, default=30, help='Days of history')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("PRE-TRADE SAFETY CHECK")
    print("=" * 80)
    print(f"Symbol: {args.symbol}")
    print(f"Direction: {args.direction.upper()}")
    print(f"Entry Price: ${args.entry:.2f}")
    print(f"Timeframe: {args.timeframe}")
    print("=" * 80)
    print("\nAnalyzing order blocks...")
    
    approved, warnings, blocks = pre_trade_check(
        args.symbol,
        args.direction,
        args.entry,
        args.timeframe,
        args.days
    )
    
    if args.json:
        # JSON output
        result = {
            'symbol': args.symbol,
            'direction': args.direction,
            'entry_price': args.entry,
            'approved': approved,
            'warnings': warnings,
            'blocks': blocks,
            'timestamp': datetime.now().isoformat()
        }
        print(json.dumps(result, indent=2))
    else:
        # Human-readable output
        print("\n" + "=" * 80)
        print("RESULTS")
        print("=" * 80)
        
        if approved:
            print("\n✅ TRADE APPROVED")
        else:
            print("\n❌ TRADE REJECTED")
        
        print("\nAnalysis:")
        for warning in warnings:
            print(f"  {warning}")
        
        print("\n" + "=" * 80)
        
        if approved:
            print("Trade is clear to proceed. Monitor order blocks during execution.")
        else:
            print("DO NOT ENTER THIS TRADE. Price is in conflict with order blocks.")
        
        print("=" * 80)
    
    # Exit with appropriate code
    sys.exit(0 if approved else 1)


if __name__ == '__main__':
    main()
