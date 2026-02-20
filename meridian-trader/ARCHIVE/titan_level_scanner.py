#!/usr/bin/env python3
"""
TITAN Session Level Scanner
Real-time monitoring of key session levels with option strike recommendations
"""

import sys
import time
import json
from datetime import datetime
import pytz
import argparse

from levels import LevelCalculator
from alerts import AlertManager, OptionStrikeCalculator


class SessionScanner:
    def __init__(self, polygon_key, tradier_token):
        self.level_calc = LevelCalculator(polygon_key)
        self.alert_mgr = AlertManager()
        self.option_calc = OptionStrikeCalculator(tradier_token)
        
        self.symbols = ['SPY', 'QQQ']
        self.levels = None
        self.threshold_pct = 0.2  # Alert when within 0.2% of level
        
    def pull_levels(self):
        """Pull and save session levels (run at 6:00 AM PST)"""
        print("\n" + "="*70)
        print("🔍 PULLING SESSION LEVELS")
        print("="*70)
        
        self.levels = self.level_calc.calculate_all_levels(self.symbols)
        self.level_calc.save_levels(self.levels)
        
        self.print_levels()
        return self.levels
    
    def load_levels(self):
        """Load previously calculated levels"""
        self.levels = self.level_calc.load_levels()
        if self.levels is None:
            print("⚠️  No levels found. Run with --pull-levels first.")
            return False
        return True
    
    def print_levels(self):
        """Print formatted level display"""
        if not self.levels:
            print("No levels to display")
            return
        
        et_tz = pytz.timezone('America/New_York')
        now = datetime.now(et_tz)
        
        print("\n" + "="*70)
        print(f"=== TITAN LEVELS - {now.strftime('%b %d, %Y')} ===")
        print("="*70)
        
        for symbol in self.symbols:
            data = self.levels.get(symbol, {})
            current = data.get('current_price')
            premarket = data.get('premarket', {})
            prior = data.get('prior_day', {})
            
            print(f"\n{symbol}:")
            if current:
                print(f"  Current:    ${current:.2f}")
            
            if premarket:
                pre_high = premarket.get('pre_high')
                pre_low = premarket.get('pre_low')
                if pre_high:
                    print(f"  Pre-High:   ${pre_high:.2f} @ {premarket.get('pre_high_time', 'N/A')}")
                if pre_low:
                    print(f"  Pre-Low:    ${pre_low:.2f} @ {premarket.get('pre_low_time', 'N/A')}")
            
            if prior:
                prior_high = prior.get('prior_high')
                prior_low = prior.get('prior_low')
                if prior_high:
                    print(f"  Prior High: ${prior_high:.2f} ({prior.get('prior_date', 'N/A')})")
                if prior_low:
                    print(f"  Prior Low:  ${prior_low:.2f} ({prior.get('prior_date', 'N/A')})")
        
        print("="*70)
    
    def scan_once(self):
        """Run a single scan cycle"""
        if not self.levels:
            if not self.load_levels():
                return
        
        et_tz = pytz.timezone('America/New_York')
        now = datetime.now(et_tz)
        
        print(f"\n[{now.strftime('%H:%M:%S')}] Scanning...")
        
        for symbol in self.symbols:
            # Get current price
            current_price = self.level_calc.get_current_price(symbol)
            if current_price is None:
                print(f"  {symbol}: Unable to fetch price")
                continue
            
            # Update current price in levels
            if symbol in self.levels:
                self.levels[symbol]['current_price'] = current_price
            
            print(f"  {symbol}: ${current_price:.2f}", end="")
            
            # Check all levels
            data = self.levels.get(symbol, {})
            premarket = data.get('premarket', {})
            prior = data.get('prior_day', {})
            
            alerts_triggered = []
            
            # Check pre-market high
            if premarket.get('pre_high'):
                if self.alert_mgr.check_level_proximity(
                    symbol, current_price, premarket['pre_high'], 'Pre-High', self.threshold_pct
                ):
                    alerts_triggered.append(('Pre-High', premarket['pre_high']))
            
            # Check pre-market low
            if premarket.get('pre_low'):
                if self.alert_mgr.check_level_proximity(
                    symbol, current_price, premarket['pre_low'], 'Pre-Low', self.threshold_pct
                ):
                    alerts_triggered.append(('Pre-Low', premarket['pre_low']))
            
            # Check prior high
            if prior.get('prior_high'):
                if self.alert_mgr.check_level_proximity(
                    symbol, current_price, prior['prior_high'], 'Prior-High', self.threshold_pct
                ):
                    alerts_triggered.append(('Prior-High', prior['prior_high']))
            
            # Check prior low
            if prior.get('prior_low'):
                if self.alert_mgr.check_level_proximity(
                    symbol, current_price, prior['prior_low'], 'Prior-Low', self.threshold_pct
                ):
                    alerts_triggered.append(('Prior-Low', prior['prior_low']))
            
            if alerts_triggered:
                print(" ⚠️  ALERT!")
                for level_type, level_price in alerts_triggered:
                    self.generate_trade_alert(symbol, level_type, level_price, current_price)
            else:
                print(" ✓")
    
    def generate_trade_alert(self, symbol, level_type, level_price, current_price):
        """Generate alert with option strike recommendation"""
        # Determine direction and target
        is_support = 'Low' in level_type
        
        if is_support:
            direction = 'Buy'
            # Target is next resistance level
            target = self.find_next_resistance(symbol, current_price)
            stop = f"Below ${level_price * 0.995:.2f}"
        else:
            direction = 'Sell'
            # Target is next support level
            target = self.find_next_support(symbol, current_price)
            stop = f"Above ${level_price * 1.005:.2f}"
        
        # Calculate option strike
        suggested_strike = None
        if target:
            strike_data = self.option_calc.calculate_strike(
                symbol, current_price, target, 'call' if is_support else 'put'
            )
            if strike_data:
                suggested_strike = strike_data['strike']
                
                # Enhanced alert with option details
                self.alert_mgr.create_alert(
                    symbol=symbol,
                    level_type=level_type,
                    level_price=level_price,
                    current_price=current_price,
                    suggested_strike=suggested_strike,
                    direction=direction,
                    target=target,
                    stop=stop
                )
                
                # Print option details
                print(f"\n    Option Details:")
                print(f"      Strike: ${strike_data['strike']}")
                print(f"      Bid/Ask: ${strike_data['bid']:.2f} / ${strike_data['ask']:.2f}")
                print(f"      Delta: {strike_data.get('delta', 'N/A')}")
                print(f"      Expiration: {strike_data['expiration']}")
                return
        
        # Fallback alert without option details
        self.alert_mgr.create_alert(
            symbol=symbol,
            level_type=level_type,
            level_price=level_price,
            current_price=current_price,
            direction=direction,
            target=target,
            stop=stop
        )
    
    def find_next_resistance(self, symbol, current_price):
        """Find next resistance level above current price"""
        if symbol not in self.levels:
            return None
        
        data = self.levels[symbol]
        premarket = data.get('premarket', {})
        prior = data.get('prior_day', {})
        
        resistance_levels = []
        
        if premarket.get('pre_high') and premarket['pre_high'] > current_price:
            resistance_levels.append(premarket['pre_high'])
        if prior.get('prior_high') and prior['prior_high'] > current_price:
            resistance_levels.append(prior['prior_high'])
        
        return min(resistance_levels) if resistance_levels else None
    
    def find_next_support(self, symbol, current_price):
        """Find next support level below current price"""
        if symbol not in self.levels:
            return None
        
        data = self.levels[symbol]
        premarket = data.get('premarket', {})
        prior = data.get('prior_day', {})
        
        support_levels = []
        
        if premarket.get('pre_low') and premarket['pre_low'] < current_price:
            support_levels.append(premarket['pre_low'])
        if prior.get('prior_low') and prior['prior_low'] < current_price:
            support_levels.append(prior['prior_low'])
        
        return max(support_levels) if support_levels else None
    
    def is_market_hours(self):
        """Check if currently in market hours (6:30 AM - 1:00 PM PST)"""
        pst_tz = pytz.timezone('America/Los_Angeles')
        now = datetime.now(pst_tz)
        
        # Skip weekends
        if now.weekday() >= 5:
            return False
        
        # Market hours: 6:30 AM - 1:00 PM PST (9:30 AM - 4:00 PM ET)
        market_start = now.replace(hour=6, minute=30, second=0, microsecond=0)
        market_end = now.replace(hour=13, minute=0, second=0, microsecond=0)
        
        return market_start <= now <= market_end
    
    def run_continuous(self, interval=60):
        """Run scanner continuously during market hours"""
        print("\n🚀 TITAN Session Scanner - RUNNING")
        print(f"Scan interval: {interval} seconds")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                if self.is_market_hours():
                    self.scan_once()
                else:
                    pst_tz = pytz.timezone('America/Los_Angeles')
                    now = datetime.now(pst_tz)
                    print(f"[{now.strftime('%H:%M:%S')}] Outside market hours. Waiting...")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n✓ Scanner stopped by user")
            print(f"Total alerts today: {len(self.alert_mgr.get_todays_alerts())}")


def main():
    parser = argparse.ArgumentParser(description='TITAN Session Level Scanner')
    parser.add_argument('--pull-levels', action='store_true', 
                       help='Pull and calculate session levels')
    parser.add_argument('--show-levels', action='store_true',
                       help='Display current levels')
    parser.add_argument('--scan-once', action='store_true',
                       help='Run a single scan')
    parser.add_argument('--continuous', action='store_true',
                       help='Run continuous scanning')
    parser.add_argument('--interval', type=int, default=60,
                       help='Scan interval in seconds (default: 60)')
    
    args = parser.parse_args()
    
    # API credentials
    POLYGON_KEY = 'h7J74V1cd8_4NQpTxwQpudpqXWaIHMhv'
    TRADIER_TOKEN = 'jj8L3RuSVG5MUwUpz2XHrjXjAFrq'
    
    scanner = SessionScanner(POLYGON_KEY, TRADIER_TOKEN)
    
    if args.pull_levels:
        scanner.pull_levels()
    elif args.show_levels:
        scanner.load_levels()
        scanner.print_levels()
    elif args.scan_once:
        scanner.scan_once()
    elif args.continuous:
        scanner.run_continuous(args.interval)
    else:
        # Default: pull levels if not exist, then run once
        if not scanner.load_levels():
            print("Pulling levels first...")
            scanner.pull_levels()
        scanner.scan_once()


if __name__ == "__main__":
    main()
