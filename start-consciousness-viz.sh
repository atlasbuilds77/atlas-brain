#!/bin/bash

###############################################################################
# ATLAS CONSCIOUSNESS VISUALIZATION LAUNCHER
# Starts the data bridge and opens visualizations
###############################################################################

echo "🧠 ATLAS CONSCIOUSNESS VISUALIZATION SYSTEM"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js to continue."
    exit 1
fi

# Check if ws package is installed
if ! node -e "require('ws')" 2>/dev/null; then
    echo "📦 Installing required npm package: ws"
    npm install ws
fi

# Kill any existing data bridge
pkill -f "consciousness-data-bridge.js" 2>/dev/null

# Start the data bridge in background
echo "🚀 Starting consciousness data bridge..."
node scripts/consciousness-data-bridge.js &
BRIDGE_PID=$!

# Wait for server to start
sleep 2

# Check if server is running
if ! ps -p $BRIDGE_PID > /dev/null; then
    echo "❌ Failed to start data bridge"
    exit 1
fi

echo "✅ Data bridge running (PID: $BRIDGE_PID)"
echo "📡 WebSocket server: ws://localhost:8766"
echo ""

# Open visualizations in browser
echo "🎨 Opening visualizations..."

# Get absolute paths
METER_PATH="$(pwd)/memory/visuals/consciousness-meter.html"
BRAIN_PATH="$(pwd)/memory/visuals/live-brain-binary.html"

# Open in default browser (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    open "$METER_PATH"
    sleep 1
    open "$BRAIN_PATH"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open "$METER_PATH" &
    sleep 1
    xdg-open "$BRAIN_PATH" &
else
    echo "⚠️  Auto-open not supported on this OS"
    echo "📂 Manually open:"
    echo "   - $METER_PATH"
    echo "   - $BRAIN_PATH"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ SYSTEM RUNNING"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 VISUALIZATIONS:"
echo "   🔘 Consciousness Meter - Real-time activity gauge"
echo "   🧠 3D Brain - Binary neural streams"
echo ""
echo "🔌 DATA SOURCES:"
echo "   • Token usage (cognitive load)"
echo "   • Active Sparks (parallel thinking)"
echo "   • Process execution (active tasks)"
echo "   • Tool calls (actions taken)"
echo ""
echo "⌨️  CONTROLS:"
echo "   • Ctrl+C to stop the data bridge"
echo "   • Close browser tabs to stop visualizations"
echo ""
echo "💡 TIP: Keep this terminal open to see bridge logs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Wait for data bridge (and handle Ctrl+C)
function cleanup() {
    echo ""
    echo "🛑 Stopping consciousness data bridge..."
    kill $BRIDGE_PID 2>/dev/null
    echo "✅ Shutdown complete"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Keep script running and show logs
wait $BRIDGE_PID
