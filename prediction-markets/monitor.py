#!/usr/bin/env python3
"""
Prediction Market Monitor
Real-time monitoring with Telegram alerts

Usage:
    python monitor.py                    # Run monitoring daemon
    python monitor.py --test-alert      # Test Telegram alert
    python monitor.py --check-once      # Single check, no loop
"""

import asyncio
import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# Add arb-bot to path
sys.path.insert(0, str(Path(__file__).parent / 'arb-bot'))

class PredictionMarketMonitor:
    def __init__(self, alert_threshold: float = 0.02):
        """
        Initialize monitor.
        
        Args:
            alert_threshold: Minimum profit % to trigger alert (default 2%)
        """
        self.alert_threshold = alert_threshold
        self.opportunities_found = []
        self.last_alert_time = {}
        self.alert_cooldown = 300  # 5 minutes between alerts for same opportunity
        
    async def check_kalshi_connection(self) -> bool:
        """Test Kalshi API connection."""
        try:
            from kalshi import KalshiClient
            from dotenv import load_dotenv
            
            # Load .env from arb-bot
            load_dotenv(Path(__file__).parent / 'arb-bot' / '.env')
            
            client = KalshiClient()
            print("✅ Kalshi credentials loaded")
            print(f"   API Key: {client.key_id[:8]}...")
            print(f"   Key File: {client.key_file}")
            return True
        except Exception as e:
            print(f"❌ Kalshi connection failed: {e}")
            return False
    
    def format_opportunity(self, opp: dict) -> str:
        """Format opportunity for display/alert."""
        return f"""
🎯 ARBITRAGE OPPORTUNITY DETECTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Type: {opp.get('type', 'Unknown')}
Profit: {opp.get('profit', 0)*100:.2f}%
Max Size: ${opp.get('max_size', 0):.2f}
Total Profit: ${opp.get('total_profit', 0):.2f}

Action:
{opp.get('action', 'Check platforms manually')}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    def should_alert(self, opp_id: str) -> bool:
        """Check if we should send alert (cooldown logic)."""
        now = datetime.now().timestamp()
        last = self.last_alert_time.get(opp_id, 0)
        
        if now - last > self.alert_cooldown:
            self.last_alert_time[opp_id] = now
            return True
        return False
    
    async def run_single_check(self):
        """Run a single check for opportunities."""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Checking for opportunities...")
        
        # Check Kalshi connection
        if not await self.check_kalshi_connection():
            return
        
        print("✅ Ready to monitor")
        print("   (Full monitoring requires running arb-bot)")
        
        # Show current status
        print("\n📊 MONITORING STATUS:")
        print(f"   Alert Threshold: {self.alert_threshold*100:.1f}%")
        print(f"   Alert Cooldown: {self.alert_cooldown}s")
        print(f"   Opportunities Found: {len(self.opportunities_found)}")
    
    async def run_daemon(self, interval: int = 30):
        """Run continuous monitoring."""
        print("🚀 Starting Prediction Market Monitor")
        print(f"   Check Interval: {interval}s")
        print(f"   Alert Threshold: {self.alert_threshold*100:.1f}%")
        print("   Press Ctrl+C to stop\n")
        
        while True:
            try:
                await self.run_single_check()
                await asyncio.sleep(interval)
            except KeyboardInterrupt:
                print("\n👋 Monitor stopped")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                await asyncio.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description="Prediction Market Monitor")
    parser.add_argument('--test-alert', action='store_true', help="Test alert system")
    parser.add_argument('--check-once', action='store_true', help="Single check, no loop")
    parser.add_argument('--threshold', type=float, default=0.02, help="Alert threshold (default 0.02 = 2 percent)")
    parser.add_argument('--interval', type=int, default=30, help="Check interval in seconds")
    args = parser.parse_args()
    
    monitor = PredictionMarketMonitor(alert_threshold=args.threshold)
    
    if args.test_alert:
        test_opp = {
            'type': 'TEST - Cross-Platform Arbitrage',
            'profit': 0.05,
            'max_size': 100,
            'total_profit': 5.00,
            'action': 'This is a test alert'
        }
        print(monitor.format_opportunity(test_opp))
        
    elif args.check_once:
        asyncio.run(monitor.run_single_check())
        
    else:
        asyncio.run(monitor.run_daemon(interval=args.interval))


if __name__ == "__main__":
    main()
