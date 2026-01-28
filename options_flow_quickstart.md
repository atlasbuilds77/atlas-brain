# Options Flow Analysis - Quick Start Implementation Guide

## Core Detection Algorithms

### 1. Unusual Volume Detection
```python
import numpy as np
from collections import deque

class UnusualVolumeDetector:
    def __init__(self, window_size=20, threshold=3.0):
        self.window = deque(maxlen=window_size)
        self.threshold = threshold
    
    def is_unusual(self, current_volume):
        if len(self.window) < 5:
            self.window.append(current_volume)
            return False
        
        mean = np.mean(list(self.window))
        std = np.std(list(self.window))
        z_score = (current_volume - mean) / std if std > 0 else 0
        
        self.window.append(current_volume)
        return abs(z_score) > self.threshold
```

### 2. Aggressive Fill Detection
```python
class AggressiveFillDetector:
    @staticmethod
    def detect_aggression(trade_price, bid_price, ask_price, option_type):
        if option_type == 'call':
            if trade_price > ask_price:
                return 'AA'  # Above Ask
            elif trade_price == ask_price:
                return 'A'   # At Ask
        elif option_type == 'put':
            if trade_price < bid_price:
                return 'BB'  # Below Bid
            elif trade_price == bid_price:
                return 'B'   # At Bid
        return 'N'  # Normal
```

### 3. Smart Money Scoring
```python
class SmartMoneyScorer:
    def __init__(self):
        self.weights = {
            'premium': 0.3,
            'volume_ratio': 0.25,
            'aggression': 0.2,
            'delta': 0.15,
            'time_of_day': 0.1
        }
    
    def score_trade(self, trade):
        scores = {}
        
        # Premium score (0-100)
        scores['premium'] = min(100, trade['premium'] / 10000)
        
        # Volume ratio score
        vol_ratio = trade['volume'] / trade['open_interest']
        scores['volume_ratio'] = min(100, vol_ratio * 20)
        
        # Aggression score
        aggression_map = {'N': 0, 'A': 50, 'B': 50, 'AA': 100, 'BB': 100}
        scores['aggression'] = aggression_map.get(trade.get('aggression', 'N'), 0)
        
        # Delta score (directional conviction)
        delta = abs(trade.get('delta', 0))
        scores['delta'] = delta * 100
        
        # Time of day score (power hour bonus)
        hour = trade['timestamp'].hour
        scores['time_of_day'] = 100 if 15 <= hour < 16 else 50
        
        # Weighted total
        total = sum(scores[k] * self.weights[k] for k in scores)
        return {
            'total_score': total,
            'component_scores': scores,
            'signal_strength': self.classify_strength(total)
        }
    
    def classify_strength(self, score):
        if score >= 80:
            return 'STRONG'
        elif score >= 60:
            return 'MODERATE'
        elif score >= 40:
            return 'WEAK'
        else:
            return 'NOISE'
```

## Real-Time Processing Pipeline

```python
import asyncio
from datetime import datetime, timedelta

class OptionsFlowProcessor:
    def __init__(self):
        self.volume_detector = UnusualVolumeDetector()
        self.aggression_detector = AggressiveFillDetector()
        self.scorer = SmartMoneyScorer()
        self.alerts = []
        self.recent_trades = []
    
    async def process_trade(self, trade_data):
        # Step 1: Basic validation
        if not self.validate_trade(trade_data):
            return
        
        # Step 2: Detect unusual volume
        is_unusual = self.volume_detector.is_unusual(trade_data['volume'])
        
        # Step 3: Detect aggressive fills
        aggression = self.aggression_detector.detect_aggression(
            trade_data['price'],
            trade_data['bid'],
            trade_data['ask'],
            trade_data['option_type']
        )
        trade_data['aggression'] = aggression
        
        # Step 4: Score the trade
        score_result = self.scorer.score_trade(trade_data)
        
        # Step 5: Check for alerts
        if (is_unusual or aggression in ['AA', 'BB']) and score_result['total_score'] > 60:
            alert = self.create_alert(trade_data, score_result)
            self.alerts.append(alert)
            await self.send_alert(alert)
        
        # Step 6: Store for analysis
        self.recent_trades.append({
            **trade_data,
            'score': score_result,
            'timestamp': datetime.now()
        })
        
        # Keep only last 1000 trades
        if len(self.recent_trades) > 1000:
            self.recent_trades = self.recent_trades[-1000:]
    
    def validate_trade(self, trade):
        required_fields = ['symbol', 'volume', 'price', 'bid', 'ask', 'option_type']
        return all(field in trade for field in required_fields)
    
    def create_alert(self, trade, score_result):
        return {
            'symbol': trade['symbol'],
            'timestamp': datetime.now(),
            'score': score_result['total_score'],
            'strength': score_result['signal_strength'],
            'premium': trade.get('premium', 0),
            'aggression': trade.get('aggression', 'N'),
            'details': {
                'volume': trade['volume'],
                'price': trade['price'],
                'option_type': trade['option_type']
            }
        }
    
    async def send_alert(self, alert):
        # Implement your alert delivery (email, webhook, etc.)
        print(f"ALERT: {alert['symbol']} - Score: {alert['score']:.1f} - {alert['strength']}")
```

## Key Thresholds for Production

### Volume Anomaly Thresholds
```python
VOLUME_THRESHOLDS = {
    'min_volume': 100,           # Minimum contracts to consider
    'volume_ratio_alert': 3.0,   # Volume/OI ratio for alert
    'z_score_threshold': 2.5,    # Standard deviations for unusual
}
```

### Premium Size Thresholds
```python
PREMIUM_THRESHOLDS = {
    'significant': 100000,       # $100k+ premium
    'major': 1000000,            # $1M+ premium
    'whale': 10000000,           # $10M+ premium
}
```

### Time-Based Filters
```python
TIME_FILTERS = {
    'market_hours': ('09:30', '16:00'),  # Regular trading hours
    'power_hour': ('15:00', '16:00'),    # Enhanced monitoring
    'ignore_premarket': True,            # Filter pre-market noise
}
```

## Multi-Leg Strategy Detection

```python
class MultiLegDetector:
    def __init__(self, time_window_ms=100):
        self.time_window = timedelta(milliseconds=time_window_ms)
        self.pending_trades = {}
    
    def detect_strategies(self, trade):
        symbol = trade['symbol']
        timestamp = trade['timestamp']
        
        # Check for existing pending trades in window
        strategies = []
        for pending_symbol, pending_trades in self.pending_trades.items():
            for pending in list(pending_trades):
                time_diff = timestamp - pending['timestamp']
                if time_diff > self.time_window:
                    pending_trades.remove(pending)
                    continue
                
                # Check for multi-leg patterns
                if self.is_vertical_spread(trade, pending):
                    strategies.append({
                        'type': 'vertical_spread',
                        'legs': [trade, pending]
                    })
                elif self.is_straddle(trade, pending):
                    strategies.append({
                        'type': 'straddle',
                        'legs': [trade, pending]
                    })
        
        # Add current trade to pending
        if symbol not in self.pending_trades:
            self.pending_trades[symbol] = []
        self.pending_trades[symbol].append(trade)
        
        return strategies
    
    def is_vertical_spread(self, trade1, trade2):
        # Same expiration, different strikes, opposite directions
        return (trade1['expiration'] == trade2['expiration'] and
                trade1['strike'] != trade2['strike'] and
                trade1['option_type'] == trade2['option_type'] and
                ((trade1['side'] == 'buy' and trade2['side'] == 'sell') or
                 (trade1['side'] == 'sell' and trade2['side'] == 'buy')))
    
    def is_straddle(self, trade1, trade2):
        # Same expiration, same strike, one call one put
        return (trade1['expiration'] == trade2['expiration'] and
                trade1['strike'] == trade2['strike'] and
                trade1['option_type'] != trade2['option_type'])
```

## Implementation Roadmap

### Week 1-2: Foundation
1. Set up data feed connection (OPRA or vendor API)
2. Implement basic trade processing pipeline
3. Create volume anomaly detection
4. Build simple alerting system

### Week 3-4: Advanced Features
1. Add aggression detection
2. Implement scoring system
3. Create multi-leg detection
4. Build dashboard for visualization

### Week 5-6: Optimization
1. Backtest scoring thresholds
2. Optimize processing performance
3. Add machine learning enhancements
4. Implement risk controls

### Week 7-8: Production
1. Deploy monitoring system
2. Set up alert delivery channels
3. Create documentation
4. Establish review processes

## Common Pitfalls to Avoid

1. **Over-optimization**: Don't curve-fit to historical data
2. **Ignoring market context**: Consider overall market conditions
3. **Missing false positives**: Implement robust validation
4. **Latency issues**: Optimize for real-time processing
5. **Data quality**: Validate incoming data streams

## Performance Benchmarks

- **Processing Latency**: < 50ms per trade
- **Alert Accuracy**: > 70% precision rate
- **System Uptime**: > 99.5% availability
- **Memory Usage**: < 1GB for 1000-trade window

## Next Steps

1. Start with simple volume anomaly detection
2. Gradually add complexity (aggression, scoring, multi-leg)
3. Continuously validate against market outcomes
4. Adjust thresholds based on performance metrics
5. Consider adding ML for pattern recognition

Remember: The most effective systems combine quantitative rigor with qualitative market understanding. Start simple, validate thoroughly, and iterate based on real-world performance.