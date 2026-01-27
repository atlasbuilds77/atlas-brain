#!/bin/bash
# Bridge SOL from Solana to Hyperliquid via deBridge
# This converts SOL → USDC on Hyperliquid automatically

set -e

WALLET_ADDRESS="28Gv5ncMyeS5oHYgsBd9r857dpvRKqw5ttc1nKN6UxXj"
HL_ADDRESS="0x623F14f26eF7D912fbB177987A57047dc68b5C4E"

echo "============================================================"
echo "SOL → HYPERLIQUID BRIDGE (via deBridge)"
echo "============================================================"
echo ""
echo "Source: Solana wallet $WALLET_ADDRESS"
echo "Destination: Hyperliquid $HL_ADDRESS"
echo ""
echo "⚠️  MANUAL STEPS REQUIRED:"
echo ""
echo "1. Go to: https://app.debridge.finance/"
echo "2. Connect Solana wallet: $WALLET_ADDRESS"
echo "3. Select:"
echo "   - From: Solana (SOL)"
echo "   - To: Hyperliquid (USDC)"
echo "   - Amount: 0.75 SOL (~\$93)"
echo "   - Destination: $HL_ADDRESS"
echo "4. Click 'Swap' and approve transaction"
echo "5. Wait 10-15 minutes for bridge to complete"
echo ""
echo "deBridge will automatically:"
echo "  - Swap SOL → USDC"
echo "  - Bridge to Hyperliquid"
echo "  - Credit your Hyperliquid account"
echo ""
echo "After bridging completes, run:"
echo "  cd ~/clawd/hyperliquid-trader"
echo "  node simple_hl.js balance    # Check funds arrived"
echo "  node simple_hl.js long 93 3   # Execute ETH trade"
echo ""
echo "============================================================"
