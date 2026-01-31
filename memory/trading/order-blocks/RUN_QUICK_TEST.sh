#!/bin/bash
# Quick test launcher - SPY last 2 weeks only

cd /Users/atlasbuilds/clawd/memory/trading/order-blocks

# Check credentials
if [ -z "$ALPACA_API_KEY" ] || [ -z "$ALPACA_API_SECRET" ]; then
    echo "❌ Set credentials first:"
    echo '  export ALPACA_API_KEY="your_key"'
    echo '  export ALPACA_API_SECRET="your_secret"'
    exit 1
fi

# Run quick test
./venv/bin/python3 quick_test.py
