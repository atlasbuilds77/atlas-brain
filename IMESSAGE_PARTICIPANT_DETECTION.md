# iMessage Participant Detection System

## Problem Solved
**Context bleeding between conversations** - messages from group chats appeared identical to DMs, causing responses to leak between contacts.

## Solution
Direct iMessage database queries to detect group vs DM chats and get participant lists.

## Components

### 1. Database Query Tools
- **`tools/get-chat-participants.sh`** - Queries chat.db for participant metadata
  - Input: chat_id
  - Output: `chat_id|chat_identifier|display_name|participants|count`
  - Example: `3|chat806694842969439313||+14245157194,+16195779919,+16193845759|3`

- **`tools/check-chat-type.sh`** - Determines DM vs GROUP
  - Input: chat_id  
  - Output: DM or GROUP with participant list

### 2. Enhanced imsg Wrapper
- **`tools/imsg-enhanced.sh`** - Adds participant metadata to imsg messages
  - Watch mode: Enriches messages with `participants`, `participant_count`, `is_group`
  - Other modes: Pass-through to regular imsg
  
Usage:
```bash
# Watch with participant detection
~/clawd/tools/imsg-enhanced.sh watch --json

# Regular imsg commands
~/clawd/tools/imsg-enhanced.sh chats --limit 5
```

### 3. Message Format
Enhanced messages include:
```json
{
  "chat_id": 3,
  "text": "message content",
  "sender": "+14245157194",
  "participants": "+14245157194,+16195779919,+16193845759",
  "participant_count": 3,
  "is_group": true
}
```

## Integration with Clawdbot
Replace `imsg` with `imsg-enhanced.sh` in channel config:
```json
{
  "channels": {
    "imessage": {
      "enabled": true,
      "cliPath": "~/clawd/tools/imsg-enhanced.sh",
      "service": "imessage"
    }
  }
}
```

## Known Chat Mappings
- **Chat 1**: DM with Dev (+14245157194)
- **Chat 2**: DM with Carlos (+16195779919)  
- **Chat 3**: GROUP - Orion, Carlos, Rain (+16193845759 - Carlos's wife)
- **Chat 4**: DM with Laura/Rain (+16193845759)

## Benefits
✅ No BlueBubbles required  
✅ No webhooks needed  
✅ No SIP disable required  
✅ Real-time via `imsg watch`  
✅ Instant participant detection  
✅ Zero polling delay  
✅ Works offline (local database)  

## Security
- Read-only database access
- No external services
- No network dependencies
- Same permissions as imsg CLI
