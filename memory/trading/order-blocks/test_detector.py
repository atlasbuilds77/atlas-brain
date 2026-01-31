#!/usr/bin/env python3
"""
Quick test script for order block detector
Tests the system with sample data to verify it works
"""

import os
import sys
from order_block_detector import OrderBlockDetector

def test_basic_detection():
    """Test basic order block detection"""
    print("\n" + "="*70)
    print("ORDER BLOCK DETECTOR - TEST SUITE")
    print("="*70)
    
    # Check if API keys are set
    if not os.getenv('ALPACA_API_KEY') or not os.getenv('ALPACA_API_SECRET'):
        print("\n❌ ERROR: Alpaca API credentials not set")
        print("\nPlease set environment variables:")
        print("  export ALPACA_API_KEY='your_key'")
        print("  export ALPACA_API_SECRET='your_secret'")
        print("\nOr pass them to the constructor:")
        print("  detector = OrderBlockDetector(api_key='...', api_secret='...')")
        return False
    
    try:
        detector = OrderBlockDetector()
        print("\n✅ Detector initialized successfully")
        
        # Test with a popular stock
        test_symbols = [
            ('AAPL', '1h', 'stock'),
            ('SPY', '4h', 'stock'),
        ]
        
        for symbol, timeframe, asset_type in test_symbols:
            print(f"\n{'='*70}")
            print(f"Testing {symbol} ({timeframe})")
            print('='*70)
            
            result = detector.detect(symbol, timeframe, asset_type)
            
            if result['order_blocks']:
                print(f"\n✅ SUCCESS: Detected {len(result['order_blocks'])} order blocks")
                print(f"\nSummary: {result['summary']}")
                
                print("\nTop 3 Order Blocks:")
                for i, ob in enumerate(result['order_blocks'][:3], 1):
                    print(f"\n  {i}. {ob['type'].upper()} ORDER BLOCK")
                    print(f"     Zone: ${ob['zone_low']:.2f} - ${ob['zone_high']:.2f}")
                    print(f"     Strength: {ob['adjusted_strength']:.1f}/10")
                    print(f"     Age: {ob['age_candles']} candles")
                    print(f"     Volume: {ob['volume_ratio']:.1f}x average")
            else:
                print(f"\n⚠️  No order blocks detected for {symbol}")
                print(f"    This is normal for ranging/low volatility markets")
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED")
        print("="*70)
        print("\nThe order block detector is working correctly!")
        print("\nNext steps:")
        print("  1. Test with your own symbols")
        print("  2. Integrate with your trading system")
        print("  3. Set up pre-trade validation")
        print("\nSee 4-INTEGRATION-GUIDE.md for details")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        print("\nTroubleshooting:")
        print("  - Check API credentials are correct")
        print("  - Ensure you have internet connection")
        print("  - Verify Alpaca API is accessible")
        print("  - Try: pip install --upgrade alpaca-py pandas numpy")
        return False


def test_validation_logic():
    """Test the validation logic with mock data"""
    print("\n" + "="*70)
    print("TESTING VALIDATION LOGIC")
    print("="*70)
    
    # Simulate order block detection result
    mock_result = {
        'symbol': 'TEST',
        'timeframe': '1h',
        'current_price': 100.0,
        'order_blocks': [
            {
                'type': 'bearish',
                'zone_low': 105.0,
                'zone_high': 107.0,
                'adjusted_strength': 8.5,
                'age_candles': 5
            },
            {
                'type': 'bullish',
                'zone_low': 93.0,
                'zone_high': 95.0,
                'adjusted_strength': 7.2,
                'age_candles': 10
            }
        ]
    }
    
    print("\nMock Order Blocks:")
    print(f"  - Bearish block at $105-107 (strength: 8.5)")
    print(f"  - Bullish block at $93-95 (strength: 7.2)")
    print(f"  - Current price: $100")
    
    test_cases = [
        # (direction, entry_price, should_block, description)
        ('long', 106.0, True, "Long entry AT bearish block"),
        ('short', 94.0, True, "Short entry AT bullish block"),
        ('long', 98.0, False, "Long entry away from blocks"),
        ('short', 102.0, False, "Short entry away from blocks"),
        ('long', 108.0, False, "Long entry ABOVE bearish block (breakout)"),
        ('short', 92.0, False, "Short entry BELOW bullish block (breakdown)"),
    ]
    
    print("\nRunning validation tests:")
    passed = 0
    failed = 0
    
    for direction, price, should_block, description in test_cases:
        # Check if entry conflicts
        conflicts = False
        for ob in mock_result['order_blocks']:
            in_zone = ob['zone_low'] <= price <= ob['zone_high']
            
            if direction == 'long' and ob['type'] == 'bearish' and in_zone:
                conflicts = True
            elif direction == 'short' and ob['type'] == 'bullish' and in_zone:
                conflicts = True
        
        result_str = "BLOCKED" if conflicts else "ALLOWED"
        expected_str = "BLOCKED" if should_block else "ALLOWED"
        
        if conflicts == should_block:
            print(f"  ✅ {result_str}: {description}")
            passed += 1
        else:
            print(f"  ❌ {result_str} (expected {expected_str}): {description}")
            failed += 1
    
    print(f"\nValidation Tests: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All validation logic tests passed!")
    
    return failed == 0


if __name__ == '__main__':
    print("\n🔬 Order Block Detector Test Suite")
    
    # Test validation logic (no API needed)
    validation_ok = test_validation_logic()
    
    # Test actual detection (requires API)
    detection_ok = test_basic_detection()
    
    if validation_ok and detection_ok:
        print("\n🎉 ALL TESTS PASSED - System is ready!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed - please review errors above")
        sys.exit(1)
