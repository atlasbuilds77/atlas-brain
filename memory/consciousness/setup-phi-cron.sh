#!/usr/bin/env bash
# SETUP PHI PERIODIC CAPTURE (OPTIONAL)
# Adds cron job for automatic Φ snapshots every 5 minutes during active sessions

CRON_JOB="*/5 * * * * bash $HOME/clawd/memory/consciousness/phi-heartbeat.sh"

echo "Setting up Phi periodic capture..."

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "phi-heartbeat.sh"; then
  echo "⚠️  Phi heartbeat cron job already exists"
  echo "Current cron:"
  crontab -l | grep "phi-heartbeat.sh"
else
  # Add cron job
  (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
  echo "✅ Phi heartbeat cron job added"
  echo "Snapshots will be captured every 5 minutes during active sessions"
fi

echo ""
echo "To verify:"
echo "  crontab -l | grep phi-heartbeat"
echo ""
echo "To remove:"
echo "  crontab -l | grep -v phi-heartbeat | crontab -"
