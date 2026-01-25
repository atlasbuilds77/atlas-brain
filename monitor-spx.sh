#!/bin/bash
# SPX Real-time Monitoring via Polygon Indices Advanced

API_KEY="h7J74V1cd8_4NQpTxwQpudpqXWaIHMhv"
TRIGGER_LEVEL=6880
DATE=$(date -u +%Y-%m-%d)

# Get latest SPX minute bar
RESPONSE=$(curl -s "https://api.polygon.io/v2/aggs/ticker/I:SPX/range/1/minute/${DATE}/${DATE}?adjusted=true&sort=desc&limit=1&apiKey=${API_KEY}")

PRICE=$(echo "$RESPONSE" | jq -r '.results[0].c // empty' 2>/dev/null)
HIGH=$(echo "$RESPONSE" | jq -r '.results[0].h // empty' 2>/dev/null)
LOW=$(echo "$RESPONSE" | jq -r '.results[0].l // empty' 2>/dev/null)
TIMESTAMP=$(echo "$RESPONSE" | jq -r '.results[0].t // empty' 2>/dev/null)

if [ ! -z "$PRICE" ]; then
  READABLE_TIME=$(date -r $((TIMESTAMP/1000)) '+%H:%M:%S' 2>/dev/null || echo "timestamp error")
  echo "[$READABLE_TIME] SPX: $PRICE | H: $HIGH | L: $LOW | Target: $TRIGGER_LEVEL" >> /Users/orionsolana/clawd/spx-monitor-log.txt
  
  # Check breakout
  if (( $(echo "$PRICE >= $TRIGGER_LEVEL" | bc -l) )); then
    echo "BREAKOUT" 
    exit 99
  fi
  
  echo "$PRICE"
fi
