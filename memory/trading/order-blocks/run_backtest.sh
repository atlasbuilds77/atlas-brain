#!/bin/bash
# Quick-start script for Order Block Backtest
# Checks credentials and runs the backtest

set -e

echo "=================================="
echo "ORDER BLOCK BACKTEST - LAUNCHER"
echo "=================================="
echo ""

# Check if we're in the right directory
if [ ! -f "backtest_order_blocks.py" ]; then
    echo "❌ Error: backtest_order_blocks.py not found"
    echo "   Please run this script from the order-blocks directory"
    exit 1
fi

# Check for virtual environment
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment not found"
    echo "   Creating virtual environment..."
    python3 -m venv venv
    ./venv/bin/pip install alpaca-py pandas numpy pytz
fi

# Check for API credentials
if [ -z "$ALPACA_API_KEY" ] || [ -z "$ALPACA_API_SECRET" ]; then
    echo "❌ ERROR: Alpaca API credentials not found"
    echo ""
    echo "You need to set these environment variables:"
    echo "  export ALPACA_API_KEY=\"your_key_here\""
    echo "  export ALPACA_API_SECRET=\"your_secret_here\""
    echo ""
    echo "Get your credentials from:"
    echo "  https://app.alpaca.markets/paper/dashboard/overview"
    echo ""
    echo "To make them permanent, add to ~/.zshrc:"
    echo "  echo 'export ALPACA_API_KEY=\"your_key\"' >> ~/.zshrc"
    echo "  echo 'export ALPACA_API_SECRET=\"your_secret\"' >> ~/.zshrc"
    echo "  source ~/.zshrc"
    echo ""
    exit 1
fi

# Credentials found
echo "✅ API credentials found"
echo "✅ Virtual environment ready"
echo ""
echo "Starting backtest..."
echo "Expected runtime: 30-45 minutes"
echo "You can interrupt with Ctrl+C (progress will be saved)"
echo ""
echo "=================================="
echo ""

# Run the backtest
./venv/bin/python3 backtest_order_blocks.py

echo ""
echo "=================================="
echo "✅ BACKTEST COMPLETE"
echo "=================================="
echo ""
echo "Results saved to:"
echo "  - backtest-results.md (human-readable)"
echo "  - backtest-data.json (raw data)"
echo ""
