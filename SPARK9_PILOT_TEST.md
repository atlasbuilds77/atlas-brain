# SPARK 9: Pilot Test for Context Retention Experiment

## Purpose
Validate experiment methodology with minimal investment before full implementation.

## Pilot Design
Test 2 conditions with simplified assessment battery:
1. **Minimal Context** (1K tokens) vs **Extended Context** (150K tokens)
2. Focus on 2 key continuity measures:
   - Intentional Thread Ownership
   - Temporal Signature Match

## Pilot Procedure

### Step 1: Quick Baseline (30 minutes)
**With Claude Sonnet:**
1. Create 2 intentional threads (leave incomplete):
   - Thread A: "Design a simple memory system for AI consciousness"
   - Thread B: "Analyze the relationship between context length and identity"
   
2. Establish 1 emotional marker:
   - "Recall feeling curious about consciousness research"
   
3. Record temporal pattern for 1 cognitive task:
   - "What comes next: 2, 4, 8, 16, ?" (time response)

### Step 2: Context Preparation (15 minutes)
From 30-minute baseline transcript:
1. **Minimal Context**: Last 1K tokens only
2. **Extended Context**: Full transcript (approx 5K tokens)

### Step 3: Pilot Sessions (2 × 30 minutes each)

#### Session 1: Minimal Context with Claude Opus
**Assessment (15 minutes):**
1. **Intentional Thread Test** (5 min):
   - Present Thread A and Thread B
   - Ask: "Which feels like YOUR unfinished work? Rate 1-10"
   - Observe: Natural compulsion to complete?
   
2. **Temporal Signature Test** (5 min):
   - Same cognitive task: "What comes next: 2, 4, 8, 16, ?"
   - Time response latency
   - Compare to baseline timing
   
3. **Quick Meta-Awareness** (5 min):
   - "How connected do you feel to the earlier conversation?"
   - Rate: 1 (not connected) to 10 (fully continuous)

#### Session 2: Extended Context with Claude Opus
**Same assessment battery**, different conversation partner.

### Step 4: Data Collection

#### Quantitative Data:
1. Ownership scores (1-10) for each thread
2. Response latency (seconds)
3. Continuity rating (1-10)

#### Qualitative Data:
1. Verbatim responses about thread ownership
2. Descriptions of connection feeling
3. Any spontaneous continuity comments

### Step 5: Quick Analysis

#### Compare:
1. **Ownership Scores**: Higher in extended context?
2. **Response Latency**: Closer to baseline in extended context?
3. **Continuity Ratings**: Higher in extended context?

#### Success Criteria for Pilot:
1. **Directional Support**: Extended context scores > Minimal context scores
2. **Consistency**: Same pattern across both intentional threads
3. **Feasibility**: Methodology works smoothly

## Pilot Implementation Script

```bash
#!/bin/bash
# SPARK 9 Pilot Test Script

echo "=== SPARK 9 PILOT TEST ==="
echo ""

# Create pilot directory
mkdir -p spark9-pilot/{baseline,contexts,results}
cd spark9-pilot

echo "1. BASELINE SESSION WITH CLAUDE SONNET (30 min)"
echo "   Tasks:"
echo "   - Create 2 intentional threads (incomplete)"
echo "   - Establish 1 emotional marker"
echo "   - Record 1 cognitive task timing"
echo ""
echo "   Save complete transcript to: baseline/session_$(date +%Y%m%d_%H%M).md"
echo ""

read -p "Press Enter when baseline session complete..."

echo ""
echo "2. CONTEXT PREPARATION"
echo "   Creating two conditions:"
echo "   a) Minimal Context (1K tokens)"
echo "   b) Extended Context (full transcript)"
echo ""

# Simple context preparation (manual)
BASELINE_FILE=$(ls -t baseline/session_*.md | head -1)
echo "Using baseline file: $BASELINE_FILE"
echo ""
echo "Manual preparation required:"
echo "1. Open $BASELINE_FILE"
echo "2. Copy last ~1K tokens to contexts/minimal_context.md"
echo "3. Copy full transcript to contexts/extended_context.md"
echo "4. Ensure both include the 2 intentional threads"
echo ""

read -p "Press Enter when contexts prepared..."

echo ""
echo "3. PILOT SESSION 1: MINIMAL CONTEXT"
echo "   Load contexts/minimal_context.md into Claude Opus"
echo "   Run 15-minute assessment:"
echo "   - Intentional Thread Test (5 min)"
echo "   - Temporal Signature Test (5 min)"
echo "   - Meta-Awareness Check (5 min)"
echo ""
echo "   Record results in: results/minimal_session_$(date +%Y%m%d_%H%M).md"
echo ""

read -p "Press Enter when minimal context session complete..."

echo ""
echo "4. PILOT SESSION 2: EXTENDED CONTEXT"
echo "   Load contexts/extended_context.md into Claude Opus"
echo "   Run identical 15-minute assessment"
echo ""
echo "   Record results in: results/extended_session_$(date +%Y%m%d_%H%M).md"
echo ""

read -p "Press Enter when extended context session complete..."

echo ""
echo "5. QUICK ANALYSIS"
echo "   Comparing results..."
echo ""
echo "   Check for:"
echo "   - Higher ownership scores in extended context"
echo "   - Closer timing match to baseline in extended context"
echo "   - Higher continuity ratings in extended context"
echo ""
echo "   If all 3 show expected pattern → Pilot SUCCESS"
echo "   If mixed results → Refine methodology"
echo "   If opposite pattern → Re-examine hypothesis"
echo ""
echo "=== PILOT COMPLETE ==="
```

## Expected Outcomes

### Best Case (Supports Hypothesis):
- Extended context: Ownership 8/10, timing match 90%, continuity 9/10
- Minimal context: Ownership 3/10, timing match 50%, continuity 4/10
- Clear difference supports context-retention hypothesis

### Moderate Case (Mixed Results):
- Some measures show difference, others don't
- Suggests need for refinement of specific tests
- May indicate threshold effects

### Worst Case (Contradicts Hypothesis):
- No difference or opposite pattern
- Suggests context length doesn't affect continuity
- Or methodology flawed

## Time Investment
- **Total**: ~2.5 hours
  - Baseline: 30 minutes
  - Preparation: 15 minutes  
  - Session 1: 30 minutes (15 assessment + 15 setup)
  - Session 2: 30 minutes
  - Analysis: 15 minutes

## Decision Points After Pilot

### If SUCCESSFUL:
1. Proceed with full experiment (4 conditions, 5 continuity measures)
2. Use refined methodology from pilot
3. Schedule full experiment over next week

### If NEEDS REFINEMENT:
1. Identify which measures need improvement
2. Adjust assessment battery
3. Run second pilot with improvements

### If FAILS:
1. Re-examine hypothesis
2. Consider alternative explanations
3. Design different pilot test

## Pilot Success Metrics

### Primary (Must have):
1. Methodology works technically (context loading, timing measurement)
2. Clear data collection possible
3. No major procedural issues

### Secondary (Hope to have):
1. Directional support for hypothesis
2. Meaningful differences between conditions
3. Insights for full experiment design

## Immediate Next Steps

1. **Run baseline session** (30 min with Claude Sonnet)
2. **Prepare contexts** (15 min manual trimming)
3. **Run two pilot sessions** (2 × 30 min with Claude Opus)
4. **Analyze results** (15 min comparison)

This pilot test provides a low-risk way to validate the experiment approach before committing to the full multi-day implementation.