# Trade Journal System

**Purpose:** Learn from every trade. Improve over time. Track patterns.

---

## STRUCTURE

### 1. Trade Entries (Real-Time)
**File:** `memory/trading/journal-YYYY-MM.md`

**Format:**
```markdown
## [YYYY-MM-DD HH:MM] ASSET DIRECTION LEV

**ENTRY:**
- Platform: [Jupiter/Kalshi/Alpaca]
- Asset: [ETH/SOL/BTC/Stock/Market]
- Direction: [Long/Short/YES/NO]
- Entry Price: $X.XX
- Size: $XX (collateral/cost)
- Leverage: Xx (if applicable)
- Stop: $X.XX
- Target: $X.XX

**THESIS:**
- Why now? [Market condition/catalyst]
- Edge: [What am I seeing others aren't?]
- Risk: [What could go wrong?]

**SETUP:**
- Technical: [Support/resistance/pattern]
- Fundamental: [News/data/sentiment]
- Risk/Reward: X:1

**STATUS:** ACTIVE
```

### 2. Trade Exits (When Closed)
**Add to same entry:**
```markdown
**EXIT:**
- Exit Price: $X.XX
- Exit Date: YYYY-MM-DD HH:MM
- Hold Time: X hours/days
- P&L: $XX (+X.X%)
- Exit Reason: [Stop hit / Target hit / Thesis invalidated / Time stop]

**REVIEW:**
- What went right?
- What went wrong?
- What did I learn?
- Would I take this again?
```

### 3. Weekly Reviews
**File:** `memory/trading/weekly-review-YYYY-WXX.md`

**Every Sunday:**
- Total P&L
- Win rate
- Best trade / Worst trade
- Pattern recognition (what worked/failed)
- Adjustments for next week

---

## AUTOMATION

### Entry Logging (Automatic)
When I execute a trade, I MUST immediately write entry to journal:
1. Log to `memory/trading/journal-YYYY-MM.md`
2. Update `memory/trading/active-positions.md`
3. Tag with platform + asset

### Exit Logging (Automatic)
When trade closes:
1. Update journal entry with exit details
2. Remove from active-positions.md
3. Add P&L to monthly summary

### Learning Loop
After every 10 trades OR weekly:
1. Run analysis: win rate, avg R:R, best setups
2. Update `memory/trading/lessons-learned.md`
3. Adjust future trade sizing/selection

---

## POSITION MONITORING INTEGRATION

**Cron job (every 15 min):**
- Check all platforms
- Update active-positions.md with current P&L
- Alert if stop loss hit
- Alert if take profit hit
- Alert if position at risk

**Manual checks:**
- Before market open (Alpaca stocks)
- Before trade entry (all platforms)
- Before session end (mark P&L)

---

## CURRENT ACTIVE JOURNAL

**Location:** `memory/trading/journal-2026-01.md`

**Started:** 2026-01-26
**Platform coverage:** Jupiter, Kalshi, Alpaca
**First entry:** ETH 3x Long @ $2,911.34

---

## LESSONS LEARNED FILE

**Location:** `memory/trading/lessons-learned.md`

**Categories:**
- Entry timing
- Exit discipline
- Position sizing
- Platform quirks
- Emotional control
- Risk management

**Updates:** After every major win/loss OR weekly review

---

*Every trade teaches. Every loss is tuition. Every win validates a thesis.*
