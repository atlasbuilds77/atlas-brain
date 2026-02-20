"""
TITAN Alert System
Manages alert generation, tracking, and persistence
"""

import json
from datetime import datetime
import pytz
from collections import defaultdict


class AlertManager:
    def __init__(self, alert_file='/tmp/titan_alerts.json'):
        self.alert_file = alert_file
        self.touched_levels = defaultdict(set)  # Track touched levels to avoid re-alerts
        self.alerts = []
        self.load_alerts()
    
    def load_alerts(self):
        """Load existing alerts from file"""
        try:
            with open(self.alert_file, 'r') as f:
                data = json.load(f)
                self.alerts = data.get('alerts', [])
                # Load touched levels (convert lists back to sets)
                touched = data.get('touched_levels', {})
                for symbol, levels in touched.items():
                    self.touched_levels[symbol] = set(levels)
        except FileNotFoundError:
            self.alerts = []
            self.touched_levels = defaultdict(set)
        except Exception as e:
            print(f"Error loading alerts: {e}")
            self.alerts = []
            self.touched_levels = defaultdict(set)
    
    def save_alerts(self):
        """Save alerts to file"""
        try:
            # Convert sets to lists for JSON serialization
            touched_serializable = {
                symbol: list(levels) 
                for symbol, levels in self.touched_levels.items()
            }
            
            data = {
                'alerts': self.alerts,
                'touched_levels': touched_serializable,
                'last_updated': datetime.now(pytz.timezone('America/New_York')).isoformat()
            }
            
            with open(self.alert_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving alerts: {e}")
    
    def check_level_proximity(self, symbol, current_price, level_price, level_type, threshold_pct=0.2):
        """
        Check if price is within threshold of a level
        Returns True if approaching and not already touched
        """
        if current_price is None or level_price is None:
            return False
        
        # Calculate percentage distance
        distance_pct = abs((current_price - level_price) / level_price) * 100
        
        # Create unique level key
        level_key = f"{level_type}_{level_price:.2f}"
        
        # Check if within threshold and not already touched
        if distance_pct <= threshold_pct:
            if level_key not in self.touched_levels[symbol]:
                self.touched_levels[symbol].add(level_key)
                return True
        
        return False
    
    def create_alert(self, symbol, level_type, level_price, current_price, 
                    suggested_strike=None, direction=None, target=None, stop=None):
        """
        Create and log an alert
        """
        et_tz = pytz.timezone('America/New_York')
        timestamp = datetime.now(et_tz)
        
        alert = {
            'time': timestamp.strftime('%H:%M:%S'),
            'timestamp': timestamp.isoformat(),
            'symbol': symbol,
            'level_type': level_type,
            'level_price': level_price,
            'current_price': current_price,
            'suggested_strike': suggested_strike,
            'direction': direction,
            'target': target,
            'stop': stop
        }
        
        self.alerts.append(alert)
        self.save_alerts()
        
        # Print to console
        self.print_alert(alert)
        
        return alert
    
    def print_alert(self, alert):
        """Print formatted alert to console"""
        print("\n" + "="*70)
        print(f"=== ALERT - {alert['time']} ===")
        print("="*70)
        print(f"{alert['symbol']} approaching {alert['level_type']} (${alert['level_price']:.2f})")
        print(f"Current Price: ${alert['current_price']:.2f}")
        
        if alert.get('suggested_strike'):
            print(f"\nSuggested Trade:")
            print(f"  {alert['direction']} {alert['symbol']} ${alert['suggested_strike']} Call")
            if alert.get('target'):
                print(f"  Target: ${alert['target']:.2f}")
            if alert.get('stop'):
                print(f"  Stop: {alert['stop']}")
        
        print("="*70 + "\n")
    
    def get_todays_alerts(self):
        """Get all alerts from today"""
        et_tz = pytz.timezone('America/New_York')
        today = datetime.now(et_tz).date()
        
        todays = []
        for alert in self.alerts:
            alert_time = datetime.fromisoformat(alert['timestamp'])
            if alert_time.date() == today:
                todays.append(alert)
        
        return todays
    
    def reset_daily(self):
        """Reset touched levels at start of new day"""
        self.touched_levels = defaultdict(set)
        self.save_alerts()
        print("✓ Daily reset: touched levels cleared")
    
    def get_alert_summary(self):
        """Get summary of today's alerts"""
        todays = self.get_todays_alerts()
        
        summary = {
            'total_alerts': len(todays),
            'by_symbol': defaultdict(int),
            'by_type': defaultdict(int)
        }
        
        for alert in todays:
            summary['by_symbol'][alert['symbol']] += 1
            summary['by_type'][alert['level_type']] += 1
        
        return summary


class OptionStrikeCalculator:
    def __init__(self, tradier_token):
        self.tradier_token = tradier_token
        self.base_url = "https://api.tradier.com/v1"
    
    def get_option_chain(self, symbol, expiration):
        """Fetch option chain from Tradier"""
        url = f"{self.base_url}/markets/options/chains"
        headers = {
            'Authorization': f'Bearer {self.tradier_token}',
            'Accept': 'application/json'
        }
        params = {
            'symbol': symbol,
            'expiration': expiration,
            'greeks': 'true'
        }
        
        try:
            import requests
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            options = data.get('options', {}).get('option', [])
            return options if isinstance(options, list) else [options]
            
        except Exception as e:
            print(f"Error fetching option chain: {e}")
            return []
    
    def get_next_expiration(self, symbol):
        """Get next available expiration date"""
        url = f"{self.base_url}/markets/options/expirations"
        headers = {
            'Authorization': f'Bearer {self.tradier_token}',
            'Accept': 'application/json'
        }
        params = {'symbol': symbol}
        
        try:
            import requests
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            expirations = data.get('expirations', {}).get('date', [])
            if expirations:
                return expirations[0] if isinstance(expirations, list) else expirations
            return None
            
        except Exception as e:
            print(f"Error fetching expirations: {e}")
            return None
    
    def calculate_strike(self, symbol, current_price, target_price, direction='call'):
        """
        Calculate optimal OTM strike at target level
        Returns strike details with greeks
        """
        expiration = self.get_next_expiration(symbol)
        if not expiration:
            print(f"No expiration found for {symbol}")
            return None
        
        chain = self.get_option_chain(symbol, expiration)
        if not chain:
            print(f"No option chain found for {symbol}")
            return None
        
        # Filter calls
        calls = [opt for opt in chain if opt.get('option_type') == 'call']
        
        # Find strike closest to target price
        best_strike = None
        min_diff = float('inf')
        
        for option in calls:
            strike = option.get('strike')
            if strike is None:
                continue
            
            # For calls, we want strike near or slightly below target
            if direction == 'call':
                if strike <= target_price:
                    diff = abs(target_price - strike)
                    if diff < min_diff:
                        min_diff = diff
                        best_strike = option
        
        if best_strike:
            greeks = best_strike.get('greeks', {})
            return {
                'symbol': best_strike.get('symbol'),
                'strike': best_strike.get('strike'),
                'expiration': expiration,
                'bid': best_strike.get('bid'),
                'ask': best_strike.get('ask'),
                'last': best_strike.get('last'),
                'delta': greeks.get('delta'),
                'gamma': greeks.get('gamma'),
                'theta': greeks.get('theta'),
                'vega': greeks.get('vega'),
                'volume': best_strike.get('volume'),
                'open_interest': best_strike.get('open_interest')
            }
        
        return None


if __name__ == "__main__":
    # Test alert manager
    alert_mgr = AlertManager()
    
    # Simulate an alert
    alert = alert_mgr.create_alert(
        symbol='QQQ',
        level_type='Pre-Low',
        level_price=597.42,
        current_price=597.65,
        suggested_strike=600,
        direction='Buy',
        target=602.28,
        stop='Below $596.50'
    )
    
    print("\nAlert Summary:")
    print(json.dumps(alert_mgr.get_alert_summary(), indent=2))
