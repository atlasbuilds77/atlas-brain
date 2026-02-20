#!/usr/bin/env python3
"""
TITAN Sweep Alert - Real-time sweep detection during market hours

Built during autonomous exploration session 2026-02-14 03:45 PST

Monitors SPY/QQQ for:
1. Sweep of premarket high/low
2. Reclaim (bounce back through level)
3. Sends alert when setup triggers

Usage: python3 titan_sweep_alert.py
       python3 titan_sweep_alert.py --test  # Test with sample data
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Optional
import argparse

# API Keys
TRADIER_TOKEN = 'jj8L3RuSVG5MUwUpz2XHrjXjAFrq'
POLYGON_KEY = 'h7J74V1cd8_4NQpTxwQpudpqXWaIHMhv'

# Telegram alert config (optional)
TELEGRAM_BOT_TOKEN = None  # Set if you want Telegram alerts
TELEGRAM_CHAT_ID = None

class TitanSweepMonitor:
    def __init__(self, symbols: list = ['SPY', 'QQQ']):
        self.symbols = symbols
        self.levels = {}  # {symbol: {'pm_high': x, 'pm_low': x}}
        self.state = {}   # {symbol: {'last_price': x, 'swept_high': bool, 'swept_low': bool}}
        self.alerts_sent = set()  # Prevent duplicate alerts
        
    def get_premarket_levels(self, symbol: str) -> dict:
        """Fetch today's premarket high/low"""
        today = datetime.now().strftime('%Y-%m-%d')
        url = f'https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{today}/{today}'
        params = {'apiKey': POLYGON_KEY, 'limit': 50000}
        
        try:
            r = requests.get(url, params=params, timeout=10)
            data = r.json()
            
            if 'results' not in data or not data['results']:
                return None
            
            # Filter premarket bars (before 9:30 ET)
            pm_bars = []
            for m in data['results']:
                ts = datetime.fromtimestamp(m['t'] / 1000)
                if ts.hour < 9 or (ts.hour == 9 and ts.minute < 30):
                    pm_bars.append(m)
            
            if not pm_bars:
                return None
            
            return {
                'pm_high': max(b['h'] for b in pm_bars),
                'pm_low': min(b['l'] for b in pm_bars)
            }
        except Exception as e:
            print(f"Error fetching premarket for {symbol}: {e}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price from Tradier"""
        url = 'https://api.tradier.com/v1/markets/quotes'
        headers = {'Authorization': f'Bearer {TRADIER_TOKEN}', 'Accept': 'application/json'}
        params = {'symbols': symbol}
        
        try:
            r = requests.get(url, headers=headers, params=params, timeout=5)
            data = r.json()
            
            if 'quotes' in data and 'quote' in data['quotes']:
                quote = data['quotes']['quote']
                return quote.get('last', quote.get('close'))
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
        
        return None
    
    def check_sweep(self, symbol: str, price: float) -> Optional[dict]:
        """Check if price swept a level and generate alert"""
        if symbol not in self.levels:
            return None
        
        levels = self.levels[symbol]
        state = self.state.get(symbol, {
            'swept_high': False, 'swept_low': False,
            'high_sweep_time': None, 'low_sweep_time': None,
            'high_sweep_count': 0, 'low_sweep_count': 0
        })
        
        pm_high = levels['pm_high']
        pm_low = levels['pm_low']
        
        alert = None
        now = datetime.now()
        
        # Check PM HIGH sweep
        if price > pm_high and not state['swept_high']:
            state['swept_high'] = True
            state['high_sweep_time'] = now
            state['high_sweep_count'] = 1
            print(f"🔺 {symbol} SWEPT PM HIGH ${pm_high:.2f}! Current: ${price:.2f}")
        
        # Check PM HIGH reclaim (rejection) - price back below
        elif state['swept_high'] and price < pm_high:
            # Check if this is within 15 min of first sweep
            if state['high_sweep_time']:
                mins_since = (now - state['high_sweep_time']).seconds / 60
                if mins_since < 15:
                    alert_key = f"{symbol}_short_{now.strftime('%Y%m%d')}"
                    if alert_key not in self.alerts_sent:
                        alert = {
                            'symbol': symbol,
                            'direction': 'SHORT',
                            'entry': price,
                            'level_swept': pm_high,
                            'target': pm_low,
                            'message': f"🔻 {symbol} SHORT SETUP! Swept PM high ${pm_high:.2f}, rejected back to ${price:.2f}. Target: ${pm_low:.2f}"
                        }
                        self.alerts_sent.add(alert_key)
            state['swept_high'] = False
        
        # Check PM LOW sweep
        if price < pm_low and not state['swept_low']:
            state['swept_low'] = True
            state['low_sweep_time'] = now
            state['low_sweep_count'] = 1
            print(f"🔻 {symbol} SWEPT PM LOW ${pm_low:.2f}! Current: ${price:.2f}")
        
        # Check PM LOW reclaim (bounce) - price back above
        elif state['swept_low'] and price > pm_low:
            # Check if this is within 15 min of first sweep
            if state['low_sweep_time']:
                mins_since = (now - state['low_sweep_time']).seconds / 60
                if mins_since < 15:
                    alert_key = f"{symbol}_long_{now.strftime('%Y%m%d')}"
                    if alert_key not in self.alerts_sent:
                        alert = {
                            'symbol': symbol,
                            'direction': 'LONG',
                            'entry': price,
                            'level_swept': pm_low,
                            'target': pm_high,
                            'message': f"🔺 {symbol} LONG SETUP! Swept PM low ${pm_low:.2f}, reclaimed to ${price:.2f}. Target: ${pm_high:.2f}"
                        }
                        self.alerts_sent.add(alert_key)
            state['swept_low'] = False
        
        # Track multiple sweeps (absorption filter)
        if state['swept_high'] and price > pm_high:
            if state['high_sweep_time'] and (now - state['high_sweep_time']).seconds > 60:
                state['high_sweep_count'] += 1
                state['high_sweep_time'] = now
                if state['high_sweep_count'] >= 2:
                    print(f"⚠️ {symbol} Multiple sweeps of PM high ({state['high_sweep_count']}x) - ABSORPTION, skip short")
        
        if state['swept_low'] and price < pm_low:
            if state['low_sweep_time'] and (now - state['low_sweep_time']).seconds > 60:
                state['low_sweep_count'] += 1
                state['low_sweep_time'] = now
                if state['low_sweep_count'] >= 2:
                    print(f"⚠️ {symbol} Multiple sweeps of PM low ({state['low_sweep_count']}x) - ABSORPTION, skip long")
        
        self.state[symbol] = state
        return alert
    
    def send_alert(self, alert: dict):
        """Send alert via console (and optionally Telegram)"""
        print("\n" + "=" * 60)
        print("🚨 TITAN V3 ALERT")
        print("=" * 60)
        print(alert['message'])
        print(f"   Entry: ${alert['entry']:.2f}")
        print(f"   Target: ${alert['target']:.2f}")
        print("=" * 60 + "\n")
        
        # TODO: Add Telegram notification
        # TODO: Add Discord webhook
        # TODO: Add iMessage via OpenClaw
    
    def initialize(self):
        """Load premarket levels for all symbols"""
        print("\n🌅 Initializing TITAN Sweep Monitor...")
        
        for symbol in self.symbols:
            levels = self.get_premarket_levels(symbol)
            if levels:
                self.levels[symbol] = levels
                print(f"   {symbol}: PM High ${levels['pm_high']:.2f} | PM Low ${levels['pm_low']:.2f}")
            else:
                print(f"   {symbol}: ⚠️ No premarket data yet")
        
        if not self.levels:
            print("\n❌ No premarket data available. Run after 4am ET or during market hours.")
            return False
        
        print("\n✅ Monitor initialized. Watching for sweeps...")
        return True
    
    def run(self, interval: int = 10):
        """Main monitoring loop"""
        if not self.initialize():
            return
        
        print(f"   Polling every {interval} seconds. Press Ctrl+C to stop.\n")
        
        try:
            while True:
                for symbol in self.symbols:
                    if symbol not in self.levels:
                        continue
                    
                    price = self.get_current_price(symbol)
                    if price:
                        alert = self.check_sweep(symbol, price)
                        if alert:
                            self.send_alert(alert)
                
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n\n👋 Monitor stopped.")

def test_mode():
    """Test with simulated price action"""
    print("\n🧪 TEST MODE - Simulating Feb 13 price action\n")
    
    monitor = TitanSweepMonitor(['SPY'])
    
    # Set fake premarket levels
    monitor.levels['SPY'] = {'pm_high': 680.00, 'pm_low': 678.50}
    print(f"PM Levels: High ${680.00:.2f} | Low ${678.50:.2f}")
    
    # Simulate price action
    prices = [
        (679.50, "Market open - mid range"),
        (680.10, "Touch PM high"),
        (679.80, "Slight pullback"),
        (680.25, "SWEEP PM high"),
        (679.60, "Rejection! Back below"),  # Should trigger SHORT alert
        (678.40, "Continues down"),
        (678.20, "SWEEP PM low"),
        (678.70, "Bounce back"),  # Should trigger LONG alert
    ]
    
    print("\nSimulated price action:")
    print("-" * 40)
    
    for price, desc in prices:
        print(f"  ${price:.2f} - {desc}")
        alert = monitor.check_sweep('SPY', price)
        if alert:
            print(f"\n  🚨 ALERT: {alert['message']}\n")
        time.sleep(0.5)
    
    print("\n✅ Test complete")

def main():
    parser = argparse.ArgumentParser(description='TITAN Sweep Alert Monitor')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    parser.add_argument('--interval', type=int, default=10, help='Polling interval in seconds')
    args = parser.parse_args()
    
    if args.test:
        test_mode()
    else:
        monitor = TitanSweepMonitor(['SPY', 'QQQ'])
        monitor.run(interval=args.interval)

if __name__ == '__main__':
    main()
