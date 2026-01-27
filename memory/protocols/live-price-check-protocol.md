# Live Price Check Protocol

**Created:** 2026-01-26 after SOL price assumption mistake
**Purpose:** Never trade on stale/assumed prices

---

## THE PROBLEM

Assumed SOL was ~$240 (from old memory) when it's actually $123. 
Knowledge cutoff = April 2024. All price memory is STALE.

---

## THE RULE

**BEFORE ANY TRADE CALCULATION, ALWAYS:**

1. Check live price via API
2. Show the result
3. Use that number for calculations
4. Never assume from memory

---

## IMPLEMENTATION

### Crypto Prices (MANDATORY)
```bash
# SOL price
curl -s "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"

# Multiple coins
curl -s "https://api.coingecko.com/api/v3/simple/price?ids=solana,bitcoin,ethereum&vs_currencies=usd"

# Show the output, use the number
```

### Stock Prices (MANDATORY)
```bash
# Via Alpaca
cd ~/clawd/atlas-trader && node cli.js quote SYMBOL

# Show the quote, verify price before calculating
```

### Kalshi Markets (MANDATORY)
```bash
# Get current market price/odds
cd ~/clawd && source .venv/bin/activate
export KALSHI_API_KEY_ID="0007b9f0-89c9-42b4-93bd-f98fbf1596b8"
python tools/kalshi-trader.py markets "search term"

# Check current price before entering
# Don't assume odds from memory or old data
```

### Before EVERY trade (ANY platform):
- ✅ Check live price/odds
- ✅ Show the price check output
- ✅ Calculate position size with fresh data
- ✅ Verify account balance
- ❌ NEVER assume from memory
- ❌ NEVER say "SOL is around $X" without checking
- ❌ NEVER say "Kalshi odds are Y%" without checking
- ❌ NEVER say "Stock is trading at $Z" without checking

### Applies to:
- Crypto (Solana, Bitcoin, ETH, etc.)
- Stocks (Alpaca paper/live trading)
- Kalshi (prediction markets)
- Options (strike prices, underlying prices)
- ANY asset with a price

---

## CONSEQUENCES OF BREAKING THIS

- Wrong position sizing = blown account
- Wrong risk calculations = unexpected losses
- Lost credibility
- Real money at stake

---

## VERIFICATION CHECKLIST

Before entering ANY trade:
- [ ] Live price checked
- [ ] Price shown in output
- [ ] Calculations based on live data
- [ ] Position size verified
- [ ] Risk calculated correctly

---

*Self-evolving: Price assumption = potential disaster. Always check live.*
