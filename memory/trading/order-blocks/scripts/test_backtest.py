#!/usr/bin/env python3
"""Quick test to verify backtest can run"""

import sys
import os

print("Python version:", sys.version)
print("Working directory:", os.getcwd())

try:
    import pandas as pd
    print("✓ pandas imported")
except ImportError as e:
    print("✗ pandas import failed:", e)
    sys.exit(1)

try:
    import numpy as np
    print("✓ numpy imported")
except ImportError as e:
    print("✗ numpy import failed:", e)
    sys.exit(1)

try:
    from alpaca_trade_api import REST
    print("✓ alpaca_trade_api imported")
except ImportError as e:
    print("✗ alpaca_trade_api import failed:", e)
    sys.exit(1)

# Check environment variables
api_key = os.environ.get('ALPACA_API_KEY')
api_secret = os.environ.get('ALPACA_API_SECRET')

if api_key:
    print(f"✓ ALPACA_API_KEY found (length: {len(api_key)})")
else:
    print("✗ ALPACA_API_KEY not set")

if api_secret:
    print(f"✓ ALPACA_API_SECRET found (length: {len(api_secret)})")
else:
    print("✗ ALPACA_API_SECRET not set")

print("\nAll prerequisites met! Ready to run backtest.")
