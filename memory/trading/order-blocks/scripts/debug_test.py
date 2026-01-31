#!/usr/bin/env python3
"""Debug why perfect OB isn't being detected"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from order_block_detector import OrderBlockDetector

def create_test_data_bullish_ob():
    """Create synthetic data with a perfect bullish order block"""
    dates = [datetime.now() - timedelta(hours=i) for i in range(40, 0, -1)]
    
    # Need 20+ candles for volume_ma calculation
    data = {
        'timestamp': dates[:25],
        'open': [100.0] * 25,
        'high': [100.5] * 25,
        'low': [99.5] * 25,
        'close': [100.0] * 25,
        'volume': [1000] * 25
    }
    
    # Order block candle (bearish at index 25)
    data['timestamp'].append(dates[25])
    data['open'].append(100.0)
    data['high'].append(100.2)
    data['low'].append(99.0)
    data['close'].append(99.2)
    data['volume'].append(2000)
    
    # Engulfing bullish candle (index 26)
    data['timestamp'].append(dates[26])
    data['open'].append(99.2)
    data['high'].append(101.0)
    data['low'].append(98.5)
    data['close'].append(100.8)
    data['volume'].append(3000)
    
    # Clean impulse up (3 candles, no pullbacks)
    data['timestamp'].append(dates[27])
    data['open'].append(100.8)
    data['high'].append(101.5)
    data['low'].append(100.7)
    data['close'].append(101.3)
    data['volume'].append(2500)
    
    data['timestamp'].append(dates[28])
    data['open'].append(101.3)
    data['high'].append(102.0)
    data['low'].append(101.2)
    data['close'].append(101.8)
    data['volume'].append(2200)
    
    data['timestamp'].append(dates[29])
    data['open'].append(101.8)
    data['high'].append(103.0)
    data['low'].append(101.7)
    data['close'].append(102.5)
    data['volume'].append(2000)
    
    # Add padding
    for i in range(10):
        data['timestamp'].append(dates[30 + i])
        data['open'].append(102.5)
        data['high'].append(103.0)
        data['low'].append(102.0)
        data['close'].append(102.5)
        data['volume'].append(1500)
    
    return pd.DataFrame(data)

# Create data and detector
df = create_test_data_bullish_ob()
detector = OrderBlockDetector(min_volume_ratio=1.5, min_price_move=1.5, lookback_candles=3)

# Add calculated fields
df['volume_ma'] = df['volume'].rolling(window=20).mean()
df['volume_ratio'] = df['volume'] / df['volume_ma']
df['is_bullish'] = df['close'] > df['open']
df['is_bearish'] = df['close'] < df['open']

print("=" * 80)
print("DEBUG: Perfect Bullish OB Test Data")
print("=" * 80)
print()

# Print key candles
print("Index 25 (Order Block - Bearish):")
print(f"  OHLC: {df.iloc[25]['open']:.2f} / {df.iloc[25]['high']:.2f} / {df.iloc[25]['low']:.2f} / {df.iloc[25]['close']:.2f}")
print(f"  Volume: {df.iloc[25]['volume']:.0f} (ratio: {df.iloc[25]['volume_ratio']:.2f})")
print(f"  Is Bearish: {df.iloc[25]['is_bearish']}")
print()

print("Index 26 (Engulfing - Bullish):")
print(f"  OHLC: {df.iloc[26]['open']:.2f} / {df.iloc[26]['high']:.2f} / {df.iloc[26]['low']:.2f} / {df.iloc[26]['close']:.2f}")
print(f"  Volume: {df.iloc[26]['volume']:.0f} (ratio: {df.iloc[26]['volume_ratio']:.2f})")
print(f"  Is Bullish: {df.iloc[26]['is_bullish']}")
print()

# Check engulfment
engulfment = (df.iloc[26]['low'] < df.iloc[25]['low'] and 
             df.iloc[26]['close'] > df.iloc[25]['high'])
print(f"Engulfment Check: {engulfment}")
print(f"  Next low ({df.iloc[26]['low']:.2f}) < Current low ({df.iloc[25]['low']:.2f}): {df.iloc[26]['low'] < df.iloc[25]['low']}")
print(f"  Next close ({df.iloc[26]['close']:.2f}) > Current high ({df.iloc[25]['high']:.2f}): {df.iloc[26]['close'] > df.iloc[25]['high']}")
print()

# Check price move
current_close = df.iloc[26]['close']
future_high = df.iloc[27:30]['high'].max()
price_move_pct = ((future_high - current_close) / current_close) * 100
print(f"Price Move: {price_move_pct:.2f}% (min required: 1.5%)")
print(f"  Current close: ${current_close:.2f}")
print(f"  Future high: ${future_high:.2f}")
print()

# Check volume ratio
print(f"Volume Ratio: {df.iloc[26]['volume_ratio']:.2f} (min required: 1.5)")
print()

# Check follow-through
print("Follow-through Check (indexes 27-29):")
for i in range(27, 30):
    if i < len(df):
        higher = df.iloc[i]['close'] > df.iloc[i-1]['close']
        print(f"  Index {i}: close {df.iloc[i]['close']:.2f} vs prev {df.iloc[i-1]['close']:.2f} = {higher}")

continuation_count = sum(1 for i in range(27, 30) if df.iloc[i]['close'] > df.iloc[i-1]['close'])
print(f"  Continuation count: {continuation_count}/3 (need >= 2)")
print()

# Check pullback
print("Pullback Check:")
move_size = df.iloc[29]['close'] - df.iloc[26]['close']
start_price = df.iloc[26]['close']
print(f"  Move size: ${move_size:.2f}")
print(f"  Start price: ${start_price:.2f}")

max_pullback = 0
for k in range(27, 29):
    drop_close = start_price - df.iloc[k]['close']
    drop_low = start_price - df.iloc[k]['low']
    max_drop = max(drop_close, drop_low)
    print(f"  Index {k}: drop_close={drop_close:.2f}, drop_low={drop_low:.2f}, max={max_drop:.2f}")
    if max_drop > max_pullback:
        max_pullback = max_drop

pullback_threshold = move_size * 0.5
print(f"  Max pullback: ${max_pullback:.2f}")
print(f"  Threshold (50% of move): ${pullback_threshold:.2f}")
print(f"  Has significant pullback: {max_pullback > pullback_threshold}")
print()

# Run detector
print("=" * 80)
print("Running Detector...")
print("=" * 80)
blocks = detector.detect_order_blocks(df)
bullish = [ob for ob in blocks if ob.type == 'bullish']

if bullish:
    print(f"✅ Detected {len(bullish)} bullish OB(s)")
    for ob in bullish:
        print(f"   Zone: ${ob.start_price:.2f} - ${ob.end_price:.2f}")
else:
    print("❌ No bullish OBs detected")
