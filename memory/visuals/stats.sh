#!/bin/bash
# Display current brain growth stats

echo "🧠 ATLAS BRAIN STATS"
echo "===================="
echo ""

if [ ! -f /tmp/atlas-memory-index.json ]; then
    echo "❌ Index file not found. Is the monitor running?"
    exit 1
fi

# Extract stats using jq
echo "📊 Overview:"
jq -r '"  Total Files: \(.totalFiles)
  New This Session: \(.newFilesThisSession)
  Last Update: \(.timestamp)"' /tmp/atlas-memory-index.json

echo ""
echo "📁 Files by Type:"
jq -r '.files | group_by(.type) | map({type: .[0].type, count: length}) | .[] | "  \(.type): \(.count)"' /tmp/atlas-memory-index.json

echo ""
echo "🔑 Top Keywords:"
jq -r '.files | map(.keywords // []) | flatten | group_by(.) | map({keyword: .[0], count: length}) | sort_by(-.count) | .[0:10] | .[] | "  \(.keyword): \(.count)"' /tmp/atlas-memory-index.json

echo ""
echo "📈 Recent Files:"
jq -r '.files | sort_by(.modified) | reverse | .[0:5] | .[] | "  ✨ \(.name) (\(.type))"' /tmp/atlas-memory-index.json

echo ""
echo "🎯 Monitor Status:"
if pgrep -f memory-monitor-service.js > /dev/null; then
    PID=$(pgrep -f memory-monitor-service.js)
    echo "  ✅ Running (PID: $PID)"
else
    echo "  ❌ Not running"
fi

echo ""
