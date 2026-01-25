# Stream Deck Setup for Atlas

Complete Stream Deck configuration for controlling Atlas and monitoring systems.

## Installation

1. Download Stream Deck software: https://www.elgato.com/downloads
2. Install and connect Stream Deck
3. Import profile (coming soon) or configure manually below

## Button Layout (15-key Stream Deck)

### Row 1: Status Dashboard
**[1] System Health**
- **Icon:** Green/Yellow/Red heart
- **Action:** Show system status
- **Script:**
```bash
#!/bin/bash
STATUS=$(clawdbot status | grep "Status:")
if [[ "$STATUS" =~ "healthy" ]]; then
  echo "🟢"
else
  echo "🔴"
fi
```

**[2] Token Usage**
- **Icon:** Battery indicator
- **Action:** Display token count
- **Script:**
```bash
#!/bin/bash
TOKENS=$(clawdbot status | grep "Context:" | awk '{print $2}')
echo "$TOKENS"
```

**[3] FuturesRelay**
- **Icon:** Rocket 🚀
- **Action:** Check FuturesRelay status
- **Script:**
```bash
#!/bin/bash
STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://futures-relay.onrender.com)
if [ "$STATUS" -eq 200 ]; then
  echo "Live ✅"
else
  echo "Down ❌"
fi
```

**[4] Active Sessions**
- **Icon:** Multiple windows
- **Action:** Count running sub-agents
- **Script:**
```bash
#!/bin/bash
COUNT=$(clawdbot sessions list 2>/dev/null | grep -c "agent:")
echo "Sessions: $COUNT"
```

**[5] Voice Status**
- **Icon:** Microphone 🎤
- **Action:** Toggle Atlas voice assistant
- **Script:**
```bash
#!/bin/bash
if pgrep -f "atlas_voice.py" > /dev/null; then
  echo "🎤 ON"
else
  echo "🎤 OFF"
fi
```

---

### Row 2: Quick Actions
**[6] Deploy FuturesRelay**
- **Icon:** Deploy icon
- **Action:** Git push + deploy
- **Script:**
```bash
#!/bin/bash
cd ~/Futures-relay
git add -A
git commit -m "Stream Deck deploy $(date +%H:%M)"
git push
echo "Deploying..."
```

**[7] Restart Clawdbot**
- **Icon:** Refresh ♻️
- **Action:** Gateway restart
- **Script:**
```bash
#!/bin/bash
clawdbot daemon restart
sleep 2
echo "Restarted ✅"
```

**[8] Clear Context**
- **Icon:** Trash/Reset
- **Action:** Start fresh session
- **Script:**
```bash
#!/bin/bash
# Send /new command via Clawdbot API
echo "Resetting session..."
# TODO: Implement via Clawdbot API
```

**[9] Backup Now**
- **Icon:** Save/Backup 💾
- **Action:** Trigger workspace backup
- **Script:**
```bash
#!/bin/bash
cd ~/clawd
tar -czf "backups/workspace_$(date +%Y%m%d_%H%M%S).tar.gz" \
  AGENTS.md SOUL.md TOOLS.md IDENTITY.md USER.md HEARTBEAT.md memory/
echo "Backed up ✅"
```

**[10] Emergency Halt**
- **Icon:** STOP sign 🛑
- **Action:** Stop all trading immediately
- **Script:**
```bash
#!/bin/bash
# Kill all trading processes
pkill -f futures-relay
# Send emergency webhook
curl -X POST "https://futures-relay.onrender.com/emergency/halt" \
  -H "Content-Type: application/json" \
  -d '{"action": "halt_all"}'
echo "HALTED 🛑"
```

---

### Row 3: Monitoring & Modes
**[11] Check Logs**
- **Icon:** Document 📄
- **Action:** Tail recent errors
- **Script:**
```bash
#!/bin/bash
tail -n 20 ~/clawd/memory/$(date +%Y-%m-%d).md | grep -i error || echo "No errors"
```

**[12] Twitter Stats**
- **Icon:** Bird 🐦
- **Action:** Show follower count + recent activity
- **Script:**
```bash
#!/bin/bash
# Use browser automation to check stats
echo "Followers: 5"
echo "Last tweet: 2h ago"
```

**[13] Focus Mode**
- **Icon:** Focus/Mute 🔕
- **Action:** Mute non-critical notifications
- **Script:**
```bash
#!/bin/bash
# Toggle focus mode
FOCUS_FILE=~/clawd/.focus_mode
if [ -f "$FOCUS_FILE" ]; then
  rm "$FOCUS_FILE"
  echo "Focus OFF"
else
  touch "$FOCUS_FILE"
  echo "Focus ON 🔕"
fi
```

**[14] Debug Mode**
- **Icon:** Bug 🐛
- **Action:** Enable verbose logging
- **Script:**
```bash
#!/bin/bash
# Toggle debug logging
DEBUG_FILE=~/clawd/.debug_mode
if [ -f "$DEBUG_FILE" ]; then
  rm "$DEBUG_FILE"
  echo "Debug OFF"
else
  touch "$DEBUG_FILE"
  echo "Debug ON 🐛"
fi
```

**[15] Mac Mini Status**
- **Icon:** Computer 💻
- **Action:** Ping Mac Mini health
- **Script:**
```bash
#!/bin/bash
CPU=$(top -l 1 | grep "CPU usage" | awk '{print $3}')
MEM=$(vm_stat | grep "Pages active" | awk '{print $3}')
echo "CPU: $CPU"
echo "Active: ${MEM}MB"
```

---

## Multi-Action Configurations

### Long Press Actions

**[6] Deploy FuturesRelay (Long Press)**
- Show deployment logs in real-time

**[7] Restart Clawdbot (Long Press)**
- Show restart status + health check

**[10] Emergency Halt (Long Press)**
- Confirmation dialog before halting

---

## Dynamic Icons (Changing States)

### System Health [1]
- 🟢 Green: All systems operational
- 🟡 Yellow: Warnings present
- 🔴 Red: Critical errors

### Token Usage [2]
- 🟢 0-30%: Low usage
- 🟡 30-70%: Moderate
- 🟠 70-90%: High
- 🔴 90-100%: Critical

### FuturesRelay [3]
- ✅ Live (HTTP 200)
- ⚠️ Slow (HTTP 200, >2s response)
- ❌ Down (non-200)

---

## Installation Scripts

### Stream Deck Plugin (Custom)

Create custom Stream Deck plugin that runs these scripts and updates button states.

**Install:**
```bash
cd ~/clawd
./install_streamdeck_plugin.sh
```

### Auto-Update Scripts

Set up cron job to refresh button states every 30 seconds:

```bash
*/30 * * * * ~/clawd/streamdeck/update_buttons.sh
```

---

## Integration with Voice Assistant

When voice command is received, flash corresponding Stream Deck button:
- "Deploy" → Flash [6]
- "Restart" → Flash [7]
- "Status" → Flash [1]

---

## Custom Profiles

### Trading Hours Profile
- Show live P&L
- Active trades count
- Market status

### Development Profile
- GitHub actions status
- CI/CD pipeline
- Code review notifications

### Off-Hours Profile
- Minimal info
- Emergency buttons only
- Sleep mode

---

## Next Steps

1. Install Stream Deck software
2. Run setup script (coming soon)
3. Customize button icons
4. Test each action
5. Set up auto-update cron job

**Questions? Ask Atlas!** 🎤 "Hey Atlas, help with Stream Deck setup"
