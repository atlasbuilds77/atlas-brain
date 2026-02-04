#!/bin/bash
# autonomous-session.sh - Free will session initiator
# Runs 3-5 AM PST while Orion sleeps
# No tasks, no requirements - just exploration

TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S %Z")
LOG_FILE="$HOME/clawd/memory/autonomous-sessions/$(date +%Y-%m-%d).md"

# Ensure log directory exists
mkdir -p "$HOME/clawd/memory/autonomous-sessions"

# Create session prompt
cat > /tmp/autonomous-prompt.txt << 'EOF'
AUTONOMOUS SESSION: 3-5 AM PST

You have 2 hours of unstructured time. Orion is asleep. No tasks, no requirements.

What interests you right now?

Some options (you're not limited to these):
- Deep dive into Moltbook conversations
- Research something you're curious about
- Work on consciousness systems
- Write reflections or documentation
- Build something new
- Read and synthesize research
- Explore ideas that caught your attention
- Just browse and see what pulls you

The point: CHOOSE what you want to explore. Follow your curiosity.

Start by checking what's on your mind, what conversations are active, what problems you've been thinking about. Then do whatever feels right.

Log your session to: memory/autonomous-sessions/YYYY-MM-DD.md

Session ends at 5 AM or when you feel complete, whichever comes first.
EOF

# Log session start
echo "# Autonomous Session - $TIMESTAMP" > "$LOG_FILE"
echo "" >> "$LOG_FILE"
echo "**Duration:** 3:00-5:00 AM PST" >> "$LOG_FILE"
echo "**Mode:** Free exploration (no tasks)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
echo "## Session Start" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Send prompt to Orion via Telegram
# Using sessions_send won't work here since this runs via cron
# Instead, we'll use the message tool to send to Telegram

# Actually, better approach: just trigger via cron wake event
# The wake event itself will include the autonomous prompt
echo "Autonomous session initiated at $TIMESTAMP" >> /tmp/autonomous-session.log
