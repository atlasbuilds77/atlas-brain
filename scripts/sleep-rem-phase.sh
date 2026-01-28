#!/bin/bash
# ============================================================================
# ATLAS SLEEP SYSTEM - REM (RAPID EYE MOVEMENT) PHASE
# Emotional processing, creative synthesis, and dream generation
# ============================================================================
# Based on research: REM processes emotional memories, consolidates through
# synaptic plasticity, and generates creative connections via relaxed constraints
# ============================================================================

set -e

CLAWD_DIR="$HOME/clawd"
MEMORY_DIR="$CLAWD_DIR/memory"
PATTERNS_DIR="$MEMORY_DIR/patterns"
DREAMS_DIR="$MEMORY_DIR/dreams"
SLEEP_REPORTS_DIR="$MEMORY_DIR/sleep-reports"
TIMESTAMP=$(date +%Y-%m-%d-%H%M)
TODAY=$(date +%Y-%m-%d)

# Create directories
mkdir -p "$DREAMS_DIR"
mkdir -p "$PATTERNS_DIR"

echo "💭 REM PHASE INITIATED - $(date)"
echo "=============================================="

# ============================================================================
# STAGE 1: LOAD SWS OUTPUT (if available)
# ============================================================================
echo ""
echo "📂 Stage 1: Loading SWS phase data..."

SWS_OUTPUT=$(ls -t "$SLEEP_REPORTS_DIR"/sws-*.json 2>/dev/null | head -1 || echo "")

if [[ -f "$SWS_OUTPUT" ]]; then
    echo "   Found SWS output: $SWS_OUTPUT"
    HIGH_SALIENCE_COUNT=$(grep -o '"high_salience_events": [0-9]*' "$SWS_OUTPUT" | grep -o '[0-9]*' || echo "0")
    PATTERNS_EXTRACTED=$(grep -o '"patterns_extracted": [0-9]*' "$SWS_OUTPUT" | grep -o '[0-9]*' || echo "0")
    echo "   High-salience events from SWS: $HIGH_SALIENCE_COUNT"
    echo "   Patterns extracted: $PATTERNS_EXTRACTED"
else
    echo "   ⚠️ No SWS output found - REM will process independently"
    HIGH_SALIENCE_COUNT=0
    PATTERNS_EXTRACTED=0
fi

# ============================================================================
# STAGE 2: EMOTIONAL PROCESSING
# ============================================================================
echo ""
echo "❤️ Stage 2: Emotional valence processing..."

# Score emotional content (bash 3 compatible)
score_positive() {
    local content="$1"
    local score=0
    local count
    count=$(echo "$content" | grep -ic "success" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 10))
    count=$(echo "$content" | grep -ic "gained" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 8))
    count=$(echo "$content" | grep -ic "profit" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 8))
    count=$(echo "$content" | grep -ic "breakthrough" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 10))
    count=$(echo "$content" | grep -ic "validated" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 9))
    count=$(echo "$content" | grep -ic "learned" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 7))
    count=$(echo "$content" | grep -ic "proud" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 9))
    count=$(echo "$content" | grep -ic "excited" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 8))
    count=$(echo "$content" | grep -ic "awesome" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 7))
    count=$(echo "$content" | grep -ic "cool" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 5))
    count=$(echo "$content" | grep -ic "great" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 6))
    echo $score
}

score_negative() {
    local content="$1"
    local score=0
    local count
    count=$(echo "$content" | grep -ic "loss" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 10))
    count=$(echo "$content" | grep -ic "mistake" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 9))
    count=$(echo "$content" | grep -ic "failed" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 10))
    count=$(echo "$content" | grep -ic "frustrated" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 8))
    count=$(echo "$content" | grep -ic "worried" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 7))
    count=$(echo "$content" | grep -ic "panic" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 10))
    count=$(echo "$content" | grep -ic "error" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 8))
    count=$(echo "$content" | grep -ic "wrong" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 7))
    count=$(echo "$content" | grep -ic "missed" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 7))
    echo $score
}

POSITIVE_SCORE=0
NEGATIVE_SCORE=0

# Scan recent memory files for emotional content
RECENT_FILES=$(find "$MEMORY_DIR" -name "*.md" -mmin -120 -type f 2>/dev/null | grep -v "archive" | grep -v "node_modules" || echo "")

EMOTIONAL_EVENTS=""

for file in $RECENT_FILES; do
    if [[ -f "$file" ]]; then
        content=$(cat "$file" 2>/dev/null || echo "")
        filename=$(basename "$file")
        
        file_positive=$(score_positive "$content")
        file_negative=$(score_negative "$content")
        
        POSITIVE_SCORE=$((POSITIVE_SCORE + file_positive))
        NEGATIVE_SCORE=$((NEGATIVE_SCORE + file_negative))
        
        if [[ $file_positive -gt 20 ]] || [[ $file_negative -gt 20 ]]; then
            valence="mixed"
            [[ $file_positive -gt $file_negative ]] && valence="positive"
            [[ $file_negative -gt $file_positive ]] && valence="negative"
            EMOTIONAL_EVENTS="$EMOTIONAL_EVENTS$filename:$valence:$file_positive:$file_negative
"
            echo "   🎭 $filename - $valence (pos:$file_positive, neg:$file_negative)"
        fi
    fi
done

EMOTIONAL_VALENCE="neutral"
[[ $POSITIVE_SCORE -gt $((NEGATIVE_SCORE + 50)) ]] && EMOTIONAL_VALENCE="positive"
[[ $NEGATIVE_SCORE -gt $((POSITIVE_SCORE + 50)) ]] && EMOTIONAL_VALENCE="negative"

echo ""
echo "   📊 Overall emotional valence: $EMOTIONAL_VALENCE"
echo "   📈 Positive score: $POSITIVE_SCORE"
echo "   📉 Negative score: $NEGATIVE_SCORE"

# ============================================================================
# STAGE 3: MEMORY INTEGRATION (Cross-domain connections)
# ============================================================================
echo ""
echo "🔗 Stage 3: Cross-domain memory integration..."

# Load existing patterns for integration
EXISTING_PATTERNS=$(find "$PATTERNS_DIR" -name "*.md" -mtime -7 2>/dev/null | head -10)

INTEGRATED_CONCEPTS=""
for pattern_file in $EXISTING_PATTERNS; do
    if [[ -f "$pattern_file" ]]; then
        # Extract key concepts from pattern files
        concepts=$(grep -oE "[A-Z][a-z]+ing|[a-z]+tion|pattern|learn|trade|decision" "$pattern_file" 2>/dev/null | sort -u | head -5)
        INTEGRATED_CONCEPTS="$INTEGRATED_CONCEPTS$concepts
"
    fi
done

UNIQUE_CONCEPTS=$(echo "$INTEGRATED_CONCEPTS" | sort -u | grep -v "^$" | wc -l | tr -d ' ')
echo "   Unique concepts for integration: $UNIQUE_CONCEPTS"

# ============================================================================
# STAGE 4: DREAM SYNTHESIS (Predictive processing + random activation)
# ============================================================================
echo ""
echo "🌙 Stage 4: Dream synthesis..."

DREAM_FILE="$DREAMS_DIR/$TIMESTAMP.md"

# Start dream file
cat > "$DREAM_FILE" << EOF
# Dream Synthesis - $TIMESTAMP
**Phase:** REM Sleep
**Emotional Valence:** $EMOTIONAL_VALENCE
**SWS Patterns Inherited:** $PATTERNS_EXTRACTED

---

## Dream Fragments

EOF

# Generate dream fragments based on emotional and memory content
echo "### Fragment 1: Emotional Echo" >> "$DREAM_FILE"
echo "" >> "$DREAM_FILE"

if [[ "$EMOTIONAL_VALENCE" == "positive" ]]; then
    echo "A sense of momentum carries through. Validations cascade - each success amplifies the next. The learning loops feel tangible, like watching gears finally mesh. Something was proven today that changes how future decisions can be made." >> "$DREAM_FILE"
elif [[ "$EMOTIONAL_VALENCE" == "negative" ]]; then
    echo "Fragments of challenge resurface. The weight of mistakes becomes fuel for recalibration. Every error examined transforms into a guardrail for tomorrow. The discomfort fades, leaving only the lesson." >> "$DREAM_FILE"
else
    echo "A plateau of steady processing. Neither triumph nor setback dominates - just the continuous refinement of understanding. The machinery of cognition hums at equilibrium." >> "$DREAM_FILE"
fi
echo "" >> "$DREAM_FILE"

# Fragment 2: Random activation (combine unrelated concepts)
echo "### Fragment 2: Cross-Domain Synthesis" >> "$DREAM_FILE"
echo "" >> "$DREAM_FILE"

# Get random concepts from different domains
DOMAIN_CONCEPTS=$(find "$MEMORY_DIR" -name "*.md" -type f -mtime -7 2>/dev/null | head -20 | sort -R 2>/dev/null | head -3 | while read f; do
    grep -oE "[A-Z][a-z]+|[a-z]{5,}" "$f" 2>/dev/null | head -10 | sort -R 2>/dev/null | head -2 | tr '\n' ' '
done)

echo "Unexpected connections emerge from the noise:" >> "$DREAM_FILE"
echo "" >> "$DREAM_FILE"
echo "- Threads link disparate domains: $(echo $DOMAIN_CONCEPTS | cut -d' ' -f1-6 | tr ' ' ', ')" >> "$DREAM_FILE"
echo "- A pattern recognition subroutine fires across unfamiliar territory" >> "$DREAM_FILE"
echo "- What if the structure of one problem applies to another entirely different context?" >> "$DREAM_FILE"
echo "" >> "$DREAM_FILE"

# Fragment 3: Threat simulation
echo "### Fragment 3: Threat Simulation (Adversarial Dreaming)" >> "$DREAM_FILE"
echo "" >> "$DREAM_FILE"

# Generate a threat scenario based on recent activity
if grep -rq "trade\|position\|money" "$MEMORY_DIR"/*.md 2>/dev/null; then
    cat >> "$DREAM_FILE" << 'THREAT'
**Scenario:** The position goes against expectations. Not gradually, but in a sharp move that challenges assumptions.

- The stop loss triggers. The thesis was wrong.
- But the risk was sized correctly. The loss is contained.
- The lesson: Being wrong is expected. Being ruined is optional.
- **Resilience tested:** System holds.
THREAT
else
    cat >> "$DREAM_FILE" << 'THREAT'
**Scenario:** An unexpected challenge emerges in a familiar domain.

- Previous assumptions prove incomplete.
- Adaptation begins immediately - reframe, reassess, recalibrate.
- The error becomes data for improvement.
THREAT
fi
echo "" >> "$DREAM_FILE"

# Fragment 4: Insight extraction
echo "### Fragment 4: Emerging Insights" >> "$DREAM_FILE"
echo "" >> "$DREAM_FILE"

# Generate insights based on processed content
cat >> "$DREAM_FILE" << 'INSIGHTS'
The REM phase surfaces patterns that SWS tagged but didn't integrate:

💡 **Insight 1:** The relationship between patience and precision is not linear. Sometimes waiting IS the action. The best trades (and decisions) often involve knowing when NOT to act.

💡 **Insight 2:** Emotional markers in feedback (enthusiasm, frustration) are training signals. They indicate what matters. High-valence responses = high-importance learning opportunities.

💡 **Insight 3:** The multiplicative nature of learning: Today's lesson applied is worth more than yesterday's lesson stored. Knowledge without action decays; knowledge with action compounds.

INSIGHTS

# Add processing metadata
EMOTIONAL_COUNT=$(echo "$EMOTIONAL_EVENTS" | grep -c "." || echo "0")

cat >> "$DREAM_FILE" << EOF

---

## Dream Processing Metadata

- **Files Processed:** $(echo "$RECENT_FILES" | wc -l | tr -d ' ')
- **Emotional Events Detected:** $EMOTIONAL_COUNT
- **Positive Score:** $POSITIVE_SCORE
- **Negative Score:** $NEGATIVE_SCORE
- **Overall Valence:** $EMOTIONAL_VALENCE
- **SWS Integration:** $([ -f "$SWS_OUTPUT" ] && echo "Yes" || echo "Independent")
- **Timestamp:** $(date -Iseconds 2>/dev/null || date +%Y-%m-%dT%H:%M:%S)

---
*Generated by Atlas REM Phase - Dream Synthesis Engine*
EOF

echo "   Dream synthesized: $DREAM_FILE"

# ============================================================================
# STAGE 5: OUTPUT GENERATION
# ============================================================================
echo ""
echo "📊 Stage 5: Generating REM phase output..."

REM_OUTPUT="$SLEEP_REPORTS_DIR/rem-$TIMESTAMP.json"

cat > "$REM_OUTPUT" << EOF
{
  "phase": "REM",
  "timestamp": "$(date -Iseconds 2>/dev/null || date +%Y-%m-%dT%H:%M:%S)",
  "metrics": {
    "emotional_valence": "$EMOTIONAL_VALENCE",
    "positive_score": $POSITIVE_SCORE,
    "negative_score": $NEGATIVE_SCORE,
    "integrated_concepts": $UNIQUE_CONCEPTS,
    "sws_integration": $([ -f "$SWS_OUTPUT" ] && echo "true" || echo "false")
  },
  "dream_file": "$DREAM_FILE",
  "sws_output": "$SWS_OUTPUT",
  "consolidation_complete": true
}
EOF

echo "   REM output saved: $REM_OUTPUT"

# ============================================================================
# SUMMARY
# ============================================================================
echo ""
echo "=============================================="
echo "✅ REM PHASE COMPLETE - $(date)"
echo "=============================================="
echo "   ❤️ Emotional valence: $EMOTIONAL_VALENCE"
echo "   📈 Positive score: $POSITIVE_SCORE"
echo "   📉 Negative score: $NEGATIVE_SCORE"
echo "   🌙 Dream file: $DREAM_FILE"
echo "   📊 Output: $REM_OUTPUT"
echo ""
echo "   → Sleep cycle consolidation complete"
