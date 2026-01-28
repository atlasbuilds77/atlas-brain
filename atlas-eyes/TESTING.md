# Atlas Eyes - Testing Guide

## Quick Start (30 seconds)

```bash
cd /Users/atlasbuilds/clawd/atlas-eyes

# Install dependencies
pip3 install -r requirements.txt

# Run basic demo
python3 examples/demo.py
```

Press **'q'** to quit when done.

---

## Test 1: Basic Motion Detection (2 minutes)

**Goal:** Verify motion detection works

```bash
python3 examples/demo.py --algorithm frame_diff
```

**Actions:**
1. Camera window should open showing your webcam
2. Wave your hand in front of camera
3. You should see motion highlighted in the right panel
4. Check terminal for stats (FPS, motion intensity)

**Success criteria:**
- ✅ FPS > 20
- ✅ Motion detected when you move
- ✅ No motion when still

---

## Test 2: Heartbeat Detection (5 minutes)

**Goal:** Detect your pulse from video

```bash
python3 tests/test_heartbeat.py --duration 30
```

**Instructions:**
1. Rest your hand palm-down on desk
2. Point camera at your hand/fingers
3. Stay completely still for 30 seconds
4. Script will analyze and show estimated BPM

**Success criteria:**
- ✅ Estimated BPM between 60-100 (resting heart rate)
- ✅ Within ±10 BPM of actual heart rate (check with Apple Watch/pulse)
- ✅ Signal-to-noise ratio > 1.5

**Tips for better results:**
- Good lighting (no shadows on hand)
- Camera close to hand (fill frame)
- Warm hands (cold = less blood flow = weaker signal)
- Focus on fingertips (strongest pulse)

---

## Test 3: Algorithm Comparison (3 minutes)

**Goal:** Compare different motion extraction algorithms

### Frame Differencing (fastest)
```bash
python3 examples/demo.py --algorithm frame_diff
```
- Simple, fast, general purpose
- Good for large motions

### Optical Flow (most detailed)
```bash
python3 examples/demo.py --algorithm optical_flow
```
- Tracks individual features
- Shows motion vectors with arrows
- Best for subtle motion

### Background Subtraction (most robust)
```bash
python3 examples/demo.py --algorithm background_sub
```
- Handles lighting changes
- Good for foreground detection
- Slower to initialize

**Try:**
- Wave hand slowly → optical flow shows detailed vectors
- Turn lights on/off → background_sub adapts
- Quick movements → frame_diff is fastest

---

## Test 4: API Mode (Atlas Integration)

**Goal:** Run as API server for Atlas to query

### Terminal 1: Start API server
```bash
python3 src/atlas_api.py --port 5000
```

### Terminal 2: Test API
```bash
# Start extraction
curl -X POST http://localhost:5000/api/start

# Get motion data
curl http://localhost:5000/api/motion

# Check heartbeat
curl http://localhost:5000/api/heartbeat

# Get status
curl http://localhost:5000/api/status

# Stop extraction
curl -X POST http://localhost:5000/api/stop
```

**Success criteria:**
- ✅ API responds on port 5000
- ✅ Motion data updates in real-time
- ✅ JSON format is valid

---

## Test 5: Video File Processing

**Goal:** Process pre-recorded video

```bash
# Record a test video first (30 seconds)
python3 examples/demo.py --save-json motion_log.json

# Process the video file
python3 examples/demo.py --input /path/to/video.mp4
```

**Use cases:**
- Analyze saved footage
- Batch processing
- Offline analysis

---

## Test 6: Multi-Algorithm Switch (Live)

**Goal:** Switch algorithms on the fly

```bash
python3 examples/demo.py
```

**While running:**
- Press **'a'** to cycle through algorithms
- Press **'s'** to save screenshot
- Press **'q'** to quit

**Watch how each algorithm handles:**
- Slow motion (optical flow wins)
- Fast motion (frame diff wins)
- Lighting changes (background sub wins)

---

## Test 7: Performance Benchmark

**Goal:** Measure FPS and latency

```bash
python3 examples/demo.py --no-display --save-json benchmark.json
```

**Let run for 60 seconds, then check:**
```bash
# Check average FPS from log
cat benchmark.json | grep fps
```

**Target metrics:**
- **FPS:** > 25 (real-time)
- **Latency:** < 100ms
- **CPU:** < 50% single core

---

## Test 8: Edge Cases

### Test 8a: Poor Lighting
- Turn off lights → motion still detectable?
- Direct sunlight → handles exposure changes?

### Test 8b: Camera Motion
- Handheld camera → false motion detected?
- Pan camera → algorithm adapts?

### Test 8c: Complex Scenes
- Multiple people moving → tracks all?
- Busy background → filters noise?

---

## Troubleshooting

### "Camera not found"
- Check camera index: `ls /dev/video*` (Linux) or System Preferences (Mac)
- Try different index: `--input 1`

### "Low FPS (< 10)"
- Reduce resolution: `--width 320 --height 240`
- Use simpler algorithm: `--algorithm frame_diff`

### "Heartbeat detection fails"
- Ensure good lighting
- Keep hand very still (use tripod for camera)
- Try 60-second recording: `--duration 60`
- Warm up hands first (run under warm water)

### "Import errors"
- Reinstall dependencies: `pip3 install -r requirements.txt --force-reinstall`
- Check Python version: `python3 --version` (need 3.8+)

---

## Expected Results Summary

| Test | Time | Success Criteria |
|------|------|------------------|
| Basic Motion | 2 min | FPS > 20, motion detected |
| Heartbeat | 5 min | BPM ±10 of actual |
| Algorithms | 3 min | All 3 run without errors |
| API Mode | 2 min | API responds, JSON valid |
| Video File | 2 min | Processes saved video |
| Multi-Switch | 2 min | Algorithms switch live |
| Benchmark | 3 min | FPS > 25 sustained |
| Edge Cases | 5 min | Graceful degradation |

**Total test time:** ~25 minutes for complete validation

---

## Next Steps After Testing

1. **Integrate with Atlas:**
   - Start API server on boot
   - Atlas queries `/api/motion` for visual perception
   - Set up alerts for specific patterns

2. **Improve Algorithms:**
   - Implement full FFT for heartbeat/tremor
   - Add ML-based pattern recognition
   - Optimize for real-time performance

3. **Add Features:**
   - Multi-camera support
   - Cloud storage for motion logs
   - Mobile app for remote monitoring

4. **Deploy:**
   - Set up as systemd service (Linux)
   - Configure auto-start on Mac (launchd)
   - Add web dashboard for visualization

---

## Contact

Questions? Issues? Ideas?

Drop them in `/Users/atlasbuilds/clawd/memory/projects/atlas-eyes-feedback.md`

---

*Atlas Eyes - Giving Atlas vision through motion* 👁️⚡
