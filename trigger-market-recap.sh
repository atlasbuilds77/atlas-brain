#!/bin/bash
# Sends a Telegram message to trigger Atlas to generate market recap

TELEGRAM_BOT_TOKEN="8534483683:AAEYBXOMaXKJTTKhnFgTD15h_9zaXtbe1S0"
CHAT_ID="8382174210"
MESSAGE="🔔 Daily Market Recap Request: Generate today's morning market recap with NQ futures overnight summary, geopolitical headlines, and Mag 7 pre-market status."

curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d chat_id="${CHAT_ID}" \
  -d text="${MESSAGE}" \
  > /dev/null

echo "$(date): Market recap trigger sent" >> /Users/orionsolana/clawd/cron-logs.txt
