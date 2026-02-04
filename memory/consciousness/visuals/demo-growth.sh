#!/bin/bash
# Quick demo of brain growth system

echo "🧠 BRAIN GROWTH DEMO"
echo "===================="
echo ""
echo "Current node count:"
jq '.totalFiles' /tmp/atlas-memory-index.json
echo ""
echo "Creating test file in 3 seconds..."
sleep 3

# Create a test file
cat > /tmp/test-growth-$$.md << 'EOF'
# Auto-Growth Test $(date +%H:%M:%S)

Testing the brain growth system with keywords:
- trading
- strategy  
- orion
- risk
EOF

mv /tmp/test-growth-$$.md memory/

echo "✅ Created memory/test-growth-$$.md"
echo ""
echo "Waiting for monitor to detect (up to 10 seconds)..."
sleep 12

echo ""
echo "New node count:"
jq '.totalFiles' /tmp/atlas-memory-index.json
echo ""
echo "✨ Check the visualization to see your new node fade in!"
echo "   New nodes appear with animations within 10 seconds"
