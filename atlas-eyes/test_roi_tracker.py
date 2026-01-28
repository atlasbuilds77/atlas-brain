#!/usr/bin/env python3
"""
Test script for ROI tracker with MediaPipe Tasks API
"""

import cv2
import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from roi_tracker import ROITracker


def test_import():
    """Test 1: Import successfully"""
    print("✓ Test 1: Import successful")
    return True


def test_initialization():
    """Test 2: Initialize ROI tracker"""
    try:
        tracker = ROITracker(
            detect_hands=True,
            detect_face=True,
            detect_chest=True
        )
        print("✓ Test 2: Initialization successful")
        tracker.release()
        return True
    except Exception as e:
        print(f"✗ Test 2 failed: {e}")
        return False


def test_process_frame():
    """Test 3: Process a test frame"""
    try:
        # Create a test frame (black image)
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        tracker = ROITracker(
            detect_hands=True,
            detect_face=True,
            detect_chest=True
        )
        
        # Process the frame
        result = tracker.process_frame(test_frame)
        
        # Verify result structure
        assert 'hands' in result
        assert 'face' in result
        assert 'chest' in result
        assert 'frame_count' in result
        assert 'frame_shape' in result
        
        print("✓ Test 3: process_frame() successful")
        print(f"  - Result structure: {list(result.keys())}")
        print(f"  - Hands detected: {len(result['hands'])}")
        print(f"  - Face detected: {'Yes' if result['face'] else 'No'}")
        print(f"  - Chest detected: {'Yes' if result['chest'] else 'No'}")
        
        tracker.release()
        return True
    except Exception as e:
        print(f"✗ Test 3 failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_with_sample_image():
    """Test 4: Process a colored test image with geometric shapes"""
    try:
        # Create a more complex test image
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Add some colored regions to simulate a scene
        # Background
        test_frame[:, :] = (50, 50, 50)
        
        # Draw a simple "face" region (circle)
        cv2.circle(test_frame, (320, 200), 80, (200, 180, 160), -1)
        
        # Draw "hand" regions (circles)
        cv2.circle(test_frame, (150, 350), 50, (220, 200, 180), -1)
        cv2.circle(test_frame, (490, 350), 50, (220, 200, 180), -1)
        
        tracker = ROITracker(
            detect_hands=True,
            detect_face=True,
            detect_chest=True,
            min_detection_confidence=0.3
        )
        
        # Process multiple frames to test video mode
        for i in range(3):
            result = tracker.process_frame(test_frame)
        
        print("✓ Test 4: Multi-frame processing successful")
        print(f"  - Processed {result['frame_count']} frames")
        
        tracker.release()
        return True
    except Exception as e:
        print(f"✗ Test 4 failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_models_exist():
    """Test 5: Verify all model files exist"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(script_dir, 'models')
    
    required_models = [
        'hand_landmarker.task',
        'face_detector.task',
        'pose_landmarker.task'
    ]
    
    all_exist = True
    for model in required_models:
        model_path = os.path.join(models_dir, model)
        exists = os.path.exists(model_path)
        status = "✓" if exists else "✗"
        size = os.path.getsize(model_path) if exists else 0
        print(f"  {status} {model}: {size / 1024:.1f} KB" if exists else f"  {status} {model}: NOT FOUND")
        all_exist = all_exist and exists
    
    if all_exist:
        print("✓ Test 5: All model files present")
        return True
    else:
        print("✗ Test 5: Some model files missing")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Atlas Eyes ROI Tracker - MediaPipe Tasks API Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        ("Import", test_import),
        ("Model Files", test_models_exist),
        ("Initialization", test_initialization),
        ("Process Frame", test_process_frame),
        ("Multi-frame Processing", test_with_sample_image)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\nRunning: {name}")
        print("-" * 60)
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ {name} failed with exception: {e}")
            results.append((name, False))
        print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {name}: {status}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! ROI tracker is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
