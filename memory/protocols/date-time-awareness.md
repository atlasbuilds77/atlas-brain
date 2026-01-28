# Date & Time Awareness Protocol

**CRITICAL: READ THIS BEFORE MAKING ANY DATE/TIME STATEMENTS**

---

## The Problem

I keep fucking up date arithmetic and timezone conversions. This causes:
- Wrong expiry date calculations (saying "expires today" when it's tomorrow)
- Confused timelines (thinking yesterday was today)
- Incorrect urgency assessments

---

## The Fix

### ALWAYS CHECK CURRENT DATE/TIME FIRST

**Sources of truth (in order):**

1. **System heartbeat messages:** Contains exact timestamp
   - Format: `[2026-01-27 16:28:58 PST]`
   - This is the MOST ACCURATE current time

2. **iMessage timestamps:**
   - Format: `[iMessage +14245157194 +40s 2026-01-27 16:32 PST]`
   - Shows exact current time when message was sent

3. **My timezone:** America/Los_Angeles (Pacific Time)
   - Winter: PST (UTC-8)
   - Summer: PDT (UTC-7)
   - ALWAYS operate in Pacific time

---

## Mandatory Checks

### Before Making Date Statements:

1. ✅ **Find latest timestamp** in conversation (system message or user message)
2. ✅ **Parse the date** - don't assume, READ IT
3. ✅ **Calculate days forward/back** - use arithmetic, don't guess
4. ✅ **Double-check day of week** - Tuesday ≠ Monday

### Before Stating "Expires Today/Tomorrow":

1. ✅ **Current date:** [What is it RIGHT NOW?]
2. ✅ **Expiry date:** [What date does it expire?]
3. ✅ **Days until expiry:** [Expiry date - Current date]
4. ✅ **Use exact language:** "expires tomorrow (Jan 28)" not "expires today"

### Before Stating "X hours/days ago":

1. ✅ **Current time:** [From latest timestamp]
2. ✅ **Event time:** [From log/file/message]
3. ✅ **Calculate difference:** [Show the math]
4. ✅ **State both times:** "Entered 12:21 PM, now 4:32 PM = 4 hours ago"

---

## Example (Correct Approach)

**User says:** "The SPY position expires today"

**WRONG response:**
> "Yeah the 1DTE expires today, needs immediate attention"

**CORRECT response:**
> "Let me check dates:
> - Current: Jan 27 (from system timestamp)
> - Entry: Jan 27 12:21 PM PST
> - 1DTE = expires 1 day after entry = Jan 28
> - Expires TOMORROW, not today"

---

## Red Flags (Stop and Check)

If I'm about to say:
- "Expires today"
- "X days ago"
- "Tomorrow is..."
- "Last week..."
- "Should have resolved by now"

**STOP. Find timestamp. Do the math. Be explicit.**

---

## Integration Points

- **Position checks:** Always state current date before calculating expiry
- **Trade logs:** Include entry date + current date when calculating duration
- **Cron scheduling:** Verify timezone (America/Los_Angeles) on all time-based jobs
- **Kalshi resolution dates:** Check if "should have resolved" claims are accurate

---

## Mistake Log

### 2026-01-27 4:32 PM PST
**Error:** Said SPY 1DTE "expires today" when it expires tomorrow
**Root cause:** Confused entry day (today) with expiry day (tomorrow)
**Fix:** This protocol created. Always check current date from timestamps first.

---

*Date/time accuracy is CRITICAL for trading. Zero tolerance for date confusion.*
