#!/usr/bin/env python3
"""
MERIDIAN V2 BACKTEST - 3 Week (Jan 27 – Feb 17, 2026) on QQQ
=============================================================
Applies the same 3 new filters from meridian_scanner.py:

  FIX 1 - Opening Flush Detection
  FIX 2 - Reclaim Body Quality (body >= 30% of range)
  FIX 3 - Level Fatigue (skip after 2+ successful reclaims on same level)

Runs BEFORE and AFTER each filter so we can see impact of each one.
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import time
import pytz
import json

# ── CONFIG ──
POLYGON_API_KEY = "h7J74V1cd8_4NQpTxwQpudpqXWaIHMhv"
ET = pytz.timezone('US/Eastern')

POSITION_SIZE = 1000
SPLIT_0DTE = 0.80
SPLIT_1DTE = 0.20
OTM_OFFSET = 3.0
MAX_LOSS_PCT = -50
TRAIL_TRIGGER_30 = 30
TRAIL_STOP_30 = 15
TRAIL_TRIGGER_50 = 50
TRAIL_STOP_50 = 30
MAX_RECLAIM_BARS = 5

START_DATE = "2026-01-27"
END_DATE   = "2026-02-17"
SYMBOL     = "QQQ"

# ── DATA FETCHING ──

def fetch_minute_bars(symbol: str, date: str) -> Dict[str, List[dict]]:
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{date}/{date}"
    params = {"apiKey": POLYGON_API_KEY, "limit": 50000}
    try:
        r = requests.get(url, params=params, timeout=15)
        data = r.json()
    except Exception as e:
        print(f"  [ERROR] fetch_minute_bars: {e}")
        return {"premarket": [], "regular": []}

    if data.get('status') not in ('OK', 'DELAYED') or not data.get('results'):
        return {"premarket": [], "regular": []}

    premarket, regular = [], []
    for bar in data['results']:
        ts = datetime.fromtimestamp(bar['t'] / 1000, tz=pytz.UTC).astimezone(ET)
        b = {
            'time': ts.strftime('%H:%M'),
            'dt': ts,
            'o': bar['o'], 'h': bar['h'], 'l': bar['l'], 'c': bar['c'], 'v': bar['v']
        }
        if (ts.hour >= 4 and ts.hour < 9) or (ts.hour == 9 and ts.minute < 30):
            premarket.append(b)
        elif (ts.hour == 9 and ts.minute >= 30) or (10 <= ts.hour < 16):
            regular.append(b)
    return {"premarket": premarket, "regular": regular}


def fetch_daily_bars(symbol: str, start: str, end: str) -> List[dict]:
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{start}/{end}"
    params = {"apiKey": POLYGON_API_KEY, "limit": 50000, "adjusted": "true"}
    try:
        r = requests.get(url, params=params, timeout=15)
        data = r.json()
    except Exception as e:
        print(f"  [ERROR] fetch_daily_bars: {e}")
        return []
    if data.get('status') not in ('OK', 'DELAYED') or not data.get('results'):
        return []
    return [{'date': datetime.fromtimestamp(b['t']/1000).strftime('%Y-%m-%d'),
             'o': b['o'], 'h': b['h'], 'l': b['l'], 'c': b['c']} for b in data['results']]


def get_option_bars(symbol: str, date: str, strike: float, opt_type: str, dte: int = 0) -> Optional[List[dict]]:
    trade_date = datetime.strptime(date, '%Y-%m-%d')
    exp_date = trade_date + timedelta(days=dte)
    while exp_date.weekday() >= 5:
        exp_date += timedelta(days=1)
    exp_str = exp_date.strftime('%y%m%d')
    strike_str = f"{int(strike * 1000):08d}"
    opt_char = 'C' if opt_type == 'call' else 'P'
    ticker = f"O:{symbol}{exp_str}{opt_char}{strike_str}"
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/minute/{date}/{date}"
    params = {"apiKey": POLYGON_API_KEY, "limit": 50000}
    try:
        r = requests.get(url, params=params, timeout=15)
        data = r.json()
    except:
        return None
    if data.get('status') != 'OK' or not data.get('results'):
        return None
    bars = []
    for bar in data['results']:
        ts = datetime.fromtimestamp(bar['t']/1000, tz=pytz.UTC).astimezone(ET)
        bars.append({'time': ts.strftime('%H:%M'), 'dt': ts,
                     'o': bar['o'], 'h': bar['h'], 'l': bar['l'], 'c': bar['c']})
    return bars or None


# ── LEVEL DETECTION ──

def get_premarket_levels(pm_bars: List[dict]) -> Tuple[Optional[float], Optional[float]]:
    if not pm_bars:
        return None, None
    return max(b['h'] for b in pm_bars), min(b['l'] for b in pm_bars)


# ── SWEEP DETECTION (BASE) ──

def find_first_sweep(regular_bars: List[dict], pm_high: float, pm_low: float) -> Optional[dict]:
    """Find first sweep+reclaim. Base logic (no new fixes)."""
    for i, bar in enumerate(regular_bars[:60]):
        # Bull: sweep PM low
        if bar['l'] < pm_low:
            for j in range(i + 1, min(i + MAX_RECLAIM_BARS + 1, len(regular_bars))):
                if regular_bars[j]['c'] > pm_low:
                    return {
                        'direction': 'LONG',
                        'swept_level': pm_low,
                        'sweep_idx': i,
                        'reclaim_idx': j,
                        'reclaim_bar': regular_bars[j],
                        'entry_price': regular_bars[j]['o'],
                        'entry_time': regular_bars[j]['time'],
                        'target_pm': pm_high,
                        'bar_idx': j,
                    }
            continue
        # Bear: sweep PM high
        if bar['h'] > pm_high:
            for j in range(i + 1, min(i + MAX_RECLAIM_BARS + 1, len(regular_bars))):
                if regular_bars[j]['c'] < pm_high:
                    return {
                        'direction': 'SHORT',
                        'swept_level': pm_high,
                        'sweep_idx': i,
                        'reclaim_idx': j,
                        'reclaim_bar': regular_bars[j],
                        'entry_price': regular_bars[j]['o'],
                        'entry_time': regular_bars[j]['time'],
                        'target_pm': pm_low,
                        'bar_idx': j,
                    }
            continue
    return None


# ── FIX 1: Opening Flush Detection ──

def is_opening_flush(regular_bars: List[dict]) -> bool:
    """True if first 3 bars are all red (close < open)."""
    if len(regular_bars) < 3:
        return False
    return all(b['c'] < b['o'] for b in regular_bars[:3])


# ── FIX 2: Reclaim Body Quality ──

def passes_body_quality(reclaim_bar: dict, direction: str) -> bool:
    """
    Body must be >= 30% of range.
    Bull reclaim → green bar required.
    Bear reclaim → red bar required.
    """
    bar_body = reclaim_bar['c'] - reclaim_bar['o']
    bar_range = reclaim_bar['h'] - reclaim_bar['l']
    if direction == 'LONG':
        if bar_body <= 0:
            return False
        if bar_range > 0 and bar_body < bar_range * 0.30:
            return False
    else:  # SHORT
        if bar_body >= 0:
            return False
        if bar_range > 0 and abs(bar_body) < bar_range * 0.30:
            return False
    return True


# ── FIX 3: Level Fatigue ──

class LevelFatigueTracker:
    def __init__(self):
        self.reclaim_counts: Dict[float, int] = {}  # level → count

    def is_fatigued(self, level: float, threshold: float = 0.10) -> bool:
        for lv, cnt in self.reclaim_counts.items():
            if abs(lv - level) < threshold and cnt >= 2:
                return True
        return False

    def record_reclaim(self, level: float):
        for lv in list(self.reclaim_counts.keys()):
            if abs(lv - level) < 0.10:
                self.reclaim_counts[lv] += 1
                return
        self.reclaim_counts[level] = 1


# ── TRADE SIMULATION ──

def simulate_option_trade(option_bars: Optional[List[dict]], entry_time: str,
                           position_size: float) -> dict:
    result = {'entry_price': None, 'exit_price': None, 'exit_reason': None,
              'pnl': 0, 'pnl_pct': 0, 'max_gain_pct': 0}
    if not option_bars:
        result['exit_reason'] = 'no_data'
        return result

    entry_idx = 0
    for i, bar in enumerate(option_bars):
        if bar['time'] >= entry_time:
            entry_idx = i
            break

    entry_price = option_bars[entry_idx]['o']
    result['entry_price'] = entry_price
    max_gain_pct = 0
    trailing_stop_pct = None

    for bar in option_bars[entry_idx:]:
        high_pct = (bar['h'] - entry_price) / entry_price * 100
        low_pct  = (bar['l'] - entry_price) / entry_price * 100

        if high_pct > max_gain_pct:
            max_gain_pct = high_pct
            result['max_gain_pct'] = max_gain_pct

        if low_pct <= MAX_LOSS_PCT:
            result['exit_price'] = entry_price * (1 + MAX_LOSS_PCT / 100)
            result['exit_reason'] = f'max_loss_{abs(int(MAX_LOSS_PCT))}'
            result['pnl_pct'] = MAX_LOSS_PCT
            result['pnl'] = position_size * (MAX_LOSS_PCT / 100)
            return result

        if max_gain_pct >= TRAIL_TRIGGER_50:
            trailing_stop_pct = TRAIL_STOP_50
        elif max_gain_pct >= TRAIL_TRIGGER_30:
            trailing_stop_pct = TRAIL_STOP_30

        if trailing_stop_pct is not None and low_pct <= trailing_stop_pct:
            result['exit_price'] = entry_price * (1 + trailing_stop_pct / 100)
            result['exit_reason'] = f'TRAIL_{trailing_stop_pct}'
            result['pnl_pct'] = trailing_stop_pct
            result['pnl'] = position_size * (trailing_stop_pct / 100)
            return result

    exit_price = option_bars[-1]['c']
    result['exit_price'] = exit_price
    result['exit_reason'] = 'EOD'
    result['pnl_pct'] = (exit_price - entry_price) / entry_price * 100
    result['pnl'] = position_size * (result['pnl_pct'] / 100)
    return result


# ── SINGLE DAY ANALYSIS ──

def analyze_day_base(symbol: str, date: str) -> Optional[dict]:
    """Original logic: no new fixes."""
    minute_data = fetch_minute_bars(symbol, date)
    regular = minute_data['regular']
    pm_bars = minute_data['premarket']

    if len(regular) < 10 or len(pm_bars) < 5:
        return None

    pm_high, pm_low = get_premarket_levels(pm_bars)
    if not pm_high or not pm_low:
        return None
    if pm_high - pm_low < 3.0:
        return None

    setup = find_first_sweep(regular, pm_high, pm_low)
    if not setup:
        return None

    return _build_result(symbol, date, setup, pm_high, pm_low, regular)


def analyze_day_v2(symbol: str, date: str, fatigue: LevelFatigueTracker,
                   fix1: bool = True, fix2: bool = True, fix3: bool = True) -> Optional[dict]:
    """V2 logic with all 3 fixes applied."""
    minute_data = fetch_minute_bars(symbol, date)
    regular = minute_data['regular']
    pm_bars = minute_data['premarket']

    if len(regular) < 10 or len(pm_bars) < 5:
        return None

    pm_high, pm_low = get_premarket_levels(pm_bars)
    if not pm_high or not pm_low:
        return None
    if pm_high - pm_low < 3.0:
        return None

    setup = find_first_sweep(regular, pm_high, pm_low)
    if not setup:
        return None

    # FIX 1: Opening Flush
    if fix1 and setup['direction'] == 'LONG' and setup['bar_idx'] < 30:
        if is_opening_flush(regular):
            return {'date': date, 'filtered_by': 'FIX1_flush', 'direction': setup['direction']}

    # FIX 2: Body Quality
    if fix2 and not passes_body_quality(setup['reclaim_bar'], setup['direction']):
        return {'date': date, 'filtered_by': 'FIX2_wick', 'direction': setup['direction']}

    # FIX 3: Level Fatigue
    if fix3 and fatigue.is_fatigued(setup['swept_level']):
        return {'date': date, 'filtered_by': 'FIX3_fatigue', 'direction': setup['direction']}

    # Record this reclaim for fatigue tracking
    if fix3:
        fatigue.record_reclaim(setup['swept_level'])

    return _build_result(symbol, date, setup, pm_high, pm_low, regular)


def _build_result(symbol: str, date: str, setup: dict,
                  pm_high: float, pm_low: float, regular: list) -> dict:
    """Shared result builder: fetch options + simulate."""
    if setup['direction'] == 'LONG':
        strike_0dte = round(setup['entry_price'] + OTM_OFFSET)
        strike_1dte = strike_0dte
        opt_type = 'call'
        target_0dte = regular[0]['o'] if regular[0]['o'] > setup['entry_price'] else pm_high
        target_1dte = pm_high
    else:
        strike_0dte = round(setup['entry_price'] - OTM_OFFSET)
        strike_1dte = strike_0dte
        opt_type = 'put'
        target_0dte = regular[0]['o'] if regular[0]['o'] < setup['entry_price'] else pm_low
        target_1dte = pm_low

    opt_0dte = get_option_bars(symbol, date, strike_0dte, opt_type, dte=0)
    opt_1dte = get_option_bars(symbol, date, strike_1dte, opt_type, dte=1)

    trade_0dte = simulate_option_trade(opt_0dte, setup['entry_time'], POSITION_SIZE * SPLIT_0DTE)
    trade_1dte = simulate_option_trade(opt_1dte, setup['entry_time'], POSITION_SIZE * SPLIT_1DTE)
    combined_pnl = trade_0dte['pnl'] + trade_1dte['pnl']

    return {
        'date': date,
        'direction': setup['direction'],
        'entry_price': setup['entry_price'],
        'entry_time': setup['entry_time'],
        'pm_high': pm_high,
        'pm_low': pm_low,
        'swept_level': setup['swept_level'],
        '0dte_result': trade_0dte,
        '1dte_result': trade_1dte,
        'combined_pnl': combined_pnl,
        'filtered_by': None,
    }


# ── SUMMARY PRINTER ──

def summarize(label: str, results: list, filtered: list):
    trades = [r for r in results if r.get('filtered_by') is None]
    wins   = [r for r in trades if r.get('combined_pnl', 0) > 0]
    losses = [r for r in trades if r.get('combined_pnl', 0) <= 0]
    total_pnl = sum(r['combined_pnl'] for r in trades)

    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    print(f"  Trading days with setup : {len(trades)}")
    print(f"  Wins                    : {len(wins)}")
    print(f"  Losses                  : {len(losses)}")
    wr = len(wins) / len(trades) * 100 if trades else 0
    print(f"  Win Rate                : {wr:.1f}%")
    print(f"  Total P&L               : ${total_pnl:+,.0f}")
    base_capital = 2000  # approx based on position sizing
    ret_pct = (total_pnl / base_capital) * 100 if base_capital else 0
    print(f"  Approx Return           : {ret_pct:+.0f}%")

    if filtered:
        f1 = sum(1 for f in filtered if f.get('filtered_by') == 'FIX1_flush')
        f2 = sum(1 for f in filtered if f.get('filtered_by') == 'FIX2_wick')
        f3 = sum(1 for f in filtered if f.get('filtered_by') == 'FIX3_fatigue')
        print(f"  Filtered by FIX1 (flush): {f1}")
        print(f"  Filtered by FIX2 (wick) : {f2}")
        print(f"  Filtered by FIX3 (tired): {f3}")

    for r in trades:
        pnl = r.get('combined_pnl', 0)
        emoji = "✅" if pnl > 0 else "❌"
        d0 = r.get('0dte_result', {})
        d1 = r.get('1dte_result', {})
        print(f"  {emoji} {r['date']} {r['direction']:5s} | "
              f"0DTE:{d0.get('exit_reason','?')} ({d0.get('pnl_pct',0):+.0f}%) "
              f"1DTE:{d1.get('exit_reason','?')} ({d1.get('pnl_pct',0):+.0f}%) "
              f"| P&L:${pnl:+.0f}")

    return {
        'label': label,
        'trades': len(trades),
        'wins': len(wins),
        'losses': len(losses),
        'win_rate': wr,
        'total_pnl': total_pnl,
    }


# ── MAIN ──

def run():
    print(f"\n{'='*60}")
    print(f"  MERIDIAN V2 BACKTEST — 3 WEEKS")
    print(f"  {START_DATE} → {END_DATE}  |  {SYMBOL}")
    print(f"{'='*60}")

    # Get trading days in range
    daily_bars = fetch_daily_bars(SYMBOL, START_DATE, END_DATE)
    if not daily_bars:
        print("ERROR: No daily bars returned from Polygon")
        return

    dates = [b['date'] for b in daily_bars
             if datetime.strptime(b['date'], '%Y-%m-%d').weekday() < 5]
    print(f"  Trading days to scan: {len(dates)}")

    # ── BASELINE (no new fixes) ──
    base_results = []
    print(f"\n--- BASELINE (original logic) ---")
    for date in dates:
        print(f"  {date}...", end=" ", flush=True)
        r = analyze_day_base(SYMBOL, date)
        if r:
            pnl = r.get('combined_pnl', 0)
            print(f"{'✅' if pnl > 0 else '❌'} {r['direction']} ${pnl:+.0f}")
            base_results.append(r)
        else:
            print("no setup")
        time.sleep(0.2)

    # ── V2 (all 3 fixes) ──
    v2_all = []
    v2_filtered = []
    fatigue = LevelFatigueTracker()
    print(f"\n--- V2: ALL 3 FIXES ---")
    for date in dates:
        print(f"  {date}...", end=" ", flush=True)
        r = analyze_day_v2(SYMBOL, date, fatigue, fix1=True, fix2=True, fix3=True)
        if r:
            fb = r.get('filtered_by')
            if fb:
                print(f"🚫 FILTERED ({fb})")
                v2_filtered.append(r)
            else:
                pnl = r.get('combined_pnl', 0)
                print(f"{'✅' if pnl > 0 else '❌'} {r['direction']} ${pnl:+.0f}")
                v2_all.append(r)
        else:
            print("no setup")
        time.sleep(0.2)

    # ── SUMMARIES ──
    base_summary = summarize("BASELINE (no new filters)", base_results, [])
    v2_summary   = summarize("V2: ALL 3 FIXES APPLIED",   v2_all, v2_filtered)

    # ── COMPARISON ──
    print(f"\n{'='*60}")
    print("  COMPARISON: BASELINE vs V2")
    print(f"{'='*60}")
    print(f"  {'Metric':<22} {'BASELINE':>12} {'V2 (fixed)':>12}")
    print(f"  {'-'*46}")
    print(f"  {'Trades':<22} {base_summary['trades']:>12} {v2_summary['trades']:>12}")
    print(f"  {'Win Rate':<22} {base_summary['win_rate']:>11.1f}% {v2_summary['win_rate']:>11.1f}%")
    print(f"  {'Total P&L':<22} ${base_summary['total_pnl']:>10,.0f} ${v2_summary['total_pnl']:>10,.0f}")
    print(f"  {'Filtered (total)':<22} {'0':>12} {len(v2_filtered):>12}")

    # Filter breakdown
    if v2_filtered:
        f1 = sum(1 for f in v2_filtered if f.get('filtered_by') == 'FIX1_flush')
        f2 = sum(1 for f in v2_filtered if f.get('filtered_by') == 'FIX2_wick')
        f3 = sum(1 for f in v2_filtered if f.get('filtered_by') == 'FIX3_fatigue')
        print(f"    FIX1 Opening Flush    : {f1} trades skipped")
        print(f"    FIX2 Wick Reclaim     : {f2} trades skipped")
        print(f"    FIX3 Level Fatigue    : {f3} trades skipped")

    # ── Save results ──
    out = {
        'run_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'period': f"{START_DATE} to {END_DATE}",
        'symbol': SYMBOL,
        'baseline': base_summary,
        'v2': v2_summary,
        'filtered_count': len(v2_filtered),
        'filtered_breakdown': {
            'FIX1_flush': sum(1 for f in v2_filtered if f.get('filtered_by') == 'FIX1_flush'),
            'FIX2_wick':  sum(1 for f in v2_filtered if f.get('filtered_by') == 'FIX2_wick'),
            'FIX3_fatigue': sum(1 for f in v2_filtered if f.get('filtered_by') == 'FIX3_fatigue'),
        },
        'baseline_trades': [{'date': r['date'], 'direction': r['direction'],
                              'pnl': r['combined_pnl'],
                              '0dte': r['0dte_result']['exit_reason'],
                              '1dte': r['1dte_result']['exit_reason']}
                             for r in base_results],
        'v2_trades': [{'date': r['date'], 'direction': r.get('direction','?'),
                       'pnl': r.get('combined_pnl', 0),
                       'filtered_by': r.get('filtered_by')}
                      for r in v2_all + v2_filtered],
    }
    out_path = '/Users/atlasbuilds/clawd/meridian-trader/meridian_backtest_v2_results.json'
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\n  Results saved → {out_path}")
    return out


if __name__ == "__main__":
    run()
