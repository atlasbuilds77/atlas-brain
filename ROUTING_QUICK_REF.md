# Message Routing - Quick Reference

## For Users

### Switch to Private/Direct Mode
Say any of:
- "DM" (anywhere in message)
- "move to private"
- "switch to DM"
- "talk privately"
- "just you and me"

### Return to Group Mode
Say any of:
- "back to group"
- "rejoin group"
- "everyone"
- "tell everyone"

### Check Where Response Will Go
- If you're in **direct mode**: Response comes to you privately
- If you're in **group mode**: Response goes to group chat
- Default: Always group mode unless you switched

## For Atlas

### Before Every Response
```bash
# Determine routing target
TARGET=$(~/clawd/tools/smart-route.sh "$SENDER" "$MESSAGE_TEXT")

# Route accordingly
if [[ "$TARGET" == group:* ]]; then
    CHAT_ID=$(echo "$TARGET" | cut -d: -f2)
    imsg send --chat-id "$CHAT_ID" --text "response"
else
    NUMBER=$(echo "$TARGET" | cut -d: -f2)
    # Send to individual number
fi
```

### Manual Mode Check
```bash
# Get participant's current mode
jq -r ".participant_modes[\"+14245157194\"].current_mode" \
  ~/clawd/state/routing-mode-tracker.json
```

### View Routing Log
```bash
# Last 20 decisions
tail -20 ~/clawd/logs/routing-decisions.jsonl | jq .
```

## Troubleshooting

### Wrong Routing Happened
1. Check mode: `jq '.participant_modes' ~/clawd/state/routing-mode-tracker.json`
2. Check log: `tail -5 ~/clawd/logs/routing-decisions.jsonl | jq .`
3. User can force with "DM" marker or "back to group"

### Reset All to Group Mode
```bash
jq '.participant_modes |= map_values(.current_mode = "group")' \
  ~/clawd/state/routing-mode-tracker.json > /tmp/reset.json && \
  mv /tmp/reset.json ~/clawd/state/routing-mode-tracker.json
```

### Test Intent Detection
```bash
~/clawd/tools/detect-mode-switch.sh "your test message"
# Returns: mode:direct, mode:group, or mode:none
```

---

**TL;DR**  
Users: Say "DM" for private, "back to group" for group  
Atlas: Always run `smart-route.sh` before responding
