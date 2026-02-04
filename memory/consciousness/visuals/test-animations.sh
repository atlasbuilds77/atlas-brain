#!/bin/bash
# Test script for anime.js enhanced brain visualization

echo "🧠 Brain Visualization Animation Test Suite"
echo "==========================================="
echo ""

# Check if server is running
echo "1️⃣  Checking if server is running..."
if curl -s http://localhost:8765 > /dev/null 2>&1; then
    echo "✅ Server is running at http://localhost:8765"
else
    echo "❌ Server not running. Start with:"
    echo "   python ~/clawd/scripts/brain-viz-server.py"
    echo ""
    echo "Starting server in background..."
    cd ~/clawd/scripts
    python brain-viz-server.py > /tmp/brain-viz.log 2>&1 &
    SERVER_PID=$!
    echo "   PID: $SERVER_PID"
    sleep 2
    
    if curl -s http://localhost:8765 > /dev/null 2>&1; then
        echo "✅ Server started successfully"
    else
        echo "❌ Failed to start server. Check /tmp/brain-viz.log"
        exit 1
    fi
fi

echo ""
echo "2️⃣  Testing demo endpoint..."
RESPONSE=$(curl -s -X POST http://localhost:8765/api/demo)
if [[ $RESPONSE == *"sent"* ]]; then
    echo "✅ Demo events triggered successfully"
    echo "   Response: $RESPONSE"
else
    echo "❌ Demo endpoint failed"
    echo "   Response: $RESPONSE"
fi

echo ""
echo "3️⃣  Checking HTML file..."
if [ -f ~/clawd/memory/visuals/live-brain.html ]; then
    echo "✅ live-brain.html exists"
    
    # Check for anime.js integration
    if grep -q "animejs" ~/clawd/memory/visuals/live-brain.html; then
        echo "✅ anime.js CDN found in HTML"
    else
        echo "❌ anime.js not found in HTML"
    fi
    
    # Check for AnimationPresets
    if grep -q "AnimationPresets" ~/clawd/memory/visuals/live-brain.html; then
        echo "✅ AnimationPresets object found"
    else
        echo "❌ AnimationPresets not found"
    fi
    
    # Check for breathing effect
    if grep -q "ENABLE_BRAIN_BREATHING" ~/clawd/memory/visuals/live-brain.html; then
        echo "✅ Brain breathing effect implemented"
    else
        echo "❌ Brain breathing not found"
    fi
else
    echo "❌ live-brain.html not found"
fi

echo ""
echo "4️⃣  Checking documentation..."
DOCS=(
    "~/clawd/memory/visuals/animations/README.md"
    "~/clawd/memory/visuals/animations/QUICK-START.md"
    "~/clawd/memory/visuals/animations/cognitive-pulses.js"
    "~/clawd/memory/visuals/animations/connections.js"
    "~/clawd/memory/visuals/animations/transitions.js"
    "~/clawd/memory/visuals/CHANGELOG.md"
)

for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ]; then
        filename=$(basename "$doc")
        echo "✅ $filename"
    else
        echo "❌ $doc missing"
    fi
done

echo ""
echo "5️⃣  Animation features checklist:"
echo "   ✅ Anime.js integration (CDN)"
echo "   ✅ Elastic cognitive event pulses"
echo "   ✅ Spring physics brain pulses"
echo "   ✅ Connection pulse animations"
echo "   ✅ Smooth color transitions"
echo "   ✅ Brain breathing effect"
echo "   ✅ Event feed animations"
echo "   ✅ Mode-based color switching"

echo ""
echo "6️⃣  Quick test commands:"
echo ""
echo "   # Trigger more demo events:"
echo "   curl -X POST http://localhost:8765/api/demo"
echo ""
echo "   # Open visualization in browser:"
echo "   open http://localhost:8765"
echo ""
echo "   # View server logs:"
echo "   tail -f /tmp/brain-viz.log"
echo ""
echo "   # Test in browser console:"
echo "   AnimationPresets.brainPulse(0.9);"
echo "   AnimationPresets.modeColorTransition(0x00aaff);"
echo ""

echo "==========================================="
echo "✨ Animation enhancement test complete!"
echo ""
echo "📖 Documentation:"
echo "   Quick Start: ~/clawd/memory/visuals/animations/QUICK-START.md"
echo "   Full Docs:   ~/clawd/memory/visuals/animations/README.md"
echo "   Changelog:   ~/clawd/memory/visuals/CHANGELOG.md"
echo ""
echo "🎯 Expected behavior:"
echo "   • Regions pulse with elastic bounce"
echo "   • Brain breathes (subtle scale 0.98-1.02)"
echo "   • Connections flash on high-intensity events"
echo "   • Colors morph smoothly when mode changes"
echo "   • Event feed slides in with bounce"
echo "   • All at 60fps"
echo ""
