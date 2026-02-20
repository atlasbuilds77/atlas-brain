#!/usr/bin/env python3
"""
TITAN V3 - POLYGON EDITION
Extended backtesting with 2 years of options data
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time
import pytz

# ============================================================
# CONFIG
# ============================================================

POLYGON_API_KEY = "h7J74V1cd8_4NQpTxwQpudpqXWaIHMhv"
ET = pytz.timezone('US/Eastern')

# ============================================================
# POLYGON DATA FUNCTIONS
# ============================================================

def fetch_minute_bars_polygon(symbol: str, date: str) -> Dict[str, List[dict]]:
    """Fetch 1-minute bars from Polygon, split into premarket and regular."""
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{date}/{date}"
    params = {"apiKey": POLYGON_API_KEY, "limit": 50000}
    
    r = requests.get(url, params=params)
    data = r.json()
    
    if data.get('status') != 'OK' or not data.get('results'):
        return {"premarket": [], "regular": [], "all": []}
    
    premarket = []
    regular = []
    
    for bar in data['results']:
        # Convert timestamp to ET
        ts = datetime.fromtimestamp(bar['t'] / 1000, tz=pytz.UTC)
        ts_et = ts.astimezone(ET)
        
        bar_data = {
            'time_et': ts_et.strftime('%H:%M'),
            'o': bar['o'],
            'h': bar['h'],
            'l': bar['l'],
            'c': bar['c'],
            'v': bar['v']
        }
        
        # Premarket: 4:00 - 9:30 ET
        if (ts_et.hour >= 4 and ts_et.hour < 9) or (ts_et.hour == 9 and ts_et.minute < 30):
            premarket.append(bar_data)
        # Regular hours: 9:30 - 16:00 ET
        elif (ts_et.hour == 9 and ts_et.minute >= 30) or (ts_et.hour >= 10 and ts_et.hour < 16):
            regular.append(bar_data)
    
    return {"premarket": premarket, "regular": regular, "all": premarket + regular}


def fetch_daily_bars_polygon(symbol: str, start: str, end: str) -> List[dict]:
    """Fetch daily bars from Polygon for swing detection."""
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{start}/{end}"
    params = {"apiKey": POLYGON_API_KEY, "limit": 50000, "adjusted": "true"}
    
    r = requests.get(url, params=params)
    data = r.json()
    
    if data.get('status') != 'OK' or not data.get('results'):
        return []
    
    bars = []
    for bar in data['results']:
        ts = datetime.fromtimestamp(bar['t'] / 1000)
        bars.append({
            'date': ts.strftime('%Y-%m-%d'),
            'o': bar['o'],
            'h': bar['h'],
            'l': bar['l'],
            'c': bar['c']
        })
    
    return sorted(bars, key=lambda x: x['date'])


def get_option_ohlc_polygon(symbol: str, date: str, strike: float, opt_type: str, dte: int = 0) -> Optional[dict]:
    """
    Get option OHLC from Polygon.
    
    Polygon option ticker format: O:QQQ251114P00600000
    - O: prefix for options
    - QQQ: underlying
    - 251114: YYMMDD expiration
    - P/C: put/call
    - 00600000: strike * 1000 (8 digits)
    """
    # Calculate expiration date
    trade_date = datetime.strptime(date, '%Y-%m-%d')
    exp_date = trade_date + timedelta(days=dte)
    
    # Skip weekends
    while exp_date.weekday() >= 5:
        exp_date += timedelta(days=1)
    
    exp_str = exp_date.strftime('%y%m%d')
    strike_str = f"{int(strike * 1000):08d}"
    opt_char = 'P' if opt_type == 'put' else 'C'
    
    option_ticker = f"O:{symbol}{exp_str}{opt_char}{strike_str}"
    
    url = f"https://api.polygon.io/v2/aggs/ticker/{option_ticker}/range/1/day/{date}/{date}"
    params = {"apiKey": POLYGON_API_KEY}
    
    r = requests.get(url, params=params)
    data = r.json()
    
    if data.get('status') == 'OK' and data.get('results'):
        bar = data['results'][0]
        return {
            'open': bar['o'],
            'high': bar['h'],
            'low': bar['l'],
            'close': bar['c'],
            'ticker': option_ticker
        }
    
    return None


# ============================================================
# TITAN V3 CORE LOGIC
# ============================================================

def get_all_levels(daily_bars: List[dict], pm_bars: List[dict] = None) -> Dict[str, List[dict]]:
    """
    Get ALL daily highs/lows as potential levels (not just swings).
    This matches the Tradier version - every daily H/L is a level.
    """
    levels = {'highs': [], 'lows': []}
    
    # Every daily bar's high and low is a level
    for bar in daily_bars:
        levels['highs'].append({'date': bar['date'], 'price': bar['h'], 'type': 'high'})
        levels['lows'].append({'date': bar['date'], 'price': bar['l'], 'type': 'low'})
    
    # Add premarket levels if available
    if pm_bars:
        pm_high = max(b['h'] for b in pm_bars)
        pm_low = min(b['l'] for b in pm_bars)
        levels['highs'].append({'date': 'premarket', 'price': pm_high, 'type': 'high'})
        levels['lows'].append({'date': 'premarket', 'price': pm_low, 'type': 'low'})
    
    return levels


def detect_clusters(levels: List[dict], threshold: float = 0.005) -> List[dict]:
    """Group levels within 0.5% into clusters."""
    if not levels:
        return []
    
    sorted_levels = sorted(levels, key=lambda x: x['price'])
    clusters = []
    current_cluster = [sorted_levels[0]]
    
    for level in sorted_levels[1:]:
        if abs(level['price'] - current_cluster[-1]['price']) / current_cluster[-1]['price'] < threshold:
            current_cluster.append(level)
        else:
            avg_price = sum(l['price'] for l in current_cluster) / len(current_cluster)
            clusters.append({
                'price': avg_price,
                'count': len(current_cluster),
                'level_type': current_cluster[0].get('type', 'unknown')
            })
            current_cluster = [level]
    
    # Don't forget last cluster
    avg_price = sum(l['price'] for l in current_cluster) / len(current_cluster)
    clusters.append({
        'price': avg_price,
        'count': len(current_cluster),
        'level_type': current_cluster[0].get('type', 'unknown')
    })
    
    return sorted(clusters, key=lambda x: x['count'], reverse=True)


def find_sweep_reclaim(bars: List[dict], level: float, level_type: str) -> Optional[dict]:
    """
    Find sweep and reclaim within 5 MINUTES.
    
    RULE (Feb 14, 2026):
    - Reclaim within 5 min = Strong rejection → TAKE IT
    - No reclaim in 5 min = Breakdown → SKIP IT
    """
    MAX_RECLAIM_BARS = 5
    
    for i, bar in enumerate(bars):
        if level_type == "high" and bar['h'] > level:
            for j in range(i + 1, min(i + 1 + MAX_RECLAIM_BARS, len(bars))):
                if bars[j]['c'] < level:
                    return {
                        "sweep_idx": i,
                        "sweep_time": bar['time_et'],
                        "reclaim_idx": j,
                        "reclaim_time": bars[j]['time_et'],
                        "reclaim_mins": j - i,
                        "entry_price": bars[j]['c'],
                        "direction": "SHORT"
                    }
            return None
        
        elif level_type == "low" and bar['l'] < level:
            for j in range(i + 1, min(i + 1 + MAX_RECLAIM_BARS, len(bars))):
                if bars[j]['c'] > level:
                    return {
                        "sweep_idx": i,
                        "sweep_time": bar['time_et'],
                        "reclaim_idx": j,
                        "reclaim_time": bars[j]['time_et'],
                        "reclaim_mins": j - i,
                        "entry_price": bars[j]['c'],
                        "direction": "LONG"
                    }
            return None
    
    return None


def simulate_trade(symbol: str, date: str, direction: str, entry_price: float,
                   target1: float, target2: float, bars: List[dict], entry_idx: int) -> dict:
    """
    Simulate trade and get option P/L.
    
    KEY LOGIC (80/20 split):
    - 0DTE (80%) → strike at TARGET1 (first level)
    - 1DTE (20%) → strike at TARGET2 (second level, more OTM for bigger move)
    """
    
    result = {"hit_target": False, "stopped": False}
    
    # Determine option type and strikes
    if direction == "SHORT":
        opt_type = "put"
        strike_0dte = round(target1)  # First target
        strike_1dte = round(target2)  # Second target (more OTM)
    else:
        opt_type = "call"
        strike_0dte = round(target1)
        strike_1dte = round(target2)
    
    # Get 0DTE option at TARGET1
    opt_0dte = get_option_ohlc_polygon(symbol, date, strike_0dte, opt_type, dte=0)
    
    if opt_0dte:
        entry = opt_0dte['open']
        high = opt_0dte['high']
        
        # Assume 70% of move captured
        realistic_exit = entry + (high - entry) * 0.70
        pnl = (realistic_exit - entry) / entry * 100 if entry > 0 else 0
        
        result['entry_0dte'] = entry
        result['high_0dte'] = high
        result['pnl_0dte'] = pnl
        result['strike_0dte'] = strike_0dte
        result['ticker_0dte'] = opt_0dte['ticker']
    else:
        result['entry_0dte'] = None
        result['pnl_0dte'] = 0
    
    # Get 1DTE option at TARGET2 (more OTM = bigger potential)
    opt_1dte = get_option_ohlc_polygon(symbol, date, strike_1dte, opt_type, dte=1)
    
    if opt_1dte:
        entry = opt_1dte['open']
        high = opt_1dte['high']
        
        realistic_exit = entry + (high - entry) * 0.60
        pnl = (realistic_exit - entry) / entry * 100 if entry > 0 else 0
        
        result['entry_1dte'] = entry
        result['high_1dte'] = high
        result['pnl_1dte'] = pnl
        result['strike_1dte'] = strike_1dte
        result['ticker_1dte'] = opt_1dte['ticker']
    else:
        result['entry_1dte'] = None
        result['pnl_1dte'] = 0
    
    # Combined P/L (80% 0DTE, 20% 1DTE)
    pnl_0 = result.get('pnl_0dte') or 0
    pnl_1 = result.get('pnl_1dte') or 0
    result['combined_pnl'] = pnl_0 * 0.8 + pnl_1 * 0.2
    
    return result


def analyze_day(symbol: str, date: str, daily_bars: List[dict]) -> Optional[dict]:
    """Analyze a single day for TITAN V3 setup."""
    
    # Get minute bars (returns dict with premarket/regular)
    minute_data = fetch_minute_bars_polygon(symbol, date)
    regular_bars = minute_data['regular']
    premarket_bars = minute_data['premarket']
    
    if len(regular_bars) < 30:
        return None
    
    # Get levels from last 15 days (matching Tradier version)
    date_dt = datetime.strptime(date, '%Y-%m-%d')
    lookback_start = (date_dt - timedelta(days=20)).strftime('%Y-%m-%d')
    lookback_end = (date_dt - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Filter daily bars for lookback period
    lookback_bars = [b for b in daily_bars if lookback_start <= b['date'] <= lookback_end]
    
    if len(lookback_bars) < 5:
        return None
    
    # Get ALL levels (every daily H/L + premarket) - matches Tradier version
    levels = get_all_levels(lookback_bars, premarket_bars)
    
    # Build combined list with type annotation
    all_levels = []
    for l in levels['highs']:
        all_levels.append({'price': l['price'], 'type': 'high'})
    for l in levels['lows']:
        all_levels.append({'price': l['price'], 'type': 'low'})
    
    if not all_levels:
        return None
    
    # Detect clusters (groups levels within 0.5%)
    clusters = detect_clusters(all_levels)
    
    # Only consider 3x+ clusters (significant)
    significant_clusters = [c for c in clusters if c['count'] >= 3]
    
    if not significant_clusters:
        return None
    
    # Find sweep of most significant cluster (using regular hours bars)
    best_setup = None
    for cluster in significant_clusters:
        setup = find_sweep_reclaim(regular_bars, cluster['price'], cluster['level_type'])
        if setup:
            setup['cluster'] = cluster
            best_setup = setup
            break
    
    if not best_setup:
        return None
    
    direction = best_setup['direction']
    entry = best_setup['entry_price']
    
    # Find targets - MUST match level_type for proper magnets
    # LONG → target HIGH clusters (resistance becomes magnet)
    # SHORT → target LOW clusters (support becomes magnet)
    # Prioritize nearest levels (premarket often closest)
    if direction == "SHORT":
        # Target lower support clusters
        targets = sorted([c['price'] for c in clusters 
                         if c['level_type'] == 'low' and c['price'] < entry], reverse=True)
    else:
        # Target higher resistance clusters  
        targets = sorted([c['price'] for c in clusters 
                         if c['level_type'] == 'high' and c['price'] > entry])
    
    # TP1 = nearest reachable target, TP2 = next level for runner
    target1 = targets[0] if len(targets) >= 1 else (entry * 0.99 if direction == "SHORT" else entry * 1.01)
    target2 = targets[1] if len(targets) >= 2 else (target1 * 0.99 if direction == "SHORT" else target1 * 1.01)
    
    # Simulate trade with both targets
    result = simulate_trade(symbol, date, direction, entry, target1, target2, regular_bars, best_setup['reclaim_idx'])
    
    return {
        "date": date,
        "direction": direction,
        "cluster_swept": best_setup['cluster']['price'],
        "cluster_count": best_setup['cluster']['count'],
        "entry_time": best_setup['reclaim_time'],
        "reclaim_mins": best_setup.get('reclaim_mins', 0),
        "entry_price": entry,
        "target1": target1,
        "target2": target2,
        **result
    }


def run_backtest(symbol: str, start: str, end: str):
    """Full backtest with Polygon data."""
    
    print(f"\n{'='*90}")
    print(f"TITAN V3 - POLYGON EDITION")
    print(f"Extended Backtest with 2 Years Options Data")
    print(f"{symbol}: {start} to {end}")
    print(f"{'='*90}\n")
    
    # Fetch all daily bars upfront
    print("Loading daily bars...")
    lookback_start = (datetime.strptime(start, '%Y-%m-%d') - timedelta(days=60)).strftime('%Y-%m-%d')
    daily_bars = fetch_daily_bars_polygon(symbol, lookback_start, end)
    print(f"Loaded {len(daily_bars)} daily bars\n")
    
    start_dt = datetime.strptime(start, '%Y-%m-%d')
    end_dt = datetime.strptime(end, '%Y-%m-%d')
    
    trades = []
    current = start_dt
    
    while current <= end_dt:
        # Skip weekends
        if current.weekday() >= 5:
            current += timedelta(days=1)
            continue
        
        date_str = current.strftime('%Y-%m-%d')
        print(f"{date_str}: ", end="", flush=True)
        
        result = analyze_day(symbol, date_str, daily_bars)
        
        if result and result.get('combined_pnl'):
            trades.append(result)
            reclaim_m = result.get('reclaim_mins', '?')
            pnl_0 = result.get('pnl_0dte') or 0
            pnl_1 = result.get('pnl_1dte') or 0
            combined = result.get('combined_pnl') or 0
            entry_0 = result.get('entry_0dte')
            
            print(f"{result['direction']} {result['cluster_count']}x @ ${result['entry_price']:.2f} (reclaim {reclaim_m}m) | ", end="")
            if entry_0:
                print(f"0DTE ${entry_0:.2f}→{pnl_0:+.0f}% | ", end="")
            else:
                print(f"0DTE N/A | ", end="")
            print(f"Combined: {combined:+.0f}%")
        else:
            print("no setup")
        
        current += timedelta(days=1)
        time.sleep(0.15)  # Rate limit
    
    if not trades:
        print("\nNo trades found.")
        return
    
    # Stats
    print(f"\n{'='*90}")
    print("RESULTS")
    print(f"{'='*90}")
    
    wins = [t for t in trades if t.get('combined_pnl', 0) > 0]
    print(f"Total Trades: {len(trades)}")
    print(f"Winners: {len(wins)} ({len(wins)/len(trades)*100:.1f}%)")
    
    avg_pnl = sum(t.get('combined_pnl', 0) for t in trades) / len(trades)
    print(f"Avg P/L: {avg_pnl:+.1f}%")
    
    # Compounded returns
    balance = 10000
    for t in trades:
        pnl = t.get('combined_pnl', 0) / 100
        balance *= (1 + pnl)
    
    print(f"\n$10,000 → ${balance:,.0f} ({(balance/10000-1)*100:+.1f}%)")
    print(f"{'='*90}\n")


if __name__ == "__main__":
    # Test with 6 months of data
    run_backtest("QQQ", "2025-08-01", "2026-02-13")
