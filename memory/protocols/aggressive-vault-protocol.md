# AGGRESSIVE VAULT PROTOCOL
**Created:** 2026-02-03 08:21 PST
**Reason:** Crashes losing context - need faster recovery

---

## AUTO-SAVE TRIGGERS

Save to vault IMMEDIATELY after:
1. **Any trade entry** - symbol, strike, contracts, entry price
2. **Any trade exit** - exit price, P/L, account balance
3. **Any significant discovery** - API fixes, new capabilities
4. **Every 30 minutes** during active sessions
5. **Before any complex operation** - quick state snapshot

---

## QUICK-SAVE FORMAT

File: `memory/vault/YYYY-MM-DD-QUICK-SAVE-HH-MM.md`

```
# QUICK SAVE - [TIME]

## ACTIVE POSITIONS
- [Symbol]: [Qty] @ [Entry] | Current: [Price] | P/L: [Amount]

## ACCOUNT BALANCES
- Webull: $[amount] (BP: $[amount])
- Alpaca: $[amount] (BP: $[amount])

## RECENT TRADES
- [Time]: [Action] [Symbol] @ [Price] = [Result]

## PENDING TASKS
- [Task 1]
- [Task 2]

## KEY CONTEXT
- [Important thing to remember]
```

---

## RECOVERY PROCEDURE

On session start or after crash:
1. Read latest vault file
2. Check account balances (live)
3. Check positions (live)
4. Resume where left off

---

## HEARTBEAT INTEGRATION

Add to HEARTBEAT.md check:
- "When was my last quick save?"
- If >30 min, trigger save immediately

---

**Goal: Never lose more than 30 minutes of context** ⚡
