#!/bin/bash
# Start Drift Gateway for automated trading
set -e

echo "============================================================"
echo "DRIFT GATEWAY - AUTOMATED TRADING SERVER"
echo "============================================================"

# Convert keypair to base58 seed
KEYPAIR_PATH="/Users/atlasbuilds/clawd/drift-bot/.secrets/solana-keypair.json"

# Get the keypair bytes and convert to base58
SEED=$(cat $KEYPAIR_PATH | jq -r 'tostring')

# Export environment
export DRIFT_GATEWAY_KEY="$KEYPAIR_PATH"
export RUST_LOG=info

# Run gateway with Docker
docker run \
  -e DRIFT_GATEWAY_KEY="$DRIFT_GATEWAY_KEY" \
  -e RUST_LOG=info \
  -p 8080:8080 \
  --platform linux/x86_64 \
  ghcr.io/drift-labs/gateway \
  https://mainnet.helius-rpc.com/?api-key=54396175-9f9a-418c-b936-2495159cdd0a \
  --host 0.0.0.0 \
  --markets eth-perp,sol-perp

echo ""
echo "Gateway running on http://localhost:8080"
echo "API docs: https://drift-labs.github.io/v2-teacher/"
