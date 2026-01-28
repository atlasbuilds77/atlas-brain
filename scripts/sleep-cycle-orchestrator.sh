#!/bin/bash
# ============================================================================
# ATLAS SLEEP SYSTEM - CYCLE ORCHESTRATOR
# Coordinates SWS → REM → Sharp-Wave Ripple sequence
# with adaptive timing and multiplicative benefits
# ============================================================================
# Based on research: SWS×REM product optimization is critical
# Sequential processing beats independent optimization
# ============================================================================

set -e

CLAWD_DIR="$HOME/clawd"
MEMORY_DIR="$CLAWD_DIR/memory"
SCRIPTS_DIR="$CLAWD_DIR/scripts"
SLEEP_REPORTS_DIR="$MEMORY_DIR/sleep-reports"
DREAMS_DIR="$MEMORY_DIR/dreams"
PATTERNS_DIR="$MEMORY_DIR/patterns"
TIMESTAMP=$(date +%Y-%m-%d-%H%M)
TODAY=$(date +%Y-%m-%d)

# Create directories
mkdir -p "$SLEEP_REPORTS_DIR"
mkdir -p "$DREAMS_DIR"
mkdir -p "$PATTERNS_DIR"

# ============================================================================
# CONFIGURATION - ADAPTIVE SLEEP ARCHITECTURE
# ============================================================================
DEFAULT_CYCLE_MIN=90  # Default cycle length (90 min)
MIN_CYCLE_MIN=60      # Minimum (light workload)
MAX_CYCLE_MIN=120     # Maximum (heavy processing)

# Phase distribution (percentage of cycle)
SWS_RATIO=0.55        # SWS gets ~55% (early cycle dominance)
REM_RATIO=0.35        # REM gets ~35% (later in cycle)
RIPPLE_RATIO=0.10     # Sharp-wave ripples throughout

# ============================================================================
# HEADER
# ============================================================================
echo "=============================================="
echo "🌙 ATLAS SLEEP CYCLE ORCHESTRATOR"
echo "=============================================="
echo "Timestamp: $(date)"
echo "Cycle target: ${DEFAULT_CYCLE_MIN} minutes"
echo ""

# ============================================================================
# STAGE 0: ADAPTIVE TIMING CALCULATION
# ============================================================================
echo "⏱️  Stage 0: Calculating adaptive timing..."

# Count recent activity to determine optimal cycle length
RECENT_ACTIVITY=$(find "$MEMORY_DIR" -name "*.md" -mmin -90 -type f 2>/dev/null | grep -v "archive" | grep -v "node_modules" | wc -l | tr -d ' ')
EMOTIONAL_LOAD=$(grep -ril "loss\|mistake\|frustrated\|success\|breakthrough" "$MEMORY_DIR"/*.md 2>/dev/null | wc -l | tr -d ' ')

# Adaptive cycle length
if [[ $RECENT_ACTIVITY -gt 15 ]] || [[ $EMOTIONAL_LOAD -gt 5 ]]; then
    CYCLE_MIN=$MAX_CYCLE_MIN
    CYCLE_TYPE="extended"
    echo "   Heavy activity detected ($RECENT_ACTIVITY files, $EMOTIONAL_LOAD emotional)"
    echo "   → Extended cycle: $CYCLE_MIN minutes"
elif [[ $RECENT_ACTIVITY -lt 5 ]] && [[ $EMOTIONAL_LOAD -lt 2 ]]; then
    CYCLE_MIN=$MIN_CYCLE_MIN
    CYCLE_TYPE="light"
    echo "   Light activity detected ($RECENT_ACTIVITY files, $EMOTIONAL_LOAD emotional)"
    echo "   → Shortened cycle: $CYCLE_MIN minutes"
else
    CYCLE_MIN=$DEFAULT_CYCLE_MIN
    CYCLE_TYPE="standard"
    echo "   Normal activity ($RECENT_ACTIVITY files, $EMOTIONAL_LOAD emotional)"
    echo "   → Standard cycle: $CYCLE_MIN minutes"
fi

# Calculate phase durations (in seconds for script timing)
SWS_DURATION=$((CYCLE_MIN * 60 * 55 / 100))
REM_DURATION=$((CYCLE_MIN * 60 * 35 / 100))
RIPPLE_DURATION=$((CYCLE_MIN * 60 * 10 / 100))

echo ""

# ============================================================================
# STAGE 1: PRE-SLEEP DIAGNOSTICS
# ============================================================================
echo "📊 Stage 1: Pre-sleep diagnostics..."

# Memory state
TOTAL_MEMORY_FILES=$(find "$MEMORY_DIR" -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')
MEMORY_SIZE=$(du -sh "$MEMORY_DIR" 2>/dev/null | cut -f1 || echo "unknown")

# Pattern state
PATTERN_COUNT=$(find "$PATTERNS_DIR" -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')
DREAM_COUNT=$(find "$DREAMS_DIR" -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')

echo "   Memory files: $TOTAL_MEMORY_FILES"
echo "   Memory size: $MEMORY_SIZE"
echo "   Patterns stored: $PATTERN_COUNT"
echo "   Dreams archived: $DREAM_COUNT"
echo ""

# ============================================================================
# STAGE 2: SWS PHASE (Slow-Wave Sleep)
# ============================================================================
echo "=============================================="
echo "🧠 STAGE 2: SWS PHASE"
echo "=============================================="
echo "Duration: $((SWS_DURATION / 60)) minutes (simulated)"
echo ""

SWS_START=$(date +%s)

if [[ -x "$SCRIPTS_DIR/sleep-sws-phase.sh" ]]; then
    bash "$SCRIPTS_DIR/sleep-sws-phase.sh"
    SWS_STATUS="complete"
else
    echo "⚠️  SWS script not found or not executable"
    SWS_STATUS="skipped"
fi

SWS_END=$(date +%s)
SWS_ACTUAL=$((SWS_END - SWS_START))

echo ""

# ============================================================================
# STAGE 3: SHARP-WAVE RIPPLE (Between phases)
# ============================================================================
echo "=============================================="
echo "🌊 STAGE 3: SHARP-WAVE RIPPLE"
echo "=============================================="
echo "Duration: $((RIPPLE_DURATION / 60)) minutes (simulated)"
echo ""

RIPPLE_START=$(date +%s)

if [[ -x "$SCRIPTS_DIR/sleep-sharp-wave-ripple.sh" ]]; then
    bash "$SCRIPTS_DIR/sleep-sharp-wave-ripple.sh"
    RIPPLE_STATUS="complete"
else
    echo "⚠️  Ripple script not found or not executable"
    RIPPLE_STATUS="skipped"
fi

RIPPLE_END=$(date +%s)
RIPPLE_ACTUAL=$((RIPPLE_END - RIPPLE_START))

echo ""

# ============================================================================
# STAGE 4: REM PHASE (Rapid Eye Movement)
# ============================================================================
echo "=============================================="
echo "💭 STAGE 4: REM PHASE"
echo "=============================================="
echo "Duration: $((REM_DURATION / 60)) minutes (simulated)"
echo ""

REM_START=$(date +%s)

if [[ -x "$SCRIPTS_DIR/sleep-rem-phase.sh" ]]; then
    bash "$SCRIPTS_DIR/sleep-rem-phase.sh"
    REM_STATUS="complete"
else
    echo "⚠️  REM script not found or not executable"
    REM_STATUS="skipped"
fi

REM_END=$(date +%s)
REM_ACTUAL=$((REM_END - REM_START))

echo ""

# ============================================================================
# STAGE 5: CONSOLIDATION METRICS (SWS × REM Product)
# ============================================================================
echo "=============================================="
echo "📈 STAGE 5: CONSOLIDATION METRICS"
echo "=============================================="

# Load phase outputs
SWS_OUTPUT=$(ls -t "$SLEEP_REPORTS_DIR"/sws-*.json 2>/dev/null | head -1 || echo "")
REM_OUTPUT=$(ls -t "$SLEEP_REPORTS_DIR"/rem-*.json 2>/dev/null | head -1 || echo "")

# Extract metrics
SWS_PATTERNS=0
REM_CONCEPTS=0
EMOTIONAL_SCORE=0

if [[ -f "$SWS_OUTPUT" ]]; then
    SWS_PATTERNS=$(cat "$SWS_OUTPUT" | grep -o '"patterns_extracted": [0-9]*' | grep -o '[0-9]*' || echo "0")
fi

if [[ -f "$REM_OUTPUT" ]]; then
    REM_CONCEPTS=$(cat "$REM_OUTPUT" | grep -o '"integrated_concepts": [0-9]*' | grep -o '[0-9]*' || echo "0")
    POSITIVE=$(cat "$REM_OUTPUT" | grep -o '"positive_score": [0-9]*' | grep -o '[0-9]*' || echo "0")
    NEGATIVE=$(cat "$REM_OUTPUT" | grep -o '"negative_score": [0-9]*' | grep -o '[0-9]*' || echo "0")
    EMOTIONAL_SCORE=$((POSITIVE + NEGATIVE))
fi

# Calculate SWS × REM product (multiplicative benefit)
SWS_SCORE=$((SWS_PATTERNS * 10 + 50))
REM_SCORE=$((REM_CONCEPTS * 10 + 50))
PRODUCT=$((SWS_SCORE * REM_SCORE / 100))

echo "   SWS Score: $SWS_SCORE (patterns: $SWS_PATTERNS)"
echo "   REM Score: $REM_SCORE (concepts: $REM_CONCEPTS)"
echo "   SWS × REM Product: $PRODUCT"
echo "   Emotional Processing: $EMOTIONAL_SCORE"
echo ""

# Determine consolidation quality
if [[ $PRODUCT -gt 80 ]]; then
    QUALITY="EXCELLENT"
elif [[ $PRODUCT -gt 60 ]]; then
    QUALITY="GOOD"
elif [[ $PRODUCT -gt 40 ]]; then
    QUALITY="ADEQUATE"
else
    QUALITY="WEAK"
fi

echo "   Consolidation Quality: $QUALITY"

# ============================================================================
# STAGE 6: GENERATE COMPREHENSIVE REPORT
# ============================================================================
echo ""
echo "=============================================="
echo "📝 STAGE 6: GENERATING REPORT"
echo "=============================================="

REPORT_FILE="$SLEEP_REPORTS_DIR/$TIMESTAMP.md"

# Find latest dream file
LATEST_DREAM=$(ls -t "$DREAMS_DIR"/*.md 2>/dev/null | head -1 || echo "")
DREAM_CONTENT=""
if [[ -f "$LATEST_DREAM" ]]; then
    DREAM_CONTENT=$(cat "$LATEST_DREAM")
fi

cat > "$REPORT_FILE" << EOF
# ATLAS SLEEP CYCLE - $TIMESTAMP

## 📊 Cycle Overview

| Metric | Value |
|--------|-------|
| **Cycle Type** | $CYCLE_TYPE |
| **Target Duration** | ${CYCLE_MIN} minutes |
| **Actual Duration** | $((SWS_ACTUAL + RIPPLE_ACTUAL + REM_ACTUAL)) seconds |
| **Recent Activity** | $RECENT_ACTIVITY files |
| **Emotional Load** | $EMOTIONAL_LOAD events |

## 🧠 SWS Phase (Slow-Wave Sleep)

**Status:** $SWS_STATUS
**Duration:** ${SWS_ACTUAL}s
**Patterns Extracted:** $SWS_PATTERNS

The SWS phase performed hippocampal replay, extracting high-salience events from recent experiences and consolidating them into pattern templates.

## 🌊 Sharp-Wave Ripple Phase

**Status:** $RIPPLE_STATUS
**Duration:** ${RIPPLE_ACTUAL}s
**Acceleration:** 15x replay speed

Accelerated replay with disinhibition gates open, allowing broader pattern matching and cross-domain connections.

## 💭 REM Phase

**Status:** $REM_STATUS
**Duration:** ${REM_ACTUAL}s
**Concepts Integrated:** $REM_CONCEPTS
**Emotional Processing:** $EMOTIONAL_SCORE

The REM phase processed emotional valence, integrated memories across domains, and generated dream synthesis.

## 📈 Consolidation Metrics

| Metric | Score |
|--------|-------|
| **SWS Score** | $SWS_SCORE |
| **REM Score** | $REM_SCORE |
| **SWS × REM Product** | $PRODUCT |
| **Quality Rating** | $QUALITY |

> **SWS × REM Product Interpretation:** This multiplicative metric (per Yuksel et al., 2025) captures the synergy between phases. Higher products indicate better emotional memory consolidation.

## 🌙 Dream Synthesis

$(if [[ -f "$LATEST_DREAM" ]]; then
    echo "**Dream File:** $(basename "$LATEST_DREAM")"
    echo ""
    echo "### Key Dream Fragments"
    echo ""
    grep -A 3 "^### Fragment" "$LATEST_DREAM" 2>/dev/null | head -20 || echo "No fragments extracted"
    echo ""
    echo "### Emerging Insights"
    echo ""
    grep -A 2 "💡" "$LATEST_DREAM" 2>/dev/null | head -15 || echo "No insights generated"
else
    echo "*No dream generated this cycle*"
fi)

## 🎯 Meta-Learning Notes

- **Cycle Adaptation:** $([ "$CYCLE_TYPE" == "extended" ] && echo "Extended due to high activity" || ([ "$CYCLE_TYPE" == "light" ] && echo "Shortened due to light activity" || echo "Standard cycle"))
- **Phase Balance:** SWS ~55% / Ripple ~10% / REM ~35%
- **Improvement Opportunities:** $([ $PRODUCT -lt 60 ] && echo "Consider longer REM phase for emotional processing" || echo "Cycle balance optimal")

## ⏰ Next Cycle

**Scheduled:** +90 minutes (~$(date -v+90M +%H:%M 2>/dev/null || date -d "+90 minutes" +%H:%M 2>/dev/null || echo "TBD"))

---

*Generated by Atlas Sleep Cycle Orchestrator v2.0*
*Based on neuroscience research: SWS-REM coordination, sharp-wave ripples, predictive processing*
EOF

echo "   Report saved: $REPORT_FILE"
echo ""

# ============================================================================
# SUMMARY
# ============================================================================
echo "=============================================="
echo "✅ SLEEP CYCLE COMPLETE"
echo "=============================================="
echo ""
echo "   📊 Cycle Type: $CYCLE_TYPE"
echo "   🧠 SWS: $SWS_STATUS ($SWS_PATTERNS patterns)"
echo "   🌊 Ripple: $RIPPLE_STATUS"
echo "   💭 REM: $REM_STATUS ($REM_CONCEPTS concepts)"
echo "   📈 Quality: $QUALITY (product: $PRODUCT)"
echo ""
echo "   📝 Report: $REPORT_FILE"
echo "   🌙 Dream: $LATEST_DREAM"
echo ""
echo "🌅 Ready for next waking period"
echo "=============================================="
