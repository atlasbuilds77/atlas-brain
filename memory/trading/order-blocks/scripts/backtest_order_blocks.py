#!/usr/bin/env python3
"""
Comprehensive Order Block Backtest
Tests order block detector across multiple symbols, timeframes, and historical periods
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import json

try:
    import pandas as pd
    import numpy as np
    from alpaca_trade_api import REST
except ImportError:
    print("ERROR: Required packages not installed")
    print("Run: pip install pandas numpy alpaca-trade-api")
    sys.exit(1)

# Import the detector
sys.path.append(os.path.dirname(__file__))
from order_block_detector import OrderBlockDetector, OrderBlock


class OrderBlockBacktest:
    """Backtest framework for order block detection"""
    
    def __init__(self, alpaca_api: REST):
        self.alpaca = alpaca_api
        self.results = []
        
    def fetch_historical_data(self, symbol: str, timeframe: str, 
                             start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Fetch historical bar data from Alpaca"""
        try:
            bars = self.alpaca.get_bars(
                symbol,
                timeframe,
                start=start_date.isoformat(),
                end=end_date.isoformat(),
                limit=10000
            ).df
            
            df = pd.DataFrame({
                'timestamp': bars.index,
                'open': bars['open'].values,
                'high': bars['high'].values,
                'low': bars['low'].values,
                'close': bars['close'].values,
                'volume': bars['volume'].values
            })
            
            return df.reset_index(drop=True)
            
        except Exception as e:
            print(f"ERROR fetching {symbol} {timeframe}: {e}")
            return pd.DataFrame()
    
    def test_order_block(self, ob: OrderBlock, future_data: pd.DataFrame, 
                        lookforward_bars: int = 50) -> Dict:
        """
        Test if an order block was respected by future price action
        
        Returns:
            Dict with test results including win/loss, R:R, etc.
        """
        if len(future_data) == 0:
            return None
        
        # Define zone boundaries
        zone_low = ob.start_price
        zone_high = ob.end_price
        zone_mid = (zone_low + zone_high) / 2
        
        # Calculate stop loss and target levels
        if ob.type == 'bullish':
            # For bullish OB: entry at zone high, stop below zone low
            entry_price = zone_high
            stop_loss = zone_low - (zone_high - zone_low) * 0.1  # 10% buffer below
            risk = entry_price - stop_loss
            target = entry_price + (risk * 2)  # 2:1 R:R
            
            # Track if price returned to test the zone
            touched_zone = False
            entry_bar = None
            
            for i, row in future_data.iterrows():
                # Check if price touched the zone (within 2% tolerance)
                if row['low'] <= zone_high * 1.02 and row['low'] >= zone_low * 0.98:
                    touched_zone = True
                    entry_bar = i
                    break
            
            if not touched_zone:
                return {
                    'tested': False,
                    'outcome': 'not_tested',
                    'reason': 'Price never returned to zone'
                }
            
            # Check outcome after entry
            trade_data = future_data.iloc[entry_bar:]
            hit_stop = False
            hit_target = False
            bars_to_result = 0
            
            for i, row in trade_data.iterrows():
                bars_to_result += 1
                
                # Check stop loss first (wicks matter)
                if row['low'] <= stop_loss:
                    hit_stop = True
                    break
                
                # Check target
                if row['high'] >= target:
                    hit_target = True
                    break
                
                # Max holding period
                if bars_to_result >= lookforward_bars:
                    break
            
            # Determine outcome
            if hit_target:
                outcome = 'win'
                rr_achieved = 2.0
            elif hit_stop:
                outcome = 'loss'
                rr_achieved = -1.0
            else:
                # Calculate partial R:R if no clear outcome
                final_price = trade_data.iloc[min(bars_to_result-1, len(trade_data)-1)]['close']
                rr_achieved = (final_price - entry_price) / risk if risk > 0 else 0
                outcome = 'partial_win' if rr_achieved > 0 else 'partial_loss'
            
            return {
                'tested': True,
                'outcome': outcome,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'target': target,
                'risk': risk,
                'rr_achieved': rr_achieved,
                'bars_to_result': bars_to_result,
                'hit_target': hit_target,
                'hit_stop': hit_stop
            }
        
        else:  # bearish
            # For bearish OB: entry at zone low, stop above zone high
            entry_price = zone_low
            stop_loss = zone_high + (zone_high - zone_low) * 0.1  # 10% buffer above
            risk = stop_loss - entry_price
            target = entry_price - (risk * 2)  # 2:1 R:R
            
            # Track if price returned to test the zone
            touched_zone = False
            entry_bar = None
            
            for i, row in future_data.iterrows():
                # Check if price touched the zone (within 2% tolerance)
                if row['high'] >= zone_low * 0.98 and row['high'] <= zone_high * 1.02:
                    touched_zone = True
                    entry_bar = i
                    break
            
            if not touched_zone:
                return {
                    'tested': False,
                    'outcome': 'not_tested',
                    'reason': 'Price never returned to zone'
                }
            
            # Check outcome after entry
            trade_data = future_data.iloc[entry_bar:]
            hit_stop = False
            hit_target = False
            bars_to_result = 0
            
            for i, row in trade_data.iterrows():
                bars_to_result += 1
                
                # Check stop loss first (wicks matter)
                if row['high'] >= stop_loss:
                    hit_stop = True
                    break
                
                # Check target
                if row['low'] <= target:
                    hit_target = True
                    break
                
                # Max holding period
                if bars_to_result >= lookforward_bars:
                    break
            
            # Determine outcome
            if hit_target:
                outcome = 'win'
                rr_achieved = 2.0
            elif hit_stop:
                outcome = 'loss'
                rr_achieved = -1.0
            else:
                # Calculate partial R:R if no clear outcome
                final_price = trade_data.iloc[min(bars_to_result-1, len(trade_data)-1)]['close']
                rr_achieved = (entry_price - final_price) / risk if risk > 0 else 0
                outcome = 'partial_win' if rr_achieved > 0 else 'partial_loss'
            
            return {
                'tested': True,
                'outcome': outcome,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'target': target,
                'risk': risk,
                'rr_achieved': rr_achieved,
                'bars_to_result': bars_to_result,
                'hit_target': hit_target,
                'hit_stop': hit_stop
            }
    
    def run_backtest(self, symbol: str, timeframe: str, 
                     start_date: datetime, end_date: datetime,
                     detector: OrderBlockDetector) -> Dict:
        """Run backtest for a single symbol/timeframe combination"""
        
        print(f"\n{'='*80}")
        print(f"Testing {symbol} on {timeframe} from {start_date.date()} to {end_date.date()}")
        print(f"{'='*80}")
        
        # Fetch data
        df = self.fetch_historical_data(symbol, timeframe, start_date, end_date)
        
        if len(df) < 100:
            print(f"⚠️  Insufficient data for {symbol} {timeframe}: {len(df)} bars")
            return None
        
        print(f"✓ Fetched {len(df)} bars")
        
        # Split data: use first 60% for detection, last 40% for validation
        split_idx = int(len(df) * 0.6)
        detection_df = df.iloc[:split_idx].copy()
        validation_df = df.iloc[split_idx:].copy()
        
        # Detect order blocks
        print(f"Detecting order blocks in first {len(detection_df)} bars...")
        order_blocks = detector.detect_order_blocks(detection_df)
        
        if len(order_blocks) == 0:
            print("⚠️  No order blocks detected")
            return {
                'symbol': symbol,
                'timeframe': timeframe,
                'total_bars': len(df),
                'order_blocks_detected': 0,
                'trades': []
            }
        
        print(f"✓ Detected {len(order_blocks)} order blocks")
        
        # Test each order block against future data
        trades = []
        for ob in order_blocks:
            # Get future data after the order block formation
            ob_bar_idx = ob.candle_index
            future_start_idx = ob_bar_idx + 1 - split_idx  # Adjust for validation df
            
            if future_start_idx < 0:
                # Order block is too late in detection period
                continue
            
            if future_start_idx >= len(validation_df):
                # No future data available
                continue
            
            future_data = validation_df.iloc[future_start_idx:].copy()
            
            # Test the order block
            test_result = self.test_order_block(ob, future_data)
            
            if test_result:
                trade = {
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'ob_type': ob.type,
                    'ob_strength': ob.strength,
                    'ob_volume_ratio': ob.volume_ratio,
                    'ob_price_move_pct': ob.price_move_pct,
                    'formation_time': ob.timestamp.isoformat(),
                    **test_result
                }
                trades.append(trade)
        
        print(f"✓ Tested {len(trades)} order blocks with future data")
        
        # Calculate statistics
        tested_trades = [t for t in trades if t['tested']]
        wins = [t for t in tested_trades if t['outcome'] in ['win', 'partial_win']]
        losses = [t for t in tested_trades if t['outcome'] in ['loss', 'partial_loss']]
        full_wins = [t for t in tested_trades if t['outcome'] == 'win']
        full_losses = [t for t in tested_trades if t['outcome'] == 'loss']
        
        win_rate = len(wins) / len(tested_trades) * 100 if len(tested_trades) > 0 else 0
        full_win_rate = len(full_wins) / len(tested_trades) * 100 if len(tested_trades) > 0 else 0
        
        avg_rr = np.mean([t['rr_achieved'] for t in tested_trades]) if len(tested_trades) > 0 else 0
        
        # Expected value (EV) calculation
        # EV = (Win Rate × Avg Win) - (Loss Rate × Avg Loss)
        avg_win_rr = np.mean([t['rr_achieved'] for t in wins]) if len(wins) > 0 else 0
        avg_loss_rr = abs(np.mean([t['rr_achieved'] for t in losses])) if len(losses) > 0 else 0
        
        win_rate_decimal = len(wins) / len(tested_trades) if len(tested_trades) > 0 else 0
        loss_rate_decimal = len(losses) / len(tested_trades) if len(tested_trades) > 0 else 0
        
        expected_value = (win_rate_decimal * avg_win_rr) - (loss_rate_decimal * avg_loss_rr)
        
        results = {
            'symbol': symbol,
            'timeframe': timeframe,
            'total_bars': len(df),
            'order_blocks_detected': len(order_blocks),
            'order_blocks_tested': len(tested_trades),
            'trades': trades,
            'win_rate_pct': round(win_rate, 2),
            'full_win_rate_pct': round(full_win_rate, 2),
            'avg_rr': round(avg_rr, 2),
            'expected_value': round(expected_value, 2),
            'total_wins': len(wins),
            'total_losses': len(losses),
            'full_wins': len(full_wins),
            'full_losses': len(full_losses)
        }
        
        print(f"\n📊 Results:")
        print(f"  Order Blocks Detected: {len(order_blocks)}")
        print(f"  Order Blocks Tested: {len(tested_trades)}")
        print(f"  Win Rate: {win_rate:.1f}% ({len(wins)}/{len(tested_trades)})")
        print(f"  Full Win Rate: {full_win_rate:.1f}% ({len(full_wins)}/{len(tested_trades)})")
        print(f"  Average R:R: {avg_rr:.2f}")
        print(f"  Expected Value: {expected_value:.2f}R")
        
        return results


def main():
    """Main backtest execution"""
    
    # Check for API credentials
    api_key = os.environ.get('ALPACA_API_KEY')
    api_secret = os.environ.get('ALPACA_API_SECRET')
    
    if not api_key or not api_secret:
        print("ERROR: Alpaca API credentials not found")
        print("Set environment variables:")
        print("  export ALPACA_API_KEY='your_key'")
        print("  export ALPACA_API_SECRET='your_secret'")
        sys.exit(1)
    
    # Initialize Alpaca API
    alpaca = REST(api_key, api_secret, base_url='https://paper-api.alpaca.markets')
    
    # Backtest configuration
    SYMBOLS = ['SPY', 'QQQ', 'AAPL', 'TSLA', 'NVDA']
    TIMEFRAMES = ['5Min', '15Min', '1Hour']
    
    # Date range: July 2024 - January 2025 (6 months)
    END_DATE = datetime(2025, 1, 31)
    START_DATE = datetime(2024, 7, 1)
    
    print("=" * 80)
    print("ORDER BLOCK DETECTOR - COMPREHENSIVE BACKTEST")
    print("=" * 80)
    print(f"Date Range: {START_DATE.date()} to {END_DATE.date()}")
    print(f"Symbols: {', '.join(SYMBOLS)}")
    print(f"Timeframes: {', '.join(TIMEFRAMES)}")
    print("=" * 80)
    
    # Initialize detector with ADJUSTED parameters
    detector = OrderBlockDetector(
        min_volume_ratio=1.3,   # Reduced from 1.5
        min_price_move=1.2,     # Reduced from 2.0
        lookback_candles=5
    )
    
    print("\n🔧 Detector Parameters (ADJUSTED):")
    print(f"  min_volume_ratio: 1.3 (was 1.5)")
    print(f"  min_price_move: 1.2% (was 2.0%)")
    print(f"  min_strength: 6.0 (unchanged)")
    
    # Run backtests
    backtester = OrderBlockBacktest(alpaca)
    all_results = []
    
    for symbol in SYMBOLS:
        for timeframe in TIMEFRAMES:
            try:
                result = backtester.run_backtest(
                    symbol=symbol,
                    timeframe=timeframe,
                    start_date=START_DATE,
                    end_date=END_DATE,
                    detector=detector
                )
                
                if result:
                    all_results.append(result)
                    
            except Exception as e:
                print(f"\n❌ Error testing {symbol} {timeframe}: {e}")
                continue
    
    # Generate summary report
    print("\n" + "=" * 80)
    print("BACKTEST COMPLETE - GENERATING SUMMARY")
    print("=" * 80)
    
    # Aggregate statistics
    total_obs = sum(r['order_blocks_detected'] for r in all_results)
    total_tested = sum(r['order_blocks_tested'] for r in all_results)
    
    # Overall win rate
    all_trades = []
    for r in all_results:
        all_trades.extend(r['trades'])
    
    tested_trades = [t for t in all_trades if t['tested']]
    wins = [t for t in tested_trades if t['outcome'] in ['win', 'partial_win']]
    full_wins = [t for t in tested_trades if t['outcome'] == 'win']
    
    overall_win_rate = len(wins) / len(tested_trades) * 100 if len(tested_trades) > 0 else 0
    overall_full_win_rate = len(full_wins) / len(tested_trades) * 100 if len(tested_trades) > 0 else 0
    overall_avg_rr = np.mean([t['rr_achieved'] for t in tested_trades]) if len(tested_trades) > 0 else 0
    
    # Best performing by timeframe
    by_timeframe = {}
    for tf in TIMEFRAMES:
        tf_trades = [t for t in tested_trades if t['timeframe'] == tf]
        if len(tf_trades) > 0:
            tf_wins = [t for t in tf_trades if t['outcome'] in ['win', 'partial_win']]
            by_timeframe[tf] = {
                'total': len(tf_trades),
                'wins': len(tf_wins),
                'win_rate': len(tf_wins) / len(tf_trades) * 100,
                'avg_rr': np.mean([t['rr_achieved'] for t in tf_trades])
            }
    
    # Best performing by symbol
    by_symbol = {}
    for sym in SYMBOLS:
        sym_trades = [t for t in tested_trades if t['symbol'] == sym]
        if len(sym_trades) > 0:
            sym_wins = [t for t in sym_trades if t['outcome'] in ['win', 'partial_win']]
            by_symbol[sym] = {
                'total': len(sym_trades),
                'wins': len(sym_wins),
                'win_rate': len(sym_wins) / len(sym_trades) * 100,
                'avg_rr': np.mean([t['rr_achieved'] for t in sym_trades])
            }
    
    # Generate markdown report
    report = generate_markdown_report(
        all_results=all_results,
        total_obs=total_obs,
        total_tested=total_tested,
        overall_win_rate=overall_win_rate,
        overall_full_win_rate=overall_full_win_rate,
        overall_avg_rr=overall_avg_rr,
        by_timeframe=by_timeframe,
        by_symbol=by_symbol,
        tested_trades=tested_trades,
        start_date=START_DATE,
        end_date=END_DATE
    )
    
    # Save results
    output_path = '/Users/atlasbuilds/clawd/memory/trading/order-blocks/backtest-results.md'
    with open(output_path, 'w') as f:
        f.write(report)
    
    print(f"\n✅ Full backtest report saved to: {output_path}")
    
    # Also save raw JSON data
    json_path = '/Users/atlasbuilds/clawd/memory/trading/order-blocks/backtest-data.json'
    with open(json_path, 'w') as f:
        json.dump({
            'backtest_date': datetime.now().isoformat(),
            'parameters': {
                'min_volume_ratio': 1.3,
                'min_price_move': 1.2,
                'lookback_candles': 5
            },
            'date_range': {
                'start': START_DATE.isoformat(),
                'end': END_DATE.isoformat()
            },
            'results': all_results
        }, f, indent=2)
    
    print(f"✅ Raw data saved to: {json_path}")


def generate_markdown_report(all_results, total_obs, total_tested, overall_win_rate,
                             overall_full_win_rate, overall_avg_rr, by_timeframe,
                             by_symbol, tested_trades, start_date, end_date) -> str:
    """Generate comprehensive markdown report"""
    
    lines = []
    lines.append("# ORDER BLOCK DETECTOR - COMPREHENSIVE BACKTEST RESULTS")
    lines.append("")
    lines.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Historical Period:** {start_date.date()} to {end_date.date()} (6 months)")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Executive Summary
    lines.append("## 📊 EXECUTIVE SUMMARY")
    lines.append("")
    lines.append(f"- **Total Order Blocks Detected:** {total_obs}")
    lines.append(f"- **Order Blocks Tested:** {total_tested}")
    lines.append(f"- **Overall Win Rate:** {overall_win_rate:.1f}%")
    lines.append(f"- **Full Win Rate (2:1 R:R):** {overall_full_win_rate:.1f}%")
    lines.append(f"- **Average R:R:** {overall_avg_rr:.2f}")
    lines.append("")
    
    # Verdict
    lines.append("## ✅ VERDICT")
    lines.append("")
    
    if overall_win_rate >= 60 and overall_avg_rr >= 0.8:
        verdict = "✅ **TRADEABLE** - High confidence"
        confidence = 85
    elif overall_win_rate >= 50 and overall_avg_rr >= 0.5:
        verdict = "⚠️ **TRADEABLE WITH CAUTION** - Moderate confidence"
        confidence = 65
    elif overall_win_rate >= 40:
        verdict = "⚠️ **MARGINAL** - Low confidence, needs refinement"
        confidence = 40
    else:
        verdict = "❌ **NOT TRADEABLE** - Performance too weak"
        confidence = 20
    
    lines.append(verdict)
    lines.append(f"**Confidence Score:** {confidence}/100")
    lines.append("")
    
    # Performance by Timeframe
    lines.append("## 📈 PERFORMANCE BY TIMEFRAME")
    lines.append("")
    lines.append("| Timeframe | Trades | Wins | Win Rate | Avg R:R |")
    lines.append("|-----------|--------|------|----------|---------|")
    
    for tf in sorted(by_timeframe.keys()):
        stats = by_timeframe[tf]
        lines.append(f"| {tf} | {stats['total']} | {stats['wins']} | {stats['win_rate']:.1f}% | {stats['avg_rr']:.2f} |")
    
    lines.append("")
    
    # Best timeframe
    if by_timeframe:
        best_tf = max(by_timeframe.items(), key=lambda x: x[1]['win_rate'])
        lines.append(f"**Best Timeframe:** {best_tf[0]} ({best_tf[1]['win_rate']:.1f}% win rate)")
        lines.append("")
    
    # Performance by Symbol
    lines.append("## 🎯 PERFORMANCE BY SYMBOL")
    lines.append("")
    lines.append("| Symbol | Trades | Wins | Win Rate | Avg R:R |")
    lines.append("|--------|--------|------|----------|---------|")
    
    for sym in sorted(by_symbol.keys()):
        stats = by_symbol[sym]
        lines.append(f"| {sym} | {stats['total']} | {stats['wins']} | {stats['win_rate']:.1f}% | {stats['avg_rr']:.2f} |")
    
    lines.append("")
    
    # Best symbol
    if by_symbol:
        best_sym = max(by_symbol.items(), key=lambda x: x[1]['win_rate'])
        lines.append(f"**Best Symbol:** {best_sym[0]} ({best_sym[1]['win_rate']:.1f}% win rate)")
        lines.append("")
    
    # Detailed Results
    lines.append("## 📋 DETAILED RESULTS BY COMBINATION")
    lines.append("")
    
    for result in all_results:
        lines.append(f"### {result['symbol']} - {result['timeframe']}")
        lines.append("")
        lines.append(f"- Order Blocks Detected: {result['order_blocks_detected']}")
        lines.append(f"- Order Blocks Tested: {result['order_blocks_tested']}")
        lines.append(f"- Win Rate: {result['win_rate_pct']}%")
        lines.append(f"- Full Win Rate: {result['full_win_rate_pct']}%")
        lines.append(f"- Average R:R: {result['avg_rr']}")
        lines.append(f"- Expected Value: {result['expected_value']}R")
        lines.append("")
    
    # Parameter Recommendations
    lines.append("## 🔧 PARAMETER RECOMMENDATIONS")
    lines.append("")
    lines.append("**Current Parameters (Adjusted):**")
    lines.append("- `min_volume_ratio`: 1.3 (was 1.5)")
    lines.append("- `min_price_move`: 1.2% (was 2.0%)")
    lines.append("- `min_strength`: 6.0")
    lines.append("")
    
    if overall_win_rate >= 55:
        lines.append("**Recommendation:** Parameters are well-tuned. Consider slight tightening for higher quality:")
        lines.append("- Increase `min_strength` to 7.0 for higher conviction trades")
    elif overall_win_rate < 45:
        lines.append("**Recommendation:** Parameters may still be too strict. Consider further relaxation:")
        lines.append("- Reduce `min_volume_ratio` to 1.2")
        lines.append("- Reduce `min_price_move` to 1.0%")
    else:
        lines.append("**Recommendation:** Parameters are reasonable. Fine-tune based on symbol/timeframe preferences.")
    
    lines.append("")
    
    # Key Insights
    lines.append("## 💡 KEY INSIGHTS")
    lines.append("")
    
    # Bullish vs Bearish
    bullish_trades = [t for t in tested_trades if t['ob_type'] == 'bullish']
    bearish_trades = [t for t in tested_trades if t['ob_type'] == 'bearish']
    
    bullish_wins = [t for t in bullish_trades if t['outcome'] in ['win', 'partial_win']]
    bearish_wins = [t for t in bearish_trades if t['outcome'] in ['win', 'partial_win']]
    
    bullish_wr = len(bullish_wins) / len(bullish_trades) * 100 if len(bullish_trades) > 0 else 0
    bearish_wr = len(bearish_wins) / len(bearish_trades) * 100 if len(bearish_trades) > 0 else 0
    
    lines.append(f"1. **Bullish Order Blocks:** {bullish_wr:.1f}% win rate ({len(bullish_wins)}/{len(bullish_trades)} trades)")
    lines.append(f"2. **Bearish Order Blocks:** {bearish_wr:.1f}% win rate ({len(bearish_wins)}/{len(bearish_trades)} trades)")
    
    if abs(bullish_wr - bearish_wr) > 10:
        better = 'Bullish' if bullish_wr > bearish_wr else 'Bearish'
        lines.append(f"3. **Bias Detected:** {better} order blocks perform significantly better")
    else:
        lines.append(f"3. **No Significant Bias:** Both types perform similarly")
    
    lines.append("")
    
    # Trading Recommendations
    lines.append("## 📝 TRADING RECOMMENDATIONS")
    lines.append("")
    lines.append("1. **Risk Management:**")
    lines.append("   - Always use stop loss below/above order block zone")
    lines.append("   - Target minimum 2:1 R:R ratio")
    lines.append("   - Position size based on stop distance")
    lines.append("")
    lines.append("2. **Entry Strategy:**")
    lines.append("   - Wait for price to return to order block zone")
    lines.append("   - Enter on confirmation (bullish/bearish candle in zone)")
    lines.append("   - Consider scaling in if zone is large")
    lines.append("")
    lines.append("3. **Timeframe Selection:**")
    
    if by_timeframe:
        best_tf = max(by_timeframe.items(), key=lambda x: x[1]['win_rate'])
        lines.append(f"   - **Primary:** {best_tf[0]} (highest win rate)")
        lines.append(f"   - **Avoid:** Lower performing timeframes unless confirmed")
    
    lines.append("")
    lines.append("4. **Symbol Selection:**")
    
    if by_symbol:
        best_sym = max(by_symbol.items(), key=lambda x: x[1]['win_rate'])
        lines.append(f"   - **Primary:** {best_sym[0]} (highest win rate)")
        lines.append(f"   - **Focus:** Top 3 performing symbols for consistency")
    
    lines.append("")
    
    # Conclusion
    lines.append("## 🎯 CONCLUSION")
    lines.append("")
    
    if overall_win_rate >= 55:
        lines.append("The order block detector shows **strong performance** with adjusted parameters. ")
        lines.append("The system is suitable for live trading with proper risk management. ")
        lines.append("Focus on best-performing timeframes and symbols for optimal results.")
    elif overall_win_rate >= 45:
        lines.append("The order block detector shows **acceptable performance** with room for improvement. ")
        lines.append("Consider additional filters (trend alignment, volume profile) for higher conviction setups. ")
        lines.append("Paper trade before committing real capital.")
    else:
        lines.append("The order block detector shows **weak performance** and needs further refinement. ")
        lines.append("Consider revising detection logic or adding confirmation filters. ")
        lines.append("**NOT recommended for live trading** in current state.")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"*Backtest completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    
    return "\n".join(lines)


if __name__ == '__main__':
    main()
