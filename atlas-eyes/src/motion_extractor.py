"""
Atlas Eyes - Motion Extraction Core
Real-time motion detection and analysis from camera feeds
"""

import cv2
import numpy as np
from typing import Dict, Optional, Tuple, List
import time
from collections import deque
from scipy import signal
from scipy.fft import rfft, rfftfreq
from roi_tracker import ROITracker
from frequency_analyzer import FrequencyAnalyzer


class MotionExtractor:
    """
    Core motion extraction system supporting multiple algorithms:
    - Frame differencing (fast, general purpose)
    - Lucas-Kanade optical flow (detailed motion vectors)
    - MOG2 background subtraction (robust to lighting changes)
    """
    
    def __init__(
        self,
        source: int = 0,
        algorithm: str = 'frame_diff',
        width: int = 640,
        height: int = 480,
        fps: int = 30,
        buffer_size: int = 30
    ):
        """
        Initialize motion extractor
        
        Args:
            source: Camera index (0 for default webcam) or video file path
            algorithm: 'frame_diff', 'optical_flow', or 'background_sub'
            width: Frame width
            height: Frame height
            fps: Target frames per second
            buffer_size: Number of frames to keep in history
        """
        self.source = source
        self.algorithm = algorithm
        self.width = width
        self.height = height
        self.target_fps = fps
        self.buffer_size = buffer_size
        
        # Initialize video capture
        self.cap = cv2.VideoCapture(source)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, fps)
        
        # Frame buffers
        self.prev_frame = None
        self.prev_gray = None
        self.frame_buffer = deque(maxlen=buffer_size)
        
        # Motion history for frequency analysis
        self.motion_history = deque(maxlen=buffer_size)  # Track motion magnitudes over time
        self.motion_timestamps = deque(maxlen=buffer_size)  # Corresponding timestamps
        
        # Algorithm-specific initializations
        if algorithm == 'background_sub':
            self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
                history=500,
                varThreshold=16,
                detectShadows=True
            )
        elif algorithm == 'optical_flow':
            # Shi-Tomasi corner detection params
            self.feature_params = dict(
                maxCorners=100,
                qualityLevel=0.3,
                minDistance=7,
                blockSize=7
            )
            # Lucas-Kanade optical flow params
            self.lk_params = dict(
                winSize=(15, 15),
                maxLevel=2,
                criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)
            )
            self.p0 = None
        
        # Performance metrics
        self.frame_count = 0
        self.start_time = time.time()
        self.fps_actual = 0
        
        # Frequency analyzer for heartbeat/tremor detection
        self.freq_analyzer = FrequencyAnalyzer(
            sample_rate=fps,
            window_size=min(300, fps * 10),  # 10 seconds or 300 frames
            min_confidence=1.5
        )
        
        # ROI tracker for focused analysis
        self.roi_tracker = ROITracker(
            detect_hands=True,
            detect_face=True,
            detect_chest=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            max_num_hands=2
        )
        
        # Per-ROI frequency analyzers for focused tremor detection
        self.roi_analyzers = {
            'left_hand': FrequencyAnalyzer(sample_rate=fps, window_size=min(300, fps * 10)),
            'right_hand': FrequencyAnalyzer(sample_rate=fps, window_size=min(300, fps * 10)),
            'face': FrequencyAnalyzer(sample_rate=fps, window_size=min(300, fps * 10)),
            'chest': FrequencyAnalyzer(sample_rate=fps, window_size=min(300, fps * 10))
        }
        
        # Current ROI data
        self.current_rois = None
        
    def process_frame(self) -> Optional[Dict]:
        """
        Process next frame and extract motion data
        
        Returns:
            Dictionary with motion data or None if frame read fails
        """
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Store in buffer
        self.frame_buffer.append(gray)
        
        # Initialize on first frame
        if self.prev_gray is None:
            self.prev_gray = gray
            self.prev_frame = frame
            self.frame_count += 1
            return {
                'frame': frame,
                'motion_frame': frame,
                'motion_detected': False,
                'intensity': 0.0,
                'vectors': [],
                'frequency_data': {},
                'timestamp': time.time(),
                'fps': 0.0,
                'frame_count': self.frame_count
            }
        
        # Process based on selected algorithm
        if self.algorithm == 'frame_diff':
            motion_data = self._frame_differencing(frame, gray)
        elif self.algorithm == 'optical_flow':
            motion_data = self._optical_flow(frame, gray)
        elif self.algorithm == 'background_sub':
            motion_data = self._background_subtraction(frame, gray)
        else:
            raise ValueError(f"Unknown algorithm: {self.algorithm}")
        
        # Update state
        self.prev_gray = gray
        self.prev_frame = frame
        self.frame_count += 1
        
        # Calculate FPS
        elapsed = time.time() - self.start_time
        if elapsed > 0:
            self.fps_actual = self.frame_count / elapsed
        
        # Add performance metrics
        motion_data['fps'] = self.fps_actual
        motion_data['frame_count'] = self.frame_count
        motion_data['timestamp'] = time.time()
        
        # Feed intensity to frequency analyzer
        self.freq_analyzer.add_sample(
            intensity=motion_data['intensity'],
            timestamp=motion_data['timestamp']
        )
        
        # Process ROI tracking and focused analysis
        rois = self.process_roi_tracking(frame)
        roi_motion = self.analyze_roi_motion(frame, gray, rois)
        
        # Add ROI data to motion data
        motion_data['rois'] = rois
        motion_data['roi_motion'] = roi_motion
        
        return motion_data
    
    def _frame_differencing(self, frame: np.ndarray, gray: np.ndarray) -> Dict:
        """Simple frame differencing algorithm"""
        # Calculate absolute difference
        diff = cv2.absdiff(self.prev_gray, gray)
        
        # Apply threshold
        _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
        
        # Morphological operations to reduce noise
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        # Calculate motion intensity
        motion_pixels = np.count_nonzero(thresh)
        total_pixels = thresh.shape[0] * thresh.shape[1]
        intensity = motion_pixels / total_pixels
        
        # Find contours (motion regions)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter small contours
        min_area = 500
        motion_regions = [c for c in contours if cv2.contourArea(c) > min_area]
        
        # Extract motion vectors (centroids)
        vectors = []
        for contour in motion_regions:
            M = cv2.moments(contour)
            if M['m00'] > 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                vectors.append({'x': cx, 'y': cy, 'area': cv2.contourArea(contour)})
        
        return {
            'frame': frame,
            'motion_frame': cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR),
            'motion_detected': intensity > 0.01,
            'intensity': float(intensity),
            'vectors': vectors,
            'num_regions': len(motion_regions),
            'frequency_data': self._analyze_frequency()
        }
    
    def _optical_flow(self, frame: np.ndarray, gray: np.ndarray) -> Dict:
        """Lucas-Kanade optical flow algorithm"""
        # Detect features to track
        if self.p0 is None or len(self.p0) < 10:
            self.p0 = cv2.goodFeaturesToTrack(self.prev_gray, mask=None, **self.feature_params)
        
        if self.p0 is None:
            return {
                'frame': frame,
                'motion_frame': frame,
                'motion_detected': False,
                'intensity': 0.0,
                'vectors': [],
                'frequency_data': {}
            }
        
        # Calculate optical flow
        p1, st, err = cv2.calcOpticalFlowPyrLK(self.prev_gray, gray, self.p0, None, **self.lk_params)
        
        # Select good points
        if p1 is not None:
            good_new = p1[st == 1]
            good_old = self.p0[st == 1]
        else:
            good_new = np.array([])
            good_old = np.array([])
        
        # Calculate motion vectors
        vectors = []
        motion_frame = frame.copy()
        total_magnitude = 0
        
        for i, (new, old) in enumerate(zip(good_new, good_old)):
            a, b = new.ravel()
            c, d = old.ravel()
            
            # Calculate magnitude
            dx = a - c
            dy = b - d
            magnitude = np.sqrt(dx**2 + dy**2)
            total_magnitude += magnitude
            
            vectors.append({
                'x': float(a),
                'y': float(b),
                'dx': float(dx),
                'dy': float(dy),
                'magnitude': float(magnitude)
            })
            
            # Draw motion vectors
            motion_frame = cv2.arrowedLine(motion_frame, (int(c), int(d)), (int(a), int(b)), (0, 255, 0), 2)
            motion_frame = cv2.circle(motion_frame, (int(a), int(b)), 5, (0, 0, 255), -1)
        
        # Update feature points
        if len(good_new) > 0:
            self.p0 = good_new.reshape(-1, 1, 2)
        else:
            self.p0 = None
        
        # Calculate average motion intensity
        avg_magnitude = total_magnitude / max(len(vectors), 1)
        intensity = min(avg_magnitude / 50.0, 1.0)  # Normalize to 0-1
        
        return {
            'frame': frame,
            'motion_frame': motion_frame,
            'motion_detected': intensity > 0.05,
            'intensity': float(intensity),
            'vectors': vectors,
            'num_features': len(vectors),
            'frequency_data': self._analyze_frequency()
        }
    
    def _background_subtraction(self, frame: np.ndarray, gray: np.ndarray) -> Dict:
        """MOG2 background subtraction algorithm"""
        # Apply background subtraction
        fg_mask = self.bg_subtractor.apply(frame)
        
        # Remove shadows (set to 0)
        fg_mask[fg_mask == 127] = 0
        
        # Morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        
        # Calculate motion intensity
        motion_pixels = np.count_nonzero(fg_mask)
        total_pixels = fg_mask.shape[0] * fg_mask.shape[1]
        intensity = motion_pixels / total_pixels
        
        # Find contours
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours
        min_area = 500
        motion_regions = [c for c in contours if cv2.contourArea(c) > min_area]
        
        # Extract regions
        vectors = []
        motion_frame = frame.copy()
        for contour in motion_regions:
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)
            
            # Draw on frame
            cv2.rectangle(motion_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Calculate centroid
            M = cv2.moments(contour)
            if M['m00'] > 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                vectors.append({
                    'x': cx,
                    'y': cy,
                    'bbox': {'x': x, 'y': y, 'w': w, 'h': h},
                    'area': float(cv2.contourArea(contour))
                })
        
        return {
            'frame': frame,
            'motion_frame': motion_frame,
            'motion_detected': intensity > 0.01,
            'intensity': float(intensity),
            'vectors': vectors,
            'num_regions': len(motion_regions),
            'frequency_data': self._analyze_frequency()
        }
    
    def _analyze_frequency(self) -> Dict:
        """
        Analyze frequency components in motion over time
        Uses FFT to detect periodic motion (heartbeat, tremor, etc.)
        """
        # Get heartbeat detection
        heartbeat = self.freq_analyzer.detect_heartbeat()
        
        # Get tremor detection
        tremor = self.freq_analyzer.detect_tremor()
        
        # Get analyzer stats
        stats = self.freq_analyzer.get_stats()
        
        return {
            'heartbeat': {
                'detected': heartbeat['detected'],
                'bpm': heartbeat['bpm'],
                'frequency_hz': heartbeat['frequency_hz'],
                'confidence': heartbeat['confidence']
            },
            'tremor': {
                'detected': tremor['detected'],
                'frequency_hz': tremor['frequency_hz'],
                'confidence': tremor['confidence']
            },
            'buffer_fill_pct': stats['buffer_fill_pct'],
            'ready': stats['ready']
        }
    
    def detect_heartbeat(self) -> Optional[Dict]:
        """
        Detect heartbeat frequency from motion data
        Target: 1-2 Hz (60-120 BPM)
        
        Returns:
            Dict with BPM, confidence, detected flag, or None if not ready
        """
        result = self.freq_analyzer.detect_heartbeat()
        
        if not result['ready']:
            return None
        
        return result
    
    def detect_tremor(self) -> Optional[Dict]:
        """
        Detect tremor frequency from motion data
        Target: 3-6 Hz (Parkinson's characteristic frequency)
        
        Returns:
            Dict with frequency, confidence, detected flag, or None if not ready
        """
        result = self.freq_analyzer.detect_tremor()
        
        if not result['ready']:
            return None
        
        return result
    
    def get_stats(self) -> Dict:
        """Get performance statistics"""
        freq_stats = self.freq_analyzer.get_stats()
        
        return {
            'fps': self.fps_actual,
            'frame_count': self.frame_count,
            'uptime': time.time() - self.start_time,
            'buffer_size': len(self.frame_buffer),
            'algorithm': self.algorithm,
            'frequency_analyzer': freq_stats
        }
    
    def get_frequency_spectrum(self) -> Dict:
        """Get full frequency spectrum for visualization"""
        return self.freq_analyzer.get_full_spectrum(freq_max=10.0, num_bins=100)
    
    def process_roi_tracking(self, frame: np.ndarray) -> Dict:
        """
        Process frame for ROI tracking and focused motion analysis
        
        Args:
            frame: Current BGR frame
            
        Returns:
            Dictionary with ROI data and focused analysis
        """
        # Detect ROIs
        rois = self.roi_tracker.process_frame(frame)
        self.current_rois = rois
        
        return rois
    
    def analyze_roi_motion(self, frame: np.ndarray, gray: np.ndarray, rois: Dict) -> Dict:
        """
        Analyze motion within specific ROIs for focused tremor detection
        
        Args:
            frame: BGR frame
            gray: Grayscale frame
            rois: ROI data from process_roi_tracking()
            
        Returns:
            Dictionary with per-ROI motion and tremor analysis
        """
        h, w = gray.shape
        roi_motion = {}
        
        # Analyze each hand
        for hand in rois.get('hands', []):
            label = hand['label']  # 'left' or 'right'
            bbox = hand['bbox']
            
            # Extract ROI
            x, y, bw, bh = bbox['x'], bbox['y'], bbox['w'], bbox['h']
            roi_gray = gray[y:y+bh, x:x+bw]
            
            # Calculate motion intensity in ROI
            if self.prev_gray is not None:
                prev_roi = self.prev_gray[y:y+bh, x:x+bw]
                if prev_roi.shape == roi_gray.shape:
                    diff = cv2.absdiff(prev_roi, roi_gray)
                    intensity = np.mean(diff) / 255.0
                    
                    # Add to corresponding analyzer
                    analyzer_key = f'{label}_hand'
                    if analyzer_key in self.roi_analyzers:
                        self.roi_analyzers[analyzer_key].add_sample(intensity)
                        
                        # Get tremor detection
                        tremor = self.roi_analyzers[analyzer_key].detect_tremor()
                        
                        roi_motion[analyzer_key] = {
                            'roi': hand,
                            'intensity': float(intensity),
                            'tremor': tremor
                        }
        
        # Analyze face
        if rois.get('face'):
            face = rois['face']
            bbox = face['bbox']
            x, y, bw, bh = bbox['x'], bbox['y'], bbox['w'], bbox['h']
            
            # Ensure bounds
            x, y = max(0, x), max(0, y)
            x2, y2 = min(w, x + bw), min(h, y + bh)
            
            if x2 > x and y2 > y:
                roi_gray = gray[y:y2, x:x2]
                
                if self.prev_gray is not None:
                    prev_roi = self.prev_gray[y:y2, x:x2]
                    if prev_roi.shape == roi_gray.shape and roi_gray.size > 0:
                        diff = cv2.absdiff(prev_roi, roi_gray)
                        intensity = np.mean(diff) / 255.0
                        
                        self.roi_analyzers['face'].add_sample(intensity)
                        tremor = self.roi_analyzers['face'].detect_tremor()
                        
                        roi_motion['face'] = {
                            'roi': face,
                            'intensity': float(intensity),
                            'tremor': tremor
                        }
        
        # Analyze chest
        if rois.get('chest'):
            chest = rois['chest']
            bbox = chest['bbox']
            x, y, bw, bh = bbox['x'], bbox['y'], bbox['w'], bbox['h']
            
            # Ensure bounds
            x, y = max(0, x), max(0, y)
            x2, y2 = min(w, x + bw), min(h, y + bh)
            
            if x2 > x and y2 > y:
                roi_gray = gray[y:y2, x:x2]
                
                if self.prev_gray is not None:
                    prev_roi = self.prev_gray[y:y2, x:x2]
                    if prev_roi.shape == roi_gray.shape and roi_gray.size > 0:
                        diff = cv2.absdiff(prev_roi, roi_gray)
                        intensity = np.mean(diff) / 255.0
                        
                        self.roi_analyzers['chest'].add_sample(intensity)
                        tremor = self.roi_analyzers['chest'].detect_tremor()
                        heartbeat = self.roi_analyzers['chest'].detect_heartbeat()
                        
                        roi_motion['chest'] = {
                            'roi': chest,
                            'intensity': float(intensity),
                            'tremor': tremor,
                            'heartbeat': heartbeat
                        }
        
        return roi_motion
    
    def get_roi_data(self) -> Optional[Dict]:
        """
        Get current ROI tracking data with motion analysis
        
        Returns:
            Dictionary with ROI data or None if not available
        """
        if self.current_rois is None:
            return None
        
        # Get motion analysis for current ROIs
        roi_motion = {}
        for roi_name, analyzer in self.roi_analyzers.items():
            tremor = analyzer.detect_tremor()
            stats = analyzer.get_stats()
            
            roi_motion[roi_name] = {
                'tremor': tremor,
                'stats': stats
            }
            
            # Add heartbeat for chest
            if roi_name == 'chest':
                heartbeat = analyzer.detect_heartbeat()
                roi_motion[roi_name]['heartbeat'] = heartbeat
        
        return {
            'rois': self.current_rois,
            'motion_analysis': roi_motion
        }
    
    def release(self):
        """Clean up resources"""
        if self.cap:
            self.cap.release()
        if self.roi_tracker:
            self.roi_tracker.release()
        cv2.destroyAllWindows()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
