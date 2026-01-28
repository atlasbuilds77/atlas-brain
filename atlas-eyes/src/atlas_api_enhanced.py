"""
Atlas Eyes API - Enhanced with Event Database
Interface for Atlas to query motion detection system with persistent storage
"""

from typing import Dict, List, Optional
from motion_extractor import MotionExtractor
from frequency_analyzer import FrequencyAnalyzer
from event_store import EventStore
from atlas_query import AtlasQuery
import json
import time
from flask import Flask, jsonify, request
from threading import Thread, Lock
import logging


class AtlasEyesAPI:
    """API server for Atlas Eyes motion extraction with event logging"""
    
    def __init__(self, port: int = 5000, camera_index: int = 0, db_path: str = "motion_events.db"):
        self.port = port
        self.camera_index = camera_index
        self.db_path = db_path
        self.app = Flask(__name__)
        self.extractor = None
        self.analyzer = None
        self.event_store = None
        self.atlas_query = None
        self.current_data = None
        self.lock = Lock()
        self.running = False
        
        # Alert configuration
        self.alert_config = {
            'heartbeat_min': 50,
            'heartbeat_max': 120,
            'tremor_threshold': 0.7,
            'motion_spike_threshold': 0.8
        }
        
        # Logging state
        self.last_heartbeat_log = 0
        self.heartbeat_log_interval = 10  # Log every 10 seconds
        
        # Disable Flask logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        
        # Initialize database and query interface
        self.event_store = EventStore(db_path)
        self.event_store.start_writer()
        self.atlas_query = AtlasQuery(db_path)
        
        # Register routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.route('/api/status', methods=['GET'])
        def status():
            """Get system status"""
            with self.lock:
                if self.extractor is None:
                    return jsonify({'status': 'stopped', 'message': 'Motion extraction not running'})
                
                stats = self.extractor.get_stats()
                analyzer_stats = self.analyzer.get_stats() if self.analyzer else {}
                
                return jsonify({
                    'status': 'running',
                    'stats': stats,
                    'analyzer': analyzer_stats,
                    'camera': self.camera_index,
                    'database': {
                        'path': self.db_path,
                        'event_count_24h': self.event_store.count_events(hours=24)
                    }
                })
        
        @self.app.route('/api/motion', methods=['GET'])
        def get_motion():
            """Get current motion data"""
            with self.lock:
                if self.current_data is None:
                    return jsonify({'error': 'No motion data available'}), 404
                
                # Return simplified data (no raw frames)
                return jsonify({
                    'timestamp': self.current_data['timestamp'],
                    'motion_detected': self.current_data['motion_detected'],
                    'intensity': self.current_data['intensity'],
                    'vectors': self.current_data['vectors'],
                    'frequency_data': self.current_data['frequency_data'],
                    'fps': self.current_data['fps']
                })
        
        # ========== HEARTBEAT ENDPOINTS ==========
        
        @self.app.route('/api/heartbeat/current', methods=['GET'])
        def heartbeat_current():
            """Get current heartbeat (latest reading)"""
            latest = self.event_store.get_latest('heartbeat', min_confidence=0.5)
            
            if not latest:
                return jsonify({
                    'detected': False,
                    'message': 'No heartbeat data available'
                }), 404
            
            age = time.time() - latest['timestamp']
            
            return jsonify({
                'detected': True,
                'bpm': latest['value'],
                'confidence': latest['confidence'],
                'timestamp': latest['timestamp'],
                'age_seconds': age,
                'fresh': age < 60
            })
        
        @self.app.route('/api/heartbeat/history', methods=['GET'])
        def heartbeat_history():
            """Get heartbeat history"""
            hours = request.args.get('hours', default=24, type=int)
            min_confidence = request.args.get('min_confidence', default=0.5, type=float)
            
            events = self.event_store.get_history('heartbeat', hours=hours)
            events = [e for e in events if e['confidence'] >= min_confidence]
            
            # Convert to simple time series
            time_series = [{
                'timestamp': e['timestamp'],
                'bpm': e['value'],
                'confidence': e['confidence']
            } for e in events]
            
            return jsonify({
                'hours': hours,
                'count': len(time_series),
                'data': time_series
            })
        
        @self.app.route('/api/heartbeat', methods=['GET'])
        def detect_heartbeat():
            """Legacy endpoint - detect heartbeat from current analyzer"""
            with self.lock:
                if self.analyzer is None:
                    return jsonify({'error': 'Analyzer not running'}), 404
                
                result = self.analyzer.detect_heartbeat()
                return jsonify(result)
        
        # ========== TREMOR ENDPOINTS ==========
        
        @self.app.route('/api/tremor/events', methods=['GET'])
        def tremor_events():
            """Get tremor events log"""
            since = request.args.get('since', type=float)
            hours = request.args.get('hours', default=24, type=int)
            min_confidence = request.args.get('min_confidence', default=0.7, type=float)
            
            if since:
                # Query from timestamp
                events = self.event_store.get_history(
                    'tremor',
                    start_time=since,
                    end_time=time.time()
                )
            else:
                # Query by hours
                events = self.event_store.get_history('tremor', hours=hours)
            
            # Filter by confidence
            events = [e for e in events if e['confidence'] >= min_confidence]
            
            # Format response
            tremor_list = [{
                'timestamp': e['timestamp'],
                'frequency_hz': e['value'],
                'confidence': e['confidence'],
                'metadata': e.get('metadata', {})
            } for e in events]
            
            return jsonify({
                'count': len(tremor_list),
                'events': tremor_list
            })
        
        @self.app.route('/api/tremor', methods=['GET'])
        def detect_tremor():
            """Legacy endpoint - detect tremor from current analyzer"""
            with self.lock:
                if self.analyzer is None:
                    return jsonify({'error': 'Analyzer not running'}), 404
                
                result = self.analyzer.detect_tremor()
                return jsonify(result)
        
        # ========== HEALTH SUMMARY ENDPOINTS ==========
        
        @self.app.route('/api/health/summary', methods=['GET'])
        def health_summary():
            """Get overall health statistics"""
            hours = request.args.get('hours', default=24, type=int)
            
            heartbeat_stats = self.event_store.get_stats('heartbeat', hours=hours)
            tremor_stats = self.event_store.get_stats('tremor', hours=hours)
            motion_stats = self.event_store.get_stats('motion_spike', hours=hours)
            
            return jsonify({
                'hours': hours,
                'heartbeat': {
                    'count': heartbeat_stats['count'],
                    'avg_bpm': heartbeat_stats['avg_value'],
                    'min_bpm': heartbeat_stats['min_value'],
                    'max_bpm': heartbeat_stats['max_value'],
                    'avg_confidence': heartbeat_stats['avg_confidence']
                },
                'tremor': {
                    'count': tremor_stats['count'],
                    'avg_frequency_hz': tremor_stats['avg_value'],
                    'avg_confidence': tremor_stats['avg_confidence']
                },
                'motion_spikes': {
                    'count': motion_stats['count']
                },
                'last_updated': time.time()
            })
        
        @self.app.route('/api/health/check', methods=['GET'])
        def health_check():
            """Quick health check (is everything normal?)"""
            hours = request.args.get('hours', default=1, type=int)
            status_text = self.atlas_query.is_everything_normal(hours=hours)
            
            # Parse for issues
            has_issues = '⚠️' in status_text
            
            return jsonify({
                'normal': not has_issues,
                'status': status_text,
                'hours': hours
            })
        
        # ========== ALERT CONFIGURATION ==========
        
        @self.app.route('/api/alert/config', methods=['GET', 'POST'])
        def alert_config():
            """Get or set alert thresholds"""
            if request.method == 'POST':
                config = request.json
                
                if 'heartbeat_min' in config:
                    self.alert_config['heartbeat_min'] = config['heartbeat_min']
                if 'heartbeat_max' in config:
                    self.alert_config['heartbeat_max'] = config['heartbeat_max']
                if 'tremor_threshold' in config:
                    self.alert_config['tremor_threshold'] = config['tremor_threshold']
                if 'motion_spike_threshold' in config:
                    self.alert_config['motion_spike_threshold'] = config['motion_spike_threshold']
                
                return jsonify({
                    'status': 'updated',
                    'config': self.alert_config
                })
            else:
                return jsonify(self.alert_config)
        
        # ========== NATURAL LANGUAGE QUERIES ==========
        
        @self.app.route('/api/query/heart_rate', methods=['GET'])
        def query_heart_rate():
            """Natural language heart rate query"""
            response = self.atlas_query.get_current_heart_rate()
            return jsonify({'response': response})
        
        @self.app.route('/api/query/tremors', methods=['GET'])
        def query_tremors():
            """Natural language tremor query"""
            hours = request.args.get('hours', default=24, type=int)
            response = self.atlas_query.check_for_tremors(last_hours=hours)
            return jsonify({'response': response})
        
        @self.app.route('/api/query/summary', methods=['GET'])
        def query_summary():
            """Natural language health summary"""
            hours = request.args.get('hours', default=24, type=int)
            response = self.atlas_query.health_summary(hours=hours)
            return jsonify({'response': response})
        
        # ========== SYSTEM CONTROL ==========
        
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
                    
                    # Initialize frequency analyzer
                    self.analyzer = FrequencyAnalyzer(
                        sample_rate=30.0,
                        window_size=300,
                        min_confidence=1.5
                    )
                    
                    self.running = True
                    
                    # Start processing thread
                    Thread(target=self._process_loop, daemon=True).start()
                    
                    return jsonify({
                        'status': 'started',
                        'algorithm': algorithm,
                        'camera': self.camera_index,
                        'database': self.db_path
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
                self.analyzer = None
                self.current_data = None
                
                return jsonify({'status': 'stopped'})
    
    def _process_loop(self):
        """Background processing loop with event logging"""
        while self.running:
            try:
                motion_data = self.extractor.process_frame()
                if motion_data is None:
                    break
                
                # Add motion intensity to frequency analyzer
                if self.analyzer:
                    self.analyzer.add_sample(
                        motion_data['intensity'],
                        motion_data['timestamp']
                    )
                
                with self.lock:
                    self.current_data = motion_data
                
                # Periodic heartbeat detection and logging
                current_time = time.time()
                if current_time - self.last_heartbeat_log >= self.heartbeat_log_interval:
                    self._log_heartbeat()
                    self.last_heartbeat_log = current_time
                
                # Log tremor detections (when confidence > threshold)
                self._log_tremor()
                
                # Log motion spikes
                self._log_motion_spikes(motion_data)
            
            except Exception as e:
                print(f"Error in processing loop: {e}")
                break
        
        # Cleanup on exit
        with self.lock:
            if self.extractor:
                self.extractor.release()
            self.running = False
    
    def _log_heartbeat(self):
        """Detect and log heartbeat"""
        if not self.analyzer:
            return
        
        result = self.analyzer.detect_heartbeat()
        
        if result['detected'] and result['bpm']:
            self.event_store.log_event(
                'heartbeat',
                value=result['bpm'],
                confidence=result['confidence'],
                metadata={
                    'frequency_hz': result['frequency_hz'],
                    'buffer_fill': result['buffer_fill']
                }
            )
    
    def _log_tremor(self):
        """Detect and log tremor"""
        if not self.analyzer:
            return
        
        result = self.analyzer.detect_tremor()
        
        if result['detected'] and result['confidence'] >= self.alert_config['tremor_threshold']:
            self.event_store.log_event(
                'tremor',
                value=result['frequency_hz'],
                confidence=result['confidence'],
                metadata={
                    'buffer_fill': result['buffer_fill']
                }
            )
    
    def _log_motion_spikes(self, motion_data: Dict):
        """Log unusual motion spikes"""
        intensity = motion_data['intensity']
        
        # Log if intensity exceeds threshold
        if intensity >= self.alert_config['motion_spike_threshold']:
            self.event_store.log_event(
                'motion_spike',
                value=intensity,
                metadata={
                    'num_regions': motion_data.get('num_regions', 0),
                    'algorithm': self.extractor.algorithm if self.extractor else 'unknown'
                }
            )
    
    def run(self, debug: bool = False):
        """Start the API server"""
        print(f"🔥 Atlas Eyes API starting on port {self.port}")
        print(f"Camera: {self.camera_index}")
        print(f"Database: {self.db_path}")
        print()
        print("API Endpoints:")
        print("  System:")
        print("    GET  /api/status           - System status")
        print("    POST /api/start            - Start extraction")
        print("    POST /api/stop             - Stop extraction")
        print()
        print("  Heartbeat:")
        print("    GET  /api/heartbeat/current         - Latest BPM")
        print("    GET  /api/heartbeat/history?hours=24 - Time series data")
        print()
        print("  Tremor:")
        print("    GET  /api/tremor/events?hours=24    - Tremor log")
        print()
        print("  Health:")
        print("    GET  /api/health/summary?hours=24   - Overall stats")
        print("    GET  /api/health/check?hours=1      - Quick check")
        print()
        print("  Alerts:")
        print("    GET  /api/alert/config              - Get thresholds")
        print("    POST /api/alert/config              - Set thresholds")
        print()
        print("  Natural Language:")
        print("    GET  /api/query/heart_rate          - 'What's my heart rate?'")
        print("    GET  /api/query/tremors?hours=24    - 'Any tremors?'")
        print("    GET  /api/query/summary?hours=24    - 'Health summary'")
        print()
        
        try:
            self.app.run(host='127.0.0.1', port=self.port, debug=debug, use_reloader=False)
        finally:
            # Cleanup
            if self.event_store:
                self.event_store.close()


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Atlas Eyes API Server (Enhanced)')
    parser.add_argument('--port', type=int, default=5000, help='API port')
    parser.add_argument('--camera', type=int, default=0, help='Camera index')
    parser.add_argument('--db', type=str, default='motion_events.db', help='Database path')
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    
    args = parser.parse_args()
    
    api = AtlasEyesAPI(port=args.port, camera_index=args.camera, db_path=args.db)
    api.run(debug=args.debug)


if __name__ == '__main__':
    main()
