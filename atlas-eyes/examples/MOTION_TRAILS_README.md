# Atlas Eyes - Motion Trails Dashboard

Professional motion capture visualization with scientific aesthetic inspired by motion analysis software.

## 🎯 Features

### Split-Screen Layout
- **LEFT (60%)**: Video feed with ROI boxes (hands, face, chest)
- **RIGHT (40%)**: Pure black canvas with motion trails

### Motion Trail System
- **Cyan trails** (#00ffff): Left & right hand tracking
- **Light cyan trails** (#00d4ff): Chest movement (heartbeat detection zone)
- **Green trails** (#00ff88): Face tracking
- **Trail duration**: 5 seconds with smooth opacity fade
- **60 FPS** rendering with requestAnimationFrame

### Scientific Visualizations
- **Motion trails**: Colored paths showing movement history
- **Fading algorithm**: `opacity = 1 - (age / maxAge)`
- **Frequency spectrum**: Vertical bars at bottom (subtle, 30% opacity)
  - Cyan bars (1-2 Hz): Heartbeat range
  - Orange bars (3.5-4.5 Hz): Tremor range
  - Green bars: Other frequencies
- **Grid overlay**: Subtle reference lines (#00ff88 at 8% opacity)
- **Crosshair**: Center reference markers

### Real-time Data Annotations
- **BPM display**: Near chest trail
- **Tremor frequency**: Near hand trails (when detected)
- **Coordinates**: (x, y) position in normalized space
- **Confidence**: Per-ROI tracking confidence

### Alert System
- **Tremor detection**: Orange alert overlay when 4Hz detected
- **Visual feedback**: Pulsing animation on alert
- **Color coding**: 
  - Green: Normal
  - Orange (#ff6600): Warning
  - Red (#ff0000): Danger

## 🚀 Usage

### 1. Start Atlas Eyes Server

```bash
cd ~/clawd/atlas-eyes
python src/atlas_api.py --camera 0 --port 5000
```

### 2. Start Camera Feed

```bash
# POST to start extraction
curl -X POST http://localhost:5000/api/start \
  -H "Content-Type: application/json" \
  -d '{"algorithm": "frame_diff"}'
```

### 3. Open Dashboard

```bash
# Open in browser
open examples/motion_trails_dashboard.html
```

Or navigate to:
```
file:///Users/atlasbuilds/clawd/atlas-eyes/examples/motion_trails_dashboard.html
```

## 🎨 Visual Design

### Color Palette
```
Background:       #000000 (Pure black)
Cyan trails:      #00ffff (Hands)
Light cyan:       #00d4ff (Chest/heartbeat)
Bright green:     #00ff88 (Face, grid, borders)
Orange warning:   #ff6600 (Tremor alerts)
Red danger:       #ff0000 (Critical tremor)
White text:       #ffffff (Labels)
Gray text:        #cccccc (Coordinates)
Dark gray:        #666666 (Inactive/subtle)
```

### Typography
- **Font**: Monaco, Courier New (monospace)
- **System title**: 18px, uppercase, 3px letter-spacing
- **Stats**: 20px bold for values
- **Labels**: 9-10px uppercase, 1.5-2px letter-spacing

### Layout Grid
```
┌──────────────────────────────────────────────────┐
│ HEADER (60px)                                     │
│ Status │ FPS │ Uptime                            │
├───────────────────────────┬──────────────────────┤
│ VIDEO FEED (60%)          │ MOTION TRAILS (40%)  │
│                           │                      │
│ • ROI boxes (green)       │ • Pure black bg      │
│ • Video stream            │ • Colored trails     │
│ • Detection overlay       │ • Data annotations   │
│                           │ • Frequency spectrum │
│                           │ • Grid overlay       │
├───────────────────────────┴──────────────────────┤
│ STATS BAR (80px)                                 │
│ BPM │ Intensity │ Tremor │ Confidence │ ROIs    │
└──────────────────────────────────────────────────┘
```

## 📊 Data Sources

### WebSocket Events
```javascript
// Main data stream (Socket.IO)
socket.on('data', {
  timestamp: 1234567890,
  motion_intensity: 0.45,
  bpm: 72,
  tremor_freq: null,
  confidence: 0.87,
  fps: 30.0,
  frequency_spectrum: [0.1, 0.2, ...], // 20 values
  motion_detected: true
})
```

### REST API Polling
```javascript
// ROI data (HTTP GET every 100ms)
GET /api/roi
{
  rois: {
    hands: [
      {label: 'left_hand', x: 0.3, y: 0.5, width: 0.1, height: 0.15},
      {label: 'right_hand', x: 0.7, y: 0.5, width: 0.1, height: 0.15}
    ],
    face: {x: 0.5, y: 0.3, width: 0.2, height: 0.25},
    chest: {x: 0.5, y: 0.6, width: 0.3, height: 0.2}
  },
  roi_motion: {
    left_hand: {
      tremor: {detected: false, frequency_hz: null, confidence: 0}
    },
    chest: {
      heartbeat: {detected: true, bpm: 72, confidence: 0.8}
    }
  }
}
```

## 🔧 Configuration

Edit `CONFIG` object in the HTML file:

```javascript
const CONFIG = {
  WS_URL: 'http://localhost:5000',
  TRAIL_LENGTH: 150,        // Max points (5 sec @ 30fps)
  TRAIL_FADE_TIME: 5000,    // Fade duration (ms)
  GRID_SIZE: 20,            // Grid spacing (px)
  MAX_FPS: 60               // Render rate limit
};
```

## 🐛 Troubleshooting

### No motion trails appearing
- Check ROI detection is working (see left panel for ROI boxes)
- Verify `/api/roi` endpoint returns valid data
- Check browser console for errors

### Trails are choppy
- Lower `MAX_FPS` if system is overloaded
- Reduce `TRAIL_LENGTH` for better performance

### Connection issues
- Verify server is running: `curl http://localhost:5000/api/status`
- Check CORS settings if accessing from file://
- Ensure camera extraction is started: `POST /api/start`

### No video feed
- This implementation shows ROI boxes only (no raw video)
- To add video: implement WebRTC or MJPEG stream from server
- Video canvas is ready for video element overlay

## 📈 Performance

- **Target**: 60 FPS rendering
- **Network**: 10 Hz ROI polling + real-time WebSocket
- **Memory**: ~150 trail points × 4 ROIs = 600 points max
- **Canvas**: Hardware-accelerated 2D rendering

## 🎯 Future Enhancements

- [ ] Add particle effects at motion hotspots
- [ ] Wireframe skeleton overlay (connect hand-face-chest)
- [ ] Motion intensity heat map
- [ ] Trail color variation based on speed/acceleration
- [ ] Export trail data to JSON/CSV
- [ ] Screenshot capture with timestamp
- [ ] Video feed integration (WebRTC/MJPEG)
- [ ] 3D depth visualization (if depth camera available)

## 📝 Notes

This dashboard prioritizes:
1. **Scientific aesthetic**: Clean, technical, professional
2. **Real-time performance**: 60 FPS with minimal latency
3. **Data visibility**: All relevant metrics at a glance
4. **Motion visualization**: Clear trails showing movement history

NOT a consumer app - this is a tool for analysis and monitoring.
