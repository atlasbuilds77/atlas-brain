#!/bin/bash
# Real-time NQ Monitoring via Polygon Indices Advanced

API_KEY="h7J74V1cd8_4NQpTxwQpudpqXWaIHMhv"
TRIGGER_LEVEL=25500
DATE=$(date -u +%Y-%m-%d)

# Get latest NDX minute bar
RESPONSE=$(curl -s "https://api.polygon.io/v2/aggs/ticker/I:NDX/range/1/minute/${DATE}/${DATE}?adjusted=true&sort=desc&limit=1&apiKey=${API_KEY}")

PRICE=$(echo "$RESPONSE" | jq -r '.results[0].c // empty' 2>/dev/null)
HIGH=$(echo "$RESPONSE" | jq -r '.results[0].h // empty' 2>/dev/null)
LOW=$(echo "$RESPONSE" | jq -r '.results[0].l // empty' 2>/dev/null)
TIMESTAMP=$(echo "$RESPONSE" | jq -r '.results[0].t // empty' 2>/dev/null)

if [ ! -z "$PRICE" ]; then
  READABLE_TIME=$(date -r $((TIMESTAMP/1000)) '+%H:%M:%S')
  echo "[$READABLE_TIME] NQ: $PRICE | H: $HIGH | L: $LOW | Target: $TRIGGER_LEVEL" >> /Users/orionsolana/clawd/nq-live-log.txt
  
  # Check breakout
  if (( $(echo "$PRICE >= $TRIGGER_LEVEL" | bc -l) )); then
    echo "🚨 TRIGGER HIT at $(date)" >> /Users/orionsolana/clawd/nq-live-log.txt
    exit 99  # Special exit code for trigger
  fi
fi
