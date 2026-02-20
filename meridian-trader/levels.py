"""
TITAN Level Calculation Module
Calculates session levels from market data
"""

import requests
from datetime import datetime, timedelta
import pytz
import json


class LevelCalculator:
    def __init__(self, polygon_api_key):
        self.polygon_key = polygon_api_key
        self.base_url = "https://api.polygon.io"
        
    def get_premarket_levels(self, symbol, date=None):
        """
        Calculate pre-market high/low from 4am-9:30am ET
        Returns: {pre_high, pre_low, pre_high_time, pre_low_time}
        """
        if date is None:
            date = datetime.now(pytz.timezone('America/New_York'))
        
        # Convert to ET if not already
        et_tz = pytz.timezone('America/New_York')
        if date.tzinfo is None:
            date = et_tz.localize(date)
        else:
            date = date.astimezone(et_tz)
        
        # Pre-market: 4:00 AM - 9:30 AM ET
        premarket_start = date.replace(hour=4, minute=0, second=0, microsecond=0)
        premarket_end = date.replace(hour=9, minute=30, second=0, microsecond=0)
        
        # Convert to milliseconds for Polygon API
        start_ms = int(premarket_start.timestamp() * 1000)
        end_ms = int(premarket_end.timestamp() * 1000)
        
        # Pull 5-minute bars
        url = f"{self.base_url}/v2/aggs/ticker/{symbol}/range/5/minute/{start_ms}/{end_ms}"
        params = {
            'apiKey': self.polygon_key,
            'adjusted': 'true',
            'sort': 'asc',
            'limit': 50000
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('resultsCount', 0) == 0:
                return None
            
            bars = data.get('results', [])
            if not bars:
                return None
            
            # Find high and low
            pre_high = max(bar['h'] for bar in bars)
            pre_low = min(bar['l'] for bar in bars)
            
            # Find times
            pre_high_bar = next(bar for bar in bars if bar['h'] == pre_high)
            pre_low_bar = next(bar for bar in bars if bar['l'] == pre_low)
            
            pre_high_time = datetime.fromtimestamp(pre_high_bar['t'] / 1000, tz=et_tz)
            pre_low_time = datetime.fromtimestamp(pre_low_bar['t'] / 1000, tz=et_tz)
            
            return {
                'pre_high': pre_high,
                'pre_low': pre_low,
                'pre_high_time': pre_high_time.strftime('%H:%M'),
                'pre_low_time': pre_low_time.strftime('%H:%M'),
                'bar_count': len(bars)
            }
            
        except Exception as e:
            print(f"Error fetching premarket data for {symbol}: {e}")
            return None
    
    def get_prior_day_levels(self, symbol, date=None):
        """
        Get prior trading day high/low
        Returns: {prior_high, prior_low, prior_date}
        """
        if date is None:
            date = datetime.now(pytz.timezone('America/New_York'))
        
        et_tz = pytz.timezone('America/New_York')
        if date.tzinfo is None:
            date = et_tz.localize(date)
        else:
            date = date.astimezone(et_tz)
        
        # Get previous trading day (skip weekends)
        prior_date = date - timedelta(days=1)
        while prior_date.weekday() >= 5:  # Saturday=5, Sunday=6
            prior_date -= timedelta(days=1)
        
        # Prior day: 9:30 AM - 4:00 PM ET
        day_start = prior_date.replace(hour=9, minute=30, second=0, microsecond=0)
        day_end = prior_date.replace(hour=16, minute=0, second=0, microsecond=0)
        
        start_ms = int(day_start.timestamp() * 1000)
        end_ms = int(day_end.timestamp() * 1000)
        
        url = f"{self.base_url}/v2/aggs/ticker/{symbol}/range/5/minute/{start_ms}/{end_ms}"
        params = {
            'apiKey': self.polygon_key,
            'adjusted': 'true',
            'sort': 'asc',
            'limit': 50000
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('resultsCount', 0) == 0:
                return None
            
            bars = data.get('results', [])
            if not bars:
                return None
            
            prior_high = max(bar['h'] for bar in bars)
            prior_low = min(bar['l'] for bar in bars)
            
            return {
                'prior_high': prior_high,
                'prior_low': prior_low,
                'prior_date': prior_date.strftime('%Y-%m-%d'),
                'bar_count': len(bars)
            }
            
        except Exception as e:
            print(f"Error fetching prior day data for {symbol}: {e}")
            return None
    
    def get_current_price(self, symbol):
        """Get current price from Polygon snapshot"""
        url = f"{self.base_url}/v2/snapshot/locale/us/markets/stocks/tickers/{symbol}"
        params = {'apiKey': self.polygon_key}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            ticker = data.get('ticker', {})
            last_trade = ticker.get('lastTrade', {})
            price = last_trade.get('p')
            
            if price:
                return float(price)
            return None
            
        except Exception as e:
            print(f"Error fetching current price for {symbol}: {e}")
            return None
    
    def calculate_all_levels(self, symbols=['SPY', 'QQQ']):
        """
        Calculate all levels for given symbols
        Returns dict with all levels
        """
        levels = {}
        
        for symbol in symbols:
            print(f"Calculating levels for {symbol}...")
            
            premarket = self.get_premarket_levels(symbol)
            prior_day = self.get_prior_day_levels(symbol)
            current_price = self.get_current_price(symbol)
            
            levels[symbol] = {
                'current_price': current_price,
                'premarket': premarket,
                'prior_day': prior_day,
                'timestamp': datetime.now(pytz.timezone('America/New_York')).isoformat()
            }
        
        return levels
    
    def save_levels(self, levels, filepath='/tmp/titan_levels.json'):
        """Save calculated levels to JSON file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(levels, f, indent=2)
            print(f"✓ Levels saved to {filepath}")
            return True
        except Exception as e:
            print(f"Error saving levels: {e}")
            return False
    
    def load_levels(self, filepath='/tmp/titan_levels.json'):
        """Load levels from JSON file"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"No levels file found at {filepath}")
            return None
        except Exception as e:
            print(f"Error loading levels: {e}")
            return None


if __name__ == "__main__":
    # Test the calculator
    calc = LevelCalculator('h7J74V1cd8_4NQpTxwQpudpqXWaIHMhv')
    levels = calc.calculate_all_levels(['SPY', 'QQQ'])
    calc.save_levels(levels)
    
    print("\n=== CALCULATED LEVELS ===")
    print(json.dumps(levels, indent=2))
