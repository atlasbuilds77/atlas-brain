#!/bin/bash
# Setup system cron job for token monitoring

# Create the cron job entry
CRON_JOB="*/30 * * * * cd /Users/atlasbuilds/clawd && /usr/bin/python3 token_monitor_simple.py >> /tmp/token_monitor_cron.log 2>&1"

# Add to crontab
(crontab -l 2>/dev/null | grep -v "token_monitor_simple.py"; echo "$CRON_JOB") | crontab -

echo "System cron job added:"
echo "$CRON_JOB"
echo ""
echo "Current crontab:"
crontab -l 2>/dev/null || echo "(no crontab)"