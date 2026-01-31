#!/usr/bin/env python3
"""
Order Block Detector
Identifies institutional supply/demand zones from price/volume data
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import json

try:
    from alpaca.data.historical import StockHistoricalDataClient, CryptoHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest, CryptoBarsRequest
    from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
    import pandas as pd
    import numpy as np
except ImportError:
    print("ERROR: Required packages not installed.")
    print("Install with: pip install alpaca-py pandas numpy")
    sys.exit(1)


class OrderBlock:
    """Represents a detected order block zone"""
    
    def __init__(self, ob_type: str, candle_index: int, timestamp: datetime,
                 zone_low: float, zone_high: float, strength: int,
                 volume_ratio: float, impulse_pct: float):
        self.type = ob_type  # 'bullish' or 'bearish'
        self.candle_index = candle_index
        self.timestamp = timestamp
        self.zone_low = zone_low
        self.zone_high = zone_high
        self.strength = strength
        self.volume_ratio = volume_ratio
        self.impulse_pct = impulse_pct
        self.adjusted_strength = strength
        self.age_candles = 0
    
    def to_dict(self) -> Dict:
        return {
            'type': self.type,
            'zone_high': round(self.zone_high, 2),
            'zone_low': round(self.zone_low, 2),
            'strength': self.strength,
            'adjusted_strength': round(self.adjusted_strength, 1),
            'age_candles': self.age_candles,
            'timestamp': self.timestamp.isoformat(),
            'volume_ratio': round(self.volume_ratio, 2),
            'impulse_pct': round(self.impulse_pct, 2),
            'notes': self._generate_notes()
        }
    
    def _generate_notes(self) -> str:
        age_desc = "Fresh" if self.age_candles <= 5 else "Recent" if self.age_candles <= 20 else "Older"
        strength_desc = "Strong" if self.strength >= 8 else "Moderate" if self.strength >= 6 else "Weak"
        zone_type = "supply zone" if self.type == "bearish" else "demand zone"
        return f"{age_desc} {zone_type.lower()} with {strength_desc.lower()} institutional footprint"


class OrderBlockDetector:
    """Main detector class"""
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        # Get API credentials from env or parameters
        self.api_key = api_key or os.getenv('ALPACA_API_KEY')
        self.api_secret = api_secret or os.getenv('ALPACA_API_SECRET')
        
        if not self.api_key or not self.api_secret:
            raise ValueError("Alpaca API credentials required. Set ALPACA_API_KEY and ALPACA_API_SECRET env vars.")
        
        # Initialize Alpaca clients
        self.stock_client = StockHistoricalDataClient(self.api_key, self.api_secret)
        self.crypto_client = CryptoHistoricalDataClient(self.api_key, self.api_secret)
        
        # Detection parameters
        self.params = {
            'lookback_candles': 100,
            'impulse_threshold_pct': 2.0,
            'volume_spike_min': 1.5,
            'consolidation_window': 10,
            'consolidation_atr_factor': 0.8,
            'followthrough_candles': 3,
            'min_strength': 5,
            'zone_extension_pct': 0.1,
            'max_order_blocks': 10,
        }
    
    def detect(self, symbol: str, timeframe: str = '1h', asset_type: str = 'stock') -> Dict:
        """
        Main detection method
        
        Args:
            symbol: Trading symbol (e.g., 'AAPL', 'BTC/USD')
            timeframe: Candle timeframe ('1m', '5m', '15m', '1h', '4h', '1d')
            asset_type: 'stock' or 'crypto'
        
        Returns:
            Dictionary with detected order blocks
        """
        print(f"\n🔍 Analyzing {symbol} on {timeframe} timeframe...")
        
        # Fetch data
        df = self._fetch_data(symbol, timeframe, asset_type)
        if df is None or len(df) < 50:
            return self._empty_result(symbol, timeframe, "Insufficient data")
        
        print(f"✓ Fetched {len(df)} candles")
        
        # Calculate indicators
        df = self._calculate_indicators(df)
        
        # Detect order blocks
        order_blocks = self._scan_for_order_blocks(df)
        
        # Apply time decay
        current_index = len(df) - 1
        for ob in order_blocks:
            ob.age_candles = current_index - ob.candle_index
            ob.adjusted_strength = self._apply_time_decay(ob.strength, ob.age_candles)
        
        # Filter by minimum strength
        order_blocks = [ob for ob in order_blocks if ob.adjusted_strength >= self.params['min_strength']]
        
        # Remove overlapping zones
        order_blocks = self._remove_overlaps(order_blocks)
        
        # Sort by adjusted strength (descending)
        order_blocks.sort(key=lambda x: x.adjusted_strength, reverse=True)
        
        # Limit to max count
        order_blocks = order_blocks[:self.params['max_order_blocks']]
        
        print(f"✓ Detected {len(order_blocks)} order blocks (strength >= {self.params['min_strength']})")
        
        # Build result
        result = {
            'symbol': symbol,
            'timeframe': timeframe,
            'analyzed_at': datetime.utcnow().isoformat(),
            'current_price': float(df['close'].iloc[-1]),
            'order_blocks': [ob.to_dict() for ob in order_blocks],
            'summary': self._generate_summary(order_blocks, float(df['close'].iloc[-1]))
        }
        
        return result
    
    def _fetch_data(self, symbol: str, timeframe: str, asset_type: str) -> Optional[pd.DataFrame]:
        """Fetch OHLCV data from Alpaca"""
        try:
            # Parse timeframe
            tf_map = {
                '1m': TimeFrame(1, TimeFrameUnit.Minute),
                '5m': TimeFrame(5, TimeFrameUnit.Minute),
                '15m': TimeFrame(15, TimeFrameUnit.Minute),
                '1h': TimeFrame(1, TimeFrameUnit.Hour),
                '4h': TimeFrame(4, TimeFrameUnit.Hour),
                '1d': TimeFrame(1, TimeFrameUnit.Day),
            }
            
            tf = tf_map.get(timeframe)
            if not tf:
                print(f"❌ Invalid timeframe: {timeframe}")
                return None
            
            # Calculate start date (enough history for lookback)
            lookback_multiplier = 2  # Fetch 2x the lookback period for indicator warmup
            if timeframe == '1m':
                start = datetime.utcnow() - timedelta(hours=self.params['lookback_candles'] * lookback_multiplier / 60)
            elif timeframe == '5m':
                start = datetime.utcnow() - timedelta(hours=self.params['lookback_candles'] * lookback_multiplier * 5 / 60)
            elif timeframe == '15m':
                start = datetime.utcnow() - timedelta(hours=self.params['lookback_candles'] * lookback_multiplier * 15 / 60)
            elif timeframe == '1h':
                start = datetime.utcnow() - timedelta(hours=self.params['lookback_candles'] * lookback_multiplier)
            elif timeframe == '4h':
                start = datetime.utcnow() - timedelta(hours=self.params['lookback_candles'] * lookback_multiplier * 4)
            else:  # 1d
                start = datetime.utcnow() - timedelta(days=self.params['lookback_candles'] * lookback_multiplier)
            
            end = datetime.utcnow()
            
            # Fetch data based on asset type
            if asset_type == 'crypto':
                request = CryptoBarsRequest(
                    symbol_or_symbols=symbol,
                    timeframe=tf,
                    start=start,
                    end=end
                )
                bars = self.crypto_client.get_crypto_bars(request)
            else:  # stock
                request = StockBarsRequest(
                    symbol_or_symbols=symbol,
                    timeframe=tf,
                    start=start,
                    end=end
                )
                bars = self.stock_client.get_stock_bars(request)
            
            # Convert to DataFrame
            df = bars.df
            
            # Reset index if multi-index (symbol, timestamp)
            if isinstance(df.index, pd.MultiIndex):
                df = df.reset_index(level=0, drop=True)
            
            return df
        
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            return None
    
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        # Volume moving average (20-period)
        df['volume_ma'] = df['volume'].rolling(window=20).mean()
        
        # ATR (14-period)
        df['tr'] = np.maximum(
            df['high'] - df['low'],
            np.maximum(
                abs(df['high'] - df['close'].shift(1)),
                abs(df['low'] - df['close'].shift(1))
            )
        )
        df['atr'] = df['tr'].rolling(window=14).mean()
        
        # Price change percentage
        df['pct_change'] = df['close'].pct_change() * 100
        
        # Volume ratio
        df['volume_ratio'] = df['volume'] / df['volume_ma']
        
        return df
    
    def _scan_for_order_blocks(self, df: pd.DataFrame) -> List[OrderBlock]:
        """Scan for order block patterns"""
        order_blocks = []
        
        # Start from 20th candle (allow indicator warmup) and stop before last few candles
        for i in range(20, len(df) - 10):
            # Check for bullish order block
            bullish_ob = self._check_bullish_order_block(df, i)
            if bullish_ob:
                order_blocks.append(bullish_ob)
            
            # Check for bearish order block
            bearish_ob = self._check_bearish_order_block(df, i)
            if bearish_ob:
                order_blocks.append(bearish_ob)
        
        return order_blocks
    
    def _check_bullish_order_block(self, df: pd.DataFrame, i: int) -> Optional[OrderBlock]:
        """Check if candle i is a bullish order block"""
        # Check if this candle is bearish (close < open)
        if df['close'].iloc[i] >= df['open'].iloc[i]:
            return None
        
        # Check consolidation before this candle
        if not self._has_consolidation(df, i):
            return None
        
        # Check for bullish impulse after this candle (next 1-4 candles)
        impulse_data = self._check_bullish_impulse(df, i)
        if not impulse_data:
            return None
        
        impulse_pct, max_volume_ratio = impulse_data
        
        # Validate volume spike
        volume_score = self._get_volume_score(max_volume_ratio)
        if volume_score == 0:
            return None
        
        # Check follow-through
        followthrough_score = self._check_bullish_followthrough(df, i + 4)
        
        # Calculate strength
        impulse_score = self._get_impulse_score(impulse_pct)
        consolidation_score = 2 if self._has_tight_consolidation(df, i) else 1
        
        strength = volume_score + impulse_score + consolidation_score + followthrough_score
        strength = min(strength, 10)
        
        # Define zone
        zone_high = df['high'].iloc[i]
        zone_low = df['low'].iloc[i]
        zone_range = zone_high - zone_low
        
        # Extend zone slightly
        zone_high += zone_range * self.params['zone_extension_pct']
        zone_low -= zone_range * self.params['zone_extension_pct']
        
        return OrderBlock(
            ob_type='bullish',
            candle_index=i,
            timestamp=df.index[i],
            zone_low=zone_low,
            zone_high=zone_high,
            strength=strength,
            volume_ratio=max_volume_ratio,
            impulse_pct=impulse_pct
        )
    
    def _check_bearish_order_block(self, df: pd.DataFrame, i: int) -> Optional[OrderBlock]:
        """Check if candle i is a bearish order block"""
        # Check if this candle is bullish (close > open)
        if df['close'].iloc[i] <= df['open'].iloc[i]:
            return None
        
        # Check consolidation before this candle
        if not self._has_consolidation(df, i):
            return None
        
        # Check for bearish impulse after this candle
        impulse_data = self._check_bearish_impulse(df, i)
        if not impulse_data:
            return None
        
        impulse_pct, max_volume_ratio = impulse_data
        
        # Validate volume spike
        volume_score = self._get_volume_score(max_volume_ratio)
        if volume_score == 0:
            return None
        
        # Check follow-through
        followthrough_score = self._check_bearish_followthrough(df, i + 4)
        
        # Calculate strength
        impulse_score = self._get_impulse_score(abs(impulse_pct))
        consolidation_score = 2 if self._has_tight_consolidation(df, i) else 1
        
        strength = volume_score + impulse_score + consolidation_score + followthrough_score
        strength = min(strength, 10)
        
        # Define zone
        zone_high = df['high'].iloc[i]
        zone_low = df['low'].iloc[i]
        zone_range = zone_high - zone_low
        
        # Extend zone
        zone_high += zone_range * self.params['zone_extension_pct']
        zone_low -= zone_range * self.params['zone_extension_pct']
        
        return OrderBlock(
            ob_type='bearish',
            candle_index=i,
            timestamp=df.index[i],
            zone_low=zone_low,
            zone_high=zone_high,
            strength=strength,
            volume_ratio=max_volume_ratio,
            impulse_pct=impulse_pct
        )
    
    def _has_consolidation(self, df: pd.DataFrame, i: int) -> bool:
        """Check if price consolidated before candle i"""
        window = min(self.params['consolidation_window'], i)
        if window < 3:
            return False
        
        # Check ATR in consolidation window
        avg_atr = df['atr'].iloc[i-window:i].mean()
        current_atr = df['atr'].iloc[i]
        
        if pd.isna(avg_atr) or pd.isna(current_atr):
            return False
        
        # Also check for large moves in consolidation period
        max_pct_change = df['pct_change'].iloc[i-window:i].abs().max()
        
        return max_pct_change < 2.0  # No single move >2% in consolidation
    
    def _has_tight_consolidation(self, df: pd.DataFrame, i: int) -> bool:
        """Check if consolidation was particularly tight"""
        window = min(self.params['consolidation_window'], i)
        if window < 3:
            return False
        
        avg_atr_14 = df['atr'].iloc[i]
        avg_atr_window = df['atr'].iloc[i-window:i].mean()
        
        if pd.isna(avg_atr_14) or pd.isna(avg_atr_window):
            return False
        
        return avg_atr_window < (avg_atr_14 * 0.7)
    
    def _check_bullish_impulse(self, df: pd.DataFrame, i: int) -> Optional[Tuple[float, float]]:
        """Check for bullish impulse after candle i"""
        if i + 4 >= len(df):
            return None
        
        # Check next 1-4 candles for strong upward move
        start_price = df['close'].iloc[i]
        max_volume_ratio = 0
        
        for j in range(i+1, min(i+5, len(df))):
            end_price = df['close'].iloc[j]
            price_change_pct = ((end_price - start_price) / start_price) * 100
            
            # Track max volume ratio in impulse window
            if not pd.isna(df['volume_ratio'].iloc[j]):
                max_volume_ratio = max(max_volume_ratio, df['volume_ratio'].iloc[j])
            
            # Check if impulse threshold met
            if price_change_pct >= self.params['impulse_threshold_pct']:
                # Verify no major pullback
                pullback = self._check_pullback_bullish(df, i+1, j)
                if not pullback:
                    return (price_change_pct, max_volume_ratio)
        
        return None
    
    def _check_bearish_impulse(self, df: pd.DataFrame, i: int) -> Optional[Tuple[float, float]]:
        """Check for bearish impulse after candle i"""
        if i + 4 >= len(df):
            return None
        
        start_price = df['close'].iloc[i]
        max_volume_ratio = 0
        
        for j in range(i+1, min(i+5, len(df))):
            end_price = df['close'].iloc[j]
            price_change_pct = ((end_price - start_price) / start_price) * 100
            
            if not pd.isna(df['volume_ratio'].iloc[j]):
                max_volume_ratio = max(max_volume_ratio, df['volume_ratio'].iloc[j])
            
            if price_change_pct <= -self.params['impulse_threshold_pct']:
                pullback = self._check_pullback_bearish(df, i+1, j)
                if not pullback:
                    return (price_change_pct, max_volume_ratio)
        
        return None
    
    def _check_pullback_bullish(self, df: pd.DataFrame, start: int, end: int) -> bool:
        """Check if there was a major pullback during bullish impulse"""
        move_size = df['close'].iloc[end] - df['close'].iloc[start]
        for k in range(start, end):
            drop = df['close'].iloc[start] - df['close'].iloc[k]
            if drop > (move_size * 0.5):  # Pullback >50% of move
                return True
        return False
    
    def _check_pullback_bearish(self, df: pd.DataFrame, start: int, end: int) -> bool:
        """Check if there was a major bounce during bearish impulse"""
        move_size = abs(df['close'].iloc[end] - df['close'].iloc[start])
        for k in range(start, end):
            bounce = df['close'].iloc[k] - df['close'].iloc[start]
            if bounce > (move_size * 0.5):
                return True
        return False
    
    def _check_bullish_followthrough(self, df: pd.DataFrame, start_i: int) -> int:
        """Check follow-through after bullish impulse"""
        if start_i + 3 >= len(df):
            return 0
        
        continuation_count = 0
        for j in range(start_i, min(start_i + 3, len(df))):
            if df['close'].iloc[j] > df['close'].iloc[j-1]:
                continuation_count += 1
        
        if continuation_count >= 3:
            return 2
        elif continuation_count >= 2:
            return 1
        else:
            return 0
    
    def _check_bearish_followthrough(self, df: pd.DataFrame, start_i: int) -> int:
        """Check follow-through after bearish impulse"""
        if start_i + 3 >= len(df):
            return 0
        
        continuation_count = 0
        for j in range(start_i, min(start_i + 3, len(df))):
            if df['close'].iloc[j] < df['close'].iloc[j-1]:
                continuation_count += 1
        
        if continuation_count >= 3:
            return 2
        elif continuation_count >= 2:
            return 1
        else:
            return 0
    
    def _get_volume_score(self, volume_ratio: float) -> int:
        """Calculate volume score (0-3)"""
        if volume_ratio >= 3.0:
            return 3
        elif volume_ratio >= 2.0:
            return 2
        elif volume_ratio >= self.params['volume_spike_min']:
            return 1
        else:
            return 0
    
    def _get_impulse_score(self, impulse_pct: float) -> int:
        """Calculate impulse strength score (0-3)"""
        abs_pct = abs(impulse_pct)
        if abs_pct >= 5.0:
            return 3
        elif abs_pct >= 3.0:
            return 2
        elif abs_pct >= 2.0:
            return 1
        else:
            return 0
    
    def _apply_time_decay(self, strength: int, age: int) -> float:
        """Apply time decay to strength rating"""
        if age <= 5:
            decay_factor = 1.0
        elif age <= 20:
            decay_factor = 0.9
        elif age <= 50:
            decay_factor = 0.7
        else:
            decay_factor = 0.5
        
        return strength * decay_factor
    
    def _remove_overlaps(self, order_blocks: List[OrderBlock]) -> List[OrderBlock]:
        """Remove overlapping order blocks of same type, keep stronger ones"""
        filtered = []
        
        # Sort by strength (descending)
        sorted_obs = sorted(order_blocks, key=lambda x: x.strength, reverse=True)
        
        for ob in sorted_obs:
            overlaps = False
            for existing in filtered:
                if self._zones_overlap(ob, existing) and ob.type == existing.type:
                    overlaps = True
                    break
            
            if not overlaps:
                filtered.append(ob)
        
        return filtered
    
    def _zones_overlap(self, zone1: OrderBlock, zone2: OrderBlock) -> bool:
        """Check if two zones overlap in price"""
        return not (zone1.zone_high < zone2.zone_low or zone2.zone_high < zone1.zone_low)
    
    def _generate_summary(self, order_blocks: List[OrderBlock], current_price: float) -> str:
        """Generate human-readable summary"""
        if not order_blocks:
            return "No significant order blocks detected in current market conditions."
        
        bullish = [ob for ob in order_blocks if ob.type == 'bullish']
        bearish = [ob for ob in order_blocks if ob.type == 'bearish']
        
        summary_parts = []
        
        if bullish:
            closest_bullish = min(bullish, key=lambda x: abs(current_price - (x.zone_high + x.zone_low)/2))
            summary_parts.append(
                f"Bullish support at ${closest_bullish.zone_low:.2f}-${closest_bullish.zone_high:.2f} "
                f"(strength: {closest_bullish.adjusted_strength:.1f}/10)"
            )
        
        if bearish:
            closest_bearish = min(bearish, key=lambda x: abs(current_price - (x.zone_high + x.zone_low)/2))
            summary_parts.append(
                f"Bearish resistance at ${closest_bearish.zone_low:.2f}-${closest_bearish.zone_high:.2f} "
                f"(strength: {closest_bearish.adjusted_strength:.1f}/10)"
            )
        
        return " | ".join(summary_parts)
    
    def _empty_result(self, symbol: str, timeframe: str, reason: str) -> Dict:
        """Return empty result with reason"""
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'analyzed_at': datetime.utcnow().isoformat(),
            'order_blocks': [],
            'summary': f"No order blocks detected: {reason}"
        }


def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Detect order blocks from price data')
    parser.add_argument('symbol', help='Trading symbol (e.g., AAPL, BTC/USD)')
    parser.add_argument('--timeframe', '-t', default='1h', 
                       choices=['1m', '5m', '15m', '1h', '4h', '1d'],
                       help='Candle timeframe (default: 1h)')
    parser.add_argument('--asset-type', '-a', default='stock',
                       choices=['stock', 'crypto'],
                       help='Asset type (default: stock)')
    parser.add_argument('--min-strength', '-s', type=int, default=5,
                       help='Minimum strength rating to display (default: 5)')
    parser.add_argument('--output', '-o', help='Save output to JSON file')
    
    args = parser.parse_args()
    
    try:
        detector = OrderBlockDetector()
        detector.params['min_strength'] = args.min_strength
        
        result = detector.detect(args.symbol, args.timeframe, args.asset_type)
        
        # Print results
        print("\n" + "="*70)
        print(f"ORDER BLOCK ANALYSIS: {result['symbol']} ({result['timeframe']})")
        print("="*70)
        print(f"Current Price: ${result.get('current_price', 0):.2f}")
        print(f"Analyzed: {result['analyzed_at']}")
        print(f"\nSummary: {result['summary']}")
        print("\n" + "-"*70)
        
        if result['order_blocks']:
            print("\nDETECTED ORDER BLOCKS:")
            print("-"*70)
            
            for i, ob in enumerate(result['order_blocks'], 1):
                print(f"\n#{i} {ob['type'].upper()} ORDER BLOCK")
                print(f"  Zone: ${ob['zone_low']:.2f} - ${ob['zone_high']:.2f}")
                print(f"  Strength: {ob['strength']}/10 (adjusted: {ob['adjusted_strength']}/10)")
                print(f"  Age: {ob['age_candles']} candles")
                print(f"  Volume Ratio: {ob['volume_ratio']}x")
                print(f"  Impulse: {ob['impulse_pct']:.2f}%")
                print(f"  Time: {ob['timestamp']}")
                print(f"  Notes: {ob['notes']}")
        else:
            print("\nNo order blocks detected meeting minimum criteria.")
        
        print("\n" + "="*70 + "\n")
        
        # Save to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"✓ Results saved to {args.output}\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
