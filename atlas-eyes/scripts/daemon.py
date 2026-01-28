#!/usr/bin/env python3
"""
Atlas Eyes Daemon
Background service for continuous health monitoring
Runs headless (no GUI), logs to database, exposes API
"""

import sys
import os
import signal
import time
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from atlas_api_enhanced import AtlasEyesAPI
import logging


class AtlasEyesDaemon:
    """
    Daemon wrapper for Atlas Eyes
    Handles startup, shutdown, and signal handling
    """
    
    def __init__(
        self,
        port: int = 5000,
        camera: int = 0,
        db_path: str = None,
        log_file: str = None,
        auto_start: bool = True
    ):
        """
        Initialize daemon
        
        Args:
            port: API server port
            camera: Camera index
            db_path: Database path (default: ~/atlas-eyes-data/motion_events.db)
            log_file: Log file path (default: ~/atlas-eyes-data/daemon.log)
            auto_start: Automatically start monitoring on launch
        """
        self.port = port
        self.camera = camera
        self.auto_start = auto_start
        
        # Setup data directory
        data_dir = Path.home() / 'atlas-eyes-data'
        data_dir.mkdir(exist_ok=True)
        
        # Database path
        if db_path is None:
            self.db_path = str(data_dir / 'motion_events.db')
        else:
            self.db_path = db_path
        
        # Log file
        if log_file is None:
            self.log_file = str(data_dir / 'daemon.log')
        else:
            self.log_file = log_file
        
        # Setup logging
        self._setup_logging()
        
        # API instance
        self.api = None
        self.running = False
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _setup_logging(self):
        """Configure logging to file"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('atlas_eyes_daemon')
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)
    
    def start(self):
        """Start the daemon"""
        self.logger.info("=" * 60)
        self.logger.info("Atlas Eyes Daemon Starting")
        self.logger.info("=" * 60)
        self.logger.info(f"Port: {self.port}")
        self.logger.info(f"Camera: {self.camera}")
        self.logger.info(f"Database: {self.db_path}")
        self.logger.info(f"Log file: {self.log_file}")
        self.logger.info(f"Auto-start monitoring: {self.auto_start}")
        self.logger.info("")
        
        try:
            # Create API instance
            self.api = AtlasEyesAPI(
                port=self.port,
                camera_index=self.camera,
                db_path=self.db_path
            )
            
            # Auto-start monitoring if enabled
            if self.auto_start:
                self.logger.info("Auto-starting motion extraction...")
                self._auto_start_monitoring()
            
            self.running = True
            
            # Run API server (blocking)
            self.logger.info("Starting API server...")
            self.api.run(debug=False)
            
        except Exception as e:
            self.logger.error(f"Error starting daemon: {e}", exc_info=True)
            self.stop()
            sys.exit(1)
    
    def _auto_start_monitoring(self):
        """Auto-start the monitoring system"""
        import requests
        
        # Wait a moment for API to be ready
        time.sleep(1)
        
        try:
            # Start extraction via API
            response = requests.post(
                f'http://127.0.0.1:{self.port}/api/start',
                json={'algorithm': 'frame_diff'},
                timeout=5
            )
            
            if response.status_code == 200:
                self.logger.info("✓ Monitoring started successfully")
            else:
                self.logger.warning(f"Failed to auto-start monitoring: {response.text}")
        
        except Exception as e:
            self.logger.warning(f"Could not auto-start monitoring: {e}")
    
    def stop(self):
        """Stop the daemon"""
        if not self.running:
            return
        
        self.logger.info("Stopping daemon...")
        
        if self.api and self.api.event_store:
            self.logger.info("Closing event database...")
            self.api.event_store.close()
        
        self.running = False
        self.logger.info("Daemon stopped")
    
    def status(self):
        """Print daemon status"""
        import requests
        
        try:
            response = requests.get(f'http://127.0.0.1:{self.port}/api/status', timeout=2)
            
            if response.status_code == 200:
                status = response.json()
                print("Daemon Status: Running ✓")
                print(f"  System: {status['status']}")
                print(f"  Camera: {self.camera}")
                print(f"  Database: {self.db_path}")
                if 'stats' in status:
                    print(f"  FPS: {status['stats'].get('fps', 0):.1f}")
                    print(f"  Frames: {status['stats'].get('frame_count', 0)}")
            else:
                print("Daemon Status: Error")
                print(f"  {response.text}")
        
        except requests.ConnectionError:
            print("Daemon Status: Not running ✗")
        except Exception as e:
            print(f"Daemon Status: Unknown ({e})")


def create_launchd_plist(port: int = 5000, camera: int = 0, db_path: str = None):
    """
    Create macOS LaunchDaemon plist for auto-start on boot
    
    Args:
        port: API port
        camera: Camera index
        db_path: Database path
    """
    data_dir = Path.home() / 'atlas-eyes-data'
    data_dir.mkdir(exist_ok=True)
    
    if db_path is None:
        db_path = str(data_dir / 'motion_events.db')
    
    daemon_script = Path(__file__).resolve()
    python_path = sys.executable
    
    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.atlas.eyes.daemon</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>{python_path}</string>
        <string>{daemon_script}</string>
        <string>--port</string>
        <string>{port}</string>
        <string>--camera</string>
        <string>{camera}</string>
        <string>--db</string>
        <string>{db_path}</string>
        <string>--auto-start</string>
    </array>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>{data_dir}/stdout.log</string>
    
    <key>StandardErrorPath</key>
    <string>{data_dir}/stderr.log</string>
    
    <key>WorkingDirectory</key>
    <string>{daemon_script.parent.parent}</string>
</dict>
</plist>
"""
    
    plist_path = Path.home() / 'Library' / 'LaunchAgents' / 'com.atlas.eyes.daemon.plist'
    plist_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(plist_path, 'w') as f:
        f.write(plist_content)
    
    print(f"✓ Created LaunchAgent plist: {plist_path}")
    print()
    print("To enable auto-start on boot:")
    print(f"  launchctl load {plist_path}")
    print()
    print("To start now:")
    print(f"  launchctl start com.atlas.eyes.daemon")
    print()
    print("To stop:")
    print(f"  launchctl stop com.atlas.eyes.daemon")
    print()
    print("To disable auto-start:")
    print(f"  launchctl unload {plist_path}")


def create_systemd_service(port: int = 5000, camera: int = 0, db_path: str = None):
    """
    Create systemd service file for Linux auto-start
    
    Args:
        port: API port
        camera: Camera index
        db_path: Database path
    """
    data_dir = Path.home() / 'atlas-eyes-data'
    data_dir.mkdir(exist_ok=True)
    
    if db_path is None:
        db_path = str(data_dir / 'motion_events.db')
    
    daemon_script = Path(__file__).resolve()
    python_path = sys.executable
    
    service_content = f"""[Unit]
Description=Atlas Eyes Health Monitoring Daemon
After=network.target

[Service]
Type=simple
User={os.getlogin()}
WorkingDirectory={daemon_script.parent.parent}
ExecStart={python_path} {daemon_script} --port {port} --camera {camera} --db {db_path} --auto-start
Restart=on-failure
RestartSec=10
StandardOutput=append:{data_dir}/stdout.log
StandardError=append:{data_dir}/stderr.log

[Install]
WantedBy=multi-user.target
"""
    
    service_path = Path.home() / '.config' / 'systemd' / 'user' / 'atlas-eyes.service'
    service_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(service_path, 'w') as f:
        f.write(service_content)
    
    print(f"✓ Created systemd service: {service_path}")
    print()
    print("To enable auto-start on boot:")
    print(f"  systemctl --user enable atlas-eyes.service")
    print()
    print("To start now:")
    print(f"  systemctl --user start atlas-eyes.service")
    print()
    print("To stop:")
    print(f"  systemctl --user stop atlas-eyes.service")
    print()
    print("To check status:")
    print(f"  systemctl --user status atlas-eyes.service")


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Atlas Eyes Daemon - Background Health Monitoring',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start daemon
  %(prog)s
  
  # Start on custom port
  %(prog)s --port 8080
  
  # Start without auto-monitoring (manual start via API)
  %(prog)s --no-auto-start
  
  # Check status
  %(prog)s --status
  
  # Create auto-start service
  %(prog)s --install
        """
    )
    
    parser.add_argument('--port', type=int, default=5000, help='API server port (default: 5000)')
    parser.add_argument('--camera', type=int, default=0, help='Camera index (default: 0)')
    parser.add_argument('--db', type=str, help='Database path (default: ~/atlas-eyes-data/motion_events.db)')
    parser.add_argument('--log', type=str, help='Log file path (default: ~/atlas-eyes-data/daemon.log)')
    parser.add_argument('--auto-start', dest='auto_start', action='store_true', default=True, help='Auto-start monitoring (default)')
    parser.add_argument('--no-auto-start', dest='auto_start', action='store_false', help='Don\'t auto-start monitoring')
    parser.add_argument('--status', action='store_true', help='Check daemon status and exit')
    parser.add_argument('--install', action='store_true', help='Create auto-start service and exit')
    
    args = parser.parse_args()
    
    # Handle special commands
    if args.status:
        daemon = AtlasEyesDaemon(port=args.port, camera=args.camera)
        daemon.status()
        return
    
    if args.install:
        import platform
        
        if platform.system() == 'Darwin':
            create_launchd_plist(port=args.port, camera=args.camera, db_path=args.db)
        elif platform.system() == 'Linux':
            create_systemd_service(port=args.port, camera=args.camera, db_path=args.db)
        else:
            print(f"Auto-start not supported on {platform.system()}")
        return
    
    # Start daemon
    daemon = AtlasEyesDaemon(
        port=args.port,
        camera=args.camera,
        db_path=args.db,
        log_file=args.log,
        auto_start=args.auto_start
    )
    
    daemon.start()


if __name__ == '__main__':
    main()
