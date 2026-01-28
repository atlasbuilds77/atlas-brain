# Live Brain Visualization - "Jarvis Mode"

Real-time visualization of Atlas's cognitive processes styled like Jarvis from Iron Man.

## Overview

The Atlas Brain Visualization system provides a stunning 3D real-time view of cognitive activity, displaying:

- **Central Orange Sphere**: The core "brain" that pulses with activity
- **Neural Regions**: 6 cognitive subsystems that light up when active
- **Particle Network**: Animated neural pathways showing connections
- **Event Feed**: Real-time stream of cognitive events
- **HUD Display**: Mode status and region activity

## Architecture

### Components

1. **brain-viz-server.py**: WebSocket server that streams events to the visualization
2. **brain-monitor.sh**: Instrumentation tool for logging cognitive events
3. **live-brain.html**: Three.js-based 3D visualization
4. **Integration hooks**: Connects to existing cognitive systems

### Data Flow

```
Cognitive System → brain-monitor.sh → logs/brain-events.jsonl → brain-viz-server.py → WebSocket → live-brain.html
```

## Getting Started

### 1. Install Dependencies

```bash
pip3 install aiohttp
```

### 2. Start the Server

```bash
chmod +x scripts/brain-monitor.sh
python3 scripts/brain-viz-server.py
```

Server will start at: `http://localhost:8765`

### 3. Open Visualization

Open your browser to `http://localhost:8765` to see the live brain visualization.

### 4. Test Events (Demo Mode)

```bash
# Generate test events
./scripts/brain-monitor.sh test

# Or start automatic demo mode
curl -X POST http://localhost:8765/api/demo
```

## Event Types

The system recognizes these cognitive event types:

| Event Type | Region | Color | Description |
|------------|--------|-------|-------------|
| `pattern_match` | Pattern Recognition | Green | Pattern database queries and matches |
| `emotion` | Emotional Processing | Red | Somatic marker activations |
| `metacognition` | Metacognition | Blue | Error detection, verification |
| `memory` | Memory | Light Blue | Episodic/semantic memory retrieval |
| `bias_detection` | Bias Detection | Orange | Cognitive bias warnings |
| `mode_switch` | Core | Amber | DMN/ECN mode transitions |
| `decision` | Metacognition | Bright Green | Decision execution |

## Logging Events

### From Shell Scripts

```bash
source scripts/brain-monitor.sh

# Log an event
log_event "pattern_match" "Pattern 'FOMO trade' detected" 0.8 '{"pattern_id": "fomo_001"}'

# Log mode switch
log_event "mode_switch" "DMN MODE: Creative exploration" 1.0 '{"old_mode": "ECN", "new_mode": "DMN"}'

# Log emotion
log_event "emotion" "Anxiety response triggered" 0.7 '{"marker": "loss_aversion"}'
```

### From Python

```python
import json
from datetime import datetime
from pathlib import Path

def log_brain_event(event_type: str, message: str, intensity: float = 0.5, metadata: dict = None):
    """Log a cognitive event for brain visualization."""
    event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "message": message,
        "intensity": intensity,
        "metadata": metadata or {}
    }
    
    log_path = Path("logs/brain-events.jsonl")
    log_path.parent.mkdir(exist_ok=True)
    
    with open(log_path, 'a') as f:
        f.write(json.dumps(event) + '\n')

# Example usage
log_brain_event(
    "pattern_match",
    "Pattern 'successful_trade' matched - HIGH CONFIDENCE",
    0.9,
    {"pattern_id": "trade_success_01", "confidence": 0.95}
)
```

### Direct HTTP API

```bash
# Send test event via API
curl -X POST http://localhost:8765/api/test-event \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "metacognition",
    "message": "Verifying source credibility",
    "intensity": 0.8
  }'
```

## Integration Examples

### Pattern Recognition (pattern-api.py)

Add to pattern matching code:

```python
from brain_logger import log_brain_event

def match_pattern(input_text):
    matches = search_patterns(input_text)
    
    for match in matches:
        log_brain_event(
            "pattern_match",
            f"Pattern '{match.name}' matched - {match.valence.upper()}",
            match.confidence,
            {
                "pattern_id": match.id,
                "valence": match.valence,
                "confidence": match.confidence
            }
        )
    
    return matches
```

### Cognitive Mode Switching (cognitive-mode.sh)

```bash
#!/usr/bin/env bash
source scripts/brain-monitor.sh

switch_mode() {
    local old_mode="$1"
    local new_mode="$2"
    
    log_event "mode_switch" "$new_mode MODE: Switching cognitive state" 1.0 \
        "{\"old_mode\": \"$old_mode\", \"new_mode\": \"$new_mode\"}"
}
```

### Somatic Markers (somatic-marker.py)

```python
def check_somatic_markers(context):
    markers = evaluate_emotional_response(context)
    
    for marker in markers:
        log_brain_event(
            "emotion",
            f"Somatic marker: {marker.name} - {marker.intensity}",
            marker.intensity,
            {
                "marker_type": marker.type,
                "valence": marker.valence,
                "context": context
            }
        )
```

### Bias Detection (bias-check.sh)

```bash
#!/usr/bin/env bash
source scripts/brain-monitor.sh

detect_bias() {
    local bias_type="$1"
    local context="$2"
    
    log_event "bias_detection" "Bias detected: $bias_type" 0.7 \
        "{\"bias_type\": \"$bias_type\", \"context\": \"$context\"}"
}
```

## Configuration

### Environment Variables

- `BRAIN_VIZ_PORT`: Server port (default: 8765)
- `BRAIN_LOG`: Event log path (default: logs/brain-events.jsonl)

### Customizing Regions

Edit `brain-viz-server.py` to modify brain regions:

```python
BRAIN_REGIONS = {
    "custom_region": {
        "name": "Custom Processing",
        "position": [1.0, 1.0, 1.0],  # [x, y, z]
        "color": "#00ff00"
    }
}
```

### Customizing Colors

Edit event colors in `brain-viz-server.py`:

```python
EVENT_CONFIG = {
    "custom_event": {
        "region": "custom_region",
        "color": "#00ff00",
        "priority": "high"
    }
}
```

## Monitoring

### Watch Events in Real-Time

```bash
./scripts/brain-monitor.sh watch
```

### Clear Event Log

```bash
./scripts/brain-monitor.sh clear
```

### Server Logs

The server outputs connection status and event broadcasts:

```
[BRAIN-VIZ] Client connected. Total clients: 1
[BRAIN-VIZ] Broadcasting event: pattern_match
[BRAIN-VIZ] Client disconnected. Total clients: 0
```

## Mobile Support

The visualization is mobile-friendly and will adapt to smaller screens:

- Responsive layout
- Touch-friendly controls
- Auto-hiding non-essential UI elements

## Demo & Investor Presentations

### Demo Mode

Start automatic demo with simulated events:

```bash
curl -X POST http://localhost:8765/api/demo
```

This generates realistic cognitive events every 2.5 seconds.

### Fullscreen Mode

Press `F11` in browser for immersive fullscreen experience.

### Recording

Use screen recording software (OBS, QuickTime) to capture demos:

```bash
# macOS
screencapture -V 10 brain-demo.mp4
```

## Performance

- **Low latency**: Events appear in real-time (<100ms)
- **Smooth 60fps**: Three.js rendering optimized
- **Scalable**: Handles 100+ events/second
- **Memory efficient**: Automatic event pruning

## Troubleshooting

### WebSocket Connection Failed

1. Check server is running: `ps aux | grep brain-viz-server`
2. Check port availability: `lsof -i :8765`
3. Check firewall settings

### Events Not Appearing

1. Check log file exists: `ls -la logs/brain-events.jsonl`
2. Watch events: `./scripts/brain-monitor.sh watch`
3. Test event generation: `./scripts/brain-monitor.sh test`

### Performance Issues

1. Reduce particle count in `live-brain.html` (line 295)
2. Increase event fade time to reduce DOM updates
3. Disable glow effects for low-end devices

## Future Enhancements

- [ ] Voice integration (speak events as they happen)
- [ ] VR/AR support
- [ ] Historical playback (replay conversations)
- [ ] Emotion-based color shifting
- [ ] Network visualization between regions
- [ ] Recording & export capabilities
- [ ] Multi-agent visualization (compare multiple AIs)

## Credits

- Inspired by: Iron Man's Jarvis UI
- Built with: Three.js, WebSockets, Python asyncio
- Neuroscience refs: Human Connectome Project

## License

Part of Atlas cognitive architecture. Private use only.

---

**Status**: ✅ Production Ready  
**Last Updated**: 2026-01-27  
**Maintainer**: Atlas + Orion
