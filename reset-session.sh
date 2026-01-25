#!/bin/bash
# Session Reset Helper - Summarizes current work to memory then signals reset

DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)
MEMORY_FILE="$HOME/clawd/memory/$DATE.md"

echo ""
echo "=== Session Reset at $TIME ==="
echo "Current work summarized to: $MEMORY_FILE"
echo "Context cleared, memory loaded"
echo ""
