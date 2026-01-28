# JUPITER POSITION CHECK - COMPLETE PROTOCOL

## THE WINNING APPROACH ✅

**Use browser tool with clawd profile** - this is the most reliable method.

## STEP-BY-STEP PROCESS

### 1. Check Available Tabs
```bash
browser tabs --profile clawd
```

Look for Jupiter tab (title contains "Jupiter" or URL is jup.ag/perps)

### 2. Take Snapshot of Jupiter Tab
```bash
browser snapshot --profile clawd --targetId <JUPITER_TAB_ID>
```

This gives you the full UI tree with all position data visible.

### 3. Dismiss Any Popups
If there's a terms/conditions popup:
```bash
browser act --profile clawd --targetId <TAB_ID> --request '{"kind": "click", "ref": "e29"}'
```

Find the "Accept" button ref from the snapshot.

### 4. Screenshot for Visual Confirmation
```bash
browser screenshot --profile clawd --targetId <TAB_ID>
```

### 5. Extract Position Data from Snapshot

Look for these keys in the snapshot text:
- **P&L:** Look for "+$X.XX (+X.XX%)" or "-$X.XX"
- **Entry Price:** "$X,XXX.XX"
- **Mark Price:** Current price
- **Liq. Price:** Liquidation price
- **Size:** Position size in ETH + USD value
- **Collateral:** Collateral amount in SOL
- **Value:** Current position value

## EXAMPLE OUTPUT (WORKING)

From snapshot on 2026-01-26 22:36 PST:

```
ETH 3.00x Long Position:
- P&L: +$0.47 (+1.52%)
- Value: $31.17
- Entry Price: $2,911.34
- Mark Price: $2,926.13
- Liq. Price: $1,948.99
- Size: $92.47 (0.03176088 ETH)
- Collateral: $30.82 SOL
```

## FALLBACK: PEEKABOO (If Browser Fails)

Only use if browser tool is unavailable or Jupiter is in Safari/Chrome outside clawd profile.

### Peekaboo Steps:
1. Find Jupiter window: `peekaboo list windows --app Safari`
2. Capture with annotations: `peekaboo see --app Safari --window-title "Jupiter" --annotate --path /tmp/jup.png`
3. Click elements: `peekaboo click --app Safari --on elem_XX`
4. Fallback to screencapture: `/usr/sbin/screencapture -x /tmp/screen.png`

**Limitations:**
- Peekaboo had intermittent Swift continuation errors
- Can't easily interact with automated browser (clawd profile)
- Read-only unless you can reliably click elements

## CRITICAL LESSONS LEARNED

### ✅ DO:
- Use browser tool with clawd profile first
- Check snapshot text for position data (it's all there)
- Dismiss popups before trying to interact
- Use targetId to keep working on same tab

### ❌ DON'T:
- Assume position data from memory (knowledge cutoff)
- Try to navigate via Chrome extensions (they block)
- Rely on Peekaboo as primary method (unstable)
- Use browser Chrome profile without attaching tab first

## WHEN TO CHECK

- User asks for position status
- Heartbeat includes position monitoring
- Before making trade decisions
- When P&L thresholds need verification

## RISK MANAGEMENT INTEGRATION

After getting live data:
- Check if position P&L <= -$50 (size down to $25)
- Verify liquidation price safety margin
- Track daily total P&L across all platforms
- Update memory/trading/active-positions.md

---

**Last updated:** 2026-01-26 10:37 PM PST  
**Verified working:** 2026-01-26 session  
**Method:** browser tool + clawd profile + snapshot parsing
