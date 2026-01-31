#!/usr/bin/env python3
"""
Quick Test - Order Block Detector on SPY (Last 2 Weeks)
Simple validation script - no comprehensive backtest
"""

import os
import sys
from datetime import datetime, timedelta

try:
    from order_block_detector import OrderBlockDetector
except ImportError:
    print("ERROR: order_block_detector.py not found")
    sys.exit(1)

def main():
    print("\n" + "="*60)
    print("QUICK TEST - Order Block Detector")
    print("="*60)
    print("Symbol: SPY")
    print("Period: Last 2 weeks")
    print("Timeframes: 5m, 15m, 1h")
    print("="*60 + "\n")
    
    # Check credentials
    if not os.getenv('ALPACA_API_KEY') or not os.getenv('ALPACA_API_SECRET'):
        print("❌ ERROR: Alpaca API credentials not found")
        print("\nSet them with:")
        print('  export ALPACA_API_KEY="your_key"')
        print('  export ALPACA_API_SECRET="your_secret"')
        sys.exit(1)
    
    # Initialize detector
    try:
        detector = OrderBlockDetector()
        print("✅ Detector initialized\n")
    except Exception as e:
        print(f"❌ Failed to initialize detector: {e}")
        sys.exit(1)
    
    # Test on each timeframe
    timeframes = ['5m', '15m', '1h']
    
    for tf in timeframes:
        print(f"\n{'='*60}")
        print(f"Testing: SPY on {tf}")
        print('='*60)
        
        try:
            result = detector.detect('SPY', timeframe=tf, asset_type='stock')
            
            # Print summary
            print(f"\nCurrent Price: ${result.get('current_price', 0):.2f}")
            print(f"Order Blocks Found: {len(result.get('order_blocks', []))}")
            print(f"\nSummary: {result.get('summary', 'N/A')}")
            
            # Print detected zones
            if result.get('order_blocks'):
                print(f"\n{'─'*60}")
                print("DETECTED ORDER BLOCKS:")
                print('─'*60)
                
                for i, ob in enumerate(result['order_blocks'], 1):
                    print(f"\n#{i} {ob['type'].upper()}")
                    print(f"  Zone: ${ob['zone_low']:.2f} - ${ob['zone_high']:.2f}")
                    print(f"  Strength: {ob['adjusted_strength']:.1f}/10")
                    print(f"  Age: {ob['age_candles']} candles")
                    print(f"  Volume: {ob['volume_ratio']:.1f}x")
                    print(f"  Impulse: {ob['impulse_pct']:.1f}%")
            else:
                print("\n  No order blocks detected")
            
            print()
            
        except Exception as e:
            print(f"❌ Error testing {tf}: {e}\n")
    
    print("\n" + "="*60)
    print("✅ QUICK TEST COMPLETE")
    print("="*60)
    print("\nNext: Manual test these zones on live charts")
    print()

if __name__ == '__main__':
    main()
