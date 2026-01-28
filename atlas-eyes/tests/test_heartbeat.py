#!/usr/bin/env python3
"""
Heartbeat Detection Test
Records video of hand and attempts to detect pulse (1-2Hz)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.motion_extractor import MotionExtractor
import cv2
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt


def test_heartbeat_detection(duration_seconds: int = 30, camera_index: int = 0):
    """
    Test heartbeat detection from video
    
    Args:
        duration_seconds: How long to record
        camera_index: Camera to use
    """
    print("🔥 Atlas Eyes - Heartbeat Detection Test")
    print("="*50)
    print()
    print("INSTRUCTIONS:")
    print("1. Rest your hand on a flat surface")
    print("2. Keep it as still as possible")
    print("3. The camera should capture your hand/fingers")
    print("4. Recording will run for 30 seconds")
    print()
    input("Press ENTER when ready...")
    
    # Initialize extractor with optical flow (best for subtle motion)
    extractor = MotionExtractor(
        source=camera_index,
        algorithm='optical_flow',
        fps=30
    )
    
    # Data collection
    motion_intensities = []
    timestamps = []
    start_time = None
    
    print(f"\nRecording for {duration_seconds} seconds...")
    print("Keep your hand still!")
    
    try:
        frame_count = 0
        while True:
            motion_data = extractor.process_frame()
            
            if motion_data is None:
                break
            
            if start_time is None:
                start_time = motion_data['timestamp']
            
            elapsed = motion_data['timestamp'] - start_time
            
            # Collect motion intensity over time
            motion_intensities.append(motion_data['intensity'])
            timestamps.append(elapsed)
            
            # Display progress
            if frame_count % 30 == 0:
                print(f"  {elapsed:.1f}s - Motion intensity: {motion_data['intensity']:.4f}")
            
            # Show video
            cv2.imshow('Heartbeat Detection - Keep Hand Still', motion_data['frame'])
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            frame_count += 1
            
            # Stop after duration
            if elapsed >= duration_seconds:
                break
    
    finally:
        extractor.release()
    
    # Analyze collected data
    print("\n" + "="*50)
    print("ANALYZING DATA...")
    print("="*50)
    
    if len(motion_intensities) < 100:
        print("ERROR: Not enough data collected")
        return
    
    # Convert to numpy arrays
    intensities = np.array(motion_intensities)
    times = np.array(timestamps)
    
    # Calculate sampling rate
    avg_dt = np.mean(np.diff(times))
    fs = 1.0 / avg_dt  # Sampling frequency
    
    print(f"\nData collected:")
    print(f"  Frames: {len(intensities)}")
    print(f"  Duration: {times[-1]:.2f}s")
    print(f"  Sampling rate: {fs:.2f} Hz")
    
    # Apply FFT to find dominant frequencies
    # Focus on 0.5-3 Hz range (30-180 BPM)
    fft = np.fft.fft(intensities)
    frequencies = np.fft.fftfreq(len(intensities), d=avg_dt)
    
    # Get positive frequencies only
    pos_mask = frequencies > 0
    frequencies = frequencies[pos_mask]
    fft_magnitude = np.abs(fft[pos_mask])
    
    # Focus on heartbeat range (0.5-3 Hz = 30-180 BPM)
    heartbeat_mask = (frequencies >= 0.5) & (frequencies <= 3.0)
    heartbeat_freqs = frequencies[heartbeat_mask]
    heartbeat_magnitudes = fft_magnitude[heartbeat_mask]
    
    if len(heartbeat_freqs) == 0:
        print("\nERROR: No data in heartbeat frequency range")
        return
    
    # Find dominant frequency
    dominant_idx = np.argmax(heartbeat_magnitudes)
    dominant_freq = heartbeat_freqs[dominant_idx]
    dominant_bpm = dominant_freq * 60
    
    print(f"\n" + "="*50)
    print("RESULTS")
    print("="*50)
    print(f"Dominant frequency: {dominant_freq:.3f} Hz")
    print(f"Estimated BPM: {dominant_bpm:.1f}")
    
    # Confidence check
    signal_to_noise = heartbeat_magnitudes[dominant_idx] / np.mean(heartbeat_magnitudes)
    print(f"Signal-to-noise ratio: {signal_to_noise:.2f}")
    
    if signal_to_noise > 2.0:
        print("✅ CONFIDENCE: HIGH - Clear heartbeat signal detected")
    elif signal_to_noise > 1.5:
        print("⚠️  CONFIDENCE: MEDIUM - Possible heartbeat detected")
    else:
        print("❌ CONFIDENCE: LOW - Signal too weak, may be noise")
    
    print("\nNOTE: For best results:")
    print("- Ensure good lighting")
    print("- Keep hand completely still")
    print("- Point camera at fingertips or palm")
    print("- Compare with actual heart rate monitor")
    
    # Plot results
    try:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Plot motion intensity over time
        ax1.plot(times, intensities)
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Motion Intensity')
        ax1.set_title('Motion Intensity Over Time')
        ax1.grid(True)
        
        # Plot frequency spectrum
        ax2.plot(heartbeat_freqs, heartbeat_magnitudes)
        ax2.axvline(dominant_freq, color='r', linestyle='--', 
                   label=f'Dominant: {dominant_freq:.3f} Hz ({dominant_bpm:.1f} BPM)')
        ax2.set_xlabel('Frequency (Hz)')
        ax2.set_ylabel('Magnitude')
        ax2.set_title('Frequency Spectrum (Heartbeat Range: 0.5-3 Hz)')
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        
        # Save plot
        plot_filename = 'heartbeat_analysis.png'
        plt.savefig(plot_filename)
        print(f"\nPlot saved: {plot_filename}")
        
        # Show plot
        plt.show()
    
    except Exception as e:
        print(f"\nWarning: Could not create plots: {e}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Heartbeat Detection Test')
    parser.add_argument('--duration', type=int, default=30, help='Recording duration in seconds')
    parser.add_argument('--camera', type=int, default=0, help='Camera index')
    
    args = parser.parse_args()
    
    test_heartbeat_detection(duration_seconds=args.duration, camera_index=args.camera)


if __name__ == '__main__':
    main()
