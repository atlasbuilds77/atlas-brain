# ROI Tracker Usage Guide

## Quick Start

```python
from roi_tracker import ROITracker
import cv2

# Initialize tracker
tracker = ROITracker(
    detect_hands=True,
    detect_face=True,
    detect_chest=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    max_num_hands=2
)

# Process video frames
cap = cv2.VideoCapture(0)
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Get ROI detections
    result = tracker.process_frame(frame)
    
    # Access results
    for hand in result['hands']:
        bbox = hand['bbox']
        print(f"{hand['label']} hand at ({bbox['x']}, {bbox['y']})")
    
    if result['face']:
        print(f"Face detected: {result['face']['confidence']:.2f}")
    
    if result['chest']:
        print(f"Chest detected: {result['chest']['confidence']:.2f}")

# Clean up
tracker.release()
cap.release()
```

## Return Format

```python
{
    'hands': [
        {
            'type': 'hand',
            'label': 'left' | 'right',
            'hand_id': 0,  # 0 or 1
            'bbox': {'x': int, 'y': int, 'w': int, 'h': int},
            'center': {'x': int, 'y': int},
            'confidence': float,
            'landmarks': [
                {'x': float, 'y': float, 'z': float},
                # ... 21 hand landmarks
            ]
        }
    ],
    'face': {
        'type': 'face',
        'bbox': {'x': int, 'y': int, 'w': int, 'h': int},
        'center': {'x': int, 'y': int},
        'confidence': float
    } | None,
    'chest': {
        'type': 'chest',
        'bbox': {'x': int, 'y': int, 'w': int, 'h': int},
        'center': {'x': int, 'y': int},
        'confidence': float
    } | None,
    'frame_count': int,
    'frame_shape': (height, width)
}
```

## Visualization

```python
# Draw bounding boxes on frame
annotated = tracker.draw_rois(frame, result)
cv2.imshow('ROI Tracking', annotated)
```

## ROI Masks

```python
# Get binary mask for a specific ROI
if result['face']:
    face_mask = tracker.get_roi_mask(result['face'], (frame.shape[0], frame.shape[1]))
    # mask is 0/1 numpy array, same size as frame
```

## Context Manager

```python
# Automatic cleanup
with ROITracker() as tracker:
    result = tracker.process_frame(frame)
    # ... use result
# tracker.release() called automatically
```

## Configuration

### Model Path
By default, models are loaded from `../models/` relative to `roi_tracker.py`.
To specify a custom path:

```python
tracker = ROITracker(model_path='/custom/path/to/models')
```

### Selective Detection
Disable specific detectors to improve performance:

```python
# Only detect hands
tracker = ROITracker(
    detect_hands=True,
    detect_face=False,
    detect_chest=False
)
```

### Confidence Thresholds
Adjust sensitivity:

```python
tracker = ROITracker(
    min_detection_confidence=0.7,  # Higher = fewer false positives
    min_tracking_confidence=0.5    # Lower = more robust tracking
)
```

## Performance Tips

1. **Disable unused detectors** - Only enable what you need
2. **Adjust confidence thresholds** - Balance detection vs. performance
3. **Process every N frames** - Skip frames if real-time isn't critical
4. **Use appropriate model** - Current models are lite/float16 optimized

## Troubleshooting

### Import Error
```
ModuleNotFoundError: No module named 'mediapipe'
```
**Solution:** `pip install mediapipe>=0.10.32`

### Model Not Found
```
FileNotFoundError: Hand model not found: ...
```
**Solution:** Run `python3 test_roi_tracker.py` to verify models are downloaded

### No Detections
- Check lighting conditions
- Ensure subjects are visible in frame
- Lower confidence thresholds
- Verify camera is working: `cv2.imshow('Test', frame)`

## MediaPipe Tasks API Reference

- [Hand Landmarker](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker)
- [Face Detector](https://developers.google.com/mediapipe/solutions/vision/face_detector)
- [Pose Landmarker](https://developers.google.com/mediapipe/solutions/vision/pose_landmarker)

## Changelog

### v2.0 (Jan 27, 2025)
- **BREAKING**: Migrated from `mp.solutions` to `mp.tasks` API
- **COMPATIBLE**: Public interface unchanged (same parameters & return format)
- Added: MediaPipe Tasks models (hand_landmarker, face_detector, pose_landmarker)
- Improved: Video mode tracking for better frame-to-frame consistency
- Fixed: Compatibility with MediaPipe 0.10.32

### v1.0 (Legacy)
- Original implementation using `mp.solutions` API
- **DEPRECATED**: No longer works with MediaPipe 0.10+
