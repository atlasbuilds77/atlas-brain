# QuantVue Algorithms - Detailed Technical Breakdown

## Reverse Engineered Core Logic

Based on documentation analysis, this document reconstructs the likely algorithms behind QuantVue's trading systems.

---

## 1. QGRID INDICATOR

### Purpose
Identify trend direction and pullback entry points using dual Heiken Ashi smoothing.

### Algorithm (Pseudocode)

```python
def qgrid(candles, smooth_period_1=10, smooth_period_2=10, step_ma_sensitivity=5):
    """
    Qgrid: Dual Heiken Ashi with Step Moving Average
    """
    
    # Step 1: First Heiken Ashi Smoothing
    ha1_open = []
    ha1_close = []
    ha1_high = []
    ha1_low = []
    
    for i, candle in enumerate(candles):
        if i == 0:
            ha1_open.append((candle.open + candle.close) / 2)
        else:
            ha1_open.append((ha1_open[i-1] + ha1_close[i-1]) / 2)
        
        ha1_close.append((candle.open + candle.high + candle.low + candle.close) / 4)
        ha1_high.append(max(candle.high, ha1_open[-1], ha1_close[-1]))
        ha1_low.append(min(candle.low, ha1_open[-1], ha1_close[-1]))
    
    # Apply SMA smoothing to HA values
    ha1_open_smooth = sma(ha1_open, smooth_period_1)
    ha1_close_smooth = sma(ha1_close, smooth_period_1)
    
    # Step 2: Second Heiken Ashi Smoothing
    ha2_open = []
    ha2_close = []
    
    for i in range(len(ha1_open_smooth)):
        if i == 0:
            ha2_open.append((ha1_open_smooth[i] + ha1_close_smooth[i]) / 2)
        else:
            ha2_open.append((ha2_open[i-1] + ha2_close[i-1]) / 2)
        
        ha2_close.append((ha1_open_smooth[i] + ha1_close_smooth[i]) / 2)
    
    # Apply second smoothing
    ha2_open_smooth = sma(ha2_open, smooth_period_2)
    ha2_close_smooth = sma(ha2_close, smooth_period_2)
    
    # Step 3: Step Moving Average (for ADD signals)
    step_ma = calculate_step_ma(ha2_close_smooth, step_ma_sensitivity)
    
    # Step 4: Generate Signals
    signals = []
    for i in range(len(candles)):
        trend = "BULL" if ha2_close_smooth[i] > ha2_open_smooth[i] else "BEAR"
        
        # ADD signal: price pulls back to step MA during trend
        is_add = False
        if trend == "BULL" and candles[i].low <= step_ma[i] <= candles[i].high:
            is_add = True
        elif trend == "BEAR" and candles[i].low <= step_ma[i] <= candles[i].high:
            is_add = True
            
        signals.append({
            "trend": trend,
            "step_ma": step_ma[i],
            "add_signal": is_add
        })
    
    return signals

def calculate_step_ma(data, sensitivity):
    """
    Step MA: Only changes value when price moves beyond threshold
    """
    step_ma = [data[0]]
    threshold = sensitivity * calculate_atr(data, 14)[0]
    
    for i in range(1, len(data)):
        if abs(data[i] - step_ma[-1]) > threshold:
            step_ma.append(data[i])
        else:
            step_ma.append(step_ma[-1])
    
    return step_ma
```

---

## 2. QWAVE INDICATOR

### Purpose
Generate breakout alerts when price breaks ATR-based bands.

### Algorithm (Pseudocode)

```python
def qwave(candles, band_deviation=2.0, lookback=20):
    """
    Qwave: ATR-based breakout bands (Keltner Channel variant)
    """
    
    # Calculate base moving average
    base_ma = sma([c.close for c in candles], lookback)
    
    # Calculate ATR
    atr = calculate_atr(candles, lookback)
    
    # Calculate bands
    upper_band = []
    lower_band = []
    
    for i in range(len(candles)):
        upper_band.append(base_ma[i] + (band_deviation * atr[i]))
        lower_band.append(base_ma[i] - (band_deviation * atr[i]))
    
    # Generate alerts
    alerts = []
    for i in range(1, len(candles)):
        alert = None
        
        # BULL alert: price breaks above upper band
        if candles[i].close > upper_band[i] and candles[i-1].close <= upper_band[i-1]:
            alert = "BULL"
        
        # BEAR alert: price breaks below lower band
        elif candles[i].close < lower_band[i] and candles[i-1].close >= lower_band[i-1]:
            alert = "BEAR"
        
        # ADD alerts: continuation signals
        elif alert is None and i > 2:
            if alerts[i-1] == "BULL" and candles[i].close > upper_band[i]:
                alert = "ADD_LONG"
            elif alerts[i-1] == "BEAR" and candles[i].close < lower_band[i]:
                alert = "ADD_SHORT"
        
        alerts.append(alert)
    
    return alerts, upper_band, lower_band
```

---

## 3. QLINE INDICATOR

### Purpose
Adaptive trend ribbon (Supertrend variant)

### Algorithm (Pseudocode)

```python
def qline(candles, length=10, multiplier=3.0, reactivity=1):
    """
    Qline: Supertrend-style trend ribbon
    """
    
    # Calculate ATR
    atr = calculate_atr(candles, length)
    
    # Calculate basic upper and lower bands
    hl2 = [(c.high + c.low) / 2 for c in candles]
    
    basic_upper = [hl2[i] + (multiplier * atr[i]) for i in range(len(candles))]
    basic_lower = [hl2[i] - (multiplier * atr[i]) for i in range(len(candles))]
    
    # Calculate final bands with trend logic
    final_upper = [basic_upper[0]]
    final_lower = [basic_lower[0]]
    trend = [1]  # 1 = bullish, -1 = bearish
    
    for i in range(1, len(candles)):
        # Upper band logic
        if basic_upper[i] < final_upper[i-1] or candles[i-1].close > final_upper[i-1]:
            final_upper.append(basic_upper[i])
        else:
            final_upper.append(final_upper[i-1])
        
        # Lower band logic
        if basic_lower[i] > final_lower[i-1] or candles[i-1].close < final_lower[i-1]:
            final_lower.append(basic_lower[i])
        else:
            final_lower.append(final_lower[i-1])
        
        # Trend determination
        if trend[i-1] == 1:
            if candles[i].close < final_lower[i]:
                trend.append(-1)
            else:
                trend.append(1)
        else:
            if candles[i].close > final_upper[i]:
                trend.append(1)
            else:
                trend.append(-1)
    
    # Output ribbon (using appropriate band based on trend)
    ribbon = []
    for i in range(len(candles)):
        if trend[i] == 1:
            ribbon.append(final_lower[i])
        else:
            ribbon.append(final_upper[i])
    
    return ribbon, trend
```

---

## 4. QCLOUD INDICATOR

### Purpose
Step-based moving average cloud for trend visualization

### Algorithm (Pseudocode)

```python
def qcloud(candles, periods=[8, 13, 21, 34, 55], step_threshold=0.001):
    """
    Qcloud: Multiple step MAs forming a cloud
    Each MA only changes when price moves beyond threshold
    """
    
    closes = [c.close for c in candles]
    cloud_lines = []
    
    for period in periods:
        base_ma = sma(closes, period)
        step_ma = []
        
        for i in range(len(base_ma)):
            if i == 0:
                step_ma.append(base_ma[i])
            else:
                change_pct = abs(base_ma[i] - step_ma[-1]) / step_ma[-1]
                if change_pct > step_threshold:
                    step_ma.append(base_ma[i])
                else:
                    step_ma.append(step_ma[-1])
        
        cloud_lines.append(step_ma)
    
    # Determine overall cloud color
    cloud_direction = []
    for i in range(len(candles)):
        bullish_count = sum(1 for line in cloud_lines if closes[i] > line[i])
        if bullish_count > len(periods) / 2:
            cloud_direction.append("BULLISH")
        else:
            cloud_direction.append("BEARISH")
    
    return cloud_lines, cloud_direction
```

---

## 5. MONEYBALL OSCILLATOR

### Purpose
Momentum oscillator for detecting trend changes

### Algorithm (Pseudocode)

```python
def moneyball(candles, period=12):
    """
    Moneyball: MACD variant with enhanced visualization
    Likely similar to standard MACD but with different display
    """
    
    closes = [c.close for c in candles]
    
    # Standard MACD calculation
    fast_ema = ema(closes, period)
    slow_ema = ema(closes, period * 2)  # Typical 12/26 ratio
    
    macd_line = [fast_ema[i] - slow_ema[i] for i in range(len(closes))]
    signal_line = ema(macd_line, 9)
    histogram = [macd_line[i] - signal_line[i] for i in range(len(closes))]
    
    # Moneyball-specific: Normalize and detect "flips"
    flips = []
    for i in range(1, len(histogram)):
        if histogram[i] > 0 and histogram[i-1] <= 0:
            flips.append("BULL_FLIP")
        elif histogram[i] < 0 and histogram[i-1] >= 0:
            flips.append("BEAR_FLIP")
        else:
            flips.append(None)
    
    return histogram, flips
```

---

## 6. QZEUS STRATEGY

### Purpose
"Set and forget" automated trading with martingale

### Algorithm (Pseudocode)

```python
class QzeusStrategy:
    def __init__(self, config):
        self.stop_multiplier = config.get('stop_multiplier', 1.5)
        self.tp_multiplier = config.get('tp_multiplier', 2.0)
        self.use_martingale = config.get('use_martingale', False)
        self.use_range_boost = config.get('use_range_boost', True)
        self.range_boost_tp_multiplier = config.get('range_boost_tp', 3.0)
        self.max_contracts = config.get('max_contracts', 4)
        self.base_contracts = 1
        self.consecutive_losses = 0
        
    def calculate_volatility(self, candles):
        """
        Proprietary volatility calculation
        Likely ATR-based with modifications
        """
        atr = calculate_atr(candles, 14)[-1]
        # Additional factors are proprietary
        return atr
    
    def detect_range_condition(self, candles, lookback=20):
        """
        Detect if market is in range for Range Boost
        """
        highs = [c.high for c in candles[-lookback:]]
        lows = [c.low for c in candles[-lookback:]]
        range_size = max(highs) - min(lows)
        avg_range = sum([c.high - c.low for c in candles[-lookback:]]) / lookback
        
        # Range condition: tight consolidation
        return range_size < avg_range * 2
    
    def get_entry_signal(self, candles):
        """
        Entry logic - PROPRIETARY
        Based on documentation, likely uses:
        - Trend indicators (Qcloud/Qgrid direction)
        - Momentum (Moneyball flips)
        - Breakout detection (Qwave)
        """
        # This is the black box
        # Returns: "LONG", "SHORT", or None
        pass
    
    def calculate_position_size(self):
        """
        Martingale position sizing
        """
        if not self.use_martingale:
            return self.base_contracts
        
        size = self.base_contracts * (2 ** self.consecutive_losses)
        return min(size, self.max_contracts)
    
    def calculate_stops(self, entry_price, direction, candles):
        """
        Calculate stop loss and take profit
        """
        volatility = self.calculate_volatility(candles)
        
        # Check for range boost condition
        if self.use_range_boost and self.detect_range_condition(candles):
            tp_mult = self.range_boost_tp_multiplier
        else:
            tp_mult = self.tp_multiplier
        
        if direction == "LONG":
            stop_loss = entry_price - (volatility * self.stop_multiplier)
            take_profit = entry_price + (volatility * tp_mult)
        else:  # SHORT
            stop_loss = entry_price + (volatility * self.stop_multiplier)
            take_profit = entry_price - (volatility * tp_mult)
        
        return stop_loss, take_profit
    
    def on_trade_result(self, is_winner):
        """
        Update state after trade completes
        """
        if is_winner:
            self.consecutive_losses = 0
        else:
            self.consecutive_losses += 1
    
    def execute(self, candles, current_time, trading_times):
        """
        Main strategy execution loop
        """
        # Check time restrictions
        if not self.is_trading_time(current_time, trading_times):
            return None
        
        signal = self.get_entry_signal(candles)
        if signal is None:
            return None
        
        entry_price = candles[-1].close
        position_size = self.calculate_position_size()
        stop_loss, take_profit = self.calculate_stops(entry_price, signal, candles)
        
        return {
            "direction": signal,
            "size": position_size,
            "entry": entry_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit
        }
```

---

## 7. QKRONOS_EVO STRATEGY

### Purpose
Fully adjustable algorithm with dynamic volatility-based position management

### Algorithm (Pseudocode)

```python
class QkronosEvoStrategy:
    def __init__(self, config):
        # Volatility settings
        self.vol_length_offset = config.get('vol_length_offset', 0)
        self.coefficient_offsets = config.get('coefficient_offsets', [0, 0, 0])
        
        # Entry settings
        self.opening_methodology = config.get('methodology', 'ORIGINAL')  # ORIGINAL, EXPANDED, ALWAYS_IN
        self.use_ha_smoothing = config.get('ha_smoothing', True)
        self.use_qgrid_confluence = config.get('qgrid_confluence', False)
        self.exit_on_qgrid_switch = config.get('exit_on_qgrid', False)
        self.force_direction = config.get('force_direction', None)  # LONG, SHORT, None
        
        # Entry on pullback
        self.enter_on_pullback = config.get('pullback_entry', False)
        self.pullback_type = config.get('pullback_type', 'MULTIPLIER')  # TICKS, MULTIPLIER
        
        # Exit settings
        self.tp_methodology = config.get('tp_method', 'STATIC')  # STATIC, TRAILING, TIERED
        self.static_tp_multiplier = config.get('static_tp', 2.0)
        self.trail_engagement_multiplier = config.get('trail_engage', 1.0)
        self.trail_offset_multiplier = config.get('trail_offset', 0.5)
        
        # Tiered exits
        self.tiered_quantity = config.get('tiered_qty', 1)
        self.tiered_engagement = config.get('tiered_engage', 1.5)
        
        # Boost settings
        self.use_long_boost = config.get('long_boost', False)
        self.use_range_boost = config.get('range_boost', True)
        self.range_boost_threshold = config.get('range_threshold', 50)
        self.range_boost_tp = config.get('range_tp', 3.0)
        
        # Martingale
        self.use_martingale = config.get('martingale', False)
        self.max_contracts = config.get('max_contracts', 4)
    
    def calculate_volatility_multiplier(self, candles):
        """
        PROPRIETARY: Three-factor volatility calculation
        
        Based on documentation:
        - Factor 1: Technical (likely ATR-based)
        - Factor 2: Technical (likely price range based)
        - Factor 3: ML/Data analytics (likely optimized coefficients)
        """
        
        # Factor 1: ATR
        base_length = 14 + self.vol_length_offset
        atr = calculate_atr(candles, base_length)[-1]
        
        # Factor 2: Standard deviation of closes
        closes = [c.close for c in candles[-base_length:]]
        std_dev = statistics.stdev(closes)
        
        # Factor 3: Coefficient (the "ML" part - likely backtested optimal values)
        coeff_1 = 1.0 + self.coefficient_offsets[0]
        coeff_2 = 1.0 + self.coefficient_offsets[1]
        coeff_3 = 1.0 + self.coefficient_offsets[2]
        
        # Combine factors (formula is proprietary, this is an approximation)
        volatility = (atr * coeff_1 + std_dev * coeff_2) / 2 * coeff_3
        
        return volatility
    
    def get_entry_signal(self, candles):
        """
        Entry signal generation based on methodology
        """
        if self.use_ha_smoothing:
            candles = apply_heiken_ashi(candles)
        
        if self.opening_methodology == 'ORIGINAL':
            return self._original_entry(candles)
        elif self.opening_methodology == 'EXPANDED':
            return self._expanded_entry(candles)
        elif self.opening_methodology in ['ALWAYS_IN_ORIGINAL', 'ALWAYS_IN_EXPANDED']:
            return self._always_in_entry(candles)
    
    def _original_entry(self, candles):
        """
        Original: Fewer, higher-quality entries
        Likely based on trend + momentum confluence
        """
        qgrid_signal = calculate_qgrid(candles)
        moneyball = calculate_moneyball(candles)
        
        if qgrid_signal['trend'] == 'BULL' and moneyball['flip'] == 'BULL_FLIP':
            return 'LONG'
        elif qgrid_signal['trend'] == 'BEAR' and moneyball['flip'] == 'BEAR_FLIP':
            return 'SHORT'
        
        return None
    
    def _expanded_entry(self, candles):
        """
        Expanded: More entries with looser criteria
        """
        # Less restrictive confluence requirements
        pass
    
    def manage_position(self, position, current_candle, volatility):
        """
        Dynamic position management during trade
        """
        if self.tp_methodology == 'TRAILING':
            return self._trailing_stop_management(position, current_candle, volatility)
        elif self.tp_methodology == 'TIERED':
            return self._tiered_exit_management(position, current_candle, volatility)
        else:
            return None  # Static TP handles itself
    
    def _trailing_stop_management(self, position, current_candle, volatility):
        """
        Trailing stop logic
        """
        entry = position['entry']
        direction = position['direction']
        current_price = current_candle.close
        
        # Calculate profit in volatility units
        if direction == 'LONG':
            profit = current_price - entry
        else:
            profit = entry - current_price
        
        profit_in_vol_units = profit / volatility
        
        # Engage trailing stop
        if profit_in_vol_units >= self.trail_engagement_multiplier:
            new_stop = current_price - (volatility * self.trail_offset_multiplier) if direction == 'LONG' \
                else current_price + (volatility * self.trail_offset_multiplier)
            
            # Only move stop in favorable direction
            if direction == 'LONG' and new_stop > position.get('current_stop', 0):
                return {'action': 'UPDATE_STOP', 'new_stop': new_stop}
            elif direction == 'SHORT' and new_stop < position.get('current_stop', float('inf')):
                return {'action': 'UPDATE_STOP', 'new_stop': new_stop}
        
        return None
```

---

## 8. QSCALPER STRATEGY

### Purpose
Multiple scalping approaches for different market conditions

### Algorithm (Pseudocode)

```python
class QscalperStrategy:
    def __init__(self, config):
        self.scalp_type = config.get('type', 'REGULAR')  # REGULAR, FAST, VELOX, MB_CVD
        
        # Regular/Fast scalper settings
        self.box_lookback = config.get('box_lookback', 4)
        self.strength_coefficient = config.get('strength_coeff', 70)  # percentage
        self.proximity_coefficient = config.get('proximity_coeff', 5)
        
        # Velox settings
        self.sensitivity_factor = config.get('sensitivity', 1.0)
        self.hard_stop = config.get('hard_stop', True)
        self.hard_stop_multiplier = config.get('hard_stop_mult', 2.0)
        self.higher_box_filter = config.get('higher_box', None)
    
    def regular_scalper_entry(self, candles, qwave_data, qline_data):
        """
        Regular scalper: Trade bounces off Qwave/Qline S/R
        """
        current_price = candles[-1].close
        
        # Get support/resistance from Qwave/Qline
        support = qline_data['support']
        resistance = qline_data['resistance']
        
        # Check proximity to S/R
        near_support = abs(current_price - support) <= self.proximity_coefficient
        near_resistance = abs(current_price - resistance) <= self.proximity_coefficient
        
        if not (near_support or near_resistance):
            return None
        
        # Check strength (momentum into S/R)
        recent_candles = candles[-self.box_lookback:]
        if near_support:
            down_count = sum(1 for c in recent_candles if c.close < c.open)
            strength_met = (down_count / self.box_lookback) * 100 >= self.strength_coefficient
            if strength_met:
                return 'LONG'  # Bounce long off support
        
        if near_resistance:
            up_count = sum(1 for c in recent_candles if c.close > c.open)
            strength_met = (up_count / self.box_lookback) * 100 >= self.strength_coefficient
            if strength_met:
                return 'SHORT'  # Bounce short off resistance
        
        return None
    
    def velox_entry(self, candles, qcloud_higher_tf=None):
        """
        Velox: Sensitivity-based entries with optional higher TF confluence
        """
        # Check higher timeframe Qcloud for confluence
        if self.higher_box_filter and qcloud_higher_tf:
            if qcloud_higher_tf['direction'] == 'BULLISH':
                allowed_directions = ['LONG']
            elif qcloud_higher_tf['direction'] == 'BEARISH':
                allowed_directions = ['SHORT']
            else:
                allowed_directions = ['LONG', 'SHORT']
        else:
            allowed_directions = ['LONG', 'SHORT']
        
        # Velox entry logic (proprietary sensitivity calculation)
        # Likely momentum-based with adjustable threshold
        momentum = calculate_momentum(candles, period=5)
        threshold = self.sensitivity_factor * calculate_atr(candles, 14)[-1]
        
        if momentum[-1] > threshold and 'LONG' in allowed_directions:
            return 'LONG'
        elif momentum[-1] < -threshold and 'SHORT' in allowed_directions:
            return 'SHORT'
        
        return None
    
    def mb_cvd_entry(self, candles, moneyball_data, cvd_data):
        """
        MB/CVD: Confluence between Moneyball and CVD
        """
        mb_bullish = moneyball_data['histogram'][-1] > 0
        cvd_bullish = cvd_data[-1] > cvd_data[-2]  # CVD rising
        
        mb_bearish = moneyball_data['histogram'][-1] < 0
        cvd_bearish = cvd_data[-1] < cvd_data[-2]  # CVD falling
        
        if mb_bullish and cvd_bullish:
            return 'LONG'
        elif mb_bearish and cvd_bearish:
            return 'SHORT'
        
        return None
```

---

## Helper Functions

```python
def calculate_atr(candles, period):
    """Standard ATR calculation"""
    true_ranges = []
    for i in range(1, len(candles)):
        high = candles[i].high
        low = candles[i].low
        prev_close = candles[i-1].close
        
        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        true_ranges.append(tr)
    
    atr = []
    for i in range(len(true_ranges)):
        if i < period - 1:
            atr.append(None)
        else:
            atr.append(sum(true_ranges[i-period+1:i+1]) / period)
    
    return atr

def sma(data, period):
    """Simple Moving Average"""
    result = []
    for i in range(len(data)):
        if i < period - 1:
            result.append(None)
        else:
            result.append(sum(data[i-period+1:i+1]) / period)
    return result

def ema(data, period):
    """Exponential Moving Average"""
    multiplier = 2 / (period + 1)
    result = [data[0]]
    for i in range(1, len(data)):
        result.append((data[i] * multiplier) + (result[-1] * (1 - multiplier)))
    return result

def apply_heiken_ashi(candles):
    """Convert candles to Heiken Ashi"""
    ha_candles = []
    for i, c in enumerate(candles):
        if i == 0:
            ha_open = (c.open + c.close) / 2
        else:
            ha_open = (ha_candles[-1].open + ha_candles[-1].close) / 2
        
        ha_close = (c.open + c.high + c.low + c.close) / 4
        ha_high = max(c.high, ha_open, ha_close)
        ha_low = min(c.low, ha_open, ha_close)
        
        ha_candles.append(Candle(ha_open, ha_high, ha_low, ha_close))
    
    return ha_candles
```

---

## Key Technical Insights

### The "Proprietary" Parts
1. **Entry Signal Generation:** The exact conditions that trigger entries in Qzeus/Qkronos are hidden. Likely combinations of trend + momentum + volatility conditions.

2. **Volatility Multiplier Coefficients:** The "ML factor" is likely pre-optimized coefficients from backtesting, not real-time machine learning.

3. **Range Boost Detection:** The conditions that trigger Range Boost are proprietary but likely based on ATR compression or Bollinger Band squeeze concepts.

### What's NOT Proprietary
- All underlying indicators (ATR, EMA, MACD variants, Supertrend) are standard
- Martingale position sizing is textbook
- Heiken Ashi smoothing is public domain
- Keltner/ATR bands are standard

### The "Secret Sauce"
QuantVue's actual value-add is:
1. Pre-optimized parameters for futures markets
2. Integration of multiple indicators into cohesive systems
3. Packaging and usability
4. Community knowledge sharing
