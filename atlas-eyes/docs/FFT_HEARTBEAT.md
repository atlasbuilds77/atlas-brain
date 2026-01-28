# FFT-Based Heartbeat Detection

This document describes the FFT (Fast Fourier Transform) based heartbeat detection system implemented in Atlas Eyes.

## Overview

Atlas Eyes can now detect heartbeat frequencies from video by analyzing periodic motion in the 1-2 Hz range (60-120 BPM). This is achieved through:

1. **Motion intensity extraction** - Frame differencing, optical flow, or background subtraction
2. **Time series analysis** - Rolling window of motion intensities over time
3. **FFT analysis** - Convert time domain to frequency domain
4. **Peak detection** - Find dominant frequencies in heartbeat range

## Architecture

### Components

```
┌─────────────────────┐
│  MotionExtractor    │  Extracts motion intensity from video frames
└──────────┬──────────┘
           │ intensity samples
           ↓
┌─────────────────────┐
│ FrequencyAnalyzer   │  Performs FFT analysis on time series
└──────────┬──────────┘
           │ frequency peaks
           ↓
┌─────────────────────┐
│   AtlasEyesAPI     │  Exposes heartbeat data via REST API
└─────────────────────┘
```

### Files

- **`src/frequency_analyzer.py`** - Core FFT analysis module
- **`src/motion_extractor.py`** - Motion extraction with frequency integration
- **`src/atlas_api.py`** - REST API endpoints
- **`tests/test_fft_heartbeat.py`** - Test suite with synthetic and live tests

## Algorithm

### 1. Data Collection

- **Rolling buffer**: Stores 5-10 seconds of motion intensity samples (150-300 frames at 30fps)
- **Sampling rate**: Matches camera FPS (typically 30 Hz)
- **Data structure**: `collections.deque` for efficient FIFO buffer

### 2. FFT Processing

```python
# Apply Hamming window to reduce spectral leakage
window = np.hamming(len(signal))
windowed_signal = signal * window

# Compute FFT
fft_vals = fftpack.fft(windowed_signal)
fft_freq = fftpack.fftfreq(len(signal), 1.0 / sample_rate)

# Extract positive frequencies only
frequencies = fft_freq[fft_freq > 0]
amplitudes = np.abs(fft_vals[fft_freq > 0])
```

### 3. Peak Detection

- **Frequency range**: 1.0 - 2.0 Hz (60-120 BPM)
- **Peak finding**: `scipy.signal.find_peaks` with prominence threshold
- **Confidence metric**: `peak_amplitude / mean_amplitude`
- **Threshold**: Confidence ≥ 1.5 for positive detection

### 4. BPM Calculation

```python
bpm = dominant_frequency_hz * 60
```

## API Endpoints

### GET /api/heartbeat

Detect heartbeat from current motion data.

**Response:**
```json
{
  "detected": true,
  "bpm": 75.2,
  "frequency_hz": 1.253,
  "confidence": 3.45,
  "ready": true,
  "buffer_fill": 1.0
}
```

**Fields:**
- `detected` - Whether heartbeat was detected (confidence ≥ threshold)
- `bpm` - Beats per minute
- `frequency_hz` - Frequency in Hz
- `confidence` - Peak amplitude / mean amplitude ratio
- `ready` - Whether enough data has been collected
- `buffer_fill` - Buffer fill percentage (0-1)

### GET /api/frequency

Get full frequency spectrum for visualization.

**Response:**
```json
{
  "frequencies": [0.1, 0.2, 0.3, ...],
  "amplitudes": [0.5, 1.2, 0.8, ...],
  "ready": true,
  "sample_count": 300,
  "window_size": 300
}
```

### GET /api/tremor

Detect tremor in 3-6 Hz range (Parkinson's characteristic).

**Response:**
```json
{
  "detected": false,
  "frequency_hz": null,
  "confidence": 0.0,
  "ready": true,
  "buffer_fill": 1.0
}
```

## Usage

### Command Line Test

```bash
# Test with synthetic signal (verifies FFT accuracy)
python3 tests/test_fft_heartbeat.py --synthetic

# Test with live webcam
python3 tests/test_fft_heartbeat.py --live
```

### Start API Server

```bash
cd ~/clawd/atlas-eyes/src
python3 atlas_api.py --port 5000
```

Then in another terminal:
```bash
# Start motion extraction
curl -X POST http://127.0.0.1:5000/api/start \
  -H "Content-Type: application/json" \
  -d '{"algorithm": "frame_diff"}'

# Wait 10 seconds, then check heartbeat
curl http://127.0.0.1:5000/api/heartbeat
```

### Python Integration

```python
from motion_extractor import MotionExtractor

extractor = MotionExtractor(source=0, algorithm='frame_diff', fps=30)

while True:
    data = extractor.process_frame()
    
    # Check heartbeat
    heartbeat = extractor.detect_heartbeat()
    if heartbeat and heartbeat['detected']:
        print(f"Heartbeat: {heartbeat['bpm']:.1f} BPM")
```

## Performance

### Accuracy

- **Target**: ±5 BPM
- **Synthetic signal test**: 3 BPM error (within target)
- **Real-world**: Varies based on:
  - Hand stability
  - Lighting conditions
  - Skin tone (affects visibility of blood flow)
  - Camera quality

### Computational Cost

- **FFT**: O(n log n) where n = window_size
- **Typical**: ~1-2ms per FFT on modern hardware
- **Caching**: Results cached for 500ms to reduce redundant computation

### Requirements

- **Minimum data**: 33% of window size (~100 frames / 3 seconds)
- **Optimal data**: Full window (300 frames / 10 seconds)
- **Update rate**: Every 500ms (configurable via cache duration)

## Tips for Best Results

### Hand Position
- Place palm facing camera
- Fill ~30% of frame
- Keep hand relatively still (small involuntary movements are OK)
- Good lighting helps

### Camera Settings
- 30 FPS minimum (60 FPS better)
- Good focus
- Stable lighting
- Avoid auto-exposure if possible

### Algorithm Choice
- **`frame_diff`**: Fast, good for general use
- **`optical_flow`**: More detailed motion vectors
- **`background_sub`**: Best for noisy environments

## Troubleshooting

### "No heartbeat detected"
- Ensure hand is visible and in focus
- Check motion intensity is > 0.001
- Wait for full 10 second buffer
- Try different hand positions
- Increase lighting

### Low confidence
- Reduce hand movement
- Improve lighting
- Ensure camera is stable
- Check for motion artifacts (fan, shadows)

### Incorrect BPM
- Verify hand is clearly visible
- Check for aliasing (motion too fast/slow for frame rate)
- Ensure buffer is full
- Try different algorithm

## Technical Details

### Hamming Window

Applied to reduce spectral leakage from FFT edge effects:
```python
window = np.hamming(n)
w(n) = 0.54 - 0.46 * cos(2π * n / (N-1))
```

### Confidence Metric

```python
confidence = peak_amplitude / mean_amplitude
```

Higher confidence indicates:
- Stronger periodic signal
- Better signal-to-noise ratio
- More reliable detection

Typical values:
- `< 1.5`: Noise or no heartbeat
- `1.5 - 3.0`: Moderate confidence
- `> 3.0`: High confidence

### Buffer Management

```python
# Efficient circular buffer
from collections import deque
buffer = deque(maxlen=300)  # Auto-drops oldest
```

## Future Enhancements

- [ ] Multi-person detection with face tracking
- [ ] Adaptive confidence thresholding
- [ ] Heart rate variability (HRV) analysis
- [ ] Real-time spectrum visualization
- [ ] GPU acceleration for large windows
- [ ] Mobile device support

## References

- [Photoplethysmography (PPG)](https://en.wikipedia.org/wiki/Photoplethysmogram)
- [FFT for Signal Processing](https://en.wikipedia.org/wiki/Fast_Fourier_transform)
- [Window Functions](https://en.wikipedia.org/wiki/Window_function)
