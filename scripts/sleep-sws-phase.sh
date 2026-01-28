#!/bin/bash
# ============================================================================
# ATLAS SLEEP SYSTEM - SWS (SLOW-WAVE SLEEP) PHASE
# Hippocampal replay simulation with sharp-wave ripple acceleration
# ============================================================================
# Based on research: SWS creates neocortex-dependent gist-like representations
# through accelerated replay and controlled disinhibition
# ============================================================================

set -e

CLAWD_DIR="$HOME/clawd"
MEMORY_DIR="$CLAWD_DIR/memory"
PATTERNS_DIR="$MEMORY_DIR/patterns"
SLEEP_REPORTS_DIR="$MEMORY_DIR/sleep-reports"
TIMESTAMP=$(date +%Y-%m-%d-%H%M)
TODAY=$(date +%Y-%m-%d)

# Create directories
mkdir -p "$PATTERNS_DIR"
mkdir -p "$SLEEP_REPORTS_DIR"

# Output file for this phase
SWS_OUTPUT="$SLEEP_REPORTS_DIR/sws-$TIMESTAMP.json"

echo "🧠 SWS PHASE INITIATED - $(date)"
echo "=============================================="

# ============================================================================
# STAGE 1: EXTRACT RECENT EXPERIENCES (Last 90 min)
# ============================================================================
echo ""
echo "📥 Stage 1: Extracting recent experiences..."

# Find files modified in last 90 minutes
RECENT_FILES=$(find "$MEMORY_DIR" -name "*.md" -mmin -90 -type f 2>/dev/null | grep -v "archive" | grep -v "node_modules" || echo "")

if [[ -z "$RECENT_FILES" ]]; then
    echo "   No recent experiences found. Extending to 3 hours..."
    RECENT_FILES=$(find "$MEMORY_DIR" -name "*.md" -mmin -180 -type f 2>/dev/null | grep -v "archive" | grep -v "node_modules" || echo "")
fi

EXPERIENCE_COUNT=$(echo "$RECENT_FILES" | grep -c "." || echo "0")
echo "   Found $EXPERIENCE_COUNT recent experience files"

# ============================================================================
# STAGE 2: IDENTIFY HIGH-SALIENCE EVENTS
# ============================================================================
echo ""
echo "⚡ Stage 2: Identifying high-salience events..."

# Score function using grep counts (bash 3 compatible)
score_file() {
    local file="$1"
    local content
    content=$(cat "$file" 2>/dev/null || echo "")
    local score=0
    local count
    
    # High-salience keywords with weights (use tr -d to ensure clean numbers)
    count=$(echo "$content" | grep -ic "CRITICAL" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 100))
    count=$(echo "$content" | grep -ic "IMPORTANT" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 80))
    count=$(echo "$content" | grep -ic "mistake" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 90))
    count=$(echo "$content" | grep -ic "learned" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 85))
    count=$(echo "$content" | grep -ic "insight" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 85))
    count=$(echo "$content" | grep -ic "money" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 70))
    count=$(echo "$content" | grep -ic "position" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 70))
    count=$(echo "$content" | grep -ic "trade" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 70))
    count=$(echo "$content" | grep -ic "breakout" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 75))
    count=$(echo "$content" | grep -ic "reversal" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 75))
    count=$(echo "$content" | grep -ic "pattern" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 65))
    count=$(echo "$content" | grep -ic "remember" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 80))
    count=$(echo "$content" | grep -ic "never" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 75))
    count=$(echo "$content" | grep -ic "always" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 75))
    count=$(echo "$content" | grep -ic "key" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 60))
    count=$(echo "$content" | grep -ic "decision" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 70))
    count=$(echo "$content" | grep -ic "validated" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 80))
    count=$(echo "$content" | grep -ic "proof" 2>/dev/null | tr -d '[:space:]' || echo "0"); score=$((score + count * 85))
    
    # Divide by 2 to normalize
    echo $((score / 2))
}

# Scan for high-salience content
HIGH_SALIENCE_EVENTS=""
HIGH_SALIENCE_COUNT=0

for file in $RECENT_FILES; do
    if [[ -f "$file" ]]; then
        filename=$(basename "$file")
        file_score=$(score_file "$file")
        
        # Boost recent modifications
        if [[ "$filename" =~ ^2026 ]]; then
            file_score=$((file_score + 20))
        fi
        
        if [[ $file_score -gt 50 ]]; then
            HIGH_SALIENCE_EVENTS="$HIGH_SALIENCE_EVENTS$file:$file_score
"
            echo "   ✓ High salience: $filename (score: $file_score)"
            HIGH_SALIENCE_COUNT=$((HIGH_SALIENCE_COUNT + 1))
        fi
    fi
done

echo "   Total high-salience events: $HIGH_SALIENCE_COUNT"

# ============================================================================
# STAGE 3: SHARP-WAVE RIPPLE SIMULATION (10-20x Accelerated Replay)
# ============================================================================
echo ""
echo "🌊 Stage 3: Sharp-wave ripple simulation (accelerated replay)..."

# Extract key patterns from high-salience content
PATTERNS_EXTRACTED=0
PATTERN_FILE="$PATTERNS_DIR/sws-$TIMESTAMP.md"

cat > "$PATTERN_FILE" << 'EOF'
# SWS Pattern Extraction
## Sharp-Wave Ripple Accelerated Replay

EOF

echo "**Extraction Time:** $(date)" >> "$PATTERN_FILE"
echo "**Files Processed:** $EXPERIENCE_COUNT" >> "$PATTERN_FILE"
echo "" >> "$PATTERN_FILE"
echo "## Extracted Patterns" >> "$PATTERN_FILE"
echo "" >> "$PATTERN_FILE"

# Sort by score and process top 10
echo "$HIGH_SALIENCE_EVENTS" | sort -t: -k2 -rn | head -10 | while read entry; do
    if [[ -n "$entry" ]]; then
        file=$(echo "$entry" | cut -d: -f1)
        score=$(echo "$entry" | cut -d: -f2)
        
        if [[ -f "$file" ]]; then
            filename=$(basename "$file")
            echo "### Pattern from: $filename (salience: $score)" >> "$PATTERN_FILE"
            echo "" >> "$PATTERN_FILE"
            
            # Extract key sentences (lines with high-salience keywords)
            grep -iE "CRITICAL|IMPORTANT|learned|insight|mistake|pattern|key|proof|validated" "$file" 2>/dev/null | head -5 >> "$PATTERN_FILE" || true
            echo "" >> "$PATTERN_FILE"
            
            # Extract any bullet points (often contain key info)
            grep -E "^-|^\*|^[0-9]+\." "$file" 2>/dev/null | head -5 >> "$PATTERN_FILE" || true
            echo "" >> "$PATTERN_FILE"
            
            PATTERNS_EXTRACTED=$((PATTERNS_EXTRACTED + 1))
        fi
    fi
done

# Count patterns actually extracted
PATTERNS_EXTRACTED=$(grep -c "^### Pattern from:" "$PATTERN_FILE" || echo "0")

echo "   Patterns extracted: $PATTERNS_EXTRACTED"
echo "   Saved to: $PATTERN_FILE"

# ============================================================================
# STAGE 4: SYNAPTIC HOMEOSTASIS (Strengthen successful, prune weak)
# ============================================================================
echo ""
echo "⚖️ Stage 4: Synaptic homeostasis..."

# Identify repeated patterns (strengthening)
if [[ -d "$PATTERNS_DIR" ]]; then
    # Look for patterns that appear across multiple files
    for kw in "learned" "insight" "pattern" "rule" "always" "never"; do
        count=$(find "$PATTERNS_DIR" -name "*.md" -exec grep -il "$kw" {} \; 2>/dev/null | wc -l | tr -d ' ')
        if [[ $count -gt 3 ]]; then
            echo "   📈 Strengthening: '$kw' pattern (found in $count files)"
        fi
    done
fi

# Identify stale patterns (candidates for pruning)
STALE_FILES=$(find "$PATTERNS_DIR" -name "*.md" -mtime +7 2>/dev/null | wc -l | tr -d ' ')
echo "   📉 Stale pattern files (>7 days old): $STALE_FILES"

# ============================================================================
# STAGE 5: GENERATE SWS OUTPUT
# ============================================================================
echo ""
echo "📊 Stage 5: Generating SWS phase output..."

# Get top 5 high salience files for JSON
TOP_FILES=$(echo "$HIGH_SALIENCE_EVENTS" | sort -t: -k2 -rn | head -5)

cat > "$SWS_OUTPUT" << EOF
{
  "phase": "SWS",
  "timestamp": "$(date -Iseconds 2>/dev/null || date +%Y-%m-%dT%H:%M:%S)",
  "metrics": {
    "recent_files_processed": $EXPERIENCE_COUNT,
    "high_salience_events": $HIGH_SALIENCE_COUNT,
    "patterns_extracted": $PATTERNS_EXTRACTED,
    "stale_patterns": $STALE_FILES
  },
  "high_salience_files": [
$(echo "$TOP_FILES" | while read entry; do
    if [[ -n "$entry" ]]; then
        file=$(echo "$entry" | cut -d: -f1)
        score=$(echo "$entry" | cut -d: -f2)
        echo "    {\"file\": \"$file\", \"salience\": $score},"
    fi
done | sed '$ s/,$//')
  ],
  "pattern_file": "$PATTERN_FILE",
  "ready_for_rem": true
}
EOF

echo "   SWS output saved: $SWS_OUTPUT"

# ============================================================================
# SUMMARY
# ============================================================================
echo ""
echo "=============================================="
echo "✅ SWS PHASE COMPLETE - $(date)"
echo "=============================================="
echo "   📥 Experiences processed: $EXPERIENCE_COUNT"
echo "   ⚡ High-salience events: $HIGH_SALIENCE_COUNT"
echo "   🌊 Patterns extracted: $PATTERNS_EXTRACTED"
echo "   📊 Output: $SWS_OUTPUT"
echo ""
echo "   → Ready for REM phase"
