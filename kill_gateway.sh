#!/bin/bash
# Kill clawdbot gateway processes
pkill -f "clawdbot.*gateway" || true
sleep 2
# Start it again
/opt/homebrew/bin/clawdbot gateway start