# Group Chat Isolation - CRITICAL

## The Problem (Solved 2026-01-23)
Without isolation, group chat messages bled into DM context. Carlos incident: internal debugging messages sent to him instead of staying private to Orion.

## The Solution
Each group chat gets its own isolated session - completely separate history, context, token budget.

## How It Works

### Config Setup
In /Users/atlasbuilds/.clawdbot/clawdbot.json:

```json
"imessage": {
  "groupPolicy": "allowlist",
  "groups": {
    "3": {},   // Orion + Carlos + Rain
    "5": {}    // Orion + Aphmas (Dev)
  }
}
```

### Session Isolation
- Chat 1 (DM with Orion): `agent:main:main` (main session)
- Chat 3 (group): `agent:main:imessage:group:3` (isolated)
- Chat 5 (group): `agent:main:imessage:group:5` (isolated)

Each session maintains:
- Separate conversation history
- Separate context window
- Separate token budget (200k each)
- Zero context bleeding

## When Adding New Group Chat
1. Find chat ID: `imsg chats`
2. Add to config: `"groups": {"X": {}}`
3. Restart gateway: `gateway.restart`
4. Clawdbot auto-creates isolated session

## Why This Matters
- Prevents leaking internal strategy to clients
- Prevents mixing conversations (Carlos getting debug messages)
- Allows simultaneous conversations without confusion
- Critical for Kronos (multi-client isolation)

## Reference
- Smart Routing System: ~/clawd/SMART_ROUTING_SYSTEM.md
- Message Routing Incident: memory/MESSAGE_ROUTING_INCIDENT.md
- BlueBubbles docs: https://docs.bluebubbles.app (if needed)

## Current Active Groups

### Chat 3: Orion + Carlos + Rain
- Purpose: TBD

### Chat 5: Orion + Aphmas (Dev)
- **Purpose: Dev Bridge for FuturesRelay/Helios**
- Atlas asks Aphmas questions directly (no relay through Orion)
- Both tell Atlas what needs fixing in repos
- Speeds up debugging/dev cycle
- Main topics: FuturesRelay, Helios, repo fixes

Last updated: 2026-01-24 11:33 PST
