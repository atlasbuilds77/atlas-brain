#!/usr/bin/env python3
"""
Test script for tremor detection and ROI tracking
Demonstrates the new functionality
"""

import cv2
import sys
import time
sys.path.insert(0, '../src')

from motion_extractor import MotionExtractor
import numpy as np


def main():
    print("=" * 60)
    print("Atlas Eyes - Tremor Detection & ROI Tracking Test")
    print("=" * 60)
    print()
    print("Features tested:")
    print("  ✓ Hand detection (left/right)")
    print("  ✓ Face detection")
    print("  ✓ Chest detection")
    print("  ✓ FFT-based tremor analysis (3-6 Hz)")
    print("  ✓ Per-ROI tremor detection")
    print("  ✓ Heartbeat detection from chest (1-2 Hz)")
    print()
    print("Press 'q' to quit, 's' to save screenshot")
    print("=" * 60)
    print()
    
    # Initialize motion extractor with frame differencing
    with MotionExtractor(
        source=0,
        algorithm='frame_diff',
        width=640,
        height=480,
        fps=30
    ) as extractor:
        
        frame_count = 0
        start_time = time.time()
        
        while True:
            # Process frame
            motion_data = extractor.process_frame()
            
            if motion_data is None:
                print("❌ Failed to read frame")
                break
            
            frame = motion_data['frame']
            frame_count += 1
            
            # Draw ROI bounding boxes
            if motion_data.get('rois'):
                rois = motion_data['rois']
                annotated = extractor.roi_tracker.draw_rois(frame, rois)
            else:
                annotated = frame.copy()
            
            # Display tremor detection results
            roi_motion = motion_data.get('roi_motion', {})
            
            y_offset = 30
            line_height = 25
            
            # Display FPS and frame count
            cv2.putText(
                annotated,
                f"FPS: {motion_data['fps']:.1f} | Frame: {frame_count}",
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )
            y_offset += line_height
            
            # Display ROI count
            hands_count = len(rois.get('hands', []))
            has_face = 1 if rois.get('face') else 0
            has_chest = 1 if rois.get('chest') else 0
            
            cv2.putText(
                annotated,
                f"ROIs: {hands_count} hands, {has_face} face, {has_chest} chest",
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )
            y_offset += line_height + 10
            
            # Display tremor detection for each ROI
            for roi_name, data in roi_motion.items():
                tremor = data.get('tremor', {})
                
                if tremor.get('detected'):
                    freq = tremor.get('frequency_hz', 0)
                    confidence = tremor.get('confidence', 0)
                    color = (0, 0, 255)  # Red for detected tremor
                    status = f"⚠️ TREMOR: {freq:.2f}Hz (conf: {confidence:.2f})"
                else:
                    color = (0, 255, 0)  # Green for no tremor
                    if tremor.get('ready'):
                        status = "✓ OK"
                    else:
                        fill = tremor.get('buffer_fill', 0)
                        status = f"⏳ Collecting data... {fill*100:.0f}%"
                
                cv2.putText(
                    annotated,
                    f"{roi_name.replace('_', ' ').title()}: {status}",
                    (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    2
                )
                y_offset += line_height
                
                # Show heartbeat for chest
                if roi_name == 'chest' and 'heartbeat' in data:
                    heartbeat = data['heartbeat']
                    if heartbeat.get('detected'):
                        bpm = heartbeat.get('bpm', 0)
                        cv2.putText(
                            annotated,
                            f"  ♥ Heartbeat: {bpm:.0f} BPM",
                            (10, y_offset),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (255, 100, 100),
                            2
                        )
                        y_offset += line_height
            
            # Display global tremor detection
            y_offset += 10
            global_tremor = motion_data.get('frequency_data', {}).get('tremor', {})
            if global_tremor.get('detected'):
                freq = global_tremor.get('frequency_hz', 0)
                cv2.putText(
                    annotated,
                    f"Global Tremor: {freq:.2f} Hz",
                    (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 255),
                    2
                )
            
            # Display instructions
            instructions_y = annotated.shape[0] - 40
            cv2.putText(
                annotated,
                "Press 'q' to quit, 's' to save screenshot",
                (10, instructions_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (200, 200, 200),
                1
            )
            
            # Show the frame
            cv2.imshow('Atlas Eyes - Tremor Detection & ROI Tracking', annotated)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\n👋 Quitting...")
                break
            elif key == ord('s'):
                timestamp = int(time.time())
                filename = f'tremor_roi_screenshot_{timestamp}.png'
                cv2.imwrite(filename, annotated)
                print(f"📸 Screenshot saved: {filename}")
            
            # Print summary every 5 seconds
            if frame_count % 150 == 0:
                elapsed = time.time() - start_time
                print(f"\n⏱️  Runtime: {elapsed:.1f}s | Frames: {frame_count} | FPS: {frame_count/elapsed:.1f}")
                
                if roi_motion:
                    print("   ROI Tremor Status:")
                    for roi_name, data in roi_motion.items():
                        tremor = data.get('tremor', {})
                        if tremor.get('detected'):
                            freq = tremor['frequency_hz']
                            conf = tremor['confidence']
                            print(f"     - {roi_name}: TREMOR at {freq:.2f}Hz (confidence: {conf:.2f})")
                        elif tremor.get('ready'):
                            print(f"     - {roi_name}: No tremor detected")
                        else:
                            fill = tremor.get('buffer_fill', 0)
                            print(f"     - {roi_name}: Collecting data ({fill*100:.0f}%)")
    
    print("\n✅ Test completed!")
    print(f"Total frames processed: {frame_count}")
    print(f"Total runtime: {time.time() - start_time:.1f}s")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
