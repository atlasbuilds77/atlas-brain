#!/usr/bin/env python3
"""
Example usage of Order Block Detector
Demonstrates basic usage without requiring live API access
"""

import pandas as pd
from datetime import datetime, timedelta
from order_block_detector import OrderBlockDetector, format_output

def create_sample_data():
    """Create sample OHLCV data for demonstration"""
    # Simulated data showing order block formation
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1H')
    
    data = []
    base_price = 150.0
    
    for i, date in enumerate(dates):
        # Create some volatility
        if i < 30:
            # Bullish order block setup (consolidation then breakout)
            if i < 25:
                open_price = base_price + (i * 0.1)
                close_price = base_price + (i * 0.1) + 0.05
            elif i == 25:
                # Last bearish candle before breakout
                open_price = base_price + 2.5
                close_price = base_price + 2.3
            elif i == 26:
                # Breakout candle with high volume
                open_price = base_price + 2.3
                close_price = base_price + 3.5
            else:
                # Continuation
                open_price = base_price + 3.0 + ((i - 26) * 0.2)
                close_price = base_price + 3.2 + ((i - 26) * 0.2)
        
        elif i < 60:
            # Ranging
            open_price = base_price + 5 + ((i % 5) * 0.3)
            close_price = base_price + 5 + ((i % 5) * 0.3) + 0.1
        
        elif i < 70:
            # Bearish order block setup
            if i < 65:
                open_price = base_price + 6 - ((i - 60) * 0.1)
                close_price = base_price + 6 - ((i - 60) * 0.1) - 0.05
            elif i == 65:
                # Last bullish candle before breakdown
                open_price = base_price + 5.5
                close_price = base_price + 5.7
            elif i == 66:
                # Breakdown candle with high volume
                open_price = base_price + 5.7
                close_price = base_price + 4.5
            else:
                # Continuation
                open_price = base_price + 4.0 - ((i - 66) * 0.2)
                close_price = base_price + 3.8 - ((i - 66) * 0.2)
        
        else:
            # Recovery
            open_price = base_price + 3 + ((i - 70) * 0.1)
            close_price = base_price + 3.1 + ((i - 70) * 0.1)
        
        high_price = max(open_price, close_price) + 0.2
        low_price = min(open_price, close_price) - 0.15
        
        # Volume spikes on breakout candles
        if i == 26 or i == 66:
            volume = 1500000
        else:
            volume = 500000 + (i * 1000)
        
        data.append({
            'timestamp': date,
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': volume
        })
    
    return pd.DataFrame(data)


def main():
    print("=" * 80)
    print("ORDER BLOCK DETECTOR - Example Usage")
    print("=" * 80)
    print("\nThis example uses simulated data to demonstrate order block detection.")
    print("In production, you would fetch real data from Alpaca API.\n")
    
    # Create sample data
    print("1. Creating sample price data...")
    df = create_sample_data()
    print(f"   ✓ Generated {len(df)} candles of hourly data")
    
    # Initialize detector
    print("\n2. Initializing Order Block Detector...")
    detector = OrderBlockDetector(
        min_volume_ratio=1.5,
        min_price_move=2.0,
        lookback_candles=5
    )
    print("   ✓ Detector configured")
    
    # Detect order blocks
    print("\n3. Scanning for order blocks...")
    order_blocks = detector.detect_order_blocks(df)
    print(f"   ✓ Found {len(order_blocks)} order blocks")
    
    # Separate by type
    bullish_blocks = [ob for ob in order_blocks if ob.type == 'bullish']
    bearish_blocks = [ob for ob in order_blocks if ob.type == 'bearish']
    
    print(f"   - Bullish blocks: {len(bullish_blocks)}")
    print(f"   - Bearish blocks: {len(bearish_blocks)}")
    
    # Get current price
    current_price = df.iloc[-1]['close']
    
    # Filter relevant blocks (within 10% of current price)
    print("\n4. Filtering to nearby order blocks...")
    bullish_nearby = detector.filter_relevant_blocks(bullish_blocks, current_price, max_distance_pct=10.0)
    bearish_nearby = detector.filter_relevant_blocks(bearish_blocks, current_price, max_distance_pct=10.0)
    
    print(f"   ✓ {len(bullish_nearby)} bullish blocks near current price")
    print(f"   ✓ {len(bearish_nearby)} bearish blocks near current price")
    
    # Display results
    print("\n5. Results:")
    print(format_output(bullish_nearby, bearish_nearby, current_price))
    
    # Example: Check if safe to enter long
    print("\n6. Example Trade Safety Check:")
    print("-" * 80)
    
    def check_long_safety(entry_price, bearish_blocks):
        """Check if it's safe to enter long"""
        for block in bearish_blocks:
            if block.broken:
                continue
            
            # Inside block?
            if entry_price >= block.start_price and entry_price <= block.end_price:
                return False, f"DANGER: Inside bearish block ${block.start_price:.2f}-${block.end_price:.2f} (strength {block.strength}/10)"
            
            # Too close to strong block?
            if entry_price < block.start_price:
                distance_pct = ((block.start_price - entry_price) / entry_price) * 100
                if distance_pct < 2 and block.strength >= 7:
                    return False, f"DANGER: Too close to strong resistance at ${block.start_price:.2f} ({distance_pct:.1f}% above)"
        
        return True, "No dangerous order blocks detected"
    
    test_price = current_price
    safe, reason = check_long_safety(test_price, bearish_nearby)
    
    if safe:
        print(f"✅ LONG ENTRY at ${test_price:.2f}: {reason}")
    else:
        print(f"❌ LONG ENTRY at ${test_price:.2f} REJECTED: {reason}")
    
    print("-" * 80)
    
    # Show what data would look like in JSON format
    print("\n7. JSON Output Example:")
    print("-" * 80)
    if bullish_nearby:
        import json
        example_block = bullish_nearby[0].to_dict()
        print(json.dumps(example_block, indent=2))
    
    print("\n" + "=" * 80)
    print("Example complete! See INTEGRATION_GUIDE.md for production usage.")
    print("=" * 80)


if __name__ == '__main__':
    main()
