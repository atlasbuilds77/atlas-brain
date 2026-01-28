# iMessage Group Detection Protocol

**Purpose**: NEVER respond individually to group chat messages. Always detect whether an incoming message is from a group chat or individual DM before responding.

**Updated:** 2026-01-26 - Aligned with actual Clawdbot field names

---

## Critical Rule: CHECK BEFORE EVERY RESPONSE

**BEFORE responding to ANY iMessage:**
1. Extract and analyze the message metadata
2. Check ALL group indicators (redundancy is safety)
3. If ANY indicator shows GROUP → respond to GROUP ONLY via the `To` field
4. If unsure → ASK, don't assume

---

## Group vs Individual Detection Rules

### PRIMARY INDICATORS (Most Reliable) - Clawdbot Fields

#### 1. **From Field Pattern** ✓ BEST INDICATOR
```
GROUP:      From contains "group:"
INDIVIDUAL: From starts with "imessage:" (no "group:")

Examples:
- "imessage:group:3"          → GROUP CHAT
- "imessage:+14245157194"     → INDIVIDUAL DM
```

#### 2. **ChatType Field** ✓ DIRECT FLAG
```
ChatType: "group"   → GROUP CHAT
ChatType: "direct"  → INDIVIDUAL DM
```

#### 3. **GroupSubject Exists** ✓ PRESENCE CHECK
```
GroupSubject: "Dev Team"     → GROUP CHAT (field exists)
GroupSubject: undefined      → INDIVIDUAL DM (field absent)
```

### SECONDARY INDICATORS

#### 4. **GroupMembers Field**
- Groups have comma-separated participant list
- Individuals have undefined/null value

#### 5. **SessionKey Pattern**
- Groups: `agent:main:imessage:group:{chatId}`
- Individuals: `agent:main:main` or `agent:main:imessage:{number}`

---

## Metadata Fields Reference

### Clawdbot Context Fields (What Agent Actually Receives):
```javascript
{
  // PRIMARY DETECTION FIELDS
  "From": "imessage:group:3",              // Contains "group:" or not
  "ChatType": "group",                      // "group" or "direct"
  "To": "imessage:chat:3",                 // ROUTING TARGET (use this!)
  
  // GROUP-SPECIFIC FIELDS (only present if group)
  "GroupSubject": "Dev Team",               // Group name
  "GroupMembers": "+14245157194, +1619...", // Comma-separated
  
  // SENDER INFO (individual who sent message)
  "SenderName": "Orion",                    // Display name
  "SenderId": "+14245157194",               // Phone number
  
  // SESSION & ROUTING
  "SessionKey": "agent:main:imessage:group:3",
  "ConversationLabel": "Group: Dev Team",
  "WasMentioned": true,                     // If @mentioned
  
  // MESSAGE METADATA
  "MessageSid": "12345",
  "Timestamp": 1706313045000
}
```

**⚠️ WARNING**: `SenderId` and `SenderName` show the INDIVIDUAL who sent the message, NOT the chat type!
- In group chat: SenderId = individual member's number (e.g., Orion's +14245157194)
- This is WHY we check `From` or `ChatType` instead!

---

## Detection Algorithm (Pseudocode)

```python
def is_group_message(context):
    """
    Returns: True if group, False if individual
    Check multiple indicators for reliability
    Uses actual Clawdbot context field names
    """
    
    # PRIMARY CHECK 1: From field pattern
    if 'From' in context:
        if 'group:' in context['From']:
            return True  # Definitely a group (e.g., "imessage:group:3")
        if context['From'].startswith('imessage:+'):
            return False  # Definitely individual (e.g., "imessage:+14245157194")
    
    # PRIMARY CHECK 2: ChatType field
    if 'ChatType' in context:
        if context['ChatType'] == 'group':
            return True
        if context['ChatType'] == 'direct':
            return False
    
    # PRIMARY CHECK 3: GroupSubject presence
    if context.get('GroupSubject') is not None:
        return True  # If GroupSubject exists, it's a group
    
    # FALLBACK: If uncertain, assume individual (safer default)
    return False  # Individual DM is safer assumption than group

def get_reply_target(context):
    """
    Returns the correct target for replying
    ALWAYS use the To field - Clawdbot sets it correctly!
    """
    # The To field is already properly formatted by Clawdbot
    # Examples:
    #   Group: "imessage:chat:3"
    #   Individual: "imessage:+14245157194"
    return context.get('To', '')
```

---

## Example Scenarios

### ✅ GROUP CHAT EXAMPLE
**Scenario**: Orion sends message in group chat 3 with Carlos and Rain

```javascript
{
  "From": "imessage:group:3",
  "To": "imessage:chat:3",
  "ChatType": "group",
  "GroupSubject": "Orion + Carlos + Rain",
  "GroupMembers": "+14245157194, +16195779919, +17636072096",
  "SenderName": "Orion",
  "SenderId": "+14245157194",
  "SessionKey": "agent:main:imessage:group:3",
  "ConversationLabel": "Group: Orion + Carlos + Rain"
}
```

**Detection Result**: GROUP CHAT
- From contains "group:" ✓ → `imessage:group:3`
- ChatType = "group" ✓
- GroupSubject exists ✓ → "Orion + Carlos + Rain"
- **Action**: Respond to `To` field → `imessage:chat:3` (the GROUP)
- **WRONG**: Responding to SenderId `+14245157194` (would DM Orion only!)

---

### ✅ INDIVIDUAL DM EXAMPLE
**Scenario**: Orion sends direct message to Atlas

```javascript
{
  "From": "imessage:+14245157194",
  "To": "imessage:+14245157194",
  "ChatType": "direct",
  "GroupSubject": null,
  "GroupMembers": null,
  "SenderName": "Orion",
  "SenderId": "+14245157194",
  "SessionKey": "agent:main:main",
  "ConversationLabel": "Orion"
}
```

**Detection Result**: INDIVIDUAL DM
- From = "imessage:+14245157194" (no "group:") ✓
- ChatType = "direct" ✓
- GroupSubject is null ✓
- **Action**: Respond to `To` field → `imessage:+14245157194` (DM to Orion)

---

## Response Protocol

### Step-by-Step Response Process

```
1. RECEIVE message from BlueBubbles
   ↓
2. EXTRACT metadata (chatGuid, isGroup, participants)
   ↓
3. RUN detection checks (all three primary indicators)
   ↓
4. DETERMINE: Group or Individual?
   ↓
5a. IF GROUP → message tool with target = GROUP chatId
5b. IF INDIVIDUAL → message tool with target = sender ID
   ↓
6. VERIFY target before sending (double-check)
   ↓
7. SEND response to correct destination
```

### ⚠️ NEVER Do This:
```
❌ See sender = "+14245157194" → respond to that number
❌ Assume DM because you see an individual name
❌ Use sender field to determine chat type
❌ Skip metadata checks "just this once"
```

### ✅ ALWAYS Do This:
```
✓ Check chatGuid pattern FIRST
✓ Verify isGroup flag
✓ Count participants as backup
✓ Use chatId/chatGuid as response target for groups
✓ Log detection results for debugging
✓ When in doubt, ask user for clarification
```

---

## Implementation Checklist

Before responding to any BlueBubbles message:

- [ ] Extract `chatGuid` field
- [ ] Check for ";+;" (group) or ";-;" (individual)
- [ ] Verify `isGroup` boolean
- [ ] Count `participants` array length
- [ ] Determine chat type (GROUP or INDIVIDUAL)
- [ ] Select correct target for response
- [ ] Double-check target matches chat type
- [ ] Send response

---

## Common Mistakes & Prevention

### Mistake 1: "Sender Field Confusion"
**Problem**: Using `sender` field to determine chat type
**Why Wrong**: Sender is always an individual, even in groups
**Fix**: IGNORE sender for type detection, use chatGuid/isGroup

### Mistake 2: "Assuming Based on Name"
**Problem**: "Message shows Orion, so respond to Orion"
**Why Wrong**: Orion could be in a group chat
**Fix**: Check metadata, not display name

### Mistake 3: "Skipping Checks"
**Problem**: "I remember this is a group, no need to check"
**Why Wrong**: Chat context can change, metadata is authoritative
**Fix**: ALWAYS run detection checks, every time

---

## Debugging & Logging

When uncertain, log the following for analysis:

```javascript
console.log("BlueBubbles Message Received:");
console.log("- chatGuid:", metadata.chatGuid);
console.log("- isGroup:", metadata.isGroup);
console.log("- participants:", metadata.participants);
console.log("- sender:", metadata.sender);
console.log("- chatIdentifier:", metadata.chatIdentifier);
console.log("DETECTED TYPE:", isGroup ? "GROUP" : "INDIVIDUAL");
```

---

## Quick Reference Card

```
┌──────────────────────────────────────────┐
│   CLAWDBOT iMessage GROUP DETECTION      │
│          CHEAT SHEET                     │
├──────────────────────────────────────────┤
│ CHECK 1: From field                      │
│   Contains "group:" = GROUP              │
│   Starts "imessage:+" = INDIVIDUAL       │
│                                          │
│ CHECK 2: ChatType                        │
│   "group"  = GROUP                       │
│   "direct" = INDIVIDUAL                  │
│                                          │
│ CHECK 3: GroupSubject                    │
│   exists/not null = GROUP                │
│   null/undefined  = INDIVIDUAL           │
│                                          │
│ ⚠️  NEVER use SenderId for type!         │
│ ✓  ALWAYS use To field for routing!     │
│ ✓  Check EVERY message independently!   │
└──────────────────────────────────────────┘
```

---

## Related Documentation

- **`memory/bluebubbles-integration-plan.md`** - Complete implementation guide
- `memory/GROUP_CHAT_ISOLATION.md` - Session isolation explanation
- `SMART_ROUTING_SYSTEM.md` - Smart routing modes
- `tools/imsg-enhanced.sh` - Message enrichment wrapper

---

## Version History
- **v2.0** (2026-01-26): Updated with actual Clawdbot field names
- **v1.0** (2026-01-24): Initial protocol created
- Focus: Prevent individual responses to group messages
- Based on: Clawdbot iMessage plugin analysis

---

**REMEMBER**: 
1. The `To` field is ALWAYS correct - use it for routing!
2. Check `From` field FIRST for group detection
3. Never route based on `SenderId` or `SenderName`
4. When in doubt, DON'T send - ask for clarification