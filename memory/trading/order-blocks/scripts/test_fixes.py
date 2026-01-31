#!/usr/bin/env python3
"""
Test script to verify the 3 critical fixes in order_block_detector.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from order_block_detector import OrderBlockDetector, OrderBlock

def create_test_data_bullish_ob():
    """
    Create synthetic data with a perfect bullish order block:
    - Consolidation
    - Bearish candle (order block)
    - Engulfing bullish candle
    - Clean impulse up (no pullbacks)
    """
    dates = [datetime.now() - timedelta(hours=i) for i in range(40, 0, -1)]
    
    # Need 20+ candles for volume_ma calculation
    # Consolidation phase (25 candles around $100 with consistent volume)
    data = {
        'timestamp': dates[:25],
        'open': [100.0] * 25,
        'high': [100.5] * 25,
        'low': [99.5] * 25,
        'close': [100.0] * 25,
        'volume': [1000] * 25  # Base volume for average
    }
    
    # Order block candle (bearish at index 25)
    data['timestamp'].append(dates[25])
    data['open'].append(100.0)
    data['high'].append(100.2)
    data['low'].append(99.0)  # Drops to 99
    data['close'].append(99.2)  # Closes bearish
    data['volume'].append(2000)  # 2x average volume
    
    # Engulfing bullish candle (index 26)
    data['timestamp'].append(dates[26])
    data['open'].append(99.2)
    data['high'].append(101.0)  # Engulfs high of previous
    data['low'].append(98.5)    # Engulfs low of previous
    data['close'].append(100.8)  # Closes bullish
    data['volume'].append(3000)  # 3x average volume
    
    # Clean impulse up (3 candles, no pullbacks) - BIGGER MOVE
    data['timestamp'].append(dates[27])
    data['open'].append(100.8)
    data['high'].append(102.0)  # Bigger high
    data['low'].append(100.7)
    data['close'].append(101.8)  # Bigger close
    data['volume'].append(2500)
    
    data['timestamp'].append(dates[28])
    data['open'].append(101.8)
    data['high'].append(103.0)  # Bigger high
    data['low'].append(101.7)
    data['close'].append(102.8)  # Bigger close
    data['volume'].append(2200)
    
    data['timestamp'].append(dates[29])
    data['open'].append(102.8)
    data['high'].append(104.0)  # Bigger high (4% total move from 100.8)
    data['low'].append(102.7)
    data['close'].append(103.5)  # Bigger close
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

def create_test_data_no_engulfment():
    """
    Create data that SHOULD NOT trigger OB due to missing engulfment
    """
    dates = [datetime.now() - timedelta(hours=i) for i in range(40, 0, -1)]
    
    data = {
        'timestamp': dates[:25],
        'open': [100.0] * 25,
        'high': [100.5] * 25,
        'low': [99.5] * 25,
        'close': [100.0] * 25,
        'volume': [1000] * 25
    }
    
    # Bearish candle
    data['timestamp'].append(dates[25])
    data['open'].append(100.0)
    data['high'].append(100.2)
    data['low'].append(99.0)
    data['close'].append(99.2)
    data['volume'].append(2000)
    
    # Bullish candle but NO ENGULFMENT (doesn't go below previous low)
    data['timestamp'].append(dates[26])
    data['open'].append(99.2)
    data['high'].append(101.0)  # Goes above previous high ✓
    data['low'].append(99.1)    # But doesn't go below previous low ✗
    data['close'].append(100.8)
    data['volume'].append(3000)
    
    # Rest of the move
    for i in range(13):
        data['timestamp'].append(dates[27 + i])
        data['open'].append(100.8 + i * 0.2)
        data['high'].append(101.5 + i * 0.2)
        data['low'].append(100.7 + i * 0.2)
        data['close'].append(101.3 + i * 0.2)
        data['volume'].append(2000)
    
    return pd.DataFrame(data)

def create_test_data_with_pullback():
    """
    Create data with a significant pullback (should be rejected)
    """
    dates = [datetime.now() - timedelta(hours=i) for i in range(40, 0, -1)]
    
    data = {
        'timestamp': dates[:25],
        'open': [100.0] * 25,
        'high': [100.5] * 25,
        'low': [99.5] * 25,
        'close': [100.0] * 25,
        'volume': [1000] * 25
    }
    
    # Order block candle
    data['timestamp'].append(dates[25])
    data['open'].append(100.0)
    data['high'].append(100.2)
    data['low'].append(99.0)
    data['close'].append(99.2)
    data['volume'].append(2000)
    
    # Engulfing candle
    data['timestamp'].append(dates[26])
    data['open'].append(99.2)
    data['high'].append(101.0)
    data['low'].append(98.5)
    data['close'].append(100.8)
    data['volume'].append(3000)
    
    # Next candle has MAJOR PULLBACK (low goes way down)
    data['timestamp'].append(dates[27])
    data['open'].append(100.8)
    data['high'].append(101.0)
    data['low'].append(99.0)  # Huge wick pullback (>50% of move)
    data['close'].append(100.5)
    data['volume'].append(2500)
    
    # Rest continues up
    for i in range(12):
        data['timestamp'].append(dates[28 + i])
        data['open'].append(100.5 + i * 0.3)
        data['high'].append(101.5 + i * 0.3)
        data['low'].append(100.4 + i * 0.3)
        data['close'].append(101.0 + i * 0.3)
        data['volume'].append(2000)
    
    return pd.DataFrame(data)

def run_tests():
    """Run all tests and report results"""
    print("=" * 80)
    print("ORDER BLOCK DETECTOR - CRITICAL FIXES VERIFICATION")
    print("=" * 80)
    print()
    
    detector = OrderBlockDetector(min_volume_ratio=1.5, min_price_move=1.5, lookback_candles=3)
    
    # Test 1: Perfect bullish OB (should detect)
    print("Test 1: Perfect Bullish Order Block")
    print("-" * 80)
    df1 = create_test_data_bullish_ob()
    blocks1 = detector.detect_order_blocks(df1)
    bullish1 = [ob for ob in blocks1 if ob.type == 'bullish']
    
    if len(bullish1) > 0:
        print("✅ PASS: Detected bullish order block")
        print(f"   Found {len(bullish1)} bullish OB(s)")
        print(f"   Zone: ${bullish1[0].start_price:.2f} - ${bullish1[0].end_price:.2f}")
        print(f"   Strength: {bullish1[0].strength}/10")
    else:
        print("❌ FAIL: Should have detected a bullish order block")
    print()
    
    # Test 2: No engulfment (should NOT detect)
    print("Test 2: Missing Engulfment (Should NOT Detect)")
    print("-" * 80)
    df2 = create_test_data_no_engulfment()
    blocks2 = detector.detect_order_blocks(df2)
    bullish2 = [ob for ob in blocks2 if ob.type == 'bullish']
    
    if len(bullish2) == 0:
        print("✅ PASS: Correctly rejected (no engulfment)")
    else:
        print("❌ FAIL: Should NOT have detected OB without engulfment")
        print(f"   Incorrectly found {len(bullish2)} OB(s)")
    print()
    
    # Test 3: Significant pullback (should NOT detect)
    print("Test 3: Significant Pullback (Should NOT Detect)")
    print("-" * 80)
    df3 = create_test_data_with_pullback()
    blocks3 = detector.detect_order_blocks(df3)
    bullish3 = [ob for ob in blocks3 if ob.type == 'bullish']
    
    if len(bullish3) == 0:
        print("✅ PASS: Correctly rejected (significant pullback detected)")
    else:
        print("❌ FAIL: Should NOT have detected OB with major pullback")
        print(f"   Incorrectly found {len(bullish3)} OB(s)")
    print()
    
    # Summary
    print("=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    tests_passed = 0
    if len(bullish1) > 0:
        tests_passed += 1
    if len(bullish2) == 0:
        tests_passed += 1
    if len(bullish3) == 0:
        tests_passed += 1
    
    print(f"Tests Passed: {tests_passed}/3")
    
    if tests_passed == 3:
        print("\n✅ ALL CRITICAL FIXES VERIFIED - READY FOR PRODUCTION")
        print("\nFixed Issues:")
        print("1. ✅ Engulfment check implemented")
        print("2. ✅ Follow-through validation (no off-by-one error)")
        print("3. ✅ Pullback detection using wicks")
    else:
        print("\n⚠️  SOME TESTS FAILED - REVIEW REQUIRED")
    
    print("=" * 80)
    
    return tests_passed == 3

if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
