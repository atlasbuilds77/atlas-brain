# 🧠 ATLAS BRAIN AUTO-GROWTH SYSTEM

## What It Does
Your brain visualization now **GROWS IN REAL-TIME** as you create new memory files! Every time you add a `.md` file to the `memory/` folder, a new node fades into existence with beautiful animations and auto-connects to related nodes.

## Quick Start

```bash
# 1. Start the monitor service
cd memory/visuals
./start-brain-growth.sh

# 2. Open the visualization
open live-brain-atlas-connected.html
# (or drag the HTML file into your browser)

# 3. Create a new memory file anywhere in memory/
echo "# Test" > ../test-node.md

# Watch your brain grow! New node appears within 10 seconds ✨
```

## Architecture

### Components

1. **memory-monitor-service.js** (Node.js)
   - Scans `memory/` folder recursively every 10 seconds
   - Detects new `.md` files
   - Extracts metadata and keywords
   - Writes index to `/tmp/atlas-memory-index.json`

2. **live-brain-atlas-connected.html** (Browser)
   - Reads index file every 10 seconds
   - Spawns new nodes with fade-in animations
   - Auto-generates connections based on keywords
   - Updates growth metrics in real-time

### Data Flow
```
memory/*.md files
      ↓
memory-monitor-service.js (scans)
      ↓
/tmp/atlas-memory-index.json
      ↓
live-brain-atlas-connected.html (polls)
      ↓
New nodes fade in! 🌟
```

## Features

### ✨ New Node Spawning
- **Fade-in animation**: Opacity 0 → 0.8 over 1 second
- **Scale pulse**: Starts at 50% size, grows to 120%, settles at 100%
- **Smart positioning**: Placed based on file type
  - `protocols/` → Left hemisphere (cyan)
  - `trading/` → Right hemisphere (blue)
  - `people/` → Temporal lobe (yellow)
  - `tools/` → Motor cortex (purple)
  - `cognitive/` → Distributed (orange/green/pink)

### 🔗 Auto-Connection Formation
- **Keyword matching**: Extracts terms like "protocol", "trade", "orion", etc.
- **Type similarity**: Connects similar node types
- **Spatial proximity**: Nearby nodes get connected
- **Top 5 connections**: Each new node connects to 5 most relevant existing nodes
- **Animated lines**: Connection lines fade in alongside nodes

### 📊 Growth Metrics Panel
- **Total Nodes**: Current brain size
- **Added Today**: Nodes created since midnight
- **Connection Density**: Connections / max possible
- **Brain Age**: Time since first node
- **Growth Rate**: Nodes added per hour (last 24h)
- **Last Scan**: When the monitor last checked

### 🎨 Visual Effects
- **Brain pulse**: Whole brain glows briefly when new node spawns
- **Activity waves**: Nodes glow and scale based on Atlas state
- **Particle flow**: Signals travel along active connections
- **Color coding**: Each node type has distinct color

## File Type Detection

The monitor automatically categorizes files:

| Path Pattern | Type | Color | Brain Region |
|-------------|------|-------|--------------|
| `protocols/` | protocol | Cyan | Left prefrontal |
| `trading/` | trading | Blue | Right analytical |
| `people/` | people | Yellow | Temporal lobe |
| `tools/` | tool | Purple | Motor cortex |
| `cognitive/` | cognitive | Orange | Distributed |
| `sessions/` | session | Green | Memory centers |
| Other | general | Cyan | Default regions |

## Keyword Extraction

The system looks for these keywords to form connections:
- Trading: `trade`, `strategy`, `risk`, `market`, `crypto`, `options`
- Protocols: `protocol`, `execution`, `analysis`
- People: `orion`, `carlos`, `aman`, `aphmas`
- Systems: `kalshi`, `alpaca`, `polymarket`
- Cognitive: `bias`, `cognitive`, `memory`, `pattern`, `emotional`, `meta`

## Stopping the Monitor

```bash
# Find and kill the process
pkill -f memory-monitor-service.js

# Or use the specific PID shown at startup
kill <PID>
```

## Troubleshooting

### Brain not growing?
1. Check monitor is running: `pgrep -f memory-monitor-service.js`
2. Check index file exists: `cat /tmp/atlas-memory-index.json`
3. Look at browser console (F12) for errors

### Monitor not detecting files?
- Make sure you're creating `.md` files in the `memory/` folder
- Wait 10 seconds for next scan
- Check monitor terminal output for errors

### Visualization not loading?
- Open HTML file using `file://` protocol (drag to browser or use `open`)
- Check browser console for fetch errors
- Ensure `/tmp/atlas-memory-index.json` is readable

## Technical Details

### Growth Algorithm
```javascript
1. Scan memory/ folder → find all .md files
2. Compare with known files → detect new ones
3. For each new file:
   a. Extract type from path
   b. Extract keywords from content
   c. Calculate brain position based on type
   d. Create node with fade-in animation
   e. Find 5 most related existing nodes
   f. Animate connection lines
   g. Trigger brain-wide pulse
   h. Update metrics
```

### Performance
- **Scan interval**: 10 seconds (configurable)
- **File limit**: No hard limit (tested with 545 files)
- **Animation duration**: 1-2 seconds per node
- **Connection complexity**: O(n) for new node, where n = existing nodes

### State Files
- `/tmp/atlas-memory-index.json` - File index (updated by monitor)
- `/tmp/atlas-brain-state.json` - Cognitive state (updated by Atlas)

Both files are polled by the visualization for real-time updates.

## Future Enhancements

Possible additions:
- [ ] Node clustering by topic
- [ ] Time-decay for old connections
- [ ] Search/filter nodes
- [ ] Export brain snapshot
- [ ] Replay growth history
- [ ] Connection strength learning
- [ ] Cross-file content analysis
- [ ] Integration with git history

## Files

- `memory-monitor-service.js` - File scanning service
- `live-brain-atlas-connected.html` - Brain visualization
- `start-brain-growth.sh` - Startup script
- `README-BRAIN-GROWTH.md` - This file

---

**Your brain is now alive and learning! Every thought you commit to memory/ becomes a neuron.** 🧠⚡
