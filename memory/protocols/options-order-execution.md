# Options Order Execution Protocol

## CRITICAL RULE: NEVER USE MARKET ORDERS ON OPTIONS

### Why Market Orders Are Dangerous
- **Instant slippage** - you'll always get the worst price (ask for buys, bid for sells)
- Wide spreads on options = instant 5-20% loss
- Example: Option bid $0.05 / ask $0.06:
  - Market buy → filled at $0.06 (ask)
  - Instantly down to $0.05 bid
  - **Immediate -16.7% loss from spread alone**

### ALWAYS Use Limit Orders at Mid-Price

**FORMULA:**
```
Mid-Price = (Bid + Ask) / 2
```

**STEPS:**
1. Get quote (bid/ask)
2. Calculate mid-price
3. Place LIMIT order at mid
4. Wait for fill (or adjust if not filling)

**EXAMPLE:**
```bash
# Get quote
node cli.js quote SPY260127C00697000
# Returns: Bid $0.05 | Ask $0.06

# Calculate mid
Mid = (0.05 + 0.06) / 2 = 0.055 → round to 0.06

# Place limit order
node cli.js buy SPY260127C00697000 2 limit 0.06
```

## 0-1 DTE Strategy

### **CRITICAL: TIME OF DAY MATTERS**

**Market Hours (PST):**
- Open: 6:30 AM
- Close: 1:00 PM
- Power Hour: 12:00-1:00 PM

**DTE Selection by Time:**
- **Before 11:00 AM:** 0DTE is fine (2+ hours to expiry)
- **11:00 AM - Close:** Use 1DTE (0DTE theta is brutal)
- **After Close:** Always 1DTE+ for next day

**Why:** 0DTE options lose value FAST in the last hour from theta decay. Even if your thesis is right, you'll get killed by time.

### Finding Short-Dated Options
```bash
# Default search is 30-180 DTE
node cli.js options SPY call

# For 0DTE (if before 11 AM)
node cli.js options SPY call 0 0

# For 1DTE (afternoon/next day)
node cli.js options SPY call 1 1
```

### Strike Selection for 0-1 DTE
- **ATM** = high delta, expensive, needs small move
- **0.1-0.5% OTM** = sweet spot for intraday moves
- **>1% OTM** = lottery tickets, wide spreads, low delta

### Example: SPY @ $696.26
- $696C = ATM
- $697C = 0.1% OTM ✅ (good balance)
- $698C = 0.25% OTM (wider spreads, lower probability)
- $700C = 0.5% OTM (lottery ticket)

## Code Snippets

### Get Mid-Price Quote
```javascript
cd ~/clawd/atlas-trader && node -e "
const alpaca = require('./src/alpaca.js');
(async () => {
  const quote = await alpaca.getOptionQuote('SYMBOL');
  const q = quote.quotes?.SYMBOL;
  if (q) {
    const bid = q.bp;
    const ask = q.ap;
    const mid = ((bid + ask) / 2).toFixed(2);
    console.log(\`Bid: \$\${bid} | Ask: \$\${ask} | Mid: \$\${mid}\`);
  }
})();
"
```

### Find Strikes Near Current Price
```javascript
cd ~/clawd/atlas-trader && node -e "
const alpaca = require('./src/alpaca.js');
(async () => {
  const params = {
    underlying_symbols: 'SPY',
    expiration_date: '2026-01-27',  // 0DTE
    type: 'call',
    strike_price_gte: 690,
    strike_price_lte: 705,
    limit: 50
  };
  const result = await alpaca.getOptionsContracts(params);
  for (const c of result.option_contracts || []) {
    console.log(\`\${c.symbol}: \${c.strike_price} | OI: \${c.open_interest}\`);
  }
})();
"
```

## Mistakes to Avoid
1. ❌ Market orders (instant slippage)
2. ❌ Ignoring spread (wide spread = low liquidity)
3. ❌ Wrong expiry (default search shows 30+ DTE)
4. ❌ Too far OTM on 0DTE (need realistic move)

## Best Practices
1. ✅ Always calculate mid-price
2. ✅ Use limit orders
3. ✅ Check open interest (higher = tighter spreads)
4. ✅ Match expiry to thesis (0-1 DTE for intraday, longer for swings)
5. ✅ Start small on 0DTE (high risk, fast decay)

---

*Created: 2026-01-27 12:18 PST*
*Lesson learned from SLV market order slippage (-6% instant)*
