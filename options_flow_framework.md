# Programmatic Options Flow Analysis Framework

## Executive Summary
This framework provides a systematic approach to programmatically analyzing options flow data like professional traders. It covers key metrics, detection algorithms, scoring systems, and practical implementation strategies for identifying meaningful signals in options market activity.

## 1. Key Metrics to Track

### Volume vs Open Interest Analysis
- **Volume**: Number of contracts traded in current session
- **Open Interest**: Total outstanding contracts (updated daily)
- **Critical Ratio**: Volume / Open Interest
  - Ratio > 1: New positions being established
  - Ratio > 3: Highly unusual activity
  - Ratio > 10: Extreme positioning change

### Premium Spent Analysis
- **Total Premium**: Contract size × Price × 100
- **Premium Thresholds**:
  - $100k+: Significant institutional interest
  - $1M+: Major positioning
  - $10M+: Whale-level activity

### Bid vs Ask Fills
- **At Ask (A)**: Buyer willing to pay market price (aggressive buying)
- **Above Ask (AA)**: Buyer paying premium for urgency (very aggressive)
- **At Bid (B)**: Seller accepting market price (aggressive selling)
- **Below Bid (BB)**: Seller accepting discount for urgency (very aggressive)

## 2. Unusual Activity Detection Algorithms

### Statistical Methods
```python
# Z-Score Calculation for Volume Anomalies
def calculate_z_score(current_volume, historical_volumes):
    mean_volume = np.mean(historical_volumes)
    std_volume = np.std(historical_volumes)
    z_score = (current_volume - mean_volume) / std_volume
    return z_score

# Thresholds for Unusual Activity
UNUSUAL_THRESHOLDS = {
    'moderate': 2.0,    # 2 standard deviations
    'high': 3.0,        # 3 standard deviations
    'extreme': 5.0      # 5 standard deviations
}
```

### Volume Multiples Detection
- **Volume > 5× Average Daily Volume**: Unusual
- **Volume > 10× Open Interest**: Extremely unusual
- **Volume > 20× Average Volume**: Major event

### Time-Series Anomaly Detection
- Use rolling windows (30-60 minutes) for real-time analysis
- Apply Modified Z-Score for skewed distributions
- Implement IQR (Interquartile Range) for robust outlier detection

## 3. Aggressive Fills Detection

### Call Options Aggression
```python
def detect_aggressive_call_fill(trade_price, ask_price):
    if trade_price > ask_price:
        return 'AA'  # Above Ask (very aggressive)
    elif trade_price == ask_price:
        return 'A'   # At Ask (aggressive)
    else:
        return 'N'   # Normal
    
# Aggressive call buying suggests bullish conviction
```

### Put Options Aggression
```python
def detect_aggressive_put_fill(trade_price, bid_price):
    if trade_price < bid_price:
        return 'BB'  # Below Bid (very aggressive)
    elif trade_price == bid_price:
        return 'B'   # At Bid (aggressive)
    else:
        return 'N'   # Normal
    
# Aggressive put buying suggests bearish conviction
```

### Golden Sweep Detection
- Premium > $1M
- Execution at AA (calls) or BB (puts)
- Days to Expiration < 45
- High urgency signature

## 4. Smart Money Signatures

### Block Trade Identification
- **Size Threshold**: > 1,000 contracts
- **Premium Threshold**: > $500,000
- **Execution Pattern**: Single large transaction vs broken into smaller lots

### Sweep Order Detection
- Multiple legs executed simultaneously
- Across multiple exchanges
- Within milliseconds of each other
- Total premium exceeding thresholds

### Institutional Patterns
1. **Opening Position**: Large blocks at market open
2. **Hedging Activity**: Puts bought during rallies, calls during declines
3. **Rolling Positions**: Closing near-expiry, opening further-dated
4. **Gamma Hedging**: Large volumes at specific strikes

## 5. Noise Filtering

### Market Maker vs Directional
```python
def classify_trader_type(trade_data):
    # Market Maker Characteristics
    if (trade_data['size'] < 100 and 
        trade_data['premium'] < 10000 and
        trade_data['time_between_trades'] < 1.0):
        return 'market_maker'
    
    # Directional Trader Characteristics
    elif (trade_data['size'] > 500 or
          trade_data['premium'] > 100000 or
          trade_data['aggression'] in ['AA', 'BB']):
        return 'directional'
    
    return 'unknown'
```

### Hedging vs Speculative
- **Hedging**: Puts bought during uptrends, calls during downtrends
- **Speculative**: Directional alignment with price action
- **Spread Trading**: Multi-leg strategies indicating defined risk

### Time-Based Filtering
- Filter out end-of-day position squaring
- Identify opening bell positioning
- Monitor power hour (3-4 PM ET) activity

## 6. Time-of-Day Patterns

### Market Session Analysis
```python
MARKET_SESSIONS = {
    'pre_market': ('04:00', '09:30'),
    'opening_bell': ('09:30', '10:30'),
    'morning_session': ('10:30', '12:00'),
    'lunch_lull': ('12:00', '13:00'),
    'afternoon_session': ('13:00', '15:00'),
    'power_hour': ('15:00', '16:00'),
    'after_hours': ('16:00', '20:00')
}

def get_session_metrics(flow_data, session):
    session_flow = filter_by_time(flow_data, session)
    return {
        'total_volume': sum(session_flow['volume']),
        'call_put_ratio': calculate_cpr(session_flow),
        'avg_premium': np.mean(session_flow['premium']),
        'aggression_score': calculate_aggression(session_flow)
    }
```

### Key Patterns
1. **Opening Bell (9:30-10:30 AM ET)**: Institutional positioning
2. **Lunch Lull (12:00-1:00 PM ET)**: Reduced activity
3. **Power Hour (3:00-4:00 PM ET)**: Last-minute positioning
4. **After Hours**: Earnings/News reactions

## 7. Greeks Analysis

### Delta Analysis (Directional Bias)
```python
def analyze_delta_exposure(flow_data):
    # High Delta (>0.70): Strong directional conviction
    # Moderate Delta (0.30-0.70): Directional with some hedging
    # Low Delta (<0.30): Volatility or hedging play
    
    delta_buckets = {
        'high_directional': flow_data[flow_data['delta'] > 0.70],
        'moderate_directional': flow_data[(flow_data['delta'] >= 0.30) & (flow_data['delta'] <= 0.70)],
        'low_directional': flow_data[flow_data['delta'] < 0.30]
    }
    return delta_buckets
```

### Vega Analysis (Volatility Plays)
- **High Vega (>0.30)**: Volatility speculation
- **Low Vega (<0.10)**: Directional focus
- **Vega/Delta Ratio**: Volatility vs directional emphasis

### Theta Analysis (Time Decay)
- **High Theta**: Short-dated options (accelerated decay)
- **Low Theta**: Long-dated options (slow decay)
- **Theta/Price Ratio**: Time decay relative to premium

## 8. Multi-Leg Detection

### Strategy Identification Algorithms
```python
def detect_multi_leg_strategies(trades):
    strategies = []
    
    # Vertical Spread Detection
    for trade in trades:
        # Same expiration, different strikes
        matching_trades = find_matching_trades(trade, trades)
        if len(matching_trades) >= 1:
            if is_vertical_spread(trade, matching_trades[0]):
                strategies.append({
                    'type': 'vertical_spread',
                    'legs': [trade, matching_trades[0]]
                })
    
    # Straddle/Strangle Detection
    straddle_candidates = find_straddle_candidates(trades)
    for candidate in straddle_candidates:
        strategies.append({
            'type': 'straddle',
            'legs': candidate
        })
    
    return strategies
```

### Common Multi-Leg Patterns
1. **Vertical Spreads**: Same expiration, different strikes
2. **Calendar Spreads**: Different expirations, same strike
3. **Straddles**: Same strike, both calls and puts
4. **Strangles**: Different strikes, both calls and puts
5. **Iron Condors**: Four-leg defined risk strategies
6. **Collars**: Protective puts + covered calls

## 9. Flow Strength Scoring System

### Weighted Scoring Framework
```python
class FlowScorer:
    def __init__(self):
        self.weights = {
            'volume_ratio': 0.20,
            'premium_size': 0.25,
            'aggression_level': 0.20,
            'greeks_strength': 0.15,
            'time_pattern': 0.10,
            'smart_money_score': 0.10
        }
    
    def calculate_score(self, flow_data):
        scores = {}
        
        # Volume Ratio Score (0-100)
        volume_ratio = flow_data['volume'] / flow_data['open_interest']
        scores['volume_ratio'] = min(100, volume_ratio * 10)
        
        # Premium Size Score (0-100)
        premium_score = min(100, flow_data['premium'] / 10000)
        scores['premium_size'] = premium_score
        
        # Aggression Score (0-100)
        aggression_map = {'N': 0, 'A': 50, 'B': 50, 'AA': 100, 'BB': 100}
        scores['aggression_level'] = aggression_map.get(flow_data['aggression'], 0)
        
        # Greeks Strength Score (0-100)
        greeks_score = self.calculate_greeks_score(flow_data)
        scores['greeks_strength'] = greeks_score
        
        # Time Pattern Score (0-100)
        time_score = self.calculate_time_score(flow_data)
        scores['time_pattern'] = time_score
        
        # Smart Money Score (0-100)
        smart_money_score = self.calculate_smart_money_score(flow_data)
        scores['smart_money_score'] = smart_money_score
        
        # Weighted Total Score
        total_score = sum(scores[key] * self.weights[key] for key in scores)
        return total_score
```

### Score Interpretation
- **0-30**: Weak signal, likely noise
- **31-60**: Moderate signal, worth monitoring
- **61-80**: Strong signal, consider position
- **81-100**: Very strong signal, high conviction

## 10. Real-Time vs End-of-Day Analysis

### Real-Time Processing Architecture
```python
class RealTimeFlowProcessor:
    def __init__(self):
        self.window_size = 30  # minutes
        self.alert_threshold = 75  # score threshold
        self.recent_flow = deque(maxlen=1000)
    
    def process_tick(self, trade_data):
        # Add to recent flow
        self.recent_flow.append(trade_data)
        
        # Calculate rolling metrics
        window_data = self.get_window_data()
        
        # Detect anomalies
        if self.detect_anomaly(window_data):
            score = self.calculate_flow_score(trade_data)
            if score > self.alert_threshold:
                self.generate_alert(trade_data, score)
        
        # Update dashboards
        self.update_dashboards(trade_data)
```

### End-of-Day Analysis
```python
class EndOfDayAnalyzer:
    def __init__(self):
        self.daily_metrics = {}
    
    def analyze_daily_flow(self, daily_data):
        # Aggregate daily metrics
        metrics = {
            'total_volume': sum(daily_data['volume']),
            'total_premium': sum(daily_data['premium']),
            'call_put_ratio': self.calculate_cpr(daily_data),
            'top_trades': self.get_top_trades(daily_data, n=10),
            'sector_analysis': self.analyze_by_sector(daily_data),
            'pattern_recognition': self.identify_patterns(daily_data)
        }
        
        # Compare with historical
        historical_context = self.compare_with_history(metrics)
        
        # Generate insights
        insights = self.generate_insights(metrics, historical_context)
        
        return {
            'metrics': metrics,
            'historical_context': historical_context,
            'insights': insights
        }
```

### Implementation Considerations

#### Data Sources
1. **Real-Time Feeds**: OPRA (Options Price Reporting Authority)
2. **Historical Data**: CBOE, NASDAQ, proprietary vendors
3. **Alternative Data**: Dark pool prints, exchange messages

#### Processing Requirements
- **Latency**: < 100ms for real-time alerts
- **Throughput**: Handle 1000+ trades/second
- **Storage**: Time-series database for historical analysis

#### Risk Management
- **False Positive Rate**: Target < 5%
- **Backtesting**: Validate against historical outcomes
- **Position Sizing**: Scale with signal strength

## 11. Practical Implementation Checklist

### Phase 1: Foundation
- [ ] Set up data pipeline (real-time + historical)
- [ ] Implement basic metrics calculation
- [ ] Create anomaly detection baseline

### Phase 2: Advanced Features
- [ ] Add multi-leg detection
- [ ] Implement scoring system
- [ ] Develop alerting framework

### Phase 3: Optimization
- [ ] Backtest scoring thresholds
- [ ] Optimize processing latency
- [ ] Add machine learning enhancements

### Phase 4: Production
- [ ] Deploy monitoring dashboards
- [ ] Implement risk controls
- [ ] Establish review processes

## 12. Key Performance Indicators

### Signal Quality Metrics
- **Precision**: % of alerts that lead to profitable moves
- **Recall**: % of significant moves captured by alerts
- **Signal-to-Noise Ratio**: Meaningful signals vs false positives

### Operational Metrics
- **Processing Latency**: Time from trade to alert
- **System Uptime**: Availability percentage
- **Data Completeness**: % of market captured

## Conclusion

This framework provides a comprehensive approach to programmatic options flow analysis. By systematically tracking key metrics, implementing robust detection algorithms, and applying weighted scoring systems, traders can identify high-probability trading opportunities while filtering out market noise.

The most effective implementations combine statistical rigor with market microstructure understanding, continuously adapting to changing market conditions while maintaining disciplined risk management practices.