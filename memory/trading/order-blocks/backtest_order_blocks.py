#!/usr/bin/env python3
"""
Order Block Backtest Script
Tests order block strategy across multiple symbols and timeframes
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import time

try:
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest
    from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
    import pandas as pd
    import numpy as np
except ImportError:
    print("ERROR: Required packages not installed.")
    print("Install with: pip install alpaca-py pandas numpy")
    sys.exit(1)

# Import the detector (adjusted parameters will be set in config)
try:
    from order_block_detector import OrderBlockDetector, OrderBlock
except ImportError:
    print("ERROR: order_block_detector.py not found in current directory")
    sys.exit(1)


class BacktestConfig:
    """Configuration for backtest parameters"""
    
    # Test universe
    SYMBOLS = ['SPY', 'QQQ', 'AAPL', 'TSLA', 'NVDA']
    TIMEFRAMES = ['5m', '15m', '1h']
    
    # Date range (6 months: Jul 2024 - Jan 2025)
    START_DATE = datetime(2024, 7, 1)
    END_DATE = datetime(2025, 1, 31)
    
    # Adjusted detection parameters (from verification)
    MIN_PRICE_MOVE = 1.2  # Down from 2.0
    MIN_VOLUME_RATIO = 1.3  # Down from 1.5
    
    # Backtest parameters
    ZONE_TOLERANCE = 0.02  # ±2% tolerance for zone respect
    RISK_REWARD_RATIO = 2.0  # 2:1 target
    STOP_LOSS_BUFFER = 0.005  # 0.5% beyond zone for stop
    
    # Progress settings
    SAVE_INTERVAL = 5  # Save progress every N tests


class Trade:
    """Represents a simulated trade"""
    
    def __init__(self, symbol: str, timeframe: str, order_block: Dict,
                 entry_price: float, entry_time: datetime):
        self.symbol = symbol
        self.timeframe = timeframe
        self.ob_type = order_block['type']
        self.ob_strength = order_block['adjusted_strength']
        self.ob_zone_high = order_block['zone_high']
        self.ob_zone_low = order_block['zone_low']
        self.entry_price = entry_price
        self.entry_time = entry_time
        
        # Calculate stop and target
        zone_range = self.ob_zone_high - self.ob_zone_low
        buffer = zone_range * BacktestConfig.STOP_LOSS_BUFFER
        
        if self.ob_type == 'bullish':
            self.stop_loss = self.ob_zone_low - buffer
            risk = entry_price - self.stop_loss
            self.target = entry_price + (risk * BacktestConfig.RISK_REWARD_RATIO)
        else:  # bearish
            self.stop_loss = self.ob_zone_high + buffer
            risk = self.stop_loss - entry_price
            self.target = entry_price - (risk * BacktestConfig.RISK_REWARD_RATIO)
        
        # Trade outcome
        self.exit_price = None
        self.exit_time = None
        self.outcome = None  # 'win', 'loss', or 'timeout'
        self.r_multiple = 0.0
        self.duration_bars = 0
    
    def to_dict(self) -> Dict:
        return {
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'ob_type': self.ob_type,
            'ob_strength': round(self.ob_strength, 2),
            'ob_zone': [self.ob_zone_low, self.ob_zone_high],
            'entry_price': round(self.entry_price, 2),
            'entry_time': self.entry_time.isoformat(),
            'stop_loss': round(self.stop_loss, 2),
            'target': round(self.target, 2),
            'exit_price': round(self.exit_price, 2) if self.exit_price else None,
            'exit_time': self.exit_time.isoformat() if self.exit_time else None,
            'outcome': self.outcome,
            'r_multiple': round(self.r_multiple, 2),
            'duration_bars': self.duration_bars
        }


class OrderBlockBacktest:
    """Main backtest engine"""
    
    def __init__(self):
        # Initialize Alpaca client
        api_key = os.getenv('ALPACA_API_KEY')
        api_secret = os.getenv('ALPACA_API_SECRET')
        
        if not api_key or not api_secret:
            raise ValueError("Alpaca API credentials required")
        
        self.client = StockHistoricalDataClient(api_key, api_secret)
        
        # Initialize detector with adjusted parameters
        self.detector = OrderBlockDetector(api_key, api_secret)
        self.detector.params['impulse_threshold_pct'] = BacktestConfig.MIN_PRICE_MOVE
        self.detector.params['volume_spike_min'] = BacktestConfig.MIN_VOLUME_RATIO
        
        # Results storage
        self.all_trades: List[Trade] = []
        self.detection_stats = defaultdict(lambda: {'detected': 0, 'tested': 0})
        self.errors = []
        
        # Progress tracking
        self.total_tests = len(BacktestConfig.SYMBOLS) * len(BacktestConfig.TIMEFRAMES)
        self.completed_tests = 0
        self.start_time = None
    
    def run(self):
        """Execute the full backtest"""
        print("\n" + "="*80)
        print("ORDER BLOCK BACKTEST")
        print("="*80)
        print(f"Period: {BacktestConfig.START_DATE.date()} to {BacktestConfig.END_DATE.date()}")
        print(f"Symbols: {', '.join(BacktestConfig.SYMBOLS)}")
        print(f"Timeframes: {', '.join(BacktestConfig.TIMEFRAMES)}")
        print(f"Total tests: {self.total_tests}")
        print(f"\nAdjusted Parameters:")
        print(f"  - Min Price Move: {BacktestConfig.MIN_PRICE_MOVE}%")
        print(f"  - Min Volume Ratio: {BacktestConfig.MIN_VOLUME_RATIO}x")
        print(f"  - Zone Tolerance: ±{BacktestConfig.ZONE_TOLERANCE*100}%")
        print(f"  - Risk:Reward: 1:{BacktestConfig.RISK_REWARD_RATIO}")
        print("="*80 + "\n")
        
        self.start_time = time.time()
        
        # Test each symbol/timeframe combination
        for symbol in BacktestConfig.SYMBOLS:
            for timeframe in BacktestConfig.TIMEFRAMES:
                self._test_combination(symbol, timeframe)
                self.completed_tests += 1
                self._print_progress()
                
                # Save progress periodically
                if self.completed_tests % BacktestConfig.SAVE_INTERVAL == 0:
                    self._save_progress()
        
        # Generate final results
        self._generate_results()
        
        print("\n✅ Backtest complete!")
        print(f"Total runtime: {self._format_duration(time.time() - self.start_time)}")
    
    def _test_combination(self, symbol: str, timeframe: str):
        """Test a single symbol/timeframe combination"""
        try:
            print(f"\n📊 Testing {symbol} on {timeframe}...")
            
            # Step 1: Fetch full historical data for the period
            df = self._fetch_historical_data(symbol, timeframe)
            if df is None or len(df) < 100:
                print(f"  ⚠️  Insufficient data for {symbol} {timeframe}")
                self.errors.append(f"{symbol} {timeframe}: Insufficient data")
                return
            
            print(f"  ✓ Loaded {len(df)} bars")
            
            # Step 2: Walk through history, detecting order blocks as we go
            # Use a rolling window approach to simulate real-time detection
            lookback_bars = 150  # Enough for detection
            scan_start = lookback_bars
            scan_end = len(df)
            
            detected_count = 0
            tested_count = 0
            
            # Scan through history
            for i in range(scan_start, scan_end, 10):  # Step by 10 bars for efficiency
                # Get historical window up to this point
                window_df = df.iloc[:i].copy()
                
                # Detect order blocks on this window
                order_blocks = self._detect_order_blocks_from_df(
                    window_df, symbol, timeframe
                )
                
                if not order_blocks:
                    continue
                
                detected_count += len(order_blocks)
                
                # For each order block, test it forward
                for ob in order_blocks:
                    # Get the candle index where OB was formed
                    ob_time = datetime.fromisoformat(ob['timestamp'])
                    ob_index = window_df.index.get_indexer([ob_time], method='nearest')[0]
                    
                    # Forward test window (next 50 bars after detection)
                    forward_end = min(ob_index + 50, len(df))
                    if forward_end <= ob_index + 5:
                        continue
                    
                    forward_df = df.iloc[ob_index:forward_end].copy()
                    
                    # Simulate trade if zone is tested
                    trade = self._simulate_trade(symbol, timeframe, ob, forward_df)
                    if trade:
                        self.all_trades.append(trade)
                        tested_count += 1
            
            # Update stats
            self.detection_stats[f"{symbol}_{timeframe}"] = {
                'detected': detected_count,
                'tested': tested_count
            }
            
            print(f"  ✓ Detected {detected_count} order blocks, {tested_count} tested")
            
        except Exception as e:
            print(f"  ❌ Error testing {symbol} {timeframe}: {e}")
            self.errors.append(f"{symbol} {timeframe}: {str(e)}")
    
    def _fetch_historical_data(self, symbol: str, timeframe: str) -> Optional[pd.DataFrame]:
        """Fetch historical data from Alpaca"""
        try:
            # Parse timeframe
            tf_map = {
                '5m': TimeFrame(5, TimeFrameUnit.Minute),
                '15m': TimeFrame(15, TimeFrameUnit.Minute),
                '1h': TimeFrame(1, TimeFrameUnit.Hour),
            }
            
            tf = tf_map.get(timeframe)
            if not tf:
                return None
            
            # Fetch data
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=tf,
                start=BacktestConfig.START_DATE,
                end=BacktestConfig.END_DATE
            )
            
            bars = self.client.get_stock_bars(request)
            df = bars.df
            
            # Reset multi-index if present
            if isinstance(df.index, pd.MultiIndex):
                df = df.reset_index(level=0, drop=True)
            
            return df
            
        except Exception as e:
            print(f"    Error fetching data: {e}")
            return None
    
    def _detect_order_blocks_from_df(self, df: pd.DataFrame, 
                                     symbol: str, timeframe: str) -> List[Dict]:
        """Detect order blocks from a DataFrame"""
        try:
            # Calculate indicators (same as detector)
            df = self._calculate_indicators(df)
            
            # Scan for order blocks (simplified version)
            order_blocks = []
            
            for i in range(20, len(df) - 10):
                # Check bullish
                ob = self._check_bullish_ob(df, i)
                if ob:
                    order_blocks.append(ob)
                
                # Check bearish
                ob = self._check_bearish_ob(df, i)
                if ob:
                    order_blocks.append(ob)
            
            return order_blocks
            
        except Exception as e:
            return []
    
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        df = df.copy()
        df['volume_ma'] = df['volume'].rolling(window=20).mean()
        df['tr'] = np.maximum(
            df['high'] - df['low'],
            np.maximum(
                abs(df['high'] - df['close'].shift(1)),
                abs(df['low'] - df['close'].shift(1))
            )
        )
        df['atr'] = df['tr'].rolling(window=14).mean()
        df['pct_change'] = df['close'].pct_change() * 100
        df['volume_ratio'] = df['volume'] / df['volume_ma']
        return df
    
    def _check_bullish_ob(self, df: pd.DataFrame, i: int) -> Optional[Dict]:
        """Check for bullish order block (simplified)"""
        # Bearish candle
        if df['close'].iloc[i] >= df['open'].iloc[i]:
            return None
        
        # Check for bullish impulse after
        if i + 4 >= len(df):
            return None
        
        start_price = df['close'].iloc[i]
        max_vol_ratio = 0
        
        for j in range(i+1, min(i+5, len(df))):
            end_price = df['close'].iloc[j]
            pct_change = ((end_price - start_price) / start_price) * 100
            
            if not pd.isna(df['volume_ratio'].iloc[j]):
                max_vol_ratio = max(max_vol_ratio, df['volume_ratio'].iloc[j])
            
            if pct_change >= BacktestConfig.MIN_PRICE_MOVE and \
               max_vol_ratio >= BacktestConfig.MIN_VOLUME_RATIO:
                return {
                    'type': 'bullish',
                    'timestamp': df.index[i].isoformat(),
                    'zone_low': float(df['low'].iloc[i]),
                    'zone_high': float(df['high'].iloc[i]),
                    'adjusted_strength': 7.0,  # Simplified
                    'volume_ratio': float(max_vol_ratio),
                    'impulse_pct': float(pct_change)
                }
        
        return None
    
    def _check_bearish_ob(self, df: pd.DataFrame, i: int) -> Optional[Dict]:
        """Check for bearish order block (simplified)"""
        # Bullish candle
        if df['close'].iloc[i] <= df['open'].iloc[i]:
            return None
        
        if i + 4 >= len(df):
            return None
        
        start_price = df['close'].iloc[i]
        max_vol_ratio = 0
        
        for j in range(i+1, min(i+5, len(df))):
            end_price = df['close'].iloc[j]
            pct_change = ((end_price - start_price) / start_price) * 100
            
            if not pd.isna(df['volume_ratio'].iloc[j]):
                max_vol_ratio = max(max_vol_ratio, df['volume_ratio'].iloc[j])
            
            if pct_change <= -BacktestConfig.MIN_PRICE_MOVE and \
               max_vol_ratio >= BacktestConfig.MIN_VOLUME_RATIO:
                return {
                    'type': 'bearish',
                    'timestamp': df.index[i].isoformat(),
                    'zone_low': float(df['low'].iloc[i]),
                    'zone_high': float(df['high'].iloc[i]),
                    'adjusted_strength': 7.0,
                    'volume_ratio': float(max_vol_ratio),
                    'impulse_pct': float(pct_change)
                }
        
        return None
    
    def _simulate_trade(self, symbol: str, timeframe: str, 
                       order_block: Dict, forward_df: pd.DataFrame) -> Optional[Trade]:
        """Simulate a trade when zone is tested"""
        ob_type = order_block['type']
        zone_low = order_block['zone_low']
        zone_high = order_block['zone_high']
        zone_mid = (zone_high + zone_low) / 2
        tolerance = zone_mid * BacktestConfig.ZONE_TOLERANCE
        
        # Look for zone test in forward data
        for i in range(1, len(forward_df)):
            bar_low = forward_df['low'].iloc[i]
            bar_high = forward_df['high'].iloc[i]
            bar_close = forward_df['close'].iloc[i]
            bar_time = forward_df.index[i]
            
            # Check if zone was tested
            zone_tested = False
            entry_price = None
            
            if ob_type == 'bullish':
                # Price dips into or near zone
                if bar_low <= zone_high + tolerance and bar_low >= zone_low - tolerance:
                    zone_tested = True
                    # Entry at zone mid or close if bar closed in zone
                    if bar_close >= zone_low and bar_close <= zone_high:
                        entry_price = bar_close
                    else:
                        entry_price = zone_mid
            else:  # bearish
                # Price rises into or near zone
                if bar_high >= zone_low - tolerance and bar_high <= zone_high + tolerance:
                    zone_tested = True
                    if bar_close >= zone_low and bar_close <= zone_high:
                        entry_price = bar_close
                    else:
                        entry_price = zone_mid
            
            if not zone_tested:
                continue
            
            # Zone was tested, create trade
            trade = Trade(symbol, timeframe, order_block, entry_price, bar_time)
            
            # Simulate trade outcome over remaining bars
            for j in range(i+1, len(forward_df)):
                bar_low_fwd = forward_df['low'].iloc[j]
                bar_high_fwd = forward_df['high'].iloc[j]
                bar_close_fwd = forward_df['close'].iloc[j]
                bar_time_fwd = forward_df.index[j]
                trade.duration_bars = j - i
                
                # Check for target hit
                if ob_type == 'bullish' and bar_high_fwd >= trade.target:
                    trade.exit_price = trade.target
                    trade.exit_time = bar_time_fwd
                    trade.outcome = 'win'
                    trade.r_multiple = BacktestConfig.RISK_REWARD_RATIO
                    return trade
                elif ob_type == 'bearish' and bar_low_fwd <= trade.target:
                    trade.exit_price = trade.target
                    trade.exit_time = bar_time_fwd
                    trade.outcome = 'win'
                    trade.r_multiple = BacktestConfig.RISK_REWARD_RATIO
                    return trade
                
                # Check for stop hit
                if ob_type == 'bullish' and bar_low_fwd <= trade.stop_loss:
                    trade.exit_price = trade.stop_loss
                    trade.exit_time = bar_time_fwd
                    trade.outcome = 'loss'
                    trade.r_multiple = -1.0
                    return trade
                elif ob_type == 'bearish' and bar_high_fwd >= trade.stop_loss:
                    trade.exit_price = trade.stop_loss
                    trade.exit_time = bar_time_fwd
                    trade.outcome = 'loss'
                    trade.r_multiple = -1.0
                    return trade
            
            # Trade timed out (no clear outcome)
            trade.exit_price = forward_df['close'].iloc[-1]
            trade.exit_time = forward_df.index[-1]
            trade.outcome = 'timeout'
            
            # Calculate realized R based on exit
            if ob_type == 'bullish':
                pnl = trade.exit_price - entry_price
                risk = entry_price - trade.stop_loss
            else:
                pnl = entry_price - trade.exit_price
                risk = trade.stop_loss - entry_price
            
            trade.r_multiple = pnl / risk if risk > 0 else 0
            
            return trade
        
        return None
    
    def _print_progress(self):
        """Print progress update"""
        pct = (self.completed_tests / self.total_tests) * 100
        elapsed = time.time() - self.start_time
        
        if self.completed_tests > 0:
            avg_time = elapsed / self.completed_tests
            remaining = avg_time * (self.total_tests - self.completed_tests)
            eta = self._format_duration(remaining)
        else:
            eta = "calculating..."
        
        print(f"\n⏳ Progress: {self.completed_tests}/{self.total_tests} ({pct:.1f}%) | ETA: {eta}")
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable form"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds/60)}m {int(seconds%60)}s"
        else:
            return f"{int(seconds/3600)}h {int((seconds%3600)/60)}m"
    
    def _save_progress(self):
        """Save intermediate results"""
        try:
            progress_data = {
                'completed_tests': self.completed_tests,
                'total_tests': self.total_tests,
                'trades_count': len(self.all_trades),
                'timestamp': datetime.now().isoformat()
            }
            
            with open('backtest-progress.json', 'w') as f:
                json.dump(progress_data, f, indent=2)
            
            print(f"  💾 Progress saved ({len(self.all_trades)} trades so far)")
        except Exception as e:
            print(f"  ⚠️  Could not save progress: {e}")
    
    def _generate_results(self):
        """Generate comprehensive results"""
        print("\n" + "="*80)
        print("GENERATING RESULTS...")
        print("="*80 + "\n")
        
        # Calculate overall statistics
        total_trades = len(self.all_trades)
        
        if total_trades == 0:
            print("⚠️  No trades were generated. Check data availability and parameters.")
            return
        
        wins = [t for t in self.all_trades if t.outcome == 'win']
        losses = [t for t in self.all_trades if t.outcome == 'loss']
        timeouts = [t for t in self.all_trades if t.outcome == 'timeout']
        
        win_rate = (len(wins) / total_trades) * 100 if total_trades > 0 else 0
        avg_r = np.mean([t.r_multiple for t in self.all_trades])
        
        # Expected value per trade
        ev_per_trade = avg_r
        
        # Breakdown by symbol
        symbol_stats = self._calculate_breakdown('symbol')
        
        # Breakdown by timeframe
        timeframe_stats = self._calculate_breakdown('timeframe')
        
        # Breakdown by OB type
        type_stats = self._calculate_breakdown('ob_type')
        
        # Generate markdown report
        self._write_markdown_report(
            total_trades, wins, losses, timeouts, win_rate, avg_r, ev_per_trade,
            symbol_stats, timeframe_stats, type_stats
        )
        
        # Generate JSON data
        self._write_json_data()
        
        print("✓ Results generated:")
        print("  - backtest-results.md (human-readable report)")
        print("  - backtest-data.json (raw data)")
    
    def _calculate_breakdown(self, field: str) -> Dict:
        """Calculate statistics breakdown by field"""
        breakdown = defaultdict(lambda: {
            'trades': 0, 'wins': 0, 'losses': 0, 'timeouts': 0,
            'r_multiples': []
        })
        
        for trade in self.all_trades:
            key = getattr(trade, field)
            breakdown[key]['trades'] += 1
            
            if trade.outcome == 'win':
                breakdown[key]['wins'] += 1
            elif trade.outcome == 'loss':
                breakdown[key]['losses'] += 1
            else:
                breakdown[key]['timeouts'] += 1
            
            breakdown[key]['r_multiples'].append(trade.r_multiple)
        
        # Calculate derived stats
        for key in breakdown:
            stats = breakdown[key]
            stats['win_rate'] = (stats['wins'] / stats['trades'] * 100) if stats['trades'] > 0 else 0
            stats['avg_r'] = np.mean(stats['r_multiples']) if stats['r_multiples'] else 0
            stats['ev_per_trade'] = stats['avg_r']
        
        return dict(breakdown)
    
    def _write_markdown_report(self, total_trades, wins, losses, timeouts,
                               win_rate, avg_r, ev_per_trade,
                               symbol_stats, timeframe_stats, type_stats):
        """Write human-readable markdown report"""
        
        with open('backtest-results.md', 'w') as f:
            f.write("# Order Block Backtest Results\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Period:** {BacktestConfig.START_DATE.date()} to {BacktestConfig.END_DATE.date()}\n\n")
            f.write("---\n\n")
            
            # Overall Summary
            f.write("## 📊 Overall Performance\n\n")
            f.write(f"- **Total Trades:** {total_trades}\n")
            f.write(f"- **Wins:** {len(wins)} ({len(wins)/total_trades*100:.1f}%)\n")
            f.write(f"- **Losses:** {len(losses)} ({len(losses)/total_trades*100:.1f}%)\n")
            f.write(f"- **Timeouts:** {len(timeouts)} ({len(timeouts)/total_trades*100:.1f}%)\n")
            f.write(f"- **Win Rate:** {win_rate:.2f}%\n")
            f.write(f"- **Average R-Multiple:** {avg_r:.2f}R\n")
            f.write(f"- **Expected Value per Trade:** {ev_per_trade:.2f}R\n\n")
            
            # By Symbol
            f.write("## 📈 Performance by Symbol\n\n")
            f.write("| Symbol | Trades | Win Rate | Avg R | EV/Trade |\n")
            f.write("|--------|--------|----------|-------|----------|\n")
            for symbol in BacktestConfig.SYMBOLS:
                if symbol in symbol_stats:
                    stats = symbol_stats[symbol]
                    f.write(f"| {symbol} | {stats['trades']} | "
                           f"{stats['win_rate']:.1f}% | {stats['avg_r']:.2f}R | "
                           f"{stats['ev_per_trade']:.2f}R |\n")
            f.write("\n")
            
            # By Timeframe
            f.write("## ⏱️ Performance by Timeframe\n\n")
            f.write("| Timeframe | Trades | Win Rate | Avg R | EV/Trade |\n")
            f.write("|-----------|--------|----------|-------|----------|\n")
            for tf in BacktestConfig.TIMEFRAMES:
                if tf in timeframe_stats:
                    stats = timeframe_stats[tf]
                    f.write(f"| {tf} | {stats['trades']} | "
                           f"{stats['win_rate']:.1f}% | {stats['avg_r']:.2f}R | "
                           f"{stats['ev_per_trade']:.2f}R |\n")
            f.write("\n")
            
            # By Order Block Type
            f.write("## 🎯 Performance by Order Block Type\n\n")
            f.write("| Type | Trades | Win Rate | Avg R | EV/Trade |\n")
            f.write("|------|--------|----------|-------|----------|\n")
            for ob_type in ['bullish', 'bearish']:
                if ob_type in type_stats:
                    stats = type_stats[ob_type]
                    f.write(f"| {ob_type.title()} | {stats['trades']} | "
                           f"{stats['win_rate']:.1f}% | {stats['avg_r']:.2f}R | "
                           f"{stats['ev_per_trade']:.2f}R |\n")
            f.write("\n")
            
            # Best Combinations
            f.write("## 🏆 Best Performing Combinations\n\n")
            
            # Symbol + Timeframe combinations
            combo_stats = defaultdict(lambda: {
                'trades': 0, 'r_multiples': []
            })
            
            for trade in self.all_trades:
                key = f"{trade.symbol}_{trade.timeframe}"
                combo_stats[key]['trades'] += 1
                combo_stats[key]['r_multiples'].append(trade.r_multiple)
            
            # Calculate EV for each combo
            combo_results = []
            for key, stats in combo_stats.items():
                if stats['trades'] >= 3:  # Min 3 trades for significance
                    avg_r = np.mean(stats['r_multiples'])
                    combo_results.append({
                        'combo': key,
                        'trades': stats['trades'],
                        'avg_r': avg_r
                    })
            
            # Sort by avg_r
            combo_results.sort(key=lambda x: x['avg_r'], reverse=True)
            
            if combo_results:
                f.write("| Symbol + Timeframe | Trades | Avg R |\n")
                f.write("|--------------------|--------|-------|\n")
                for combo in combo_results[:10]:  # Top 10
                    f.write(f"| {combo['combo']} | {combo['trades']} | "
                           f"{combo['avg_r']:.2f}R |\n")
            else:
                f.write("*Insufficient data for combination analysis*\n")
            f.write("\n")
            
            # Verdict
            f.write("## 🎯 IS THIS TRADEABLE?\n\n")
            
            if ev_per_trade > 0.3 and win_rate > 45:
                verdict = "✅ **YES** - Positive expected value with acceptable win rate"
                f.write(f"{verdict}\n\n")
                f.write("**Key Strengths:**\n")
                if win_rate > 50:
                    f.write(f"- Win rate above 50% ({win_rate:.1f}%)\n")
                if avg_r > 0.5:
                    f.write(f"- Strong average R-multiple ({avg_r:.2f}R)\n")
                if ev_per_trade > 0.5:
                    f.write(f"- High expected value per trade ({ev_per_trade:.2f}R)\n")
            elif ev_per_trade > 0:
                verdict = "⚠️ **MARGINAL** - Positive EV but requires optimization"
                f.write(f"{verdict}\n\n")
                f.write("**Concerns:**\n")
                if win_rate < 45:
                    f.write(f"- Low win rate ({win_rate:.1f}%)\n")
                if avg_r < 0.3:
                    f.write(f"- Weak average R-multiple ({avg_r:.2f}R)\n")
                f.write("\n**Recommendations:**\n")
                f.write("- Focus on best-performing symbols/timeframes\n")
                f.write("- Consider stricter entry filters\n")
                f.write("- Test different R:R ratios\n")
            else:
                verdict = "❌ **NO** - Negative expected value"
                f.write(f"{verdict}\n\n")
                f.write("**Issues:**\n")
                f.write(f"- Negative expected value ({ev_per_trade:.2f}R)\n")
                if win_rate < 40:
                    f.write(f"- Poor win rate ({win_rate:.1f}%)\n")
                f.write("\n**This strategy is not recommended for live trading.**\n")
            
            f.write("\n---\n\n")
            f.write("*Backtest results are not indicative of future performance. "
                   "Test on paper trading before risking real capital.*\n")
        
        print("✓ Markdown report written")
    
    def _write_json_data(self):
        """Write raw data to JSON"""
        data = {
            'config': {
                'symbols': BacktestConfig.SYMBOLS,
                'timeframes': BacktestConfig.TIMEFRAMES,
                'start_date': BacktestConfig.START_DATE.isoformat(),
                'end_date': BacktestConfig.END_DATE.isoformat(),
                'min_price_move': BacktestConfig.MIN_PRICE_MOVE,
                'min_volume_ratio': BacktestConfig.MIN_VOLUME_RATIO,
                'zone_tolerance': BacktestConfig.ZONE_TOLERANCE,
                'risk_reward_ratio': BacktestConfig.RISK_REWARD_RATIO
            },
            'summary': {
                'total_trades': len(self.all_trades),
                'wins': len([t for t in self.all_trades if t.outcome == 'win']),
                'losses': len([t for t in self.all_trades if t.outcome == 'loss']),
                'timeouts': len([t for t in self.all_trades if t.outcome == 'timeout']),
                'win_rate': (len([t for t in self.all_trades if t.outcome == 'win']) / 
                           len(self.all_trades) * 100) if self.all_trades else 0,
                'avg_r_multiple': np.mean([t.r_multiple for t in self.all_trades]) if self.all_trades else 0,
                'expected_value': np.mean([t.r_multiple for t in self.all_trades]) if self.all_trades else 0
            },
            'trades': [trade.to_dict() for trade in self.all_trades],
            'detection_stats': dict(self.detection_stats),
            'errors': self.errors
        }
        
        with open('backtest-data.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        print("✓ JSON data written")


def main():
    """Main entry point"""
    try:
        backtest = OrderBlockBacktest()
        backtest.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Backtest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
