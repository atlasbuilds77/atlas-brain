#!/usr/bin/env python3
"""
MERIDIAN V2 BACKTEST — ALL 4 FIXES (20% body quality)
======================================================
Runs 4 columns for comparison:
  BASELINE   — no filters
  V2 (30%)   — FIX1+FIX2(30%)+FIX3    [previous result for reference]
  V2 (20%)   — FIX1+FIX2(20%)+FIX3    [already confirmed matches baseline]
  V2 (20%+FIX4) — all 4 fixes, flush-day window extends to bar 90 (11:00 ET)

FIX1: Opening Flush — block LONG signals bars 0-29 if first 3 bars all red
FIX2: Body Quality  — body >= 20% of range
FIX3: Level Fatigue — skip levels reclaimed 2+ times this session
FIX4: Window Ext.   — flush days scan to bar 90 (11:00 ET); normal days bar 60 (10:30 ET)
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

POSITION_SIZE   = 1000
SPLIT_0DTE      = 0.80
SPLIT_1DTE      = 0.20
OTM_OFFSET      = 3.0
MAX_LOSS_PCT    = -50
TRAIL_TRIGGER_30 = 30
TRAIL_STOP_30   = 15
TRAIL_TRIGGER_50 = 50
TRAIL_STOP_50   = 30
MAX_RECLAIM_BARS = 5

START_DATE = "2026-01-27"
END_DATE   = "2026-02-17"
SYMBOL     = "QQQ"

NORMAL_WINDOW = 60   # bars 0-59  → 9:30–10:30 ET
FLUSH_WINDOW  = 90   # bars 0-89  → 9:30–11:00 ET (FIX4 extension)
BODY_Q_PCT    = 0.20 # FIX2 threshold (20%)


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


# ── SWEEP DETECTION ──

def find_first_sweep(regular_bars: List[dict], pm_high: float, pm_low: float,
                     window: int = NORMAL_WINDOW) -> Optional[dict]:
    """Find first sweep+reclaim within `window` bars."""
    for i, bar in enumerate(regular_bars[:window]):
        # Bull: sweep PM low, then reclaim
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
        # Bear: sweep PM high, then reclaim
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

def passes_body_quality(reclaim_bar: dict, direction: str, threshold: float = BODY_Q_PCT) -> bool:
    """Body must be >= threshold% of range. Bull=green bar, Bear=red bar."""
    bar_body  = reclaim_bar['c'] - reclaim_bar['o']
    bar_range = reclaim_bar['h'] - reclaim_bar['l']
    if direction == 'LONG':
        if bar_body <= 0:
            return False
        if bar_range > 0 and bar_body < bar_range * threshold:
            return False
    else:
        if bar_body >= 0:
            return False
        if bar_range > 0 and abs(bar_body) < bar_range * threshold:
            return False
    return True


# ── FIX 3: Level Fatigue ──

class LevelFatigueTracker:
    def __init__(self):
        self.reclaim_counts: Dict[float, int] = {}

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
    """Original logic: no filters, window=60 bars."""
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

    setup = find_first_sweep(regular, pm_high, pm_low, window=NORMAL_WINDOW)
    if not setup:
        return None

    return _build_result(symbol, date, setup, pm_high, pm_low)


def analyze_day_v2(symbol: str, date: str, fatigue: LevelFatigueTracker,
                   fix1: bool = True, fix2: bool = True, fix3: bool = True,
                   fix4: bool = False, body_q_pct: float = BODY_Q_PCT) -> Optional[dict]:
    """V2 logic. fix4=True enables window extension on flush days."""
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

    # FIX4: determine search window
    flush_day = is_opening_flush(regular)
    if fix4 and flush_day:
        search_window = FLUSH_WINDOW
        window_note = "EXTENDED (flush day)"
    else:
        search_window = NORMAL_WINDOW
        window_note = "normal"

    setup = find_first_sweep(regular, pm_high, pm_low, window=search_window)
    if not setup:
        return None

    # FIX1: Opening Flush — block LONG signals bars 0-29 on flush days
    if fix1 and setup['direction'] == 'LONG' and setup['bar_idx'] < 30 and flush_day:
        return {'date': date, 'filtered_by': 'FIX1_flush', 'direction': setup['direction'],
                'window': window_note}

    # FIX2: Body Quality
    if fix2 and not passes_body_quality(setup['reclaim_bar'], setup['direction'], threshold=body_q_pct):
        return {'date': date, 'filtered_by': 'FIX2_wick', 'direction': setup['direction'],
                'window': window_note}

    # FIX3: Level Fatigue
    if fix3 and fatigue.is_fatigued(setup['swept_level']):
        return {'date': date, 'filtered_by': 'FIX3_fatigue', 'direction': setup['direction'],
                'window': window_note}

    # Record this reclaim for fatigue tracking
    if fix3:
        fatigue.record_reclaim(setup['swept_level'])

    result = _build_result(symbol, date, setup, pm_high, pm_low)
    result['window_note'] = window_note
    result['flush_day'] = flush_day
    return result


def _build_result(symbol: str, date: str, setup: dict,
                  pm_high: float, pm_low: float) -> dict:
    """Shared result builder."""
    if setup['direction'] == 'LONG':
        strike_0dte = round(setup['entry_price'] + OTM_OFFSET)
        strike_1dte = strike_0dte
        opt_type = 'call'
    else:
        strike_0dte = round(setup['entry_price'] - OTM_OFFSET)
        strike_1dte = strike_0dte
        opt_type = 'put'

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
        'bar_idx': setup['bar_idx'],
        'pm_high': pm_high,
        'pm_low': pm_low,
        'swept_level': setup['swept_level'],
        '0dte_result': trade_0dte,
        '1dte_result': trade_1dte,
        'combined_pnl': combined_pnl,
        'filtered_by': None,
        'window_note': 'normal',
        'flush_day': False,
    }


# ── SUMMARY ──

def summarize(label: str, results: list, filtered: list) -> dict:
    trades = [r for r in results if r.get('filtered_by') is None]
    wins   = [r for r in trades if r.get('combined_pnl', 0) > 0]
    losses = [r for r in trades if r.get('combined_pnl', 0) <= 0]
    total_pnl = sum(r['combined_pnl'] for r in trades)
    wr = len(wins) / len(trades) * 100 if trades else 0

    print(f"\n{'='*65}")
    print(f"  {label}")
    print(f"{'='*65}")
    print(f"  Trades    : {len(trades)}")
    print(f"  Wins      : {len(wins)}")
    print(f"  Losses    : {len(losses)}")
    print(f"  Win Rate  : {wr:.1f}%")
    print(f"  Total P&L : ${total_pnl:+,.0f}")
    if filtered:
        f1 = sum(1 for f in filtered if f.get('filtered_by') == 'FIX1_flush')
        f2 = sum(1 for f in filtered if f.get('filtered_by') == 'FIX2_wick')
        f3 = sum(1 for f in filtered if f.get('filtered_by') == 'FIX3_fatigue')
        print(f"  Filtered  : {len(filtered)} total (FIX1={f1}, FIX2={f2}, FIX3={f3})")
    for r in trades:
        pnl = r.get('combined_pnl', 0)
        emoji = "✅" if pnl > 0 else "❌"
        d0 = r.get('0dte_result', {})
        d1 = r.get('1dte_result', {})
        wn = r.get('window_note', '')
        fd = "🔥flush" if r.get('flush_day') else ""
        print(f"  {emoji} {r['date']} {r['direction']:5s} bar={r.get('bar_idx','?'):2} {fd} "
              f"| 0DTE:{d0.get('exit_reason','?')} ({d0.get('pnl_pct',0):+.0f}%) "
              f"1DTE:{d1.get('exit_reason','?')} ({d1.get('pnl_pct',0):+.0f}%) "
              f"| P&L:${pnl:+.0f}")

    return {
        'label': label,
        'trades': len(trades),
        'wins': len(wins),
        'losses': len(losses),
        'win_rate': wr,
        'total_pnl': total_pnl,
        'filtered': len(filtered),
    }


# ── MAIN ──

def run():
    print(f"\n{'='*65}")
    print(f"  MERIDIAN V2 — ALL 4 FIXES BACKTEST")
    print(f"  {START_DATE} → {END_DATE}  |  {SYMBOL}")
    print(f"  Body quality threshold : {int(BODY_Q_PCT*100)}%")
    print(f"  Normal window          : bar {NORMAL_WINDOW} (10:30 ET)")
    print(f"  Flush-day window       : bar {FLUSH_WINDOW} (11:00 ET) — FIX4")
    print(f"{'='*65}")

    daily_bars = fetch_daily_bars(SYMBOL, START_DATE, END_DATE)
    if not daily_bars:
        print("ERROR: No daily bars returned from Polygon")
        return

    dates = [b['date'] for b in daily_bars
             if datetime.strptime(b['date'], '%Y-%m-%d').weekday() < 5]
    print(f"  Trading days to scan: {len(dates)}")

    # ── BASELINE ──
    base_results = []
    print(f"\n--- BASELINE (no filters, window=60) ---")
    for date in dates:
        print(f"  {date}...", end=" ", flush=True)
        r = analyze_day_base(SYMBOL, date)
        if r:
            pnl = r.get('combined_pnl', 0)
            print(f"{'✅' if pnl > 0 else '❌'} {r['direction']} bar={r.get('bar_idx','?')} ${pnl:+.0f}")
            base_results.append(r)
        else:
            print("no setup")
        time.sleep(0.2)

    # ── V2 (20%, FIX1+FIX2+FIX3, no FIX4) ──
    v2_results, v2_filtered = [], []
    fatigue2 = LevelFatigueTracker()
    print(f"\n--- V2: FIX1+FIX2(20%)+FIX3 (no window ext.) ---")
    for date in dates:
        print(f"  {date}...", end=" ", flush=True)
        r = analyze_day_v2(SYMBOL, date, fatigue2, fix1=True, fix2=True, fix3=True,
                           fix4=False, body_q_pct=0.20)
        if r:
            fb = r.get('filtered_by')
            if fb:
                print(f"🚫 FILTERED ({fb})")
                v2_filtered.append(r)
            else:
                pnl = r.get('combined_pnl', 0)
                print(f"{'✅' if pnl > 0 else '❌'} {r['direction']} bar={r.get('bar_idx','?')} ${pnl:+.0f}")
                v2_results.append(r)
        else:
            print("no setup")
        time.sleep(0.2)

    # ── V2 + FIX4 (20%, all 4 fixes) ──
    v2f4_results, v2f4_filtered = [], []
    fatigue4 = LevelFatigueTracker()
    print(f"\n--- V2+FIX4: ALL 4 FIXES (20% body, flush ext. to bar 90) ---")
    for date in dates:
        print(f"  {date}...", end=" ", flush=True)
        r = analyze_day_v2(SYMBOL, date, fatigue4, fix1=True, fix2=True, fix3=True,
                           fix4=True, body_q_pct=0.20)
        if r:
            fb = r.get('filtered_by')
            if fb:
                print(f"🚫 FILTERED ({fb})")
                v2f4_filtered.append(r)
            else:
                pnl = r.get('combined_pnl', 0)
                fd = "🔥" if r.get('flush_day') else ""
                wn = r.get('window_note', '')
                print(f"{'✅' if pnl > 0 else '❌'} {r['direction']} bar={r.get('bar_idx','?')} {fd} ${pnl:+.0f} [{wn}]")
                v2f4_results.append(r)
        else:
            print("no setup")
        time.sleep(0.2)

    # ── SUMMARIES ──
    base_sum = summarize("BASELINE (no filters)", base_results, [])
    v2_sum   = summarize("V2: FIX1+FIX2(20%)+FIX3", v2_results, v2_filtered)
    v2f4_sum = summarize("V2+FIX4: ALL 4 FIXES", v2f4_results, v2f4_filtered)

    # ── FLUSH DAY DETAILS for FIX4 ──
    flush_days_found = [r for r in v2f4_results if r.get('flush_day')]
    flush_days_new = [r for r in v2f4_results
                      if r.get('flush_day') and r.get('bar_idx', 0) >= NORMAL_WINDOW]

    print(f"\n{'='*65}")
    print(f"  FIX4 — FLUSH DAY ANALYSIS")
    print(f"{'='*65}")
    print(f"  Flush days with trades : {len(flush_days_found)}")
    print(f"  NEW trades (bar 60-90) : {len(flush_days_new)}")
    if flush_days_new:
        for r in flush_days_new:
            pnl = r.get('combined_pnl', 0)
            print(f"  🆕 {r['date']} {r['direction']} bar={r['bar_idx']} ${pnl:+.0f}")
    else:
        print(f"  (No new trades found in the extended window)")

    # ── COMPARISON TABLE ──
    print(f"\n{'='*65}")
    print(f"  COMPARISON TABLE")
    print(f"{'='*65}")
    # Reference columns from prior runs
    ref_30pct = {'trades': 6, 'win_rate': 83.3, 'total_pnl': 327, 'filtered': 1}

    header = f"  {'Metric':<18} {'BASELINE':>10} {'V2 (30%)':>10} {'V2 (20%)':>10} {'V2(20%+FX4)':>12}"
    print(header)
    print(f"  {'-'*62}")
    print(f"  {'Trades':<18} {base_sum['trades']:>10} {ref_30pct['trades']:>10} "
          f"{v2_sum['trades']:>10} {v2f4_sum['trades']:>12}")
    print(f"  {'Win Rate':<18} {base_sum['win_rate']:>9.1f}% {ref_30pct['win_rate']:>9.1f}% "
          f"{v2_sum['win_rate']:>9.1f}% {v2f4_sum['win_rate']:>11.1f}%")
    print(f"  {'Total P&L':<18} ${base_sum['total_pnl']:>+8,.0f} ${ref_30pct['total_pnl']:>+8,.0f} "
          f"${v2_sum['total_pnl']:>+8,.0f} ${v2f4_sum['total_pnl']:>+10,.0f}")
    print(f"  {'Filtered':<18} {'0':>10} {ref_30pct['filtered']:>10} "
          f"{v2_sum['filtered']:>10} {v2f4_sum['filtered']:>12}")
    print(f"  {'New (FIX4)':<18} {'-':>10} {'-':>10} {'-':>10} {len(flush_days_new):>12}")

    # ── Save ──
    out = {
        'run_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'period': f"{START_DATE} to {END_DATE}",
        'symbol': SYMBOL,
        'body_quality_pct': BODY_Q_PCT,
        'normal_window_bars': NORMAL_WINDOW,
        'flush_window_bars': FLUSH_WINDOW,
        'baseline': base_sum,
        'v2_20pct': v2_sum,
        'v2_20pct_fix4': v2f4_sum,
        'fix4_flush_day_trades': len(flush_days_found),
        'fix4_new_trades_in_extension': len(flush_days_new),
        'baseline_trades': [{'date': r['date'], 'direction': r['direction'],
                              'bar_idx': r.get('bar_idx','?'),
                              'pnl': r['combined_pnl'],
                              '0dte': r['0dte_result']['exit_reason'],
                              '1dte': r['1dte_result']['exit_reason']}
                             for r in base_results],
        'v2_20pct_trades': [{'date': r['date'], 'direction': r.get('direction','?'),
                             'bar_idx': r.get('bar_idx','?'),
                             'pnl': r.get('combined_pnl', 0),
                             'filtered_by': r.get('filtered_by')}
                            for r in v2_results + v2_filtered],
        'v2_20pct_fix4_trades': [{'date': r['date'], 'direction': r.get('direction','?'),
                                  'bar_idx': r.get('bar_idx','?'),
                                  'flush_day': r.get('flush_day', False),
                                  'window': r.get('window_note', ''),
                                  'pnl': r.get('combined_pnl', 0),
                                  'filtered_by': r.get('filtered_by')}
                                 for r in v2f4_results + v2f4_filtered],
    }
    out_path = '/Users/atlasbuilds/clawd/meridian-trader/meridian_backtest_v2_results.json'
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\n  Results → {out_path}")
    return out


if __name__ == "__main__":
    run()
