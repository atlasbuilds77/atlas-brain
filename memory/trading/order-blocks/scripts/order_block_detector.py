#!/usr/bin/env python3
"""
Order Block Detection System
Detects bullish and bearish order blocks from price/volume data
Designed for atlas-trader integration
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import json

try:
    import pandas as pd
    import numpy as np
except ImportError:
    print("ERROR: Required packages not installed")
    print("Run: pip install pandas numpy")
    sys.exit(1)


class OrderBlock:
    """Represents a detected order block zone"""
    
    def __init__(self, block_type: str, start_price: float, end_price: float, 
                 timestamp: datetime, volume_ratio: float, price_move_pct: float,
                 candle_index: int):
        self.type = block_type  # 'bullish' or 'bearish'
        self.start_price = start_price  # Lower bound of zone
        self.end_price = end_price      # Upper bound of zone
        self.timestamp = timestamp
        self.volume_ratio = volume_ratio  # Volume vs average
        self.price_move_pct = price_move_pct  # Magnitude of move after block
        self.candle_index = candle_index
        self.tests = 0  # How many times price has tested this zone
        self.broken = False  # Has the zone been broken?
        self.strength = self._calculate_strength()
    
    def _calculate_strength(self) -> float:
        """Calculate order block strength (0-10 scale)"""
        score = 0.0
        
        # 1. Volume Intensity (30% weight)
        if self.volume_ratio >= 3.0:
            score += 3.0
        elif self.volume_ratio >= 2.0:
            score += 2.4
        elif self.volume_ratio >= 1.5:
            score += 1.5
        else:
            score += 0.9
        
        # 2. Price Movement Magnitude (25% weight)
        if abs(self.price_move_pct) >= 5.0:
            score += 2.5
        elif abs(self.price_move_pct) >= 3.0:
            score += 2.0
        elif abs(self.price_move_pct) >= 2.0:
            score += 1.5
        else:
            score += 0.8
        
        # 3. Time Since Formation (20% weight)
        ts = self.timestamp.replace(tzinfo=None) if hasattr(self.timestamp, 'tzinfo') and self.timestamp.tzinfo else self.timestamp
        age_days = (datetime.now() - ts).days
        if age_days < 7:
            score += 2.0
        elif age_days < 14:
            score += 1.6
        elif age_days < 30:
            score += 1.0
        else:
            score += 0.4
        
        # 4. Number of Tests (15% weight)
        if self.tests == 0:
            score += 1.5
        elif self.tests == 1:
            score += 1.2
        elif self.tests == 2:
            score += 0.8
        else:
            score += 0.3
        
        # 5. Placeholder for market structure (10% weight)
        # TODO: Add trend alignment check
        score += 1.0
        
        return round(min(score, 10.0), 1)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for output"""
        return {
            'type': self.type,
            'price_range': f"${self.start_price:.2f} - ${self.end_price:.2f}",
            'start_price': self.start_price,
            'end_price': self.end_price,
            'mid_price': (self.start_price + self.end_price) / 2,
            'timestamp': self.timestamp.isoformat(),
            'volume_ratio': round(self.volume_ratio, 2),
            'price_move_pct': round(self.price_move_pct, 2),
            'strength': self.strength,
            'tests': self.tests,
            'broken': self.broken
        }
    
    def __repr__(self) -> str:
        return (f"OrderBlock({self.type}, ${self.start_price:.2f}-${self.end_price:.2f}, "
                f"strength={self.strength}/10)")


class OrderBlockDetector:
    """Main detector class for identifying order blocks"""
    
    def __init__(self, min_volume_ratio: float = 1.5, min_price_move: float = 2.0,
                 lookback_candles: int = 5):
        """
        Args:
            min_volume_ratio: Minimum volume vs average to consider (default 1.5x)
            min_price_move: Minimum price move percentage to consider (default 2%)
            lookback_candles: Candles to look ahead for confirmation (default 5)
        """
        self.min_volume_ratio = min_volume_ratio
        self.min_price_move = min_price_move
        self.lookback_candles = lookback_candles
    
    def detect_order_blocks(self, df: pd.DataFrame) -> List[OrderBlock]:
        """
        Detect order blocks from OHLCV dataframe
        
        Args:
            df: DataFrame with columns: timestamp, open, high, low, close, volume
        
        Returns:
            List of OrderBlock objects
        """
        if len(df) < 20:
            print("WARNING: Not enough data for reliable detection (need 20+ candles)")
            return []
        
        # Calculate volume moving average
        df['volume_ma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_ma']
        
        # Identify candle direction
        df['is_bullish'] = df['close'] > df['open']
        df['is_bearish'] = df['close'] < df['open']
        df['body_size'] = abs(df['close'] - df['open'])
        
        order_blocks = []
        
        # Scan for bullish order blocks
        for i in range(len(df) - self.lookback_candles):
            # Check if current candle is bearish
            if not df.iloc[i]['is_bearish']:
                continue
            
            # Check if next candle is strongly bullish
            next_candle = df.iloc[i + 1]
            if not next_candle['is_bullish']:
                continue
            
            # CRITICAL FIX #1: Check for engulfment (ICT theory requirement)
            # Next candle must engulf current candle (body-to-body + wicks)
            current_candle = df.iloc[i]
            engulfment = (next_candle['low'] < current_candle['low'] and 
                         next_candle['close'] > current_candle['high'])
            if not engulfment:
                continue
            
            # Calculate price move over next N candles
            current_close = df.iloc[i + 1]['close']
            future_high = df.iloc[i + 1:i + 1 + self.lookback_candles]['high'].max()
            price_move_pct = ((future_high - current_close) / current_close) * 100
            
            # Check if move is significant
            if price_move_pct < self.min_price_move:
                continue
            
            # CRITICAL FIX #2: Validate clean follow-through (no off-by-one error)
            if not self._check_bullish_followthrough(df, i + 1, self.lookback_candles):
                continue
            
            # CRITICAL FIX #3: Check for pullbacks using wicks, not just closes
            end_idx = min(i + 1 + self.lookback_candles, len(df) - 1)
            if self._check_pullback_bullish(df, i + 1, end_idx):
                continue  # Reject if significant pullback detected
            
            # Check volume confirmation
            volume_ratio = next_candle['volume_ratio']
            if volume_ratio < self.min_volume_ratio:
                continue
            
            # Create bullish order block (using the bearish candle's range)
            bearish_candle = df.iloc[i]
            ob = OrderBlock(
                block_type='bullish',
                start_price=min(bearish_candle['open'], bearish_candle['close']),
                end_price=max(bearish_candle['open'], bearish_candle['close']),
                timestamp=pd.to_datetime(bearish_candle['timestamp']),
                volume_ratio=volume_ratio,
                price_move_pct=price_move_pct,
                candle_index=i
            )
            
            # Check for tests and breaks
            self._check_zone_interactions(ob, df, i)
            order_blocks.append(ob)
        
        # Scan for bearish order blocks
        for i in range(len(df) - self.lookback_candles):
            # Check if current candle is bullish
            if not df.iloc[i]['is_bullish']:
                continue
            
            # Check if next candle is strongly bearish
            next_candle = df.iloc[i + 1]
            if not next_candle['is_bearish']:
                continue
            
            # CRITICAL FIX #1: Check for engulfment (ICT theory requirement)
            # Next candle must engulf current candle (body-to-body + wicks)
            current_candle = df.iloc[i]
            engulfment = (next_candle['high'] > current_candle['high'] and 
                         next_candle['close'] < current_candle['low'])
            if not engulfment:
                continue
            
            # Calculate price move over next N candles
            current_close = df.iloc[i + 1]['close']
            future_low = df.iloc[i + 1:i + 1 + self.lookback_candles]['low'].min()
            price_move_pct = ((current_close - future_low) / current_close) * 100
            
            # Check if move is significant
            if price_move_pct < self.min_price_move:
                continue
            
            # CRITICAL FIX #2: Validate clean follow-through (no off-by-one error)
            if not self._check_bearish_followthrough(df, i + 1, self.lookback_candles):
                continue
            
            # CRITICAL FIX #3: Check for pullbacks using wicks, not just closes
            end_idx = min(i + 1 + self.lookback_candles, len(df) - 1)
            if self._check_pullback_bearish(df, i + 1, end_idx):
                continue  # Reject if significant pullback detected
            
            # Check volume confirmation
            volume_ratio = next_candle['volume_ratio']
            if volume_ratio < self.min_volume_ratio:
                continue
            
            # Create bearish order block (using the bullish candle's range)
            bullish_candle = df.iloc[i]
            ob = OrderBlock(
                block_type='bearish',
                start_price=min(bullish_candle['open'], bullish_candle['close']),
                end_price=max(bullish_candle['open'], bullish_candle['close']),
                timestamp=pd.to_datetime(bullish_candle['timestamp']),
                volume_ratio=volume_ratio,
                price_move_pct=price_move_pct,
                candle_index=i
            )
            
            # Check for tests and breaks
            self._check_zone_interactions(ob, df, i)
            order_blocks.append(ob)
        
        # Sort by strength (strongest first)
        order_blocks.sort(key=lambda x: x.strength, reverse=True)
        
        return order_blocks
    
    def _check_bullish_followthrough(self, df: pd.DataFrame, start_i: int, 
                                      lookback: int = 3) -> bool:
        """
        CRITICAL FIX #2: Check for clean bullish follow-through after order block
        Fixed off-by-one error: starts loop from start_i+1, not start_i
        """
        if start_i + lookback >= len(df):
            return False
        
        continuation_count = 0
        # CRITICAL: Start from start_i+1, not start_i (fix off-by-one error)
        for j in range(start_i + 1, min(start_i + lookback + 1, len(df))):
            if df.iloc[j]['close'] > df.iloc[j-1]['close']:
                continuation_count += 1
        
        # Require at least 2 out of 3 candles to continue upward
        return continuation_count >= 2
    
    def _check_bearish_followthrough(self, df: pd.DataFrame, start_i: int, 
                                      lookback: int = 3) -> bool:
        """
        CRITICAL FIX #2: Check for clean bearish follow-through after order block
        Fixed off-by-one error: starts loop from start_i+1, not start_i
        """
        if start_i + lookback >= len(df):
            return False
        
        continuation_count = 0
        # CRITICAL: Start from start_i+1, not start_i (fix off-by-one error)
        for j in range(start_i + 1, min(start_i + lookback + 1, len(df))):
            if df.iloc[j]['close'] < df.iloc[j-1]['close']:
                continuation_count += 1
        
        # Require at least 2 out of 3 candles to continue downward
        return continuation_count >= 2
    
    def _check_pullback_bullish(self, df: pd.DataFrame, start: int, end: int) -> bool:
        """
        CRITICAL FIX #3: Check for significant pullback during bullish move
        Fixed to use WICKS (low), not just closing prices
        """
        if start >= end or end >= len(df):
            return False
        
        move_size = df.iloc[end]['close'] - df.iloc[start]['close']
        if move_size <= 0:
            return False
        
        start_price = df.iloc[start]['close']
        
        for k in range(start + 1, end):
            # CRITICAL FIX: Check both close AND low (worst case)
            drop_close = start_price - df.iloc[k]['close']
            drop_low = start_price - df.iloc[k]['low']
            max_drop = max(drop_close, drop_low)
            
            # If pullback exceeds 50% of total move, it's not a clean impulse
            if max_drop > (move_size * 0.5):
                return True
        
        return False
    
    def _check_pullback_bearish(self, df: pd.DataFrame, start: int, end: int) -> bool:
        """
        CRITICAL FIX #3: Check for significant pullback during bearish move
        Fixed to use WICKS (high), not just closing prices
        """
        if start >= end or end >= len(df):
            return False
        
        move_size = df.iloc[start]['close'] - df.iloc[end]['close']
        if move_size <= 0:
            return False
        
        start_price = df.iloc[start]['close']
        
        for k in range(start + 1, end):
            # CRITICAL FIX: Check both close AND high (worst case)
            rise_close = df.iloc[k]['close'] - start_price
            rise_high = df.iloc[k]['high'] - start_price
            max_rise = max(rise_close, rise_high)
            
            # If pullback exceeds 50% of total move, it's not a clean impulse
            if max_rise > (move_size * 0.5):
                return True
        
        return False
    
    def _check_zone_interactions(self, ob: OrderBlock, df: pd.DataFrame, 
                                  start_index: int) -> None:
        """Check how many times price has tested or broken the zone"""
        future_candles = df.iloc[start_index + 1:]
        
        for idx, candle in future_candles.iterrows():
            # Check if price touched the zone
            if candle['low'] <= ob.end_price and candle['high'] >= ob.start_price:
                ob.tests += 1
            
            # Check if zone was broken
            if ob.type == 'bullish' and candle['close'] < ob.start_price:
                ob.broken = True
            elif ob.type == 'bearish' and candle['close'] > ob.end_price:
                ob.broken = True
        
        # Recalculate strength after updating tests
        ob.strength = ob._calculate_strength()
    
    def filter_relevant_blocks(self, order_blocks: List[OrderBlock], 
                               current_price: float, max_distance_pct: float = 10.0) -> List[OrderBlock]:
        """
        Filter order blocks to only include those near current price
        
        Args:
            order_blocks: List of all detected order blocks
            current_price: Current market price
            max_distance_pct: Maximum distance from current price (default 10%)
        
        Returns:
            Filtered list of nearby order blocks
        """
        relevant = []
        for ob in order_blocks:
            mid_price = (ob.start_price + ob.end_price) / 2
            distance_pct = abs((mid_price - current_price) / current_price) * 100
            
            if distance_pct <= max_distance_pct and not ob.broken:
                relevant.append(ob)
        
        return relevant


def format_output(bullish_blocks: List[OrderBlock], bearish_blocks: List[OrderBlock],
                  current_price: Optional[float] = None) -> str:
    """Format detection results for display"""
    output = []
    output.append("=" * 80)
    output.append("ORDER BLOCK DETECTION RESULTS")
    output.append("=" * 80)
    
    if current_price:
        output.append(f"\nCurrent Price: ${current_price:.2f}\n")
    
    # Bullish blocks
    output.append(f"\n🟢 BULLISH ORDER BLOCKS (Demand Zones - Support)")
    output.append("-" * 80)
    if bullish_blocks:
        for i, ob in enumerate(bullish_blocks[:5], 1):  # Top 5
            output.append(f"{i}. ${ob.start_price:.2f} - ${ob.end_price:.2f}")
            output.append(f"   Strength: {ob.strength}/10 | Volume: {ob.volume_ratio:.1f}x | "
                         f"Move: {ob.price_move_pct:.1f}% | Tests: {ob.tests} | "
                         f"Broken: {'Yes' if ob.broken else 'No'}")
            output.append(f"   Formed: {ob.timestamp.strftime('%Y-%m-%d %H:%M')}")
            output.append("")
    else:
        output.append("   No bullish order blocks detected")
    
    # Bearish blocks
    output.append(f"\n🔴 BEARISH ORDER BLOCKS (Supply Zones - Resistance)")
    output.append("-" * 80)
    if bearish_blocks:
        for i, ob in enumerate(bearish_blocks[:5], 1):  # Top 5
            output.append(f"{i}. ${ob.start_price:.2f} - ${ob.end_price:.2f}")
            output.append(f"   Strength: {ob.strength}/10 | Volume: {ob.volume_ratio:.1f}x | "
                         f"Move: {ob.price_move_pct:.1f}% | Tests: {ob.tests} | "
                         f"Broken: {'Yes' if ob.broken else 'No'}")
            output.append(f"   Formed: {ob.timestamp.strftime('%Y-%m-%d %H:%M')}")
            output.append("")
    else:
        output.append("   No bearish order blocks detected")
    
    output.append("=" * 80)
    output.append("\n⚠️  TRADING RULES:")
    output.append("  1. DO NOT enter against an unbroken order block")
    output.append("  2. Wait for price to BREAK and CLOSE beyond the zone")
    output.append("  3. Use blocks as support/resistance for entries WITH the zone")
    output.append("  4. Higher strength = more reliable zone")
    output.append("=" * 80)
    
    return "\n".join(output)


def main():
    """Main entry point for standalone usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Detect order blocks from price data')
    parser.add_argument('--symbol', type=str, required=True, help='Trading symbol (e.g., AAPL)')
    parser.add_argument('--timeframe', type=str, default='1Hour', 
                       help='Timeframe (e.g., 1Min, 5Min, 15Min, 1Hour, 1Day)')
    parser.add_argument('--days', type=int, default=30, help='Days of historical data')
    parser.add_argument('--output', type=str, help='Output file (JSON)')
    parser.add_argument('--alpaca-key', type=str, help='Alpaca API key (or set ALPACA_API_KEY env)')
    parser.add_argument('--alpaca-secret', type=str, help='Alpaca API secret (or set ALPACA_API_SECRET env)')
    
    args = parser.parse_args()
    
    # Get API credentials
    api_key = args.alpaca_key or os.environ.get('ALPACA_API_KEY')
    api_secret = args.alpaca_secret or os.environ.get('ALPACA_API_SECRET')
    
    if not api_key or not api_secret:
        print("ERROR: Alpaca API credentials required")
        print("Set --alpaca-key and --alpaca-secret OR environment variables:")
        print("  export ALPACA_API_KEY='your_key'")
        print("  export ALPACA_API_SECRET='your_secret'")
        sys.exit(1)
    
    # Fetch data (placeholder - actual implementation below)
    print(f"Fetching {args.days} days of {args.timeframe} data for {args.symbol}...")
    
    try:
        from alpaca_trade_api import REST
        alpaca = REST(api_key, api_secret, base_url='https://paper-api.alpaca.markets')
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=args.days)
        
        # Fetch bars
        bars = alpaca.get_bars(
            args.symbol,
            args.timeframe,
            start=start_date.isoformat(),
            end=end_date.isoformat()
        ).df
        
        # Prepare dataframe
        df = pd.DataFrame({
            'timestamp': bars.index,
            'open': bars['open'],
            'high': bars['high'],
            'low': bars['low'],
            'close': bars['close'],
            'volume': bars['volume']
        })
        
        current_price = df.iloc[-1]['close']
        
    except ImportError:
        print("ERROR: alpaca-trade-api not installed")
        print("Run: pip install alpaca-trade-api")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR fetching data: {e}")
        sys.exit(1)
    
    # Detect order blocks
    print("Detecting order blocks...")
    detector = OrderBlockDetector()
    all_blocks = detector.detect_order_blocks(df)
    
    # Separate by type
    bullish_blocks = [ob for ob in all_blocks if ob.type == 'bullish']
    bearish_blocks = [ob for ob in all_blocks if ob.type == 'bearish']
    
    # Filter to relevant (near current price)
    bullish_blocks = detector.filter_relevant_blocks(bullish_blocks, current_price)
    bearish_blocks = detector.filter_relevant_blocks(bearish_blocks, current_price)
    
    # Display results
    print(format_output(bullish_blocks, bearish_blocks, current_price))
    
    # Save to file if requested
    if args.output:
        results = {
            'symbol': args.symbol,
            'timeframe': args.timeframe,
            'current_price': current_price,
            'timestamp': datetime.now().isoformat(),
            'bullish_blocks': [ob.to_dict() for ob in bullish_blocks],
            'bearish_blocks': [ob.to_dict() for ob in bearish_blocks]
        }
        
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✓ Results saved to {args.output}")


if __name__ == '__main__':
    main()
