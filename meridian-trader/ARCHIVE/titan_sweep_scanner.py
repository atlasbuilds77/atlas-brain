#!/usr/bin/env python3
"""
Titan Sweep Scanner V2

This script implements a sweep/reclaim strategy backtest using Tradier data for Feb 13, 2026.

RULES:
1. Track pre-market H/L for SPY and QQQ.
2. Wait for SWEEP: price breaks through (liquidity grab).
3. Wait for RECLAIM: price gets back inside range (above pre-low or below pre-high).
4. Confirmation candle must hold the reclaim.
5. Enter trade at the confirmation moment.
6. Stop if it re-sweeps and fails to reclaim.

BACKTEST TASK:
Compare a 1-minute vs a 2-minute confirmation after reclaim:
- Compute entry prices using a 1-min candle vs a 2-min candle post reclaim.
- Calculate the P&L difference between the two entries.

Example provided:
- QQQ pre-low: $597.42
- Swept to: $596.42 at 9:42
- Reclaimed above: $597.42 at 9:43 (closed at $599.02)
- Move went to: $606.48

Tradier API token: jj8L3RuSVG5MUwUpz2XHrjXjAFrq

Usage:
 - This scanner fetches historical minute data for SPY and QQQ for Feb 13, 2026 using the Tradier API.
 - It computes pre-market high/low levels, identifies sweep and reclaim events,
   then compares entry prices based on 1-min and 2-min confirmations.

Note: This is a basic backtest scaffold; production implementation must include error handling
and more robust event identification.

Author: TITAN SCANNER V2 Team
Date: 2026-02-13
"""

import requests
import datetime
import json

# Constants
API_TOKEN = 'jj8L3RuSVG5MUwUpz2XHrjXjAFrq'
BASE_URL = 'https://api.tradier.com/v1/markets/history'

# Set parameters for backtest
DATE = '2026-02-13'
SYMBOLS = ['SPY', 'QQQ']

HEADERS = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Accept': 'application/json'
}


def fetch_data(symbol, date):
    """
    Fetch historical minute data for a given symbol on a specific date.
    """
    params = {
        'symbol': symbol,
        'interval': '1min',
        'start': f'{date}T09:30:00',
        'end': f'{date}T16:00:00'
    }
    response = requests.get(BASE_URL, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data for {symbol}: {response.text}")
        return None


def calculate_pre_market_levels(data):
    """
    Calculate pre-market high/low levels from available data before 09:30.
    For this example, assume the first available data point before 09:30 is the pre-market level.
    """
    pre_market_data = [pt for pt in data if pt['time'] < '09:30:00']
    if not pre_market_data:
        return None, None
    high = max(float(pt['high']) for pt in pre_market_data)
    low = min(float(pt['low']) for pt in pre_market_data)
    return high, low


def backtest_strategy(data, pre_low, pre_high):
    """
    This function scans through minute data to detect sweep, reclaim events, and then 
    simulate entries based on 1-min and 2-min confirmation candles after reclaim.

    Returns a dictionary containing key trade metrics: 
    entry price for 1-min confirmation, entry price for 2-minute confirmation, 
    and the P&L difference given the move to the high of the trade.
    """
    sweep_time = None
    reclaim_time = None
    entry_1min = None
    entry_2min = None
    close_after_reclaim = None

    # Flag to note if sweep occurred
    in_sweep = False

    for i, pt in enumerate(data):
        time = pt['time']
        price = float(pt['close'])

        # Detect sweep: price breaks through the pre-market level
        if not in_sweep and (price < pre_low or price > pre_high):
            sweep_time = time
            in_sweep = True
            # print(f'Sweep detected at {time} with price {price}')
            continue

        # Detect reclaim: price comes back inside the range
        if in_sweep and ((pre_low <= price <= pre_high)):
            reclaim_time = time
            # Use the candle for additional confirmation
            # For 1-min confirmation, take the close of that minute
            entry_1min = price
            # For 2-min entry, average with the next minute if available
            if i+1 < len(data):
                next_price = float(data[i+1]['close'])
                entry_2min = (price + next_price) / 2
            # Set a target, for demonstration, assume trade captures move to day's high
            day_high = max(float(pt['high']) for pt in data)
            close_after_reclaim = day_high
            break

    if entry_1min is None or entry_2min is None or close_after_reclaim is None:
        return None

    # Calculate returns based on potential exit price
    pnl_1min = close_after_reclaim - entry_1min
    pnl_2min = close_after_reclaim - entry_2min
    difference = pnl_1min - pnl_2min

    return {
        'sweep_time': sweep_time,
        'reclaim_time': reclaim_time,
        'entry_1min': entry_1min,
        'entry_2min': entry_2min,
        'exit_price': close_after_reclaim,
        'pnl_1min': pnl_1min,
        'pnl_2min': pnl_2min,
        'pnl_difference': difference
    }


def main():
    results = {}
    for symbol in SYMBOLS:
        print(f'Processing {symbol}...')
        json_data = fetch_data(symbol, DATE)
        if json_data is None or 'history' not in json_data or 'day' not in json_data['history']:
            continue
        data = json_data['history']['day']['data']

        # Calculate pre-market levels; here we assume pre-market data is part of the data stream
        pre_high, pre_low = calculate_pre_market_levels(data)
        if pre_high is None or pre_low is None:
            print(f'No pre-market data for {symbol}')
            continue
        print(f'{symbol} pre-market levels - High: {pre_high}, Low: {pre_low}')
        trade_result = backtest_strategy(data, pre_low, pre_high)
        if trade_result is None:
            print(f'No valid trade signals for {symbol}')
            continue
        results[symbol] = trade_result

    # Save results
    with open('/Users/atlasbuilds/clawd/titan-trader/sweep_reclaim_backtest.md', 'w') as f:
        f.write('# Titan Sweep Scanner Backtest Results\n\n')
        for symbol, res in results.items():
            f.write(f'## {symbol}\n')
            f.write(f"Sweep Time: {res['sweep_time']}\n")
            f.write(f"Reclaim Time: {res['reclaim_time']}\n")
            f.write(f"Entry (1-min confirmation): {res['entry_1min']:.2f}\n")
            f.write(f"Entry (2-min confirmation): {res['entry_2min']:.2f}\n")
            f.write(f"Exit Price (Day High): {res['exit_price']:.2f}\n")
            f.write(f"PnL (1-min): {res['pnl_1min']:.2f}\n")
            f.write(f"PnL (2-min): {res['pnl_2min']:.2f}\n")
            f.write(f"PnL Difference (1-min vs 2-min): {res['pnl_difference']:.2f}\n\n")
        if not results:
            f.write('No valid trade signals found for any symbol.\n')
    print('Backtest results saved.')


if __name__ == '__main__':
    main()
