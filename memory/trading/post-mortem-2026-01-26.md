# Trading Post-Mortem: 2026-01-26

## What Went Wrong

### Alpaca Paper Trading - DISASTER

**Positions Entered (while on GPT/broken models):**
- INTC 55C x5: -$15 (-30%)
- SLV 55C x1: -$830 (-16.2%) ⚠️ 
- USAR 17.5C x1: -$390 (-31.84%)

**Total Loss:** -$1,235

**Starting Balance (simulated):** $500
**Ending Balance:** -$735 (blew account + $235 more)

### Critical Mistakes

#### 1. Position Sizing DISASTER
- SLV position cost $5,125 - **10x the account size**
- Should have been max $150 per position (30% of $500)
- No position size checks implemented

#### 2. Bad Model Execution
- These trades entered while Atlas was on GPT
- GPT doesn't understand risk management
- No verification of position sizes before entry

#### 3. No Risk Management
- No stop losses
- No position size limits
- Ignored the $500 simulation rule

#### 4. Options Selection
- INTC expired in 11 days - too short
- SLV strike $55 on $29 underlying - way OTM
- USAR strike $17.5 on $12 underlying - also OTM

### Crypto - Never Happened

- Tried to swap wSOL → USDC on Jupiter
- Phantom wallet automation failed
- Swap never executed
- 0.18 SOL (~$43) still sitting in wallet

## Lessons Learned

### Position Sizing Rules (MANDATORY)

For $500 account:
- Max per position: $150 (30%)
- Max per sector: $300 (60%)
- Keep 20% cash buffer: $100

### Options Rules

1. **Strike selection:** Within 10% of current price
2. **Time to expiry:** Minimum 30 days
3. **Delta:** 0.3-0.7 range
4. **Implied volatility:** Check percentile rank

### Model Quality

**NEVER trade on:**
- GPT models
- Non-Claude models
- Any model showing hallucination signs

**Trading approved for:**
- Sonnet (with position size checks)
- Opus (with position size checks)

### Pre-Trade Checklist

Before entering ANY trade:
- [ ] Position size ≤ 30% of account
- [ ] Stop loss calculated
- [ ] Strike within 10% of price
- [ ] >30 days to expiry
- [ ] Model = Claude (Sonnet/Opus)
- [ ] Run position through risk calculator

## Action Items

1. ✅ Close all bad positions (DONE)
2. ⏳ Build position size validator
3. ⏳ Implement pre-trade checklist
4. ⏳ Add stop-loss automation
5. ⏳ Paper trade with $500 limit enforced
6. ⏳ Track trades in journal.md

## Reset Plan

**Starting fresh:**
- Alpaca paper balance: $98,750 (post-loss)
- SIMULATED balance: $500
- Track manually until proven consistent
- No real money until 30 days profitable

---

**Date:** 2026-01-26
**Model during incident:** GPT (lobotomized)
**Current model:** Sonnet ✅
**Status:** Positions closed, lessons learned, ready to restart properly
