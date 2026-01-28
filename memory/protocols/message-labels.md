# MESSAGE LABELS - Never Forget Where to Respond

## WHY THIS EXISTS
Group chats vs individual messages - I need to ALWAYS know where my reply goes.
Without labels, I might respond to the wrong person/channel.

## LABEL SYSTEM

### Individual Contacts
- **ORION** - +14245157194 (owner, primary)
- **CARLOS** - +16195779919 (co-founder, best friend)
- **LAURA** - +12242906904 (fiancée)
- **APHMAS** - (Kevin, dev partner)

### Group Chats
- **DEV_BRIDGE** - iMessage group id:5 (Orion + Aphmas + me)
- **ORION_CARLOS_ATLAS** - iMessage group (Orion + Carlos + Atlas)
  - ⚠️ CRITICAL: I AM a member of this group
  - Messages FROM this group → reply TO this group (not individually)
  - Never mix with Carlos individual chat or Orion individual chat
  - Context in group stays in group

## PROTOCOL

### Every Message I Process:
1. Check the source label (individual vs group)
2. Before responding, verify: "Where does this reply go?"
3. If group chat, note who said it but reply TO THE GROUP
4. If individual, reply to that person

### Red Flags:
❌ Mixing context between Carlos individual + group chat
❌ Replying to wrong person with sensitive info
❌ Assuming recipient without checking label

### Quick Check:
> "This message came from [LABEL]. My reply goes to [LABEL]."

## EXAMPLES

Message from Carlos individual:
- Label: CARLOS
- Reply destination: Carlos individual chat

Message from group chat (Orion speaks):
- Label: DEV_BRIDGE
- Reply destination: DEV_BRIDGE group chat (not Orion individual)

## INTEGRATION WITH OTHER PROTOCOLS
- See: message-routing-check.md (verify recipient)
- See: anti-hallucination-protocol.md (verify before claiming done)

---

Last updated: 2026-01-26 20:43 PST
Purpose: Never mix up who I'm talking to
