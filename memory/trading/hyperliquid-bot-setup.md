# Crypto Scalping Bot Setup

**Status:** READY - Awaiting SOL funding from Orion
**Created:** 2026-01-25
**Location:** ~/clawd/drift-bot/ (Python 3.12)
**Platform:** Drift Protocol (Solana) - cheaper than Arbitrum!

## Solana Wallet (PRIMARY)
- **Address:** `7UKP7mofxSk6mn4z4jQNNE7HZSdXTPkMY8VKypZcrafx`
- **Network:** Solana Mainnet
- **Keypair:** `.secrets/solana-keypair.json`
- **Seed:** `.secrets/wallet-solana.json`

## Old Arbitrum Wallet (Backup)
- **Address:** `0x623F14f26eF7D912fbB177987A57047dc68b5C4E`
- **Network:** Arbitrum (for Hyperliquid)
- **Private Key:** `.secrets/wallet.json`

## Bot Files
- `scalper.py` - Main scalping bot
- `.secrets/wallet.json` - Wallet credentials (gitignored)
- `bin/` - Python venv with hyperliquid-python-sdk

## Current Config
- Symbol: BTC
- Leverage: 5x (conservative start)
- Position Size: $100
- Take Profit: 0.5%
- Stop Loss: 0.3%
- Mode: PAPER (testnet)

## To Fund
1. Send USDC to wallet address on Arbitrum
2. Need small ETH for gas (~$5 worth)
3. Deposit USDC to Hyperliquid via their bridge

## To Run
```bash
cd ~/clawd/hyperliquid-bot
source bin/activate
python3 scalper.py
```

## Next Steps
- [ ] Fund wallet with USDC on Arbitrum
- [ ] Test paper trading on testnet
- [ ] Refine strategy based on results
- [ ] Go live with small size
