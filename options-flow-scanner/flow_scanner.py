#!/usr/bin/env python3
"""
SPX Options Flow Scanner
Real-time unusual options activity detection and alerting
"""
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class FlowStrength(Enum):
    WEAK = 1
    MODERATE = 2
    STRONG = 3
    EXTREME = 4

@dataclass
class OptionsFlow:
    """Single options flow alert"""
    ticker: str
    strike: float
    expiration: str
    option_type: str  # 'call' or 'put'
    side: str  # 'buy' or 'sell'
    contracts: int
    premium_per: float
    total_premium: float
    fill_type: str  # 'ask', 'bid', 'mid'
    timestamp: datetime
    volume_vs_oi: float  # volume / open interest ratio
    is_sweep: bool
    strength: FlowStrength
    
    def to_dict(self) -> Dict:
        return {
            'ticker': self.ticker,
            'strike': self.strike,
            'expiration': self.expiration,
            'option_type': self.option_type,
            'side': self.side,
            'contracts': self.contracts,
            'premium_per': self.premium_per,
            'total_premium': self.total_premium,
            'fill_type': self.fill_type,
            'timestamp': self.timestamp.isoformat(),
            'volume_vs_oi': self.volume_vs_oi,
            'is_sweep': self.is_sweep,
            'strength': self.strength.name
        }

class FlowScanner:
    """Main flow scanner class"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.alerts = []
        self.thresholds = config.get('thresholds', {
            'min_premium': 200_000,  # $200K minimum
            'min_contracts': 100,
            'volume_oi_ratio': 2.0,  # 2x OI = unusual
            'spx_min_premium': 500_000,  # $500K for SPX (higher threshold)
        })
        
    def calculate_strength(self, flow: OptionsFlow) -> FlowStrength:
        """Score flow strength based on multiple factors"""
        score = 0
        
        # Premium size
        if flow.total_premium >= 5_000_000:
            score += 4
        elif flow.total_premium >= 2_000_000:
            score += 3
        elif flow.total_premium >= 1_000_000:
            score += 2
        elif flow.total_premium >= 500_000:
            score += 1
            
        # Aggressive fill (at ask for calls, at bid for puts)
        if flow.fill_type == 'ask' and flow.option_type == 'call':
            score += 2
        elif flow.fill_type == 'bid' and flow.option_type == 'put':
            score += 2
        elif flow.fill_type == 'ask' and flow.option_type == 'put':
            score += 2
        elif flow.fill_type == 'bid' and flow.option_type == 'call':
            score += 2
            
        # Volume vs OI
        if flow.volume_vs_oi >= 5.0:
            score += 2
        elif flow.volume_vs_oi >= 3.0:
            score += 1
            
        # Sweep order
        if flow.is_sweep:
            score += 2
            
        # Determine strength
        if score >= 8:
            return FlowStrength.EXTREME
        elif score >= 6:
            return FlowStrength.STRONG
        elif score >= 4:
            return FlowStrength.MODERATE
        else:
            return FlowStrength.WEAK
    
    def is_0dte(self, expiration: str) -> bool:
        """Check if option is 0DTE"""
        try:
            exp_date = datetime.strptime(expiration, '%Y-%m-%d')
            today = datetime.now().date()
            return exp_date.date() == today
        except:
            return False
    
    def filter_spx_flow(self, flow: OptionsFlow) -> bool:
        """SPX-specific filtering"""
        # Must meet minimum premium
        if flow.total_premium < self.thresholds['spx_min_premium']:
            return False
        
        # Prefer aggressive fills
        if flow.fill_type == 'mid':
            return False
        
        # 0DTE gets priority
        if self.is_0dte(flow.expiration):
            return True
        
        # Weekly contracts (1-7 DTE) also good
        try:
            exp_date = datetime.strptime(flow.expiration, '%Y-%m-%d')
            dte = (exp_date.date() - datetime.now().date()).days
            if dte <= 7:
                return True
        except:
            pass
        
        # Otherwise needs to be very large
        return flow.total_premium >= 2_000_000
    
    def process_flow(self, flow_data: Dict) -> Optional[OptionsFlow]:
        """Process raw flow data and return OptionsFlow if it passes filters"""
        try:
            flow = OptionsFlow(
                ticker=flow_data['ticker'],
                strike=flow_data['strike'],
                expiration=flow_data['expiration'],
                option_type=flow_data['option_type'],
                side=flow_data['side'],
                contracts=flow_data['contracts'],
                premium_per=flow_data['premium_per'],
                total_premium=flow_data['total_premium'],
                fill_type=flow_data['fill_type'],
                timestamp=datetime.fromisoformat(flow_data['timestamp']),
                volume_vs_oi=flow_data.get('volume_vs_oi', 1.0),
                is_sweep=flow_data.get('is_sweep', False),
                strength=FlowStrength.WEAK  # Will be calculated
            )
            
            # Calculate strength
            flow.strength = self.calculate_strength(flow)
            
            # Apply filters
            if flow.ticker in ['SPX', 'SPY']:
                if not self.filter_spx_flow(flow):
                    return None
            else:
                # General filtering
                if flow.total_premium < self.thresholds['min_premium']:
                    return None
                if flow.contracts < self.thresholds['min_contracts']:
                    return None
            
            return flow
            
        except Exception as e:
            print(f"Error processing flow: {e}")
            return None
    
    def alert(self, flow: OptionsFlow):
        """Generate alert for significant flow"""
        dte_label = "0DTE" if self.is_0dte(flow.expiration) else flow.expiration
        
        direction = "📈" if flow.option_type == 'call' else "📉"
        strength_emoji = {
            FlowStrength.WEAK: "⚪",
            FlowStrength.MODERATE: "🟡",
            FlowStrength.STRONG: "🟠",
            FlowStrength.EXTREME: "🔴"
        }
        
        alert_msg = f"""
{strength_emoji[flow.strength]} {direction} {flow.ticker} FLOW - {flow.strength.name}

Strike: ${flow.strike} {flow.option_type.upper()}
Expiration: {dte_label}
Side: {flow.side.upper()} {flow.contracts} contracts
Premium: ${flow.total_premium:,.0f} (${flow.premium_per:.2f}/contract)
Fill: {flow.fill_type.upper()} {"🔥" if flow.is_sweep else ""}
Vol/OI: {flow.volume_vs_oi:.1f}x
Time: {flow.timestamp.strftime('%H:%M:%S')}
"""
        print(alert_msg)
        self.alerts.append(flow)
        return alert_msg
    
    def run_backtest(self, historical_data: List[Dict]):
        """Backtest scanner on historical flow data"""
        print(f"\n=== BACKTESTING ON {len(historical_data)} FLOWS ===\n")
        
        alerts_generated = 0
        for flow_data in historical_data:
            flow = self.process_flow(flow_data)
            if flow:
                self.alert(flow)
                alerts_generated += 1
        
        print(f"\n=== BACKTEST COMPLETE ===")
        print(f"Total flows processed: {len(historical_data)}")
        print(f"Alerts generated: {alerts_generated}")
        print(f"Alert rate: {alerts_generated/len(historical_data)*100:.1f}%")
        
        # Strength breakdown
        strength_counts = {}
        for flow in self.alerts:
            strength_counts[flow.strength.name] = strength_counts.get(flow.strength.name, 0) + 1
        
        print(f"\nStrength breakdown:")
        for strength, count in sorted(strength_counts.items()):
            print(f"  {strength}: {count} ({count/alerts_generated*100:.1f}%)")

def load_api_config(api_name: str) -> Dict:
    """Load API-specific configuration"""
    configs = {
        'unusual_whales': {
            'api_key': 'YOUR_API_KEY',
            'endpoint': 'https://api.unusualwhales.com/v1',
            'rate_limit': 10,  # requests per second
        },
        'flowalgo': {
            'api_key': 'YOUR_API_KEY',
            'endpoint': 'https://api.flowalgo.com/v1',
            'rate_limit': 5,
        },
        'polygon': {
            'api_key': 'YOUR_API_KEY',
            'endpoint': 'https://api.polygon.io/v3',
            'rate_limit': 5,
        },
        'test': {
            # Test mode with mock data
            'mock': True,
        }
    }
    return configs.get(api_name, configs['test'])

if __name__ == '__main__':
    # Example usage
    config = {
        'api': 'test',
        'tickers': ['SPX', 'SPY'],
        'thresholds': {
            'min_premium': 200_000,
            'spx_min_premium': 500_000,
        }
    }
    
    scanner = FlowScanner(config)
    
    # Example flow (like Flow God's SLV)
    test_flows = [
        {
            'ticker': 'SPX',
            'strike': 7000,
            'expiration': datetime.now().strftime('%Y-%m-%d'),  # 0DTE
            'option_type': 'call',
            'side': 'buy',
            'contracts': 1000,
            'premium_per': 5.50,
            'total_premium': 5_500_000,
            'fill_type': 'ask',
            'timestamp': datetime.now().isoformat(),
            'volume_vs_oi': 8.5,
            'is_sweep': True,
        },
        {
            'ticker': 'SPY',
            'strike': 695,
            'expiration': datetime.now().strftime('%Y-%m-%d'),
            'option_type': 'put',
            'side': 'buy',
            'contracts': 500,
            'premium_per': 0.28,
            'total_premium': 14_000,
            'fill_type': 'ask',
            'timestamp': datetime.now().isoformat(),
            'volume_vs_oi': 3.2,
            'is_sweep': False,
        },
        {
            'ticker': 'SPX',
            'strike': 6950,
            'expiration': '2026-02-03',
            'option_type': 'call',
            'side': 'buy',
            'contracts': 2000,
            'premium_per': 15.75,
            'total_premium': 3_150_000,
            'fill_type': 'ask',
            'timestamp': datetime.now().isoformat(),
            'volume_vs_oi': 5.2,
            'is_sweep': True,
        }
    ]
    
    scanner.run_backtest(test_flows)
