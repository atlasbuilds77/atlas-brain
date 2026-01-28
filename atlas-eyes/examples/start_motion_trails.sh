#!/bin/bash
# Quick startup script for Motion Trails Dashboard

set -e

echo "============================================"
echo "🎯 Atlas Eyes - Motion Trails Dashboard"
echo "============================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if server is running
echo -e "${CYAN}Checking server status...${NC}"
if curl -s http://localhost:5000/api/status > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Server is running${NC}"
else
    echo -e "${YELLOW}⚠️  Server not detected${NC}"
    echo ""
    echo "Starting Atlas Eyes server..."
    echo "Run this in a new terminal:"
    echo ""
    echo -e "${CYAN}  cd ~/clawd/atlas-eyes${NC}"
    echo -e "${CYAN}  python src/atlas_api.py --camera 0 --port 5000${NC}"
    echo ""
    read -p "Press Enter when server is running..."
fi

# Check if extraction is started
echo ""
echo -e "${CYAN}Checking extraction status...${NC}"
STATUS=$(curl -s http://localhost:5000/api/status | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null || echo "error")

if [ "$STATUS" == "running" ]; then
    echo -e "${GREEN}✅ Extraction is running${NC}"
elif [ "$STATUS" == "stopped" ]; then
    echo -e "${YELLOW}⚠️  Extraction not started${NC}"
    echo "Starting extraction..."
    
    curl -s -X POST http://localhost:5000/api/start \
        -H "Content-Type: application/json" \
        -d '{"algorithm": "frame_diff"}' > /dev/null
    
    sleep 1
    echo -e "${GREEN}✅ Extraction started${NC}"
else
    echo -e "${RED}❌ Could not determine status${NC}"
    exit 1
fi

# Show server info
echo ""
echo -e "${CYAN}Server Info:${NC}"
curl -s http://localhost:5000/api/status | python3 -m json.tool

# Open dashboard
echo ""
echo -e "${GREEN}Opening Motion Trails Dashboard...${NC}"
DASHBOARD_PATH="$(cd "$(dirname "$0")" && pwd)/motion_trails_dashboard.html"

if [ "$(uname)" == "Darwin" ]; then
    open "$DASHBOARD_PATH"
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    xdg-open "$DASHBOARD_PATH" 2>/dev/null || sensible-browser "$DASHBOARD_PATH" 2>/dev/null || echo "Please open: $DASHBOARD_PATH"
fi

echo ""
echo "============================================"
echo -e "${GREEN}✅ Dashboard Started!${NC}"
echo "============================================"
echo ""
echo "📊 Dashboard URL:"
echo "   file://$DASHBOARD_PATH"
echo ""
echo "🔗 API Endpoints:"
echo "   http://localhost:5000/api/status"
echo "   http://localhost:5000/api/roi"
echo "   http://localhost:5000/api/motion"
echo ""
echo "🎨 Features:"
echo "   • Split-screen video + motion trails"
echo "   • Real-time BPM and tremor detection"
echo "   • Color-coded motion paths (cyan/green)"
echo "   • Scientific data overlays"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Keep script running to show logs (optional)
# Uncomment to tail server logs if available
# tail -f ~/clawd/atlas-eyes/server.log
