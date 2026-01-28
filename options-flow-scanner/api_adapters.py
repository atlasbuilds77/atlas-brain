#!/usr/bin/env python3
"""
API Adapters for different options flow data sources
Modular design - plug in whichever API you choose
"""
import requests
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime

class FlowAPIAdapter(ABC):
    """Base class for all API adapters"""
    
    def __init__(self, api_key: str, config: Dict = None):
        self.api_key = api_key
        self.config = config or {}
        
    @abstractmethod
    def fetch_realtime_flow(self, tickers: List[str]) -> List[Dict]:
        """Fetch real-time options flow"""
        pass
    
    @abstractmethod
    def parse_flow_data(self, raw_data: Dict) -> Dict:
        """Parse raw API response into standardized format"""
        pass

class UnusualWhalesAdapter(FlowAPIAdapter):
    """Unusual Whales API adapter"""
    
    BASE_URL = 'https://api.unusualwhales.com/v1'
    
    def fetch_realtime_flow(self, tickers: List[str]) -> List[Dict]:
        """Fetch flow from Unusual Whales"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Accept': 'application/json'
        }
        
        flows = []
        for ticker in tickers:
            try:
                response = requests.get(
                    f'{self.BASE_URL}/options/flow',
                    headers=headers,
                    params={
                        'ticker': ticker,
                        'limit': 50,
                        'min_premium': 200000
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get('data', []):
                        flows.append(self.parse_flow_data(item))
                        
            except Exception as e:
                print(f"Error fetching {ticker} from Unusual Whales: {e}")
                
        return flows
    
    def parse_flow_data(self, raw_data: Dict) -> Dict:
        """Parse Unusual Whales format"""
        return {
            'ticker': raw_data.get('ticker'),
            'strike': float(raw_data.get('strike', 0)),
            'expiration': raw_data.get('expiration_date'),
            'option_type': raw_data.get('option_type', '').lower(),
            'side': 'buy' if raw_data.get('side') == 'ASK' else 'sell',
            'contracts': int(raw_data.get('size', 0)),
            'premium_per': float(raw_data.get('price', 0)),
            'total_premium': float(raw_data.get('premium', 0)),
            'fill_type': raw_data.get('fill_type', 'mid').lower(),
            'timestamp': raw_data.get('timestamp', datetime.now().isoformat()),
            'volume_vs_oi': float(raw_data.get('volume', 0)) / max(float(raw_data.get('open_interest', 1)), 1),
            'is_sweep': raw_data.get('is_sweep', False),
        }

class FlowAlgoAdapter(FlowAPIAdapter):
    """FlowAlgo API adapter"""
    
    BASE_URL = 'https://api.flowalgo.com/v1'
    
    def fetch_realtime_flow(self, tickers: List[str]) -> List[Dict]:
        """Fetch flow from FlowAlgo"""
        headers = {
            'X-API-KEY': self.api_key,
            'Accept': 'application/json'
        }
        
        flows = []
        try:
            response = requests.get(
                f'{self.BASE_URL}/flow',
                headers=headers,
                params={
                    'tickers': ','.join(tickers),
                    'limit': 100
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                for item in data.get('flows', []):
                    flows.append(self.parse_flow_data(item))
                    
        except Exception as e:
            print(f"Error fetching from FlowAlgo: {e}")
            
        return flows
    
    def parse_flow_data(self, raw_data: Dict) -> Dict:
        """Parse FlowAlgo format"""
        return {
            'ticker': raw_data.get('symbol'),
            'strike': float(raw_data.get('strike_price', 0)),
            'expiration': raw_data.get('expiration'),
            'option_type': raw_data.get('type', '').lower(),
            'side': raw_data.get('side', '').lower(),
            'contracts': int(raw_data.get('contracts', 0)),
            'premium_per': float(raw_data.get('price', 0)),
            'total_premium': float(raw_data.get('total_cost', 0)),
            'fill_type': raw_data.get('execution', 'mid').lower(),
            'timestamp': raw_data.get('time', datetime.now().isoformat()),
            'volume_vs_oi': float(raw_data.get('volume_oi_ratio', 1.0)),
            'is_sweep': raw_data.get('is_sweep', False),
        }

class PolygonAdapter(FlowAPIAdapter):
    """Polygon.io API adapter"""
    
    BASE_URL = 'https://api.polygon.io/v3'
    
    def fetch_realtime_flow(self, tickers: List[str]) -> List[Dict]:
        """Fetch options data from Polygon"""
        flows = []
        
        for ticker in tickers:
            try:
                response = requests.get(
                    f'{self.BASE_URL}/snapshot/options/{ticker}',
                    params={'apiKey': self.api_key},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get('results', []):
                        # Polygon gives snapshot, need to filter for unusual activity
                        if self._is_unusual(item):
                            flows.append(self.parse_flow_data(item))
                            
            except Exception as e:
                print(f"Error fetching {ticker} from Polygon: {e}")
                
        return flows
    
    def _is_unusual(self, item: Dict) -> bool:
        """Determine if option activity is unusual"""
        volume = item.get('day', {}).get('volume', 0)
        open_interest = item.get('open_interest', 1)
        
        # Volume must be at least 2x open interest
        if volume < open_interest * 2:
            return False
            
        # Must have significant dollar volume
        last_price = item.get('last', {}).get('price', 0)
        dollar_volume = volume * last_price * 100
        if dollar_volume < 200_000:
            return False
            
        return True
    
    def parse_flow_data(self, raw_data: Dict) -> Dict:
        """Parse Polygon format"""
        details = raw_data.get('details', {})
        last_trade = raw_data.get('last', {})
        day_data = raw_data.get('day', {})
        
        return {
            'ticker': details.get('underlying_ticker'),
            'strike': float(details.get('strike_price', 0)),
            'expiration': details.get('expiration_date'),
            'option_type': details.get('contract_type', '').lower(),
            'side': 'buy',  # Polygon doesn't provide side, assume buy for unusual volume
            'contracts': int(day_data.get('volume', 0)),
            'premium_per': float(last_trade.get('price', 0)),
            'total_premium': float(day_data.get('volume', 0)) * float(last_trade.get('price', 0)) * 100,
            'fill_type': 'mid',
            'timestamp': datetime.now().isoformat(),
            'volume_vs_oi': float(day_data.get('volume', 0)) / max(float(raw_data.get('open_interest', 1)), 1),
            'is_sweep': False,
        }

class AlpacaAdapter(FlowAPIAdapter):
    """Alpaca Markets API adapter (free tier available)"""
    
    BASE_URL = 'https://data.alpaca.markets/v1beta1'
    
    def fetch_realtime_flow(self, tickers: List[str]) -> List[Dict]:
        """Fetch options data from Alpaca"""
        headers = {
            'APCA-API-KEY-ID': self.api_key,
            'APCA-API-SECRET-KEY': self.config.get('secret_key', ''),
        }
        
        flows = []
        for ticker in tickers:
            try:
                response = requests.get(
                    f'{self.BASE_URL}/options/snapshots/{ticker}',
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get('snapshots', []):
                        if self._is_unusual(item):
                            flows.append(self.parse_flow_data(item))
                            
            except Exception as e:
                print(f"Error fetching {ticker} from Alpaca: {e}")
                
        return flows
    
    def _is_unusual(self, item: Dict) -> bool:
        """Determine if unusual (similar to Polygon)"""
        volume = item.get('latestTrade', {}).get('s', 0)
        # Basic filtering - would need more sophisticated logic
        return volume > 100
    
    def parse_flow_data(self, raw_data: Dict) -> Dict:
        """Parse Alpaca format"""
        latest_trade = raw_data.get('latestTrade', {})
        
        # Alpaca options format: AAPL250117C00200000 (ticker + date + type + strike)
        symbol = raw_data.get('symbol', '')
        # Parse symbol to extract details (simplified)
        
        return {
            'ticker': symbol[:3] if len(symbol) > 3 else symbol,  # First 3 chars usually ticker
            'strike': 0.0,  # Would need proper symbol parsing
            'expiration': '2026-01-01',  # Would need proper symbol parsing
            'option_type': 'call',  # Would need proper symbol parsing
            'side': 'buy',
            'contracts': int(latest_trade.get('s', 0)),
            'premium_per': float(latest_trade.get('p', 0)),
            'total_premium': int(latest_trade.get('s', 0)) * float(latest_trade.get('p', 0)) * 100,
            'fill_type': 'mid',
            'timestamp': latest_trade.get('t', datetime.now().isoformat()),
            'volume_vs_oi': 1.0,
            'is_sweep': False,
        }

def get_adapter(api_name: str, api_key: str, config: Dict = None) -> FlowAPIAdapter:
    """Factory function to get appropriate adapter"""
    adapters = {
        'unusual_whales': UnusualWhalesAdapter,
        'flowalgo': FlowAlgoAdapter,
        'polygon': PolygonAdapter,
        'alpaca': AlpacaAdapter,
    }
    
    adapter_class = adapters.get(api_name)
    if not adapter_class:
        raise ValueError(f"Unknown API: {api_name}. Available: {list(adapters.keys())}")
    
    return adapter_class(api_key, config)

if __name__ == '__main__':
    # Example: Test adapter
    print("API Adapters ready. Use get_adapter() to instantiate.")
    print("Available APIs:", ['unusual_whales', 'flowalgo', 'polygon', 'alpaca'])
