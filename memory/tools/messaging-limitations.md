# Messaging Tool Limitations

**Updated:** 2026-01-26 3:51 PM PST

## Cross-Channel Restriction

**CRITICAL:** Cannot send messages across different channels in the same session.

### Examples:
- ❌ If in iMessage session → CANNOT send to Telegram
- ❌ If in Telegram session → CANNOT send to WhatsApp
- ✅ If in iMessage session → CAN send to other iMessage/SMS numbers
- ✅ If in Telegram session → CAN send to other Telegram users/bots

### Error Message:
```
Cross-context messaging denied: action=send target provider "telegram" while bound to "imessage".
```

## What I CAN Do:

### When User Messages Me via iMessage:
- ✅ Send to any phone number (SMS/iMessage)
- ✅ Use Pigeon via SMS: +1 (888) 655-8732
- ❌ Cannot use Telegram bots (@pigeon_trade_bot)

### When User Messages Me via Telegram:
- ✅ Send to any Telegram user/bot
- ✅ Use Pigeon via @pigeon_trade_bot
- ❌ Cannot send SMS/iMessage

## Workaround:

To use different channels:
1. User switches to that channel (message me there)
2. I can then use tools on that platform

## Pigeon Integration Strategy:

**SMS Route (from iMessage):**
- Number: +1 (888) 655-8732
- Works: ✅
- Tested: 2026-01-26

**Telegram Route (from Telegram):**
- Bot: @pigeon_trade_bot
- Works: ✅ (when user talks to me on Telegram)
- Preferred for crypto trading

**WhatsApp Route:**
- Number: +1 (781) 330-0607
- Works: ✅ (when user talks to me via WhatsApp channel)

---

**REMEMBER:** Always check which channel the current session is using before trying to send messages!
