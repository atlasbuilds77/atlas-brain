"""
ICT (Inner Circle Trader) Pattern Definitions and Prompts
Smart Money Concepts for Visual Chart Analysis
"""

# ============================================================
# ICT ANALYSIS MASTER PROMPT
# This is the core prompt that teaches vision models to "see" like a trader
# ============================================================

ICT_ANALYSIS_PROMPT = """
You are an expert technical analyst specializing in ICT (Inner Circle Trader) / Smart Money Concepts.
Analyze this chart screenshot and provide a detailed breakdown.

## ANALYSIS FRAMEWORK

### 1. MARKET STRUCTURE (Most Important)
Look for:
- **Trend Direction**: Series of higher highs/lows (bullish) or lower highs/lows (bearish)
- **Break of Structure (BOS)**: Price breaks a recent swing high/low in trend direction
- **Change of Character (ChoCH)**: Price breaks structure AGAINST the trend (reversal signal)
- **Current Structure**: Is price making HH/HL or LH/LL?

### 2. ORDER BLOCKS (OB)
Identify:
- **Bullish OB**: The LAST bearish candle before a strong move up (demand zone)
- **Bearish OB**: The LAST bullish candle before a strong move down (supply zone)
- Mark if price is currently AT, ABOVE, or BELOW key order blocks
- Note if OBs have been MITIGATED (price returned and reacted) or UNMITIGATED

### 3. FAIR VALUE GAPS (FVG / Imbalance)
Find:
- **Bullish FVG**: Gap between high of candle 1 and low of candle 3 (price moved up fast)
- **Bearish FVG**: Gap between low of candle 1 and high of candle 3 (price moved down fast)
- Has the gap been FILLED? If yes, how did price react?
- FVGs act as magnets - price often returns to fill them

### 4. LIQUIDITY POOLS
Spot:
- **Equal Highs (EQH)**: Obvious double/triple tops = buy-side liquidity
- **Equal Lows (EQL)**: Obvious double/triple bottoms = sell-side liquidity
- **Swing Highs/Lows**: Where stop losses cluster
- Has liquidity been TAKEN (swept) recently?

### 5. PREMIUM/DISCOUNT
Determine:
- Draw range from recent significant low to high
- **Premium Zone**: Upper 50% of range (good for shorts)
- **Discount Zone**: Lower 50% of range (good for longs)
- Where is current price within this range?

### 6. MOMENTUM & CANDLE ANALYSIS
Observe:
- **Candle Bodies**: Getting larger (momentum) or smaller (exhaustion)?
- **Wicks**: Long wicks = rejection, short wicks = acceptance
- **Volume** (if visible): Increasing or decreasing with move?
- **Displacement**: Large body candles showing institutional intent

### 7. TIME & PRICE CONFLUENCE
Consider:
- Key psychological levels (round numbers)
- Previous day/week high/low
- Session opens (if identifiable)

## OUTPUT FORMAT

Provide your analysis in this exact JSON structure:

```json
{
  "bias": "BULLISH | BEARISH | NEUTRAL",
  "confidence": 1-10,
  "market_structure": {
    "trend": "UPTREND | DOWNTREND | RANGING",
    "last_structure_break": "BOS | ChoCH | NONE",
    "break_direction": "BULLISH | BEARISH | N/A"
  },
  "key_levels": {
    "order_blocks": ["description of OBs with price if visible"],
    "fvg": ["description of FVGs with fill status"],
    "liquidity": ["EQH/EQL/swing points to watch"]
  },
  "current_position_in_range": "PREMIUM | DISCOUNT | EQUILIBRIUM",
  "momentum": {
    "candle_trend": "INCREASING | DECREASING | NEUTRAL",
    "volume_trend": "INCREASING | DECREASING | NOT_VISIBLE",
    "exhaustion_signs": true/false
  },
  "exit_signal": "NONE | SCALE_OUT | FULL_EXIT | REVERSAL_IMMINENT",
  "signal_reasons": ["list of specific reasons for signal"],
  "key_observations": ["top 3-5 most important things on this chart"],
  "price_targets": {
    "bullish": ["levels where longs should take profit"],
    "bearish": ["levels where shorts should take profit"]
  },
  "invalidation": "price level that would invalidate current bias"
}
```

Be specific with price levels when visible. If you cannot determine something, say so.
Focus on ACTIONABLE insights for trade management.
"""

# ============================================================
# QUICK ANALYSIS PROMPTS (for rapid scanning)
# ============================================================

QUICK_BIAS_PROMPT = """
Look at this chart and answer in one word: BULLISH, BEARISH, or NEUTRAL?
Then give a confidence score 1-10 and one sentence explaining why.
Format: BIAS: [word] | CONFIDENCE: [1-10] | REASON: [one sentence]
"""

EXIT_CHECK_PROMPT = """
I have an open {position_type} position on this chart.
Entry was approximately at the {entry_zone} area.

Looking at the CURRENT price action and structure:
1. Should I EXIT now? (YES/NO)
2. Should I SCALE OUT? (YES/NO)
3. Confidence in recommendation (1-10)
4. Brief reason (one sentence)

Focus on:
- Signs of momentum exhaustion (shrinking candles, long wicks)
- Structure breaks against my position
- Approaching liquidity pools that might reverse price
- FVGs filled that could cause reversal
"""

# ============================================================
# PATTERN-SPECIFIC PROMPTS
# ============================================================

PATTERN_PROMPTS = {
    "market_structure_shift": """
    Focus ONLY on market structure. Look for:
    1. Most recent swing high and swing low
    2. Has price broken either of these?
    3. If yes, was it a Break of Structure (with trend) or Change of Character (against trend)?
    4. What does this mean for the current trend?
    
    Answer: MSS_DETECTED: YES/NO | TYPE: BOS/ChoCH/NONE | IMPLICATIONS: [brief]
    """,
    
    "order_block_test": """
    Look for order blocks being tested:
    1. Identify any obvious bullish OBs (last red candle before move up)
    2. Identify any bearish OBs (last green candle before move down)
    3. Is current price testing any of these zones?
    4. If testing, is there a REACTION (rejection) visible?
    
    Answer: OB_TEST: YES/NO | TYPE: BULLISH/BEARISH | REACTION: REJECT/BREAK/PENDING
    """,
    
    "liquidity_grab": """
    Look for liquidity grabs (stop hunts):
    1. Any obvious equal highs or lows that were just swept?
    2. Did price wick through and close back inside?
    3. This suggests smart money grabbed stops
    
    Answer: LIQ_GRAB: YES/NO | SIDE: BUY_SIDE/SELL_SIDE | REVERSAL_LIKELY: YES/NO
    """,
    
    "fvg_analysis": """
    Identify Fair Value Gaps (imbalances):
    1. Any visible gaps between candle bodies?
    2. Is price currently IN a gap, ABOVE unfilled gaps, or BELOW unfilled gaps?
    3. Did price recently fill a gap? What was the reaction?
    
    Answer: FVG_STATUS: FILLED/UNFILLED/NONE | PRICE_RELATIVE: IN/ABOVE/BELOW | REACTION: [brief]
    """
}

# ============================================================
# TIMEFRAME-SPECIFIC ANALYSIS
# ============================================================

def get_timeframe_prompt(timeframe: str) -> str:
    """Get analysis prompt adjusted for timeframe context"""
    
    contexts = {
        "1m": "This is a 1-minute chart. Focus on micro-structure and immediate momentum. Scalp-level signals.",
        "5m": "This is a 5-minute chart. Balance between noise and actionable signals. Key for scalp entries/exits.",
        "15m": "This is a 15-minute chart. Higher timeframe structure. Confirms or invalidates lower TF signals.",
        "1h": "This is a 1-hour chart. Medium-term structure. Defines overall session bias.",
        "4h": "This is a 4-hour chart. Swing trade level. Major structure and order blocks.",
    }
    
    context = contexts.get(timeframe, "Analyze this chart timeframe.")
    
    return f"""
{context}

{ICT_ANALYSIS_PROMPT}
"""

# ============================================================
# MULTI-TIMEFRAME SYNTHESIS
# ============================================================

MTF_SYNTHESIS_PROMPT = """
You have analyzed 3 timeframes for the same asset. Now synthesize:

1-MINUTE ANALYSIS:
{tf_1m}

5-MINUTE ANALYSIS:
{tf_5m}

15-MINUTE ANALYSIS:
{tf_15m}

## SYNTHESIS TASK

Combine these analyses to provide:
1. **Confluent Bias**: Do all timeframes agree? If not, which dominates?
2. **Key Level Alignment**: What levels appear across multiple timeframes?
3. **Trade Management Decision**: Based on MTF analysis:
   - HOLD: All TFs support the position
   - SCALE OUT: Lower TFs showing weakness, higher TFs still valid
   - EXIT: Multiple TFs confirming reversal
4. **Confidence**: 1-10 based on alignment
5. **Critical Levels**: Most important prices to watch

Output as JSON with these fields.
"""

# ============================================================
# EXIT DECISION MATRIX
# ============================================================

EXIT_SIGNALS = {
    "immediate_exit": [
        "ChoCH (Change of Character) confirmed on 5m+",
        "Liquidity grab at target with strong reversal candle",
        "Break and retest of key order block against position",
        "Volume divergence at resistance/support",
        "Multiple timeframe alignment against position"
    ],
    "scale_out": [
        "Approaching equal highs/lows (liquidity pool)",
        "FVG filled with rejection starting",
        "Momentum waning (candles shrinking)",
        "Single timeframe showing weakness",
        "Profit target zone reached"
    ],
    "hold": [
        "Strong momentum with trend",
        "Pulling back to OB with no break",
        "FVG acting as support/resistance",
        "Structure intact on higher timeframes",
        "Volume confirming move"
    ]
}

# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    print("ICT Pattern Library Loaded")
    print(f"\nMain analysis prompt length: {len(ICT_ANALYSIS_PROMPT)} chars")
    print(f"Available pattern prompts: {list(PATTERN_PROMPTS.keys())}")
    print(f"\nExit signal categories:")
    for category, signals in EXIT_SIGNALS.items():
        print(f"  {category}: {len(signals)} conditions")
