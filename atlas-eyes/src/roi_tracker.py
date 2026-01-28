"""
Atlas Eyes - Region of Interest (ROI) Tracker
Detects and tracks specific body regions: hands, face, chest
Uses MediaPipe Tasks API (0.10.x) for accurate landmark detection
"""

import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os


class ROITracker:
    """
    Track regions of interest in video frames using MediaPipe Tasks API
    - Hands: HandLandmarker (accurate hand tracking)
    - Face: FaceDetector (face detection)
    - Chest: PoseLandmarker (pose-based torso detection)
    """
    
    def __init__(
        self,
        detect_hands: bool = True,
        detect_face: bool = True,
        detect_chest: bool = True,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        max_num_hands: int = 2,
        model_path: Optional[str] = None
    ):
        """
        Initialize ROI tracker with MediaPipe Tasks API
        
        Args:
            detect_hands: Enable hand detection
            detect_face: Enable face detection
            detect_chest: Enable chest/torso detection
            min_detection_confidence: Minimum confidence for initial detection
            min_tracking_confidence: Minimum confidence for tracking
            max_num_hands: Maximum number of hands to track
            model_path: Base path for model files (default: ../models/)
        """
        self.detect_hands_enabled = detect_hands
        self.detect_face_enabled = detect_face
        self.detect_chest_enabled = detect_chest
        
        # Determine model path
        if model_path is None:
            # Default to models directory relative to this file
            script_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(script_dir, '..', 'models')
        
        self.model_path = os.path.expanduser(model_path)
        
        # Initialize detectors
        self.hand_landmarker = None
        self.face_detector = None
        self.pose_landmarker = None
        
        # Initialize hand detector
        if self.detect_hands_enabled:
            hand_model = os.path.join(self.model_path, 'hand_landmarker.task')
            if not os.path.exists(hand_model):
                raise FileNotFoundError(f"Hand model not found: {hand_model}")
            
            base_options = python.BaseOptions(model_asset_path=hand_model)
            options = vision.HandLandmarkerOptions(
                base_options=base_options,
                running_mode=vision.RunningMode.VIDEO,
                num_hands=max_num_hands,
                min_hand_detection_confidence=min_detection_confidence,
                min_hand_presence_confidence=min_tracking_confidence,
                min_tracking_confidence=min_tracking_confidence
            )
            self.hand_landmarker = vision.HandLandmarker.create_from_options(options)
        
        # Initialize face detector
        if self.detect_face_enabled:
            face_model = os.path.join(self.model_path, 'face_detector.task')
            if not os.path.exists(face_model):
                raise FileNotFoundError(f"Face model not found: {face_model}")
            
            base_options = python.BaseOptions(model_asset_path=face_model)
            options = vision.FaceDetectorOptions(
                base_options=base_options,
                running_mode=vision.RunningMode.VIDEO,
                min_detection_confidence=min_detection_confidence
            )
            self.face_detector = vision.FaceDetector.create_from_options(options)
        
        # Initialize pose detector
        if self.detect_chest_enabled:
            pose_model = os.path.join(self.model_path, 'pose_landmarker.task')
            if not os.path.exists(pose_model):
                raise FileNotFoundError(f"Pose model not found: {pose_model}")
            
            base_options = python.BaseOptions(model_asset_path=pose_model)
            options = vision.PoseLandmarkerOptions(
                base_options=base_options,
                running_mode=vision.RunningMode.VIDEO,
                min_pose_detection_confidence=min_detection_confidence,
                min_pose_presence_confidence=min_tracking_confidence,
                min_tracking_confidence=min_tracking_confidence
            )
            self.pose_landmarker = vision.PoseLandmarker.create_from_options(options)
        
        # Tracking state
        self.frame_count = 0
        self.last_hand_positions = []
        self.last_face_position = None
        self.last_chest_position = None
    
    def process_frame(self, frame: np.ndarray) -> Dict:
        """
        Process frame and detect all ROIs
        
        Args:
            frame: BGR image from OpenCV
            
        Returns:
            Dictionary with detected ROIs and bounding boxes
        """
        self.frame_count += 1
        
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, _ = frame.shape
        
        # Create MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # Timestamp in milliseconds
        timestamp_ms = int(self.frame_count * 33.33)  # Assuming ~30fps
        
        results = {
            'hands': [],
            'face': None,
            'chest': None,
            'frame_count': self.frame_count,
            'frame_shape': (h, w)
        }
        
        # Detect hands
        if self.detect_hands_enabled and self.hand_landmarker:
            try:
                hand_result = self.hand_landmarker.detect_for_video(mp_image, timestamp_ms)
                if hand_result.hand_landmarks and hand_result.handedness:
                    for idx, (hand_landmarks, handedness) in enumerate(
                        zip(hand_result.hand_landmarks, hand_result.handedness)
                    ):
                        hand_roi = self._extract_hand_roi(hand_landmarks, handedness, w, h, idx)
                        results['hands'].append(hand_roi)
                    self.last_hand_positions = results['hands']
            except Exception as e:
                print(f"Hand detection error: {e}")
        
        # Detect face
        if self.detect_face_enabled and self.face_detector:
            try:
                face_result = self.face_detector.detect_for_video(mp_image, timestamp_ms)
                if face_result.detections:
                    # Use first (most prominent) face
                    detection = face_result.detections[0]
                    face_roi = self._extract_face_roi(detection, w, h)
                    results['face'] = face_roi
                    self.last_face_position = face_roi
                elif self.last_face_position:
                    # Use last known position if tracking lost
                    results['face'] = self._smooth_roi(self.last_face_position, None)
            except Exception as e:
                print(f"Face detection error: {e}")
        
        # Detect chest/torso
        if self.detect_chest_enabled and self.pose_landmarker:
            try:
                pose_result = self.pose_landmarker.detect_for_video(mp_image, timestamp_ms)
                if pose_result.pose_landmarks:
                    # Use first pose
                    chest_roi = self._extract_chest_roi(pose_result.pose_landmarks[0], w, h)
                    results['chest'] = chest_roi
                    self.last_chest_position = chest_roi
                elif self.last_chest_position:
                    results['chest'] = self._smooth_roi(self.last_chest_position, None)
            except Exception as e:
                print(f"Pose detection error: {e}")
        
        return results
    
    def _extract_hand_roi(
        self,
        hand_landmarks,
        handedness,
        width: int,
        height: int,
        hand_id: int
    ) -> Dict:
        """Extract hand ROI from MediaPipe landmarks"""
        # Get all landmark coordinates
        x_coords = [lm.x * width for lm in hand_landmarks]
        y_coords = [lm.y * height for lm in hand_landmarks]
        
        # Calculate bounding box with padding
        padding = 20
        x_min = max(0, int(min(x_coords)) - padding)
        x_max = min(width, int(max(x_coords)) + padding)
        y_min = max(0, int(min(y_coords)) - padding)
        y_max = min(height, int(max(y_coords)) + padding)
        
        # Calculate centroid
        cx = int(np.mean(x_coords))
        cy = int(np.mean(y_coords))
        
        # Determine hand label (left/right)
        label = handedness[0].category_name  # "Left" or "Right"
        confidence = handedness[0].score
        
        return {
            'type': 'hand',
            'label': label.lower(),
            'hand_id': hand_id,
            'bbox': {
                'x': x_min,
                'y': y_min,
                'w': x_max - x_min,
                'h': y_max - y_min
            },
            'center': {'x': cx, 'y': cy},
            'confidence': float(confidence),
            'landmarks': [
                {'x': lm.x * width, 'y': lm.y * height, 'z': lm.z}
                for lm in hand_landmarks
            ]
        }
    
    def _extract_face_roi(self, detection, width: int, height: int) -> Dict:
        """Extract face ROI from MediaPipe detection"""
        bbox = detection.bounding_box
        
        # Convert to pixel coordinates
        x = int(bbox.origin_x)
        y = int(bbox.origin_y)
        w = int(bbox.width)
        h = int(bbox.height)
        
        # Ensure within bounds
        x = max(0, x)
        y = max(0, y)
        w = min(w, width - x)
        h = min(h, height - y)
        
        # Calculate center
        cx = x + w // 2
        cy = y + h // 2
        
        return {
            'type': 'face',
            'bbox': {'x': x, 'y': y, 'w': w, 'h': h},
            'center': {'x': cx, 'y': cy},
            'confidence': float(detection.categories[0].score if detection.categories else 0.0)
        }
    
    def _extract_chest_roi(self, pose_landmarks, width: int, height: int) -> Dict:
        """
        Extract chest/torso ROI from pose landmarks
        Uses shoulders and hips to define the chest region
        """
        # Key landmarks (MediaPipe Pose indices)
        # 11: left shoulder, 12: right shoulder
        # 23: left hip, 24: right hip
        left_shoulder = pose_landmarks[11]
        right_shoulder = pose_landmarks[12]
        left_hip = pose_landmarks[23]
        right_hip = pose_landmarks[24]
        
        # Calculate bounding box for chest region
        x_coords = [
            left_shoulder.x * width,
            right_shoulder.x * width,
            left_hip.x * width,
            right_hip.x * width
        ]
        y_coords = [
            left_shoulder.y * height,
            right_shoulder.y * height,
            left_hip.y * height,
            right_hip.y * height
        ]
        
        # Focus on upper torso (shoulder to mid-torso)
        y_min = int(min(y_coords[:2]))  # Top of shoulders
        y_max = int(np.mean([y_coords[0], y_coords[1], y_coords[2], y_coords[3]]))  # Mid torso
        
        x_min = int(min(x_coords))
        x_max = int(max(x_coords))
        
        # Add padding
        padding = 30
        x_min = max(0, x_min - padding)
        x_max = min(width, x_max + padding)
        y_min = max(0, y_min - padding)
        y_max = min(height, y_max + padding)
        
        # Calculate center
        cx = (x_min + x_max) // 2
        cy = (y_min + y_max) // 2
        
        # Calculate average visibility/confidence
        visibility = np.mean([
            left_shoulder.visibility if hasattr(left_shoulder, 'visibility') else 1.0,
            right_shoulder.visibility if hasattr(right_shoulder, 'visibility') else 1.0,
            left_hip.visibility if hasattr(left_hip, 'visibility') else 1.0,
            right_hip.visibility if hasattr(right_hip, 'visibility') else 1.0
        ])
        
        return {
            'type': 'chest',
            'bbox': {
                'x': x_min,
                'y': y_min,
                'w': x_max - x_min,
                'h': y_max - y_min
            },
            'center': {'x': cx, 'y': cy},
            'confidence': float(visibility)
        }
    
    def _smooth_roi(self, prev_roi: Optional[Dict], curr_roi: Optional[Dict]) -> Optional[Dict]:
        """
        Simple exponential smoothing for ROI tracking
        Helps with occlusion and jitter
        """
        if curr_roi is None:
            return prev_roi
        
        if prev_roi is None:
            return curr_roi
        
        # Smooth bounding box coordinates (alpha = 0.7 for responsiveness)
        alpha = 0.7
        smoothed = curr_roi.copy()
        
        for key in ['x', 'y', 'w', 'h']:
            smoothed['bbox'][key] = int(
                alpha * curr_roi['bbox'][key] + (1 - alpha) * prev_roi['bbox'][key]
            )
        
        # Smooth center
        smoothed['center']['x'] = int(
            alpha * curr_roi['center']['x'] + (1 - alpha) * prev_roi['center']['x']
        )
        smoothed['center']['y'] = int(
            alpha * curr_roi['center']['y'] + (1 - alpha) * prev_roi['center']['y']
        )
        
        return smoothed
    
    def get_roi_mask(self, roi: Dict, frame_shape: Tuple[int, int]) -> np.ndarray:
        """
        Create a binary mask for the given ROI
        
        Args:
            roi: ROI dictionary with bbox
            frame_shape: (height, width) of the frame
            
        Returns:
            Binary mask (0s and 1s) of shape frame_shape
        """
        mask = np.zeros(frame_shape, dtype=np.uint8)
        
        if roi is None:
            return mask
        
        bbox = roi['bbox']
        x, y, w, h = bbox['x'], bbox['y'], bbox['w'], bbox['h']
        
        # Set ROI region to 1
        mask[y:y+h, x:x+w] = 1
        
        return mask
    
    def draw_rois(self, frame: np.ndarray, rois: Dict) -> np.ndarray:
        """
        Draw ROI bounding boxes on frame for visualization
        
        Args:
            frame: BGR image
            rois: Dictionary of ROIs from process_frame()
            
        Returns:
            Annotated frame
        """
        annotated = frame.copy()
        
        # Draw hands (green)
        for hand in rois.get('hands', []):
            bbox = hand['bbox']
            label = f"{hand['label'].capitalize()} Hand ({hand['confidence']:.2f})"
            
            cv2.rectangle(
                annotated,
                (bbox['x'], bbox['y']),
                (bbox['x'] + bbox['w'], bbox['y'] + bbox['h']),
                (0, 255, 0),
                2
            )
            cv2.putText(
                annotated,
                label,
                (bbox['x'], bbox['y'] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )
        
        # Draw face (blue)
        if rois.get('face'):
            face = rois['face']
            bbox = face['bbox']
            label = f"Face ({face['confidence']:.2f})"
            
            cv2.rectangle(
                annotated,
                (bbox['x'], bbox['y']),
                (bbox['x'] + bbox['w'], bbox['y'] + bbox['h']),
                (255, 0, 0),
                2
            )
            cv2.putText(
                annotated,
                label,
                (bbox['x'], bbox['y'] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 0, 0),
                2
            )
        
        # Draw chest (red)
        if rois.get('chest'):
            chest = rois['chest']
            bbox = chest['bbox']
            label = f"Chest ({chest['confidence']:.2f})"
            
            cv2.rectangle(
                annotated,
                (bbox['x'], bbox['y']),
                (bbox['x'] + bbox['w'], bbox['y'] + bbox['h']),
                (0, 0, 255),
                2
            )
            cv2.putText(
                annotated,
                label,
                (bbox['x'], bbox['y'] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255),
                2
            )
        
        return annotated
    
    def release(self):
        """Release MediaPipe resources"""
        if self.hand_landmarker:
            self.hand_landmarker.close()
        if self.face_detector:
            self.face_detector.close()
        if self.pose_landmarker:
            self.pose_landmarker.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
