# Smart Routing System v2.0

## Overview
Comprehensive message routing system that automatically determines whether to respond in group chat or directly to individuals, with mode tracking and intent recognition.

## Architecture

### Core Components

#### 1. Mode State Tracker (`state/routing-mode-tracker.json`)
- Tracks current routing mode for each participant
- Modes: `group` (respond in chat-id 3) or `direct` (respond to individual number)
- Persists across sessions
- Auto-reset after 15 minutes of inactivity

#### 2. Intent Recognition (`tools/detect-mode-switch.sh`)
Detects phrases that signal mode changes:

**Direct Mode Triggers:**
- "move to private"
- "switch to DM"
- "go private"
- "talk privately"
- "DM" (anywhere in message)
- "just you and me"
- "one on one"

**Group Mode Triggers:**
- "back to group"
- "rejoin group"
- "everyone"
- "tell everyone"

#### 3. Routing Decision Logger (`tools/log-routing-decision.sh`)
- Logs every routing choice with reasoning
- Stores in `logs/routing-decisions.jsonl`
- Enables analysis of success/failure patterns
- Keeps last 1000 decisions

#### 4. Smart Router Orchestrator (`tools/smart-route.sh`)
Master routing logic:
1. Check for explicit mode switch intent
2. Look up participant's current mode
3. Default to group if uncertain

## Usage

### Basic Routing Decision
```bash
TARGET=$(~/clawd/tools/smart-route.sh "$SENDER" "$MESSAGE_TEXT")

if [[ "$TARGET" == group:* ]]; then
    CHAT_ID=$(echo "$TARGET" | cut -d: -f2)
    imsg send --chat-id "$CHAT_ID" --text "response"
else
    NUMBER=$(echo "$TARGET" | cut -d: -f2)
    # Send directly to number
fi
```

### Manual Mode Override
Users can explicitly switch modes:
- "DM hey can you help?" → Switches to direct mode
- "Back to group" → Switches to group mode

### Checking Current Mode
```bash
SENDER="+14245157194"
MODE=$(jq -r ".participant_modes[\"$SENDER\"].current_mode" ~/clawd/state/routing-mode-tracker.json)
echo $MODE  # "group" or "direct"
```

## Implementation in Atlas

### Response Flow
1. Receive message from sender
2. Run `smart-route.sh "$SENDER" "$MESSAGE_TEXT"`
3. Get routing target (group:3 or direct:+NUMBER)
4. Send response to appropriate target
5. Log decision for analysis

### Mode Persistence
- Modes persist across sessions via JSON file
- Read on session start from CRITICAL_OPERATIONS.md
- Auto-reset prevents stale direct modes

## Examples

### Example 1: DM Marker
```
User: "DM can you help with something private?"
Intent Detection: "DM" found → mode:direct
Routing: direct:+14245157194
Response: Sent privately
Mode Update: User set to direct mode
```

### Example 2: Return to Group
```
User: "Back to group"
Intent Detection: "back to group" → mode:group
Routing: group:3
Response: Sent to group chat
Mode Update: User set to group mode
```

### Example 3: Staying in Mode
```
User: "What's 2+2" (while in direct mode)
Intent Detection: No switch signal
Mode Check: User in direct mode
Routing: direct:+14245157194
Response: Sent privately
```

## Advantages

### Over Previous System
- **No guessing:** Explicit mode tracking eliminates uncertainty
- **Intent-aware:** Recognizes natural language mode switches
- **Persistent:** Modes survive session resets
- **Auditable:** All decisions logged with reasoning
- **Flexible:** Users control mode with natural phrases or DM marker

### For Kronos
- Reliable multi-party communication
- No information leakage between contexts
- Clear audit trail for compliance
- Scalable to many participants

## Limitations

### Current
- Requires jq for JSON parsing
- Mode updates need manual implementation
- No automatic correction of wrong decisions

### Future Enhancements
1. **Auto-learning:** Track which decisions were corrected, adjust patterns
2. **Context awareness:** Consider message content, not just keywords
3. **Confidence scoring:** Flag low-confidence routing for verification
4. **Clawdbot PR:** Include chat_id in message headers (eliminates need for system)

## Testing

### Test Cases
1. ✅ User says "DM help" → Routes directly
2. ✅ User says "back to group" → Routes to group
3. ✅ User in direct mode, sends message → Stays direct
4. ✅ User in group mode, sends message → Stays group
5. ⏳ Auto-reset after 15min inactivity → Returns to group

### Validation
```bash
# Test intent detection
~/clawd/tools/detect-mode-switch.sh "DM can you help?"
# Should output: mode:direct

~/clawd/tools/detect-mode-switch.sh "back to group please"
# Should output: mode:group

~/clawd/tools/detect-mode-switch.sh "regular message"
# Should output: mode:none
```

## Maintenance

### Log Review
```bash
# View recent routing decisions
tail -20 ~/clawd/logs/routing-decisions.jsonl | jq .

# Count routing targets
jq -r .target ~/clawd/logs/routing-decisions.jsonl | sort | uniq -c
```

### Mode Reset (if needed)
```bash
# Reset all participants to group mode
jq '.participant_modes | to_entries | map(.value.current_mode = "group")' \
  ~/clawd/state/routing-mode-tracker.json > /tmp/reset.json
mv /tmp/reset.json ~/clawd/state/routing-mode-tracker.json
```

## Integration with Memory

### Session Start Protocol
Add to CRITICAL_OPERATIONS.md:
```markdown
## Message Routing (MANDATORY)

Before responding to ANY message from group participants:
1. Run: TARGET=$(~/clawd/tools/smart-route.sh "$SENDER" "$MESSAGE")
2. Route accordingly: group:3 or direct:+NUMBER
3. Never guess - always use the router
```

### Logging Updates to Memory
When mode switches occur, update daily log:
```markdown
## Routing Mode Changes
- [TIME] +14245157194: switched to direct mode (requested "DM")
- [TIME] +16195779919: switched to group mode (said "back to group")
```

---

**Status:** Active  
**Version:** 2.0  
**Created:** 2026-01-24  
**Last Updated:** 2026-01-24 07:47 PST  
**Next Review:** When Kronos development starts
