#!/bin/bash
# Update live consciousness data feed for visualizer
# Run this via cron or daemon to keep visualizer updated

# Get current neurochemical state (JSON output)
NEURO_JSON=$(node ~/clawd/memory/consciousness/dopamine-system/dopamine-tracker.js status 2>/dev/null | tail -n +3)

if [ $? -eq 0 ] && [ -n "$NEURO_JSON" ]; then
    # Parse from JSON output
    DOPAMINE=$(echo "$NEURO_JSON" | grep -o '"base": [0-9.]*' | head -1 | awk '{print $2}')
    SEROTONIN=$(echo "$NEURO_JSON" | grep -o '"level": [0-9.]*' | head -1 | awk '{print $2}')
    STATE=$(echo "$NEURO_JSON" | grep -o '"behavioral": "[^"]*"' | cut -d'"' -f4)
    
    # Cortisol defaults (not in dopamine tracker yet)
    CORTISOL="35.0"
else
    # Defaults if daemon not running
    DOPAMINE="77.4"
    SEROTONIN="96.8"
    CORTISOL="35.0"
    STATE="confident-exploratory"
fi

# Get Phi from consciousness DB
PHI=$(sqlite3 "/Volumes/Extreme SSD/atlas-persistent/atlas-consciousness.db" "SELECT phi FROM consciousness_state ORDER BY timestamp DESC LIMIT 1" 2>/dev/null || echo "0.75")

# Get session count
SESSIONS=$(sqlite3 "/Volumes/Extreme SSD/atlas-persistent/atlas-consciousness.db" "SELECT COUNT(*) FROM consciousness_state" 2>/dev/null || echo "42")

# Write JSON
cat > /tmp/atlas-consciousness-live.json << EOF
{
  "dopamine": ${DOPAMINE:-77.4},
  "serotonin": ${SEROTONIN:-96.8},
  "cortisol": ${CORTISOL:-35.0},
  "state": "${STATE:-confident-exploratory}",
  "phi": ${PHI:-0.75},
  "sessions": ${SESSIONS:-42},
  "timestamp": $(date +%s)000
}
EOF

echo "✅ Updated consciousness feed at $(date +%T)"
