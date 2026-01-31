#!/usr/bin/env python3
"""
Simple isolated test to verify detection logic
"""

import pandas as pd
from datetime import datetime, timedelta

# Create minimal test data
dates = [datetime.now() - timedelta(hours=i) for i in range(40, 0, -1)]

data = {
    'timestamp': [],
    'open': [],
    'high': [],
    'low': [],
    'close': [],
    'volume': []
}

# 25 consolidation candles
for i in range(25):
    data['timestamp'].append(dates[i])
    data['open'].append(100.0)
    data['high'].append(100.5)
    data['low'].append(99.5)
    data['close'].append(100.0)
    data['volume'].append(1000)

# Bearish OB candle (index 25)
data['timestamp'].append(dates[25])
data['open'].append(100.0)
data['high'].append(100.2)
data['low'].append(99.0)
data['close'].append(99.2)
data['volume'].append(2000)

# Engulfing bullish (index 26)
data['timestamp'].append(dates[26])
data['open'].append(99.2)
data['high'].append(101.0)
data['low'].append(98.5)
data['close'].append(100.8)
data['volume'].append(3000)

# Impulse (indexes 27-29)
for i, (o, h, l, c) in enumerate([(100.8, 101.5, 100.7, 101.3),
                                    (101.3, 102.0, 101.2, 101.8),
                                    (101.8, 103.0, 101.7, 102.5)]):
    data['timestamp'].append(dates[27 + i])
    data['open'].append(o)
    data['high'].append(h)
    data['low'].append(l)
    data['close'].append(c)
    data['volume'].append(2000)

# Padding
for i in range(10):
    data['timestamp'].append(dates[30 + i])
    data['open'].append(102.5)
    data['high'].append(103.0)
    data['low'].append(102.0)
    data['close'].append(102.5)
    data['volume'].append(1500)

df = pd.DataFrame(data)

# Calculate required fields
df['volume_ma'] = df['volume'].rolling(window=20).mean()
df['volume_ratio'] = df['volume'] / df['volume_ma']
df['is_bullish'] = df['close'] > df['open']
df['is_bearish'] = df['close'] < df['open']

print("Testing OB detection at index 25...")
print()

# Manual simulation of detector logic
i = 25
lookback_candles = 3
min_volume_ratio = 1.5
min_price_move = 1.5

print(f"Step 1: Check if candle {i} is bearish")
is_bearish = df.iloc[i]['is_bearish']
print(f"  Result: {is_bearish}")
if not is_bearish:
    print("  ❌ Failed - not bearish")
    exit(1)

print()
print(f"Step 2: Check if candle {i+1} is bullish")
next_candle = df.iloc[i + 1]
is_bullish = next_candle['is_bullish']
print(f"  Result: {is_bullish}")
if not is_bullish:
    print("  ❌ Failed - next not bullish")
    exit(1)

print()
print("Step 3: Check engulfment")
current_candle = df.iloc[i]
engulfment = (next_candle['low'] < current_candle['low'] and 
             next_candle['close'] > current_candle['high'])
print(f"  Result: {engulfment}")
print(f"  Next low ({next_candle['low']}) < Current low ({current_candle['low']}): {next_candle['low'] < current_candle['low']}")
print(f"  Next close ({next_candle['close']}) > Current high ({current_candle['high']}): {next_candle['close'] > current_candle['high']}")
if not engulfment:
    print("  ❌ Failed - no engulfment")
    exit(1)

print()
print("Step 4: Check price move")
current_close = df.iloc[i + 1]['close']
future_slice = df.iloc[i + 1:i + 1 + lookback_candles]
print(f"  Future slice: indexes {i+1} to {i+1+lookback_candles-1}")
print(f"  Future slice length: {len(future_slice)}")
future_high = future_slice['high'].max()
price_move_pct = ((future_high - current_close) / current_close) * 100
print(f"  Current close: ${current_close:.2f}")
print(f"  Future high: ${future_high:.2f}")
print(f"  Price move: {price_move_pct:.2f}%")
if price_move_pct < min_price_move:
    print(f"  ❌ Failed - price move {price_move_pct:.2f}% < {min_price_move}%")
    exit(1)

print()
print("Step 5: Check follow-through")
start_i = i + 1
print(f"  Starting from index {start_i}")
if start_i + lookback_candles >= len(df):
    print(f"  ❌ Failed - not enough data ({start_i} + {lookback_candles} >= {len(df)})")
    exit(1)

continuation_count = 0
for j in range(start_i + 1, min(start_i + lookback_candles + 1, len(df))):
    higher = df.iloc[j]['close'] > df.iloc[j-1]['close']
    print(f"  Index {j}: {df.iloc[j]['close']:.2f} > {df.iloc[j-1]['close']:.2f} = {higher}")
    if higher:
        continuation_count += 1

print(f"  Continuation count: {continuation_count}")
if continuation_count < 2:
    print(f"  ❌ Failed - continuation {continuation_count} < 2")
    exit(1)

print()
print("Step 6: Check pullback")
end_idx = min(i + 1 + lookback_candles, len(df) - 1)
print(f"  Checking indexes {i+1+1} to {end_idx}")
move_size = df.iloc[end_idx]['close'] - df.iloc[i + 1]['close']
start_price = df.iloc[i + 1]['close']

print(f"  Move size: ${move_size:.2f}")
print(f"  Start price: ${start_price:.2f}")

has_pullback = False
for k in range(i + 2, end_idx):
    drop_close = start_price - df.iloc[k]['close']
    drop_low = start_price - df.iloc[k]['low']
    max_drop = max(drop_close, drop_low)
    print(f"  Index {k}: drop_close={drop_close:.2f}, drop_low={drop_low:.2f}, max={max_drop:.2f}")
    if max_drop > (move_size * 0.5):
        has_pullback = True

print(f"  Has significant pullback: {has_pullback}")
if has_pullback:
    print("  ❌ Failed - significant pullback detected")
    exit(1)

print()
print("Step 7: Check volume ratio")
volume_ratio = next_candle['volume_ratio']
print(f"  Volume ratio: {volume_ratio:.2f}")
if volume_ratio < min_volume_ratio:
    print(f"  ❌ Failed - volume ratio {volume_ratio:.2f} < {min_volume_ratio}")
    exit(1)

print()
print("=" * 80)
print("✅ ALL CHECKS PASSED - OB should be detected!")
print("=" * 80)
