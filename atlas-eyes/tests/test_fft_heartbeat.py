#!/usr/bin/env python3
"""
Test FFT-based heartbeat detection
Run this with a webcam and place your hand in view
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from motion_extractor import MotionExtractor
import time
import cv2


def test_heartbeat_detection():
    """Test heartbeat detection with live webcam"""
    print("🫀 Testing FFT-based heartbeat detection")
    print("=" * 60)
    print()
    print("Instructions:")
    print("1. Place your hand in front of the camera (palm facing camera)")
    print("2. Keep your hand as still as possible")
    print("3. Wait 10 seconds for data collection")
    print("4. Press 'q' to quit")
    print()
    print("Starting in 3 seconds...")
    time.sleep(3)
    
    # Initialize motion extractor
    extractor = MotionExtractor(
        source=0,
        algorithm='frame_diff',
        fps=30
    )
    
    print("✓ Motion extractor initialized")
    print("✓ Frequency analyzer initialized")
    print()
    print("Collecting data... (need ~10 seconds)")
    print()
    
    frame_count = 0
    last_print = time.time()
    
    try:
        while True:
            # Process frame
            data = extractor.process_frame()
            if data is None:
                print("❌ Failed to read frame")
                break
            
            frame_count += 1
            
            # Display frame with motion overlay
            display_frame = data['frame'].copy()
            
            # Add text overlay
            freq_data = data.get('frequency_data', {})
            heartbeat = freq_data.get('heartbeat', {})
            buffer_fill = freq_data.get('buffer_fill_pct', 0)
            
            # Status text
            cv2.putText(display_frame, f"Frame: {frame_count}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.putText(display_frame, f"Buffer: {buffer_fill*100:.1f}%", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.putText(display_frame, f"Motion: {data['intensity']:.3f}", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Heartbeat info
            if heartbeat.get('ready', False):
                if heartbeat.get('detected', False):
                    bpm = heartbeat.get('bpm', 0)
                    conf = heartbeat.get('confidence', 0)
                    cv2.putText(display_frame, f"BPM: {bpm:.1f}", (10, 120),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(display_frame, f"Confidence: {conf:.2f}", (10, 150),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    # Draw heartbeat indicator if detected
                    if bpm >= 60 and bpm <= 120:
                        cv2.circle(display_frame, (500, 50), 30, (0, 255, 0), -1)
                        cv2.putText(display_frame, "❤️", (480, 60),
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                else:
                    cv2.putText(display_frame, "No heartbeat detected", (10, 120),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                cv2.putText(display_frame, "Collecting data...", (10, 120),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            # Show frame
            cv2.imshow('Atlas Eyes - Heartbeat Detection', display_frame)
            
            # Print periodic updates
            current_time = time.time()
            if current_time - last_print >= 2.0:
                print(f"[{frame_count:04d}] Motion: {data['intensity']:.4f} | " +
                      f"Buffer: {buffer_fill*100:.1f}% | ", end="")
                
                if heartbeat.get('ready', False):
                    if heartbeat.get('detected', False):
                        bpm = heartbeat.get('bpm', 0)
                        conf = heartbeat.get('confidence', 0)
                        print(f"❤️  BPM: {bpm:.1f} (conf: {conf:.2f})")
                    else:
                        print("No heartbeat detected")
                else:
                    print("Collecting samples...")
                
                last_print = current_time
            
            # Check for quit
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\nQuitting...")
                break
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    finally:
        # Get final stats
        stats = extractor.get_stats()
        print()
        print("=" * 60)
        print("Final Statistics:")
        print(f"  Frames processed: {stats['frame_count']}")
        print(f"  Average FPS: {stats['fps']:.2f}")
        print(f"  Uptime: {stats['uptime']:.1f}s")
        print(f"  Algorithm: {stats['algorithm']}")
        
        freq_stats = stats.get('frequency_analyzer', {})
        if freq_stats:
            print(f"\nFrequency Analyzer:")
            print(f"  Buffer fill: {freq_stats['buffer_fill']}/{freq_stats['window_size']}")
            print(f"  Mean intensity: {freq_stats['mean_intensity']:.4f}")
            print(f"  Std intensity: {freq_stats['std_intensity']:.4f}")
            print(f"  Ready: {freq_stats['ready']}")
        
        # Final heartbeat check
        heartbeat_result = extractor.detect_heartbeat()
        if heartbeat_result and heartbeat_result['ready']:
            print(f"\nFinal Heartbeat Detection:")
            if heartbeat_result['detected']:
                print(f"  ✅ Detected: {heartbeat_result['bpm']:.1f} BPM")
                print(f"  Frequency: {heartbeat_result['frequency_hz']:.3f} Hz")
                print(f"  Confidence: {heartbeat_result['confidence']:.2f}")
            else:
                print(f"  ❌ No heartbeat detected")
                print(f"  Confidence: {heartbeat_result['confidence']:.2f}")
        
        extractor.release()
        print("\n✓ Test complete")


def test_frequency_analyzer_standalone():
    """Test frequency analyzer with synthetic heartbeat signal"""
    print("🔬 Testing frequency analyzer with synthetic signal")
    print("=" * 60)
    
    from frequency_analyzer import FrequencyAnalyzer
    import numpy as np
    
    # Create analyzer
    analyzer = FrequencyAnalyzer(sample_rate=30.0, window_size=300)
    
    # Generate synthetic heartbeat signal (75 BPM = 1.25 Hz)
    target_bpm = 75
    target_freq = target_bpm / 60.0  # 1.25 Hz
    
    print(f"Generating synthetic signal: {target_bpm} BPM ({target_freq:.3f} Hz)")
    
    duration = 10  # seconds
    sample_rate = 30  # Hz
    num_samples = duration * sample_rate
    
    t = np.linspace(0, duration, num_samples)
    # Sine wave with some noise
    signal = 0.5 + 0.3 * np.sin(2 * np.pi * target_freq * t) + np.random.normal(0, 0.05, num_samples)
    signal = np.clip(signal, 0, 1)
    
    print(f"Adding {num_samples} samples...")
    for i, intensity in enumerate(signal):
        analyzer.add_sample(intensity)
    
    print("✓ Samples added")
    print()
    
    # Test heartbeat detection
    result = analyzer.detect_heartbeat()
    print("Heartbeat Detection Results:")
    print(f"  Detected: {result['detected']}")
    print(f"  BPM: {result['bpm']}")
    print(f"  Frequency: {result['frequency_hz']:.3f} Hz")
    print(f"  Confidence: {result['confidence']:.2f}")
    print(f"  Ready: {result['ready']}")
    print()
    
    # Check accuracy
    if result['bpm'] is not None:
        error = abs(result['bpm'] - target_bpm)
        print(f"Accuracy:")
        print(f"  Target: {target_bpm} BPM")
        print(f"  Detected: {result['bpm']:.1f} BPM")
        print(f"  Error: {error:.1f} BPM")
        
        if error <= 5:
            print("  ✅ PASS (within ±5 BPM)")
        else:
            print("  ⚠️  WARN (error > 5 BPM)")
    
    print()
    print("✓ Synthetic test complete")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Test FFT heartbeat detection')
    parser.add_argument('--synthetic', action='store_true', 
                       help='Run synthetic signal test only')
    parser.add_argument('--live', action='store_true',
                       help='Run live webcam test only')
    
    args = parser.parse_args()
    
    if args.synthetic:
        test_frequency_analyzer_standalone()
    elif args.live:
        test_heartbeat_detection()
    else:
        # Run both tests
        print("Running all tests...\n")
        test_frequency_analyzer_standalone()
        print("\n" + "=" * 60 + "\n")
        test_heartbeat_detection()
