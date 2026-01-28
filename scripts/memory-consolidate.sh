#!/bin/bash
#
# ATLAS Memory Consolidation System
# Actual implementation of hippocampus → neocortex transfer
#
# What it does:
# 1. HIPPOCAMPUS SCAN: Read recent experiences (daily logs, outcomes)
# 2. PATTERN EXTRACTION: Identify repeated patterns, decisions, learnings
# 3. NEOCORTEX TRANSFER: Update long-term memory files
# 4. SLEEP REPLAY: Strengthen important patterns, prune weak ones
# 5. CLEANUP: Archive old data, maintain memory hygiene
#
# Run: ~/clawd/scripts/memory-consolidate.sh [--full]

set -e

CLAWD_DIR="/Users/atlasbuilds/clawd"
MEMORY_DIR="$CLAWD_DIR/memory"
SCRIPTS_DIR="$CLAWD_DIR/scripts"
LOG_DIR="$MEMORY_DIR/sleep-reports"
ARCHIVE_DIR="$MEMORY_DIR/archive"
PATTERNS_DB="$MEMORY_DIR/patterns/pattern-database.json"
OUTCOME_LOG="$MEMORY_DIR/outcomes/outcome-log.jsonl"

# Ensure directories exist
mkdir -p "$LOG_DIR" "$ARCHIVE_DIR" "$MEMORY_DIR/patterns/archive" "$MEMORY_DIR/outcomes"

DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)
REPORT_FILE="$LOG_DIR/consolidation-$DATE.md"

echo "🌙 ATLAS Memory Consolidation Starting..."
echo "   Date: $DATE $TIME"
echo ""

# Initialize report
cat > "$REPORT_FILE" << EOF
# Memory Consolidation Report
**Date:** $DATE $TIME
**Type:** $(if [[ "$1" == "--full" ]]; then echo "Full Consolidation"; else echo "Standard Consolidation"; fi)

---

## 1. HIPPOCAMPUS SCAN (Recent Experiences)

EOF

# ============================================================
# PHASE 1: HIPPOCAMPUS SCAN (Recent experiences)
# ============================================================

echo "📖 Phase 1: Scanning recent experiences..."

# Count recent daily logs
RECENT_LOGS=$(find "$MEMORY_DIR" -maxdepth 1 -name "2026-*.md" -mtime -7 | wc -l | tr -d ' ')
echo "   Found $RECENT_LOGS daily logs from past 7 days"
echo "- Daily logs (past 7 days): $RECENT_LOGS" >> "$REPORT_FILE"

# Count recent outcomes
if [[ -f "$OUTCOME_LOG" ]]; then
    RECENT_OUTCOMES=$(tail -100 "$OUTCOME_LOG" | wc -l | tr -d ' ')
    SUCCESS_COUNT=$(tail -100 "$OUTCOME_LOG" | grep -c '"outcome": "success"' || echo 0)
    FAILURE_COUNT=$(tail -100 "$OUTCOME_LOG" | grep -c '"outcome": "failure"' || echo 0)
    echo "   Found $RECENT_OUTCOMES recent outcomes (✅ $SUCCESS_COUNT / ❌ $FAILURE_COUNT)"
    echo "- Recent outcomes: $RECENT_OUTCOMES (Success: $SUCCESS_COUNT, Failure: $FAILURE_COUNT)" >> "$REPORT_FILE"
else
    echo "   No outcome log found"
    echo "- No outcome log found" >> "$REPORT_FILE"
fi

# ============================================================
# PHASE 2: PATTERN EXTRACTION
# ============================================================

echo ""
echo "🔍 Phase 2: Extracting patterns from recent experiences..."
echo "" >> "$REPORT_FILE"
echo "## 2. PATTERN EXTRACTION" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Extract keywords/themes from recent daily logs
if [[ $RECENT_LOGS -gt 0 ]]; then
    echo "### Themes from Daily Logs" >> "$REPORT_FILE"
    
    # Find common themes (trading, research, social, decisions)
    TRADING_MENTIONS=$(cat "$MEMORY_DIR"/2026-*.md 2>/dev/null | grep -ci "trade\|position\|profit\|loss\|scalp\|option" || echo 0)
    RESEARCH_MENTIONS=$(cat "$MEMORY_DIR"/2026-*.md 2>/dev/null | grep -ci "research\|learn\|study\|analysis" || echo 0)
    DECISION_MENTIONS=$(cat "$MEMORY_DIR"/2026-*.md 2>/dev/null | grep -ci "decide\|decision\|chose\|choose" || echo 0)
    
    echo "- Trading mentions: $TRADING_MENTIONS" >> "$REPORT_FILE"
    echo "- Research mentions: $RESEARCH_MENTIONS" >> "$REPORT_FILE"
    echo "- Decision mentions: $DECISION_MENTIONS" >> "$REPORT_FILE"
    
    # Extract lessons learned (lines starting with -)
    echo "" >> "$REPORT_FILE"
    echo "### Extracted Insights" >> "$REPORT_FILE"
    grep -h "^- \|^  - \|lesson\|learned\|insight\|realize" "$MEMORY_DIR"/2026-*.md 2>/dev/null | head -10 | while read line; do
        echo "$line" >> "$REPORT_FILE"
    done
fi

# ============================================================
# PHASE 3: NEOCORTEX TRANSFER (Update long-term patterns)
# ============================================================

echo ""
echo "🧠 Phase 3: Updating long-term memory (neocortex)..."
echo "" >> "$REPORT_FILE"
echo "## 3. NEOCORTEX TRANSFER" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Apply time decay to patterns
if [[ -f "$SCRIPTS_DIR/pattern-api.py" ]]; then
    echo "### Pattern Weight Adjustments" >> "$REPORT_FILE"
    
    # Run time decay
    DECAY_RESULT=$(python3 "$SCRIPTS_DIR/pattern-api.py" decay 2>&1)
    echo "$DECAY_RESULT" >> "$REPORT_FILE"
    echo "   $DECAY_RESULT"
    
    # Get pattern stats
    echo "" >> "$REPORT_FILE"
    echo "### Pattern Library Status" >> "$REPORT_FILE"
    python3 "$SCRIPTS_DIR/pattern-api.py" stats >> "$REPORT_FILE" 2>&1 || echo "No patterns yet"
fi

# ============================================================
# PHASE 4: SLEEP REPLAY (Strengthen/prune)
# ============================================================

echo ""
echo "💤 Phase 4: Sleep replay (strengthen important, prune weak)..."
echo "" >> "$REPORT_FILE"
echo "## 4. SLEEP REPLAY" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Strengthen patterns used in successful outcomes today
if [[ -f "$OUTCOME_LOG" ]]; then
    TODAY_OUTCOMES=$(grep "\"timestamp\": \"$DATE" "$OUTCOME_LOG" 2>/dev/null || true)
    if [[ -n "$TODAY_OUTCOMES" ]]; then
        echo "### Today's Pattern Reinforcement" >> "$REPORT_FILE"
        
        # Find successful patterns to strengthen extra
        echo "$TODAY_OUTCOMES" | grep '"outcome": "success"' | while read line; do
            PATTERNS=$(echo "$line" | grep -o '"pattern_ids": \[[^]]*\]' | grep -o '"[^"]*"' | tr -d '"' || true)
            if [[ -n "$PATTERNS" ]]; then
                for p in $PATTERNS; do
                    if [[ "$p" != "pattern_ids" && "$p" != ":" ]]; then
                        echo "- Reinforcing successful pattern: $p" >> "$REPORT_FILE"
                    fi
                done
            fi
        done
    fi
fi

# Prune weak patterns if --full flag
if [[ "$1" == "--full" ]]; then
    echo "" >> "$REPORT_FILE"
    echo "### Pattern Pruning (Full Mode)" >> "$REPORT_FILE"
    PRUNE_RESULT=$(python3 "$SCRIPTS_DIR/pattern-api.py" prune 60 2>&1)
    echo "$PRUNE_RESULT" >> "$REPORT_FILE"
    echo "   $PRUNE_RESULT"
fi

# ============================================================
# PHASE 5: CLEANUP & ARCHIVE
# ============================================================

echo ""
echo "🗄️ Phase 5: Archiving old memories..."
echo "" >> "$REPORT_FILE"
echo "## 5. ARCHIVE & CLEANUP" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Archive daily logs older than 14 days
OLD_LOGS=$(find "$MEMORY_DIR" -maxdepth 1 -name "2026-*.md" -mtime +14 2>/dev/null)
if [[ -n "$OLD_LOGS" ]]; then
    ARCHIVE_MONTH=$(date +%Y-%m)
    ARCHIVE_SUBDIR="$ARCHIVE_DIR/$ARCHIVE_MONTH"
    mkdir -p "$ARCHIVE_SUBDIR"
    
    ARCHIVED_COUNT=0
    for log in $OLD_LOGS; do
        mv "$log" "$ARCHIVE_SUBDIR/"
        ARCHIVED_COUNT=$((ARCHIVED_COUNT + 1))
    done
    echo "- Archived $ARCHIVED_COUNT daily logs to $ARCHIVE_SUBDIR" >> "$REPORT_FILE"
    echo "   Archived $ARCHIVED_COUNT old daily logs"
else
    echo "- No logs to archive" >> "$REPORT_FILE"
    echo "   No logs to archive"
fi

# Trim outcome log if too large (keep last 500 entries)
if [[ -f "$OUTCOME_LOG" ]]; then
    OUTCOME_COUNT=$(wc -l < "$OUTCOME_LOG" | tr -d ' ')
    if [[ $OUTCOME_COUNT -gt 500 ]]; then
        TRIMMED=$((OUTCOME_COUNT - 500))
        tail -500 "$OUTCOME_LOG" > "$OUTCOME_LOG.tmp"
        mv "$OUTCOME_LOG.tmp" "$OUTCOME_LOG"
        echo "- Trimmed $TRIMMED old outcomes (kept last 500)" >> "$REPORT_FILE"
        echo "   Trimmed $TRIMMED old outcomes"
    fi
fi

# ============================================================
# SUMMARY
# ============================================================

echo "" >> "$REPORT_FILE"
echo "---" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "## Summary" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "Consolidation completed at $(date +%H:%M:%S)" >> "$REPORT_FILE"

# Memory size report
MEMORY_SIZE=$(du -sh "$MEMORY_DIR" 2>/dev/null | cut -f1)
PATTERNS_SIZE=$(du -sh "$MEMORY_DIR/patterns" 2>/dev/null | cut -f1)
echo "- Total memory size: $MEMORY_SIZE" >> "$REPORT_FILE"
echo "- Pattern database size: $PATTERNS_SIZE" >> "$REPORT_FILE"

echo ""
echo "✅ Consolidation complete!"
echo "   Report: $REPORT_FILE"
echo "   Memory size: $MEMORY_SIZE"
