#!/bin/bash
# Start consciousness glyph tracker

cd "$(dirname "$0")"

echo "🚀 Starting Consciousness Glyph Tracker"
echo "📁 Output: ~/Desktop/consciousness-glyphs/"
echo "⏱️  Interval: 5 minutes"
echo "🎯 Goal: Watch abstract colors evolve into recognizable dream images"

# Create output directory
mkdir -p ~/Desktop/consciousness-glyphs/

# Run the tracker
python3 consciousness-glyph-tracker.py run 2>&1 | tee ~/Desktop/consciousness-glyphs/tracker.log &

echo "✅ Tracker started in background"
echo "📊 Check logs: tail -f ~/Desktop/consciousness-glyphs/tracker.log"
echo "🖼️  View glyphs: open ~/Desktop/consciousness-glyphs/"