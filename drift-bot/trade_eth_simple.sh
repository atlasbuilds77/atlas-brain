#!/bin/bash
# Simple ETH perp trade script bypassing Drift SDK rate limits

set -e

WALLET_KEYPAIR="/Users/atlasbuilds/clawd/drift-bot/.secrets/solana-keypair.json"
SOL_AMOUNT=0.7  # Leave 0.08 for fees
LEVERAGE=5
ETH_USD=2907.62

echo "=== DRIFT ETH PERP TRADE SETUP ==="
echo "Wallet: 7UKP7mofxSk6mn4z4jQNNE7HZSdXTPkMY8VKypZcrafx"
echo "Balance: 0.782 SOL (\$96.78)"
echo "Depositing: $SOL_AMOUNT SOL (~\$86.60)"
echo "Leverage: ${LEVERAGE}x"
echo "ETH Price: \$$ETH_USD"
echo "Notional: ~\$433"
echo ""
echo "MANUAL STEPS (Drift SDK having rate limit issues):"
echo "1. Go to: https://app.drift.trade"
echo "2. Import wallet with seed phrase:"
echo "   vapor fetch ribbon gold inside pledge glimpse person chapter source talent ready"
echo "3. Deposit $SOL_AMOUNT SOL as collateral"
echo "4. Navigate to ETH-PERP market"
echo "5. Set leverage to ${LEVERAGE}x"
echo "6. Open LONG position with ~\$86 collateral (${LEVERAGE}x = \$433 notional)"
echo ""
echo "OR use Hyperliquid (no rate limits):"
echo "1. Transfer 0.78 SOL → USDC on Jupiter"
echo "2. Bridge USDC to Arbitrum"
echo "3. Deposit to Hyperliquid"
echo "4. Trade ETH perp there"
echo ""
read -p "Want me to set up Hyperliquid instead? (y/n): " choice
