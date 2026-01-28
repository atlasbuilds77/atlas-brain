#!/usr/bin/env bash
# Quick start script for Atlas Brain Visualization

set -euo pipefail

echo "╔════════════════════════════════════════════╗"
echo "║   ATLAS BRAIN VISUALIZATION - JARVIS MODE  ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Check dependencies
echo "🔍 Checking dependencies..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.7+"
    exit 1
fi

if ! python3 -c "import aiohttp" 2>/dev/null; then
    echo "📦 Installing aiohttp..."
    pip3 install aiohttp
fi

echo "✓ Dependencies OK"
echo ""

# Create necessary directories
mkdir -p logs memory/visuals

# Check if demo mode requested
DEMO_MODE=false
if [ "${1:-}" = "demo" ]; then
    DEMO_MODE=true
    echo "🎬 Demo mode enabled - will generate test events"
    echo ""
fi

# Start server in background if not already running
if ! lsof -i :8765 &>/dev/null; then
    echo "🚀 Starting brain visualization server..."
    python3 scripts/brain-viz-server.py &
    SERVER_PID=$!
    echo "   PID: $SERVER_PID"
    
    # Wait for server to start
    sleep 2
    
    # Save PID for cleanup
    echo $SERVER_PID > /tmp/atlas-brain-viz.pid
else
    echo "✓ Server already running on port 8765"
fi

echo ""
echo "🌐 Visualization available at: http://localhost:8765"
echo ""

# Start demo mode if requested
if [ "$DEMO_MODE" = true ]; then
    echo "🎭 Starting demo event generator..."
    sleep 1
    curl -s -X POST http://localhost:8765/api/demo > /dev/null
    echo "   Demo events streaming..."
    echo ""
    echo "📺 Open http://localhost:8765 in your browser to see the visualization"
    echo ""
    echo "Press Ctrl+C to stop demo mode"
    
    # Keep script running
    trap 'echo ""; echo "🛑 Stopping demo mode..."; exit 0' INT
    while true; do
        sleep 1
    done
else
    echo "💡 Test the visualization:"
    echo "   ./scripts/brain-monitor.sh test        # Generate test events"
    echo "   ./scripts/brain-logger.py test         # Python test events"
    echo "   curl -X POST http://localhost:8765/api/demo   # Auto demo mode"
    echo ""
    echo "📖 Documentation: memory/capabilities/live-brain-visualization.md"
    echo ""
    echo "🛑 To stop server: kill \$(cat /tmp/atlas-brain-viz.pid)"
fi
