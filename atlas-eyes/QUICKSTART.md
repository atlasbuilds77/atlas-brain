# Atlas Eyes - Quick Start Guide

Get Atlas asking about health data in 5 minutes.

## Installation

```bash
cd ~/clawd/atlas-eyes

# Install dependencies (if not already installed)
pip3 install -r requirements.txt
```

## Step 1: Run Tests (30 seconds)

Verify the integration layer works:

```bash
# Test database and query interface
python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'src'))
from event_store import EventStore, log_heartbeat
from atlas_query import get_current_heart_rate

# Create test data
with EventStore('/tmp/test.db') as store:
    log_heartbeat(store, 72, 0.9, {})

# Query it
print('Atlas asks: What is my heart rate?')
print('Response:', get_current_heart_rate('/tmp/test.db'))
print('\n✅ Integration layer working!')
"
```

Expected output:
```
Atlas asks: What is my heart rate?
Response: 72 BPM (confident)

✅ Integration layer working!
```

## Step 2: Start Background Daemon (optional)

For continuous monitoring:

```bash
# Start daemon (will begin logging heartbeat data)
python3 scripts/daemon.py

# In another terminal, test it
curl http://localhost:5000/api/status
curl http://localhost:5000/api/query/heart_rate
```

**Note:** The daemon needs camera access. On macOS, you may need to grant Terminal camera permissions in System Settings > Privacy & Security > Camera.

## Step 3: Use in Your Code

### Simple Approach (Just Works™)

```python
import sys
sys.path.insert(0, '/Users/atlasbuilds/clawd/atlas-eyes/src')

from atlas_query import get_current_heart_rate, check_for_tremors, health_summary

# Atlas can now call these functions directly:
print(get_current_heart_rate())
print(check_for_tremors(last_hours=24))
print(health_summary(hours=24))
```

### HTTP API Approach (For Remote Access)

```python
import requests

def ask_about_health(question):
    if "heart rate" in question.lower():
        r = requests.get('http://localhost:5000/api/query/heart_rate')
        return r.json()['response']
    elif "tremor" in question.lower():
        r = requests.get('http://localhost:5000/api/query/tremors')
        return r.json()['response']
    elif "summary" in question.lower():
        r = requests.get('http://localhost:5000/api/query/summary')
        return r.json()['response']

# Usage
print(ask_about_health("What's my heart rate?"))
```

## What Gets Logged?

When the daemon is running:

- **Heartbeat**: Every 10 seconds (if detected with >50% confidence)
- **Tremor**: When detected with >70% confidence
- **Motion Spikes**: When intensity >80% (sudden movements)

All data stored in `~/atlas-eyes-data/motion_events.db`

## Common Questions

### "No heart rate data available yet"

The system needs ~10 seconds to collect enough data for heartbeat detection. Wait a bit and try again.

### "Daemon not running"

Start it: `python3 scripts/daemon.py`

### "ModuleNotFoundError"

Install dependencies: `pip3 install -r requirements.txt`

### "Camera not accessible"

- Check camera permissions in System Settings (macOS)
- Try a different camera: `python3 scripts/daemon.py --camera 1`
- Ensure no other app is using the camera

## Next Steps

1. **Let it run for 10 minutes** to collect baseline data
2. **Query the data** using the examples above
3. **Check the README** for full API documentation: `INTEGRATION_README.md`
4. **Integrate with Atlas** by importing the query functions

## Files Created

- `~/atlas-eyes-data/motion_events.db` - Event database
- `~/atlas-eyes-data/daemon.log` - Log file
- Logs kept for 30 days (configurable)

## Example Session

```bash
# Terminal 1: Start daemon
cd ~/clawd/atlas-eyes
python3 scripts/daemon.py

# Terminal 2: Query data (after 30 seconds)
curl http://localhost:5000/api/query/heart_rate
# Output: {"response": "72 BPM (confident)"}

curl http://localhost:5000/api/heartbeat/history?hours=1
# Output: {"hours": 1, "count": 6, "data": [...]}

# Or use Python
python3 -c "
import sys
sys.path.insert(0, 'src')
from atlas_query import health_summary
print(health_summary(hours=1))
"
```

## Troubleshooting

Check logs:
```bash
tail -f ~/atlas-eyes-data/daemon.log
```

Check database:
```bash
python3 -c "
import sys
sys.path.insert(0, 'src')
from event_store import EventStore

with EventStore('~/atlas-eyes-data/motion_events.db') as store:
    print('Total events (24h):', store.count_events(hours=24))
    print('Heartbeats:', store.count_events('heartbeat', hours=24))
    print('Tremors:', store.count_events('tremor', hours=24))
"
```

That's it! Atlas Eyes is now queryable and persistent. 🎉
