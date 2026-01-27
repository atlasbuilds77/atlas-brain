# Pigeon Trading Setup - Status

**Updated:** 2026-01-26 3:51 PM PST

## Current Status: ⏳ WAITING FOR WALLET

### What I Did:
1. ✅ Added Pigeon MCP to Claude Code config (doesn't help Clawdbot though)
2. ✅ Sent message to Pigeon via SMS: +1 (888) 655-8732
3. ⏳ Waiting for reply with wallet address

### Message Sent:
- **To:** +1 (888) 655-8732 (Pigeon SMS)
- **Via:** iMessage (from this session)
- **Content:** "Hi, what's my wallet address?"
- **Time:** 2026-01-26 ~3:45 PM PST

## How Trading Will Work:

**Via SMS (Current Session):**
```
Orion → Atlas (iMessage) → Atlas sends to Pigeon (SMS) → Trade executes
```

**Via Telegram (If Orion switches):**
```
Orion → Atlas (Telegram) → Atlas sends to @pigeon_trade_bot → Trade executes
```

## Next Steps:

1. **Wait for Pigeon reply** with wallet addresses (EVM + Solana)
2. **Fund wallet** - Orion sends USDC/ETH/SOL to those addresses
3. **Start trading** - I send commands to Pigeon on Orion's behalf

## Command Examples (Once Funded):

```
"Swap 100 USDC for SOL on Base"
"Long BTC 5x leverage"
"What's my portfolio worth?"
"Buy $50 YES on Bitcoin hitting $100k"
```

## Integration Type:

**NOT MCP-based** (that doesn't work with Clawdbot)
**Instead:** SMS/Telegram bot messaging
- Simpler
- More reliable
- No auth headaches

## Security Notes:

- Pigeon uses Privy (Stripe) MPC wallets
- Self-custodial (can export keys)
- Export URL: https://pigeon.trade/privy
- Start with small amounts ($50-100)
- Export keys immediately after funding

---

**Current Limitation:** Cross-channel messaging blocked (see memory/tools/messaging-limitations.md)
