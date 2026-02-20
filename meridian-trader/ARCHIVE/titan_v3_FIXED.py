#!/usr/bin/env python3
"""
TITAN V3 FIXED - Entry Timing + Volume Confirmation
====================================================
CHANGES FROM V3:
1. Entry AFTER confirmation bar (not at bounce)
2. Volume confirmation (sweep volume > 2x avg)
3. Tighter stop (-50% max, not -80%)
4. Entry at CLOSE of confirmation bar
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
POSITION_SIZE = 1000  # $1000 per trade

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
        
        # Premarket: 4:00 - 9:30 ET
        if (ts_et.hour >= 4 and ts_et.hour < 9) or (ts_et.hour == 9 and ts_et.minute < 30):
            premarket.append(bar_data)
        # Regular hours: 9:30 - 16:00 ET
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
        # Return all minute bars for proper simulation
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
    """Get ALL daily highs/lows as potential levels."""
    levels = {'highs': [], 'lows': []}
    
    for bar in daily_bars:
        levels['highs'].append({'price': bar['h'], 'type': 'high'})
        levels['lows'].append({'price': bar['l'], 'type': 'low'})
    
    if pm_bars:
        pm_high = max(b['h'] for b in pm_bars)
        pm_low = min(b['l'] for b in pm_bars)
        levels['highs'].append({'price': pm_high, 'type': 'high'})
        levels['lows'].append({'price': pm_low, 'type': 'low'})
    
    return levels


def detect_clusters(levels: List[dict], threshold: float = 0.005) -> List[dict]:
    """Group levels within threshold."""
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
                'level_type': current_cluster[0].get('type', 'unknown')
            })
            current_cluster = [level]
    
    avg_price = sum(l['price'] for l in current_cluster) / len(current_cluster)
    clusters.append({
        'price': avg_price,
        'count': len(current_cluster),
        'level_type': current_cluster[0].get('type', 'unknown')
    })
    
    return sorted(clusters, key=lambda x: x['count'], reverse=True)


# ============================================================
# VOLUME HELPER
# ============================================================

def get_avg_volume(bars: List[dict], idx: int, lookback: int = 20) -> float:
    """Get average volume over last N bars before idx."""
    start = max(0, idx - lookback)
    vols = [bars[i]['v'] for i in range(start, idx)]
    return sum(vols) / len(vols) if vols else 0


# ============================================================
# SWEEP DETECTION WITH VOLUME CONFIRMATION + ENTRY TIMING FIX
# ============================================================

def find_sweep_reclaim(bars: List[dict], level: float, level_type: str, 
                       start_idx: int = 0) -> Optional[dict]:
    """
    FIXED VERSION:
    1. Find sweep with VOLUME CONFIRMATION (>2x avg)
    2. Wait for reclaim bar
    3. Wait 1-2 bars for CONFIRMATION bar that closes in direction
    4. Entry = CLOSE of confirmation bar
    """
    MAX_RECLAIM_BARS = 5
    MAX_CONFIRMATION_WAIT = 2
    
    for i in range(start_idx, len(bars)):
        bar = bars[i]
        
        # VOLUME CHECK - sweep must have high volume
        avg_vol = get_avg_volume(bars, i, lookback=20)
        if avg_vol == 0 or bar['v'] < avg_vol * 2:
            continue  # Skip weak sweeps
        
        if level_type == "high" and bar['h'] > level:
            # Found sweep above high with volume - look for reclaim
            for j in range(i + 1, min(i + 1 + MAX_RECLAIM_BARS, len(bars))):
                reclaim_bar = bars[j]
                
                # Reclaim = close back below level
                if reclaim_bar['c'] < level:
                    # Now wait for CONFIRMATION bar (1-2 bars after)
                    for k in range(j + 1, min(j + 1 + MAX_CONFIRMATION_WAIT, len(bars))):
                        confirm_bar = bars[k]
                        
                        # CONFIRMATION = bar that closes BELOW reclaim level (continuing SHORT)
                        if confirm_bar['c'] < level:
                            return {
                                "sweep_idx": i,
                                "sweep_time": bar['time_et'],
                                "sweep_price": bar['h'],
                                "sweep_volume": bar['v'],
                                "avg_volume": avg_vol,
                                "volume_ratio": bar['v'] / avg_vol,
                                "reclaim_idx": j,
                                "reclaim_time": reclaim_bar['time_et'],
                                "reclaim_mins": j - i,
                                "confirm_idx": k,
                                "confirm_time": confirm_bar['time_et'],
                                "confirm_bars_after": k - j,
                                "entry_price": confirm_bar['c'],  # CLOSE of confirmation bar
                                "direction": "SHORT"
                            }
                    # If no confirmation within 2 bars, skip this sweep
                    break
            
        elif level_type == "low" and bar['l'] < level:
            # Found sweep below low with volume - look for reclaim
            for j in range(i + 1, min(i + 1 + MAX_RECLAIM_BARS, len(bars))):
                reclaim_bar = bars[j]
                
                # Reclaim = close back above level
                if reclaim_bar['c'] > level:
                    # Now wait for CONFIRMATION bar (1-2 bars after)
                    for k in range(j + 1, min(j + 1 + MAX_CONFIRMATION_WAIT, len(bars))):
                        confirm_bar = bars[k]
                        
                        # CONFIRMATION = bar that closes ABOVE reclaim level (continuing LONG)
                        if confirm_bar['c'] > level:
                            return {
                                "sweep_idx": i,
                                "sweep_time": bar['time_et'],
                                "sweep_price": bar['l'],
                                "sweep_volume": bar['v'],
                                "avg_volume": avg_vol,
                                "volume_ratio": bar['v'] / avg_vol,
                                "reclaim_idx": j,
                                "reclaim_time": reclaim_bar['time_et'],
                                "reclaim_mins": j - i,
                                "confirm_idx": k,
                                "confirm_time": confirm_bar['time_et'],
                                "confirm_bars_after": k - j,
                                "entry_price": confirm_bar['c'],  # CLOSE of confirmation bar
                                "direction": "LONG"
                            }
                    # If no confirmation within 2 bars, skip this sweep
                    break
    
    return None


def check_multiple_sweeps(bars: List[dict], level: float, level_type: str, 
                          window_bars: int = 15) -> bool:
    """Check if level was swept multiple times in window (absorption = skip)."""
    sweep_count = 0
    
    for i, bar in enumerate(bars[:window_bars]):
        if level_type == "high" and bar['h'] > level:
            sweep_count += 1
        elif level_type == "low" and bar['l'] < level:
            sweep_count += 1
    
    return sweep_count >= 2  # 2+ sweeps = absorption


# ============================================================
# TRADE SIMULATION WITH -50% MAX LOSS (TIGHTER)
# ============================================================

def simulate_trade_real(symbol: str, date: str, direction: str, 
                        entry_price: float, target1: float, target2: float,
                        entry_time: datetime, regular_bars: List[dict],
                        entry_idx: int) -> dict:
    """
    Simulate trade with TIGHTER stop:
    1. Track option price minute-by-minute
    2. Apply trailing stop (+30% → trail at +15%)
    3. Max -50% loss (WAS -80%)
    4. Time-based scaling at Phase 2
    """
    
    # Determine option type and strikes
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
    
    result = {
        'entry_price': entry_price,
        'target1': target1,
        'target2': target2,
        'direction': direction,
        'phase2_hit': False,
        'phase2_time': None,
        'phase2_elapsed_mins': None,
        'phase3_hit': False,
        'stopped': False,
        'trailing_stopped': False,
        'max_option_gain': 0,
        'exit_reason': None,
        'pnl_0dte': 0,
        'combined_pnl': 0
    }
    
    if not opt_0dte or not opt_0dte.get('bars'):
        result['exit_reason'] = 'no_option_data'
        return result
    
    option_entry = opt_0dte['open']
    option_bars = opt_0dte['bars']
    result['option_entry'] = option_entry
    result['option_ticker'] = opt_0dte['ticker']
    
    # Find option bar index closest to our entry time
    entry_time_str = entry_time.strftime('%H:%M') if hasattr(entry_time, 'strftime') else entry_time
    opt_start_idx = 0
    for i, ob in enumerate(option_bars):
        if ob['time'] >= entry_time_str:
            opt_start_idx = i
            break
    
    # Track position through the day
    max_gain_pct = 0
    trailing_stop_pct = None
    position_open = True
    exit_price = option_entry
    
    for i in range(opt_start_idx, len(option_bars)):
        opt_bar = option_bars[i]
        
        # Calculate current P&L
        current_high = opt_bar['h']
        current_low = opt_bar['l']
        current_close = opt_bar['c']
        
        high_gain = (current_high - option_entry) / option_entry * 100
        low_gain = (current_low - option_entry) / option_entry * 100
        
        # Update max gain
        if high_gain > max_gain_pct:
            max_gain_pct = high_gain
            result['max_option_gain'] = max_gain_pct
        
        # TIGHTER STOP: -50% max loss (was -80%)
        if low_gain <= -50:
            result['stopped'] = True
            result['exit_reason'] = 'max_loss_50'
            exit_price = option_entry * 0.5  # -50%
            position_open = False
            break
        
        # Update trailing stop
        if max_gain_pct >= 30 and trailing_stop_pct is None:
            trailing_stop_pct = 15  # Trail at +15%
        if max_gain_pct >= 50:
            trailing_stop_pct = 30  # Trail at +30%
        
        # Check trailing stop hit
        if trailing_stop_pct is not None:
            if low_gain <= trailing_stop_pct:
                result['trailing_stopped'] = True
                result['exit_reason'] = f'trailing_stop_{trailing_stop_pct}pct'
                exit_price = option_entry * (1 + trailing_stop_pct / 100)
                position_open = False
                break
        
        # Check if underlying hit target1 (Phase 2)
        if i + opt_start_idx < len(regular_bars):
            underlying_bar = regular_bars[min(entry_idx + (i - opt_start_idx), len(regular_bars) - 1)]
            
            if not result['phase2_hit']:
                hit_target1 = (direction == "LONG" and underlying_bar['h'] >= target1) or \
                              (direction == "SHORT" and underlying_bar['l'] <= target1)
                
                if hit_target1:
                    result['phase2_hit'] = True
                    result['phase2_time'] = opt_bar['time']
                    elapsed = i - opt_start_idx
                    result['phase2_elapsed_mins'] = elapsed
                    result['phase2_option_price'] = current_high
            
            if result['phase2_hit'] and not result['phase3_hit']:
                hit_target2 = (direction == "LONG" and underlying_bar['h'] >= target2) or \
                              (direction == "SHORT" and underlying_bar['l'] <= target2)
                
                if hit_target2:
                    result['phase3_hit'] = True
                    result['phase3_time'] = opt_bar['time']
                    result['phase3_option_price'] = current_high
                    result['exit_reason'] = 'target2_hit'
                    exit_price = current_high
                    position_open = False
                    break
    
    # If still open at end of day
    if position_open:
        exit_price = option_bars[-1]['c'] if option_bars else option_entry
        result['exit_reason'] = 'eod'
    
    result['option_exit'] = exit_price
    
    # Calculate P&L with time-based scaling
    if result['phase2_hit'] and result['phase2_elapsed_mins'] is not None:
        elapsed = result['phase2_elapsed_mins']
        if elapsed < 60:  # <1 hour: sell 25%, ride 75%
            phase2_scale = 0.25
            phase3_scale = 0.75
        else:  # >=1 hour: sell 50%, ride 50%
            phase2_scale = 0.50
            phase3_scale = 0.50
        
        result['scale_rule'] = f"{'<1hr' if elapsed < 60 else '>=1hr'}: {int(phase2_scale*100)}/{int(phase3_scale*100)}"
        
        # Phase 2 P&L
        if result.get('phase2_option_price'):
            phase2_gain = (result['phase2_option_price'] - option_entry) / option_entry
            result['phase2_pnl'] = POSITION_SIZE * phase2_scale * phase2_gain
        
        # Phase 3 P&L (or remaining)
        final_gain = (exit_price - option_entry) / option_entry
        result['phase3_pnl'] = POSITION_SIZE * phase3_scale * final_gain
        
        result['pnl_0dte'] = result.get('phase2_pnl', 0) + result.get('phase3_pnl', 0)
    else:
        # No phase 2 hit - full position P&L
        final_gain = (exit_price - option_entry) / option_entry
        result['pnl_0dte'] = POSITION_SIZE * final_gain
    
    result['pnl_pct'] = (exit_price - option_entry) / option_entry * 100
    result['combined_pnl'] = result['pnl_0dte']
    
    return result


# ============================================================
# MAIN ANALYSIS
# ============================================================

def analyze_day(symbol: str, date: str, daily_bars: List[dict]) -> Optional[dict]:
    """Analyze a single day for TITAN V3 FIXED setup."""
    
    minute_data = fetch_minute_bars_polygon(symbol, date)
    regular_bars = minute_data['regular']
    premarket_bars = minute_data['premarket']
    
    if len(regular_bars) < 30:
        return None
    
    # Get levels from last 15 days
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
        all_levels.append({'price': l['price'], 'type': 'high'})
    for l in levels['lows']:
        all_levels.append({'price': l['price'], 'type': 'low'})
    
    if not all_levels:
        return None
    
    # Detect clusters
    clusters = detect_clusters(all_levels)
    
    # Only 3x+ clusters (significant)
    significant_clusters = [c for c in clusters if c['count'] >= 3]
    
    if not significant_clusters:
        return None
    
    # Find first valid sweep/reclaim with volume + confirmation
    best_setup = None
    for cluster in significant_clusters:
        # Check for multiple sweeps (absorption filter)
        if check_multiple_sweeps(regular_bars, cluster['price'], cluster['level_type']):
            continue  # Skip - absorption, not rejection
        
        setup = find_sweep_reclaim(regular_bars, cluster['price'], cluster['level_type'])
        if setup:
            setup['cluster'] = cluster
            best_setup = setup
            break
    
    if not best_setup:
        return None
    
    direction = best_setup['direction']
    entry = best_setup['entry_price']  # Now = CLOSE of confirmation bar
    entry_idx = best_setup['confirm_idx']  # Entry at confirmation bar
    entry_time = regular_bars[entry_idx]['dt']
    
    # Find targets
    if direction == "SHORT":
        targets = sorted([c['price'] for c in clusters 
                         if c['level_type'] == 'low' and c['price'] < entry], reverse=True)
    else:
        targets = sorted([c['price'] for c in clusters 
                         if c['level_type'] == 'high' and c['price'] > entry])
    
    target1 = targets[0] if len(targets) >= 1 else (entry * 0.99 if direction == "SHORT" else entry * 1.01)
    target2 = targets[1] if len(targets) >= 2 else (target1 * 0.99 if direction == "SHORT" else target1 * 1.01)
    
    # Simulate trade with real exit logic
    result = simulate_trade_real(symbol, date, direction, entry, target1, target2,
                                  entry_time, regular_bars, entry_idx)
    
    return {
        "date": date,
        "direction": direction,
        "cluster_swept": best_setup['cluster']['price'],
        "cluster_count": best_setup['cluster']['count'],
        "sweep_time": best_setup['sweep_time'],
        "sweep_volume": best_setup['sweep_volume'],
        "avg_volume": best_setup['avg_volume'],
        "volume_ratio": best_setup['volume_ratio'],
        "reclaim_time": best_setup['reclaim_time'],
        "reclaim_mins": best_setup.get('reclaim_mins', 0),
        "confirm_time": best_setup['confirm_time'],
        "confirm_bars_after": best_setup['confirm_bars_after'],
        "entry_price": entry,
        "target1": target1,
        "target2": target2,
        **result
    }


def run_backtest(symbol: str, start: str, end: str):
    """Full backtest with FIXED entry timing + volume."""
    
    print(f"\n{'='*90}")
    print(f"TITAN V3 FIXED BACKTEST")
    print(f"CHANGES: Entry after confirmation bar + Volume check + Tighter stop (-50%)")
    print(f"{symbol}: {start} to {end}")
    print(f"{'='*90}\n")
    
    # Fetch all daily bars upfront
    print("Loading daily bars...")
    lookback_start = (datetime.strptime(start, '%Y-%m-%d') - timedelta(days=30)).strftime('%Y-%m-%d')
    daily_bars = fetch_daily_bars_polygon(symbol, lookback_start, end)
    print(f"Loaded {len(daily_bars)} daily bars\n")
    
    start_dt = datetime.strptime(start, '%Y-%m-%d')
    end_dt = datetime.strptime(end, '%Y-%m-%d')
    
    trades = []
    current = start_dt
    
    while current <= end_dt:
        if current.weekday() >= 5:
            current += timedelta(days=1)
            continue
        
        date_str = current.strftime('%Y-%m-%d')
        print(f"{date_str}: ", end="", flush=True)
        
        result = analyze_day(symbol, date_str, daily_bars)
        
        if result and result.get('option_entry'):
            trades.append(result)
            pnl = result.get('combined_pnl', 0)
            pnl_pct = result.get('pnl_pct', 0)
            exit_reason = result.get('exit_reason', '?')
            vol_ratio = result.get('volume_ratio', 0)
            confirm_bars = result.get('confirm_bars_after', 0)
            
            status = "✅" if pnl > 0 else "❌"
            print(f"{status} {result['direction']} {result['cluster_count']}x | "
                  f"Vol:{vol_ratio:.1f}x | +{confirm_bars}bars | "
                  f"${result.get('option_entry', 0):.2f}→{pnl_pct:+.0f}% | "
                  f"${pnl:+.0f} | {exit_reason}")
        else:
            print("no setup")
        
        current += timedelta(days=1)
        time.sleep(0.15)
    
    if not trades:
        print("\nNo trades found.")
        return trades
    
    # Stats
    print(f"\n{'='*90}")
    print("RESULTS")
    print(f"{'='*90}")
    
    wins = [t for t in trades if t.get('combined_pnl', 0) > 0]
    losses = [t for t in trades if t.get('combined_pnl', 0) <= 0]
    
    print(f"Total Trades: {len(trades)}")
    print(f"Winners: {len(wins)} ({len(wins)/len(trades)*100:.1f}%)")
    print(f"Losers: {len(losses)}")
    
    total_pnl = sum(t.get('combined_pnl', 0) for t in trades)
    avg_win = sum(t.get('combined_pnl', 0) for t in wins) / len(wins) if wins else 0
    avg_loss = sum(t.get('combined_pnl', 0) for t in losses) / len(losses) if losses else 0
    
    print(f"\nTotal P&L: ${total_pnl:+,.0f}")
    print(f"Avg Win: ${avg_win:+,.0f}")
    print(f"Avg Loss: ${avg_loss:+,.0f}")
    
    # Exit reasons
    print(f"\nExit Reasons:")
    reasons = {}
    for t in trades:
        r = t.get('exit_reason', 'unknown')
        reasons[r] = reasons.get(r, 0) + 1
    for r, c in sorted(reasons.items(), key=lambda x: -x[1]):
        print(f"  {r}: {c}")
    
    # Compounded returns
    balance = 10000
    for t in trades:
        pnl_pct = t.get('pnl_pct', 0) / 100
        # Risk 10% per trade
        balance *= (1 + pnl_pct * 0.1)
    
    print(f"\n$10,000 (10% risk/trade) → ${balance:,.0f} ({(balance/10000-1)*100:+.1f}%)")
    print(f"{'='*90}\n")
    
    return trades


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) >= 4:
        symbol = sys.argv[1]
        start = sys.argv[2]
        end = sys.argv[3]
        run_backtest(symbol, start, end)
    else:
        # Default
        run_backtest("QQQ", "2026-01-13", "2026-02-13")
