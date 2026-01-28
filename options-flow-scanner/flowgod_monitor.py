#!/usr/bin/env python3
"""
Flow God Exit Monitor
Tracks Flow God's posts for whale exit alerts
Alerts when whales close positions at loss
"""
import subprocess
import json
import re
from datetime import datetime
from typing import List, Dict, Optional

class FlowGodMonitor:
    """Monitor Flow God's Twitter for whale exits"""
    
    def __init__(self, tracked_positions: Dict[str, Dict]):
        """
        tracked_positions format:
        {
            'SLV': {
                'our_entry': 4.80,
                'our_size': 3,
                'whale_entry': 8.25,
                'whale_size': 10015,
                'whale_premium': 8262047,
                'entry_time': '2026-01-27T09:30:00'
            }
        }
        """
        self.tracked_positions = tracked_positions
        self.exit_alerts = []
        
    def fetch_flowgod_tweets(self, limit: int = 20) -> List[Dict]:
        """Fetch recent Flow God tweets using bird CLI"""
        try:
            result = subprocess.run(
                ['bird', 'search', 'from:fl0wg0d', '-n', str(limit), '--json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                tweets = json.loads(result.stdout)
                return tweets
            else:
                print(f"Error fetching tweets: {result.stderr}")
                return []
                
        except Exception as e:
            print(f"Error running bird CLI: {e}")
            return []
    
    def is_exit_post(self, tweet_text: str) -> bool:
        """Check if tweet is about whale closing position"""
        exit_phrases = [
            'closed out',
            'just closed',
            'exited',
            'took profit',
            'cut loss',
            'stopped out'
        ]
        
        text_lower = tweet_text.lower()
        return any(phrase in text_lower for phrase in exit_phrases)
    
    def extract_ticker(self, tweet_text: str) -> Optional[str]:
        """Extract ticker from tweet"""
        # Flow God format: "$TICKER - ..."
        match = re.search(r'\$([A-Z]{1,5})', tweet_text)
        if match:
            return match.group(1)
        return None
    
    def check_for_exits(self) -> List[Dict]:
        """Check Flow God's recent posts for exit alerts"""
        tweets = self.fetch_flowgod_tweets()
        
        exit_alerts = []
        
        for tweet in tweets:
            text = tweet.get('text', '')
            
            if not self.is_exit_post(text):
                continue
            
            ticker = self.extract_ticker(text)
            if not ticker:
                continue
            
            # Check if this is a position we're tracking
            if ticker in self.tracked_positions:
                alert = {
                    'ticker': ticker,
                    'tweet_text': text,
                    'tweet_time': tweet.get('createdAt'),
                    'tweet_id': tweet.get('id'),
                    'position': self.tracked_positions[ticker],
                    'alert_time': datetime.now().isoformat()
                }
                
                exit_alerts.append(alert)
                print(f"\n{'='*60}")
                print(f"🚨 WHALE EXIT ALERT - {ticker}")
                print(f"{'='*60}")
                print(f"Flow God: {text}")
                print(f"Posted: {tweet.get('createdAt')}")
                print(f"\nOUR POSITION:")
                print(f"  Entry: ${self.tracked_positions[ticker]['our_entry']}")
                print(f"  Size: {self.tracked_positions[ticker]['our_size']} contracts")
                print(f"\nWHALE POSITION:")
                print(f"  Entry: ${self.tracked_positions[ticker]['whale_entry']}")
                print(f"  Size: {self.tracked_positions[ticker]['whale_size']} contracts")
                print(f"  Premium: ${self.tracked_positions[ticker]['whale_premium']:,}")
                print(f"\n⚠️  ACTION: Consider exiting immediately")
                print(f"{'='*60}\n")
        
        self.exit_alerts.extend(exit_alerts)
        return exit_alerts
    
    def add_position(self, ticker: str, position_data: Dict):
        """Add a new position to track"""
        self.tracked_positions[ticker] = position_data
        print(f"✅ Now tracking {ticker} for whale exits")
    
    def remove_position(self, ticker: str):
        """Remove position from tracking"""
        if ticker in self.tracked_positions:
            del self.tracked_positions[ticker]
            print(f"✅ Stopped tracking {ticker}")
    
    def save_tracked_positions(self, filepath: str = 'tracked_positions.json'):
        """Save tracked positions to file"""
        with open(filepath, 'w') as f:
            json.dump(self.tracked_positions, f, indent=2)
    
    def load_tracked_positions(self, filepath: str = 'tracked_positions.json'):
        """Load tracked positions from file"""
        try:
            with open(filepath, 'r') as f:
                self.tracked_positions = json.load(f)
                print(f"✅ Loaded {len(self.tracked_positions)} tracked positions")
        except FileNotFoundError:
            print(f"No saved positions found at {filepath}")

def main():
    """Example usage"""
    
    # Current positions to track
    tracked = {
        'SLV': {
            'our_entry': 4.80,
            'our_size': 3,
            'our_contracts': 3,
            'whale_entry': 8.25,
            'whale_size': 10015,
            'whale_premium': 8262047,
            'entry_time': '2026-01-27T09:30:00',
            'strike': 105,
            'expiration': '2026-02-06',
            'option_type': 'call'
        }
    }
    
    monitor = FlowGodMonitor(tracked)
    
    print("🔍 Checking Flow God for whale exits...\n")
    exits = monitor.check_for_exits()
    
    if exits:
        print(f"\n🚨 Found {len(exits)} exit alert(s)")
    else:
        print("\n✅ No whale exits detected for tracked positions")

if __name__ == '__main__':
    main()
