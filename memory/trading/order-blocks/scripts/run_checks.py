#!/usr/bin/env python3
"""Run pre-trade checks for META, SPY, and QQQ"""

import subprocess
import sys

tickers = [
    ('META', 'long', 734.93),
    ('SPY', 'long', 696.41),
    ('QQQ', 'long', 633.02)
]

print("STARTING ORDER BLOCK PRE-TRADE CHECKS")
print("=" * 80)

for symbol, direction, entry in tickers:
    print(f"\n\n{'=' * 80}")
    print(f"CHECKING: {symbol} - {direction.upper()} @ ${entry:.2f}")
    print("=" * 80)
    
    try:
        result = subprocess.run(
            [
                'python3', 'pre_trade_check.py',
                '--symbol', symbol,
                '--direction', direction,
                '--entry', str(entry)
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        print(f"\nExit Code: {result.returncode}")
        print("VERDICT:", "✅ APPROVED" if result.returncode == 0 else "❌ REJECTED")
        
    except subprocess.TimeoutExpired:
        print(f"ERROR: Timeout while checking {symbol}")
    except Exception as e:
        print(f"ERROR: {e}")

print("\n" + "=" * 80)
print("ALL CHECKS COMPLETE")
print("=" * 80)
