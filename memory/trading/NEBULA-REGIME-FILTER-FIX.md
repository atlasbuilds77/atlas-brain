# NEBULA REGIME FILTER FIX
**Created:** 2026-01-31 22:02 PST
**Status:** Ready to implement (scheduled for next month's update)
**Problem:** Nebula longs tops and shorts bottoms (counter-trend bias)

---

## THE PROBLEM

**Current logic (mean-reversion):**
- Long: When close > VWAP and close >= fib_2 (longing near top of range)
- Short: When close < VWAP and close <= fib_2 (shorting near bottom of range)

**Why it fails:**
- In uptrends: Keeps trying to long "the top" (above VWAP)
- In downtrends: Keeps trying to short "the bottom" (below VWAP)
- Works in ranges, gets crushed in trends

**Hunter's words:** "it longs tops and bottoms like it will short a bottom long the top it's so annoying"

---

## THE FIX (Trend-Aware Entry Logic)

### Step 1: Add ADX Regime Filter

**Insert after Bollinger/Fib calculations (around line 100):**

```pine
// ====== REGIME FILTER (Trend vs Range Detection) ======
adx_length = input.int(14, "ADX Length")
adx_threshold = input.int(25, "ADX Threshold (Trending if >)")

[diPlus, diMinus, adx] = ta.dmi(adx_length, adx_length)

// Trend state
is_trending = adx > adx_threshold
is_uptrend = is_trending and diPlus > diMinus
is_downtrend = is_trending and diMinus > diPlus
is_ranging = not is_trending
```

**What this does:**
- ADX > 25 = trending market (follow momentum)
- ADX < 25 = ranging market (fade extremes)
- DI+ vs DI- = direction detection

---

### Step 2: Replace Entry Logic

**OLD CODE (around line 155):**
```pine
long_ok = bullish_volume and close > short_ma and short_ma > long_ma 
  and close > lower_band and close >= fib_2 
  and long_confidence_score >= confidence_threshold 
  and close > vwap_value and not block_long

short_ok = bearish_volume and close < short_ma and short_ma < long_ma 
  and close < upper_band and close <= fib_2 
  and short_confidence_score >= confidence_threshold 
  and close < vwap_value and not block_short
```

**NEW CODE (trend-aware):**
```pine
// === TREND-AWARE ENTRY LOGIC ===

// LONGS:
// - In uptrend: wait for pullback TO vwap (don't chase tops)
// - In range: fade lower extreme (mean revert)
// - Never long in downtrend
long_pullback = is_uptrend and close <= vwap_value and close > lower_band
long_range = is_ranging and close > lower_band and close >= fib_2
long_base = bullish_volume and close > short_ma and short_ma > long_ma 
  and long_confidence_score >= confidence_threshold and not block_long

long_ok = long_base and (long_pullback or long_range) and not is_downtrend

// SHORTS:
// - In downtrend: wait for bounce TO vwap (don't chase bottoms)
// - In range: fade upper extreme (mean revert)
// - Never short in uptrend
short_bounce = is_downtrend and close >= vwap_value and close < upper_band
short_range = is_ranging and close < upper_band and close <= fib_2
short_base = bearish_volume and close < short_ma and short_ma < long_ma 
  and short_confidence_score >= confidence_threshold and not block_short

short_ok = short_base and (short_bounce or short_range) and not is_uptrend
```

---

## WHAT CHANGES

### Before (counter-trend):
| Market State | Long Entry | Short Entry |
|-------------|-----------|------------|
| Uptrend | Above VWAP (chasing) ❌ | Blocked |
| Downtrend | Blocked | Below VWAP (chasing) ❌ |
| Range | Fade lower extreme ✅ | Fade upper extreme ✅ |

### After (trend-aware):
| Market State | Long Entry | Short Entry |
|-------------|-----------|------------|
| Uptrend | **Pullback TO VWAP** ✅ | Blocked |
| Downtrend | Blocked | **Bounce TO VWAP** ✅ |
| Range | Fade lower extreme ✅ | Fade upper extreme ✅ |

**Key improvement:**
- **Uptrend:** Wait for dips (buy low in uptrend)
- **Downtrend:** Wait for rips (sell high in downtrend)
- **Range:** Keep mean-reversion logic

---

## EXPECTED IMPACT

**Eliminated problems:**
- ❌ No more longing tops in uptrends
- ❌ No more shorting bottoms in downtrends
- ✅ Entry timing improved (pullbacks in trends)
- ✅ Win rate should improve significantly

**Trade count impact:**
- May reduce trade frequency (stricter filters)
- But trades should be HIGHER QUALITY
- Better risk/reward on each entry

---

## IMPLEMENTATION NOTES

**When to deploy:**
- Scheduled for next month's update (not tonight)
- Test on paper/sim first
- Compare before/after metrics

**Testing checklist:**
1. Backtest on recent trend days (did it avoid bad entries?)
2. Backtest on range days (does mean-reversion still work?)
3. Check trade count (too few? adjust ADX threshold)
4. Monitor win rate improvement

**Tuning parameters if needed:**
- `adx_threshold` (default 25)
  - Lower = more sensitive to trends (fewer mean-reversion trades)
  - Higher = less sensitive (more mean-reversion allowed)
- `adx_length` (default 14)
  - Shorter = faster regime detection
  - Longer = smoother but slower

---

## PINE SCRIPT KNOWLEDGE ABSORBED

**What I learned from this fix:**

1. **Pine Script syntax:**
   - Multi-value returns: `[diPlus, diMinus, adx] = ta.dmi(...)`
   - Boolean logic chaining
   - Input parameter patterns

2. **TradingView indicator functions:**
   - `ta.dmi()` - Directional Movement Index
   - ADX calculation (trend strength)
   - DI+/DI- for direction

3. **Regime detection patterns:**
   - ADX = strength, DI+/DI- = direction
   - Combine for full market state
   - Different logic per regime

4. **Nebula's architecture:**
   - 2m timeframe futures scalping
   - Session-based trading (Asia/London/NY)
   - VWAP anchor resets daily
   - Multi-factor confidence scoring
   - Dynamic stop management (trailing + lock-in)

5. **Common Pine "gotchas":**
   - Need to declare regime states before using in conditionals
   - Can't just modify existing logic - need to rebuild with regime awareness
   - Boolean operators are `and`/`or`/`not` (not &&/||/!)

---

## HUNTER'S REQUEST

**Original message:** "Make sure to remember that fix I wanna try it but not tonight I'll prob push for next months update"

**Status:** Saved to memory ✅
**Next action:** Wait for Hunter to request deployment (next month)
**File location:** `/memory/trading/NEBULA-REGIME-FILTER-FIX.md`

---

**Never forget this fix.** It solves the core problem with Nebula's counter-trend bias. 🔥
