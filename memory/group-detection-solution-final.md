# GROUP CHAT DETECTION - THE REAL SOLUTION

## 🚨 ROOT CAUSE FOUND

**THE PROBLEM WAS NEVER CODE - IT WAS CONFIGURATION!**

The group chat messages are coming from **Chat ID 10** (identifier: `chat74410171541772161`), which is a NEW group with Orion (+14245157194) and Carlos (+16195779919).

BUT Clawdbot's config only has groups `3` and `5` enabled!

## Current State Analysis

### Chat IDs in System:
| Chat ID | Type | Identifier | Participants |
|---------|------|------------|--------------|
| 1 | DM | +14245157194 | Orion only |
| 2 | DM | +16195779919 | Carlos only |
| 3 | GROUP | chat806694842969439313 | Orion, Carlos, Rain (3 people) |
| 5 | GROUP | chat434932019159296258 | Unknown |
| **10** | **GROUP** | **chat74410171541772161** | **Orion + Carlos (2 people)** ← **THIS IS THE ACTIVE ONE!** |

### Why Detection Failed:
1. Group chat 10 exists and is active
2. Messages from both Orion and Carlos are hitting chat 10
3. BUT Clawdbot's groups config only includes `{"3": {}, "5": {}}`
4. Group 10 is NOT in the allowlist!
5. So messages from group 10 are being routed to the DM sessions (1 and 2) or agent:main:main

## ⚡ IMMEDIATE FIX

Add group 10 to Clawdbot config:

```bash
# Current config:
cat ~/.clawdbot/clawdbot.json | jq '.channels.imessage.groups'
# Shows: {"3": {}, "5": {}}

# Need to add group 10!
```

### Manual Fix Command:
```bash
# Edit ~/.clawdbot/clawdbot.json and change:
# "groups": {"3": {}, "5": {}}
# To:
# "groups": {"3": {}, "5": {}, "10": {}}

# Then restart gateway:
clawdbot gateway restart
```

## How Session Routing Actually Works

1. **Each configured group gets its own session**: `agent:main:imessage:group:X`
2. **DMs go to individual sessions OR agent:main:main**
3. **The `chatType` in a session is SET when that session is created**
4. **Messages only route to group sessions if the group ID is in config!**

### Current Sessions (iMessage):
- `agent:main:imessage:group:3` - chatType: "group" ✅
- `agent:main:imessage:group:5` - chatType: "group" ✅  
- `agent:main:main` - chatType: "direct" (catch-all)

### Missing:
- `agent:main:imessage:group:10` - DOESN'T EXIST because group 10 isn't configured!

## Detection Logic (Once Config Fixed)

The tools DO work:
```bash
# Check if a chat is a group:
./tools/check-chat-type.sh 10
# Returns: GROUP, Participants: +14245157194,+16195779919 (count: 2)

# Get participant info:
./tools/get-chat-participants.sh 10
# Returns: 10|chat74410171541772161||+14245157194,+16195779919|2
```

## Real-Time Detection (Current Session)

Since messages are hitting agent:main:main with `chatType: "direct"`, the ONLY reliable way to detect group context in the CURRENT message flow is:

1. **Check the `chat_id` from the incoming message** (if available in message metadata)
2. **Query the database for that chat_id's participants**

```bash
# If you have the chat_id from the message:
./tools/check-chat-type.sh $CHAT_ID

# OR run the enhanced wrapper which adds metadata:
# (Already configured but group 10 needs to be in allowlist)
```

## SUMMARY

| Issue | Solution |
|-------|----------|
| Group 10 not in config | Add `"10": {}` to groups in clawdbot.json |
| No session for group 10 | Will auto-create after config fix + restart |
| chatType shows "direct" | Because messages falling through to main session |
| Multiple senders detected | Correct observation! Both from group 10 |

## Action Items

1. ✅ **Problem identified**: Group 10 not in allowlist
2. ⏳ **Fix needed**: Add `"10": {}` to `.clawdbot/clawdbot.json` groups
3. ⏳ **After fix**: `clawdbot gateway restart`
4. ✅ **Tools work**: `check-chat-type.sh` and `get-chat-participants.sh` are correct
5. ✅ **Enhanced wrapper works**: `imsg-enhanced.sh` is properly configured

## Detection Workaround (Until Config Fixed)

Check recent messages for multiple unique senders in a short time window:
```bash
# Multiple senders in recent messages = likely group activity
imsg history --chat-id 10 --limit 10 --json | jq '.sender' | sort -u
# If > 1 unique sender, it's a group
```

---
**TLDR: Add group 10 to the config and restart. That's it.**
