# Dashboard Comparison

## live_dashboard.html vs motion_trails_dashboard.html

### Visual Aesthetic

| Feature | live_dashboard.html | motion_trails_dashboard.html |
|---------|-------------------|---------------------------|
| **Theme** | Consumer app (gradients, blur) | Scientific/technical (stark, clean) |
| **Background** | Gradient (#0a0e27 → #1a1b3c) | Pure black (#000000) |
| **Layout** | 3-column grid | Split-screen (60/40) |
| **Font** | System sans-serif | Monaco monospace |
| **Glass effects** | Heavy blur, transparency | None - solid colors |
| **Color palette** | Purple/blue gradients | Cyan/green/orange technical |

### Key Differences

#### live_dashboard.html (Original)
```
✅ Consumer-friendly UI
✅ Chart.js visualizations
✅ Anime.js animations
✅ Glass morphism design
✅ Centered metric cards
✅ Heart icon animation
❌ No motion trails
❌ Limited data overlays
❌ Single video view
```

#### motion_trails_dashboard.html (NEW)
```
✅ Scientific motion capture aesthetic
✅ Pure canvas rendering (60 FPS)
✅ Motion trail system with fade
✅ Split-screen video + trails
✅ Real-time data annotations
✅ Grid/crosshair overlays
✅ Frequency spectrum visualization
✅ Per-ROI trail tracking
✅ Monospace technical typography
❌ No Chart.js (pure canvas)
❌ No glass effects
```

### Layout Comparison

#### live_dashboard.html
```
┌─────────────────────────────────────────┐
│ Header                                   │
├──────────────┬──────────┬───────────────┤
│              │          │               │
│   Video      │  Heart   │    Tremor     │
│   Feed       │  Monitor │   Indicator   │
│   (Large)    │  (BPM)   │   (Status)    │
│              │          │               │
├──────────────┴──────────┴───────────────┤
│  Waveform  │  Spectrum  │   Metrics    │
└─────────────┴────────────┴──────────────┘
```

#### motion_trails_dashboard.html
```
┌─────────────────────────────────────────┐
│ HEADER - System Status                  │
├───────────────────────┬─────────────────┤
│                       │                 │
│   VIDEO FEED          │  MOTION TRAILS  │
│   (60%)               │  (40%)          │
│                       │                 │
│   • ROI boxes         │  • Black bg     │
│   • Live camera       │  • Trails       │
│                       │  • Grid         │
│                       │  • Spectrum     │
├───────────────────────┴─────────────────┤
│  BPM │ Intensity │ Tremor │ Conf │ ROIs│
└─────────────────────────────────────────┘
```

### Color Palette Comparison

#### live_dashboard.html
```css
Primary gradient:   #667eea → #764ba2 (purple)
Background:         #0a0e27 → #1a1b3c (dark blue gradient)
Success:            #10b981 (green)
Danger:             #ef4444 (red)
Warning:            #f59e0b (amber)
Glass effects:      rgba(255,255,255,0.05) + blur
```

#### motion_trails_dashboard.html
```css
Background:         #000000 (pure black)
Cyan trails:        #00ffff (hands)
Light cyan:         #00d4ff (chest/heartbeat)
Bright green:       #00ff88 (face, grid)
Orange:             #ff6600 (tremor warning)
Red:                #ff0000 (tremor danger)
White:              #ffffff (text)
Gray:               #cccccc (coordinates)
Subtle elements:    rgba(0,255,136,0.08) (grid)
```

### Motion Trail Features (NEW)

```javascript
// Trail configuration
TRAIL_LENGTH: 150 points (5 seconds @ 30fps)
TRAIL_FADE_TIME: 5000ms
Fade algorithm: opacity = 1 - (age / maxAge)

// Trail colors by ROI
left_hand:  rgba(0, 255, 255, opacity)  // Cyan
right_hand: rgba(0, 255, 255, opacity)  // Cyan
face:       rgba(0, 255, 136, opacity)  // Green
chest:      rgba(0, 212, 255, opacity)  // Light cyan
```

### Data Visualization

#### live_dashboard.html
- Chart.js line chart (waveform)
- Chart.js bar chart (spectrum)
- Large BPM number display
- Confidence bar progress
- Metric cards

#### motion_trails_dashboard.html
- Canvas-based motion trails
- Real-time position tracking
- Data annotations on trails
- Frequency spectrum bars (subtle)
- Grid reference overlay
- Coordinate displays

### Performance

| Metric | live_dashboard.html | motion_trails_dashboard.html |
|--------|-------------------|---------------------------|
| **Rendering** | Chart.js (lower FPS) | Pure canvas (60 FPS) |
| **Animation** | Anime.js tweens | requestAnimationFrame |
| **Updates** | Chart updates | Direct canvas draw |
| **Trail tracking** | ❌ None | ✅ 150 points × 4 ROIs |
| **Polling rate** | WebSocket only | WebSocket + 10Hz REST |

### Use Cases

#### live_dashboard.html - Best for:
- Consumer demonstrations
- Simple monitoring
- Single-screen overview
- Chart-based analysis
- Less technical audiences

#### motion_trails_dashboard.html - Best for:
- Scientific analysis
- Motion capture work
- Detailed ROI tracking
- Medical/research applications
- Technical audiences
- When you need to see motion history

### API Usage

#### Both use:
```javascript
// WebSocket for real-time data
socket.on('data', {
  motion_intensity,
  bpm,
  tremor_freq,
  confidence,
  fps,
  frequency_spectrum
})
```

#### motion_trails_dashboard.html additionally:
```javascript
// REST API polling for ROI data (10Hz)
GET /api/roi → {
  rois: { hands, face, chest },
  roi_motion: { tremor, heartbeat }
}
```

### Inspiration

#### live_dashboard.html
- Apple Health
- Fitness apps
- Consumer monitoring tools
- Modern web dashboards

#### motion_trails_dashboard.html
- Motion capture software (e.g., Vicon)
- Medical imaging displays
- Scientific visualization tools
- Professional analysis software
- **Reference**: Hummingbird motion trail example

### Quick Start

#### live_dashboard.html
```bash
# Start server
python src/atlas_api.py --port 5000

# Open dashboard
open examples/live_dashboard.html
```

#### motion_trails_dashboard.html
```bash
# Quick start script
./examples/start_motion_trails.sh

# Or manual:
python src/atlas_api.py --port 5000
curl -X POST http://localhost:5000/api/start
open examples/motion_trails_dashboard.html
```

### Migration Path

If you want to enhance live_dashboard.html with motion trails:

1. Add canvas element for trails
2. Implement trail buffer system
3. Add ROI polling
4. Render trails with fade algorithm
5. Overlay on existing video feed

Or keep both and switch based on use case! 🎯
