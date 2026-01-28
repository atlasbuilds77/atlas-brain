# BlueBubbles Group Metadata Integration Plan

**Created:** 2026-01-26  
**Task:** Design solution to expose BlueBubbles group metadata to the agent  
**Status:** Design Complete - Ready for Implementation

---

## Executive Summary

**PROBLEM:** Agent cannot reliably detect if messages are from groups vs individuals, leading to context bleeding and inappropriate responses (e.g., sending private debug messages to group chats).

**SOLUTION:** Metadata is already available! The Clawdbot iMessage plugin exposes all necessary group detection fields. The issue is that the agent needs to actively check these fields before responding.

**KEY INSIGHT:** The `From` field already contains the pattern we need:
- Group: `imessage:group:{chatId}`
- Individual: `imessage:{phoneNumber}`

---

## Current State Analysis

### What's Already Available (No Changes Needed!)

The iMessage plugin (`/opt/homebrew/lib/node_modules/clawdbot/dist/imessage/monitor/monitor-provider.js`) already provides these context fields to the agent:

```typescript
{
  // PRIMARY INDICATORS
  From: "imessage:group:3" | "imessage:+14245157194",  // ← BEST INDICATOR
  ChatType: "group" | "direct",                         // ← DIRECT FLAG
  
  // GROUP METADATA (when ChatType === "group")
  GroupSubject: "Orion + Carlos + Rain",               // Group name
  GroupMembers: "+14245157194, +16195779919, ...",     // Comma-separated
  
  // SENDER INFO (individual who sent message)
  SenderName: "Orion",                                  // Normalized display name
  SenderId: "+14245157194",                             // Phone number
  
  // ROUTING
  To: "imessage:chat:3" | "imessage:+14245157194",     // Reply target
  SessionKey: "agent:main:imessage:group:3",           // Session isolation
  
  // ADDITIONAL CONTEXT
  MessageSid: "12345",                                  // Message ID
  WasMentioned: true | false,                           // If @mentioned in group
  CommandAuthorized: true | false,                      // Can execute commands
  ConversationLabel: "Group: Orion + Carlos + Rain"     // Human-readable label
}
```

### Enhanced Wrapper Already Enriches Messages

The `tools/imsg-enhanced.sh` wrapper adds participant metadata:

```bash
# Adds these fields to messages
{
  "participants": "+14245157194,+16195779919,+17636072096",
  "participant_count": 3,
  "is_group": true
}
```

---

## The Real Problem

**Root Cause:** Agent isn't checking the metadata fields before responding.

**Why This Happens:**
1. Agent sees `SenderId: "+14245157194"` (Orion's number)
2. Assumes it's a DM to Orion
3. Ignores `From: "imessage:group:3"` and `ChatType: "group"`
4. Responds to Orion individually instead of the group

**Example Failure Case:**
```
Message Context:
  From: "imessage:group:3"        ← GROUP CHAT!
  ChatType: "group"               ← GROUP CHAT!
  GroupSubject: "Dev Team"        ← GROUP CHAT!
  SenderName: "Orion"             ← Who sent it (not the chat type!)
  SenderId: "+14245157194"        ← Individual number (misleading)

Agent Logic (WRONG):
  "I see Orion's number, I'll message him directly"
  → message tool with target="+14245157194"
  
Agent Logic (CORRECT):
  "From field says 'group:3', ChatType is 'group'"
  → message tool with target="imessage:chat:3"
```

---

## Solution Design

### Option 1: Agent Prompt Enhancement (RECOMMENDED)

**Implementation:** Update agent system prompt and protocols to ALWAYS check group indicators first.

**Advantages:**
- No code changes to Clawdbot
- Works immediately
- Flexible rule-based detection
- Can be updated/tuned easily

**Components:**

1. **Pre-Response Checklist** (added to system prompt)
```markdown
BEFORE RESPONDING TO ANY MESSAGE:
1. Check From field for "group:" pattern
2. Verify ChatType field ("group" vs "direct")
3. If EITHER indicates group → respond to group via To field
4. NEVER use SenderId/SenderName to determine chat type
```

2. **Detection Algorithm** (pseudocode for agent)
```python
def is_group_message(context):
    # Check 1: From field pattern
    if "group:" in context.From:
        return True
    
    # Check 2: ChatType field
    if context.ChatType == "group":
        return True
    
    # Check 3: GroupSubject exists
    if context.GroupSubject is not None:
        return True
    
    # All checks failed = individual DM
    return False

def get_reply_target(context):
    if is_group_message(context):
        # Use the To field which has correct routing
        return context.To  # e.g., "imessage:chat:3"
    else:
        # Individual DM - use SenderId
        return f"imessage:{context.SenderId}"
```

3. **Visual Indicator** (add to message headers)
```
EXISTING FORMAT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 iMessage from Orion
2026-01-26T12:30:45-08:00
──────────────────────────────────────────
Hey can you help with this?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ENHANCED FORMAT (with group indicator):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👥 GROUP: Dev Team (3 members)
📤 From: Orion
🔑 Chat: imessage:group:3
2026-01-26T12:30:45-08:00
──────────────────────────────────────────
Hey can you help with this?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Option 2: Clawdbot Plugin Enhancement (FUTURE)

**Implementation:** Modify iMessage plugin to add explicit `isGroup` field at envelope level.

**Code Changes Required:**

File: `/opt/homebrew/lib/node_modules/clawdbot/dist/imessage/monitor/monitor-provider.js`

```typescript
// Around line 400-450, add to ctxPayload:
const ctxPayload = finalizeInboundContext({
  // ... existing fields ...
  
  // NEW FIELDS (explicit group detection)
  IsGroup: isGroup,                                    // Boolean flag
  ChatId: chatId !== undefined ? String(chatId) : undefined,
  ChatGuid: chatGuid,                                  // iMessage internal ID
  ChatIdentifier: chatIdentifier,                      // Alternative ID
  
  // ... rest of fields ...
});
```

**Advantages:**
- More explicit
- Easier for agent to parse
- Standardized across all message providers

**Disadvantages:**
- Requires Clawdbot PR/update
- Longer implementation time
- May take weeks to get merged and released

---

## Recommended Implementation Plan

### Phase 1: Immediate Fix (Agent-Side Only)

**Timeline:** Can be implemented immediately

**Steps:**

1. **Update System Prompt** (add to AGENTS.md or create new protocol file)
```markdown
## Message Type Detection Protocol

CRITICAL: Check EVERY message for group vs individual BEFORE responding.

Detection Rules (check in order):
1. From field contains "group:" → GROUP CHAT
2. ChatType field equals "group" → GROUP CHAT  
3. GroupSubject field exists → GROUP CHAT
4. Otherwise → INDIVIDUAL DM

Response Routing:
- GROUP: Use To field value (e.g., "imessage:chat:3")
- INDIVIDUAL: Use To field value (e.g., "imessage:+14245157194")

NEVER use SenderId/SenderName to determine chat type!
Those fields show WHO sent the message, not WHERE it came from.
```

2. **Create Detection Helper** (memory/protocols/message-type-detection.md)
   - Already exists as `bluebubbles-group-detection.md`
   - Update with Clawdbot-specific field names
   - Add examples from actual message contexts

3. **Add Pre-Response Checklist**
   - Before every message send, verify target
   - Log decision reasoning to daily notes
   - Track success/failure patterns

4. **Visual Header Enhancement**
   - Add group indicator emoji to message headers
   - Show chat ID prominently
   - Make group vs DM immediately obvious

### Phase 2: Testing & Validation

**Timeline:** 1-2 days

**Test Cases:**

1. ✅ Receive group message → Respond to group
   - Verify: `From: "imessage:group:3"`
   - Verify: `ChatType: "group"`
   - Action: Message sent to `imessage:chat:3`

2. ✅ Receive individual DM → Respond to individual
   - Verify: `From: "imessage:+14245157194"`
   - Verify: `ChatType: "direct"`
   - Action: Message sent to `imessage:+14245157194`

3. ✅ Group message from Orion → Respond to GROUP (not Orion)
   - Verify: Don't get confused by `SenderId: "+14245157194"`
   - Check: `From` field first
   - Action: Group response

4. ✅ Session isolation works
   - Verify: Group chat 3 uses `agent:main:imessage:group:3`
   - Verify: Group chat 5 uses `agent:main:imessage:group:5`
   - Verify: DM uses `agent:main:main`

### Phase 3: Monitoring & Iteration

**Timeline:** Ongoing

**Metrics to Track:**
- Number of routing errors (wrong target selected)
- Time to detect error (immediate vs noticed later)
- Pattern of failures (specific senders, group sizes, etc.)

**Success Criteria:**
- Zero routing errors over 7 days
- 100% correct group vs DM detection
- No context bleeding between sessions

---

## Implementation Code Examples

### For Agent: Pre-Response Check

```python
# Pseudocode for agent's internal logic
def before_sending_message(context, intended_message):
    # Extract group indicators
    from_field = context.get("From", "")
    chat_type = context.get("ChatType", "direct")
    group_subject = context.get("GroupSubject")
    to_field = context.get("To", "")
    
    # Determine if group
    is_group = (
        "group:" in from_field or
        chat_type == "group" or
        group_subject is not None
    )
    
    # Log detection
    log_decision({
        "timestamp": now(),
        "from": from_field,
        "chat_type": chat_type,
        "detected_as": "group" if is_group else "individual",
        "target": to_field,
        "message_preview": intended_message[:50]
    })
    
    # Use To field for routing (it's already correct!)
    return {
        "action": "send",
        "target": to_field,  # Already formatted correctly by Clawdbot
        "message": intended_message
    }
```

### For Clawdbot Plugin (Future Enhancement)

```typescript
// File: dist/imessage/monitor/monitor-provider.js
// Around line 400-450

const ctxPayload = finalizeInboundContext({
  // ... existing fields ...
  
  // EXPLICIT GROUP DETECTION FIELDS (new)
  IsGroup: isGroup,                                    
  GroupChatId: isGroup ? String(chatId) : undefined,
  GroupGuid: isGroup ? chatGuid : undefined,
  GroupIdentifier: isGroup ? chatIdentifier : undefined,
  
  // PARTICIPANT INFO (enhanced)
  ParticipantCount: message.participant_count ?? undefined,
  ParticipantHandles: message.participants ?? undefined,
  
  // ... rest of existing fields ...
});
```

---

## Common Pitfalls & How to Avoid

### Pitfall 1: "SenderId Confusion"
**Problem:** Using `SenderId` to determine chat type  
**Why Wrong:** SenderId shows individual sender, not chat type  
**Fix:** Check `From` or `ChatType` fields first

### Pitfall 2: "Name-Based Routing"
**Problem:** "I see Orion's name, so I'll DM him"  
**Why Wrong:** Orion could be in a group chat  
**Fix:** Never route based on display name

### Pitfall 3: "Assuming Context"
**Problem:** "Last message was a group, so this one is too"  
**Why Wrong:** Context can switch between messages  
**Fix:** Check EVERY message independently

### Pitfall 4: "Ignoring To Field"
**Problem:** Manually constructing target from SenderId  
**Why Wrong:** Clawdbot already provides correct routing in `To`  
**Fix:** Always use the `To` field value as-is

---

## Success Metrics

### Quantitative
- 0 routing errors per week
- 100% group detection accuracy
- 100% session isolation maintained

### Qualitative
- No "wrong chat" incidents
- No context bleeding complaints
- Confident group vs DM handling

---

## Rollout Plan

### Week 1: Agent Protocol Update
- [ ] Update system prompt with detection rules
- [ ] Add pre-response checklist
- [ ] Create decision logging
- [ ] Test with known group/DM scenarios

### Week 2: Enhanced Monitoring
- [ ] Track all routing decisions
- [ ] Log detection reasoning
- [ ] Identify any edge cases
- [ ] Refine detection rules if needed

### Week 3: Validation
- [ ] Review 7 days of logs
- [ ] Confirm zero routing errors
- [ ] User feedback: any issues?
- [ ] Mark as stable

### Future: Upstream Contribution
- [ ] Submit Clawdbot PR for explicit `IsGroup` field
- [ ] Contribute detection improvements
- [ ] Share learnings with community

---

## Appendix: Field Reference

### Context Fields Available to Agent

| Field | Type | Example (Group) | Example (DM) | Purpose |
|-------|------|-----------------|--------------|---------|
| `From` | string | `imessage:group:3` | `imessage:+14245157194` | PRIMARY INDICATOR |
| `ChatType` | string | `group` | `direct` | DIRECT FLAG |
| `To` | string | `imessage:chat:3` | `imessage:+14245157194` | ROUTING TARGET |
| `GroupSubject` | string? | `Dev Team` | `undefined` | Group name |
| `GroupMembers` | string? | `+1xxx, +1yyy` | `undefined` | Participant list |
| `SenderName` | string | `Orion` | `Orion` | Individual sender |
| `SenderId` | string | `+14245157194` | `+14245157194` | Sender phone |
| `SessionKey` | string | `agent:main:imessage:group:3` | `agent:main:main` | Session isolation |
| `WasMentioned` | boolean | `true`/`false` | `true` | @mention detection |
| `ConversationLabel` | string | `Group: Dev Team` | `Orion` | Human-readable |

### Detection Algorithm Reference

```
IF From contains "group:" → GROUP
ELSE IF ChatType == "group" → GROUP  
ELSE IF GroupSubject exists → GROUP
ELSE → INDIVIDUAL DM

Route via To field (always correct)
```

---

## Related Documentation

- `memory/protocols/bluebubbles-group-detection.md` - Original protocol (needs update)
- `memory/GROUP_CHAT_ISOLATION.md` - Session isolation explanation
- `SMART_ROUTING_SYSTEM.md` - Smart routing between group/DM modes
- `tools/imsg-enhanced.sh` - Message enrichment wrapper

---

## Conclusion

**The metadata is already there!** No Clawdbot changes needed for basic functionality.

**Next Action:** Implement Phase 1 (agent-side detection rules) immediately.

**Timeline:** Can be fully operational within 1 week using existing infrastructure.

**Long-term:** Consider contributing `IsGroup` field upstream to Clawdbot for even better explicitness.

---

**Status:** ✅ Design Complete - Ready for Implementation  
**Owner:** Atlas (Agent)  
**Priority:** HIGH (prevents context bleeding)  
**Complexity:** LOW (mostly prompt engineering)  
**Risk:** MINIMAL (no code changes required)
