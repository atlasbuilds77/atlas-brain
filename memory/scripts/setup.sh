#!/bin/bash
# Make all brain daemon scripts executable

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Making brain daemon scripts executable..."

chmod +x "$SCRIPT_DIR/brain-daemon.js"
chmod +x "$SCRIPT_DIR/brain-daemon-control.sh"
chmod +x "$SCRIPT_DIR/brain-query.sh"
chmod +x "$SCRIPT_DIR/test-brain-daemon.sh"

echo "✓ Done"
echo ""
echo "Next steps:"
echo "  1. Test: bash $SCRIPT_DIR/test-brain-daemon.sh"
echo "  2. Start: bash $SCRIPT_DIR/brain-daemon-control.sh start"
echo "  3. Status: bash $SCRIPT_DIR/brain-daemon-control.sh status"
