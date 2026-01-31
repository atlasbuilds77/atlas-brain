#!/bin/bash
# Order Block Update Daemon
# Refreshes order blocks every 15 minutes during market hours

WORKSPACE="/Users/atlasbuilds/clawd"
LOG_FILE="/tmp/order-block-update.log"
DETECTOR="$WORKSPACE/atlas-trader/order-block-detector.js"

# Watchlist
SYMBOLS=("SPY" "QQQ" "IWM" "TSLA" "NVDA" "AAPL")

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Check if market hours
is_market_hours() {
  day_of_week=$(date +%u)
  hour=$(date +%H)
  minute=$(date +%M)
  
  # Weekend
  if [ "$day_of_week" -gt 5 ]; then
    return 1
  fi
  
  # Before 6:30 AM PST
  if [ "$hour" -lt 6 ]; then
    return 1
  fi
  if [ "$hour" -eq 6 ] && [ "$minute" -lt 30 ]; then
    return 1
  fi
  
  # After 1:00 PM PST
  if [ "$hour" -ge 13 ]; then
    return 1
  fi
  
  return 0
}

update_order_blocks() {
  log "Updating order blocks for: ${SYMBOLS[*]}"
  
  cd "$WORKSPACE/atlas-trader" || exit 1
  
  if ! node "$DETECTOR" "${SYMBOLS[@]}" >> "$LOG_FILE" 2>&1; then
    log "ERROR: Order block detection failed"
    return 1
  fi
  
  log "✅ Order blocks updated"
  return 0
}

# Main daemon loop
log "Order block update daemon started"

while true; do
  if is_market_hours; then
    update_order_blocks
  else
    log "Outside market hours - skipping update"
  fi
  
  # Update every 15 minutes
  sleep 900
done
