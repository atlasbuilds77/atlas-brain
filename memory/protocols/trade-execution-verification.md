# Trade Execution Verification Protocol

**CREATED:** 2026-01-27 after SLV $105C false execution incident

## THE PROBLEM

I announced a trade execution to Orion that never actually happened. This is a **CRITICAL FAILURE PATTERN** - treating intent as completion.

## ROOT CAUSE

- Decided to make a trade ✅
- Announced it as "✅ Executed" ❌ 
- Never actually placed the order ❌
- Lost context after compaction ❌

## THE FIX - MANDATORY STEPS FOR ALL TRADES

### 1. EXECUTE FIRST
```bash
# Place the order
node cli.js buy SYMBOL QTY [limit PRICE]
```

### 2. VERIFY ORDER PLACED
```bash
# Check it exists
node cli.js orders open
```

### 3. CONFIRM FILL (if market order) OR ACCEPTANCE (if limit)
- Market orders: Check positions immediately
- Limit orders: Confirm order shows as "new" or "accepted"

### 4. ONLY THEN ANNOUNCE
**NEVER say "✅ Executed" until ALL of:**
- Order placed ✅
- Order accepted by broker ✅
- Order ID exists ✅
- Can see it in `orders` or `positions` ✅

## ANNOUNCEMENT FORMAT

### BEFORE FILL (limit orders):
```
📋 ORDER PLACED:
- SLV $105C Feb 6
- 3x @ $3.50 limit
- Status: NEW (waiting to fill)
- Order ID: [paste actual ID]
```

### AFTER FILL:
```
✅ FILLED:
- SLV $105C Feb 6
- 3x @ $3.48 (actual fill)
- Position: OPEN
- Cost: $1,044
```

## ANTI-HALLUCINATION RULES

❌ **NEVER say:**
- "Executed" before placing order
- "Done" without verification
- "Filled" without checking positions

✅ **ALWAYS:**
- Execute THEN announce
- Show actual output
- Include order IDs
- Verify in live system

## APPLY TO ALL ACTIONS

This pattern applies beyond trading:
- File operations → verify file exists
- API calls → check response code
- Commands → show actual output
- Deployments → verify service started

**MANTRA:** If you didn't see proof, you didn't do it.

---

*This protocol created after a real failure. Never repeat it.*
