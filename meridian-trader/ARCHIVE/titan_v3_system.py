''' 
Titan V3 Trading System
Full system incorporating entries/exits based on the following logic:

1. SWING DETECTION and CLUSTER DETECTION:
   - Uses titan_v3_formula.py to compute swing highs, swing lows, and clusters

2. TRADE TRIGGER:
   - IF price SWEEPS a significant level (goes through it) 
   - AND price RECLAIMS the opposite side within 10 bars (1-min confirmation)
   - THEN ENTRY in the opposite direction
     - Sweep HIGH + reclaim below = SHORT
     - Sweep LOW + reclaim above = LONG

3. ONE TRADE PER DAY: 
   - Only the first quality setup is taken for the day

4. TARGETS:
   - TP1: Open or nearest significant level opposite to the entry
   - TP2 (runner): Next swing level

This module expects OHLC data and tick data (or minute bars) for simulation.

Note: This system uses Polygon API key for live data if needed: h7J74V1cd8_4NQpTxwQpudpqXWaIHMhv
Reference structure from titan_v2_full.py

'''

import pandas as pd
import numpy as np
from datetime import timedelta

# Import the formula module
import titan_v3_formula as formula


class TitanV3System:
    def __init__(self, ohlc_df, tick_df=None):
        """
        ohlc_df: DataFrame with columns ['Date', 'High', 'Low', 'Open', 'Close'] (Date should be datetime)
        tick_df: DataFrame with tick data if available for intraday trigger confirmation
        """
        self.ohlc_df = ohlc_df.copy()
        self.tick_df = tick_df
        # Results container for trades
        self.trades = []
        # Detect swings first, then get significant levels
        self.ohlc_df = formula.detect_swings(self.ohlc_df)
        self.significant_levels = formula.get_significant_levels(self.ohlc_df)

    def run(self):
        """
        Run the trading system on provided data
        """
        # Process day by day
        for date, day_data in self.ohlc_df.groupby('Date'):
            # Only one trade per day. Check if any trade already executed for this day.
            trade_executed = False
            # Look for swing high/low in this day
            day_row = day_data.iloc[0]
            # Using previous detection to get potential levels
            sig_levels = self.significant_levels
            # For simplicity, we assume the trigger is met if price crosses above/below any significant level
            # This is a simplified simulation logic

            # Simulate trading trigger based on day's High and Low and assume confirmation if within 10 periods (not implemented in detail)
            for level in sig_levels['swing_highs'] + [c[1] for c in sig_levels['resistance_clusters']]:
                # If day's high sweeps above a swing high level and then closes below it (simulate reclaim)
                if day_data['High'].max() > level and day_data['Close'].iloc[-1] < level and not trade_executed:
                    # SHORT signal triggered
                    trade = {
                        'Date': date,
                        'Direction': 'SHORT',
                        'Entry_Level': level
                    }
                    self.trades.append(trade)
                    trade_executed = True
                    break

            for level in sig_levels['swing_lows'] + [c[0] for c in sig_levels['support_clusters']]:
                # If day's low sweeps below a swing low level and then closes above it (simulate reclaim)
                if day_data['Low'].min() < level and day_data['Close'].iloc[-1] > level and not trade_executed:
                    # LONG signal triggered
                    trade = {
                        'Date': date,
                        'Direction': 'LONG',
                        'Entry_Level': level
                    }
                    self.trades.append(trade)
                    trade_executed = True
                    break

    def exit_targets(self, trade):
        """
        Determine exit targets for a given trade.
        For TP1: Nearest significant level opposite direction
        For TP2: Next swing level (runner)
        """
        sig_levels = self.significant_levels
        if trade['Direction'] == 'LONG':
            # TP1 is nearest resistance above entry
            resistances = sorted(sig_levels['swing_highs'] + [c[1] for c in sig_levels['resistance_clusters']])
            tp1 = next((r for r in resistances if r > trade['Entry_Level']), None)
            # TP2 is next swing high beyond TP1 if available
            tp2 = None
            if tp1:
                higher = [r for r in sig_levels['swing_highs'] if r > tp1]
                if higher:
                    tp2 = min(higher)
        else:
            # SHORT: TP1 is nearest support below entry
            supports = sorted(sig_levels['swing_lows'] + [c[0] for c in sig_levels['support_clusters']], reverse=True)
            tp1 = next((s for s in supports if s < trade['Entry_Level']), None)
            tp2 = None
            if tp1:
                lower = [s for s in sig_levels['swing_lows'] if s < tp1]
                if lower:
                    tp2 = max(lower)

        return {'TP1': tp1, 'TP2': tp2}

    def attach_targets(self):
        """
        Attach exit targets to all trades
        """
        for trade in self.trades:
            trade['Exits'] = self.exit_targets(trade)


if __name__ == '__main__':
    # For testing purposes
    # Load sample OHLC data, in real scenario the data would be intraday or tick data
    ohlc_df = pd.read_csv('sample_data.csv', parse_dates=['Date'])
    system = TitanV3System(ohlc_df)
    system.run()
    system.attach_targets()
    print('Trades executed:')
    for trade in system.trades:
        print(trade)
