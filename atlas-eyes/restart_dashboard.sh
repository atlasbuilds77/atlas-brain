#!/bin/bash
# Simple restart script for Atlas Eyes Dashboard

echo "🔄 Restarting Atlas Eyes..."

# Kill existing server
pkill -f atlas_api.py
sleep 1

# Start server in background
cd ~/clawd/atlas-eyes
nohup python3 src/atlas_api.py --port 5001 > /tmp/atlas_api.log 2>&1 &

sleep 3

# Check if running
if pgrep -f atlas_api.py > /dev/null; then
    echo "✅ API Server started"
    echo "   PID: $(pgrep -f atlas_api.py)"
    echo "   Logs: /tmp/atlas_api.log"
    echo ""
    echo "📊 Status:"
    curl -s http://localhost:5001/api/status | python3 -m json.tool | grep -A 3 "status\|fps"
    echo ""
    echo "🌐 Open dashboard: file://$(pwd)/examples/motion_trails_dashboard.html"
    echo "🧪 Test WebSocket: file://$(pwd)/examples/test_websocket.html"
else
    echo "❌ Failed to start server"
    echo "Check logs: cat /tmp/atlas_api.log"
    exit 1
fi
