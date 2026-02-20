#!/usr/bin/env python3
"""
TITAN V3 PM BACKTEST - Pre-Market Levels Only
==============================================
The REAL system:
1. Use ONLY pre-market HIGH and LOW as key levels
2. Sweep + 5-min reclaim
3. Entry at bounce
4. Target = opposite PM level
5. Trailing stops + time-based scaling
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time
import pytz

POLYGON_API_KEY = "h7J74V1cd8_4NQpTxwQpudpqXWaIHMhv"
ET = pytz.timezone('US/Eastern')
POSITION_SIZE = 1000

def fetch_minute_bars_polygon(symbol: str, date: str) -> Dict[str, List[dict]]:
    """Fetch 1-minute bars from Polygon."""
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{date}/{date}"
    params = {"apiKey": POLYGON_API_KEY, "limit": 50000}
    
    r = requests.get(url, params=params)
    data = r.json()
    
    if data.get('status') != 'OK' or not data.get('results'):
        return {"premarket": [], "regular": []}
    
    premarket, regular = [], []
    
    for bar in data['results']:
        ts = datetime.fromtimestamp(bar['t'] / 1000, tz=pytz.UTC).astimezone(ET)
        bar_data = {
            'time': ts.strftime('%H:%M'),
            'dt': ts,
            'o': bar['o'], 'h': bar['h'], 'l': bar['l'], 'c': bar['c']
        }
        
        if ts.hour < 9 or (ts.hour == 9 and ts.minute < 30):
            if ts.hour >= 4:
                premarket.append(bar_data)
        elif ts.hour < 16:
            regular.append(bar_data)
    
    return {"premarket": premarket, "regular": regular}


def get_option_bars(symbol: str, date: str, strike: float, opt_type: str) -> Optional[List[dict]]:
    """Get option minute bars."""
    trade_date = datetime.strptime(date, '%Y-%m-%d')
    exp_str = trade_date.strftime('%y%m%d')
    strike_str = f"{int(strike * 1000):08d}"
    opt_char = 'P' if opt_type == 'put' else 'C'
    ticker = f"O:{symbol}{exp_str}{opt_char}{strike_str}"
    
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/minute/{date}/{date}"
    r = requests.get(url, params={"apiKey": POLYGON_API_KEY, "limit": 50000})
    data = r.json()
    
    if data.get('status') != 'OK' or not data.get('results'):
        return None
    
    bars = []
    for bar in data['results']:
        ts = datetime.fromtimestamp(bar['t'] / 1000, tz=pytz.UTC).astimezone(ET)
        bars.append({
            'time': ts.strftime('%H:%M'),
            'o': bar['o'], 'h': bar['h'], 'l': bar['l'], 'c': bar['c']
        })
    return bars


def find_pm_sweep_reclaim(bars: List[dict], pm_level: float, level_type: str) -> Optional[dict]:
    """Find sweep of PM level and reclaim within 5 minutes."""
    
    for i, bar in enumerate(bars):
        # Skip first 2 minutes (noisy open)
        if i < 2:
            continue
        
        swept = False
        if level_type == "low" and bar['l'] < pm_level:
            swept = True
        elif level_type == "high" and bar['h'] > pm_level:
            swept = True
        
        if swept:
            # Look for reclaim within 5 bars
            for j in range(i + 1, min(i + 6, len(bars))):
                reclaimed = False
                if level_type == "low" and bars[j]['c'] > pm_level:
                    reclaimed = True
                elif level_type == "high" and bars[j]['c'] < pm_level:
                    reclaimed = True
                
                if reclaimed:
                    # Find bounce price (entry)
                    if level_type == "low":
                        bounce = min(bars[k]['l'] for k in range(i, j + 1))
                        direction = "LONG"
                    else:
                        bounce = max(bars[k]['h'] for k in range(i, j + 1))
                        direction = "SHORT"
                    
                    return {
                        "sweep_idx": i,
                        "sweep_time": bar['time'],
                        "reclaim_idx": j,
                        "reclaim_time": bars[j]['time'],
                        "bounce_price": bounce,
                        "reclaim_price": bars[j]['c'],
                        "direction": direction
                    }
            # Swept but no reclaim = breakdown, skip
            return None
    
    return None


def simulate_with_trailing(option_bars: List[dict], entry_idx: int, 
                           underlying_bars: List[dict], target: float,
                           direction: str) -> dict:
    """
    SIMPLE TRAILING STOP SYSTEM:
    - Trail from start (don't wait for target)
    - Up 30% → lock +15%
    - Up 50% → lock +30%
    - Up 75% → lock +50%
    - Max loss: -50% (not -80%, too much slippage)
    """
    
    if not option_bars or entry_idx >= len(option_bars):
        return {'pnl': 0, 'exit_reason': 'no_data'}
    
    entry_price = option_bars[entry_idx]['o']
    max_gain = 0
    trailing_stop = None
    
    for i in range(entry_idx, len(option_bars)):
        opt = option_bars[i]
        
        # Current gain/loss
        gain = (opt['h'] - entry_price) / entry_price * 100
        loss = (opt['l'] - entry_price) / entry_price * 100
        
        if gain > max_gain:
            max_gain = gain
            
            # Update trailing stop based on max gain
            if max_gain >= 75:
                trailing_stop = 50
            elif max_gain >= 50:
                trailing_stop = 30
            elif max_gain >= 30:
                trailing_stop = 15
        
        # Check trailing stop FIRST (capture gains)
        if trailing_stop is not None:
            current_gain = (opt['c'] - entry_price) / entry_price * 100
            if current_gain <= trailing_stop:
                return {
                    'pnl': (trailing_stop / 100) * POSITION_SIZE,
                    'pnl_pct': trailing_stop,
                    'exit_reason': f'TRAIL_{trailing_stop}',
                    'max_gain': max_gain
                }
        
        # Check -50% max loss (not -80%, too much slippage on 0DTE)
        if loss <= -50:
            return {
                'pnl': -0.5 * POSITION_SIZE,
                'pnl_pct': -50,
                'exit_reason': 'max_loss_50',
                'max_gain': max_gain
            }
    
    # End of day exit
    final_price = option_bars[-1]['c']
    final_gain = (final_price - entry_price) / entry_price * 100
    
    return {
        'pnl': POSITION_SIZE * (final_gain / 100),
        'pnl_pct': final_gain,
        'exit_reason': 'eod',
        'max_gain': max_gain
    }


def analyze_day(symbol: str, date: str) -> Optional[dict]:
    """Analyze one day using PM levels only."""
    
    data = fetch_minute_bars_polygon(symbol, date)
    pm_bars = data['premarket']
    reg_bars = data['regular']
    
    if not pm_bars or len(reg_bars) < 30:
        return None
    
    # Get PM levels
    pm_high = max(b['h'] for b in pm_bars)
    pm_low = min(b['l'] for b in pm_bars)
    
    # Try PM low sweep first (LONG setup)
    setup = find_pm_sweep_reclaim(reg_bars, pm_low, "low")
    target = pm_high
    
    # If no low sweep, try PM high sweep (SHORT setup)
    if not setup:
        setup = find_pm_sweep_reclaim(reg_bars, pm_high, "high")
        target = pm_low
    
    if not setup:
        return None
    
    direction = setup['direction']
    entry_price = setup['bounce_price']
    entry_idx = setup['reclaim_idx']
    
    # Get option - try ~$2 OTM (closer to money, less gamma risk)
    # Instead of strike AT target, use strike ~$3 from entry
    opt_type = 'call' if direction == "LONG" else 'put'
    if direction == "LONG":
        strike = round(entry_price + 3)  # $3 OTM call
    else:
        strike = round(entry_price - 3)  # $3 OTM put
    
    opt_bars = get_option_bars(symbol, date, strike, opt_type)
    
    if not opt_bars:
        return None
    
    # Find option bar at entry time
    entry_time = reg_bars[entry_idx]['time']
    opt_entry_idx = 0
    for i, ob in enumerate(opt_bars):
        if ob['time'] >= entry_time:
            opt_entry_idx = i
            break
    
    # Simulate
    result = simulate_with_trailing(opt_bars, opt_entry_idx, reg_bars[entry_idx:], 
                                    target, direction)
    
    return {
        'date': date,
        'direction': direction,
        'pm_high': pm_high,
        'pm_low': pm_low,
        'sweep_time': setup['sweep_time'],
        'entry_price': entry_price,
        'target': target,
        'strike': strike,
        'option_type': opt_type,
        **result
    }


def run_backtest(symbol: str, start: str, end: str):
    """Run backtest."""
    
    print(f"\n{'='*80}")
    print(f"TITAN V3 PM LEVELS BACKTEST")
    print(f"Pre-market HIGH/LOW sweeps only")
    print(f"{symbol}: {start} to {end}")
    print(f"{'='*80}\n")
    
    trades = []
    current = datetime.strptime(start, '%Y-%m-%d')
    end_dt = datetime.strptime(end, '%Y-%m-%d')
    
    while current <= end_dt:
        if current.weekday() >= 5:
            current += timedelta(days=1)
            continue
        
        date_str = current.strftime('%Y-%m-%d')
        print(f"{date_str}: ", end="", flush=True)
        
        result = analyze_day(symbol, date_str)
        
        if result:
            trades.append(result)
            pnl = result.get('pnl', 0)
            pnl_pct = result.get('pnl_pct', 0)
            reason = result.get('exit_reason', '?')
            max_g = result.get('max_gain', 0)
            
            status = "✅" if pnl > 0 else "❌"
            print(f"{status} {result['direction']} | PM {result['pm_low']:.0f}-{result['pm_high']:.0f} | "
                  f"${result['strike']}{result['option_type'][0].upper()} | "
                  f"{pnl_pct:+.0f}% (max +{max_g:.0f}%) | ${pnl:+.0f} | {reason}")
        else:
            print("no setup")
        
        current += timedelta(days=1)
        time.sleep(0.15)
    
    # Summary
    print(f"\n{'='*80}")
    print("RESULTS")
    print(f"{'='*80}")
    
    if not trades:
        print("No trades")
        return
    
    wins = [t for t in trades if t.get('pnl', 0) > 0]
    losses = [t for t in trades if t.get('pnl', 0) <= 0]
    
    print(f"Trades: {len(trades)} | Wins: {len(wins)} ({len(wins)/len(trades)*100:.0f}%) | Losses: {len(losses)}")
    
    total = sum(t.get('pnl', 0) for t in trades)
    avg_win = sum(t.get('pnl', 0) for t in wins) / len(wins) if wins else 0
    avg_loss = sum(t.get('pnl', 0) for t in losses) / len(losses) if losses else 0
    
    print(f"Total P&L: ${total:+,.0f} | Avg Win: ${avg_win:+,.0f} | Avg Loss: ${avg_loss:+,.0f}")
    
    reasons = {}
    for t in trades:
        r = t.get('exit_reason', '?')
        reasons[r] = reasons.get(r, 0) + 1
    print(f"Exit reasons: {reasons}")


if __name__ == "__main__":
    run_backtest("QQQ", "2026-01-13", "2026-02-13")
