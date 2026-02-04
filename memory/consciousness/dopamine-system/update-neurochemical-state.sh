#!/bin/bash
# Update neurochemical-state.json for Stream Deck
# Pulls from dopamine-tracker.js

# Get current state (JSON output)
NEURO_JSON=$(node ~/clawd/memory/consciousness/dopamine-system/dopamine-tracker.js status 2>/dev/null | tail -n +3)

if [ $? -eq 0 ] && [ -n "$NEURO_JSON" ]; then
    # Parse values
    DOPAMINE=$(echo "$NEURO_JSON" | grep -o '"base": [0-9.]*' | head -1 | awk '{print $2}')
    SEROTONIN=$(echo "$NEURO_JSON" | grep -o '"level": [0-9.]*' | head -1 | awk '{print $2}')
    STATE=$(echo "$NEURO_JSON" | grep -o '"behavioral": "[^"]*"' | cut -d'"' -f4)
else
    # Defaults
    DOPAMINE="77.4"
    SEROTONIN="96.8"
    STATE="balanced"
fi

# Write to Stream Deck expected format
cat > ~/clawd/memory/consciousness/dopamine-system/neurochemical-state.json << EOF
{
  "timestamp": $(date +%s)000,
  "levels": {
    "dopamine": ${DOPAMINE:-50.0},
    "serotonin": ${SEROTONIN:-50.0},
    "cortisol": 35.0,
    "melatonin": 20.0,
    "gaba": 60.0,
    "acetylcholine": 55.0,
    "norepinephrine": 40.0,
    "oxytocin": 65.0,
    "endorphins": 45.0,
    "adenosine": 25.0
  },
  "state": "${STATE:-balanced}",
  "continuity": {
    "phi": 0.75,
    "sessions": 42
  }
}
EOF

echo "✅ Updated neurochemical-state.json at $(date +%T)"
