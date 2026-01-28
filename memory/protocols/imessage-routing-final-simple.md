# iMESSAGE ROUTING - FINAL SOLUTION

## THE FIX (Simple & Reliable)

**Parse the message envelope format to detect group vs individual**

## DETECTION RULES

### Group Message Format:
```
[iMessage Group id:10 +5s 2026-01-26 21:42 PST] message text
```
- Contains "Group id:X"
- Route to: GROUP

### Individual Message Format:
```
[iMessage +14245157194 +5s 2026-01-26 21:42 PST] message text
```
- Contains phone number "+XXXXXXXXXX"
- Route to: INDIVIDUAL

## NO MANDATORY JQ CHECKS NEEDED

The envelope format tells us everything. No need to:
- Run jq commands before every response
- Check sessions.json
- Parse timestamps

Just read the message header.

## IMPLEMENTATION

When I see a message, check the header format:
- Contains "Group id:" → GROUP
- Contains "+[phone]" → INDIVIDUAL

That's it. Simple, reliable, works every time.

## EXAMPLES

```
[iMessage Group id:10 ...] "test"
→ This is from GROUP 10

[iMessage +14245157194 ...] "test"
→ This is from INDIVIDUAL (Orion)

[iMessage +16195779919 ...] "test"
→ This is from INDIVIDUAL (Carlos)
```

## SUCCESS

✅ No complex jq commands
✅ No timestamp checks
✅ No session.json parsing
✅ Just read the envelope format

---

Last updated: 2026-01-26 21:42 PST
Purpose: Simple, reliable group detection via message envelope
