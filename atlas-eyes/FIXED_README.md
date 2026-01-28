# 🔥 Atlas Eyes API - FIXED AND WORKING

## ✅ What Was Fixed

### Critical Issues Resolved:
1. **Port Conflict**: Changed default port from 5000 → 5001 (macOS AirPlay Receiver uses 5000)
2. **Auto-Start**: Motion extraction now starts automatically when server launches
3. **Host Binding**: Changed from `127.0.0.1` to `0.0.0.0` for better connectivity
4. **JSON Serialization**: Fixed numpy boolean type in `/api/motion` endpoint
5. **Data Type Conversion**: Properly convert numpy types to Python native types

### What Now Works:
- ✅ API server starts and responds immediately
- ✅ All 6 REST endpoints working (status, motion, heartbeat, tremor, roi, frequency)
- ✅ WebSocket connection for real-time streaming
- ✅ Auto-start motion extraction on server launch
- ✅ Dashboard can connect and receive data

## 🚀 Quick Start

### Option 1: Auto-Start Script (Recommended)
```bash
cd ~/clawd/atlas-eyes
./start_atlas_eyes.sh
```

**With dashboard auto-open:**
```bash
./start_atlas_eyes.sh --dashboard
```

**Background mode:**
```bash
./start_atlas_eyes.sh --background
```

### Option 2: Direct Python Launch
```bash
cd ~/clawd/atlas-eyes
python3 src/atlas_api.py
```

**Custom port/camera:**
```bash
python3 src/atlas_api.py --port 5001 --camera 0
```

**Disable auto-start:**
```bash
python3 src/atlas_api.py --no-auto-start
```

## 🧪 Testing

### Test All API Endpoints
```bash
cd ~/clawd/atlas-eyes
./test_api_simple.sh
```

Expected output:
```
================================
Atlas Eyes API Simple Test
================================

Testing: GET /api/status
✅ PASS - Status: 200

Testing: GET /api/heartbeat
✅ PASS - Status: 200

Testing: GET /api/tremor
✅ PASS - Status: 200

Testing: GET /api/roi
✅ PASS - Status: 200

Testing: GET /api/motion
✅ PASS - Status: 200

Testing: GET /api/frequency
✅ PASS - Status: 200

================================
Results: 6 passed, 0 failed
================================

🎉 All tests passed!
```

### Test Individual Endpoints
```bash
# Server status
curl http://localhost:5001/api/status | python3 -m json.tool

# Heartbeat detection
curl http://localhost:5001/api/heartbeat | python3 -m json.tool

# ROI tracking
curl http://localhost:5001/api/roi | python3 -m json.tool

# Motion data
curl http://localhost:5001/api/motion | python3 -m json.tool
```

### Test WebSocket Connection
1. Open `test_websocket.html` in your browser
2. You should see connection status and data updates
3. Or open the full dashboard: `examples/motion_trails_dashboard.html`

## 📡 API Endpoints

All endpoints respond on **http://localhost:5001**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/status` | System status and stats |
| GET | `/api/motion` | Current motion data |
| GET | `/api/heartbeat` | Heartbeat detection (BPM) |
| GET | `/api/tremor` | Tremor detection (frequency) |
| GET | `/api/roi` | ROI tracking with analysis |
| GET | `/api/frequency` | Full frequency spectrum |
| POST | `/api/start` | Start motion extraction |
| POST | `/api/stop` | Stop motion extraction |
| WS | `/` | Real-time WebSocket stream |

## 🎨 Dashboard

**Location:** `examples/motion_trails_dashboard.html`

**To use:**
1. Start the API server (see Quick Start above)
2. Open `motion_trails_dashboard.html` in your browser
3. Dashboard will automatically connect to `http://localhost:5001`
4. You should see:
   - Real-time video feed with ROI boxes
   - Motion trails visualization
   - BPM readings (from chest movements)
   - Tremor detection (from hand movements)
   - Frequency spectrum
   - Live statistics

## 🔧 Configuration

### Change Port (if 5001 is also in use)
```bash
python3 src/atlas_api.py --port 5002
```

Then update dashboard:
```javascript
// In motion_trails_dashboard.html, line ~130
const CONFIG = {
    WS_URL: 'http://localhost:5002',  // Change this
    ...
};
```

### Change Camera
```bash
python3 src/atlas_api.py --camera 1  # Use camera index 1
```

### Debug Mode
```bash
python3 src/atlas_api.py --debug
```

## ✨ What's Working Now

### Server Behavior:
- ✅ Starts on port 5001 (avoiding macOS AirPlay conflict)
- ✅ Auto-starts motion extraction using camera 0
- ✅ Immediately responds to API requests
- ✅ WebSocket broadcasts data at ~23-30 FPS
- ✅ Detects hands, face, chest ROIs
- ✅ Tracks motion intensity and frequency

### Dashboard Behavior:
- ✅ Connects to WebSocket automatically
- ✅ Shows "CONNECTED" status
- ✅ Displays ROI boxes (hands, face, chest)
- ✅ Renders motion trails
- ✅ Shows BPM estimates
- ✅ Detects tremor frequency
- ✅ Updates in real-time

## 📊 Example API Responses

### GET /api/status
```json
{
  "status": "running",
  "camera": 0,
  "stats": {
    "algorithm": "frame_diff",
    "fps": 23.3,
    "frame_count": 150,
    "uptime": 6.5,
    "frequency_analyzer": {
      "ready": true,
      "buffer_fill_pct": 0.85
    }
  }
}
```

### GET /api/heartbeat
```json
{
  "detected": true,
  "bpm": 72,
  "frequency_hz": 1.2,
  "confidence": 0.65,
  "ready": true,
  "buffer_fill": 1.0
}
```

### GET /api/roi
```json
{
  "rois": {
    "hands": [
      {
        "label": "left",
        "center": {"x": 357, "y": 378},
        "bbox": {"x": 313, "y": 333, "w": 102, "h": 86},
        "confidence": 0.99
      }
    ],
    "face": {
      "center": {"x": 415, "y": 213},
      "confidence": 0.52
    },
    "chest": {
      "center": {"x": 410, "y": 287},
      "confidence": 0.93
    }
  },
  "motion_analysis": {
    "chest": {
      "heartbeat": {
        "detected": true,
        "bpm": 68,
        "confidence": 0.72
      }
    },
    "left_hand": {
      "tremor": {
        "detected": false,
        "frequency_hz": null
      }
    }
  }
}
```

## 🐛 Troubleshooting

### Port still in use?
```bash
# Check what's using port 5001
lsof -i :5001

# Kill it
lsof -ti:5001 | xargs kill -9
```

### Camera not working?
```bash
# Check available cameras (macOS)
system_profiler SPCameraDataType

# Try different camera index
python3 src/atlas_api.py --camera 1
```

### Dashboard not connecting?
1. Check server is running: `curl http://localhost:5001/api/status`
2. Check browser console for errors (F12)
3. Verify WebSocket port matches in dashboard HTML
4. Try opening test_websocket.html first

### No motion detected?
- Ensure camera is not blocked
- Try moving in front of camera
- Check lighting conditions
- Verify camera feed is working (check logs)

## 📝 Files Created/Modified

### Modified:
- `src/atlas_api.py` - Fixed port, auto-start, host binding, JSON serialization
- `examples/motion_trails_dashboard.html` - Updated port to 5001

### Created:
- `start_atlas_eyes.sh` - Auto-start script with options
- `test_api_simple.sh` - Simple endpoint tester (no Python deps)
- `test_api.py` - Full test suite (requires requests, socketio)
- `test_websocket.html` - WebSocket connection tester
- `FIXED_README.md` - This file

## 🎯 Next Steps

1. **Start the server:**
   ```bash
   ./start_atlas_eyes.sh
   ```

2. **Run tests:**
   ```bash
   ./test_api_simple.sh
   ```

3. **Open dashboard:**
   ```bash
   open examples/motion_trails_dashboard.html
   ```

4. **Verify everything works:**
   - See "CONNECTED" in dashboard
   - See ROI boxes on video
   - See motion trails
   - See BPM updates

## 🔥 READY TO GO!

The Atlas Eyes API server is now fully functional and ready for Orion to use. All endpoints work, WebSocket streams data in real-time, and the dashboard can connect and visualize everything.

**To get started right now:**
```bash
cd ~/clawd/atlas-eyes && ./start_atlas_eyes.sh --dashboard
```

This will:
1. Start the API server on port 5001
2. Auto-start motion extraction
3. Open the motion trails dashboard in your browser
4. Start streaming live camera data with motion analysis

**Enjoy! 🎉**
