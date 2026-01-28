#!/bin/bash
# ============================================================================
# ATLAS SLEEP SYSTEM - SHARP-WAVE RIPPLE SIMULATION
# Accelerated replay (10-20x) with disinhibition for rapid consolidation
# ============================================================================
# Based on research: Sharp-wave ripples in CA1 hippocampus replay recent
# experiences at 10-20x speed, coordinated with cortical sleep spindles
# for efficient memory transfer to neocortex
# ============================================================================

set -e

CLAWD_DIR="$HOME/clawd"
MEMORY_DIR="$CLAWD_DIR/memory"
PATTERNS_DIR="$MEMORY_DIR/patterns"
RIPPLES_DIR="$MEMORY_DIR/patterns/ripples"
TIMESTAMP=$(date +%Y-%m-%d-%H%M)

# Create directories
mkdir -p "$RIPPLES_DIR"

echo "🌊 SHARP-WAVE RIPPLE SIMULATION - $(date)"
echo "=============================================="

# ============================================================================
# CONFIGURATION
# ============================================================================
REPLAY_SPEED=15  # 15x acceleration (middle of 10-20x range)
RIPPLE_DURATION_MS=80  # Typical ripple: 50-100ms
MAX_EXPERIENCES=20  # Process top 20 experiences per ripple sequence

# ============================================================================
# STAGE 1: IDENTIFY REPLAY CANDIDATES
# ============================================================================
echo ""
echo "📂 Stage 1: Identifying replay candidates..."

# Find recent experiences (prioritize last 90 min, extend to 3 hours if needed)
RECENT_FILES=$(find "$MEMORY_DIR" -name "*.md" -mmin -90 -type f 2>/dev/null | grep -v "archive" | grep -v "node_modules" | grep -v "patterns" || echo "")

if [[ $(echo "$RECENT_FILES" | wc -l | tr -d ' ') -lt 5 ]]; then
    RECENT_FILES=$(find "$MEMORY_DIR" -name "*.md" -mmin -180 -type f 2>/dev/null | grep -v "archive" | grep -v "node_modules" | grep -v "patterns" || echo "")
fi

echo "   Found $(echo "$RECENT_FILES" | grep -c "." || echo "0") candidate files"

# ============================================================================
# STAGE 2: SALIENCE SCORING FOR REPLAY PRIORITY
# ============================================================================
echo ""
echo "⚡ Stage 2: Scoring replay priority..."

# Create temp file for scored candidates
CANDIDATE_FILE="/tmp/ripple_candidates_$$.txt"
> "$CANDIDATE_FILE"

# Priority factors: prediction error × emotional salience × novelty
for file in $RECENT_FILES; do
    if [[ -f "$file" ]]; then
        content=$(cat "$file" 2>/dev/null || echo "")
        filename=$(basename "$file")
        
        score=0
        
        # Emotional salience (high valence = higher priority)
        emotion_hits=$(echo "$content" | grep -ioE "success|failure|profit|loss|learned|mistake|breakthrough|frustrat" | wc -l | tr -d ' ')
        score=$((score + emotion_hits * 10))
        
        # Prediction error (unexpected outcomes)
        surprise_hits=$(echo "$content" | grep -ioE "unexpected|surprise|different|changed|but|however|contrary" | wc -l | tr -d ' ')
        score=$((score + surprise_hits * 15))
        
        # Novelty (new information)
        novel_hits=$(echo "$content" | grep -ioE "first|new|discovered|realized|insight|never before" | wc -l | tr -d ' ')
        score=$((score + novel_hits * 12))
        
        # Recency bonus (using stat for macOS compatibility)
        if [[ -f "$file" ]]; then
            mtime=$(stat -f %m "$file" 2>/dev/null || stat -c %Y "$file" 2>/dev/null || echo "0")
            now=$(date +%s)
            age_min=$(( (now - mtime) / 60 ))
            if [[ $age_min -lt 30 ]]; then
                score=$((score + 30))
            elif [[ $age_min -lt 60 ]]; then
                score=$((score + 20))
            elif [[ $age_min -lt 90 ]]; then
                score=$((score + 10))
            fi
        fi
        
        echo "$score:$file" >> "$CANDIDATE_FILE"
    fi
done

# Sort by score and get top experiences
sort -rn "$CANDIDATE_FILE" | head -$MAX_EXPERIENCES > /tmp/ripple_sorted_$$.txt
mv /tmp/ripple_sorted_$$.txt "$CANDIDATE_FILE"

echo "   Top experiences for replay:"
head -5 "$CANDIDATE_FILE" | while read line; do
    score=$(echo "$line" | cut -d: -f1)
    file=$(echo "$line" | cut -d: -f2-)
    echo "   - $(basename "$file") (score: $score)"
done

# ============================================================================
# STAGE 3: ACCELERATED REPLAY (10-20x speed simulation)
# ============================================================================
echo ""
echo "🏃 Stage 3: Accelerated replay at ${REPLAY_SPEED}x speed..."

RIPPLE_OUTPUT="$RIPPLES_DIR/ripple-$TIMESTAMP.md"

cat > "$RIPPLE_OUTPUT" << EOF
# Sharp-Wave Ripple Sequence - $TIMESTAMP
**Replay Speed:** ${REPLAY_SPEED}x
**Ripple Duration:** ${RIPPLE_DURATION_MS}ms equivalent
**Experiences Processed:** $(wc -l < "$CANDIDATE_FILE" | tr -d ' ')

---

## Ripple Sequence

EOF

RIPPLE_COUNT=0
while read line; do
    if [[ -n "$line" ]]; then
        score=$(echo "$line" | cut -d: -f1)
        file=$(echo "$line" | cut -d: -f2-)
        filename=$(basename "$file")
        
        if [[ -f "$file" ]]; then
            RIPPLE_COUNT=$((RIPPLE_COUNT + 1))
            
            echo "### Ripple $RIPPLE_COUNT: $filename" >> "$RIPPLE_OUTPUT"
            echo "**Priority Score:** $score" >> "$RIPPLE_OUTPUT"
            echo "" >> "$RIPPLE_OUTPUT"
            
            # Extract core content (accelerated = compressed)
            # Get the first header and key bullet points
            head -20 "$file" | grep -E "^#|^-|^[0-9]+\." | head -5 >> "$RIPPLE_OUTPUT" 2>/dev/null || true
            
            # Extract any lines with high-value keywords
            grep -iE "learned|insight|key|important|pattern|rule|decision" "$file" 2>/dev/null | head -3 >> "$RIPPLE_OUTPUT" || true
            
            echo "" >> "$RIPPLE_OUTPUT"
        fi
    fi
done < "$CANDIDATE_FILE"

echo "   Completed $RIPPLE_COUNT ripple sequences"

# ============================================================================
# STAGE 4: PATTERN EXTRACTION (Disinhibition gate)
# ============================================================================
echo ""
echo "🔓 Stage 4: Disinhibition-gated pattern extraction..."

# With disinhibition, consolidation accelerates by allowing
# broader pattern matching without normal filtering constraints

cat >> "$RIPPLE_OUTPUT" << 'EOF'

---

## Disinhibited Pattern Extraction

With disinhibition gates open, broader patterns emerge:

EOF

# Extract patterns across all replay content
echo "### Repeated Sequences" >> "$RIPPLE_OUTPUT"
echo "" >> "$RIPPLE_OUTPUT"

# Find frequently appearing words in the processed files
cat "$CANDIDATE_FILE" | cut -d: -f2- | while read f; do
    cat "$f" 2>/dev/null
done | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '\n' | sort | uniq -c | sort -rn | head -20 | while read count word; do
    if [[ $count -gt 3 ]] && [[ ${#word} -gt 4 ]]; then
        echo "- **$word** (×$count)" >> "$RIPPLE_OUTPUT"
    fi
done

echo "" >> "$RIPPLE_OUTPUT"
echo "### Cross-File Patterns" >> "$RIPPLE_OUTPUT"
echo "" >> "$RIPPLE_OUTPUT"

# Find concepts that appear in multiple files
total_files=$(wc -l < "$CANDIDATE_FILE" | tr -d ' ')
for concept in "trade" "learn" "pattern" "decision" "mistake" "insight" "position" "market"; do
    files_with_concept=0
    while read entry; do
        f=$(echo "$entry" | cut -d: -f2-)
        if grep -qi "$concept" "$f" 2>/dev/null; then
            files_with_concept=$((files_with_concept + 1))
        fi
    done < "$CANDIDATE_FILE"
    
    if [[ $files_with_concept -gt 2 ]]; then
        echo "- **$concept**: found in $files_with_concept/$total_files files" >> "$RIPPLE_OUTPUT"
    fi
done

# ============================================================================
# STAGE 5: FEED TO PATTERN DATABASE
# ============================================================================
echo ""
echo "💾 Stage 5: Updating pattern database..."

PATTERN_DB="$PATTERNS_DIR/pattern-database.md"

# Create or update pattern database
if [[ ! -f "$PATTERN_DB" ]]; then
    cat > "$PATTERN_DB" << 'EOF'
# Atlas Pattern Database
**Purpose:** Accumulated patterns from sleep consolidation

---

## Pattern Registry

EOF
fi

# Append new patterns with timestamp
TOP_SCORE=$(head -1 "$CANDIDATE_FILE" | cut -d: -f1 || echo "0")
KEY_CONCEPTS=$(grep -o "^\*\*[a-z]*\*\*" "$RIPPLE_OUTPUT" 2>/dev/null | tr -d '*' | head -5 | tr '\n' ', ' || echo "N/A")

cat >> "$PATTERN_DB" << EOF

### Ripple Sequence $TIMESTAMP
- Experiences processed: $RIPPLE_COUNT
- Top priority score: $TOP_SCORE
- Key concepts: $KEY_CONCEPTS

EOF

echo "   Pattern database updated: $PATTERN_DB"

# ============================================================================
# CLEANUP
# ============================================================================
rm -f "$CANDIDATE_FILE"

# ============================================================================
# SUMMARY
# ============================================================================
echo ""
echo "=============================================="
echo "✅ SHARP-WAVE RIPPLE COMPLETE - $(date)"
echo "=============================================="
echo "   🌊 Ripples executed: $RIPPLE_COUNT"
echo "   🏃 Replay speed: ${REPLAY_SPEED}x"
echo "   📄 Output: $RIPPLE_OUTPUT"
echo "   💾 Pattern DB: $PATTERN_DB"
echo ""
