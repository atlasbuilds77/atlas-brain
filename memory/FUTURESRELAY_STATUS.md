# FuturesRelay - Production Status

## Overview
Multi-tenant TradingView webhook relay for funded futures trading accounts.

**Live URL:** https://futures-relay.onrender.com  
**Repo:** OrionSolana/Futures-relay  
**Owner:** Orion (Nebula-only access via Discord OAuth)

## Current Status: PRODUCTION READY ✅

### Supported Brokers (Live)
1. **TopstepX** ✅
   - Full integration
   - Order placement, positions, account info
   - Setup guides with subscription requirements

2. **Tradovate** ✅ (Completed 2026-01-24)
   - Contract ID resolution (critical fix)
   - Order placement (Market, Limit, Stop, StopLimit)
   - Position tracking with reverse contract lookup
   - Account info + cash balance
   - Order cancellation
   - Token caching (24hr expiry, 5min refresh buffer)

### Locked Brokers (Hidden)
- TradeStation
- NinjaTrader  
- Rithmic

## Recent Major Updates

### 2026-01-24: Tradovate Integration Complete
**Problem:** Template-only code with TODOs, couldn't place orders

**Solution (commit 1389a70):**
- Implemented contract ID resolution (TradingView sends "NQ", Tradovate needs contract ID)
- Complete order placement with proper payload format
- Position fetching with contract reverse lookup
- Account info + buying power
- Order cancellation
- Contract caching to avoid repeated API calls

**Impact:** TradingView webhooks → Tradovate now fully functional

### 2026-01-23: Email/Password Auth
- Email/password registration with one-time Discord verification
- Sessions last 120 days
- Keeps Nebula-only gatekeeper
- Supports legacy Discord-only users

### 2026-01-22: Production Launch Features
- Edit/Delete account functionality
- Test Connection button for TopstepX
- Comprehensive broker setup guides
- PostgreSQL migration (persistent database, no more wipes)
- Improved UX with step-by-step instructions

## Architecture

**Multi-tenant:**
- Discord OAuth (Nebula role required)
- Email/password registration with Discord verification
- PostgreSQL database for persistence
- FastAPI backend
- WebSocket support for TradingView webhooks

**Webhook Flow:**
1. TradingView → POST /webhook/{account_id}
2. FuturesRelay validates user session
3. Resolves contract IDs (for Tradovate)
4. Routes to broker-specific adapter
5. Places order via broker REST API
6. Returns execution result

## Key Files

**Main:** `main.py` (multi-tenant version)  
**Brokers:** `brokers/topstepx.py`, `brokers/tradovate.py`  
**Docs:** WORK_LOG.md, TRADOVATE_INSIGHTS.md, BROKER_SETUP.md  
**Database:** PostgreSQL (managed via Render)

## Common Issues & Solutions

### Tradovate
- **Contract resolution:** Uses `/contract/find` API with caching
- **Token expiry:** 24hr tokens, auto-refresh at 23:55
- **Order format:** Must include contractId (resolved from ticker)

### TopstepX
- **Subscription required:** Active TopstepX subscription needed for API access
- **Account ID:** Can auto-fetch via "Fetch Account ID" button
- **Credentials:** Username + API Key (not password)

## Dev Team
- **Orion:** Owner, product direction
- **Aphmas (Kevin):** Co-founder, QoL improvements, dev bridge
- **Atlas:** Implementation, integration work

## Next Steps (Future)
- WebSocket integration for real-time position updates (Tradovate)
- Market data WebSocket (Tradovate mdAccessToken)
- Additional brokers (TradeStation, NinjaTrader, Rithmic)

---

**Last Updated:** 2026-01-24 13:27 PST  
**Status:** Production-ready, actively used by Nebula members
