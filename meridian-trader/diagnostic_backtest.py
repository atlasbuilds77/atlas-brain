#!/usr/bin/env python3
"""
DIAGNOSTIC BACKTEST - Full transparency on all 23 variables
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time
import pytz
import json

# ============================================================
# CONFIG
# ============================================================

POLYGON_API_KEY = "h7J74V1cd8_4NQpTxwQpudpqXWaIHMhv"
ET = pytz.timezone('US/Eastern')
POSITION_SIZE = 1000

# ============================================================
# POLYGON DATA FUNCTIONS
# ============================================================

def fetch_minute_bars_polygon(symbol: str, date: str) -> Dict[str, List[dict]]:
    """Fetch 1-minute bars from Polygon."""
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{date}/{date}"
    params = {"apiKey": POLYGON_API_KEY, "limit": 50000}
    
    r = requests.get(url, params=params)
    data = r.json()
    
    if data.get('status') != 'OK' or not data.get('results'):
        return {"premarket": [], "regular": [], "all": []}
    
    premarket = []
    regular = []
    
    for bar in data['results']:
        ts = datetime.fromtimestamp(bar['t'] / 1000, tz=pytz.UTC)
        ts_et = ts.astimezone(ET)
        
        bar_data = {
            'time_et': ts_et.strftime('%H:%M'),
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
    
    return {"premarket": premarket, "regular": regular, "all": premarket + regular}


def fetch_daily_bars_polygon(symbol: str, start: str, end: str) -> List[dict]:
    """Fetch daily bars from Polygon."""
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
    """Get option OHLC from Polygon."""
    trade_date = datetime.strptime(date, '%Y-%m-%d')
    exp_date = trade_date + timedelta(days=dte)
    
    while exp_date.weekday() >= 5:
        exp_date += timedelta(days=1)
    
    exp_str = exp_date.strftime('%y%m%d')
    strike_str = f"{int(strike * 1000):08d}"
    opt_char = 'P' if opt_type == 'put' else 'C'
    
    option_ticker = f"O:{symbol}{exp_str}{opt_char}{strike_str}"
    
    url = f"https://api.polygon.io/v2/aggs/ticker/{option_ticker}/range/1/minute/{date}/{date}"
    params = {"apiKey": POLYGON_API_KEY, "limit": 50000}
    
    r = requests.get(url, params=params)
    data = r.json()
    
    if data.get('status') == 'OK' and data.get('results'):
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
        
        if bars:
            return {
                'open': bars[0]['o'],
                'bars': bars,
                'ticker': option_ticker
            }
    
    return None


# ============================================================
# LEVEL DETECTION
# ============================================================

def get_all_levels(daily_bars: List[dict], pm_bars: List[dict] = None) -> Dict[str, List[dict]]:
    """Get ALL daily highs/lows with dates for lookback tracking."""
    levels = {'highs': [], 'lows': []}
    
    for bar in daily_bars:
        levels['highs'].append({'price': bar['h'], 'type': 'high', 'date': bar['date']})
        levels['lows'].append({'price': bar['l'], 'type': 'low', 'date': bar['date']})
    
    if pm_bars:
        pm_high = max(b['h'] for b in pm_bars)
        pm_low = min(b['l'] for b in pm_bars)
        levels['highs'].append({'price': pm_high, 'type': 'high', 'date': 'premarket'})
        levels['lows'].append({'price': pm_low, 'type': 'low', 'date': 'premarket'})
    
    return levels


def detect_clusters(levels: List[dict], threshold: float = 0.005) -> List[dict]:
    """Group levels within threshold and track source dates."""
    if not levels:
        return []
    
    sorted_levels = sorted(levels, key=lambda x: x['price'])
    clusters = []
    current_cluster = [sorted_levels[0]]
    
    for level in sorted_levels[1:]:
        avg = sum(l['price'] for l in current_cluster) / len(current_cluster)
        if abs(level['price'] - avg) / avg <= threshold:
            current_cluster.append(level)
        else:
            avg_price = sum(l['price'] for l in current_cluster) / len(current_cluster)
            clusters.append({
                'price': avg_price,
                'count': len(current_cluster),
                'level_type': current_cluster[0].get('type', 'unknown'),
                'dates': [l.get('date', 'unknown') for l in current_cluster]
            })
            current_cluster = [level]
    
    avg_price = sum(l['price'] for l in current_cluster) / len(current_cluster)
    clusters.append({
        'price': avg_price,
        'count': len(current_cluster),
        'level_type': current_cluster[0].get('type', 'unknown'),
        'dates': [l.get('date', 'unknown') for l in current_cluster]
    })
    
    return sorted(clusters, key=lambda x: x['count'], reverse=True)


# ============================================================
# SWEEP DETECTION
# ============================================================

def find_sweep_reclaim(bars: List[dict], level: float, level_type: str, 
                       start_idx: int = 0) -> Optional[dict]:
    """Find sweep and reclaim within 5 minutes."""
    MAX_RECLAIM_BARS = 5
    
    for i in range(start_idx, len(bars)):
        bar = bars[i]
        
        if level_type == "high" and bar['h'] > level:
            for j in range(i + 1, min(i + 1 + MAX_RECLAIM_BARS, len(bars))):
                if bars[j]['c'] < level:
                    bounce_low = min(bars[k]['l'] for k in range(i, j + 1))
                    return {
                        "sweep_idx": i,
                        "sweep_time": bar['time_et'],
                        "sweep_price": bar['h'],
                        "reclaim_idx": j,
                        "reclaim_time": bars[j]['time_et'],
                        "reclaim_mins": j - i,
                        "bounce_price": bounce_low,
                        "entry_price": bars[j]['c'],
                        "direction": "SHORT"
                    }
            return None
        
        elif level_type == "low" and bar['l'] < level:
            for j in range(i + 1, min(i + 1 + MAX_RECLAIM_BARS, len(bars))):
                if bars[j]['c'] > level:
                    bounce_low = min(bars[k]['l'] for k in range(i, j + 1))
                    return {
                        "sweep_idx": i,
                        "sweep_time": bar['time_et'],
                        "sweep_price": bar['l'],
                        "reclaim_idx": j,
                        "reclaim_time": bars[j]['time_et'],
                        "reclaim_mins": j - i,
                        "bounce_price": bounce_low,
                        "entry_price": bars[j]['c'],
                        "direction": "LONG"
                    }
            return None
    
    return None


def check_multiple_sweeps(bars: List[dict], level: float, level_type: str, 
                          window_bars: int = 15) -> bool:
    """Check if level was swept multiple times."""
    sweep_count = 0
    
    for i, bar in enumerate(bars[:window_bars]):
        if level_type == "high" and bar['h'] > level:
            sweep_count += 1
        elif level_type == "low" and bar['l'] < level:
            sweep_count += 1
    
    return sweep_count >= 2


# ============================================================
# DIAGNOSTIC TRADE SIMULATION
# ============================================================

def simulate_trade_diagnostic(symbol: str, date: str, direction: str, 
                               entry_price: float, target1: float, target2: float,
                               target1_cluster: dict, target2_cluster: dict,
                               entry_time: datetime, regular_bars: List[dict],
                               entry_idx: int) -> dict:
    """Full diagnostic trade simulation with all 23 variables."""
    
    # Strike selection
    if direction == "SHORT":
        opt_type = "put"
        strike_0dte = round(target1)
        strike_1dte = round(target2)
    else:
        opt_type = "call"
        strike_0dte = round(target1)
        strike_1dte = round(target2)
    
    # Get option data
    opt_0dte = get_option_ohlc_polygon(symbol, date, strike_0dte, opt_type, dte=0)
    opt_1dte = get_option_ohlc_polygon(symbol, date, strike_1dte, opt_type, dte=1)
    
    result = {
        # Option details (10-13)
        'strike_0dte': strike_0dte,
        'strike_1dte': strike_1dte,
        'option_0dte_entry': None,
        'option_1dte_entry': None,
        'option_0dte_ticker': None,
        'option_1dte_ticker': None,
        
        # Target details (6-9)
        'target1_price': target1,
        'target1_cluster_count': target1_cluster.get('count', 0),
        'target1_cluster_dates': target1_cluster.get('dates', []),
        'target2_price': target2,
        'target2_cluster_count': target2_cluster.get('count', 0),
        'target2_cluster_dates': target2_cluster.get('dates', []),
        'distance_to_t1_dollars': abs(target1 - entry_price),
        'distance_to_t1_pct': abs(target1 - entry_price) / entry_price * 100,
        'distance_to_t2_dollars': abs(target2 - entry_price),
        'distance_to_t2_pct': abs(target2 - entry_price) / entry_price * 100,
        
        # Price action (14-17)
        'underlying_hit_t1': False,
        'underlying_t1_time': None,
        'underlying_hit_t2': False,
        'underlying_t2_time': None,
        'underlying_high_after_entry': None,
        'underlying_low_after_entry': None,
        
        # Exit details (18-23)
        'option_0dte_exit': None,
        'pnl_0dte': 0,
        'option_1dte_exit': None,
        'pnl_1dte': 0,
        'exit_reason': None,
        'max_gain_before_exit': 0
    }
    
    # Track underlying high/low after entry
    underlying_high = entry_price
    underlying_low = entry_price
    
    for i in range(entry_idx, len(regular_bars)):
        bar = regular_bars[i]
        underlying_high = max(underlying_high, bar['h'])
        underlying_low = min(underlying_low, bar['l'])
        
        # Check T1 hit
        if not result['underlying_hit_t1']:
            if (direction == "LONG" and bar['h'] >= target1) or \
               (direction == "SHORT" and bar['l'] <= target1):
                result['underlying_hit_t1'] = True
                result['underlying_t1_time'] = bar['time_et']
        
        # Check T2 hit
        if not result['underlying_hit_t2']:
            if (direction == "LONG" and bar['h'] >= target2) or \
               (direction == "SHORT" and bar['l'] <= target2):
                result['underlying_hit_t2'] = True
                result['underlying_t2_time'] = bar['time_et']
    
    result['underlying_high_after_entry'] = underlying_high
    result['underlying_low_after_entry'] = underlying_low
    
    # If no option data, return early
    if not opt_0dte or not opt_0dte.get('bars'):
        result['exit_reason'] = 'no_option_data'
        return result
    
    result['option_0dte_entry'] = opt_0dte['open']
    result['option_0dte_ticker'] = opt_0dte['ticker']
    
    if opt_1dte and opt_1dte.get('bars'):
        result['option_1dte_entry'] = opt_1dte['open']
        result['option_1dte_ticker'] = opt_1dte['ticker']
    
    # Simulate option price movement
    option_entry = opt_0dte['open']
    option_bars = opt_0dte['bars']
    
    entry_time_str = entry_time.strftime('%H:%M') if hasattr(entry_time, 'strftime') else entry_time
    opt_start_idx = 0
    for i, ob in enumerate(option_bars):
        if ob['time'] >= entry_time_str:
            opt_start_idx = i
            break
    
    max_gain_pct = 0
    trailing_stop_pct = None
    position_open = True
    exit_price = option_entry
    
    for i in range(opt_start_idx, len(option_bars)):
        opt_bar = option_bars[i]
        
        current_high = opt_bar['h']
        current_low = opt_bar['l']
        current_close = opt_bar['c']
        
        high_gain = (current_high - option_entry) / option_entry * 100
        low_gain = (current_low - option_entry) / option_entry * 100
        
        if high_gain > max_gain_pct:
            max_gain_pct = high_gain
            result['max_gain_before_exit'] = max_gain_pct
        
        # -80% max loss
        if low_gain <= -80:
            result['exit_reason'] = 'max_loss_80'
            exit_price = option_entry * 0.2
            position_open = False
            break
        
        # Trailing stop
        if max_gain_pct >= 30 and trailing_stop_pct is None:
            trailing_stop_pct = 15
        if max_gain_pct >= 50:
            trailing_stop_pct = 30
        
        if trailing_stop_pct is not None and low_gain <= trailing_stop_pct:
            result['exit_reason'] = f'trailing_stop_{trailing_stop_pct}pct'
            exit_price = option_entry * (1 + trailing_stop_pct / 100)
            position_open = False
            break
    
    if position_open:
        exit_price = option_bars[-1]['c'] if option_bars else option_entry
        result['exit_reason'] = 'eod'
    
    result['option_0dte_exit'] = exit_price
    
    # Calculate P&L
    final_gain = (exit_price - option_entry) / option_entry
    result['pnl_0dte'] = POSITION_SIZE * final_gain
    
    return result


# ============================================================
# MAIN DIAGNOSTIC ANALYSIS
# ============================================================

def analyze_day_diagnostic(symbol: str, date: str, daily_bars: List[dict], trade_date: str) -> Optional[dict]:
    """Full diagnostic analysis for a single day."""
    
    minute_data = fetch_minute_bars_polygon(symbol, date)
    regular_bars = minute_data['regular']
    premarket_bars = minute_data['premarket']
    
    if len(regular_bars) < 30:
        return None
    
    # Calculate lookback
    date_dt = datetime.strptime(date, '%Y-%m-%d')
    lookback_start = (date_dt - timedelta(days=20)).strftime('%Y-%m-%d')
    lookback_end = (date_dt - timedelta(days=1)).strftime('%Y-%m-%d')
    
    lookback_bars = [b for b in daily_bars if lookback_start <= b['date'] <= lookback_end]
    
    if len(lookback_bars) < 5:
        return None
    
    # Get all levels
    levels = get_all_levels(lookback_bars, premarket_bars)
    
    all_levels = []
    for l in levels['highs']:
        all_levels.append({'price': l['price'], 'type': 'high', 'date': l.get('date', 'unknown')})
    for l in levels['lows']:
        all_levels.append({'price': l['price'], 'type': 'low', 'date': l.get('date', 'unknown')})
    
    if not all_levels:
        return None
    
    # Detect clusters
    clusters = detect_clusters(all_levels)
    
    # Only 3x+ clusters
    significant_clusters = [c for c in clusters if c['count'] >= 3]
    
    if not significant_clusters:
        return None
    
    # Find first valid sweep/reclaim
    best_setup = None
    for cluster in significant_clusters:
        if check_multiple_sweeps(regular_bars, cluster['price'], cluster['level_type']):
            continue
        
        setup = find_sweep_reclaim(regular_bars, cluster['price'], cluster['level_type'])
        if setup:
            setup['cluster'] = cluster
            best_setup = setup
            break
    
    if not best_setup:
        return None
    
    direction = best_setup['direction']
    entry = best_setup['bounce_price']
    entry_idx = best_setup['reclaim_idx']
    entry_time = regular_bars[entry_idx]['dt']
    
    # Find targets WITH cluster info
    if direction == "SHORT":
        target_clusters = [c for c in clusters 
                          if c['level_type'] == 'low' and c['price'] < entry]
        target_clusters = sorted(target_clusters, key=lambda x: x['price'], reverse=True)
    else:
        target_clusters = [c for c in clusters 
                          if c['level_type'] == 'high' and c['price'] > entry]
        target_clusters = sorted(target_clusters, key=lambda x: x['price'])
    
    target1_cluster = target_clusters[0] if len(target_clusters) >= 1 else {'price': entry * (0.99 if direction == "SHORT" else 1.01), 'count': 0, 'dates': []}
    target2_cluster = target_clusters[1] if len(target_clusters) >= 2 else {'price': target1_cluster['price'] * (0.99 if direction == "SHORT" else 1.01), 'count': 0, 'dates': []}
    
    target1 = target1_cluster['price']
    target2 = target2_cluster['price']
    
    # Calculate cluster lookback
    swept_dates = best_setup['cluster'].get('dates', [])
    days_back = []
    for d in swept_dates:
        if d != 'premarket' and d != 'unknown':
            cluster_dt = datetime.strptime(d, '%Y-%m-%d')
            days_ago = (date_dt - cluster_dt).days
            days_back.append(days_ago)
    
    avg_days_back = sum(days_back) / len(days_back) if days_back else 0
    
    # Run diagnostic simulation
    result = simulate_trade_diagnostic(symbol, date, direction, entry, target1, target2,
                                       target1_cluster, target2_cluster,
                                       entry_time, regular_bars, entry_idx)
    
    return {
        "symbol": symbol,
        "date": date,
        "direction": direction,
        
        # Setup details (1-5)
        "cluster_swept_price": best_setup['cluster']['price'],
        "cluster_significance": f"{best_setup['cluster']['count']}x",
        "cluster_lookback_days": f"{avg_days_back:.1f} days" if days_back else "premarket",
        "cluster_dates": swept_dates,
        "sweep_time": best_setup['sweep_time'],
        "reclaim_time": best_setup['reclaim_time'],
        "entry_price": entry,
        
        **result
    }


def run_diagnostic_backtest(symbols: List[str], start: str, end: str, output_file: str):
    """Run full diagnostic backtest and output to markdown."""
    
    print(f"\nDIAGNOSTIC BACKTEST - {', '.join(symbols)}: {start} to {end}\n")
    
    all_trades = []
    
    for symbol in symbols:
        print(f"\n{symbol}:")
        
        lookback_start = (datetime.strptime(start, '%Y-%m-%d') - timedelta(days=30)).strftime('%Y-%m-%d')
        daily_bars = fetch_daily_bars_polygon(symbol, lookback_start, end)
        
        start_dt = datetime.strptime(start, '%Y-%m-%d')
        end_dt = datetime.strptime(end, '%Y-%m-%d')
        
        current = start_dt
        while current <= end_dt:
            if current.weekday() >= 5:
                current += timedelta(days=1)
                continue
            
            date_str = current.strftime('%Y-%m-%d')
            print(f"  {date_str}...", end="", flush=True)
            
            result = analyze_day_diagnostic(symbol, date_str, daily_bars, date_str)
            
            if result:
                all_trades.append(result)
                print(f" ✓ {result['direction']} {result['cluster_significance']}")
            else:
                print(" no setup")
            
            current += timedelta(days=1)
            time.sleep(0.15)
    
    # Generate markdown report
    print(f"\nGenerating diagnostic report: {output_file}")
    
    with open(output_file, 'w') as f:
        f.write("# TITAN V3 DIAGNOSTIC REPORT\n")
        f.write(f"## Period: {start} to {end}\n")
        f.write(f"## Symbols: {', '.join(symbols)}\n\n")
        f.write("---\n\n")
        
        if not all_trades:
            f.write("**NO TRADES FOUND**\n")
            return
        
        for idx, trade in enumerate(all_trades, 1):
            f.write(f"## TRADE {idx}: {trade['symbol']} {trade['date']} ({trade['direction']})\n\n")
            
            f.write("### SETUP DETAILS\n\n")
            f.write(f"1. **Cluster swept:** ${trade['cluster_swept_price']:.2f} ({trade['cluster_significance']})\n")
            f.write(f"2. **Cluster lookback:** {trade['cluster_lookback_days']}\n")
            f.write(f"   - Dates: {', '.join(str(d) for d in trade['cluster_dates'][:5])}\n")
            f.write(f"3. **Sweep time:** {trade['sweep_time']}\n")
            f.write(f"4. **Reclaim time:** {trade['reclaim_time']}\n")
            f.write(f"5. **Entry price (bounce):** ${trade['entry_price']:.2f}\n")
            f.write(f"6. **Direction:** {trade['direction']}\n\n")
            
            f.write("### TARGET SELECTION\n\n")
            f.write(f"7. **Target 1 (T1):** ${trade['target1_price']:.2f} (from {trade['target1_cluster_count']}x cluster)\n")
            f.write(f"   - Cluster dates: {', '.join(str(d) for d in trade.get('target1_cluster_dates', [])[:3])}\n")
            f.write(f"8. **Target 2 (T2):** ${trade['target2_price']:.2f} (from {trade['target2_cluster_count']}x cluster)\n")
            f.write(f"   - Cluster dates: {', '.join(str(d) for d in trade.get('target2_cluster_dates', [])[:3])}\n")
            f.write(f"9. **Distance to T1:** ${trade['distance_to_t1_dollars']:.2f} ({trade['distance_to_t1_pct']:.2f}%)\n")
            f.write(f"10. **Distance to T2:** ${trade['distance_to_t2_dollars']:.2f} ({trade['distance_to_t2_pct']:.2f}%)\n\n")
            
            f.write("### OPTION DETAILS\n\n")
            f.write(f"11. **0DTE strike:** ${trade['strike_0dte']:.0f}\n")
            opt_0dte_entry = f"${trade['option_0dte_entry']:.2f}" if trade['option_0dte_entry'] else 'N/A'
            f.write(f"12. **0DTE entry price:** {opt_0dte_entry}\n")
            f.write(f"    - Ticker: {trade.get('option_0dte_ticker', 'N/A')}\n")
            f.write(f"13. **1DTE strike:** ${trade['strike_1dte']:.0f}\n")
            opt_1dte_entry = f"${trade['option_1dte_entry']:.2f}" if trade['option_1dte_entry'] else 'N/A'
            f.write(f"14. **1DTE entry price:** {opt_1dte_entry}\n")
            f.write(f"    - Ticker: {trade.get('option_1dte_ticker', 'N/A')}\n\n")
            
            f.write("### PRICE ACTION\n\n")
            f.write(f"15. **Underlying hit T1?** {'YES at ' + trade['underlying_t1_time'] if trade['underlying_hit_t1'] else 'NO'}\n")
            f.write(f"16. **Underlying hit T2?** {'YES at ' + trade['underlying_t2_time'] if trade['underlying_hit_t2'] else 'NO'}\n")
            f.write(f"17. **Underlying high after entry:** ${trade['underlying_high_after_entry']:.2f}\n")
            
            if trade['direction'] == 'LONG':
                distance_to_t1 = trade['underlying_high_after_entry'] - trade['entry_price']
                pct_to_t1 = distance_to_t1 / (trade['target1_price'] - trade['entry_price']) * 100 if trade['target1_price'] > trade['entry_price'] else 0
                f.write(f"    - Moved ${distance_to_t1:.2f} toward T1 ({pct_to_t1:.1f}% of the way)\n")
            
            f.write(f"18. **Underlying low after entry:** ${trade['underlying_low_after_entry']:.2f}\n")
            
            if trade['direction'] == 'SHORT':
                distance_to_t1 = trade['entry_price'] - trade['underlying_low_after_entry']
                pct_to_t1 = distance_to_t1 / (trade['entry_price'] - trade['target1_price']) * 100 if trade['entry_price'] > trade['target1_price'] else 0
                f.write(f"    - Moved ${distance_to_t1:.2f} toward T1 ({pct_to_t1:.1f}% of the way)\n")
            
            f.write("\n")
            
            f.write("### EXIT DETAILS\n\n")
            opt_0dte_exit = f"${trade['option_0dte_exit']:.2f}" if trade['option_0dte_exit'] else 'N/A'
            f.write(f"19. **0DTE exit price:** {opt_0dte_exit}\n")
            f.write(f"20. **0DTE P&L:** ${trade['pnl_0dte']:+.2f}\n")
            opt_1dte_exit = f"${trade['option_1dte_exit']:.2f}" if trade['option_1dte_exit'] else 'N/A'
            f.write(f"21. **1DTE exit price:** {opt_1dte_exit}\n")
            f.write(f"22. **1DTE P&L:** ${trade['pnl_1dte']:+.2f}\n")
            f.write(f"23. **Exit reason:** {trade['exit_reason']}\n")
            f.write(f"24. **Max gain reached before exit:** {trade['max_gain_before_exit']:.1f}%\n\n")
            
            f.write("---\n\n")
        
        # Summary section
        f.write("## SUMMARY: What's Broken?\n\n")
        
        total_trades = len(all_trades)
        hit_t1 = sum(1 for t in all_trades if t['underlying_hit_t1'])
        hit_t2 = sum(1 for t in all_trades if t['underlying_hit_t2'])
        max_loss = sum(1 for t in all_trades if t['exit_reason'] == 'max_loss_80')
        
        f.write(f"### Key Findings\n\n")
        f.write(f"- **Total trades:** {total_trades}\n")
        f.write(f"- **Underlying hit T1:** {hit_t1}/{total_trades} ({hit_t1/total_trades*100:.0f}%)\n")
        f.write(f"- **Underlying hit T2:** {hit_t2}/{total_trades} ({hit_t2/total_trades*100:.0f}%)\n")
        f.write(f"- **Hit -80% max loss:** {max_loss}/{total_trades} ({max_loss/total_trades*100:.0f}%)\n\n")
        
        f.write("### Diagnosis\n\n")
        
        if max_loss == total_trades:
            f.write("🚨 **CRITICAL: ALL TRADES HIT -80% MAX LOSS**\n\n")
            f.write("This means:\n")
            f.write("1. Price immediately reversed against us after entry\n")
            f.write("2. Entry timing is too early (before true reversal)\n")
            f.write("3. Bounce price entry may be catching falling knives\n\n")
        
        if hit_t1 == 0:
            f.write("🚨 **PROBLEM: ZERO TRADES HIT TARGET 1**\n\n")
            f.write("Check:\n")
            f.write("- Are targets too far from entry?\n")
            f.write("- Is price moving in our direction at all?\n")
            f.write("- Look at 'how close to T1' metrics above\n\n")
        
        avg_t1_distance = sum(t['distance_to_t1_pct'] for t in all_trades) / total_trades
        f.write(f"- **Average distance to T1:** {avg_t1_distance:.2f}%\n")
        f.write(f"  - If >5%, targets may be too ambitious for 0DTE\n\n")
        
        avg_lookback = []
        for t in all_trades:
            lb = t.get('cluster_lookback_days', '0 days')
            if 'days' in str(lb):
                try:
                    days = float(str(lb).split()[0])
                    avg_lookback.append(days)
                except:
                    pass
        
        if avg_lookback:
            f.write(f"- **Average cluster lookback:** {sum(avg_lookback)/len(avg_lookback):.1f} days\n")
            f.write(f"  - If >10 days, levels may be stale\n\n")
        
        f.write("### Recommended Fixes\n\n")
        f.write("1. **Entry timing:** Wait for confirmation bar after reclaim (one more green/red candle)\n")
        f.write("2. **Tighter stops:** -50% instead of -80%\n")
        f.write("3. **Target validation:** Only use clusters from last 5 days\n")
        f.write("4. **Volume confirmation:** Add volume spike requirement on sweep\n\n")
    
    print(f"✓ Report saved to {output_file}")


if __name__ == "__main__":
    run_diagnostic_backtest(
        symbols=["QQQ", "SPY"],
        start="2026-02-12",
        end="2026-02-14",
        output_file="/Users/atlasbuilds/clawd/titan-trader/DIAGNOSTIC-FEB12-14.md"
    )
