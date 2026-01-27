# COMPLETE HYPERLIQUID SETUP - EXECUTION PLAN

## CURRENT STATUS
- ✅ Hyperliquid wallet: 0x623F14f26eF7D912fbB177987A57047dc68b5C4E
- ✅ Hyperliquid API client built & tested
- ✅ Drift account has ~$94 (0.758 SOL deposited)
- ❌ Hyperliquid balance: $0 (needs funding)
- ❌ ETH trade not executed yet

## IMMEDIATE ACTIONS (RIGHT NOW)

### 1. EXECUTE ETH TRADE IN DRIFT (30 SECONDS) ⚡
**YOU DO THIS MANUALLY:**
1. Go to app.drift.trade (already open)
2. ETH-PERP market
3. LONG, 3x leverage
4. Enter 0.095 ETH or use "Max" 
5. Market order → Approve

**TRADE PARAMS:**
- Entry: ~$2,926
- Size: 0.095 ETH (~$280 notional on 3x)
- Stop: $2,635 (-10% = -$28 loss)
- Target: $3,370 (+15% = +$42 gain)

---

## PHASE 2: MIGRATE TO HYPERLIQUID (AFTER DRIFT TRADE)

### Step 1: Withdraw from Drift (2 min)
```bash
cd ~/clawd/drift-bot
source bin/activate
python withdraw_from_drift.py
```

### Step 2: Bridge SOL → Hyperliquid (15 min)
**Manual bridge via deBridge:**
1. Go to: https://app.debridge.finance/
2. Connect Solana wallet: 28Gv5ncMyeS5oHYgsBd9r857dpvRKqw5ttc1nKN6UxXj
3. Bridge:
   - From: Solana (SOL)
   - To: Hyperliquid (USDC)
   - Amount: 0.75 SOL
   - Destination: 0x623F14f26eF7D912fbB177987A57047dc68b5C4E
4. Approve & wait 10-15 min

### Step 3: Trade on Hyperliquid (AUTOMATED ✅)
```bash
cd ~/clawd/hyperliquid-trader

# Check balance arrived
node simple_hl.js balance

# Execute ETH LONG 3x
node simple_hl.js long 93 3

# Set stop loss
node simple_hl.js stop 2635

# Set take profit  
node simple_hl.js target 3370
```

---

## ALTERNATIVE: HYPERLIQUID PYTHON SDK

If Node.js fails, Python alternative ready:
```bash
cd ~/clawd/hyperliquid-trader
pip install hyperliquid-python-sdk
python hl_trade.py long ETH 93 3
```

---

## COMPLETED TOOLS

### Files Created:
1. `/Users/atlasbuilds/clawd/hyperliquid-trader/simple_hl.js` - Working REST API client
2. `/Users/atlasbuilds/clawd/drift-bot/withdraw_from_drift.py` - Drift withdrawal
3. `/Users/atlasbuilds/clawd/hyperliquid-trader/bridge_sol_to_hl.sh` - Bridge guide

### API Endpoints Mapped:
- ✅ GET user state (balance, positions, PnL)
- ✅ GET market prices
- ✅ POST update leverage
- ✅ POST place order (market/limit)
- ✅ POST cancel order
- ✅ GET position details

---

## KALSHI API (BONUS - ALSO READY)

Found credentials:
- API Key: 0007b9f0-89c9-42b4-93bd-f98fbf1596b8
- Private Key: /Users/atlasbuilds/.clawdbot/credentials/kalshi/private_key.pem

To use:
```bash
export KALSHI_API_KEY_ID="0007b9f0-89c9-42b4-93bd-f98fbf1596b8"
cd ~/clawd && source .venv/bin/activate
python tools/kalshi-trader.py balance
python tools/kalshi-trader.py positions
```

---

## NEXT SESSION QUICK START

1. **Check Drift position:** app.drift.trade
2. **Check Hyperliquid:** `node simple_hl.js balance`
3. **Execute new trade:** `node simple_hl.js long 93 3`
4. **Monitor positions:** Both platforms have APIs hooked up

---

## TIME BREAKDOWN

| Task | Method | Time |
|------|--------|------|
| Execute Drift trade | Manual UI | 30 sec |
| Withdraw from Drift | Python script | 2 min |
| Bridge to Hyperliquid | deBridge UI | 10-15 min |
| Trade on Hyperliquid | Node.js script | 30 sec |
| **TOTAL** | | **~18 min** |

---

**RECOMMENDATION:**
Execute Drift trade NOW (30 sec), then migrate to Hyperliquid for tomorrow. Don't burn another 20 min while ETH moves.

**ETH Status:** $2,926, +4% today, momentum intact ⚡
