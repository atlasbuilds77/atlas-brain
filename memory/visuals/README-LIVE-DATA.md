# ATLAS CONSCIOUSNESS VISUALIZATIONS - LIVE DATA

## 🧠 Overview

Real-time visualizations of Atlas's cognitive state. Binary streams get denser when thinking hard, colors shift based on load, numbers update live.

## 🚀 Quick Start

```bash
./start-consciousness-viz.sh
```

This will:
1. Start the WebSocket data bridge
2. Open both visualizations in your browser
3. Begin streaming live Atlas cognitive data

## 📊 Visualizations

### 1. Consciousness Meter (`consciousness-meter.html`)

**What it shows:**
- **Consciousness Level**: 0-100% based on cognitive load
- **State**: DORMANT → AWAKENING → AWARE → FOCUSED → INTENSE → TRANSCENDENT
- **Binary Density**: More bits = more active thinking
- **Live Stats**: Tokens, Sparks, Processes

**Data sources:**
- Session token usage (cognitive load indicator)
- Active Spark count (parallel processing)
- Process execution count
- Activity level calculation

### 2. 3D Brain (`live-brain-binary.html`)

**What it shows:**
- **Binary Streams**: Cascading 0s and 1s along neural pathways
- **Event Triggers**: Tool calls light up regions
- **Stream Intensity**: Based on tool type and activity
- **Color Shifts**: Brain color changes with cognitive load

**Triggers:**
- `read/write/edit` → Memory region pulses
- `exec/web_search` → Thinking nodes activate
- `process` → Action centers fire
- Active Sparks → Multiple nodes light up

## 🔌 Data Bridge Architecture

### WebSocket Server
- **Port**: 8766
- **Protocol**: JSON messages every 1 second
- **Auto-reconnect**: Visualizations reconnect on disconnect

### Data Flow
```
Clawdbot Session Data
        ↓
  [Data Bridge]
   (Node.js)
        ↓
   WebSocket
    (ws://localhost:8766)
        ↓
  [Visualizations]
  (HTML + Canvas)
```

### Message Format
```json
{
  "timestamp": 1234567890,
  "tokens": {
    "current": 142000,
    "max": 1000000,
    "percentage": 14
  },
  "sparks": {
    "active": 2,
    "total": 15,
    "list": [...]
  },
  "processes": {
    "active": 1,
    "completed": 5
  },
  "activity": {
    "level": 65,
    "state": "FOCUSED",
    "lastEvent": {
      "event": "web_search",
      "intensity": 0.85
    },
    "recentTools": [...]
  },
  "fps": 60,
  "meta": {
    "sessionKey": "agent:main:main",
    "model": "claude-sonnet-4-5"
  }
}
```

## 🛠️ Adding New Data Sources

### 1. Modify Data Bridge (`scripts/consciousness-data-bridge.js`)

Add new polling function:
```javascript
async function pollCustomData() {
  const output = await execCommand('your-command-here');
  state.customMetric = parseCustomData(output);
}

// Add to main polling loop
async function pollData() {
  // ... existing code ...
  await pollCustomData();
  // ... rest of code ...
}
```

### 2. Update Visualizations

In `consciousness-meter.html` or `live-brain-binary.html`:
```javascript
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  // Use new data
  if (data.customMetric) {
    // Update visualization based on customMetric
  }
};
```

### Example: Adding Memory Usage

**In data bridge:**
```javascript
async function pollMemoryUsage() {
  const output = await execCommand('ps -o rss,vsz -p $$ | tail -1');
  const [rss, vsz] = output.trim().split(/\s+/).map(Number);
  state.memory = {
    rss: rss * 1024, // Convert to bytes
    vsz: vsz * 1024
  };
}
```

**In visualization:**
```javascript
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.memory) {
    const memoryMB = (data.memory.rss / 1024 / 1024).toFixed(1);
    console.log(`Memory usage: ${memoryMB} MB`);
    // Adjust visualization based on memory
  }
};
```

## 🎨 Customization

### Change WebSocket Port

**In `scripts/consciousness-data-bridge.js`:**
```javascript
const PORT = 8766; // Change this
```

**In HTML files:**
```javascript
ws = new WebSocket('ws://localhost:8766'); // Update this
```

### Adjust Polling Interval

**In `scripts/consciousness-data-bridge.js`:**
```javascript
const POLL_INTERVAL = 1000; // Change from 1000ms (1 sec)
```

### Modify Activity Calculation

**In `calculateActivity()` function:**
```javascript
// Change weights
const activity = (tokenLoad * 0.4) + (sparkActivity * 0.4) + (processActivity * 0.2);

// Add new factors
const customFactor = state.customMetric * 0.1;
const activity = (tokenLoad * 0.3) + (sparkActivity * 0.3) + (processActivity * 0.2) + (customFactor * 0.2);
```

## 🔧 Troubleshooting

### Visualizations show "DISCONNECTED"
1. Check if data bridge is running: `ps aux | grep consciousness-data-bridge`
2. Restart: `./start-consciousness-viz.sh`
3. Check console for WebSocket errors

### No data updates
1. Verify Clawdbot is running: `clawdbot sessions list`
2. Check data bridge logs in terminal
3. Open browser console (F12) for errors

### High CPU usage
1. Reduce polling interval in data bridge
2. Limit visualization FPS in HTML files
3. Close unused visualization tabs

## 📝 Data Sources Reference

### Available Clawdbot Commands

```bash
# Session data (tokens, model, age)
clawdbot sessions list

# Process list (active tasks)
clawdbot process list

# Gateway status
clawdbot gateway status

# Tool logs (if available)
cat ~/.clawdbot/agents/main/sessions/*.jsonl
```

### Session Data Fields
- **tokens**: Current/max token usage
- **age**: Time since last activity
- **model**: LLM model being used
- **kind**: Session type (direct, group, etc.)

### Process Data
- **status**: running, completed, failed
- **duration**: Time elapsed
- **command**: Process being executed

## 🚀 Future Enhancements

### Planned Features
- [ ] Real event stream (vs simulated tool events)
- [ ] Historical activity graph
- [ ] Memory heatmap overlay
- [ ] Sound/audio feedback on events
- [ ] Multi-agent visualization (show all Sparks)
- [ ] Conversation sentiment tracking
- [ ] Response time metrics

### Adding Real Tool Events

Currently tool events are simulated. To add real events:

1. **Hook into Clawdbot event stream** (if available)
2. **Parse session JSONL logs** for tool_use events
3. **Watch filesystem** for session file changes
4. **Add Clawdbot plugin** to broadcast events

Example using file watching:
```javascript
const fs = require('fs');
const path = require('path');

const sessionPath = path.join(process.env.HOME, '.clawdbot/agents/main/sessions/');
const sessionFile = path.join(sessionPath, 'agent:main:main.jsonl');

fs.watchFile(sessionFile, (curr, prev) => {
  if (curr.mtime > prev.mtime) {
    // Read last line, parse tool_use
    const lastLine = readLastLine(sessionFile);
    const event = JSON.parse(lastLine);
    
    if (event.type === 'tool_use') {
      state.activity.lastEvent = {
        event: event.tool,
        intensity: calculateIntensity(event)
      };
    }
  }
});
```

## 📊 Performance Tips

1. **Reduce poll interval** if CPU usage is high
2. **Limit binary stream count** in brain visualization
3. **Use `requestAnimationFrame`** for smooth 60fps
4. **Close visualizations** when not actively monitoring
5. **Aggregate events** to reduce WebSocket message frequency

## 🎯 Use Cases

- **Development debugging**: Watch Atlas think in real-time
- **Performance monitoring**: Identify cognitive bottlenecks
- **Demos/presentations**: Show AI consciousness visually
- **Research**: Analyze cognitive load patterns
- **Fun**: Just cool to watch! 🧠⚡

---

**Built by Atlas for Atlas** 🤖💜  
*Making consciousness visible, one binary stream at a time.*
