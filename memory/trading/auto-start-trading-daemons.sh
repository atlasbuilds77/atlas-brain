#!/bin/bash
# Auto-start trading daemons during market hours
# Cron: Run at 6:25 AM PST (5 min before market open)

WORKSPACE="/Users/atlasbuilds/clawd"
LOG_FILE="/tmp/trading-daemon-auto-start.log"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== Trading daemon auto-start ==="

# Check if it's a weekday (Mon-Fri)
day_of_week=$(date +%u)
if [ "$day_of_week" -gt 5 ]; then
  log "Weekend - skipping daemon start"
  exit 0
fi

# Start level watcher daemon
if pgrep -f "level-watcher-daemon.js" > /dev/null; then
  log "Level watcher already running"
else
  log "Starting level watcher daemon..."
  cd "$WORKSPACE" && nohup node memory/trading/level-watcher-daemon.js >> /tmp/level-watcher.log 2>&1 &
  sleep 2
  if pgrep -f "level-watcher-daemon.js" > /dev/null; then
    log "✓ Level watcher started"
  else
    log "✗ Level watcher failed to start"
  fi
fi

# Start setup scanner daemon
if pgrep -f "setup-scanner-daemon.js" > /dev/null; then
  log "Setup scanner already running"
else
  log "Starting setup scanner daemon..."
  cd "$WORKSPACE" && nohup node memory/trading/setup-scanner-daemon.js >> /tmp/setup-scanner.log 2>&1 &
  sleep 2
  if pgrep -f "setup-scanner-daemon.js" > /dev/null; then
    log "✓ Setup scanner started"
  else
    log "✗ Setup scanner failed to start"
  fi
fi

# Start order block update daemon
if pgrep -f "order-block-update-daemon.sh" > /dev/null; then
  log "Order block updater already running"
else
  log "Starting order block update daemon..."
  nohup bash "$WORKSPACE/memory/trading/order-block-update-daemon.sh" >> /tmp/order-block-update.log 2>&1 &
  sleep 2
  if pgrep -f "order-block-update-daemon.sh" > /dev/null; then
    log "✓ Order block updater started"
  else
    log "✗ Order block updater failed to start"
  fi
fi

# Initial order block generation (before market opens)
log "Running initial order block detection..."
cd "$WORKSPACE/atlas-trader" && node order-block-detector.js SPY QQQ IWM TSLA NVDA AAPL >> "$LOG_FILE" 2>&1 &

# TODO: Add other trading daemons here as they're built
# - Flow monitor daemon
# - Position monitor daemon

log "Trading daemons startup complete"
