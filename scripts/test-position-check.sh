#!/bin/bash

# Test script for Jupiter position checker
# Verifies that automated position checking works without browser

set -e

echo "======================================"
echo "Jupiter Position Check - Test Script"
echo "======================================"
echo ""

cd "$(dirname "$0")"

# Check dependencies
echo "1. Checking dependencies..."
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi
echo "✅ Dependencies OK"
echo ""

# Check IDL file
echo "2. Checking IDL file..."
if [ ! -f "jupiter-perps-idl.json" ]; then
    echo "❌ ERROR: jupiter-perps-idl.json not found!"
    echo "Run: cp /tmp/jupiter-perps-idl.json scripts/"
    exit 1
fi
echo "✅ IDL file OK"
echo ""

# Test the position check
echo "3. Running position check..."
node jupiter-position-check-v2.js
echo ""

# Verify output file was created
echo "4. Verifying output file..."
OUTPUT_FILE="../memory/trading/jupiter-positions-latest.md"
if [ ! -f "$OUTPUT_FILE" ]; then
    echo "❌ ERROR: Output file not created!"
    exit 1
fi
echo "✅ Output file created: $OUTPUT_FILE"
echo ""

# Show file size and first few lines
FILE_SIZE=$(wc -c < "$OUTPUT_FILE")
echo "   File size: $FILE_SIZE bytes"
echo "   Content preview:"
head -10 "$OUTPUT_FILE" | sed 's/^/   /'
echo ""

echo "======================================"
echo "✅ ALL TESTS PASSED!"
echo "======================================"
echo ""
echo "The position checker is working and ready for cron automation."
echo ""
