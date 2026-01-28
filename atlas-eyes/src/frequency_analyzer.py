"""
Atlas Eyes - Frequency Analysis Module
FFT-based frequency detection for periodic motion (heartbeat, tremor, etc.)
"""

import numpy as np
from scipy import fftpack
from scipy.signal import find_peaks
from collections import deque
from typing import Dict, Optional, Tuple
import time


class FrequencyAnalyzer:
    """
    FFT-based frequency analyzer for detecting periodic motion patterns
    Designed for heartbeat detection (1-2 Hz / 60-120 BPM)
    """
    
    def __init__(
        self,
        sample_rate: float = 30.0,
        window_size: int = 300,  # 10 seconds at 30fps
        min_confidence: float = 1.5
    ):
        """
        Initialize frequency analyzer
        
        Args:
            sample_rate: Sampling rate in Hz (typically camera FPS)
            window_size: Number of samples in rolling window
            min_confidence: Minimum confidence threshold (peak_amp / mean_amp)
        """
        self.sample_rate = sample_rate
        self.window_size = window_size
        self.min_confidence = min_confidence
        
        # Rolling buffer for motion intensities
        self.intensity_buffer = deque(maxlen=window_size)
        self.timestamp_buffer = deque(maxlen=window_size)
        
        # FFT cache
        self._last_fft_time = 0
        self._fft_cache_duration = 0.5  # Cache FFT results for 500ms
        self._cached_spectrum = None
        
    def add_sample(self, intensity: float, timestamp: Optional[float] = None):
        """
        Add a motion intensity sample to the buffer
        
        Args:
            intensity: Motion intensity value (0-1 range)
            timestamp: Optional timestamp (uses current time if None)
        """
        if timestamp is None:
            timestamp = time.time()
        
        self.intensity_buffer.append(intensity)
        self.timestamp_buffer.append(timestamp)
        
        # Invalidate cache when new data arrives
        if len(self.intensity_buffer) >= self.window_size // 2:
            self._cached_spectrum = None
    
    def compute_fft(self, apply_window: bool = True) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute FFT of intensity time series
        
        Args:
            apply_window: Whether to apply Hamming window (reduces spectral leakage)
        
        Returns:
            Tuple of (frequencies, amplitudes)
        """
        if len(self.intensity_buffer) < 10:
            return np.array([]), np.array([])
        
        # Convert to numpy array
        signal = np.array(list(self.intensity_buffer))
        
        # Apply Hamming window to reduce spectral leakage
        if apply_window:
            window = np.hamming(len(signal))
            signal = signal * window
        
        # Compute FFT
        fft_vals = fftpack.fft(signal)
        fft_freq = fftpack.fftfreq(len(signal), 1.0 / self.sample_rate)
        
        # Only keep positive frequencies
        positive_mask = fft_freq > 0
        frequencies = fft_freq[positive_mask]
        amplitudes = np.abs(fft_vals[positive_mask])
        
        return frequencies, amplitudes
    
    def detect_peak_frequency(
        self,
        freq_min: float = 1.0,
        freq_max: float = 2.0,
        min_prominence: float = None
    ) -> Dict:
        """
        Detect dominant frequency peak in specified range
        
        Args:
            freq_min: Minimum frequency (Hz)
            freq_max: Maximum frequency (Hz)
            min_prominence: Minimum peak prominence (auto if None)
        
        Returns:
            Dict with dominant_freq, amplitude, confidence, all_peaks
        """
        if len(self.intensity_buffer) < self.window_size // 3:
            return {
                'dominant_freq': None,
                'amplitude': 0.0,
                'confidence': 0.0,
                'all_peaks': [],
                'ready': False,
                'buffer_fill': len(self.intensity_buffer) / self.window_size
            }
        
        # Check cache
        current_time = time.time()
        if (self._cached_spectrum is not None and 
            current_time - self._last_fft_time < self._fft_cache_duration):
            return self._cached_spectrum
        
        # Compute FFT
        frequencies, amplitudes = self.compute_fft(apply_window=True)
        
        if len(frequencies) == 0:
            return {
                'dominant_freq': None,
                'amplitude': 0.0,
                'confidence': 0.0,
                'all_peaks': [],
                'ready': False,
                'buffer_fill': len(self.intensity_buffer) / self.window_size
            }
        
        # Filter to target frequency range
        freq_mask = (frequencies >= freq_min) & (frequencies <= freq_max)
        target_freqs = frequencies[freq_mask]
        target_amps = amplitudes[freq_mask]
        
        if len(target_freqs) == 0:
            return {
                'dominant_freq': None,
                'amplitude': 0.0,
                'confidence': 0.0,
                'all_peaks': [],
                'ready': True,
                'buffer_fill': 1.0
            }
        
        # Adaptive prominence threshold
        if min_prominence is None:
            mean_amp = np.mean(target_amps)
            min_prominence = mean_amp * 0.5
        
        # Find peaks
        peaks, properties = find_peaks(
            target_amps,
            prominence=min_prominence,
            distance=int(0.1 * self.sample_rate)  # At least 0.1 Hz apart
        )
        
        # Extract peak information
        all_peaks = []
        for peak_idx in peaks:
            freq = target_freqs[peak_idx]
            amp = target_amps[peak_idx]
            all_peaks.append({
                'frequency': float(freq),
                'amplitude': float(amp),
                'prominence': float(properties['prominences'][list(peaks).index(peak_idx)])
            })
        
        # Sort by amplitude
        all_peaks.sort(key=lambda x: x['amplitude'], reverse=True)
        
        # Dominant peak
        if len(all_peaks) > 0:
            dominant = all_peaks[0]
            mean_amp = np.mean(target_amps)
            confidence = dominant['amplitude'] / mean_amp if mean_amp > 0 else 0
            
            result = {
                'dominant_freq': dominant['frequency'],
                'amplitude': dominant['amplitude'],
                'confidence': float(confidence),
                'all_peaks': all_peaks[:5],  # Top 5 peaks
                'ready': True,
                'buffer_fill': 1.0
            }
        else:
            # No significant peaks found
            result = {
                'dominant_freq': None,
                'amplitude': 0.0,
                'confidence': 0.0,
                'all_peaks': [],
                'ready': True,
                'buffer_fill': 1.0
            }
        
        # Cache result
        self._cached_spectrum = result
        self._last_fft_time = current_time
        
        return result
    
    def detect_heartbeat(self) -> Dict:
        """
        Detect heartbeat from motion data
        Target range: 1-2 Hz (60-120 BPM)
        
        Returns:
            Dict with bpm, confidence, detected flag
        """
        result = self.detect_peak_frequency(freq_min=1.0, freq_max=2.0)
        
        if result['dominant_freq'] is not None:
            bpm = result['dominant_freq'] * 60  # Convert Hz to BPM
            detected = result['confidence'] >= self.min_confidence
            
            return {
                'detected': detected,
                'bpm': float(bpm),
                'frequency_hz': result['dominant_freq'],
                'confidence': result['confidence'],
                'ready': result['ready'],
                'buffer_fill': result['buffer_fill']
            }
        else:
            return {
                'detected': False,
                'bpm': None,
                'frequency_hz': None,
                'confidence': 0.0,
                'ready': result['ready'],
                'buffer_fill': result['buffer_fill']
            }
    
    def detect_tremor(self) -> Dict:
        """
        Detect tremor from motion data
        Target range: 3-6 Hz (Parkinson's characteristic)
        
        Returns:
            Dict with frequency, confidence, detected flag
        """
        result = self.detect_peak_frequency(freq_min=3.0, freq_max=6.0)
        
        if result['dominant_freq'] is not None:
            detected = result['confidence'] >= self.min_confidence
            
            return {
                'detected': detected,
                'frequency_hz': result['dominant_freq'],
                'confidence': result['confidence'],
                'ready': result['ready'],
                'buffer_fill': result['buffer_fill']
            }
        else:
            return {
                'detected': False,
                'frequency_hz': None,
                'confidence': 0.0,
                'ready': result['ready'],
                'buffer_fill': result['buffer_fill']
            }
    
    def get_full_spectrum(
        self,
        freq_max: float = 10.0,
        num_bins: int = 100
    ) -> Dict:
        """
        Get full frequency spectrum for visualization
        
        Args:
            freq_max: Maximum frequency to include
            num_bins: Number of frequency bins
        
        Returns:
            Dict with frequencies and amplitudes arrays
        """
        frequencies, amplitudes = self.compute_fft(apply_window=True)
        
        if len(frequencies) == 0:
            return {
                'frequencies': [],
                'amplitudes': [],
                'ready': False
            }
        
        # Filter to max frequency
        mask = frequencies <= freq_max
        frequencies = frequencies[mask]
        amplitudes = amplitudes[mask]
        
        # Resample to fixed number of bins
        if len(frequencies) > num_bins:
            indices = np.linspace(0, len(frequencies) - 1, num_bins, dtype=int)
            frequencies = frequencies[indices]
            amplitudes = amplitudes[indices]
        
        return {
            'frequencies': frequencies.tolist(),
            'amplitudes': amplitudes.tolist(),
            'ready': len(self.intensity_buffer) >= self.window_size // 3,
            'sample_count': len(self.intensity_buffer),
            'window_size': self.window_size
        }
    
    def reset(self):
        """Clear all buffers and cache"""
        self.intensity_buffer.clear()
        self.timestamp_buffer.clear()
        self._cached_spectrum = None
        self._last_fft_time = 0
    
    def get_stats(self) -> Dict:
        """Get analyzer statistics"""
        if len(self.intensity_buffer) > 0:
            intensities = list(self.intensity_buffer)
            mean_intensity = np.mean(intensities)
            std_intensity = np.std(intensities)
        else:
            mean_intensity = 0.0
            std_intensity = 0.0
        
        return {
            'sample_rate': self.sample_rate,
            'window_size': self.window_size,
            'buffer_fill': len(self.intensity_buffer),
            'buffer_fill_pct': len(self.intensity_buffer) / self.window_size,
            'mean_intensity': float(mean_intensity),
            'std_intensity': float(std_intensity),
            'ready': len(self.intensity_buffer) >= self.window_size // 3
        }
