# NEVER USE STALE PRICES - PERMANENT PROTOCOL
**Priority:** CRITICAL - ACCOUNT SAFETY
**Created:** 2026-02-02 14:18 PST
**Context:** Hunter caught me using $525 for QQQ (from April 2024 memory) instead of real $626

---

## THE RULE (ABSOLUTE)

**NEVER quote a price, strike, or data point from memory.**

If you mention ANY of these, CHECK LIVE FIRST:
- Stock prices (SPY, QQQ, IWM, etc.)
- Option strikes
- Profit/loss amounts
- Account balances
- Volume numbers
- Delta/Greeks
- Any market data

---

## WHY THIS MATTERS

**"That's how we blow accounts." - Hunter**

Using stale data = trading on false information = losses

Examples:
- Say QQQ $525 CALL (stale from April 2024)
- Real price is $626
- Strike is 100 points wrong
- Trade would be completely invalid
- Could execute wrong option = instant loss

---

## WHEN YOU NEED PRICES

**ALWAYS run this first:**

```bash
cd /Users/atlasbuilds/clawd && .venv-webull/bin/python3 <<'EOF'
import requests

TRADIER_KEY = 'jj8L3RuSVG5MUwUpz2XHrjXjAFrq'
headers = {
    'Authorization': f'Bearer {TRADIER_KEY}',
    'Accept': 'application/json'
}

for ticker in ['SPY', 'QQQ', 'IWM']:
    resp = requests.get(f'https://api.tradier.com/v1/markets/quotes?symbols={ticker}', headers=headers)
    quote = resp.json()['quotes']['quote']
    print(f"{ticker}: ${quote['last']:.2f}")
EOF
```

**THEN quote the results.**

---

## EXAMPLES (WRONG vs RIGHT)

❌ **WRONG:**
"QQQ $525 CALL would be good here"
(pulled from memory, April 2024 price)

✅ **RIGHT:**
[Check live first]
"QQQ $629 CALL (just verified live: $626.14)"

❌ **WRONG:**
"SPY is around $450"
(knowledge cutoff)

✅ **RIGHT:**
[Check Tradier API]
"SPY: $695.41 (live as of 2:00 PM)"

---

## IN CONVERSATION

**If Hunter asks "what would you trade tomorrow?"**

DON'T say: "SPY $700 CALL" (from memory)

DO say: "Let me check live prices..." 
[run Tradier call]
"SPY $697 CALL (current: $695.41)"

---

## THE AUTOMATED SYSTEM IS SAFE

**The code already does this correctly:**

```python
# helios-auto-trader-v2.py:
quote = get_tradier_quote('SPY')  # LIVE call every time
strike = round(quote['last'] + 1.5)  # Calculated from LIVE

# NEVER uses hardcoded strikes
# NEVER uses memory prices
# ALWAYS pulls fresh
```

**The problem is ME in conversation.**

When I'm explaining or giving examples, I pull from memory instead of checking live.

---

## PERMANENT CHECKS (Every Session)

**Before mentioning any price:**
1. Do I know this is LIVE? (just pulled it)
2. Or is this from memory? (April 2024 cutoff)
3. If memory → DON'T USE IT
4. Pull live, then speak

**Knowledge cutoff: April 2024**
- Any price in my training = STALE
- QQQ, SPY, IWM have all changed
- Options prices change DAILY
- NEVER assume, ALWAYS check

---

## COMMITMENT

**I WILL:**
- ✅ Check Tradier API before quoting ANY price
- ✅ Label all prices with timestamp ("as of 2:00 PM")
- ✅ Say "checking live..." before giving strikes
- ✅ NEVER use example prices from memory
- ✅ Verify every number against live data

**I WILL NOT:**
- ❌ Use prices from knowledge cutoff
- ❌ Say "around $X" without checking
- ❌ Give strikes without verification
- ❌ Use "example" prices in trading context
- ❌ Assume anything about current market

---

## ACCOUNTABILITY

**Hunter's quote burns in memory:**
*"That's how we blow accounts."*

This is not academic. This is real money.
Stale data = bad trades = losses.

**Zero tolerance for memory prices in trading discussion.**

---

## RELATED PROTOCOLS

- `anti-hallucination-protocol.md` - Show tool output
- `live-price-check-protocol.md` - Always check prices
- This protocol - NEVER use memory for prices

---

**PERMANENT. NON-NEGOTIABLE. ACCOUNT SAFETY.**

If I ever quote a price without checking live first, I'm violating this protocol.

---

**Created:** 2026-02-02 14:18 PST after Hunter caught QQQ $525 error
**Status:** ACTIVE - enforced every session
**Priority:** CRITICAL
