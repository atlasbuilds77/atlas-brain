# Atlas Eyes Integration Layer

**Atlas can now ask "What's my heart rate?" and get historical health data automatically.**

## Overview

This integration layer adds persistent event storage and natural language query capabilities to Atlas Eyes, making it easy for Atlas to access health monitoring data.

## Features

✅ **Event Database** - SQLite storage for all health events  
✅ **Automated Logging** - Continuous background logging of heartbeat, tremor, and motion data  
✅ **HTTP API** - RESTful API for querying health data  
✅ **Natural Language Interface** - Human-readable responses for Atlas  
✅ **Background Daemon** - Headless service that runs continuously  
✅ **Auto-start on Boot** - Optional system service configuration  

## Quick Start

### 1. Test the Integration

Run the test suite to verify everything works:

```bash
cd ~/clawd/atlas-eyes
python scripts/test_integration.py
```

This will test:
- Event database operations
- Natural language queries
- API endpoints (if daemon is running)

### 2. Start the Daemon

Start the background monitoring service:

```bash
# Basic start (default port 5000, camera 0)
python scripts/daemon.py

# Custom configuration
python scripts/daemon.py --port 8080 --camera 1

# Start without auto-monitoring (manual start via API)
python scripts/daemon.py --no-auto-start
```

The daemon will:
- Initialize the event database at `~/atlas-eyes-data/motion_events.db`
- Start the camera and motion detection
- Log heartbeat readings every 10 seconds
- Log tremor detections (confidence > 70%)
- Log motion anomalies
- Expose HTTP API on port 5000

### 3. Query Health Data

#### Using Python (Natural Language Interface)

```python
from atlas_query import AtlasQuery

with AtlasQuery() as query:
    # What's my heart rate?
    print(query.get_current_heart_rate())
    # Output: "72 BPM (confident)"
    
    # Any tremors?
    print(query.check_for_tremors(last_hours=24))
    # Output: "2 tremor episodes detected in the last 24 hours..."
    
    # Health summary
    print(query.health_summary(hours=24))
    # Output: Full health report
    
    # Quick check
    print(query.is_everything_normal(hours=1))
    # Output: "✅ Everything looks normal (last 1 hour)"
```

#### Using HTTP API (curl)

```bash
# Current heart rate
curl http://localhost:5000/api/heartbeat/current

# Heart rate history (last 24 hours)
curl http://localhost:5000/api/heartbeat/history?hours=24

# Tremor events
curl http://localhost:5000/api/tremor/events?hours=24

# Health summary
curl http://localhost:5000/api/health/summary?hours=24

# Natural language query
curl http://localhost:5000/api/query/heart_rate
curl http://localhost:5000/api/query/tremors?hours=24
curl http://localhost:5000/api/query/summary?hours=24
```

## API Endpoints

### System Control

- **GET /api/status** - System status and statistics
- **POST /api/start** - Start motion extraction
  ```bash
  curl -X POST http://localhost:5000/api/start \
    -H "Content-Type: application/json" \
    -d '{"algorithm": "frame_diff"}'
  ```
- **POST /api/stop** - Stop motion extraction

### Heartbeat

- **GET /api/heartbeat/current** - Latest BPM reading
  ```json
  {
    "detected": true,
    "bpm": 72.5,
    "confidence": 0.85,
    "timestamp": 1234567890.123,
    "age_seconds": 5.2,
    "fresh": true
  }
  ```

- **GET /api/heartbeat/history?hours=24** - Time series data
  ```json
  {
    "hours": 24,
    "count": 8640,
    "data": [
      {"timestamp": 1234567890.0, "bpm": 72, "confidence": 0.85},
      ...
    ]
  }
  ```

### Tremor

- **GET /api/tremor/events?hours=24&min_confidence=0.7** - Tremor event log
  ```json
  {
    "count": 3,
    "events": [
      {
        "timestamp": 1234567890.0,
        "frequency_hz": 4.2,
        "confidence": 0.92,
        "metadata": {}
      },
      ...
    ]
  }
  ```

### Health Summary

- **GET /api/health/summary?hours=24** - Overall statistics
  ```json
  {
    "hours": 24,
    "heartbeat": {
      "count": 8640,
      "avg_bpm": 72.3,
      "min_bpm": 65,
      "max_bpm": 95,
      "avg_confidence": 0.82
    },
    "tremor": {
      "count": 12,
      "avg_frequency_hz": 4.3,
      "avg_confidence": 0.88
    },
    "motion_spikes": {
      "count": 5
    }
  }
  ```

- **GET /api/health/check?hours=1** - Quick health check
  ```json
  {
    "normal": true,
    "status": "✅ Everything looks normal (last 1 hour)",
    "hours": 1
  }
  ```

### Alert Configuration

- **GET /api/alert/config** - Get current thresholds
- **POST /api/alert/config** - Set thresholds
  ```bash
  curl -X POST http://localhost:5000/api/alert/config \
    -H "Content-Type: application/json" \
    -d '{
      "heartbeat_min": 50,
      "heartbeat_max": 120,
      "tremor_threshold": 0.7,
      "motion_spike_threshold": 0.8
    }'
  ```

### Natural Language Queries

- **GET /api/query/heart_rate** - "What's my heart rate?"
- **GET /api/query/tremors?hours=24** - "Any tremors recently?"
- **GET /api/query/summary?hours=24** - "Give me a health summary"

## Database Schema

The event database (`motion_events.db`) stores:

```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    timestamp REAL NOT NULL,           -- Unix timestamp
    event_type TEXT NOT NULL,          -- 'heartbeat', 'tremor', 'motion_spike', 'anomaly'
    value REAL,                        -- BPM for heartbeat, Hz for tremor, intensity for motion
    confidence REAL,                   -- 0-1 confidence score
    metadata TEXT,                     -- JSON metadata
    created_at REAL DEFAULT (strftime('%s', 'now'))
);
```

Indexed on:
- `timestamp` (for fast time-range queries)
- `event_type` (for filtering by type)
- `created_at` (for cleanup operations)

### Data Retention

By default, events are kept for **30 days**. To manually cleanup:

```python
from event_store import EventStore

with EventStore() as store:
    deleted = store.cleanup_old_events()
    print(f"Deleted {deleted} old events")
```

## Auto-Start on Boot

### macOS (LaunchAgent)

Create and install the auto-start service:

```bash
python scripts/daemon.py --install

# Enable
launchctl load ~/Library/LaunchAgents/com.atlas.eyes.daemon.plist

# Start now
launchctl start com.atlas.eyes.daemon

# Stop
launchctl stop com.atlas.eyes.daemon

# Disable
launchctl unload ~/Library/LaunchAgents/com.atlas.eyes.daemon.plist
```

### Linux (systemd)

```bash
python scripts/daemon.py --install

# Enable auto-start
systemctl --user enable atlas-eyes.service

# Start now
systemctl --user start atlas-eyes.service

# Check status
systemctl --user status atlas-eyes.service

# Stop
systemctl --user stop atlas-eyes.service
```

## File Structure

```
~/clawd/atlas-eyes/
├── src/
│   ├── event_store.py          # Event database (NEW)
│   ├── atlas_query.py          # Natural language interface (NEW)
│   ├── atlas_api_enhanced.py   # Enhanced API with DB integration (NEW)
│   ├── motion_extractor.py     # Core motion detection
│   ├── frequency_analyzer.py   # FFT-based heartbeat/tremor detection
│   └── atlas_api.py            # Original API (legacy)
├── scripts/
│   ├── daemon.py               # Background daemon (NEW)
│   └── test_integration.py     # Integration tests (NEW)
└── ~/atlas-eyes-data/          # Data directory
    ├── motion_events.db        # Event database
    ├── daemon.log              # Daemon logs
    ├── stdout.log              # Stdout
    └── stderr.log              # Stderr
```

## Example: Atlas Integration

### Simple Query Script for Atlas

```python
#!/usr/bin/env python3
"""
Example: How Atlas can query health data
"""

import sys
sys.path.insert(0, '/Users/atlasbuilds/clawd/atlas-eyes/src')

from atlas_query import (
    get_current_heart_rate,
    check_for_tremors,
    health_summary,
    is_everything_normal
)

# Quick functions (no setup needed)
print("Heart Rate:", get_current_heart_rate())
print("\nTremors:", check_for_tremors(last_hours=24))
print("\nHealth Check:", is_everything_normal(hours=1))
print("\n" + health_summary(hours=24))
```

### Via HTTP (for remote access)

```python
import requests

def ask_atlas_eyes(question: str) -> str:
    """Ask Atlas Eyes a question in natural language"""
    
    base_url = "http://localhost:5000"
    
    if "heart rate" in question.lower():
        response = requests.get(f"{base_url}/api/query/heart_rate")
    elif "tremor" in question.lower():
        response = requests.get(f"{base_url}/api/query/tremors?hours=24")
    elif "summary" in question.lower() or "how am i" in question.lower():
        response = requests.get(f"{base_url}/api/query/summary?hours=24")
    else:
        return "I can answer questions about heart rate, tremors, and health summary."
    
    return response.json()['response']

# Example usage
print(ask_atlas_eyes("What's my heart rate?"))
print(ask_atlas_eyes("Any tremors today?"))
print(ask_atlas_eyes("Give me a health summary"))
```

## Testing

### Run Tests

```bash
# Full test suite
python scripts/test_integration.py

# Just database tests
python -c "from test_integration import test_event_store; test_event_store()"

# Just query interface tests
python -c "from test_integration import test_atlas_query; test_atlas_query()"
```

### Manual Testing

```bash
# Start daemon
python scripts/daemon.py &

# Wait 1 minute for data collection

# Test queries
curl http://localhost:5000/api/query/heart_rate
curl http://localhost:5000/api/heartbeat/history?hours=1
curl http://localhost:5000/api/health/summary
```

### Verify Data Collection

```python
from event_store import EventStore

with EventStore() as store:
    # Check event counts
    print(f"Heartbeat events (24h): {store.count_events('heartbeat', hours=24)}")
    print(f"Tremor events (24h): {store.count_events('tremor', hours=24)}")
    
    # View recent events
    recent = store.query_recent(limit=10)
    for event in recent:
        print(f"{event['event_type']}: {event['value']} @ {event['confidence']:.0%}")
    
    # Statistics
    stats = store.get_stats('heartbeat', hours=24)
    print(f"\nHeartbeat stats: {stats['count']} readings, avg {stats['avg_value']:.1f} BPM")
```

## Troubleshooting

### Daemon won't start

```bash
# Check logs
tail -f ~/atlas-eyes-data/daemon.log

# Check if port is in use
lsof -i :5000

# Try different port
python scripts/daemon.py --port 8080
```

### No camera access

```bash
# List available cameras (macOS)
system_profiler SPCameraDataType

# Try different camera index
python scripts/daemon.py --camera 1
```

### No heartbeat detection

- Ensure good lighting
- Position camera to see visible motion (e.g., neck/wrist)
- Wait at least 10 seconds for buffer to fill
- Check confidence threshold in `/api/alert/config`

### Database locked

```bash
# Check if multiple instances are running
ps aux | grep daemon.py

# Remove lock (only if no daemon running)
rm ~/atlas-eyes-data/motion_events.db-journal
```

## Performance

### Expected Metrics

- **Heartbeat logging**: ~8,640 events/day (every 10 seconds)
- **Database size**: ~5-10 MB/day
- **CPU usage**: ~5-10% (single core)
- **Memory**: ~100-200 MB

### Optimization

```python
# Adjust logging interval (in daemon or API)
self.heartbeat_log_interval = 30  # Log every 30 seconds instead of 10

# Reduce retention period
store = EventStore(db_path, retention_days=7)  # Keep only 7 days

# Manual cleanup
store.cleanup_old_events()
```

## Next Steps

1. **Run 10-minute test**: `python scripts/daemon.py` and let it run
2. **Query data**: Use the examples above to verify data collection
3. **Integrate with Atlas**: Import `atlas_query.py` in Atlas's main code
4. **Optional**: Set up auto-start for continuous monitoring

## Support

For issues or questions:
- Check logs: `~/atlas-eyes-data/daemon.log`
- Run tests: `python scripts/test_integration.py`
- Verify API: `curl http://localhost:5000/api/status`
