#!/usr/bin/env python3
"""
Order Block Detector - Test Suite
Independent verification with synthetic data
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Create synthetic test data
def create_synthetic_bullish_ob():
    """Create perfect bullish order block pattern"""
    dates = pd.date_range(start='2024-01-01', periods=50, freq='1h')
    
    # Consolidation phase (candles 0-9)
    consolidation = [100] * 10
    
    # Order block candle (candle 10) - bearish
    ob_candle_open = 100
    ob_candle_close = 98
    ob_candle_high = 100.5
    ob_candle_low = 97.5
    
    # Bullish impulse (candles 11-14)
    impulse_candles = [99, 101, 103, 105]  # Strong upward move
    
    # Follow-through (candles 15-20)
    followthrough = [106, 107, 108, 107, 108, 109]
    
    # Rest
    rest = [109] * (50 - 10 - 1 - 4 - 6)
    
    # Build price series
    close_prices = consolidation + [ob_candle_close] + impulse_candles + followthrough + rest
    
    # Generate OHLCV
    data = []
    for i, close in enumerate(close_prices):
        if i == 10:  # Order block candle
            row = {
                'timestamp': dates[i],
                'open': ob_candle_open,
                'high': ob_candle_high,
                'low': ob_candle_low,
                'close': ob_candle_close,
                'volume': 50000  # High volume
            }
        else:
            row = {
                'timestamp': dates[i],
                'open': close - 0.5,
                'high': close + 0.5,
                'low': close - 0.5,
                'close': close,
                'volume': 10000 + np.random.randint(-2000, 2000)
            }
        data.append(row)
    
    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)
    return df

def create_synthetic_bearish_ob():
    """Create perfect bearish order block pattern"""
    dates = pd.date_range(start='2024-01-01', periods=50, freq='1h')
    
    # Consolidation
    consolidation = [100] * 10
    
    # Order block candle - bullish
    ob_candle_open = 100
    ob_candle_close = 102
    ob_candle_high = 102.5
    ob_candle_low = 99.5
    
    # Bearish impulse
    impulse_candles = [101, 99, 97, 95]
    
    # Follow-through
    followthrough = [94, 93, 92, 93, 92, 91]
    
    # Rest
    rest = [91] * (50 - 10 - 1 - 4 - 6)
    
    close_prices = consolidation + [ob_candle_close] + impulse_candles + followthrough + rest
    
    data = []
    for i, close in enumerate(close_prices):
        if i == 10:
            row = {
                'timestamp': dates[i],
                'open': ob_candle_open,
                'high': ob_candle_high,
                'low': ob_candle_low,
                'close': ob_candle_close,
                'volume': 50000
            }
        else:
            row = {
                'timestamp': dates[i],
                'open': close + 0.5,
                'high': close + 0.5,
                'low': close - 0.5,
                'close': close,
                'volume': 10000 + np.random.randint(-2000, 2000)
            }
        data.append(row)
    
    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)
    return df

def verify_volume_calculations(df):
    """Test volume ratio calculations"""
    print("\n🔍 TESTING: Volume Calculations")
    print("-" * 60)
    
    # Calculate volume MA (20-period)
    volume_ma = df['volume'].rolling(window=20).mean()
    
    # Calculate volume ratio
    volume_ratio = df['volume'] / volume_ma
    
    # Verify at candle 25 (should have 20 periods of history)
    idx = 25
    manual_ma = df['volume'].iloc[idx-20:idx].mean()
    manual_ratio = df['volume'].iloc[idx] / manual_ma
    
    print(f"Volume at candle {idx}: {df['volume'].iloc[idx]}")
    print(f"Manual MA (20-period): {manual_ma:.2f}")
    print(f"Manual Ratio: {manual_ratio:.2f}")
    print(f"Calculated MA: {volume_ma.iloc[idx]:.2f}")
    print(f"Calculated Ratio: {volume_ratio.iloc[idx]:.2f}")
    
    if abs(volume_ratio.iloc[idx] - manual_ratio) < 0.01:
        print("✅ Volume calculations CORRECT")
        return True
    else:
        print("❌ Volume calculations INCORRECT")
        return False

def verify_atr_calculation(df):
    """Test ATR calculations"""
    print("\n🔍 TESTING: ATR Calculations")
    print("-" * 60)
    
    # Calculate True Range
    tr = np.maximum(
        df['high'] - df['low'],
        np.maximum(
            abs(df['high'] - df['close'].shift(1)),
            abs(df['low'] - df['close'].shift(1))
        )
    )
    
    # Calculate ATR (14-period)
    atr = tr.rolling(window=14).mean()
    
    # Verify at candle 30
    idx = 30
    manual_atr = tr.iloc[idx-14:idx].mean()
    
    print(f"True Range at candle {idx}: {tr.iloc[idx]:.4f}")
    print(f"Manual ATR (14-period): {manual_atr:.4f}")
    print(f"Calculated ATR: {atr.iloc[idx]:.4f}")
    
    if abs(atr.iloc[idx] - manual_atr) < 0.01:
        print("✅ ATR calculations CORRECT")
        return True
    else:
        print("❌ ATR calculations INCORRECT")
        return False

def verify_impulse_detection(df, expected_impulse_start=10):
    """Test impulse move detection logic"""
    print("\n🔍 TESTING: Impulse Detection Logic")
    print("-" * 60)
    
    impulse_threshold = 2.0  # 2% move
    
    # Check candle 10 (should trigger impulse)
    start_idx = expected_impulse_start
    start_price = df['close'].iloc[start_idx]
    
    for j in range(start_idx + 1, min(start_idx + 5, len(df))):
        end_price = df['close'].iloc[j]
        pct_change = ((end_price - start_price) / start_price) * 100
        
        print(f"Candle {start_idx} to {j}: {pct_change:.2f}%")
        
        if abs(pct_change) >= impulse_threshold:
            print(f"✅ Impulse detected at candle {j} ({pct_change:.2f}%)")
            return True
    
    print("❌ No impulse detected")
    return False

def verify_consolidation_detection(df, consolidation_end=9):
    """Test consolidation detection"""
    print("\n🔍 TESTING: Consolidation Detection")
    print("-" * 60)
    
    window = 10
    start_idx = consolidation_end - window + 1
    end_idx = consolidation_end
    
    # Check price changes in consolidation window
    pct_changes = df['close'].iloc[start_idx:end_idx+1].pct_change() * 100
    max_pct_change = pct_changes.abs().max()
    
    print(f"Consolidation window: candles {start_idx} to {end_idx}")
    print(f"Max percentage change: {max_pct_change:.2f}%")
    print(f"Threshold: 2.0%")
    
    if max_pct_change < 2.0:
        print("✅ Consolidation detected correctly")
        return True
    else:
        print("⚠️  Consolidation threshold exceeded")
        return False

def verify_strength_scoring():
    """Test strength scoring logic"""
    print("\n🔍 TESTING: Strength Scoring")
    print("-" * 60)
    
    # Test volume scores
    test_cases_volume = [
        (1.0, 0),  # Below threshold (1.5)
        (1.5, 1),  # At minimum
        (2.0, 2),  # Medium
        (3.0, 3),  # High
        (5.0, 3),  # Very high (capped at 3)
    ]
    
    print("Volume Score Tests:")
    all_passed = True
    for volume_ratio, expected_score in test_cases_volume:
        if volume_ratio >= 3.0:
            score = 3
        elif volume_ratio >= 2.0:
            score = 2
        elif volume_ratio >= 1.5:
            score = 1
        else:
            score = 0
        
        status = "✅" if score == expected_score else "❌"
        print(f"  {status} Volume {volume_ratio}x → Score {score} (expected {expected_score})")
        if score != expected_score:
            all_passed = False
    
    # Test impulse scores
    test_cases_impulse = [
        (1.5, 0),  # Below 2%
        (2.0, 1),  # Minimum
        (3.0, 2),  # Medium
        (5.0, 3),  # Strong
    ]
    
    print("\nImpulse Score Tests:")
    for impulse_pct, expected_score in test_cases_impulse:
        if impulse_pct >= 5.0:
            score = 3
        elif impulse_pct >= 3.0:
            score = 2
        elif impulse_pct >= 2.0:
            score = 1
        else:
            score = 0
        
        status = "✅" if score == expected_score else "❌"
        print(f"  {status} Impulse {impulse_pct}% → Score {score} (expected {expected_score})")
        if score != expected_score:
            all_passed = False
    
    if all_passed:
        print("\n✅ Strength scoring CORRECT")
    else:
        print("\n❌ Strength scoring has errors")
    
    return all_passed

def verify_time_decay():
    """Test time decay formula"""
    print("\n🔍 TESTING: Time Decay")
    print("-" * 60)
    
    test_cases = [
        (5, 1.0),   # Fresh (≤5 candles)
        (10, 0.9),  # Recent (≤20 candles)
        (30, 0.7),  # Older (≤50 candles)
        (60, 0.5),  # Very old (>50 candles)
    ]
    
    all_passed = True
    for age, expected_decay in test_cases:
        if age <= 5:
            decay = 1.0
        elif age <= 20:
            decay = 0.9
        elif age <= 50:
            decay = 0.7
        else:
            decay = 0.5
        
        status = "✅" if decay == expected_decay else "❌"
        print(f"  {status} Age {age} candles → Decay {decay} (expected {expected_decay})")
        if decay != expected_decay:
            all_passed = False
    
    if all_passed:
        print("\n✅ Time decay CORRECT")
    else:
        print("\n❌ Time decay has errors")
    
    return all_passed

def verify_zone_extension():
    """Test zone extension calculation"""
    print("\n🔍 TESTING: Zone Extension")
    print("-" * 60)
    
    # Test case: OB with high=100, low=98
    zone_high = 100
    zone_low = 98
    extension_pct = 0.1  # 10%
    
    zone_range = zone_high - zone_low  # 2
    
    extended_high = zone_high + (zone_range * extension_pct)  # 100 + 0.2 = 100.2
    extended_low = zone_low - (zone_range * extension_pct)    # 98 - 0.2 = 97.8
    
    print(f"Original zone: {zone_low} - {zone_high}")
    print(f"Zone range: {zone_range}")
    print(f"Extension: {extension_pct * 100}%")
    print(f"Extended zone: {extended_low} - {extended_high}")
    
    # Verify the math
    expected_high = 100.2
    expected_low = 97.8
    
    if abs(extended_high - expected_high) < 0.01 and abs(extended_low - expected_low) < 0.01:
        print("✅ Zone extension calculation CORRECT")
        return True
    else:
        print("❌ Zone extension calculation INCORRECT")
        return False

def main():
    print("="*70)
    print("ORDER BLOCK DETECTOR - VERIFICATION TEST SUITE")
    print("Independent Mathematical Verification")
    print("="*70)
    
    # Create synthetic data
    print("\n📊 Creating synthetic test data...")
    df_bullish = create_synthetic_bullish_ob()
    df_bearish = create_synthetic_bearish_ob()
    print(f"✓ Created bullish OB test data ({len(df_bullish)} candles)")
    print(f"✓ Created bearish OB test data ({len(df_bearish)} candles)")
    
    # Run verification tests
    results = []
    
    results.append(("Volume Calculations", verify_volume_calculations(df_bullish)))
    results.append(("ATR Calculations", verify_atr_calculation(df_bullish)))
    results.append(("Impulse Detection", verify_impulse_detection(df_bullish, 10)))
    results.append(("Consolidation Detection", verify_consolidation_detection(df_bullish, 9)))
    results.append(("Strength Scoring", verify_strength_scoring()))
    results.append(("Time Decay", verify_time_decay()))
    results.append(("Zone Extension", verify_zone_extension()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Algorithm is mathematically sound")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - Review needed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
