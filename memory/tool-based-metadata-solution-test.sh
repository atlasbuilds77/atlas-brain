#!/bin/bash
# Test script to demonstrate accessing session.chatType via tools

echo "=== Tool-Based Session Metadata Access Tests ==="
echo ""

# Test 1: Direct file access with jq
echo "Test 1: Read chatType from sessions.json"
SESSION_KEY="agent:main:main"
CHAT_TYPE=$(jq -r --arg key "$SESSION_KEY" '.[$key].chatType' \
  ~/.clawdbot/agents/main/sessions/sessions.json)
echo "  Session: $SESSION_KEY"
echo "  chatType: $CHAT_TYPE"
echo ""

# Test 2: Read channel field
echo "Test 2: Read channel from sessions.json"
CHANNEL=$(jq -r --arg key "$SESSION_KEY" '.[$key].channel' \
  ~/.clawdbot/agents/main/sessions/sessions.json)
echo "  Session: $SESSION_KEY"
echo "  channel: $CHANNEL"
echo ""

# Test 3: Using clawdbot sessions CLI
echo "Test 3: Use clawdbot sessions --json (chatType becomes 'kind')"
KIND=$(clawdbot sessions --json | \
  jq -r --arg key "$SESSION_KEY" \
  '.sessions[] | select(.key == $key) | .kind')
echo "  Session: $SESSION_KEY"
echo "  kind (was chatType): $KIND"
echo ""

# Test 4: Find all group chats
echo "Test 4: List all group chat sessions"
jq -r 'to_entries[] | select(.value.chatType == "group") | "\(.key) -> \(.value.channel):\(.value.groupId)"' \
  ~/.clawdbot/agents/main/sessions/sessions.json | head -5
echo ""

# Test 5: Get full session metadata
echo "Test 5: Complete session metadata"
jq --arg key "$SESSION_KEY" '.[$key] | {chatType, channel, sessionId, model, totalTokens}' \
  ~/.clawdbot/agents/main/sessions/sessions.json

echo ""
echo "=== All tests complete ==="
