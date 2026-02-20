#!/usr/bin/env python3
"""
TITAN V3 STRUCTURED TARGETS - 3 Month Backtest
===============================================
Per Orion's guidance (Feb 14):
- 80% 0DTE: Target = OPEN (quick scalp)
- 20% 1DTE: Target = OPPOSITE PM level (or nearest cluster)
- Strike: $3 OTM (not at target, not extreme)
- Always trade level to level (PM high/low or clusters)
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import time
import pytz
import json

# ============================================================
# CONFIG
# ============================================================

POLYGON_API_KEY = "h7J74V1cd8_4NQpTxwQpudpqXWaIHMhv"
ET = pytz.timezone('US/Eastern')

# Position sizing
POSITION_SIZE = 1000  # $1000 per trade total
SPLIT_0DTE = 0.80     # 80% in 0DTE (scalp)
SPLIT_1DTE = 0.20     # 20% in 1DTE (runner)

# Strike selection
OTM_OFFSET = 3.0  # $3 OTM

# Exit rules - TIGHT IS BETTER (tested both)
MAX_LOSS_PCT = -50    # Tighter stop (was -80)
TRAIL_TRIGGER_30 = 30  # Start trailing at +30%
TRAIL_STOP_30 = 15     # Trail at +15%
TRAIL_TRIGGER_50 = 50  # Tighter trail at +50%
TRAIL_STOP_50 = 30     # Trail at +30%

# Reclaim rule
MAX_RECLAIM_BARS = 5   # Must reclaim within 5 mins

# ============================================================
# DATA FUNCTIONS
# ============================================================

def fetch_minute_bars(symbol: str, date: str) -> Dict[str, List[dict]]:
    """Fetch 1-minute bars from Polygon."""
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{date}/{date}"
    params = {"apiKey": POLYGON_API_KEY, "limit": 50000}
    
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
    except:
        return {"premarket": [], "regular": [], "all": []}
    
    if data.get('status') != 'OK' or not data.get('results'):
        return {"premarket": [], "regular": [], "all": []}
    
    premarket = []
    regular = []
    
    for bar in data['results']:
        ts = datetime.fromtimestamp(bar['t'] / 1000, tz=pytz.UTC)
        ts_et = ts.astimezone(ET)
        
        bar_data = {
            'time': ts_et.strftime('%H:%M'),
            'dt': ts_et,
            'o': bar['o'],
            'h': bar['h'],
            'l': bar['l'],
            'c': bar['c'],
            'v': bar['v']
        }
        
        if (ts_et.hour >= 4 and ts_et.hour < 9) or (ts_et.hour == 9 and ts_et.minute < 30):
            premarket.append(bar_data)
        elif (ts_et.hour == 9 and ts_et.minute >= 30) or (ts_et.hour >= 10 and ts_et.hour < 16):
            regular.append(bar_data)
    
    return {"premarket": premarket, "regular": regular}


def fetch_daily_bars(symbol: str, start: str, end: str) -> List[dict]:
    """Fetch daily bars from Polygon."""
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{start}/{end}"
    params = {"apiKey": POLYGON_API_KEY, "limit": 50000, "adjusted": "true"}
    
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
    except Exception as e:
        print(f"Fetch error: {e}")
        return []
    
    # Accept 'OK' or 'DELAYED' status
    if data.get('status') not in ['OK', 'DELAYED'] or not data.get('results'):
        print(f"API status: {data.get('status')}, results: {len(data.get('results', []))}")
        return []
    
    return [{
        'date': datetime.fromtimestamp(b['t'] / 1000).strftime('%Y-%m-%d'),
        'o': b['o'], 'h': b['h'], 'l': b['l'], 'c': b['c']
    } for b in data['results']]


def get_option_bars(symbol: str, date: str, strike: float, opt_type: str, dte: int = 0) -> Optional[List[dict]]:
    """Get option minute bars from Polygon."""
    trade_date = datetime.strptime(date, '%Y-%m-%d')
    exp_date = trade_date + timedelta(days=dte)
    
    # Skip to next trading day if weekend
    while exp_date.weekday() >= 5:
        exp_date += timedelta(days=1)
    
    exp_str = exp_date.strftime('%y%m%d')
    strike_str = f"{int(strike * 1000):08d}"
    opt_char = 'P' if opt_type == 'put' else 'C'
    
    option_ticker = f"O:{symbol}{exp_str}{opt_char}{strike_str}"
    
    url = f"https://api.polygon.io/v2/aggs/ticker/{option_ticker}/range/1/minute/{date}/{date}"
    params = {"apiKey": POLYGON_API_KEY, "limit": 50000}
    
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
    except:
        return None
    
    if data.get('status') != 'OK' or not data.get('results'):
        return None
    
    bars = []
    for bar in data['results']:
        ts = datetime.fromtimestamp(bar['t'] / 1000, tz=pytz.UTC)
        ts_et = ts.astimezone(ET)
        bars.append({
            'time': ts_et.strftime('%H:%M'),
            'dt': ts_et,
            'o': bar['o'],
            'h': bar['h'],
            'l': bar['l'],
            'c': bar['c']
        })
    
    return bars if bars else None


# ============================================================
# LEVEL DETECTION
# ============================================================

def get_premarket_levels(pm_bars: List[dict]) -> Tuple[float, float]:
    """Get premarket high and low."""
    if not pm_bars:
        return None, None
    
    pm_high = max(b['h'] for b in pm_bars)
    pm_low = min(b['l'] for b in pm_bars)
    return pm_high, pm_low


def detect_clusters(daily_bars: List[dict], threshold_pct: float = 0.5) -> Dict[str, List[dict]]:
    """Detect clusters of similar highs/lows."""
    all_levels = []
    
    for bar in daily_bars:
        all_levels.append({'price': bar['h'], 'type': 'high', 'date': bar['date']})
        all_levels.append({'price': bar['l'], 'type': 'low', 'date': bar['date']})
    
    # Group into clusters
    sorted_levels = sorted(all_levels, key=lambda x: x['price'])
    
    high_clusters = []
    low_clusters = []
    
    i = 0
    while i < len(sorted_levels):
        cluster_start = sorted_levels[i]
        cluster = [cluster_start]
        
        j = i + 1
        while j < len(sorted_levels):
            price_diff_pct = abs(sorted_levels[j]['price'] - cluster_start['price']) / cluster_start['price'] * 100
            if price_diff_pct <= threshold_pct:
                cluster.append(sorted_levels[j])
                j += 1
            else:
                break
        
        if len(cluster) >= 2:  # At least 2x touch
            avg_price = sum(l['price'] for l in cluster) / len(cluster)
            level_types = [l['type'] for l in cluster]
            
            cluster_data = {
                'price': avg_price,
                'count': len(cluster),
                'type': 'high' if level_types.count('high') >= level_types.count('low') else 'low'
            }
            
            if cluster_data['type'] == 'high':
                high_clusters.append(cluster_data)
            else:
                low_clusters.append(cluster_data)
        
        i = j
    
    # Sort by significance (count)
    high_clusters.sort(key=lambda x: -x['count'])
    low_clusters.sort(key=lambda x: -x['count'])
    
    return {'highs': high_clusters, 'lows': low_clusters}


# ============================================================
# SWEEP DETECTION
# ============================================================

def find_sweep_and_bounce(regular_bars: List[dict], pm_high: float, pm_low: float) -> Optional[dict]:
    """
    Find first valid sweep with reclaim - but enter at reclaim bar OPEN, not close.
    
    Reclaim = confirmation (filters false sweeps)
    Entry = reclaim bar OPEN (faster than close)
    """
    if len(regular_bars) < 10:
        return None
    
    for i, bar in enumerate(regular_bars[:60]):  # First hour only
        # Check PM LOW sweep (LONG setup)
        if bar['l'] < pm_low:
            # Look for reclaim within 5 bars
            for j in range(i + 1, min(i + MAX_RECLAIM_BARS + 1, len(regular_bars))):
                if regular_bars[j]['c'] > pm_low:  # Reclaim confirmed
                    # Enter at reclaim bar OPEN (not close!)
                    return {
                        'direction': 'LONG',
                        'swept_level': pm_low,
                        'sweep_idx': i,
                        'sweep_low': bar['l'],
                        'entry_price': regular_bars[j]['o'],  # Reclaim bar OPEN
                        'entry_time': regular_bars[j]['time'],
                        'target_pm': pm_high
                    }
            continue
        
        # Check PM HIGH sweep (SHORT setup)
        if bar['h'] > pm_high:
            for j in range(i + 1, min(i + MAX_RECLAIM_BARS + 1, len(regular_bars))):
                if regular_bars[j]['c'] < pm_high:  # Reclaim confirmed
                    return {
                        'direction': 'SHORT',
                        'swept_level': pm_high,
                        'sweep_idx': i,
                        'sweep_high': bar['h'],
                        'entry_price': regular_bars[j]['o'],  # Reclaim bar OPEN
                        'entry_time': regular_bars[j]['time'],
                        'target_pm': pm_low
                    }
            continue
    
    return None


# ============================================================
# TRADE SIMULATION
# ============================================================

def simulate_option_trade(
    option_bars: List[dict],
    entry_time: str,
    position_size: float,
    max_loss_pct: float = MAX_LOSS_PCT
) -> dict:
    """
    Walk through option bars and simulate realistic exit.
    Returns P&L with exit reason.
    """
    result = {
        'entry_price': None,
        'exit_price': None,
        'exit_reason': None,
        'pnl': 0,
        'pnl_pct': 0,
        'max_gain_pct': 0
    }
    
    if not option_bars:
        result['exit_reason'] = 'no_data'
        return result
    
    # Find entry bar
    entry_idx = 0
    for i, bar in enumerate(option_bars):
        if bar['time'] >= entry_time:
            entry_idx = i
            break
    
    entry_price = option_bars[entry_idx]['o']
    result['entry_price'] = entry_price
    
    max_gain_pct = 0
    trailing_stop_pct = None
    
    for i in range(entry_idx, len(option_bars)):
        bar = option_bars[i]
        
        high_pct = (bar['h'] - entry_price) / entry_price * 100
        low_pct = (bar['l'] - entry_price) / entry_price * 100
        
        # Update max gain
        if high_pct > max_gain_pct:
            max_gain_pct = high_pct
            result['max_gain_pct'] = max_gain_pct
        
        # Check max loss
        if low_pct <= max_loss_pct:
            result['exit_price'] = entry_price * (1 + max_loss_pct / 100)
            result['exit_reason'] = f'max_loss_{abs(int(max_loss_pct))}'
            result['pnl_pct'] = max_loss_pct
            result['pnl'] = position_size * (max_loss_pct / 100)
            return result
        
        # Update trailing stop
        if max_gain_pct >= TRAIL_TRIGGER_50:
            trailing_stop_pct = TRAIL_STOP_50
        elif max_gain_pct >= TRAIL_TRIGGER_30:
            trailing_stop_pct = TRAIL_STOP_30
        
        # Check trailing stop
        if trailing_stop_pct is not None and low_pct <= trailing_stop_pct:
            result['exit_price'] = entry_price * (1 + trailing_stop_pct / 100)
            result['exit_reason'] = f'TRAIL_{trailing_stop_pct}'
            result['pnl_pct'] = trailing_stop_pct
            result['pnl'] = position_size * (trailing_stop_pct / 100)
            return result
    
    # EOD exit
    exit_price = option_bars[-1]['c']
    result['exit_price'] = exit_price
    result['exit_reason'] = 'EOD'
    result['pnl_pct'] = (exit_price - entry_price) / entry_price * 100
    result['pnl'] = position_size * (result['pnl_pct'] / 100)
    
    return result


# ============================================================
# MAIN ANALYSIS
# ============================================================

def analyze_day(symbol: str, date: str, daily_bars: List[dict]) -> Optional[dict]:
    """Analyze a single day for TITAN V3 setup."""
    
    minute_data = fetch_minute_bars(symbol, date)
    regular_bars = minute_data['regular']
    pm_bars = minute_data['premarket']
    
    if len(regular_bars) < 30 or len(pm_bars) < 5:
        return None
    
    # Get premarket levels
    pm_high, pm_low = get_premarket_levels(pm_bars)
    if not pm_high or not pm_low:
        return None
    
    # PM RANGE FILTER - Skip tight PM days (< $3)
    pm_range = pm_high - pm_low
    if pm_range < 3.0:
        return None  # Skip - weak levels
    
    # Find sweep + bounce setup
    setup = find_sweep_and_bounce(regular_bars, pm_high, pm_low)
    if not setup:
        return None
    
    # Get open price (0DTE target)
    day_open = regular_bars[0]['o']
    
    # Determine strikes ($3 OTM) - SIMPLE TARGETS
    if setup['direction'] == 'LONG':
        strike_0dte = round(setup['entry_price'] + OTM_OFFSET)
        opt_type = 'call'
        
        # 0DTE target = OPEN if above entry, else PM HIGH
        if day_open > setup['entry_price']:
            target_0dte = day_open
        else:
            target_0dte = pm_high
        
        # 1DTE target = PM HIGH (opposite level)
        target_1dte = pm_high
        strike_1dte = round(target_1dte)
        
    else:  # SHORT
        strike_0dte = round(setup['entry_price'] - OTM_OFFSET)
        opt_type = 'put'
        
        if day_open < setup['entry_price']:
            target_0dte = day_open
        else:
            target_0dte = pm_low
        
        # 1DTE target = PM LOW (opposite level)
        target_1dte = pm_low
        strike_1dte = round(target_1dte)
    
    # Calculate target distances
    target_dist_0dte = abs(target_0dte - setup['entry_price'])
    target_dist_1dte = abs(target_1dte - setup['entry_price'])
    # Targets are always PM levels (cluster fallback removed - we skip tight PM days)
    
    # Get option data
    opt_0dte_bars = get_option_bars(symbol, date, strike_0dte, opt_type, dte=0)
    opt_1dte_bars = get_option_bars(symbol, date, strike_1dte, opt_type, dte=1)
    
    # Simulate 0DTE trade (80%)
    size_0dte = POSITION_SIZE * SPLIT_0DTE
    trade_0dte = simulate_option_trade(opt_0dte_bars, setup['entry_time'], size_0dte)
    
    # Simulate 1DTE trade (20%)
    size_1dte = POSITION_SIZE * SPLIT_1DTE
    trade_1dte = simulate_option_trade(opt_1dte_bars, setup['entry_time'], size_1dte)
    
    # Combined result
    combined_pnl = trade_0dte['pnl'] + trade_1dte['pnl']
    
    return {
        'date': date,
        'direction': setup['direction'],
        'entry_price': setup['entry_price'],
        'entry_time': setup['entry_time'],
        'pm_high': pm_high,
        'pm_low': pm_low,
        'day_open': day_open,
        'swept_level': setup['swept_level'],
        'target_0dte': target_0dte,
        'target_1dte': target_1dte,
        'target_dist_0dte': target_dist_0dte,
        'target_dist_1dte': target_dist_1dte,
        'strike_0dte': strike_0dte,
        'strike_1dte': strike_1dte,
        '0dte_result': trade_0dte,
        '1dte_result': trade_1dte,
        'combined_pnl': combined_pnl
    }


def run_backtest(symbol: str = "QQQ", months: int = 3):
    """Run backtest over specified months."""
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 30)
    
    print(f"\n{'='*60}")
    print(f"TITAN V3 STRUCTURED TARGETS - {months} MONTH BACKTEST")
    print(f"{'='*60}")
    print(f"Symbol: {symbol}")
    print(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"Split: {int(SPLIT_0DTE*100)}% 0DTE / {int(SPLIT_1DTE*100)}% 1DTE")
    print(f"Strike: ${OTM_OFFSET} OTM")
    print(f"Max Loss: {MAX_LOSS_PCT}%")
    print(f"Trailing: +{TRAIL_TRIGGER_30}%→{TRAIL_STOP_30}%, +{TRAIL_TRIGGER_50}%→{TRAIL_STOP_50}%")
    print(f"{'='*60}\n")
    
    # Fetch all daily bars
    daily_bars = fetch_daily_bars(symbol, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    if not daily_bars:
        print("ERROR: No daily data")
        return
    
    print(f"Loaded {len(daily_bars)} trading days\n")
    
    results = []
    
    for bar in daily_bars:
        date = bar['date']
        
        # Skip weekends
        dt = datetime.strptime(date, '%Y-%m-%d')
        if dt.weekday() >= 5:
            continue
        
        print(f"Analyzing {date}...", end=" ")
        
        result = analyze_day(symbol, date, daily_bars)
        
        if result:
            pnl = result['combined_pnl']
            emoji = "✅" if pnl > 0 else "❌"
            print(f"{emoji} {result['direction']} | Entry: ${result['entry_price']:.2f} | "
                  f"0DTE: {result['0dte_result']['exit_reason']} ({result['0dte_result']['pnl_pct']:+.0f}%) | "
                  f"1DTE: {result['1dte_result']['exit_reason']} ({result['1dte_result']['pnl_pct']:+.0f}%) | "
                  f"P&L: ${pnl:+.0f}")
            results.append(result)
        else:
            print("⏭️  No setup")
        
        time.sleep(0.15)  # Rate limit
    
    # Summary
    if results:
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        
        wins = [r for r in results if r['combined_pnl'] > 0]
        losses = [r for r in results if r['combined_pnl'] <= 0]
        
        total_pnl = sum(r['combined_pnl'] for r in results)
        
        print(f"Total Trades: {len(results)}")
        print(f"Wins: {len(wins)} ({len(wins)/len(results)*100:.0f}%)")
        print(f"Losses: {len(losses)}")
        print(f"Total P&L: ${total_pnl:+,.0f}")
        
        if wins:
            avg_win = sum(r['combined_pnl'] for r in wins) / len(wins)
            print(f"Avg Win: ${avg_win:+,.0f}")
        
        if losses:
            avg_loss = sum(r['combined_pnl'] for r in losses) / len(losses)
            print(f"Avg Loss: ${avg_loss:+,.0f}")
        
        # Exit breakdown
        print(f"\n0DTE Exit Breakdown:")
        exits_0dte = {}
        for r in results:
            reason = r['0dte_result']['exit_reason']
            exits_0dte[reason] = exits_0dte.get(reason, 0) + 1
        for reason, count in sorted(exits_0dte.items(), key=lambda x: -x[1]):
            print(f"  {reason}: {count}")
        
        print(f"\n1DTE Exit Breakdown:")
        exits_1dte = {}
        for r in results:
            reason = r['1dte_result']['exit_reason']
            exits_1dte[reason] = exits_1dte.get(reason, 0) + 1
        for reason, count in sorted(exits_1dte.items(), key=lambda x: -x[1]):
            print(f"  {reason}: {count}")
        
        # Save results
        with open('titan_v3_structured_results.json', 'w') as f:
            json.dump({
                'config': {
                    'symbol': symbol,
                    'months': months,
                    'split_0dte': SPLIT_0DTE,
                    'split_1dte': SPLIT_1DTE,
                    'otm_offset': OTM_OFFSET,
                    'max_loss': MAX_LOSS_PCT
                },
                'summary': {
                    'total_trades': len(results),
                    'wins': len(wins),
                    'win_rate': len(wins)/len(results)*100,
                    'total_pnl': total_pnl
                },
                'trades': [{
                    'date': r['date'],
                    'direction': r['direction'],
                    'pnl': r['combined_pnl'],
                    '0dte_pnl': r['0dte_result']['pnl'],
                    '1dte_pnl': r['1dte_result']['pnl']
                } for r in results]
            }, f, indent=2)
        
        print(f"\nResults saved to titan_v3_structured_results.json")


if __name__ == "__main__":
    run_backtest("QQQ", months=3)
