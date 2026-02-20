"""
TITAN V3 LIVE - Full System with Minute Data
- Swing detection on daily timeframe
- Cluster detection (0.5% grouping)
- Minute data for sweep/reclaim timing
- Premarket levels included
- Option P&L estimation
"""

import requests
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict
import json

POLYGON_API_KEY = "h7J74V1cd8_4NQpTxwQpudpqXWaIHMhv"

# ============================================================
# DATA FETCHING
# ============================================================

def fetch_daily_bars(symbol: str, start: str, end: str) -> List[dict]:
    """Fetch daily OHLCV data."""
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{start}/{end}"
    params = {"adjusted": "true", "sort": "asc", "limit": 500, "apiKey": POLYGON_API_KEY}
    resp = requests.get(url, params=params, timeout=30)
    data = resp.json()
    return data.get("results", [])

def fetch_minute_bars(symbol: str, date: str) -> dict:
    """Fetch minute data for a single day, split into sessions."""
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{date}/{date}"
    params = {"adjusted": "true", "sort": "asc", "limit": 50000, "apiKey": POLYGON_API_KEY}
    resp = requests.get(url, params=params, timeout=30)
    data = resp.json()
    bars = data.get("results", [])
    
    premarket, regular = [], []
    for bar in bars:
        ts = datetime.fromtimestamp(bar['t']/1000, tz=timezone.utc)
        bar['ts'] = ts
        bar['time_et'] = f"{ts.hour-5}:{ts.minute:02d}"
        
        if ts.hour < 14 or (ts.hour == 14 and ts.minute < 30):
            premarket.append(bar)
        elif ts.hour < 21:
            regular.append(bar)
    
    return {"premarket": premarket, "regular": regular, "all": bars}


# ============================================================
# SWING & CLUSTER DETECTION
# ============================================================

def detect_swing_levels(daily_bars: List[dict], lookback: int = 2) -> Dict:
    """
    Detect swing highs/lows from daily bars.
    Swing high = high > high of N days before AND after
    """
    swing_highs = []
    swing_lows = []
    
    for i in range(lookback, len(daily_bars) - lookback):
        bar = daily_bars[i]
        date = datetime.fromtimestamp(bar['t']/1000).strftime("%Y-%m-%d")
        
        # Check swing high
        is_swing_high = True
        for j in range(i - lookback, i + lookback + 1):
            if j != i and daily_bars[j]['h'] >= bar['h']:
                is_swing_high = False
                break
        
        if is_swing_high:
            swing_highs.append({
                "price": bar['h'],
                "date": date,
                "type": "swing_high"
            })
        
        # Check swing low
        is_swing_low = True
        for j in range(i - lookback, i + lookback + 1):
            if j != i and daily_bars[j]['l'] <= bar['l']:
                is_swing_low = False
                break
        
        if is_swing_low:
            swing_lows.append({
                "price": bar['l'],
                "date": date,
                "type": "swing_low"
            })
    
    return {"swing_highs": swing_highs, "swing_lows": swing_lows}


def detect_clusters(levels: List[dict], threshold: float = 0.005) -> List[dict]:
    """
    Group levels within threshold % into clusters.
    """
    if not levels:
        return []
    
    sorted_levels = sorted(levels, key=lambda x: x['price'])
    clusters = []
    current_cluster = [sorted_levels[0]]
    
    for level in sorted_levels[1:]:
        # Check if within threshold of cluster
        cluster_avg = sum(l['price'] for l in current_cluster) / len(current_cluster)
        if abs(level['price'] - cluster_avg) / cluster_avg <= threshold:
            current_cluster.append(level)
        else:
            # Save current cluster
            if len(current_cluster) >= 2:
                clusters.append({
                    "min": min(l['price'] for l in current_cluster),
                    "max": max(l['price'] for l in current_cluster),
                    "mid": sum(l['price'] for l in current_cluster) / len(current_cluster),
                    "count": len(current_cluster),
                    "dates": [l['date'] for l in current_cluster],
                    "type": current_cluster[0]['type'] + "_cluster"
                })
            current_cluster = [level]
    
    # Don't forget last cluster
    if len(current_cluster) >= 2:
        clusters.append({
            "min": min(l['price'] for l in current_cluster),
            "max": max(l['price'] for l in current_cluster),
            "mid": sum(l['price'] for l in current_cluster) / len(current_cluster),
            "count": len(current_cluster),
            "dates": [l['date'] for l in current_cluster],
            "type": current_cluster[0]['type'] + "_cluster"
        })
    
    return clusters


def get_significant_levels(symbol: str, before_date: str, lookback_days: int = 20, recent_days: int = 5) -> Dict:
    """
    Get all significant levels (swings + recent session highs/lows + clusters) before a date.
    
    Two types of levels:
    1. SWING highs/lows (lookback_days) - Major reversal points
    2. RECENT session highs/lows (recent_days) - Even non-swings, for cluster detection
    """
    end_dt = datetime.strptime(before_date, "%Y-%m-%d")
    start_dt = end_dt - timedelta(days=lookback_days + 10)  # Extra for swing detection
    
    daily_bars = fetch_daily_bars(symbol, start_dt.strftime("%Y-%m-%d"), 
                                   (end_dt - timedelta(days=1)).strftime("%Y-%m-%d"))
    
    if len(daily_bars) < 5:
        return {"swing_highs": [], "swing_lows": [], "recent_highs": [], "recent_lows": [], "high_clusters": [], "low_clusters": []}
    
    # Get swing levels
    swings = detect_swing_levels(daily_bars)
    
    # Filter swings to lookback period
    cutoff = (end_dt - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
    swing_highs = [s for s in swings['swing_highs'] if s['date'] >= cutoff]
    swing_lows = [s for s in swings['swing_lows'] if s['date'] >= cutoff]
    
    # Get RECENT session highs/lows (last N days, regardless of swing status)
    recent_cutoff = (end_dt - timedelta(days=recent_days)).strftime("%Y-%m-%d")
    recent_highs = []
    recent_lows = []
    
    for bar in daily_bars:
        date = datetime.fromtimestamp(bar['t']/1000).strftime("%Y-%m-%d")
        if date >= recent_cutoff and date < before_date:
            recent_highs.append({
                "price": bar['h'],
                "date": date,
                "type": "recent_high"
            })
            recent_lows.append({
                "price": bar['l'],
                "date": date,
                "type": "recent_low"
            })
    
    # Combine all highs and lows for cluster detection
    all_highs = swing_highs + recent_highs
    all_lows = swing_lows + recent_lows
    
    # Detect clusters from combined levels
    high_clusters = detect_clusters(all_highs) if all_highs else []
    low_clusters = detect_clusters(all_lows) if all_lows else []
    
    return {
        "swing_highs": swing_highs,
        "swing_lows": swing_lows,
        "recent_highs": recent_highs,
        "recent_lows": recent_lows,
        "high_clusters": high_clusters,
        "low_clusters": low_clusters
    }


# ============================================================
# SWEEP DETECTION (MINUTE DATA)
# ============================================================

def find_sweep_and_reclaim(minute_bars: List[dict], level: float, level_type: str, 
                            reclaim_bars: int = 10) -> Optional[dict]:
    """
    Find sweep through level and reclaim.
    level_type: "high" or "low"
    """
    for i, bar in enumerate(minute_bars):
        if level_type == "high":
            # Sweep above high
            if bar['h'] > level:
                # Look for reclaim below
                for j in range(i + 1, min(i + reclaim_bars + 1, len(minute_bars))):
                    if minute_bars[j]['c'] < level:
                        return {
                            "sweep_time": bar['time_et'],
                            "sweep_price": bar['h'],
                            "reclaim_time": minute_bars[j]['time_et'],
                            "entry_price": minute_bars[j]['c'],
                            "entry_bar_idx": j,
                            "direction": "SHORT"
                        }
                return None  # Swept but no reclaim
        else:
            # Sweep below low
            if bar['l'] < level:
                # Look for reclaim above
                for j in range(i + 1, min(i + reclaim_bars + 1, len(minute_bars))):
                    if minute_bars[j]['c'] > level:
                        return {
                            "sweep_time": bar['time_et'],
                            "sweep_price": bar['l'],
                            "reclaim_time": minute_bars[j]['time_et'],
                            "entry_price": minute_bars[j]['c'],
                            "entry_bar_idx": j,
                            "direction": "LONG"
                        }
                return None
    return None


# ============================================================
# TRADE SIMULATION
# ============================================================

def simulate_option_trade(entry_price: float, direction: str, minute_bars: List[dict], 
                          entry_idx: int, target: Optional[float] = None) -> dict:
    """
    Simulate option trade from entry to exit.
    Uses 75x leverage approximation for ATM 0DTE options.
    """
    OPTION_LEVERAGE = 75
    MAX_LOSS = -0.80
    TRAIL_TRIGGER = 0.30  # Activate trail at +30%
    TRAIL_AMOUNT = 0.15   # Trail by 15%
    
    max_favorable = 0
    trailing_active = False
    trailing_stop = None
    
    for i, bar in enumerate(minute_bars[entry_idx + 1:], start=entry_idx + 1):
        if direction == "LONG":
            move_pct = (bar['h'] - entry_price) / entry_price
            adverse_pct = (entry_price - bar['l']) / entry_price
            current_price = bar['c']
            
            # Check target
            if target and bar['h'] >= target:
                underlying_move = (target - entry_price) / entry_price
                option_pnl = underlying_move * OPTION_LEVERAGE
                return {
                    "exit_price": target,
                    "exit_time": bar['time_et'],
                    "exit_reason": "TARGET",
                    "underlying_move_pct": underlying_move * 100,
                    "option_pnl_pct": option_pnl * 100
                }
            
            # Update max favorable
            if move_pct > max_favorable:
                max_favorable = move_pct
                if max_favorable >= TRAIL_TRIGGER and not trailing_active:
                    trailing_active = True
                if trailing_active:
                    trailing_stop = entry_price * (1 + max_favorable - TRAIL_AMOUNT)
            
            # Check trailing stop
            if trailing_active and bar['l'] <= trailing_stop:
                underlying_move = (trailing_stop - entry_price) / entry_price
                option_pnl = underlying_move * OPTION_LEVERAGE
                return {
                    "exit_price": trailing_stop,
                    "exit_time": bar['time_et'],
                    "exit_reason": "TRAIL_STOP",
                    "underlying_move_pct": underlying_move * 100,
                    "option_pnl_pct": option_pnl * 100
                }
            
            # Check hard stop (roughly -1% underlying = -75% option)
            if adverse_pct >= 0.0107:  # ~80% option loss
                underlying_move = -adverse_pct
                return {
                    "exit_price": bar['l'],
                    "exit_time": bar['time_et'],
                    "exit_reason": "STOP",
                    "underlying_move_pct": underlying_move * 100,
                    "option_pnl_pct": MAX_LOSS * 100
                }
        
        else:  # SHORT (puts)
            move_pct = (entry_price - bar['l']) / entry_price
            adverse_pct = (bar['h'] - entry_price) / entry_price
            
            # Check target
            if target and bar['l'] <= target:
                underlying_move = (entry_price - target) / entry_price
                option_pnl = underlying_move * OPTION_LEVERAGE
                return {
                    "exit_price": target,
                    "exit_time": bar['time_et'],
                    "exit_reason": "TARGET",
                    "underlying_move_pct": underlying_move * 100,
                    "option_pnl_pct": option_pnl * 100
                }
            
            if move_pct > max_favorable:
                max_favorable = move_pct
                if max_favorable >= TRAIL_TRIGGER and not trailing_active:
                    trailing_active = True
                if trailing_active:
                    trailing_stop = entry_price * (1 - max_favorable + TRAIL_AMOUNT)
            
            if trailing_active and bar['h'] >= trailing_stop:
                underlying_move = (entry_price - trailing_stop) / entry_price
                option_pnl = underlying_move * OPTION_LEVERAGE
                return {
                    "exit_price": trailing_stop,
                    "exit_time": bar['time_et'],
                    "exit_reason": "TRAIL_STOP",
                    "underlying_move_pct": underlying_move * 100,
                    "option_pnl_pct": option_pnl * 100
                }
            
            if adverse_pct >= 0.0107:
                return {
                    "exit_price": bar['h'],
                    "exit_time": bar['time_et'],
                    "exit_reason": "STOP",
                    "underlying_move_pct": -adverse_pct * 100,
                    "option_pnl_pct": MAX_LOSS * 100
                }
    
    # EOD exit
    last_bar = minute_bars[-1]
    if direction == "LONG":
        underlying_move = (last_bar['c'] - entry_price) / entry_price
    else:
        underlying_move = (entry_price - last_bar['c']) / entry_price
    
    option_pnl = max(underlying_move * OPTION_LEVERAGE, MAX_LOSS)
    
    return {
        "exit_price": last_bar['c'],
        "exit_time": last_bar['time_et'],
        "exit_reason": "EOD",
        "underlying_move_pct": underlying_move * 100,
        "option_pnl_pct": option_pnl * 100
    }


# ============================================================
# MAIN BACKTEST
# ============================================================

def backtest_day(symbol: str, date: str, lookback_days: int = 15) -> Optional[dict]:
    """
    Run TITAN V3 on a single day.
    Returns trade result or None if no setup.
    """
    # Get significant levels going into this day
    levels = get_significant_levels(symbol, date, lookback_days)
    
    if not levels['swing_highs'] and not levels['swing_lows']:
        return None
    
    # Get minute data for the day
    minute_data = fetch_minute_bars(symbol, date)
    regular_bars = minute_data['regular']
    
    if not regular_bars:
        return None
    
    # Build level list to check (prioritize: clusters > swings > recent)
    levels_to_check = []
    
    # Add high clusters FIRST (most significant - multiple touches)
    for hc in levels['high_clusters']:
        levels_to_check.append({"price": hc['max'], "type": "high", "source": f"cluster {hc['count']}x", "priority": 1})
    
    # Add individual swing highs
    for sh in levels['swing_highs']:
        # Skip if already covered by a cluster
        if not any(abs(sh['price'] - l['price']) / l['price'] < 0.005 for l in levels_to_check):
            levels_to_check.append({"price": sh['price'], "type": "high", "source": f"swing {sh['date']}", "priority": 2})
    
    # Add recent highs (non-swing)
    for rh in levels.get('recent_highs', []):
        if not any(abs(rh['price'] - l['price']) / l['price'] < 0.005 for l in levels_to_check):
            levels_to_check.append({"price": rh['price'], "type": "high", "source": f"recent {rh['date']}", "priority": 3})
    
    # Add low clusters FIRST
    for lc in levels['low_clusters']:
        levels_to_check.append({"price": lc['min'], "type": "low", "source": f"cluster {lc['count']}x", "priority": 1})
    
    # Add individual swing lows
    for sl in levels['swing_lows']:
        if not any(abs(sl['price'] - l['price']) / l['price'] < 0.005 for l in levels_to_check):
            levels_to_check.append({"price": sl['price'], "type": "low", "source": f"swing {sl['date']}", "priority": 2})
    
    # Add recent lows (non-swing)
    for rl in levels.get('recent_lows', []):
        if not any(abs(rl['price'] - l['price']) / l['price'] < 0.005 for l in levels_to_check):
            levels_to_check.append({"price": rl['price'], "type": "low", "source": f"recent {rl['date']}", "priority": 3})
    
    # Find first sweep + reclaim (ONE TRADE PER DAY)
    best_setup = None
    earliest_time = None
    
    for level in levels_to_check:
        setup = find_sweep_and_reclaim(regular_bars, level['price'], level['type'])
        if setup:
            # Parse time to compare
            sweep_parts = setup['sweep_time'].split(':')
            sweep_minutes = int(sweep_parts[0]) * 60 + int(sweep_parts[1])
            
            if earliest_time is None or sweep_minutes < earliest_time:
                earliest_time = sweep_minutes
                best_setup = {**setup, "level": level}
    
    if not best_setup:
        return None
    
    # Find target (nearest significant level in opposite direction)
    entry = best_setup['entry_price']
    direction = best_setup['direction']
    target = None
    
    if direction == "LONG":
        # Target is nearest swing high above
        highs_above = [l['price'] for l in levels_to_check if l['type'] == 'high' and l['price'] > entry]
        if highs_above:
            target = min(highs_above)
    else:
        # Target is nearest swing low below
        lows_below = [l['price'] for l in levels_to_check if l['type'] == 'low' and l['price'] < entry]
        if lows_below:
            target = max(lows_below)
    
    # Simulate the trade
    result = simulate_option_trade(
        entry, direction, regular_bars, 
        best_setup['entry_bar_idx'], target
    )
    
    return {
        "date": date,
        "direction": direction,
        "level_swept": best_setup['level']['price'],
        "level_source": best_setup['level']['source'],
        "sweep_time": best_setup['sweep_time'],
        "entry_price": best_setup['entry_price'],
        "entry_time": best_setup['reclaim_time'],
        "target": target,
        **result
    }


def run_backtest(symbol: str, start_date: str, end_date: str) -> dict:
    """Run full backtest over date range."""
    
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    
    print(f"\n{'='*70}")
    print(f"TITAN V3 BACKTEST (WITH MINUTE DATA) - {symbol}")
    print(f"{start_date} to {end_date}")
    print(f"{'='*70}\n")
    
    all_trades = []
    current_dt = start_dt
    
    while current_dt <= end_dt:
        if current_dt.weekday() >= 5:  # Skip weekends
            current_dt += timedelta(days=1)
            continue
        
        date_str = current_dt.strftime("%Y-%m-%d")
        print(f"Scanning {date_str}...", end=" ")
        
        result = backtest_day(symbol, date_str)
        
        if result:
            all_trades.append(result)
            pnl = result['option_pnl_pct']
            print(f"{result['direction']} @ {result['entry_time']} → {result['exit_reason']} {pnl:+.1f}%")
        else:
            print("no setup")
        
        current_dt += timedelta(days=1)
    
    # Calculate stats
    if not all_trades:
        print("\nNo trades found.")
        return {"trades": 0}
    
    wins = [t for t in all_trades if t['option_pnl_pct'] > 0]
    losses = [t for t in all_trades if t['option_pnl_pct'] <= 0]
    
    win_rate = len(wins) / len(all_trades) * 100
    avg_win = sum(t['option_pnl_pct'] for t in wins) / len(wins) if wins else 0
    avg_loss = sum(t['option_pnl_pct'] for t in losses) / len(losses) if losses else 0
    
    # Compound with 10% risk
    balance = 10000
    for t in all_trades:
        pnl_pct = t['option_pnl_pct'] / 100
        position = balance * 0.10
        balance += position * pnl_pct
    
    print(f"\n{'='*70}")
    print("RESULTS")
    print(f"{'='*70}")
    print(f"Total Trades: {len(all_trades)}")
    print(f"Wins: {len(wins)} | Losses: {len(losses)}")
    print(f"Win Rate: {win_rate:.1f}%")
    print(f"Avg Win: +{avg_win:.1f}%")
    print(f"Avg Loss: {avg_loss:.1f}%")
    print(f"\n$10K → ${balance:,.0f} (10% risk/trade)")
    print(f"Total Return: {((balance-10000)/10000)*100:.1f}%")
    
    # Show trade list
    print(f"\n{'='*70}")
    print("TRADE LIST")
    print(f"{'='*70}")
    for t in all_trades:
        print(f"{t['date']}: {t['direction']} {t['level_source'][:20]:<20} | "
              f"Entry {t['entry_time']} @ ${t['entry_price']:.2f} | "
              f"{t['exit_reason']} {t['option_pnl_pct']:+.1f}%")
    
    return {
        "trades": len(all_trades),
        "win_rate": win_rate,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "final_balance": balance,
        "all_trades": all_trades
    }


if __name__ == "__main__":
    # Test Jan 2 first
    print("\n=== TESTING JAN 2 ===")
    result = backtest_day("QQQ", "2026-01-02")
    if result:
        print(f"\nTrade found:")
        for k, v in result.items():
            print(f"  {k}: {v}")
    
    # Full backtest
    print("\n\n")
    run_backtest("QQQ", "2026-01-02", "2026-02-13")
