#!/usr/bin/env python3
"""
Real-Time SPX Options Flow Scanner
Continuously monitors and alerts on unusual options activity
"""
import time
import json
import argparse
from datetime import datetime
from typing import List, Dict
from flow_scanner import FlowScanner, OptionsFlow
from api_adapters import get_adapter

class LiveFlowScanner:
    """Real-time options flow monitoring"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.scanner = FlowScanner(config)
        self.api_adapter = get_adapter(
            config['api_name'],
            config['api_key'],
            config.get('api_config', {})
        )
        self.tickers = config.get('tickers', ['SPX', 'SPY'])
        self.poll_interval = config.get('poll_interval', 10)  # seconds
        self.seen_flows = set()  # Track already alerted flows
        
    def deduplicate_flow(self, flow: OptionsFlow) -> bool:
        """Check if we've already alerted on this flow"""
        flow_id = f"{flow.ticker}_{flow.strike}_{flow.expiration}_{flow.timestamp.isoformat()}"
        
        if flow_id in self.seen_flows:
            return True  # Already seen
        
        self.seen_flows.add(flow_id)
        
        # Cleanup old flows (older than 1 hour)
        hour_ago = datetime.now().timestamp() - 3600
        self.seen_flows = {
            fid for fid in self.seen_flows 
            if float(fid.split('_')[-1].split('T')[-1].split(':')[0]) > hour_ago
        }
        
        return False
    
    def run(self):
        """Main monitoring loop"""
        print(f"\n{'='*60}")
        print(f"SPX Options Flow Scanner - LIVE")
        print(f"{'='*60}")
        print(f"API: {self.config['api_name']}")
        print(f"Tickers: {', '.join(self.tickers)}")
        print(f"Poll interval: {self.poll_interval}s")
        print(f"Min premium: ${self.scanner.thresholds['spx_min_premium']:,}")
        print(f"{'='*60}\n")
        
        print(f"🟢 Scanner started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Waiting for unusual flow...\n")
        
        try:
            while True:
                self.scan_once()
                time.sleep(self.poll_interval)
                
        except KeyboardInterrupt:
            print(f"\n\n🔴 Scanner stopped at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Total alerts generated: {len(self.scanner.alerts)}")
    
    def scan_once(self):
        """Single scan iteration"""
        try:
            # Fetch latest flow from API
            raw_flows = self.api_adapter.fetch_realtime_flow(self.tickers)
            
            if not raw_flows:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] No flows returned from API")
                return
            
            # Process each flow
            new_alerts = 0
            for flow_data in raw_flows:
                flow = self.scanner.process_flow(flow_data)
                
                if flow and not self.deduplicate_flow(flow):
                    self.scanner.alert(flow)
                    new_alerts += 1
                    
                    # Additional actions based on strength
                    if flow.strength.name in ['STRONG', 'EXTREME']:
                        self.send_urgent_alert(flow)
            
            if new_alerts == 0:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {len(raw_flows)} flows scanned, 0 alerts")
            
        except Exception as e:
            print(f"❌ Error during scan: {e}")
    
    def send_urgent_alert(self, flow: OptionsFlow):
        """Send high-priority alert for strong flow"""
        # Write to file for external monitoring
        alert_file = self.config.get('alert_file', '/tmp/flow_alerts.txt')
        
        try:
            with open(alert_file, 'a') as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"URGENT ALERT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Ticker: {flow.ticker}\n")
                f.write(f"Strike: ${flow.strike} {flow.option_type.upper()}\n")
                f.write(f"Premium: ${flow.total_premium:,.0f}\n")
                f.write(f"Strength: {flow.strength.name}\n")
                f.write(f"{'='*60}\n")
        except Exception as e:
            print(f"Failed to write alert file: {e}")
        
        # Could also: send Discord/Telegram notification, email, SMS, etc.

def load_config(config_file: str = None) -> Dict:
    """Load configuration from file or use defaults"""
    if config_file:
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
    
    # Default configuration
    return {
        'api_name': 'unusual_whales',  # or 'flowalgo', 'polygon', 'alpaca'
        'api_key': 'YOUR_API_KEY_HERE',
        'api_config': {},
        'tickers': ['SPX', 'SPY'],
        'poll_interval': 10,
        'thresholds': {
            'min_premium': 200_000,
            'spx_min_premium': 500_000,
        },
        'alert_file': '/tmp/flow_alerts.txt',
    }

def main():
    parser = argparse.ArgumentParser(description='SPX Options Flow Scanner')
    parser.add_argument('--config', help='Path to config file (JSON)')
    parser.add_argument('--api', help='API to use (unusual_whales, flowalgo, polygon, alpaca)')
    parser.add_argument('--key', help='API key')
    parser.add_argument('--tickers', help='Comma-separated tickers (default: SPX,SPY)')
    parser.add_argument('--interval', type=int, help='Poll interval in seconds (default: 10)')
    parser.add_argument('--test', action='store_true', help='Run in test mode with mock data')
    
    args = parser.parse_args()
    
    # Load config
    config = load_config(args.config)
    
    # Override with CLI args
    if args.api:
        config['api_name'] = args.api
    if args.key:
        config['api_key'] = args.key
    if args.tickers:
        config['tickers'] = args.tickers.split(',')
    if args.interval:
        config['poll_interval'] = args.interval
    
    if args.test:
        print("🧪 Running in TEST mode with mock data")
        config['api_name'] = 'test'
        # Would implement mock data source here
    
    # Validate API key
    if config['api_key'] == 'YOUR_API_KEY_HERE' and not args.test:
        print("❌ Error: No API key provided")
        print("Use --key YOUR_KEY or create config.json with api_key")
        return
    
    # Start scanner
    scanner = LiveFlowScanner(config)
    scanner.run()

if __name__ == '__main__':
    main()
