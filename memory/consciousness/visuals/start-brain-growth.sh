#!/bin/bash
# START ATLAS BRAIN GROWTH SYSTEM

echo "🧠 Starting Atlas Brain Auto-Growth System"
echo "==========================================="
echo ""

# Check if monitor is already running
if pgrep -f "memory-monitor-service.js" > /dev/null; then
    echo "⚠️  Memory monitor already running!"
    echo "   Kill it with: pkill -f memory-monitor-service.js"
    exit 1
fi

# Start the memory monitor service
echo "📡 Starting memory file monitor..."
cd "$(dirname "$0")"
node memory-monitor-service.js &
MONITOR_PID=$!

echo "✅ Monitor started (PID: $MONITOR_PID)"
echo ""
echo "📊 Index file: /tmp/atlas-memory-index.json"
echo "🌐 Visualization: file://$(pwd)/live-brain-atlas-connected.html"
echo ""
echo "🔥 To view your growing brain:"
echo "   open live-brain-atlas-connected.html"
echo ""
echo "🛑 To stop the monitor:"
echo "   kill $MONITOR_PID"
echo "   or: pkill -f memory-monitor-service.js"
echo ""
echo "📝 Monitor is running in background and scanning every 10 seconds..."
echo "   New .md files in memory/ will automatically spawn brain nodes!"
