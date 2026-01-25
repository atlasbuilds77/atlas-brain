#!/bin/bash
# Wrapper script that sends market recap via Atlas

# This will trigger Atlas to generate and send the market recap
echo "Daily market recap triggered at $(date)" >> /Users/orionsolana/clawd/cron-logs.txt

# TODO: Integrate with Clawdbot messaging when cron is set up
# For now, this creates a trigger file that Atlas can monitor
touch /Users/orionsolana/clawd/.market-recap-trigger
