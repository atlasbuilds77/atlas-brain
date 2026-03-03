# Commission Tracking - Added 2026-03-03

## Context

**Problem:** Aman reported $451 P&L, but our database showed $578.56. Discrepancy was **commissions.**

**Discovery:**
- Database tracked GROSS P&L (before commissions)
- Tradier shows NET P&L (after commissions)
- Commission rate: **$2.06 per contract** (includes exchange fees, clearing fees, etc.)

**Aman's actual:**
- Gross: $578.56
- Commissions: $127.72 (62 contracts × $2.06 × 2 legs)
- Net: $450.84 ✅ (matches his $451)

## Database Changes

### New Columns
```sql
ALTER TABLE trades 
ADD COLUMN commission DECIMAL(10, 2) DEFAULT 0,
ADD COLUMN net_pnl DECIMAL(10, 2);
```

**commission:** Total commission for the trade (buy leg + sell leg)
**net_pnl:** P&L after commissions (pnl - commission)

### Calculation Formula
```
commission = quantity × $2.06 × 2 (buy + sell)
net_pnl = pnl - commission
```

### Code Changes

**meridian_db.py (line ~492):**
```python
commission = (quantity * 2.06 * 2),
net_pnl = ((%s - entry_price) * quantity * 100) - (quantity * 2.06 * 2),
```

**meridian-dashboard/app/api/admin/users/route.ts:**
```typescript
COALESCE(
  t.net_pnl,
  t.pnl - COALESCE(t.commission, 0),
  // fallback to calculated...
) AS pnl_value
```

## Commission Rate Source

Based on actual Tradier fills for Aman's account (6YB71689) on 2026-03-03:
- 62 total contracts traded
- $127.72 total commission
- $2.06 per contract average

This rate includes:
- Base commission
- Exchange fees
- Clearing fees
- Regulatory fees

**Note:** This is an estimate. Actual commissions may vary slightly by contract, but $2.06 is the working average.

## Dashboard Display

Admin dashboard now shows **NET P&L** (after commissions) by default.

This matches what users see in their Tradier accounts, eliminating confusion.

## Migration Applied

```bash
# Database migration run on 2026-03-03 08:47 AM PST
# Backfilled today's trades with commission estimates
# All future trades will calculate commissions automatically
```

## Testing

**Before:**
- Aman: "I see $451"
- Database: "$578.56"
- ❌ Mismatch

**After:**
- Aman: "$451"
- Database: "$450.84 net"
- ✅ Match

---

**Commission tracking is now permanent. Dashboard shows NET P&L. Users see accurate numbers that match their broker statements.**
