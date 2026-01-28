# JUPITER POSITION CHECK - Peekaboo Method

## THE APPROACH

Use Peekaboo to capture Jupiter interface when browser automation fails.

## PROCESS

### 1. Try Browser First
```bash
# Check if Jupiter tab exists in clawd or chrome profile
browser tabs --profile clawd
browser tabs --profile chrome
```

### 2. If Browser Fails, Use Peekaboo
```bash
# List Chrome processes to find Jupiter
peekaboo list apps | grep Chrome

# Capture the active Chrome window
peekaboo see --app "Google Chrome" --annotate --path /tmp/jupiter-check.png

# View the annotated image
read /tmp/jupiter-check_annotated.png
```

### 3. Extract Position Data
From the screenshot, look for:
- Position size (ETH amount and $ value)
- Collateral amount (SOL)
- Current P&L (green/red numbers)
- Liquidation price
- Entry price

### 4. Limitations
- Can't interact with popups via Peekaboo easily
- Automated browser (clawd profile) not visible to Peekaboo
- Best for READ ONLY position checks, not trading actions

## WHEN TO USE

- Browser automation fails (terms popups, connection issues)
- Need quick visual confirmation of position status
- Browser profiles not responding to automation commands

## ALTERNATIVE: Manual Check

If all automation fails, ask user to manually check at jup.ag/perps and report status.

---

Last updated: 2026-01-26 10:25 PM PST
Purpose: Backup method for position monitoring when browser automation unavailable
