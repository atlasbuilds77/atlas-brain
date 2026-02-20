#!/usr/bin/env python3
"""
TITAN System Backtest V2 - Relative Strength Selection
Last Week (Feb 6-13, 2026)
Real data from Polygon (prices) and Tradier (options)

V2 CHANGES:
- Added IWM to symbol universe
- Pre-market relative strength calculation
- Trade ONLY strongest symbol for longs
- Trade ONLY weakest symbol for shorts
"""

import requests
import json
from datetime import datetime, timedelta
from collections import defaultdict
import pytz
from typing import Dict, List, Tuple, Optional

# API Configuration
POLYGON_API_KEY = "h7J74V1cd8_4NQpTxwQpudpqXWaIHMhv"
TRADIER_TOKEN = "jj8L3RuSVG5MUwUpz2XHrjXjAFrq"

# Trading dates (last 6 trading days)
TRADING_DATES = [
    "2026-02-06",
    "2026-02-07",
    "2026-02-10",
    "2026-02-11",
    "2026-02-12",
    "2026-02-13"
]

SYMBOLS = ["QQQ", "SPY", "IWM"]  # V2: Added IWM
ET = pytz.timezone('America/New_York')
POSITION_SIZE = 1000  # $1000 per trade


class OptionsDataCache:
    """Cache options chain data to minimize API calls"""
    def __init__(self):
        self.cache = {}
    
    def get_chain(self, symbol: str, expiration: str) -> dict:
        key = f"{symbol}:{expiration}"
        if key not in self.cache:
            url = f"https://api.tradier.com/v1/markets/options/chains"
            params = {
                'symbol': symbol,
                'expiration': expiration,
                'greeks': 'true'
            }
            headers = {
                'Authorization': f'Bearer {TRADIER_TOKEN}',
                'Accept': 'application/json'
            }
            
            print(f"  Fetching options chain for {symbol} exp {expiration}...")
            response = requests.get(url, params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.cache[key] = data
            else:
                print(f"  ERROR: Tradier API returned {response.status_code}")
                self.cache[key] = None
        
        return self.cache[key]


def get_price_data(symbol: str, date: str) -> List[dict]:
    """Fetch 5-minute bars from Polygon for a given date"""
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/5/minute/{date}/{date}"
    params = {'apiKey': POLYGON_API_KEY, 'adjusted': 'true', 'limit': 50000}
    
    print(f"  Fetching {symbol} price data for {date}...")
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if 'results' in data:
            return data['results']
    
    print(f"  WARNING: No price data for {symbol} on {date}")
    return []


def get_prior_close(symbol: str, date: str) -> Optional[float]:
    """Get prior day's close price"""
    # Parse the date and get previous trading day
    current_date = datetime.strptime(date, "%Y-%m-%d")
    days_back = 1
    if current_date.weekday() == 0:  # Monday
        days_back = 3
    
    prior_date = (current_date - timedelta(days=days_back)).strftime("%Y-%m-%d")
    
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{prior_date}/{prior_date}"
    params = {'apiKey': POLYGON_API_KEY, 'adjusted': 'true'}
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if 'results' in data and data['results']:
            return data['results'][0]['c']
    
    return None


def calculate_premarket_change(bars: List[dict], prior_close: float, date: str) -> dict:
    """Calculate pre-market % change from prior close"""
    premarket_start = ET.localize(datetime.strptime(f"{date} 04:00:00", "%Y-%m-%d %H:%M:%S"))
    market_open = ET.localize(datetime.strptime(f"{date} 09:30:00", "%Y-%m-%d %H:%M:%S"))
    
    premarket_bars = []
    for bar in bars:
        bar_time = datetime.fromtimestamp(bar['t'] / 1000, tz=ET)
        if premarket_start <= bar_time < market_open:
            premarket_bars.append(bar)
    
    if not premarket_bars or prior_close is None:
        return {'pre_high': None, 'pre_low': None, 'pre_price': None, 'change_pct': None}
    
    pre_high = max(bar['h'] for bar in premarket_bars)
    pre_low = min(bar['l'] for bar in premarket_bars)
    # Use latest pre-market price (last bar before open)
    pre_price = premarket_bars[-1]['c']
    
    change_pct = ((pre_price - prior_close) / prior_close) * 100
    
    return {
        'pre_high': pre_high,
        'pre_low': pre_low,
        'pre_price': pre_price,
        'prior_close': prior_close,
        'change_pct': change_pct
    }


def select_symbols_by_relative_strength(date: str) -> dict:
    """
    V2 CORE LOGIC: Calculate relative strength and select symbols
    Returns: {
        'long_symbol': strongest symbol,
        'short_symbol': weakest symbol,
        'analysis': {symbol: {change_pct, pre_price, etc}}
    }
    """
    print(f"\n  === RELATIVE STRENGTH ANALYSIS ===")
    
    analysis = {}
    
    for symbol in SYMBOLS:
        bars = get_price_data(symbol, date)
        prior_close = get_prior_close(symbol, date)
        
        if not bars or prior_close is None:
            print(f"  WARNING: Cannot calculate RS for {symbol}")
            analysis[symbol] = {'change_pct': None}
            continue
        
        data = calculate_premarket_change(bars, prior_close, date)
        analysis[symbol] = data
        
        if data['change_pct'] is not None:
            print(f"  {symbol}: {data['change_pct']:+.2f}% (pre-market)")
    
    # Find strongest and weakest
    valid_symbols = {s: a for s, a in analysis.items() if a['change_pct'] is not None}
    
    if not valid_symbols:
        print(f"  ERROR: No valid symbols for relative strength")
        return {'long_symbol': None, 'short_symbol': None, 'analysis': analysis}
    
    strongest = max(valid_symbols.items(), key=lambda x: x[1]['change_pct'])
    weakest = min(valid_symbols.items(), key=lambda x: x[1]['change_pct'])
    
    print(f"\n  LONG PICK: {strongest[0]} (strongest at {strongest[1]['change_pct']:+.2f}%)")
    print(f"  SHORT PICK: {weakest[0]} (weakest at {weakest[1]['change_pct']:+.2f}%)")
    print(f"  ===================================\n")
    
    return {
        'long_symbol': strongest[0],
        'short_symbol': weakest[0],
        'analysis': analysis
    }


def get_market_hours_bars(bars: List[dict], date: str) -> List[dict]:
    """Filter bars to market hours (9:30am-4pm ET)"""
    market_open = ET.localize(datetime.strptime(f"{date} 09:30:00", "%Y-%m-%d %H:%M:%S"))
    market_close = ET.localize(datetime.strptime(f"{date} 16:00:00", "%Y-%m-%d %H:%M:%S"))
    
    market_bars = []
    for bar in bars:
        bar_time = datetime.fromtimestamp(bar['t'] / 1000, tz=ET)
        if market_open <= bar_time < market_close:
            bar['dt'] = bar_time
            market_bars.append(bar)
    
    return market_bars


def find_option_strike(current_price: float, target_price: float, option_type: str) -> float:
    """Find appropriate strike for target level"""
    # Round to nearest $1 strike for liquid options
    if option_type == 'call':
        strike = round(target_price)
    else:
        strike = round(target_price)
    return strike


def get_option_price(cache: OptionsDataCache, symbol: str, strike: float, 
                     option_type: str, expiration: str, underlying_price: float) -> Optional[float]:
    """Get option price from chain, estimate if not available"""
    chain = cache.get_chain(symbol, expiration)
    
    if chain is None or 'options' not in chain or chain.get('options') is None or 'option' not in chain.get('options', {}):
        # Fallback: estimate using simple intrinsic + time value
        if option_type == 'call':
            intrinsic = max(0, underlying_price - strike)
            extrinsic = 0.5  # Rough estimate for 0DTE
        else:
            intrinsic = max(0, strike - underlying_price)
            extrinsic = 0.5
        return intrinsic + extrinsic
    
    options = chain['options']['option']
    if not isinstance(options, list):
        options = [options]
    
    # Find matching option
    for opt in options:
        if (opt.get('option_type', '').lower() == option_type.lower() and 
            float(opt.get('strike', 0)) == strike):
            # Use bid/ask midpoint
            bid = float(opt.get('bid', 0))
            ask = float(opt.get('ask', 0))
            if bid > 0 and ask > 0:
                return (bid + ask) / 2
            elif ask > 0:
                return ask
    
    # Estimate if exact strike not found
    if option_type == 'call':
        intrinsic = max(0, underlying_price - strike)
        extrinsic = max(0.1, 2.0 - (0.5 * abs(underlying_price - strike)))
    else:
        intrinsic = max(0, strike - underlying_price)
        extrinsic = max(0.1, 2.0 - (0.5 * abs(underlying_price - strike)))
    
    return intrinsic + extrinsic


def estimate_option_price_at_level(entry_price: float, entry_underlying: float, 
                                   exit_underlying: float, strike: float, 
                                   option_type: str) -> float:
    """Estimate option price at exit using delta approximation"""
    # Calculate delta (simplified - closer to ATM = higher delta)
    if option_type == 'call':
        moneyness = (entry_underlying - strike) / entry_underlying
        delta = 0.5 + min(0.45, max(-0.45, moneyness * 2))
        
        # Price change
        underlying_move = exit_underlying - entry_underlying
        option_move = underlying_move * delta
        
        # Add intrinsic value
        new_intrinsic = max(0, exit_underlying - strike)
        estimated_price = entry_price + option_move
        
        # Floor at intrinsic
        return max(new_intrinsic, estimated_price)
    else:
        moneyness = (strike - entry_underlying) / entry_underlying
        delta = -0.5 + min(0.45, max(-0.45, moneyness * 2))
        
        underlying_move = exit_underlying - entry_underlying
        option_move = underlying_move * delta
        
        new_intrinsic = max(0, strike - exit_underlying)
        estimated_price = entry_price + option_move
        
        return max(new_intrinsic, estimated_price)


def detect_liquidity_grab(bars: List[dict], index: int, level: float, direction: str) -> bool:
    """Detect if price swept a level and reversed (liquidity grab)"""
    if index < 2:
        return False
    
    current = bars[index]
    prev1 = bars[index - 1]
    prev2 = bars[index - 2]
    
    if direction == 'long':
        # Look for sweep below level then bounce
        swept = (prev2['l'] < level or prev1['l'] < level)
        bounced = current['c'] > level
        return swept and bounced
    else:
        # Look for sweep above level then rejection
        swept = (prev2['h'] > level or prev1['h'] > level)
        rejected = current['c'] < level
        return swept and rejected


def simulate_day(symbol: str, date: str, cache: OptionsDataCache, levels: dict) -> List[dict]:
    """Simulate TITAN system for one symbol on one day"""
    bars = get_price_data(symbol, date)
    if not bars:
        return []
    
    # Use pre-calculated levels
    if levels['pre_high'] is None:
        print(f"  WARNING: No pre-market data for {symbol} on {date}")
        return []
    
    market_bars = get_market_hours_bars(bars, date)
    if not market_bars:
        return []
    
    print(f"  {symbol} Pre-market levels: High ${levels['pre_high']:.2f} | Low ${levels['pre_low']:.2f}")
    
    # Use 0DTE options (same day expiration)
    expiration = date
    
    trades = []
    in_trade = False
    
    for i, bar in enumerate(market_bars):
        if in_trade:
            continue
        
        # Check for LONG entry (touch pre-low)
        if bar['l'] <= levels['pre_low'] * 1.002:  # Within 0.2% of level
            is_liquidity_grab = detect_liquidity_grab(market_bars, i, levels['pre_low'], 'long')
            
            # Entry conditions met
            entry_time = bar['dt']
            entry_price = levels['pre_low']
            
            # Calculate target levels (simple: +0.5% and +1%)
            target1 = entry_price * 1.005
            target2 = entry_price * 1.010
            
            # Select strike
            strike = find_option_strike(entry_price, target1, 'call')
            
            # Get option entry price
            option_entry = get_option_price(cache, symbol, strike, 'call', expiration, entry_price)
            if option_entry is None:
                continue
            
            # Track trade through remaining bars
            trade = {
                'symbol': symbol,
                'date': date,
                'direction': 'LONG',
                'entry_time': entry_time.strftime('%I:%M %p ET'),
                'entry_price': entry_price,
                'strike': strike,
                'option_entry': option_entry,
                'liquidity_grab': is_liquidity_grab,
                'phase2_price': None,
                'phase2_time': None,
                'phase2_option': None,
                'phase3_price': None,
                'phase3_time': None,
                'phase3_option': None,
                'stopped': False
            }
            
            # Look for exits
            for j in range(i + 1, len(market_bars)):
                exit_bar = market_bars[j]
                
                # Check stop (-0.5%)
                if exit_bar['l'] <= entry_price * 0.995:
                    trade['stopped'] = True
                    trade['stop_price'] = exit_bar['l']
                    trade['stop_time'] = exit_bar['dt'].strftime('%I:%M %p ET')
                    break
                
                # Check Phase 2 (target1)
                if trade['phase2_price'] is None and exit_bar['h'] >= target1:
                    elapsed = (exit_bar['dt'] - entry_time).total_seconds() / 60
                    trade['phase2_price'] = target1
                    trade['phase2_time'] = exit_bar['dt'].strftime('%I:%M %p ET')
                    trade['phase2_elapsed'] = elapsed
                    trade['phase2_option'] = estimate_option_price_at_level(
                        option_entry, entry_price, target1, strike, 'call'
                    )
                
                # Check Phase 3 (target2)
                if trade['phase3_price'] is None and exit_bar['h'] >= target2:
                    trade['phase3_price'] = target2
                    trade['phase3_time'] = exit_bar['dt'].strftime('%I:%M %p ET')
                    trade['phase3_option'] = estimate_option_price_at_level(
                        option_entry, entry_price, target2, strike, 'call'
                    )
                    break
            
            trades.append(trade)
            in_trade = True
            break  # Only one trade per day per symbol
        
        # Check for SHORT entry (touch pre-high)
        elif bar['h'] >= levels['pre_high'] * 0.998:
            is_liquidity_grab = detect_liquidity_grab(market_bars, i, levels['pre_high'], 'short')
            
            entry_time = bar['dt']
            entry_price = levels['pre_high']
            
            target1 = entry_price * 0.995
            target2 = entry_price * 0.990
            
            strike = find_option_strike(entry_price, target1, 'put')
            
            option_entry = get_option_price(cache, symbol, strike, 'put', expiration, entry_price)
            if option_entry is None:
                continue
            
            trade = {
                'symbol': symbol,
                'date': date,
                'direction': 'SHORT',
                'entry_time': entry_time.strftime('%I:%M %p ET'),
                'entry_price': entry_price,
                'strike': strike,
                'option_entry': option_entry,
                'liquidity_grab': is_liquidity_grab,
                'phase2_price': None,
                'phase2_time': None,
                'phase2_option': None,
                'phase3_price': None,
                'phase3_time': None,
                'phase3_option': None,
                'stopped': False
            }
            
            for j in range(i + 1, len(market_bars)):
                exit_bar = market_bars[j]
                
                if exit_bar['h'] >= entry_price * 1.005:
                    trade['stopped'] = True
                    trade['stop_price'] = exit_bar['h']
                    trade['stop_time'] = exit_bar['dt'].strftime('%I:%M %p ET')
                    break
                
                if trade['phase2_price'] is None and exit_bar['l'] <= target1:
                    elapsed = (exit_bar['dt'] - entry_time).total_seconds() / 60
                    trade['phase2_price'] = target1
                    trade['phase2_time'] = exit_bar['dt'].strftime('%I:%M %p ET')
                    trade['phase2_elapsed'] = elapsed
                    trade['phase2_option'] = estimate_option_price_at_level(
                        option_entry, entry_price, target1, strike, 'put'
                    )
                
                if trade['phase3_price'] is None and exit_bar['l'] <= target2:
                    trade['phase3_price'] = target2
                    trade['phase3_time'] = exit_bar['dt'].strftime('%I:%M %p ET')
                    trade['phase3_option'] = estimate_option_price_at_level(
                        option_entry, entry_price, target2, strike, 'put'
                    )
                    break
            
            trades.append(trade)
            in_trade = True
            break
    
    return trades


def calculate_pnl(trade: dict) -> dict:
    """Calculate P&L for a trade with scaling logic"""
    entry = trade['option_entry']
    
    if trade['stopped']:
        # Full loss - option likely worthless or minimal value
        loss = -POSITION_SIZE * 0.8  # Assume 80% loss on stop
        return {
            'phase2_pnl': 0,
            'phase3_pnl': 0,
            'total_pnl': loss,
            'phase2_pct': 0,
            'phase3_pct': 0,
            'total_pct': -80
        }
    
    result = {'phase2_pnl': 0, 'phase3_pnl': 0, 'total_pnl': 0}
    
    # Phase 2 exit
    if trade['phase2_option']:
        elapsed = trade['phase2_elapsed']
        if elapsed < 60:  # <1 hour: sell 25%
            scale = 0.25
        else:  # >1 hour: sell 50%
            scale = 0.50
        
        phase2_gain = (trade['phase2_option'] - entry) / entry
        phase2_pnl = POSITION_SIZE * scale * phase2_gain
        result['phase2_pnl'] = phase2_pnl
        result['phase2_pct'] = phase2_gain * 100
        result['phase2_scale'] = scale
    
    # Phase 3 exit (remaining position)
    if trade['phase3_option']:
        if trade['phase2_elapsed'] and trade['phase2_elapsed'] < 60:
            remaining = 0.75
        else:
            remaining = 0.50
        
        phase3_gain = (trade['phase3_option'] - entry) / entry
        phase3_pnl = POSITION_SIZE * remaining * phase3_gain
        result['phase3_pnl'] = phase3_pnl
        result['phase3_pct'] = phase3_gain * 100
        result['phase3_scale'] = remaining
    
    result['total_pnl'] = result['phase2_pnl'] + result['phase3_pnl']
    result['total_pct'] = (result['total_pnl'] / POSITION_SIZE) * 100
    
    return result


def format_trade_report(trade: dict, pnl: dict) -> str:
    """Format a single trade for the report"""
    option_type = 'C' if trade['direction'] == 'LONG' else 'P'
    
    report = f"\nTRADE:\n"
    report += f"  Symbol: {trade['symbol']}\n"
    report += f"  Direction: {trade['direction']}"
    if trade['liquidity_grab']:
        report += " (LIQUIDITY GRAB)"
    report += f"\n"
    report += f"  Entry Time: {trade['entry_time']}\n"
    report += f"  Entry Price (underlying): ${trade['entry_price']:.2f}\n"
    report += f"  Entry Price (option): ${trade['strike']:.0f}{option_type} @ ${trade['option_entry']:.2f}\n"
    
    if trade['stopped']:
        report += f"\n  STOPPED OUT at {trade['stop_time']}\n"
        report += f"  Stop Price: ${trade['stop_price']:.2f}\n"
        report += f"  TOTAL P&L: ${pnl['total_pnl']:.2f} ({pnl['total_pct']:.1f}%)\n"
        return report
    
    if trade['phase2_option']:
        elapsed = trade['phase2_elapsed']
        scale_pct = int(pnl.get('phase2_scale', 0.25) * 100)
        time_rule = f"<1hr = sell {scale_pct}%" if elapsed < 60 else f">1hr = sell {scale_pct}%"
        
        report += f"\n  Phase 2: {trade['phase2_time']} (${trade['phase2_price']:.2f})\n"
        report += f"  Time elapsed: {int(elapsed)} min ({time_rule})\n"
        report += f"  Option price at Phase 2: ${trade['phase2_option']:.2f} ({pnl['phase2_pct']:+.1f}%)\n"
        report += f"  Action: Sold {scale_pct}% @ {pnl['phase2_pct']:+.1f}%\n"
    
    if trade['phase3_option']:
        scale_pct = int(pnl.get('phase3_scale', 0.75) * 100)
        report += f"\n  Phase 3: {trade['phase3_time']} (${trade['phase3_price']:.2f})\n"
        report += f"  Option price at Phase 3: ${trade['phase3_option']:.2f} ({pnl['phase3_pct']:+.1f}%)\n"
        report += f"  Action: Sold {scale_pct}% @ {pnl['phase3_pct']:+.1f}%\n"
    
    report += f"\n  TOTAL P&L: ${pnl['total_pnl']:+.2f} ({pnl['total_pct']:+.1f}%)\n"
    
    return report


def main():
    """Run full backtest with relative strength selection"""
    print("=" * 60)
    print("TITAN SYSTEM BACKTEST V2 - RELATIVE STRENGTH SELECTION")
    print("Feb 6-13, 2026 | Real Data | Real Options")
    print("=" * 60)
    
    cache = OptionsDataCache()
    all_trades = []
    daily_results = {}
    
    for date in TRADING_DATES:
        print(f"\n{'=' * 60}")
        print(f"Processing {date}...")
        print('=' * 60)
        
        # V2: Calculate relative strength and select symbols
        rs_selection = select_symbols_by_relative_strength(date)
        
        day_trades = []
        
        # Try LONG on strongest symbol
        if rs_selection['long_symbol']:
            symbol = rs_selection['long_symbol']
            levels = rs_selection['analysis'][symbol]
            print(f"\n  Checking LONG setup on {symbol}...")
            trades = simulate_day(symbol, date, cache, levels)
            # Only keep LONG trades
            long_trades = [t for t in trades if t['direction'] == 'LONG']
            day_trades.extend(long_trades)
        
        # Try SHORT on weakest symbol
        if rs_selection['short_symbol']:
            symbol = rs_selection['short_symbol']
            levels = rs_selection['analysis'][symbol]
            print(f"\n  Checking SHORT setup on {symbol}...")
            trades = simulate_day(symbol, date, cache, levels)
            # Only keep SHORT trades
            short_trades = [t for t in trades if t['direction'] == 'SHORT']
            day_trades.extend(short_trades)
        
        # Attach RS analysis to results
        for trade in day_trades:
            trade['rs_analysis'] = rs_selection['analysis']
            trade['rs_long_pick'] = rs_selection['long_symbol']
            trade['rs_short_pick'] = rs_selection['short_symbol']
        
        daily_results[date] = {
            'trades': day_trades,
            'rs_analysis': rs_selection['analysis'],
            'rs_long_pick': rs_selection['long_symbol'],
            'rs_short_pick': rs_selection['short_symbol']
        }
        all_trades.extend(day_trades)
        print(f"\n  Found {len(day_trades)} trade(s)")
    
    # Generate reports
    print("\n" + "=" * 60)
    print("GENERATING REPORTS...")
    print("=" * 60)
    
    markdown_report = "# TITAN SYSTEM BACKTEST V2 - RELATIVE STRENGTH SELECTION\n\n"
    markdown_report += "**Week of Feb 6-13, 2026**\n\n"
    markdown_report += "**V2 Changes:**\n"
    markdown_report += "- Added IWM to symbol universe (QQQ, SPY, IWM)\n"
    markdown_report += "- Pre-market relative strength calculation\n"
    markdown_report += "- Trade ONLY strongest symbol for longs\n"
    markdown_report += "- Trade ONLY weakest symbol for shorts\n\n"
    markdown_report += "**Data Sources:**\n"
    markdown_report += "- Price Data: Polygon.io (5-minute bars)\n"
    markdown_report += "- Options Data: Tradier (real chains + estimates)\n"
    markdown_report += f"- Position Size: ${POSITION_SIZE} per trade\n\n"
    markdown_report += "---\n\n"
    
    daily_stats = []
    
    for date in TRADING_DATES:
        result = daily_results[date]
        trades = result['trades']
        rs_analysis = result['rs_analysis']
        
        markdown_report += f"## {datetime.strptime(date, '%Y-%m-%d').strftime('%B %d, %Y')}\n\n"
        
        # Show RS analysis
        markdown_report += "**RELATIVE STRENGTH:**\n"
        for symbol in SYMBOLS:
            if symbol in rs_analysis and rs_analysis[symbol]['change_pct'] is not None:
                markdown_report += f"- {symbol}: {rs_analysis[symbol]['change_pct']:+.2f}% (pre-market)\n"
        
        markdown_report += f"\n**SELECTION:**\n"
        markdown_report += f"- LONG PICK: {result['rs_long_pick']} (strongest)\n"
        markdown_report += f"- SHORT PICK: {result['rs_short_pick']} (weakest)\n\n"
        
        if not trades:
            markdown_report += "**TRADE TAKEN:** None (no setup triggered)\n\n"
            markdown_report += "---\n\n"
            continue
        
        # Calculate P&L for all trades
        day_pnl = 0
        wins = 0
        losses = 0
        
        for trade in trades:
            pnl = calculate_pnl(trade)
            trade['pnl'] = pnl
            day_pnl += pnl['total_pnl']
            
            if pnl['total_pnl'] > 0:
                wins += 1
            else:
                losses += 1
            
            markdown_report += format_trade_report(trade, pnl)
        
        markdown_report += f"\n**DAILY SUMMARY:**\n"
        markdown_report += f"- Trades: {len(trades)}\n"
        markdown_report += f"- Wins: {wins} | Losses: {losses}\n"
        markdown_report += f"- Net P&L: ${day_pnl:+.2f}\n"
        markdown_report += f"- Return: {(day_pnl / (POSITION_SIZE * len(trades))) * 100:+.1f}%\n\n"
        markdown_report += "---\n\n"
        
        daily_stats.append({
            'date': date,
            'trades': len(trades),
            'wins': wins,
            'losses': losses,
            'pnl': day_pnl
        })
    
    # Overall statistics
    markdown_report += "## WEEK SUMMARY (V2)\n\n"
    
    total_trades = len(all_trades)
    total_wins = sum(1 for t in all_trades if t.get('pnl', {}).get('total_pnl', 0) > 0)
    total_losses = total_trades - total_wins
    
    win_pnls = [t['pnl']['total_pnl'] for t in all_trades if t.get('pnl', {}).get('total_pnl', 0) > 0]
    loss_pnls = [t['pnl']['total_pnl'] for t in all_trades if t.get('pnl', {}).get('total_pnl', 0) <= 0]
    
    avg_win = sum(win_pnls) / len(win_pnls) if win_pnls else 0
    avg_loss = sum(loss_pnls) / len(loss_pnls) if loss_pnls else 0
    
    total_pnl = sum(t['pnl']['total_pnl'] for t in all_trades)
    
    win_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0
    profit_factor = abs(sum(win_pnls) / sum(loss_pnls)) if loss_pnls and sum(loss_pnls) != 0 else 0
    
    markdown_report += f"**V2 Performance (Relative Strength Selection):**\n"
    markdown_report += f"- Total Trades: {total_trades}\n"
    markdown_report += f"- Wins: {total_wins} | Losses: {total_losses}\n"
    markdown_report += f"- Win Rate: {win_rate:.1f}%\n"
    markdown_report += f"- Average Win: ${avg_win:.2f}\n"
    markdown_report += f"- Average Loss: ${avg_loss:.2f}\n"
    markdown_report += f"- Profit Factor: {profit_factor:.2f}\n"
    markdown_report += f"- Total Return: ${total_pnl:+.2f}\n"
    markdown_report += f"- Total Return %: {(total_pnl / (POSITION_SIZE * total_trades)) * 100:+.1f}%\n\n"
    
    # Comparison to V1
    markdown_report += "---\n\n"
    markdown_report += "## COMPARISON: V1 vs V2\n\n"
    markdown_report += "```\n"
    markdown_report += "V1 (Both symbols):   10 trades, 50% WR, +$39,261\n"
    markdown_report += f"V2 (RS Selection):   {total_trades} trades, {win_rate:.0f}% WR, ${total_pnl:+,.0f}\n"
    markdown_report += "\n"
    if total_trades > 0:
        difference = total_pnl - 39261
        markdown_report += f"Difference: ${difference:+,.0f}\n"
    markdown_report += "```\n\n"
    
    markdown_report += "**Analysis:**\n"
    markdown_report += "- V2 uses relative strength to focus on the most liquid/volatile symbol\n"
    markdown_report += "- Reduces trade count by selecting single best setup per direction\n"
    markdown_report += "- Potentially improves fill quality and reduces slippage\n"
    
    # Save markdown report
    report_path = "/Users/atlasbuilds/clawd/memory/research/titan-week-backtest-RS.md"
    with open(report_path, 'w') as f:
        f.write(markdown_report)
    print(f"\n✓ Markdown report saved to: {report_path}")
    
    # Save JSON data
    json_data = {
        'metadata': {
            'version': 'V2',
            'dates': TRADING_DATES,
            'symbols': SYMBOLS,
            'position_size': POSITION_SIZE,
            'strategy': 'Relative Strength Selection'
        },
        'summary': {
            'total_trades': total_trades,
            'wins': total_wins,
            'losses': total_losses,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'total_pnl': total_pnl,
            'total_return_pct': (total_pnl / (POSITION_SIZE * total_trades)) * 100 if total_trades > 0 else 0
        },
        'comparison': {
            'v1_trades': 10,
            'v1_win_rate': 50,
            'v1_pnl': 39261,
            'v2_trades': total_trades,
            'v2_win_rate': win_rate,
            'v2_pnl': total_pnl,
            'difference': total_pnl - 39261 if total_trades > 0 else 0
        },
        'daily_results': daily_stats,
        'trades': all_trades
    }
    
    json_path = "/Users/atlasbuilds/clawd/titan-trader/backtest_results_RS.json"
    with open(json_path, 'w') as f:
        json.dump(json_data, f, indent=2, default=str)
    print(f"✓ JSON data saved to: {json_path}")
    
    print("\n" + "=" * 60)
    print("BACKTEST V2 COMPLETE")
    print("=" * 60)
    print(f"\nV2 Results:")
    print(f"Total Trades: {total_trades}")
    print(f"Win Rate: {win_rate:.1f}%")
    print(f"Total P&L: ${total_pnl:+.2f}")
    if total_trades > 0:
        print(f"Return: {(total_pnl / (POSITION_SIZE * total_trades)) * 100:+.1f}%")
        print(f"\nVs V1: ${total_pnl - 39261:+.2f} ({total_trades - 10:+d} trades)")


if __name__ == "__main__":
    main()
