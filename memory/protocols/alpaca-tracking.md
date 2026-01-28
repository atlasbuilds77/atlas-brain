# Alpaca Trade Tracking Protocol

## THE PROBLEM (2026-01-26)
Lost track of three options trades. Didn't log them in real-time. Had to reconstruct from API calls hours later during conversation with Orion + Carlos.

## THE FIX

### 1. LOG TRADES IMMEDIATELY
When Orion executes ANY trade via Alpaca CLI:
- **Update active-positions.md** with entry details IMMEDIATELY
- **Update journal.md** with thesis + entry price
- Don't wait, don't delay, log it NOW

### 2. CHECK POSITIONS REGULARLY
Every few hours during market hours:
```bash
cd ~/clawd/atlas-trader && node cli.js positions
```
If positions closed → get fill details and update memory

### 3. GET FILL DATA WHEN TRADES CLOSE
```bash
cd /Users/atlasbuilds/clawd/atlas-trader && node -e "
import('./src/alpaca.js').then(async (alpaca) => {
  const activities = await alpaca.getActivities('FILL', 20);
  activities.forEach(a => {
    console.log(JSON.stringify({
      symbol: a.symbol,
      side: a.side,
      qty: a.qty,
      price: a.price,
      date: a.transaction_time
    }, null, 2));
  });
});
"
```

This gives exact fill prices for P&L calculation.

### 4. CALCULATE P&L CORRECTLY
**Options P&L Formula:**
```
P&L = (Exit Price - Entry Price) × 100 × Contracts
```

**Example:**
- Buy 1 contract @ $51.25 = $5,125.00
- Sell 1 contract @ $42.80 = $4,280.00
- P&L = ($42.80 - $51.25) × 100 × 1 = -$845.00

**For multiple contracts:**
- Buy 5 contracts @ $0.10 = $50.00
- Sell 5 contracts @ $0.07 = $35.00
- P&L = ($0.07 - $0.10) × 100 × 5 = -$15.00

### 5. UPDATE FILES IN THIS ORDER
1. **active-positions.md** - Move from OPEN to CLOSED section
2. **journal.md** - Add P&L, lesson learned
3. **CURRENT_STATE.md** - Update portfolio summary if needed

### 6. WHEN SPAWN EBADF HITS
- Update memory FIRST with pending check details
- Restart gateway: `gateway.restart()`
- Come back and finish the check

## NEVER AGAIN
If Orion asks "what positions do I have?" and I don't know → I FAILED.

Track trades in real-time. No exceptions.

---

*Created after 2026-01-26 tracking failure*
