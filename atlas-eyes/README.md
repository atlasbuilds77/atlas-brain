# Atlas Eyes - Motion Extraction Perception System

A real-time camera-based motion extraction system for AI visual perception.

## Features
- **Multi-algorithm motion detection**: Frame differencing, Lucas-Kanade optical flow, MOG2 background subtraction
- **Real-time processing**: Target 30fps on standard hardware
- **Frequency analysis**: Detect heartbeat (1-2Hz), tremor (4Hz), structural vibrations
- **JSON API**: Query motion data programmatically
- **Comprehensive testing**: Synthetic patterns, real-world validation, performance benchmarks

## Quick Start

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd atlas-eyes

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage
```bash
# Run with webcam (default)
python examples/demo.py

# Run with video file
python examples/demo.py --input data/sample_video.mp4

# Run specific algorithm
python examples/demo.py --algorithm optical_flow
```

### API Usage
```python
from src.motion_extractor import MotionExtractor

# Initialize with webcam
extractor = MotionExtractor(source=0, algorithm='frame_diff')

# Process frames
while True:
    motion_data = extractor.process_frame()
    print(f"Motion intensity: {motion_data['intensity']}")
    print(f"Motion vectors: {motion_data['vectors']}")
```

## Algorithms

### 1. Frame Differencing
- Simple difference between consecutive frames
- Fast, low computational cost
- Good for general motion detection

### 2. Lucas-Kanade Optical Flow
- Dense optical flow using sparse features
- Provides motion vectors with direction
- Good for detailed motion analysis

### 3. MOG2 Background Subtraction
- Gaussian mixture model for background subtraction
- Robust to lighting changes
- Good for foreground object detection

## Testing

Run the test suite:
```bash
python -m pytest tests/ -v
```

Performance benchmarks:
```bash
python tests/benchmark.py
```

## Directory Structure
```
atlas-eyes/
├── src/                    # Core motion extraction code
├── tests/                  # Test suite and benchmarks
├── docs/                   # Documentation
├── examples/               # Demo scripts
├── data/                   # Sample videos for testing
└── requirements.txt        # Python dependencies
```

## Requirements
- Python 3.8+
- OpenCV 4.5+
- NumPy 1.20+
- FFmpeg (for video file support)

## Performance Targets
- **Frame Rate**: 30 FPS minimum
- **Latency**: < 100ms end-to-end
- **Accuracy**: > 90% motion detection rate
- **Memory**: < 500MB peak usage

## Limitations
- Requires adequate lighting for reliable detection
- Camera motion can interfere with motion extraction
- Performance depends on hardware capabilities
- Not suitable for extremely fast motion (> 60Hz)

## License
MIT License

## Contributing
Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.