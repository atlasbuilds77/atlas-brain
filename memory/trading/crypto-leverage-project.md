# Crypto Leverage Trading Project

**Status:** ACTIVE - Research & Setup Phase
**Started:** 2026-01-25
**Goal:** Automated scalping on crypto perpetuals

## Strategy Approach
- SCALPING style - quick in/out, take profits, rotate
- Don't marry positions
- Target 2-5% moves on leveraged positions
- Trail stops or hard exits when target hits

## Platforms Researched
1. **Hyperliquid** (PRIMARY CHOICE)
   - DEX, non-custodial, no KYC
   - Up to 50x leverage
   - Python SDK: `pip install hyperliquid-python-sdk`
   - Wallet-based auth (not API keys)
   - Rate limit: 1200 weight/minute

2. **Drift Protocol** (Solana option)
   - Up to 101x on SOL/BTC/ETH
   - Python SDK: `pip install driftpy`
   - Good if staying Solana-native

3. **Coinbase CFM** (US Legal)
   - CFTC regulated, up to 10x
   - Lower leverage but fully compliant

## Bot Framework Choice
- **Freqtrade** - Best overall for scalping
- **Passivbot** - Best for perps market-making
- **CCXT** - For custom builds

## Files Created
- hyperliquid_python_sdk_guide.md
- hyperliquid_quick_start.py
- drift_sdk_guide.md
- crypto_scalping_frameworks_comparison.md

## Next Steps
- [ ] Find specific proven strategies
- [ ] Set up Hyperliquid wallet
- [ ] Paper trade first
- [ ] Go live with small size

## Risk Management
- Never risk more than 1-2% per trade
- Always use stop losses
- Don't hold overnight (funding rates)
- Start small, scale up
