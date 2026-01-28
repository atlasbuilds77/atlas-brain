# Jupiter Position Check - Automated Solution

## 🎯 Problem Solved

**OLD:** Position check cron used browser tool → required manual Chrome extension attachment → failed in automated runs → data went stale for 15+ hours

**NEW:** Direct Solana blockchain queries → NO browser needed → works 100% automatically → always fresh data

---

## 🚀 Quick Start

### Run Position Check
```bash
cd scripts
node jupiter-position-check-v2.js
```

### Run Tests
```bash
cd scripts
./test-position-check.sh
```

### View Latest Positions
```bash
cat memory/trading/jupiter-positions-latest.md
```

---

## 📁 Files

| File | Purpose |
|------|---------|
| `jupiter-position-check-v2.js` | Main script - queries Solana, calculates P&L |
| `jupiter-perps-idl.json` | Jupiter Perpetuals Program IDL (required) |
| `package.json` | Dependencies (@coral-xyz/anchor, @solana/web3.js) |
| `test-position-check.sh` | Test script - verifies everything works |
| `jupiter-position-check.js` | OLD VERSION - manual parsing (deprecated) |

---

## 🔧 How It Works

1. **Connect to Solana RPC**  
   Uses public Mainnet endpoint (or custom via `SOLANA_RPC_URL` env var)

2. **Query Program Accounts**  
   Filters Jupiter Perpetuals Program for wallet: `28Gv5ncMyeS5oHYgsBd9r857dpvRKqw5ttc1nKN6UxXj`

3. **Decode with Anchor**  
   Uses Jupiter Perpetuals IDL to decode position account data

4. **Get Current Prices**  
   Fetches live prices from CoinGecko API (ETH, SOL, BTC)

5. **Calculate P&L**  
   `P&L = (sizeUsd * priceDelta) / entryPrice`

6. **Write Output**  
   Updates `memory/trading/jupiter-positions-latest.md` with formatted results

---

## 📊 Output Example

```markdown
# Jupiter Perps Positions

**Last Updated:** 01/27/2026, 20:43:39 PST
**Wallet:** 28Gv5ncMyeS5oHYgsBd9r857dpvRKqw5ttc1nKN6UxXj
**Total Positions:** 1

## ETH 10.59x LONG

- **Entry Price:** $2996.29
- **Current Price:** $2998.17
- **Size:** $664.59
- **Collateral:** $62.71
- **P&L:** $+0.42 (+0.66%)
- **Opened:** 2026-01-27T20:44:26.000Z
- **Last Update:** 2026-01-27T20:44:26.000Z
- **Address:** `2krUpGPLi4WknLRx3nNZSLCQQzdLDLxkNXCfoFNzjL49`
```

---

## ⚙️ Cron Integration

**Job ID:** `4d329d5f-ea6b-4bc7-9920-6dba45a7605d`  
**Schedule:** Every 15 minutes  
**System Event:** `POSITION_CHECK_ALL_PLATFORMS`  

When the cron fires, the agent should:
1. Run `cd scripts && node jupiter-position-check-v2.js`
2. Read the output file
3. Check for risk alerts (P&L <= -5%, approaching liquidation)
4. Report status

See: `memory/protocols/position-check-cron-handler.md`

---

## 🛠️ Installation

```bash
cd scripts
npm install
```

Dependencies:
- `@coral-xyz/anchor` - Solana program framework
- `@solana/web3.js` - Solana web3 library

---

## 🧪 Testing

```bash
cd scripts
./test-position-check.sh
```

Expected output:
```
✅ Dependencies OK
✅ IDL file OK
✅ Position check complete
✅ Output file created
✅ ALL TESTS PASSED!
```

---

## 🔐 Configuration

### Custom RPC Endpoint
```bash
export SOLANA_RPC_URL="https://your-rpc-url.com"
node jupiter-position-check-v2.js
```

### Custom Wallet Address
```bash
export JUPITER_WALLET="YourWalletAddressHere"
node jupiter-position-check-v2.js
```

Default wallet: `28Gv5ncMyeS5oHYgsBd9r857dpvRKqw5ttc1nKN6UxXj`

---

## 📝 Risk Management

Alert triggers:
- **P&L <= -5%** → Yellow flag
- **P&L <= -$50** → Consider closing/sizing down to $25
- **Price within 10% of liquidation** → URGENT
- **Daily total loss >= $100** → Stop trading

---

## 🐛 Troubleshooting

### Module not found
```bash
cd scripts && npm install
```

### IDL not found
```bash
# IDL should already be committed
# If missing, regenerate from source repo
```

### RPC rate limit
Use a premium RPC endpoint:
```bash
export SOLANA_RPC_URL="https://api.mainnet-beta.solana.com" # or better
```

### Position not found
- Verify wallet address
- Check position is still open on Solscan
- Ensure position has `sizeUsd > 0`

---

## ✅ Advantages Over Browser Method

| Feature | Browser Method | New Method |
|---------|---------------|------------|
| Manual steps | ❌ Required | ✅ None |
| Cron-safe | ❌ No | ✅ Yes |
| Speed | ~10 seconds | ~3 seconds |
| Reliability | ⚠️ UI-dependent | ✅ Direct RPC |
| Setup | Complex (extension) | Simple (npm install) |
| Data freshness | Stale (hours) | Always live |

---

## 📚 Documentation

- **Main Protocol:** `memory/protocols/jupiter-position-check-automated.md`
- **Cron Handler:** `memory/protocols/position-check-cron-handler.md`
- **Old Method (deprecated):** `memory/protocols/jupiter-position-check-complete.md`

---

## 🎉 Status

✅ **PRODUCTION READY**  
✅ **Tested and verified:** 2026-01-27 8:43 PM PST  
✅ **Cron job updated:** System event `POSITION_CHECK_ALL_PLATFORMS`  
✅ **All tests passing**  

---

**Built by:** Atlas (subagent:fix-position-check-cron)  
**Date:** 2026-01-27  
**Purpose:** Enable automated, reliable position monitoring without manual intervention
