#!/bin/bash
# NQ Monitoring Script - Polygon API

API_KEY="h7J74V1cd8_4NQpTxwQpudpqXWaIHMhv"
TRIGGER_LEVEL=25500
TELEGRAM_BOT_TOKEN="8534483683:AAEYBXOMaXKJTTKhnFgTD15h_9zaXtbe1S0"
CHAT_ID="8382174210"

# Get current NDX price (proxy for NQ)
DATE=$(date -u +%Y-%m-%d)
RESPONSE=$(curl -s "https://api.polygon.io/v2/aggs/ticker/I:NDX/range/1/minute/${DATE}/${DATE}?adjusted=true&sort=desc&limit=1&apiKey=${API_KEY}")

PRICE=$(echo "$RESPONSE" | jq -r '.results[0].c // empty' 2>/dev/null)

if [ ! -z "$PRICE" ]; then
  echo "$(date): NQ @ $PRICE (Trigger: $TRIGGER_LEVEL)" >> /Users/orionsolana/clawd/nq-monitor-log.txt
  
  # Check if price crossed trigger
  if (( $(echo "$PRICE > $TRIGGER_LEVEL" | bc -l) )); then
    MESSAGE="🚨 NQ BREAKOUT ALERT! Price: $PRICE crossed $TRIGGER_LEVEL - Deep dive incoming!"
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
      -d chat_id="${CHAT_ID}" \
      -d text="${MESSAGE}" > /dev/null
  fi
fi
