# JUPITER POSITION CHECK - AUTOMATED PROTOCOL ✅

**Status:** PRODUCTION READY  
**Last Updated:** 2026-01-27 8:43 PM PST  
**Method:** Direct Solana RPC queries via Anchor + Jupiter Perps IDL

---

## THE PROBLEM (SOLVED)

❌ **OLD METHOD:** Browser tool with manual Chrome extension connection  
- Required manual tab attachment  
- Didn't work in automated cron jobs  
- Data went stale for 15+ hours  

✅ **NEW METHOD:** Direct blockchain queries via Node.js  
- NO browser required  
- NO manual intervention  
- Works perfectly in cron jobs  
- Gets live on-chain data every time  

---

## HOW IT WORKS

### 1. Query Solana Blockchain Directly
```bash
cd scripts && node jupiter-position-check-v2.js
```

The script:
1. Connects to Solana RPC (Mainnet)
2. Queries Jupiter Perpetuals Program accounts
3. Filters for wallet address: `28Gv5ncMyeS5oHYgsBd9r857dpvRKqw5ttc1nKN6UxXj`
4. Decodes position data using Anchor IDL
5. Fetches current prices from CoinGecko API
6. Calculates P&L
7. Writes results to `memory/trading/jupiter-positions-latest.md`

### 2. Output Format
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

## CRON JOB CONFIGURATION

**Job ID:** `4d329d5f-ea6b-4bc7-9920-6dba45a7605d`  
**Name:** Position Check - All Platforms  
**Schedule:** Every 15 minutes  
**Payload:**

```
POSITION CHECK: Run automated position check using Node.js script. 
Execute: cd scripts && node jupiter-position-check-v2.js. 
This queries Jupiter Perps positions directly from Solana blockchain (no browser needed). 
Output written to memory/trading/jupiter-positions-latest.md. 
Check P&L and report if any position is down >5% or approaching liquidation. 
Risk limits: If position P&L <= -$50, recommend closing or sizing down. 
Daily loss cap $100 total. 
This method works 100% automatically in cron jobs.
```

---

## RISK MANAGEMENT ALERTS

Trigger alerts when:

1. **P&L <= -5%** - Yellow flag, monitor closely
2. **P&L <= -$50** - Red flag, consider closing or sizing down to $25
3. **Price within 10% of liquidation** - URGENT, close position
4. **Daily total loss >= $100** - STOP trading for the day

---

## DEPENDENCIES

Required packages (already installed in `scripts/`):
```json
{
  "@coral-xyz/anchor": "^0.29.0",
  "@solana/web3.js": "^1.95.3"
}
```

Required files:
- `scripts/jupiter-position-check-v2.js` - Main script
- `scripts/jupiter-perps-idl.json` - Jupiter Perpetuals IDL
- `scripts/package.json` - NPM dependencies

---

## TESTING

Run the test script to verify everything works:
```bash
cd scripts && ./test-position-check.sh
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

## TROUBLESHOOTING

### Error: Cannot find module '@coral-xyz/anchor'
```bash
cd scripts && npm install
```

### Error: jupiter-perps-idl.json not found
```bash
cp /tmp/jupiter-perps-idl.json scripts/
```

### Error: RPC rate limit
Set custom RPC URL:
```bash
export SOLANA_RPC_URL="https://your-premium-rpc-url.com"
node jupiter-position-check-v2.js
```

### Error: Position not found
- Check wallet address is correct: `28Gv5ncMyeS5oHYgsBd9r857dpvRKqw5ttc1nKN6UxXj`
- Verify position is still open (not closed)
- Check on Solscan: https://solscan.io/account/28Gv5ncMyeS5oHYgsBd9r857dpvRKqw5ttc1nKN6UxXj

---

## KEY ADVANTAGES

✅ **100% Automated** - No manual steps  
✅ **Works in Cron** - Perfect for scheduled checks  
✅ **Live Data** - Always fresh from blockchain  
✅ **No Browser** - No extension setup required  
✅ **Fast** - Completes in 2-3 seconds  
✅ **Reliable** - Direct RPC queries, no UI scraping  
✅ **Portable** - Works on any machine with Node.js  

---

## WHEN TO USE

- ✅ **Automated cron jobs** (every 15 min)
- ✅ **Quick position checks** from command line
- ✅ **Heartbeat monitoring**
- ✅ **Risk management alerts**

## WHEN NOT TO USE

- ❌ Opening/closing positions (use browser tool for that)
- ❌ Viewing charts (use browser)
- ❌ Changing leverage/TP/SL (use browser)

This is READ-ONLY for monitoring. For trading actions, use the browser tool.

---

## MIGRATION FROM OLD METHOD

**Old protocol:** `memory/protocols/jupiter-position-check-complete.md`  
**Status:** DEPRECATED (browser method)  
**Reason:** Requires manual Chrome extension connection  

**New protocol:** `memory/protocols/jupiter-position-check-automated.md` (this file)  
**Status:** ACTIVE  
**Reason:** Fully automated, cron-friendly  

---

**Last verified working:** 2026-01-27 8:43 PM PST  
**Test command:** `cd scripts && ./test-position-check.sh`  
**✅ PRODUCTION READY**
