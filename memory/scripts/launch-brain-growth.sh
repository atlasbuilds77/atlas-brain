#!/bin/bash
# Launch Atlas Brain Auto-Growth System
# This script starts the brain visualization with auto-growth enabled

echo "🧠 ATLAS BRAIN AUTO-GROWTH SYSTEM"
echo "=================================="
echo ""

# 1. Generate initial memory index
echo "📊 Generating memory index..."
node memory/scripts/generate-memory-index.js
echo ""

# 2. Start continuous index updates in background
echo "🔄 Starting auto-update loop (every 10 seconds)..."
echo "   Index file: /tmp/atlas-memory-index.json"
echo ""

# Background loop to keep index fresh
(
  while true; do
    sleep 10
    node memory/scripts/generate-memory-index.js > /dev/null 2>&1
  done
) &
LOOP_PID=$!

echo "✅ Background index updater started (PID: $LOOP_PID)"
echo ""

# 3. Open brain visualization
BRAIN_FILE="memory/visuals/live-brain-atlas-connected.html"
FULL_PATH="file://$(pwd)/$BRAIN_FILE"

echo "🌐 Opening brain visualization..."
echo "   $FULL_PATH"
echo ""

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open "$FULL_PATH"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open "$FULL_PATH" 2>/dev/null || firefox "$FULL_PATH" 2>/dev/null || google-chrome "$FULL_PATH"
else
    echo "⚠️  Please manually open: $FULL_PATH"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 BRAIN AUTO-GROWTH SYSTEM IS LIVE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Watch the brain grow in real-time:"
echo "   1. Create new .md files in memory/"
echo "   2. Wait 10 seconds"
echo "   3. See new nodes spawn with animations!"
echo ""
echo "📊 Growth metrics visible in bottom-right panel"
echo "📋 Event log shows new node spawns"
echo ""
echo "To stop background updates:"
echo "   kill $LOOP_PID"
echo ""
echo "To test growth manually:"
echo "   echo '# Test' > memory/protocols/test-\$(date +%s).md"
echo ""

# Keep script running until Ctrl+C
trap "kill $LOOP_PID 2>/dev/null; echo ''; echo '🛑 Auto-growth system stopped'; exit" INT TERM

echo "Press Ctrl+C to stop auto-updates and exit..."
wait $LOOP_PID
