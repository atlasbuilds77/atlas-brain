# Drift Protocol - ARCHIVED

**Status:** Shelved indefinitely (Jan 26, 2026)

## Why Archived:
- Solana RPC connections consistently failing
- Multiple endpoints timing out (mainnet-beta, projectserum, ankr)
- Can't verify positions or execute trades
- Too unreliable for production use

## What Was Built:
- ✅ Full TypeScript wrapper for Drift Protocol
- ✅ Position checker scripts
- ✅ Trading interface (open/close positions)
- ❌ **Critical blocker:** RPC infrastructure broken

## If We Return:
**Location:** `~/clawd/drift-bot/`
**Issue:** Need reliable Solana RPC endpoint or wait for network stability
**Alternative:** Use Pigeon MCP (works around RPC issues)

## Lessons:
- Direct blockchain integration = infrastructure headaches
- MCP-based solutions > DIY RPC management
- Keeper models (Jupiter) unreliable for small sizes
- Drift itself works, Solana RPC doesn't

---
*Archived: 2026-01-26 3:45 PM PST*
