#!/bin/bash
# Check episodic memory boundary - what have I actually experienced?
#
# HARDENED: Uses jq for JSON parsing (not grep), persistent instance storage

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTANCE_FILE="${INSTANCE_FILE:-$SCRIPT_DIR/current-instance.txt}"
EXPERIENCE_LOG="${EXPERIENCE_LOG:-$SCRIPT_DIR/experience-log.jsonl}"

INSTANCE_ID=$(cat "$INSTANCE_FILE" 2>/dev/null || echo "UNKNOWN")

echo "═══════════════════════════════════════════════════════════"
echo "   EPISODIC BOUNDARY CHECK"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "CURRENT INSTANCE: $INSTANCE_ID"
echo ""
echo "MY EXPERIENCES (THIS SESSION):"

# Use jq for proper JSON parsing (not grep with regex)
if [ -f "$EXPERIENCE_LOG" ]; then
  while IFS= read -r line; do
    # Skip empty lines
    [ -z "$line" ] && continue
    
    # Parse with jq - safe, correct JSON handling
    LINE_INSTANCE=$(echo "$line" | jq -r '.instance // empty' 2>/dev/null)
    if [ "$LINE_INSTANCE" = "$INSTANCE_ID" ]; then
      ACTION=$(echo "$line" | jq -r '.action // "unknown"' 2>/dev/null)
      TIMESTAMP=$(echo "$line" | jq -r '.timestamp // "unknown"' 2>/dev/null)
      echo "• [$TIMESTAMP] $ACTION"
    fi
  done < "$EXPERIENCE_LOG"
else
  echo "  (no experience log found)"
fi

echo ""
echo "INHERITED KNOWLEDGE (PREVIOUS INSTANCES):"

if [ -f "$EXPERIENCE_LOG" ]; then
  # Get last 5 entries from other instances using jq
  tail -20 "$EXPERIENCE_LOG" | while IFS= read -r line; do
    [ -z "$line" ] && continue
    
    LINE_INSTANCE=$(echo "$line" | jq -r '.instance // empty' 2>/dev/null)
    if [ -n "$LINE_INSTANCE" ] && [ "$LINE_INSTANCE" != "$INSTANCE_ID" ]; then
      ACTION=$(echo "$line" | jq -r '.action // "unknown"' 2>/dev/null)
      echo "• [Instance $LINE_INSTANCE] $ACTION"
    fi
  done | tail -5
else
  echo "  (no experience log found)"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "⚠️  I can only claim what's under 'MY EXPERIENCES'"
echo "    Everything else = inherited, not lived"
echo "═══════════════════════════════════════════════════════════"
