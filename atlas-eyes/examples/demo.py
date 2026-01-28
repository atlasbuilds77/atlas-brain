#!/usr/bin/env python3
"""
Atlas Eyes Demo
Real-time motion extraction visualization
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.motion_extractor import MotionExtractor
from src.security import check_kill_switch
import cv2
import argparse
import json


def main():
    parser = argparse.ArgumentParser(description='Atlas Eyes Motion Extraction Demo')
    parser.add_argument('--input', type=str, default=0, help='Camera index or video file path')
    parser.add_argument('--algorithm', type=str, default='frame_diff',
                       choices=['frame_diff', 'optical_flow', 'background_sub'],
                       help='Motion extraction algorithm')
    parser.add_argument('--width', type=int, default=640, help='Frame width')
    parser.add_argument('--height', type=int, default=480, help='Frame height')
    parser.add_argument('--no-display', action='store_true', help='Run without GUI (API only)')
    parser.add_argument('--save-json', type=str, help='Save motion data to JSON file')
    
    args = parser.parse_args()
    
    # CHECK KILL SWITCH BEFORE STARTING
    if check_kill_switch():
        print("🔴 CAMERA SYSTEM DISABLED (Kill switch active)")
        print("Atlas Eyes cannot start while kill switch is active.")
        print("\nTo re-enable camera access:")
        print("  python3 kill_switch.py deactivate")
        sys.exit(1)
    
    # Handle camera index
    source = args.input
    if args.input != 0:
        try:
            source = int(args.input)
        except ValueError:
            source = args.input  # It's a file path
    
    print(f"🔥 Atlas Eyes - Motion Extraction System")
    print(f"Algorithm: {args.algorithm}")
    print(f"Source: {source}")
    print(f"Press 'q' to quit, 's' to screenshot, 'a' to change algorithm")
    print()
    
    # Initialize motion extractor
    extractor = MotionExtractor(
        source=source,
        algorithm=args.algorithm,
        width=args.width,
        height=args.height
    )
    
    motion_log = []
    frame_counter = 0
    
    try:
        while True:
            # Process frame
            motion_data = extractor.process_frame()
            
            if motion_data is None:
                print("End of video or camera disconnected")
                break
            
            frame_counter += 1
            
            # Log data if requested
            if args.save_json:
                # Simplify for JSON
                log_entry = {
                    'frame': frame_counter,
                    'timestamp': motion_data['timestamp'],
                    'motion_detected': motion_data['motion_detected'],
                    'intensity': motion_data['intensity'],
                    'num_vectors': len(motion_data['vectors']),
                    'fps': motion_data['fps']
                }
                motion_log.append(log_entry)
            
            # Display stats in terminal
            if frame_counter % 30 == 0:  # Every second at 30fps
                print(f"Frame {frame_counter} | "
                      f"FPS: {motion_data['fps']:.1f} | "
                      f"Motion: {'YES' if motion_data['motion_detected'] else 'NO '} | "
                      f"Intensity: {motion_data['intensity']:.3f} | "
                      f"Vectors: {len(motion_data['vectors'])}")
            
            # Display visualization
            if not args.no_display:
                # Create side-by-side view
                original = motion_data['frame']
                motion_vis = motion_data.get('motion_frame', original.copy())
                
                # Add text overlays
                cv2.putText(original, f"Original ({args.algorithm})", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(motion_vis, "Motion Extraction", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Add stats
                stats_text = [
                    f"FPS: {motion_data['fps']:.1f}",
                    f"Motion: {motion_data['intensity']:.3f}",
                    f"Vectors: {len(motion_data['vectors'])}"
                ]
                y_offset = 60
                for text in stats_text:
                    cv2.putText(motion_vis, text, (10, y_offset),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    y_offset += 25
                
                # Combine frames
                combined = cv2.hconcat([original, motion_vis])
                
                # Show window
                cv2.imshow('Atlas Eyes - Motion Extraction', combined)
                
                # Handle keys
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("Quitting...")
                    break
                elif key == ord('s'):
                    filename = f"screenshot_{frame_counter}.png"
                    cv2.imwrite(filename, combined)
                    print(f"Screenshot saved: {filename}")
                elif key == ord('a'):
                    # Cycle through algorithms
                    algorithms = ['frame_diff', 'optical_flow', 'background_sub']
                    current_idx = algorithms.index(extractor.algorithm)
                    next_idx = (current_idx + 1) % len(algorithms)
                    extractor.algorithm = algorithms[next_idx]
                    print(f"Switched to algorithm: {extractor.algorithm}")
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    finally:
        # Save JSON log if requested
        if args.save_json and motion_log:
            with open(args.save_json, 'w') as f:
                json.dump({
                    'metadata': {
                        'algorithm': args.algorithm,
                        'source': str(source),
                        'total_frames': frame_counter
                    },
                    'frames': motion_log
                }, f, indent=2)
            print(f"Motion data saved to: {args.save_json}")
        
        # Print final stats
        stats = extractor.get_stats()
        print("\n" + "="*50)
        print("FINAL STATS")
        print("="*50)
        print(f"Total frames: {stats['frame_count']}")
        print(f"Average FPS: {stats['fps']:.2f}")
        print(f"Uptime: {stats['uptime']:.2f}s")
        print(f"Algorithm: {stats['algorithm']}")
        
        # Cleanup
        extractor.release()
        print("\nAtlas Eyes session complete. 👁️⚡")


if __name__ == '__main__':
    main()
