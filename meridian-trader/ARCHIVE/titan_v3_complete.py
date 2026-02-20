"""
TITAN V3 COMPLETE - Full System with OTM Strikes + 80/20 Split
- All session levels (Asia/London/US)
- OTM strike selection at target
- 80% 0DTE + 20% 1DTE position split
- Separate P&L tracking for each leg
"""

import requests
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict
import json

POLYGON_API_KEY = "h7J74V1cd8_4NQpTxwQpudpqXWaIHMhv"

# ============================================================
# DATA FETCHING
# ============================================================

def fetch_minute_bars(symbol: str, date: str) -> dict:
    """Fetch minute data split by session."""
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{date}/{date}"
    params = {"adjusted": "true", "sort": "asc", "limit": 50000, "apiKey": POLYGON_API_KEY}
    resp = requests.get(url, params=params, timeout=30)
    bars = resp.json().get("results", [])
    
    asia, london, premarket, regular = [], [], [], []
    
    for bar in bars:
        ts = datetime.fromtimestamp(bar['t']/1000, tz=timezone.utc)
        bar['ts'] = ts
        et_hour = ts.hour - 5  # UTC to ET
        bar['time_et'] = f"{et_hour}:{ts.minute:02d}"
        
        # Session classification (ET hours)
        if -6 <= et_hour < 2:  # 6pm-2am ET (Asia) - previous evening
            asia.append(bar)
        elif 2 <= et_hour < 5:  # 2am-5am ET (London)
            london.append(bar)
        elif 5 <= et_hour < 9 or (et_hour == 9 and ts.minute < 30):  # 5am-9:30am (Premarket)
            premarket.append(bar)
        elif 9 <= et_hour < 16:  # 9:30am-4pm (Regular)
            regular.append(bar)
    
    return {"asia": asia, "london": london, "premarket": premarket, "regular": regular, "all": bars}

def fetch_daily_bars(symbol: str, start: str, end: str) -> List[dict]:
    """Fetch daily OHLCV."""
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{start}/{end}"
    params = {"adjusted": "true", "sort": "asc", "limit": 500, "apiKey": POLYGON_API_KEY}
    resp = requests.get(url, params=params, timeout=30)
    return resp.json().get("results", [])


# ============================================================
# LEVEL DETECTION
# ============================================================

def get_session_levels(session_bars: List[dict], session_name: str) -> dict:
    """Extract high/low from a session."""
    if not session_bars:
        return None
    return {
        "high": max(b['h'] for b in session_bars),
        "low": min(b['l'] for b in session_bars),
        "session": session_name
    }

def detect_swing_levels(daily_bars: List[dict], lookback: int = 2) -> Dict:
    """Detect swing highs/lows."""
    swing_highs, swing_lows = [], []
    
    for i in range(lookback, len(daily_bars) - lookback):
        bar = daily_bars[i]
        date = datetime.fromtimestamp(bar['t']/1000).strftime("%Y-%m-%d")
        
        is_swing_high = all(daily_bars[j]['h'] < bar['h'] for j in range(i-lookback, i+lookback+1) if j != i)
        is_swing_low = all(daily_bars[j]['l'] > bar['l'] for j in range(i-lookback, i+lookback+1) if j != i)
        
        if is_swing_high:
            swing_highs.append({"price": bar['h'], "date": date, "type": "swing_high"})
        if is_swing_low:
            swing_lows.append({"price": bar['l'], "date": date, "type": "swing_low"})
    
    return {"swing_highs": swing_highs, "swing_lows": swing_lows}

def detect_clusters(levels: List[dict], threshold: float = 0.005) -> List[dict]:
    """Group levels within threshold."""
    if not levels:
        return []
    
    sorted_levels = sorted(levels, key=lambda x: x['price'])
    clusters = []
    current = [sorted_levels[0]]
    
    for level in sorted_levels[1:]:
        avg = sum(l['price'] for l in current) / len(current)
        if abs(level['price'] - avg) / avg <= threshold:
            current.append(level)
        else:
            if len(current) >= 2:
                clusters.append({
                    "price": max(l['price'] for l in current),
                    "count": len(current),
                    "type": "cluster"
                })
            current = [level]
    
    if len(current) >= 2:
        clusters.append({
            "price": max(l['price'] for l in current),
            "count": len(current),
            "type": "cluster"
        })
    
    return clusters

def get_all_levels(symbol: str, date: str, lookback_days: int = 15) -> Dict:
    """Get all significant levels for a trading day."""
    end_dt = datetime.strptime(date, "%Y-%m-%d")
    start_dt = end_dt - timedelta(days=lookback_days + 5)
    
    # Get daily bars for swing detection
    daily_bars = fetch_daily_bars(symbol, start_dt.strftime("%Y-%m-%d"), 
                                   (end_dt - timedelta(days=1)).strftime("%Y-%m-%d"))
    
    # Get minute data for today's session levels
    minute_data = fetch_minute_bars(symbol, date)
    
    # Swing levels
    swings = detect_swing_levels(daily_bars) if len(daily_bars) >= 5 else {"swing_highs": [], "swing_lows": []}
    
    # Recent session highs/lows (last 5 days)
    recent_highs, recent_lows = [], []
    cutoff = (end_dt - timedelta(days=5)).strftime("%Y-%m-%d")
    for bar in daily_bars:
        d = datetime.fromtimestamp(bar['t']/1000).strftime("%Y-%m-%d")
        if d >= cutoff:
            recent_highs.append({"price": bar['h'], "date": d, "type": "recent_high"})
            recent_lows.append({"price": bar['l'], "date": d, "type": "recent_low"})
    
    # Today's session levels
    asia_levels = get_session_levels(minute_data['asia'], 'asia')
    london_levels = get_session_levels(minute_data['london'], 'london')
    premarket_levels = get_session_levels(minute_data['premarket'], 'premarket')
    
    # Combine all highs and lows
    all_highs = swings['swing_highs'] + recent_highs
    all_lows = swings['swing_lows'] + recent_lows
    
    # Add session levels
    for lvl in [asia_levels, london_levels, premarket_levels]:
        if lvl:
            all_highs.append({"price": lvl['high'], "date": date, "type": f"{lvl['session']}_high"})
            all_lows.append({"price": lvl['low'], "date": date, "type": f"{lvl['session']}_low"})
    
    # Detect clusters
    high_clusters = detect_clusters(all_highs)
    low_clusters = detect_clusters(all_lows)
    
    return {
        "swing_highs": swings['swing_highs'],
        "swing_lows": swings['swing_lows'],
        "recent_highs": recent_highs,
        "recent_lows": recent_lows,
        "session_levels": {"asia": asia_levels, "london": london_levels, "premarket": premarket_levels},
        "high_clusters": high_clusters,
        "low_clusters": low_clusters,
        "minute_data": minute_data
    }


# ============================================================
# OPTION PRICING
# ============================================================

def estimate_option_price(underlying: float, strike: float, direction: str, dte: int) -> float:
    """
    Estimate OTM option price.
    OTM options are CHEAP at entry, become valuable as they approach/pass strike.
    """
    distance = abs(underlying - strike)
    distance_pct = distance / underlying
    
    # OTM 0DTE options are cheap - roughly $0.30-1.50 depending on distance
    # They explode in value when underlying approaches strike
    if dte == 0:
        # Base: ~$0.50-2.00 for 0DTE depending on OTM distance
        base = 2.50 * max(0.20, 1 - distance_pct * 5)  # Cheaper the further OTM
    else:
        # 1DTE has more time value
        base = 4.00 * max(0.30, 1 - distance_pct * 4)
    
    return max(0.30, base)  # Minimum $0.30

def option_value_at_price(underlying_now: float, strike: float, direction: str, dte: int) -> float:
    """
    Calculate option value when underlying moves.
    Key: OTM becomes ATM = big gain. ATM becomes ITM = intrinsic + time value.
    """
    if direction == "PUT":
        intrinsic = max(0, strike - underlying_now)
        distance_to_strike = underlying_now - strike  # Positive = OTM, Negative = ITM
    else:
        intrinsic = max(0, underlying_now - strike)
        distance_to_strike = strike - underlying_now
    
    distance_pct = distance_to_strike / underlying_now if underlying_now > 0 else 0
    
    # Time value - higher for ATM, lower for far OTM/ITM
    if dte == 0:
        # 0DTE ATM time value ~$2-3, decays to near zero for far OTM/ITM
        atm_time_value = 2.50
    else:
        atm_time_value = 4.00
    
    # Time value peaks at ATM, decreases as you go OTM or deep ITM
    if abs(distance_pct) < 0.005:  # Near ATM
        time_value = atm_time_value
    else:
        time_value = atm_time_value * max(0.1, 1 - abs(distance_pct) * 3)
    
    return intrinsic + time_value


# ============================================================
# SWEEP DETECTION
# ============================================================

def find_sweep_reclaim(bars: List[dict], level: float, level_type: str) -> Optional[dict]:
    """Find sweep through level and reclaim."""
    for i, bar in enumerate(bars):
        if level_type == "high" and bar['h'] > level:
            # Look for reclaim below
            for j in range(i + 1, min(i + 11, len(bars))):
                if bars[j]['c'] < level:
                    return {
                        "sweep_idx": i,
                        "sweep_time": bar['time_et'],
                        "sweep_price": bar['h'],
                        "reclaim_idx": j,
                        "reclaim_time": bars[j]['time_et'],
                        "entry_price": bars[j]['c'],
                        "direction": "SHORT"
                    }
            return None
        
        elif level_type == "low" and bar['l'] < level:
            for j in range(i + 1, min(i + 11, len(bars))):
                if bars[j]['c'] > level:
                    return {
                        "sweep_idx": i,
                        "sweep_time": bar['time_et'],
                        "sweep_price": bar['l'],
                        "reclaim_idx": j,
                        "reclaim_time": bars[j]['time_et'],
                        "entry_price": bars[j]['c'],
                        "direction": "LONG"
                    }
            return None
    return None


# ============================================================
# TRADE SIMULATION (80/20 SPLIT)
# ============================================================

def simulate_trade_full(entry_price: float, direction: str, target1: float, target2: float,
                        bars: List[dict], entry_idx: int) -> dict:
    """
    Simulate full trade with 80/20 split.
    - 80% 0DTE exits at TP1
    - 20% 1DTE runs to TP2 with trailing stop
    """
    
    # Strike selection - OTM at target
    if direction == "SHORT":
        strike = round(target1)  # Put strike at target
    else:
        strike = round(target1)  # Call strike at target
    
    # Entry prices
    entry_0dte = estimate_option_price(entry_price, strike, "PUT" if direction == "SHORT" else "CALL", 0)
    entry_1dte = estimate_option_price(entry_price, strike, "PUT" if direction == "SHORT" else "CALL", 1)
    
    # Track both legs
    leg_0dte = {"entry": entry_0dte, "exit": None, "exit_reason": None, "exit_time": None}
    leg_1dte = {"entry": entry_1dte, "exit": None, "exit_reason": None, "exit_time": None, "max_price": entry_1dte}
    
    trailing_active = False
    trailing_stop = None
    
    for bar in bars[entry_idx + 1:]:
        if direction == "SHORT":
            current_underlying = bar['l']  # Best case for puts
            worst_underlying = bar['h']
        else:
            current_underlying = bar['h']  # Best case for calls
            worst_underlying = bar['l']
        
        # Calculate current option values
        current_0dte = option_value_at_price(current_underlying, strike, "PUT" if direction == "SHORT" else "CALL", 0)
        current_1dte = option_value_at_price(current_underlying, strike, "PUT" if direction == "SHORT" else "CALL", 1)
        
        # 0DTE LEG - Exit at TP1
        if leg_0dte['exit'] is None:
            if direction == "SHORT" and bar['l'] <= target1:
                leg_0dte['exit'] = option_value_at_price(target1, strike, "PUT", 0)
                leg_0dte['exit_reason'] = "TP1"
                leg_0dte['exit_time'] = bar['time_et']
            elif direction == "LONG" and bar['h'] >= target1:
                leg_0dte['exit'] = option_value_at_price(target1, strike, "CALL", 0)
                leg_0dte['exit_reason'] = "TP1"
                leg_0dte['exit_time'] = bar['time_et']
            # Stop check for 0DTE
            elif current_0dte <= entry_0dte * 0.20:  # -80% stop
                leg_0dte['exit'] = entry_0dte * 0.20
                leg_0dte['exit_reason'] = "STOP"
                leg_0dte['exit_time'] = bar['time_et']
        
        # 1DTE LEG - Run to TP2 with trail
        if leg_1dte['exit'] is None:
            # Update max
            if current_1dte > leg_1dte['max_price']:
                leg_1dte['max_price'] = current_1dte
                
                # Activate trail at +30%
                if leg_1dte['max_price'] >= entry_1dte * 1.30 and not trailing_active:
                    trailing_active = True
                
                if trailing_active:
                    trailing_stop = leg_1dte['max_price'] * 0.85  # Trail at 15%
            
            # Check TP2
            if direction == "SHORT" and bar['l'] <= target2:
                leg_1dte['exit'] = option_value_at_price(target2, strike, "PUT", 1)
                leg_1dte['exit_reason'] = "TP2"
                leg_1dte['exit_time'] = bar['time_et']
            elif direction == "LONG" and bar['h'] >= target2:
                leg_1dte['exit'] = option_value_at_price(target2, strike, "CALL", 1)
                leg_1dte['exit_reason'] = "TP2"
                leg_1dte['exit_time'] = bar['time_et']
            # Trail stop
            elif trailing_active and current_1dte <= trailing_stop:
                leg_1dte['exit'] = trailing_stop
                leg_1dte['exit_reason'] = "TRAIL"
                leg_1dte['exit_time'] = bar['time_et']
            # Hard stop
            elif current_1dte <= entry_1dte * 0.20:
                leg_1dte['exit'] = entry_1dte * 0.20
                leg_1dte['exit_reason'] = "STOP"
                leg_1dte['exit_time'] = bar['time_et']
        
        # Both legs closed
        if leg_0dte['exit'] and leg_1dte['exit']:
            break
    
    # EOD exits for unclosed
    last_bar = bars[-1]
    if direction == "SHORT":
        eod_underlying = last_bar['c']
    else:
        eod_underlying = last_bar['c']
    
    if leg_0dte['exit'] is None:
        leg_0dte['exit'] = max(option_value_at_price(eod_underlying, strike, "PUT" if direction == "SHORT" else "CALL", 0), entry_0dte * 0.05)
        leg_0dte['exit_reason'] = "EOD"
        leg_0dte['exit_time'] = last_bar['time_et']
    
    if leg_1dte['exit'] is None:
        leg_1dte['exit'] = option_value_at_price(eod_underlying, strike, "PUT" if direction == "SHORT" else "CALL", 1)
        leg_1dte['exit_reason'] = "EOD"
        leg_1dte['exit_time'] = last_bar['time_et']
    
    # Calculate returns
    pnl_0dte = (leg_0dte['exit'] - leg_0dte['entry']) / leg_0dte['entry'] * 100
    pnl_1dte = (leg_1dte['exit'] - leg_1dte['entry']) / leg_1dte['entry'] * 100
    
    # Combined (80/20 weighted)
    combined_pnl = pnl_0dte * 0.80 + pnl_1dte * 0.20
    
    return {
        "strike": strike,
        "entry_0dte": entry_0dte,
        "entry_1dte": entry_1dte,
        "leg_0dte": leg_0dte,
        "leg_1dte": leg_1dte,
        "pnl_0dte": pnl_0dte,
        "pnl_1dte": pnl_1dte,
        "combined_pnl": combined_pnl
    }


# ============================================================
# BACKTEST
# ============================================================

def backtest_day(symbol: str, date: str) -> Optional[dict]:
    """Run TITAN on a single day."""
    
    levels = get_all_levels(symbol, date)
    regular_bars = levels['minute_data']['regular']
    
    if not regular_bars:
        return None
    
    # Build level list - PRIORITIZE BY SIGNIFICANCE
    # Bigger clusters = more significant = check first
    levels_to_check = []
    
    # Combine all clusters with their touch counts
    all_clusters = []
    for c in levels['high_clusters']:
        all_clusters.append({"price": c['price'], "type": "high", "source": f"cluster {c['count']}x", "count": c['count']})
    for c in levels['low_clusters']:
        all_clusters.append({"price": c['price'], "type": "low", "source": f"cluster {c['count']}x", "count": c['count']})
    
    # Sort by count (most touches first) - these are the SIGNIFICANT levels
    all_clusters.sort(key=lambda x: -x['count'])
    
    # Add clusters in significance order
    for c in all_clusters:
        if c['count'] >= 3:  # Minimum 3 touches to be significant
            levels_to_check.append(c)
    
    # Then add swing levels
    for sh in levels['swing_highs']:
        if not any(abs(sh['price'] - l['price'])/l['price'] < 0.005 for l in levels_to_check):
            levels_to_check.append({"price": sh['price'], "type": "high", "source": f"swing {sh['date']}", "count": 1})
    
    for sl in levels['swing_lows']:
        if not any(abs(sl['price'] - l['price'])/l['price'] < 0.005 for l in levels_to_check):
            levels_to_check.append({"price": sl['price'], "type": "low", "source": f"swing {sl['date']}", "count": 1})
    
    # Recent levels last (least significant)
    for rh in levels['recent_highs']:
        if not any(abs(rh['price'] - l['price'])/l['price'] < 0.005 for l in levels_to_check):
            levels_to_check.append({"price": rh['price'], "type": "high", "source": f"recent {rh['date']}", "count": 0})
    
    for rl in levels['recent_lows']:
        if not any(abs(rl['price'] - l['price'])/l['price'] < 0.005 for l in levels_to_check):
            levels_to_check.append({"price": rl['price'], "type": "low", "source": f"recent {rl['date']}", "count": 0})
    
    # Find sweep + reclaim - PRIORITIZE BY SIGNIFICANCE (count), not time
    best_setup = None
    best_significance = -1
    
    for level in levels_to_check:
        setup = find_sweep_reclaim(regular_bars, level['price'], level['type'])
        if setup:
            significance = level.get('count', 0)
            # Take the most significant level that sweeps, not the earliest
            if significance > best_significance:
                best_significance = significance
                best_setup = {**setup, "level": level}
    
    if not best_setup:
        return None
    
    # Find targets
    entry = best_setup['entry_price']
    direction = best_setup['direction']
    
    if direction == "SHORT":
        lows = sorted([l['price'] for l in levels_to_check if l['type'] == 'low' and l['price'] < entry], reverse=True)
        target1 = lows[0] if lows else entry * 0.995
        target2 = lows[1] if len(lows) > 1 else target1 * 0.995
    else:
        highs = sorted([l['price'] for l in levels_to_check if l['type'] == 'high' and l['price'] > entry])
        target1 = highs[0] if highs else entry * 1.005
        target2 = highs[1] if len(highs) > 1 else target1 * 1.005
    
    # Simulate trade
    result = simulate_trade_full(entry, direction, target1, target2, regular_bars, best_setup['reclaim_idx'])
    
    return {
        "date": date,
        "direction": direction,
        "level": best_setup['level']['price'],
        "source": best_setup['level']['source'],
        "sweep_time": best_setup['sweep_time'],
        "entry_price": entry,
        "entry_time": best_setup['reclaim_time'],
        "target1": target1,
        "target2": target2,
        **result
    }


def run_backtest(symbol: str, start: str, end: str):
    """Full backtest."""
    
    start_dt = datetime.strptime(start, "%Y-%m-%d")
    end_dt = datetime.strptime(end, "%Y-%m-%d")
    
    print(f"\n{'='*80}")
    print(f"TITAN V3 COMPLETE BACKTEST - {symbol}")
    print(f"80% 0DTE + 20% 1DTE | OTM Strikes at Target")
    print(f"{start} to {end}")
    print(f"{'='*80}\n")
    
    trades = []
    current = start_dt
    
    while current <= end_dt:
        if current.weekday() >= 5:
            current += timedelta(days=1)
            continue
        
        date_str = current.strftime("%Y-%m-%d")
        print(f"{date_str}:", end=" ")
        
        result = backtest_day(symbol, date_str)
        
        if result:
            trades.append(result)
            print(f"{result['direction']} {result['source'][:15]:<15} | "
                  f"0DTE: {result['pnl_0dte']:+.0f}% ({result['leg_0dte']['exit_reason']}) | "
                  f"1DTE: {result['pnl_1dte']:+.0f}% ({result['leg_1dte']['exit_reason']}) | "
                  f"Combined: {result['combined_pnl']:+.0f}%")
        else:
            print("no setup")
        
        current += timedelta(days=1)
    
    if not trades:
        print("\nNo trades.")
        return
    
    # Stats
    wins = [t for t in trades if t['combined_pnl'] > 0]
    losses = [t for t in trades if t['combined_pnl'] <= 0]
    
    wr = len(wins) / len(trades) * 100
    avg_win = sum(t['combined_pnl'] for t in wins) / len(wins) if wins else 0
    avg_loss = sum(t['combined_pnl'] for t in losses) / len(losses) if losses else 0
    
    # Compound
    balance = 10000
    for t in trades:
        pnl = t['combined_pnl'] / 100
        balance += balance * 0.10 * pnl
    
    print(f"\n{'='*80}")
    print("RESULTS")
    print(f"{'='*80}")
    print(f"Trades: {len(trades)} | Wins: {len(wins)} | Losses: {len(losses)}")
    print(f"Win Rate: {wr:.1f}%")
    print(f"Avg Win: +{avg_win:.1f}% | Avg Loss: {avg_loss:.1f}%")
    print(f"\n$10K → ${balance:,.0f} (10% risk/trade)")
    print(f"Return: {(balance-10000)/100:.1f}%")
    
    # Separate leg stats
    print(f"\n--- BY LEG ---")
    avg_0dte = sum(t['pnl_0dte'] for t in trades) / len(trades)
    avg_1dte = sum(t['pnl_1dte'] for t in trades) / len(trades)
    print(f"0DTE Avg: {avg_0dte:+.1f}%")
    print(f"1DTE Avg: {avg_1dte:+.1f}%")


if __name__ == "__main__":
    run_backtest("QQQ", "2026-01-02", "2026-02-13")
