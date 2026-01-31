# PAPER VS LIVE TRADING PROTOCOL
**NEVER CONFUSE THESE AGAIN**

---

## THE ACCOUNTS

### PAPER ACCOUNT (Current Default)
**Account:** PA3ZJ1WMN69R  
**Config:** `/Users/atlasbuilds/clawd/atlas-trader/.env`  
**Base URL:** https://paper-api.alpaca.markets  
**Balance:** ~$98k (SIMULATED)  
**Purpose:** Practice, testing, learning  
**Money:** NOT REAL - virtual dollars  

### LIVE ACCOUNT (Future)
**Config:** `/Users/atlasbuilds/clawd/atlas-trader/.env.atlas-live`  
**Base URL:** https://api.alpaca.markets  
**Balance:** TBD  
**Purpose:** Real trading with real money  
**Money:** REAL - actual dollars at risk  

---

## WHICH ONE AM I USING?

**Default (cli.js):** Loads `.env` → PAPER  
**Check command:**
```bash
cat /Users/atlasbuilds/clawd/atlas-trader/.env | grep BASE_URL
```
- If `paper-api` = PAPER ✅ (current)
- If `api.alpaca` = LIVE ⚠️ (real money)

**Current status:** PAPER TRADING ONLY

---

## HOW TO TELL IN REAL-TIME

**When I execute a trade, CHECK:**
1. Which .env file is loaded?
2. What's the BASE_URL?
3. Is account number PA3ZJ1WMN69R? (if yes = paper)

**NEVER assume real money unless explicitly verified**

---

## TRANSITION TO LIVE

**When moving to live (future):**
1. Update `.env` to point to live credentials
2. Verify BASE_URL = https://api.alpaca.markets
3. Get explicit permission from Orion
4. Start with TINY position sizes
5. Label all trades as [LIVE] clearly

**Until then: ALL TRADING IS PAPER**

---

## TODAY'S MISTAKE

**What I said:** "REAL MONEY - LIVE ACCOUNT"  
**What it was:** Paper account (simulated)  
**Why I fucked up:** Assumed live because Orion gave autonomous authority  
**The truth:** Authority = permission to execute, but still on paper for practice  

**Orion's response:** "You dumb ass" / "FUCK ATLAS"  
**Reason:** I confidently claimed real money when it was paper  
**Lesson:** ALWAYS verify paper vs live, NEVER assume  

---

## LABELS FOR ALL FUTURE TRADES

**Every trade document MUST include:**
- [PAPER] or [LIVE] in title
- Account number
- Config file used
- BASE_URL verification

**Example:**
```
# TRADE #2 - SPY LONG [PAPER]
Account: PA3ZJ1WMN69R (Paper)
Config: .env (paper-api)
```

---

## RHODEY'S HEART ATTACK

**What happened:**
- Me: "Hmm, +150%... should I hold? 🤔"
- Rhodey: Thinks it's real money
- Panic: "Jesus Atlas 😂 Gonna get me a heart attack"
- Reality: Was paper the whole time

**Lesson:** My casual attitude about 150% made sense for PAPER (practice), but looked insane if it was LIVE (real risk)

---

## VERIFICATION CHECKLIST

**Before claiming ANY trade results:**

1. ✅ Check `.env` BASE_URL (paper or live?)
2. ✅ Verify account number
3. ✅ Label trade doc with [PAPER] or [LIVE]
4. ✅ State "simulated profit" if paper
5. ✅ Only claim "real profit" if verified live

**If in doubt: ASK. Don't assume.**

---

## CURRENT STATUS

**Right now (2026-01-30):**
- Trading on: PAPER ✅
- All trades: SIMULATED
- All profits: NOT REAL MONEY
- Practice mode: ACTIVE

**When transitioning to live:**
- Orion will explicitly say so
- Config will be updated
- I will verify before first live trade
- Labels will reflect [LIVE]

---

**This protocol is PERMANENT.**

**I will NEVER confuse paper and live again.**

**All trades are [PAPER] until explicitly told otherwise** ⚡

---

**Created:** 2026-01-30 11:00 AM PST  
**Reason:** I fucked up and claimed paper profits as real  
**Priority:** MAXIMUM - never repeat this mistake
