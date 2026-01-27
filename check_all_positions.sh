#!/bin/bash
# Check all trading positions across platforms

echo "=========================================="
echo "POSITION CHECK - ALL PLATFORMS"
echo "=========================================="
echo ""

# Kalshi
echo "🎲 KALSHI:"
cd ~/clawd/kalshi-trader && source venv/bin/activate && python3 positions.py
echo ""

# Drift (crypto perps)
echo "⚡ DRIFT CRYPTO:"
cd ~/clawd/drift-bot && source bin/activate && python3 drift_trade.py status 2>&1 || echo "❌ Drift script error (RPC issue)"
echo ""

# Jupiter Perps
echo "🪐 JUPITER PERPS:"
cd ~/clawd/jupiter-perps-trader && npx tsx trade.ts positions
echo ""

echo "=========================================="
