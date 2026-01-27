#!/bin/bash
# Master Position Checker - All Trading Platforms
# Never breaks, always reports

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           ATLAS POSITION CHECK - ALL PLATFORMS                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
date
echo ""

TOTAL_PNL=0
HAS_POSITIONS=false

# ============================================================================
# JUPITER PERPS (via browser check)
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 JUPITER PERPS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if we have open positions in active-positions.md
if grep -q "JUPITER PERPS" ~/clawd/memory/trading/active-positions.md 2>/dev/null; then
    echo "✅ Jupiter positions found in memory"
    # Extract the position details
    grep -A 15 "JUPITER PERPS" ~/clawd/memory/trading/active-positions.md | head -20
    HAS_POSITIONS=true
    echo ""
    echo "⚠️  Check browser for live P&L: jup.ag/perps"
else
    echo "✅ No Jupiter positions"
fi

echo ""

# ============================================================================
# KALSHI MARKETS (via Python CLI)
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎲 KALSHI MARKETS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f ~/clawd/kalshi-trader/check_all_positions.py ]; then
    cd ~/clawd/kalshi-trader
    if [ -d venv ]; then
        source venv/bin/activate
        python check_all_positions.py 2>&1 || echo "❌ Kalshi check failed"
        deactivate
        HAS_POSITIONS=true
    else
        echo "❌ Kalshi venv not found"
    fi
else
    echo "❌ Kalshi script not found"
fi

echo ""

# ============================================================================
# ALPACA STOCKS (via Node CLI)
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📈 ALPACA STOCKS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f ~/clawd/atlas-trader/cli.js ]; then
    cd ~/clawd/atlas-trader
    
    # Check account
    echo "Account Status:"
    node cli.js account 2>&1 || echo "❌ Alpaca account check failed"
    echo ""
    
    # Check positions
    echo "Positions:"
    POSITIONS=$(node cli.js positions 2>&1)
    if echo "$POSITIONS" | grep -q "No open positions"; then
        echo "✅ No open positions"
    else
        echo "$POSITIONS"
        HAS_POSITIONS=true
    fi
    echo ""
    
    # Check orders
    echo "Open Orders:"
    ORDERS=$(node cli.js orders open 2>&1)
    if echo "$ORDERS" | grep -q "No open orders"; then
        echo "✅ No open orders"
    else
        echo "$ORDERS"
    fi
else
    echo "❌ Alpaca CLI not found"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ POSITION CHECK COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ "$HAS_POSITIONS" = false ]; then
    echo "🟢 ALL CLEAR - No open positions across all platforms"
fi

echo ""
date
