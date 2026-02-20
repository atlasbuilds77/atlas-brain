''' 
Titan V3 Backtest Harness

This script runs a backtest on QQQ data between 2026-01-02 and 2026-02-13 using the Titan V3 Trading System.
It reports the following metrics:
    - Number of trades
    - Win rate
    - Average win / average loss
    - Final P&L with 10% risk sizing
    - List of trades with dates

Usage:
    Ensure that QQQ data is available in a CSV file with columns: Date, Open, High, Low, Close
    Dates should be in a format parsable by pandas as datetime.

Note: This is a simplified backtest that uses daily OHLC data and simulates trade outcomes by comparing the trade's entry level and the day's Close.
For LONG trades: Profit = Close - Entry_Level
For SHORT trades: Profit = Entry_Level - Close
Risk per trade is assumed to be 10% of a hypothetical account size; results are scaled accordingly.
''' 

import pandas as pd
import numpy as np
from datetime import datetime

from titan_v3_system import TitanV3System

# Configuration
BACKTEST_START = '2026-01-02'
BACKTEST_END   = '2026-02-13'
ACCOUNT_SIZE = 100000  # hypothetical account size
RISK_PERCENT = 0.10  # 10% risk per trade (for position sizing)


def load_data(filepath):
    """
    Load QQQ data from CSV. CSV should contain Date, Open, High, Low, Close columns.
    """
    df = pd.read_csv(filepath, parse_dates=['Date'])
    # Filter by date range
    mask = (df['Date'] >= BACKTEST_START) & (df['Date'] <= BACKTEST_END)
    df = df.loc[mask].reset_index(drop=True)
    return df


def simulate_trades(system, ohlc_df):
    """
    Simulate each trade using the day's data:
    For LONG trades: profit = Close - Entry_Level
    For SHORT trades: profit = Entry_Level - Close
    Each trade's profit is scaled with 10% of ACCOUNT_SIZE as risk.
    """
    results = []
    for trade in system.trades:
        # Find the row for the trade date
        trade_date = pd.to_datetime(trade['Date'])
        day_data = ohlc_df[ohlc_df['Date'].dt.date == trade_date.date()]
        if day_data.empty:
            continue
        # Use the last close as trade exit price (simplification)
        trade_close = day_data.iloc[-1]['Close']
        if trade['Direction'] == 'LONG':
            raw_profit = trade_close - trade['Entry_Level']
        else:
            raw_profit = trade['Entry_Level'] - trade_close

        # Scale profit by risk (risk is 10% of account size)
        # For example, if risk is 10% and raw profit is per unit, then trade profit = (raw_profit / entry risk range) * (RISK_PERCENT * ACCOUNT_SIZE)
        # Here we use raw profit directly scaled by a constant factor for simplicity
        scaled_profit = raw_profit * (RISK_PERCENT * ACCOUNT_SIZE / abs(trade['Entry_Level'])) if trade['Entry_Level'] != 0 else 0

        trade_result = {
            'Date': trade_date.strftime('%Y-%m-%d'),
            'Direction': trade['Direction'],
            'Entry_Level': trade['Entry_Level'],
            'Exit_Price': trade_close,
            'Raw_Profit': raw_profit,
            'Scaled_Profit': scaled_profit
        }
        results.append(trade_result)
    return results


def calculate_performance(trade_results):
    """
    Calculate performance metrics: number of trades, win rate, average win, average loss, final P&L.
    """
    num_trades = len(trade_results)
    wins = [t for t in trade_results if t['Scaled_Profit'] > 0]
    losses = [t for t in trade_results if t['Scaled_Profit'] <= 0]
    win_rate = (len(wins) / num_trades) * 100 if num_trades > 0 else 0
    avg_win = np.mean([t['Scaled_Profit'] for t in wins]) if wins else 0
    avg_loss = np.mean([t['Scaled_Profit'] for t in losses]) if losses else 0
    final_pnl = sum(t['Scaled_Profit'] for t in trade_results)
    return {
        'Number of Trades': num_trades,
        'Win Rate (%)': win_rate,
        'Average Win': avg_win,
        'Average Loss': avg_loss,
        'Final P&L': final_pnl
    }


def main():
    # Load QQQ data (path to be adjusted as needed)
    data_file = 'qqq_data.csv'  # Ensure this file exists with data for the backtest period
    ohlc_df = load_data(data_file)
    if ohlc_df.empty:
        print('No data loaded for the specified backtest period.')
        return

    # Initialize trading system
    system = TitanV3System(ohlc_df)
    system.run()
    system.attach_targets()

    # Simulate trade outcomes
    trade_results = simulate_trades(system, ohlc_df)

    # Calculate performance
    performance = calculate_performance(trade_results)

    print('Backtest Performance:')
    for key, value in performance.items():
        print(f'{key}: {value}')

    print('\nTrade Details:')
    for trade in trade_results:
        print(trade)


if __name__ == '__main__':
    main()
