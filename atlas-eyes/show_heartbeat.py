#!/usr/bin/env python3
"""
Atlas Eyes - Live Heartbeat Detection Demo
Shows BPM in real-time from camera feed
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from motion_extractor import MotionExtractor
import cv2

def main():
    print("🔥 Atlas Eyes - Live Heartbeat Detection")
    print("=" * 60)
    print("Starting camera...")
    print()
    print("Instructions:")
    print("  - Keep your hand steady in view")
    print("  - Wait 5-10 seconds for BPM calculation")
    print("  - Press 'q' to quit")
    print()
    
    # Initialize
    extractor = MotionExtractor(
        source=0,
        algorithm='optical_flow',
        width=640,
        height=480
    )
    
    frame_count = 0
    
    try:
        while True:
            # Process frame
            data = extractor.process_frame()
            if data is None:
                break
            
            frame_count += 1
            frame = data['frame']
            motion_frame = data.get('motion_frame', frame.copy())
            
            # Get heartbeat detection
            heartbeat_data = extractor.detect_heartbeat()
            tremor_data = extractor.detect_tremor()
            
            # Overlay stats on frame
            cv2.putText(frame, "Atlas Eyes - Heartbeat Detection", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            y = 70
            if heartbeat_data and heartbeat_data.get('detected'):
                bpm = heartbeat_data['bpm']
                conf = heartbeat_data.get('confidence', 0) * 100
                cv2.putText(frame, f"HEARTBEAT: {bpm:.1f} BPM ({conf:.0f}%)", (10, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
                y += 40
            else:
                cv2.putText(frame, "HEARTBEAT: Detecting...", (10, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (128, 128, 128), 2)
                y += 40
            
            if tremor_data and tremor_data.get('detected'):
                freq = tremor_data['frequency_hz']
                cv2.putText(frame, f"TREMOR: {freq:.2f} Hz", (10, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 128, 0), 2)
            
            # Motion intensity
            cv2.putText(frame, f"Motion: {data['intensity']:.3f}", (10, frame.shape[0] - 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(frame, f"FPS: {data['fps']:.1f}", (10, frame.shape[0] - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            # Show
            cv2.imshow('Atlas Eyes - Heartbeat Detection', frame)
            cv2.imshow('Motion Extraction', motion_frame)
            
            # Terminal output
            if frame_count % 30 == 0:
                status = f"Frame {frame_count} | FPS: {data['fps']:.1f} | "
                if heartbeat_data and heartbeat_data.get('detected'):
                    status += f"💓 BPM: {heartbeat_data['bpm']:.1f}"
                else:
                    status += "💓 BPM: --"
                if tremor_data and tremor_data.get('detected'):
                    status += f" | 🌊 Tremor: {tremor_data['frequency_hz']:.2f}Hz"
                print(status)
            
            # Quit on 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\n\nStopping...")
    
    finally:
        extractor.release()
        cv2.destroyAllWindows()
        print("\n✨ Atlas Eyes session complete")

if __name__ == '__main__':
    main()
