# Motion Trails Dashboard - Quick Start

## ⚡ 30-Second Start

```bash
cd ~/clawd/atlas-eyes/examples
./start_motion_trails.sh
```

Done! Dashboard opens automatically.

---

## 🔧 Manual Start (3 steps)

### 1. Start Server
```bash
cd ~/clawd/atlas-eyes
python src/atlas_api.py --camera 0 --port 5000
```

### 2. Start Extraction
```bash
curl -X POST http://localhost:5000/api/start \
  -H "Content-Type: application/json" \
  -d '{"algorithm": "frame_diff"}'
```

### 3. Open Dashboard
```bash
open examples/motion_trails_dashboard.html
```

---

## 📊 What You'll See

```
┌─────────────────────────────────────────┐
│ ⚡ ATLAS EYES - MOTION CAPTURE          │
├──────────────────────┬──────────────────┤
│ VIDEO FEED (ROIs)    │ MOTION TRAILS    │
│ • Green boxes        │ • Black bg       │
│ • Hand/face/chest    │ • Cyan trails    │
│                      │ • Data overlays  │
├──────────────────────┴──────────────────┤
│ BPM │ INTENSITY │ TREMOR │ CONFIDENCE  │
└─────────────────────────────────────────┘
```

---

## 🎨 Key Features

- **Cyan trails** (#00ffff) → Hands
- **Green trails** (#00ff88) → Face  
- **Light cyan** (#00d4ff) → Chest/heartbeat
- **5-second fade** → Motion history
- **60 FPS** → Smooth rendering
- **Real-time** → Live data overlays

---

## 🐛 Troubleshooting

**No motion trails?**
```bash
# Check ROI detection
curl http://localhost:5000/api/roi | python3 -m json.tool
```

**Connection failed?**
```bash
# Verify server
curl http://localhost:5000/api/status
```

**Server not running?**
```bash
# Start it
python src/atlas_api.py --camera 0 --port 5000
```

---

## 📚 Full Docs

- `MOTION_TRAILS_README.md` - Complete documentation
- `DASHBOARD_COMPARISON.md` - vs old dashboard
- `IMPLEMENTATION_SUMMARY.md` - Technical details

---

## 🎯 Next Steps

1. ✅ Start dashboard (see above)
2. 🎥 Position yourself in camera view
3. ✋ Move hands to see cyan trails
4. 👀 Move face to see green trail
5. 💓 Stay still for heartbeat detection
6. 📊 Monitor BPM and tremor alerts

**Enjoy your motion capture experience!** 🚀
