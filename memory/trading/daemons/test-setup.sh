#!/bin/bash
# Quick test of daemon setup

echo "=================================="
echo "Trading Daemon Setup Test"
echo "=================================="
echo ""

DAEMON_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "1. Checking files..."
echo ""

# Check Python files
for daemon in setup-scanner.py level-watcher.py order-block-updater.py; do
    if [ -f "$DAEMON_DIR/$daemon" ]; then
        echo "  ✓ $daemon"
    else
        echo "  ✗ $daemon MISSING"
    fi
done

echo ""

# Check shell scripts
for script in start-all.sh stop-all.sh status.sh; do
    if [ -f "$DAEMON_DIR/$script" ]; then
        echo "  ✓ $script"
    else
        echo "  ✗ $script MISSING"
    fi
done

echo ""
echo "2. Checking dependencies..."
echo ""

# Check Python
if command -v python3 &> /dev/null; then
    echo "  ✓ Python 3: $(python3 --version)"
else
    echo "  ✗ Python 3 not found"
fi

# Check alpaca-py
if python3 -c "import alpaca" 2>/dev/null; then
    echo "  ✓ alpaca-py installed"
else
    echo "  ✗ alpaca-py NOT installed (run: pip install alpaca-py)"
fi

# Check pandas
if python3 -c "import pandas" 2>/dev/null; then
    echo "  ✓ pandas installed"
else
    echo "  ✗ pandas NOT installed (run: pip install pandas)"
fi

# Check numpy
if python3 -c "import numpy" 2>/dev/null; then
    echo "  ✓ numpy installed"
else
    echo "  ✗ numpy NOT installed (run: pip install numpy)"
fi

echo ""
echo "3. Checking environment..."
echo ""

if [ -z "$ALPACA_API_KEY" ]; then
    echo "  ✗ ALPACA_API_KEY not set"
else
    echo "  ✓ ALPACA_API_KEY set"
fi

if [ -z "$ALPACA_API_SECRET" ]; then
    echo "  ✗ ALPACA_API_SECRET not set"
else
    echo "  ✓ ALPACA_API_SECRET set"
fi

echo ""
echo "4. Checking order block detector..."
echo ""

DETECTOR="/Users/atlasbuilds/clawd/memory/trading/order-blocks/order_block_detector.py"
if [ -f "$DETECTOR" ]; then
    echo "  ✓ Order block detector found"
else
    echo "  ✗ Order block detector NOT found at $DETECTOR"
fi

echo ""
echo "5. Checking iMessage script..."
echo ""

IMSG="/Users/atlasbuilds/clawd/tools/imsg-enhanced.sh"
if [ -f "$IMSG" ]; then
    echo "  ✓ iMessage script found"
    if [ -x "$IMSG" ]; then
        echo "  ✓ iMessage script is executable"
    else
        echo "  ⚠ iMessage script not executable (run: chmod +x $IMSG)"
    fi
else
    echo "  ✗ iMessage script NOT found at $IMSG"
fi

echo ""
echo "6. Checking watch levels file..."
echo ""

WATCH_LEVELS="/Users/atlasbuilds/clawd/memory/trading/watch-levels.json"
if [ -f "$WATCH_LEVELS" ]; then
    echo "  ✓ Watch levels file exists"
    echo "  Sample:"
    head -n 10 "$WATCH_LEVELS" | sed 's/^/    /'
else
    echo "  ⚠ Watch levels file not found (will be created on first run)"
fi

echo ""
echo "=================================="
echo "Setup Check Complete"
echo "=================================="
echo ""

# Make scripts executable
echo "Making scripts executable..."
chmod +x "$DAEMON_DIR"/*.sh 2>/dev/null
echo "  ✓ Shell scripts made executable"

echo ""
echo "Ready to start daemons:"
echo "  ./start-all.sh"
echo ""
