#!/bin/bash
# Order Block Detection System - Installation & Verification Script

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║     Order Block Detection System - Installation              ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track status
ERRORS=0
WARNINGS=0

# 1. Check Python version
echo "📋 Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
    echo -e "${GREEN}✓${NC} Python 3 found: $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python 3 not found. Please install Python 3.8+"
    ERRORS=$((ERRORS + 1))
fi

# 2. Check pip
echo ""
echo "📦 Checking pip..."
if command -v pip3 &> /dev/null; then
    echo -e "${GREEN}✓${NC} pip3 found"
else
    echo -e "${RED}✗${NC} pip3 not found. Please install pip"
    ERRORS=$((ERRORS + 1))
fi

# 3. Install requirements
echo ""
echo "📥 Installing Python dependencies..."
if pip3 install -q -r requirements.txt; then
    echo -e "${GREEN}✓${NC} Dependencies installed successfully"
else
    echo -e "${RED}✗${NC} Failed to install dependencies"
    ERRORS=$((ERRORS + 1))
fi

# 4. Check Alpaca API credentials
echo ""
echo "🔑 Checking Alpaca API credentials..."
if [ -z "$ALPACA_API_KEY" ]; then
    echo -e "${YELLOW}⚠${NC} ALPACA_API_KEY not set"
    echo "   Set with: export ALPACA_API_KEY='your_key'"
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "${GREEN}✓${NC} ALPACA_API_KEY is set"
fi

if [ -z "$ALPACA_API_SECRET" ]; then
    echo -e "${YELLOW}⚠${NC} ALPACA_API_SECRET not set"
    echo "   Set with: export ALPACA_API_SECRET='your_secret'"
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "${GREEN}✓${NC} ALPACA_API_SECRET is set"
fi

# 5. Verify file structure
echo ""
echo "📂 Verifying file structure..."
FILES=(
    "order_block_detector.py"
    "orderBlockValidator.js"
    "test_detector.py"
    "1-ORDER-BLOCK-THEORY.md"
    "2-DETECTION-ALGORITHM.md"
    "4-INTEGRATION-GUIDE.md"
    "README.md"
    "requirements.txt"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file missing"
        ERRORS=$((ERRORS + 1))
    fi
done

# 6. Check executables
echo ""
echo "🔧 Checking executable permissions..."
if [ -x "order_block_detector.py" ]; then
    echo -e "${GREEN}✓${NC} order_block_detector.py is executable"
else
    echo -e "${YELLOW}⚠${NC} Making order_block_detector.py executable..."
    chmod +x order_block_detector.py
fi

if [ -x "test_detector.py" ]; then
    echo -e "${GREEN}✓${NC} test_detector.py is executable"
else
    echo -e "${YELLOW}⚠${NC} Making test_detector.py executable..."
    chmod +x test_detector.py
fi

# 7. Summary
echo ""
echo "═══════════════════════════════════════════════════════════════"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ Installation Complete!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Set API credentials (if not done):"
    echo "     export ALPACA_API_KEY='your_key'"
    echo "     export ALPACA_API_SECRET='your_secret'"
    echo ""
    echo "  2. Run test suite:"
    echo "     python3 test_detector.py"
    echo ""
    echo "  3. Try your first detection:"
    echo "     python3 order_block_detector.py AAPL --timeframe 1h"
    echo ""
    echo "  4. Read the docs:"
    echo "     cat README.md"
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ Installation Complete with Warnings${NC}"
    echo ""
    echo "Warnings: $WARNINGS"
    echo "Please address the warnings above before testing."
else
    echo -e "${RED}❌ Installation Failed${NC}"
    echo ""
    echo "Errors: $ERRORS"
    echo "Warnings: $WARNINGS"
    echo ""
    echo "Please fix the errors above and run this script again."
    exit 1
fi

echo "═══════════════════════════════════════════════════════════════"
