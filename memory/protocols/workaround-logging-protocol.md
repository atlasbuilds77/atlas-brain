# Workaround Logging Protocol

## Created: 2026-01-26
## Purpose: Remember solutions to recurring blockers

---

## THE RULE

**When I hit a blocker and we find a workaround, LOG IT immediately so I use the workaround next time instead of repeating the same failure.**

---

## THE PROCESS

### When I Can't Do Something:
1. **Try the obvious approach**
2. **If it fails, note the error**
3. **We figure out a workaround together**
4. **LOG THE WORKAROUND** in this file or a topic-specific memory file

### What to Log:
- **Problem:** What I tried to do
- **Blocker:** What failed and why
- **Workaround:** What actually worked
- **When to Use:** Next time this comes up, skip the blocker and go straight to the workaround

---

## ACTIVE WORKAROUNDS

### 1. Exec Spawn Errors (EBADF)

**Problem:** Need to run shell commands
**Blocker:** `exec` tool returns "spawn EBADF" errors
**Workaround:** Use `sessions_spawn` to delegate the command to a Spark
**When to Use:** Any time exec fails with spawn errors

**Example:**
```
❌ exec("tailscale ip -4") → spawn EBADF
✅ sessions_spawn(task="Run tailscale ip -4 and report back")
```

**Added:** 2026-01-26

---

### 2. Browser Screenshot Issues

**Problem:** Need to capture browser screenshots
**Blocker:** Browser tool keeps returning "404: tab not found" even when tabs exist
**Workaround:** 
- ✅ **Best:** Use Peekaboo: `peekaboo image --mode frontmost --path /tmp/screenshot.png`
  - Open content in Safari/browser first
  - Use `--mode frontmost` to capture active window (better than `--app Safari --mode window`)
- Option B: Host HTML file and let user screenshot on their device
- Option C: Spawn a Spark with fresh browser session

**When to Use:** When browser screenshot fails repeatedly

**Added:** 2026-01-26
**Updated:** 2026-01-26 (confirmed Peekaboo frontmost mode works best)

---

## WHY THIS MATTERS

- **Saves time** - Don't repeat failed approaches
- **Looks competent** - I learn from experience
- **Builds patterns** - Document what actually works
- **Faster execution** - Go straight to the working solution

---

### 3. Jupiter Position Check Workflow

**Problem:** Need to check live positions on Jupiter Perps with Phantom wallet
**Solution:** Use Peekaboo to control regular Chrome (not browser tool)

**Complete Workflow:**
1. **Open Chrome with Jupiter:**
   - Spawn a Spark to handle: `open -a "Google Chrome" "https://jup.ag/perps/long/SOL-ETH"`
   - Or use Peekaboo directly if exec works

2. **Use Peekaboo for UI automation:**
   - `peekaboo see --app "Google Chrome"` - Get element IDs
   - Find "Connect" button element ID (e.g., elem_24)
   - `peekaboo click --on elem_24 --app "Google Chrome"`

3. **Connect Phantom wallet:**
   - After clicking Connect, modal appears with wallet options
   - `peekaboo see --app "Google Chrome"` again
   - Find Phantom button element ID
   - `peekaboo click --on [phantom_elem_id] --app "Google Chrome"`

4. **Capture position data:**
   - Wait 2-3 seconds for position to load
   - `peekaboo image --app "Google Chrome" --mode window --path /tmp/jupiter-position.png`
   - Use `image` tool to extract: Entry, Current, P&L, Size, Liquidation

5. **Extract with vision:**
   ```
   image(/tmp/jupiter-position.png, "Extract Jupiter position: Entry price, Current price, P&L, Size, Liquidation price")
   ```

**Key Points:**
- Use **regular Chrome** (has Phantom extension), not browser tool or isolated browser
- Use **Peekaboo** for UI automation, not browser tool
- Wallet address: 28Gv5ncMyeS5oHYgsBd9r857dpvRKqw5ttc1nKN6UxXj
- Credentials: /Users/atlasbuilds/clawd/.secrets/solana-keypair.json

**When to Use:** Every position check (scheduled or on-demand)

**Added:** 2026-01-26

---

## ADDING NEW WORKAROUNDS

When we solve a problem, add it here:
```markdown
### [Number]. [Problem Name]

**Problem:** What I was trying to do
**Blocker:** What failed
**Workaround:** What worked
**When to Use:** When to apply this workaround

**Added:** YYYY-MM-DD
```

---

## REVIEWING WORKAROUNDS

**Monthly:** Review this file and see if:
- The blocker is now fixed (remove workaround)
- The workaround can be improved
- New patterns emerged

**Session Start:** Check this file if I hit a familiar blocker

---

*When something doesn't work, we don't just move on - we log the fix so I'm smarter next time.*
