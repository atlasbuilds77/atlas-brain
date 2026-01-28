"""
Atlas Eyes API
Interface for Atlas to query motion detection system
"""

from typing import Dict, List, Optional, Any
from motion_extractor import MotionExtractor
import json
import time
import numpy as np
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from threading import Thread, Lock
import logging


def serialize_for_json(obj: Any) -> Any:
    """Convert numpy types to native Python types for JSON serialization"""
    if isinstance(obj, dict):
        return {k: serialize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [serialize_for_json(item) for item in obj]
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    else:
        return obj


class AtlasEyesAPI:
    """API server for Atlas Eyes motion extraction"""
    
    def __init__(self, port: int = 5001, camera_index: int = 0):
        self.port = port
        self.camera_index = camera_index
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'atlas-eyes-secret'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode='threading')
        self.extractor = None
        self.current_data = None
        self.lock = Lock()
        self.running = False
        self.clients_connected = 0
        self.motion_history = []
        self.history_size = 300  # 10 seconds at 30fps
        
        # Disable Flask logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        
        # Register routes and WebSocket handlers
        self._setup_routes()
        self._setup_websocket()
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.route('/api/status', methods=['GET'])
        def status():
            """Get system status"""
            with self.lock:
                if self.extractor is None:
                    return jsonify({'status': 'stopped', 'message': 'Motion extraction not running'})
                
                stats = self.extractor.get_stats()
                return jsonify({
                    'status': 'running',
                    'stats': stats,
                    'camera': self.camera_index
                })
        
        @self.app.route('/api/motion', methods=['GET'])
        def get_motion():
            """Get current motion data"""
            with self.lock:
                if self.current_data is None:
                    return jsonify({'error': 'No motion data available'}), 404
                
                # Return simplified data (no raw frames)
                # Convert numpy types to Python native types
                vectors = self.current_data.get('vectors', [])
                if isinstance(vectors, list):
                    vectors_count = len(vectors)
                else:
                    vectors_count = int(vectors)
                
                return jsonify({
                    'timestamp': float(self.current_data['timestamp']),
                    'motion_detected': bool(self.current_data['motion_detected']),
                    'intensity': float(self.current_data['intensity']),
                    'vectors_count': vectors_count,
                    'frequency_data': self.current_data.get('frequency_data', {}),
                    'fps': float(self.current_data['fps'])
                })
        
        @self.app.route('/api/heartbeat', methods=['GET'])
        def detect_heartbeat():
            """Attempt to detect heartbeat from motion using FFT analysis"""
            with self.lock:
                if self.extractor is None:
                    return jsonify({'error': 'Extractor not running'}), 404
                
                result = self.extractor.detect_heartbeat()
                
                if result is None:
                    return jsonify({
                        'detected': False,
                        'bpm': None,
                        'confidence': 0.0,
                        'ready': False,
                        'message': 'Insufficient data - collecting samples...'
                    })
                
                return jsonify({
                    'detected': result['detected'],
                    'bpm': result['bpm'],
                    'frequency_hz': result['frequency_hz'],
                    'confidence': result['confidence'],
                    'ready': result['ready'],
                    'buffer_fill': result['buffer_fill']
                })
        
        @self.app.route('/api/tremor', methods=['GET'])
        def detect_tremor():
            """Attempt to detect tremor from motion using FFT analysis"""
            with self.lock:
                if self.extractor is None:
                    return jsonify({'error': 'Extractor not running'}), 404
                
                result = self.extractor.detect_tremor()
                
                if result is None:
                    return jsonify({
                        'detected': False,
                        'frequency_hz': None,
                        'confidence': 0.0,
                        'ready': False,
                        'message': 'Insufficient data - collecting samples...'
                    })
                
                return jsonify({
                    'detected': result['detected'],
                    'frequency_hz': result['frequency_hz'],
                    'confidence': result['confidence'],
                    'ready': result['ready'],
                    'buffer_fill': result['buffer_fill']
                })
        
        @self.app.route('/api/roi', methods=['GET'])
        def get_roi():
            """Get current ROI tracking data with focused motion analysis"""
            with self.lock:
                if self.extractor is None:
                    return jsonify({'error': 'Extractor not running'}), 404
                
                roi_data = self.extractor.get_roi_data()
                if roi_data is None:
                    return jsonify({'error': 'No ROI data available'}), 404
                
                return jsonify(roi_data)
        
        @self.app.route('/api/frequency', methods=['GET'])
        def get_frequency_spectrum():
            """Get full frequency spectrum for visualization"""
            with self.lock:
                if self.extractor is None:
                    return jsonify({'error': 'Extractor not running'}), 404
                
                spectrum = self.extractor.get_frequency_spectrum()
                return jsonify({
                    'frequencies': spectrum['frequencies'],
                    'amplitudes': spectrum['amplitudes'],
                    'ready': spectrum['ready'],
                    'sample_count': spectrum['sample_count'],
                    'window_size': spectrum['window_size']
                })
        
        @self.app.route('/api/start', methods=['POST'])
        def start_extraction():
            """Start motion extraction"""
            algorithm = request.json.get('algorithm', 'frame_diff') if request.json else 'frame_diff'
            
            with self.lock:
                if self.extractor is not None:
                    return jsonify({'error': 'Already running'}), 400
                
                try:
                    self.extractor = MotionExtractor(
                        source=self.camera_index,
                        algorithm=algorithm
                    )
                    self.running = True
                    
                    # Start processing thread
                    Thread(target=self._process_loop, daemon=True).start()
                    
                    return jsonify({
                        'status': 'started',
                        'algorithm': algorithm,
                        'camera': self.camera_index
                    })
                except Exception as e:
                    return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/stop', methods=['POST'])
        def stop_extraction():
            """Stop motion extraction"""
            with self.lock:
                if self.extractor is None:
                    return jsonify({'error': 'Not running'}), 400
                
                self.running = False
                self.extractor.release()
                self.extractor = None
                self.current_data = None
                
                return jsonify({'status': 'stopped'})
    
    def _setup_websocket(self):
        """Setup WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            self.clients_connected += 1
            print(f"🔌 Client connected (total: {self.clients_connected})")
            emit('status', {'message': 'Connected to Atlas Eyes'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            self.clients_connected -= 1
            print(f"🔌 Client disconnected (total: {self.clients_connected})")
    
    def _compute_fft_spectrum(self, data: List[float], sample_rate: float = 30.0) -> List[float]:
        """Compute FFT spectrum from motion history"""
        if len(data) < 10:
            return [0.0] * 20
        
        # Perform FFT
        fft = np.fft.rfft(data)
        freqs = np.fft.rfftfreq(len(data), 1.0 / sample_rate)
        magnitudes = np.abs(fft)
        
        # Bin into 20 frequency bands (0-10 Hz)
        spectrum = []
        for i in range(20):
            freq_start = i * 0.5
            freq_end = (i + 1) * 0.5
            mask = (freqs >= freq_start) & (freqs < freq_end)
            if np.any(mask):
                spectrum.append(float(np.mean(magnitudes[mask])))
            else:
                spectrum.append(0.0)
        
        # Normalize
        max_val = max(spectrum) if max(spectrum) > 0 else 1.0
        return [s / max_val for s in spectrum]
    
    def _detect_heartbeat_from_spectrum(self, spectrum: List[float]) -> tuple:
        """Detect heartbeat from frequency spectrum (1-2 Hz range)"""
        # Indices for 1-2 Hz range (60-120 BPM)
        heartbeat_bins = spectrum[2:5]  # 1.0-2.5 Hz
        
        if max(heartbeat_bins) > 0.3:  # Threshold for detection
            peak_idx = heartbeat_bins.index(max(heartbeat_bins))
            freq_hz = 1.0 + (peak_idx * 0.5)
            bpm = freq_hz * 60
            confidence = min(max(heartbeat_bins), 1.0)
            return bpm, confidence
        
        return None, 0.0
    
    def _detect_tremor_from_spectrum(self, spectrum: List[float]) -> tuple:
        """Detect tremor from frequency spectrum (around 4 Hz)"""
        # Indices for 3.5-4.5 Hz range
        tremor_bins = spectrum[7:10]  # 3.5-5.0 Hz
        
        if max(tremor_bins) > 0.4:  # Threshold for detection
            peak_idx = tremor_bins.index(max(tremor_bins))
            freq_hz = 3.5 + (peak_idx * 0.5)
            confidence = min(max(tremor_bins), 1.0)
            return freq_hz, confidence
        
        return None, 0.0
    
    def _process_loop(self):
        """Background processing loop"""
        while self.running:
            try:
                motion_data = self.extractor.process_frame()
                if motion_data is None:
                    break
                
                with self.lock:
                    self.current_data = motion_data
                    
                    # Update motion history
                    intensity = motion_data.get('intensity', 0.0)
                    self.motion_history.append(intensity)
                    if len(self.motion_history) > self.history_size:
                        self.motion_history.pop(0)
                    
                    # Compute frequency spectrum
                    spectrum = self._compute_fft_spectrum(self.motion_history)
                    
                    # Detect heartbeat and tremor
                    bpm, bpm_confidence = self._detect_heartbeat_from_spectrum(spectrum)
                    tremor_freq, tremor_confidence = self._detect_tremor_from_spectrum(spectrum)
                    
                    # Prepare data for WebSocket broadcast
                    ws_data = {
                        'timestamp': float(motion_data['timestamp']),
                        'motion_intensity': float(intensity),
                        'bpm': float(bpm) if bpm is not None else None,
                        'tremor_freq': float(tremor_freq) if tremor_freq is not None else None,
                        'confidence': float(max(bpm_confidence, tremor_confidence)),
                        'fps': float(motion_data.get('fps', 0.0)),
                        'frequency_spectrum': [float(x) for x in spectrum],
                        'motion_detected': bool(motion_data.get('motion_detected', False))
                    }
                    
                    # Broadcast to all connected clients
                    if self.clients_connected > 0:
                        self.socketio.emit('data', ws_data)
                        
                        # Also broadcast ROI data for motion trails
                        roi_data = self.extractor.get_roi_data()
                        if roi_data:
                            # Convert numpy types to native Python types for JSON serialization
                            roi_data_clean = serialize_for_json(roi_data)
                            self.socketio.emit('roi_data', roi_data_clean)
            
            except Exception as e:
                print(f"Error in processing loop: {e}")
                break
        
        # Cleanup on exit
        with self.lock:
            if self.extractor:
                self.extractor.release()
            self.running = False
    
    def run(self, debug: bool = False, auto_start: bool = True):
        """Start the API server"""
        print(f"🔥 Atlas Eyes API starting on port {self.port}")
        print(f"Camera: {self.camera_index}")
        print()
        print("API Endpoints:")
        print("  GET  /api/status     - System status")
        print("  GET  /api/motion     - Current motion data")
        print("  GET  /api/heartbeat  - Heartbeat detection (FFT-based)")
        print("  GET  /api/tremor     - Tremor detection (FFT-based)")
        print("  GET  /api/roi        - ROI tracking with focused tremor analysis")
        print("  GET  /api/frequency  - Full frequency spectrum")
        print("  POST /api/start      - Start extraction")
        print("  POST /api/stop       - Stop extraction")
        print()
        print("WebSocket:")
        print("  WS   /               - Real-time data stream (Socket.IO)")
        print()
        print("🎨 Visualization:")
        print("  Open examples/live_dashboard.html in your browser")
        print()
        
        # Auto-start motion extraction
        if auto_start:
            print("🎬 Auto-starting motion extraction...")
            try:
                self.extractor = MotionExtractor(
                    source=self.camera_index,
                    algorithm='frame_diff'
                )
                self.running = True
                Thread(target=self._process_loop, daemon=True).start()
                print("✅ Motion extraction started")
            except Exception as e:
                print(f"❌ Failed to start motion extraction: {e}")
                print("   Server will continue, but extraction must be started manually via POST /api/start")
        
        print(f"\n🌐 Server running on http://localhost:{self.port}")
        print("Press Ctrl+C to stop\n")
        
        self.socketio.run(self.app, host='0.0.0.0', port=self.port, debug=debug, allow_unsafe_werkzeug=True)


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Atlas Eyes API Server')
    parser.add_argument('--port', type=int, default=5001, help='API port (default 5001, avoiding macOS AirPlay on 5000)')
    parser.add_argument('--camera', type=int, default=0, help='Camera index')
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    parser.add_argument('--no-auto-start', action='store_true', help='Disable auto-start of motion extraction')
    
    args = parser.parse_args()
    
    api = AtlasEyesAPI(port=args.port, camera_index=args.camera)
    api.run(debug=args.debug, auto_start=not args.no_auto_start)


if __name__ == '__main__':
    main()
