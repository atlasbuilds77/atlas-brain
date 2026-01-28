# Position Check Cron Handler

**System Event:** `POSITION_CHECK_ALL_PLATFORMS`  
**Frequency:** Every 15 minutes  
**Handler:** Main agent  

---

## WHAT TO DO WHEN THIS EVENT FIRES

When you receive the `POSITION_CHECK_ALL_PLATFORMS` system event:

### 1. Run Jupiter Position Check
```bash
cd scripts && node jupiter-position-check-v2.js
```

This automatically:
- Queries on-chain position data
- Calculates current P&L
- Updates `memory/trading/jupiter-positions-latest.md`

### 2. Read the Output
```bash
cat memory/trading/jupiter-positions-latest.md
```

### 3. Check Other Platforms (if applicable)
- **Kalshi:** Read `memory/trading/active-positions.md` (Kalshi section)
- **Alpaca:** Read `memory/trading/active-positions.md` (Alpaca section)

### 4. Risk Assessment
For each position, check:
- **P&L percentage** - Flag if <= -5%
- **Absolute P&L** - Alert if <= -$50
- **Liquidation risk** - Urgent if price within 10% of liq price
- **Daily total** - Stop if total losses >= $100

### 5. Response Format

If all positions are healthy:
```
✅ Position check complete - all systems green
- Jupiter: 1 position, +$X.XX
- Total P&L: +$X.XX
```

If action needed:
```
⚠️ RISK ALERT: Position check requires attention

Jupiter ETH 10x LONG:
- Entry: $3000 | Current: $2850
- P&L: -$50 (-8.5%)
- 📍 ACTION: Consider closing or reducing size to $25

Daily total: -$50 / $100 limit
```

---

## AUTOMATION NOTES

This replaces the old browser-based method that required manual Chrome extension connection.

✅ **Fully automated** - No manual steps  
✅ **Cron-safe** - Works in background  
✅ **Fast** - 2-3 seconds  
✅ **Reliable** - Direct blockchain queries  

---

See full protocol: `memory/protocols/jupiter-position-check-automated.md`
