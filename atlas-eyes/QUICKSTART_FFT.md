# FFT Heartbeat Detection - Quick Start

Get Atlas Eyes detecting heartbeats in 2 minutes.

## Install Dependencies

```bash
cd ~/clawd/atlas-eyes
pip3 install numpy scipy opencv-python flask
```

## Quick Test (Synthetic Signal)

Verify FFT implementation works correctly:

```bash
python3 tests/test_fft_heartbeat.py --synthetic
```

Expected output:
```
✅ PASS (within ±5 BPM)
```

## Live Webcam Test

Test with real camera (place hand in view):

```bash
python3 tests/test_fft_heartbeat.py --live
```

Instructions:
1. Place palm facing camera
2. Keep hand still
3. Wait 10 seconds
4. Look for green heart indicator
5. Press 'q' to quit

## API Server

### Start Server

```bash
cd src
python3 atlas_api.py
```

### Test Endpoints

In another terminal:

```bash
# Start motion extraction
curl -X POST http://127.0.0.1:5000/api/start

# Wait 10 seconds, then check heartbeat
curl http://127.0.0.1:5000/api/heartbeat

# Get frequency spectrum
curl http://127.0.0.1:5000/api/frequency
```

### API Test Script

```bash
python3 tests/test_api_heartbeat.py
```

## Integration Example

```python
from motion_extractor import MotionExtractor
import time

# Initialize
extractor = MotionExtractor(source=0, fps=30)

print("Collecting data for 10 seconds...")
for _ in range(300):  # 10 seconds at 30fps
    data = extractor.process_frame()
    time.sleep(1/30)

# Check heartbeat
result = extractor.detect_heartbeat()
if result and result['detected']:
    print(f"❤️ Heartbeat: {result['bpm']:.1f} BPM")
    print(f"   Confidence: {result['confidence']:.2f}")
else:
    print("No heartbeat detected")

extractor.release()
```

## Expected Results

### Synthetic Test
- **Target**: 75 BPM
- **Detected**: 75-80 BPM
- **Error**: < 5 BPM ✅

### Live Test (Hand)
- **Range**: 60-100 BPM (typical resting)
- **Confidence**: 2.0-4.0
- **Time to detection**: 10 seconds

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Import errors | `pip3 install numpy scipy opencv-python` |
| No camera | Check camera index (try 0, 1, 2) |
| Low confidence | Better lighting, keep hand still |
| Wrong BPM | Ensure hand fills ~30% of frame |

## Files Created

```
atlas-eyes/
├── src/
│   ├── frequency_analyzer.py      ← New FFT module
│   ├── motion_extractor.py        ← Updated with FFT
│   └── atlas_api.py               ← Updated API
├── tests/
│   ├── test_fft_heartbeat.py     ← New test suite
│   └── test_api_heartbeat.py     ← New API test
└── docs/
    └── FFT_HEARTBEAT.md          ← Full documentation
```

## Next Steps

- Read full docs: `docs/FFT_HEARTBEAT.md`
- Adjust confidence threshold in `FrequencyAnalyzer.__init__`
- Customize window size for faster/slower response
- Add visualization with matplotlib
