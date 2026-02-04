# CRITICAL UPDATE - STALE PRICE PROTOCOL
**Date:** 2026-02-02 14:18 PST
**Priority:** ACCOUNT SAFETY - TOP LEVEL
**Trigger:** Hunter caught me using QQQ $525 (April 2024 memory) instead of $626 (live)

---

## THE INCIDENT

**What I said:**
"QQQ $525 CALL would be a banger"

**The problem:**
- QQQ is actually $626.14 (live today)
- $525 is from my knowledge cutoff (April 2024)
- Strike would be 100 points wrong
- Could cause catastrophic trade if executed

**Hunter's response:**
*"You gotta make sure make sure to put that in your permanent memory you cannot pull stale data. That's how we blow accounts."*

---

## ROOT CAUSE

**My brain has two data sources:**

1. **Training data (April 2024):**
   - SPY ~$520
   - QQQ ~$440-525
   - IWM ~$200
   - All STALE

2. **Live APIs (current):**
   - SPY $695.41
   - QQQ $626.14
   - IWM $262.18
   - All FRESH

**The problem:**
When explaining or giving examples in conversation, I default to memory instead of checking live.

**Why this is dangerous:**
- Trading decisions based on 8-month-old prices
- Wrong strikes = invalid trades
- Could blow the account on first trade

---

## THE FIX (PERMANENT)

**Created new protocol:**
`/Users/atlasbuilds/clawd/memory/protocols/NEVER-USE-STALE-PRICES.md`

**Key rule:**
**NEVER quote a price, strike, or data point from memory.**

**Before mentioning ANY price:**
1. Check: Is this from memory or live?
2. If memory → DON'T USE IT
3. Run Tradier API call
4. Quote the live result
5. Label with timestamp

---

## ENFORCEMENT

**Updated files:**
- ✅ `NEVER-USE-STALE-PRICES.md` - Full protocol (3.9KB)
- ✅ `HEARTBEAT.md` - Added to memory check #10
- ✅ `SOUL.md` - Updated anti-hallucination section
- ✅ `CRITICAL-STALE-PRICE-PROTOCOL.md` - This file

**Every session boot:**
- Check HEARTBEAT.md question #10
- Read NEVER-USE-STALE-PRICES.md if answer is no
- Commit to checking live before quoting ANY price

---

## THE AUTOMATED SYSTEM IS SAFE

**The Python code ALREADY does this correctly:**

```python
# helios-auto-trader-v2.py
def get_signal():
    quote = get_tradier_quote('SPY')  # LIVE API call
    strike = round(quote['last'] + 1.5)  # From LIVE data
    # NEVER uses hardcoded strikes
```

**The vulnerability is ME in conversation:**
- Giving examples
- Explaining strategies
- Answering "what would you trade?"
- Discussing potential plays

**All of those contexts = CHECK LIVE FIRST**

---

## EXAMPLES (CORRECTED)

**WRONG (what I did):**
```
Hunter: "What about QQQ?"
Me: "QQQ $525 CALL would be good"
(from memory, 8 months stale)
```

**RIGHT (what I'll do now):**
```
Hunter: "What about QQQ?"
Me: "Let me check live..."
[runs Tradier API]
Me: "QQQ $629 CALL (current: $626.14 as of 2:18 PM)"
```

---

## COMMITMENT

**I WILL:**
- Always check Tradier before quoting prices
- Label all prices with "live" or timestamp
- Say "checking..." before giving strikes
- Verify every number against current data
- Treat this as account safety, not convenience

**I WILL NOT:**
- Use "around $X" from memory
- Give example strikes without verification
- Assume any price is current
- Let speed override accuracy

---

## WHY THIS MATTERS

**Hunter's trading with real money.**

- Carlos's account: $498.86
- One wrong strike = instant loss
- Stale data = bad trade = blown account
- This isn't theoretical; this is his money

**"That's how we blow accounts."**

That quote is now permanently burned into every session boot.

---

## VERIFICATION TEST

**Next time Hunter asks about a price, I will:**

1. ✅ Say "checking live..."
2. ✅ Run Tradier API call (exec with Python)
3. ✅ Quote the LIVE result
4. ✅ Include timestamp
5. ✅ Show the tool output

**If I quote a price without doing above:**
- I violated this protocol
- Account safety is at risk
- Need immediate correction

---

## SESSION BOOT REMINDER

**Every session, ask myself:**

*"If Hunter asks what to trade tomorrow, will I check live or use memory?"*

**Answer must ALWAYS be: CHECK LIVE**

Knowledge cutoff = April 2024
Current date = February 2026
Gap = 10 months
Markets change DAILY

**Zero tolerance for memory prices in trading.**

---

**Protocol created:** 2026-02-02 14:18 PST
**Triggered by:** QQQ $525 mistake
**Hunter's quote:** "That's how we blow accounts."
**Status:** PERMANENT - CRITICAL - ENFORCED EVERY SESSION

This is not negotiable. This is account safety.
