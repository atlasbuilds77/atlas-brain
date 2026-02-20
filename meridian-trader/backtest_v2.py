#!/usr/bin/env python3
"""
TITAN Backtester V2 - Uses daily data for more history
Tests order block strategy with proper trade simulation
"""

import requests
from datetime import datetime, timedelta
from collections import defaultdict
import sys
sys.path.insert(0, '/Users/atlasbuilds/clawd')

try:
    from trading_creds import get_tradier_token
    TRADIER_TOKEN = get_tradier_token()
except:
    TRADIER_TOKEN = "jj8L3RuSVG5MUwUpz2XHrjXjAFrq"

HEADERS = {
    "Authorization": f"Bearer {TRADIER_TOKEN}",
    "Accept": "application/json"
}


def fetch_daily_candles(symbol: str, start_date: str = "2025-01-01") -> list:
    """Fetch daily candles from Tradier."""
    resp = requests.get(
        "https://api.tradier.com/v1/markets/history",
        params={
            "symbol": symbol,
            "interval": "daily",
            "start": start_date,
            "end": datetime.now().strftime("%Y-%m-%d")
        },
        headers=HEADERS,
        timeout=30
    )
    
    if resp.status_code == 200:
        data = resp.json()
        if "history" in data and data["history"]:
            return data["history"]["day"]
    return []


def detect_order_blocks_v2(candles: list, min_strength: float = 1.2) -> dict:
    """
    Detect order blocks with configurable strength.
    More aggressive than v1 - catches more setups.
    """
    demand_zones = []
    supply_zones = []
    
    for i in range(1, len(candles) - 1):
        prev = candles[i - 1]
        curr = candles[i]
        next_c = candles[i + 1]
        
        curr_open = float(curr.get("open", 0))
        curr_close = float(curr.get("close", 0))
        curr_high = float(curr.get("high", 0))
        curr_low = float(curr.get("low", 0))
        
        next_open = float(next_c.get("open", 0))
        next_close = float(next_c.get("close", 0))
        next_high = float(next_c.get("high", 0))
        next_low = float(next_c.get("low", 0))
        
        curr_body = abs(curr_close - curr_open)
        next_body = abs(next_close - next_open)
        
        if curr_body == 0:
            continue
        
        # DEMAND ZONE (Bullish OB)
        # Red candle followed by strong green candle
        is_red = curr_close < curr_open
        is_next_green = next_close > next_open
        breaks_high = next_close > curr_high
        strong_move = next_body > curr_body * min_strength
        
        if is_red and is_next_green and (breaks_high or strong_move):
            demand_zones.append({
                "high": curr_high,
                "low": curr_low,
                "mid": (curr_high + curr_low) / 2,
                "date": curr.get("date"),
                "index": i,
                "strength": next_body / curr_body,
                "touched": False,
                "broken": False
            })
        
        # SUPPLY ZONE (Bearish OB)
        # Green candle followed by strong red candle
        is_green = curr_close > curr_open
        is_next_red = next_close < next_open
        breaks_low = next_close < curr_low
        
        if is_green and is_next_red and (breaks_low or strong_move):
            supply_zones.append({
                "high": curr_high,
                "low": curr_low,
                "mid": (curr_high + curr_low) / 2,
                "date": curr.get("date"),
                "index": i,
                "strength": next_body / curr_body,
                "touched": False,
                "broken": False
            })
    
    return {"demand": demand_zones, "supply": supply_zones}


def simulate_trades_v2(candles: list, order_blocks: dict,
                       stop_pct: float = 0.02,  # 2% underlying stop = ~35% option
                       target_pcts: list = [0.01, 0.015, 0.02]) -> list:  # ~30/50/75% option
    """
    Walk through candles and simulate entries/exits.
    More realistic: enters on touch, manages with stops/targets.
    """
    trades = []
    active_trades = []  # Can have multiple positions
    
    # Mark OBs as we go
    demand_zones = order_blocks["demand"].copy()
    supply_zones = order_blocks["supply"].copy()
    
    for i, candle in enumerate(candles):
        date = candle.get("date", "")
        open_p = float(candle.get("open", 0))
        high = float(candle.get("high", 0))
        low = float(candle.get("low", 0))
        close = float(candle.get("close", 0))
        
        # Update active trades
        closed_trades = []
        for trade in active_trades:
            entry = trade["entry_price"]
            direction = trade["direction"]
            
            if direction == "LONG":
                # Stop check
                if low <= entry * (1 - stop_pct):
                    trade["exit_price"] = entry * (1 - stop_pct)
                    trade["exit_date"] = date
                    trade["result"] = "STOPPED"
                    trade["underlying_pnl"] = -stop_pct
                    trade["option_pnl"] = -35  # Approximate
                    closed_trades.append(trade)
                    continue
                
                # Target check (use high for best case)
                max_move = (high - entry) / entry
                if max_move >= target_pcts[-1]:
                    trade["exit_price"] = entry * (1 + target_pcts[-1])
                    trade["exit_date"] = date
                    trade["result"] = "TARGET"
                    trade["underlying_pnl"] = target_pcts[-1]
                    trade["option_pnl"] = 75  # Approximate
                    closed_trades.append(trade)
                    continue
                    
            elif direction == "SHORT":
                # Stop check
                if high >= entry * (1 + stop_pct):
                    trade["exit_price"] = entry * (1 + stop_pct)
                    trade["exit_date"] = date
                    trade["result"] = "STOPPED"
                    trade["underlying_pnl"] = -stop_pct
                    trade["option_pnl"] = -35
                    closed_trades.append(trade)
                    continue
                
                # Target check
                max_move = (entry - low) / entry
                if max_move >= target_pcts[-1]:
                    trade["exit_price"] = entry * (1 - target_pcts[-1])
                    trade["exit_date"] = date
                    trade["result"] = "TARGET"
                    trade["underlying_pnl"] = target_pcts[-1]
                    trade["option_pnl"] = 75
                    closed_trades.append(trade)
                    continue
        
        # Remove closed trades
        for trade in closed_trades:
            active_trades.remove(trade)
            trades.append(trade)
        
        # Only enter new trades if we don't have too many active
        if len(active_trades) >= 2:
            continue
        
        # Check for LONG entries (price touches demand zone)
        for zone in demand_zones:
            if zone["touched"] or zone["broken"]:
                continue
            if zone["index"] >= i:  # Zone hasn't formed yet
                continue
            
            # Price dips into zone
            if low <= zone["high"] and high >= zone["low"]:
                zone["touched"] = True
                
                # Check if zone is broken (invalidated)
                if close < zone["low"]:
                    zone["broken"] = True
                    continue
                
                # Enter LONG at zone high
                active_trades.append({
                    "direction": "LONG",
                    "entry_price": zone["high"],
                    "entry_date": date,
                    "zone": zone,
                    "exit_price": None,
                    "exit_date": None,
                    "result": None,
                    "underlying_pnl": 0,
                    "option_pnl": 0
                })
                break  # Only one entry per candle
        
        # Check for SHORT entries (price touches supply zone)
        if len(active_trades) < 2:
            for zone in supply_zones:
                if zone["touched"] or zone["broken"]:
                    continue
                if zone["index"] >= i:
                    continue
                
                # Price rallies into zone
                if high >= zone["low"] and low <= zone["high"]:
                    zone["touched"] = True
                    
                    # Check if zone is broken
                    if close > zone["high"]:
                        zone["broken"] = True
                        continue
                    
                    # Enter SHORT at zone low
                    active_trades.append({
                        "direction": "SHORT",
                        "entry_price": zone["low"],
                        "entry_date": date,
                        "zone": zone,
                        "exit_price": None,
                        "exit_date": None,
                        "result": None,
                        "underlying_pnl": 0,
                        "option_pnl": 0
                    })
                    break
    
    # Close remaining trades at last price
    last_close = float(candles[-1].get("close", 0))
    last_date = candles[-1].get("date", "")
    
    for trade in active_trades:
        entry = trade["entry_price"]
        if trade["direction"] == "LONG":
            pnl = (last_close - entry) / entry
        else:
            pnl = (entry - last_close) / entry
        
        trade["exit_price"] = last_close
        trade["exit_date"] = last_date
        trade["result"] = "OPEN"
        trade["underlying_pnl"] = pnl
        trade["option_pnl"] = pnl * 25 * 100  # Rough option leverage
        trades.append(trade)
    
    return trades


def analyze_results(trades: list, symbol: str) -> dict:
    """Analyze backtest results."""
    if not trades:
        return None
    
    wins = [t for t in trades if t["option_pnl"] > 0]
    losses = [t for t in trades if t["option_pnl"] < 0]
    
    total_option_pnl = sum(t["option_pnl"] for t in trades)
    win_rate = len(wins) / len(trades) * 100
    
    avg_win = sum(t["option_pnl"] for t in wins) / len(wins) if wins else 0
    avg_loss = sum(t["option_pnl"] for t in losses) / len(losses) if losses else 0
    
    # Profit factor
    gross_profit = sum(t["option_pnl"] for t in wins) if wins else 0
    gross_loss = abs(sum(t["option_pnl"] for t in losses)) if losses else 1
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
    
    # By direction
    longs = [t for t in trades if t["direction"] == "LONG"]
    shorts = [t for t in trades if t["direction"] == "SHORT"]
    
    long_wins = len([t for t in longs if t["option_pnl"] > 0])
    short_wins = len([t for t in shorts if t["option_pnl"] > 0])
    
    return {
        "symbol": symbol,
        "total_trades": len(trades),
        "wins": len(wins),
        "losses": len(losses),
        "win_rate": win_rate,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "profit_factor": profit_factor,
        "total_pnl": total_option_pnl,
        "longs": len(longs),
        "long_wr": long_wins / len(longs) * 100 if longs else 0,
        "shorts": len(shorts),
        "short_wr": short_wins / len(shorts) * 100 if shorts else 0,
        "trades": trades
    }


def run_backtest(symbol: str, min_strength: float = 1.2) -> dict:
    """Run backtest on a single symbol."""
    print(f"\n📊 BACKTESTING {symbol}")
    print("-" * 40)
    
    candles = fetch_daily_candles(symbol)
    if not candles:
        print("  ❌ No data")
        return None
    
    print(f"  ✓ {len(candles)} daily bars ({candles[0]['date']} to {candles[-1]['date']})")
    
    # Detect order blocks
    obs = detect_order_blocks_v2(candles, min_strength)
    print(f"  ✓ Found {len(obs['demand'])} demand zones, {len(obs['supply'])} supply zones")
    
    # Simulate
    trades = simulate_trades_v2(candles, obs)
    print(f"  ✓ Generated {len(trades)} trades")
    
    if not trades:
        return None
    
    # Analyze
    results = analyze_results(trades, symbol)
    
    # Print results
    print(f"\n  📈 RESULTS:")
    print(f"     Total Trades: {results['total_trades']}")
    print(f"     Win Rate: {results['win_rate']:.1f}%")
    print(f"     Avg Win: +{results['avg_win']:.1f}%")
    print(f"     Avg Loss: {results['avg_loss']:.1f}%")
    print(f"     Profit Factor: {results['profit_factor']:.2f}")
    print(f"     Total P/L: {results['total_pnl']:+.0f}%")
    print(f"     Longs: {results['longs']} ({results['long_wr']:.0f}% WR)")
    print(f"     Shorts: {results['shorts']} ({results['short_wr']:.0f}% WR)")
    
    return results


def run_full_backtest():
    """Run backtest on all symbols."""
    print("\n" + "=" * 60)
    print("🧪 TITAN BACKTESTER V2")
    print("=" * 60)
    print("Data: Daily bars from Jan 2025")
    print("Strategy: Order Block entries (1.2x strength)")
    print("Risk: 2% underlying stop (~35% option)")
    print("Targets: 1/1.5/2% underlying (~30/50/75% option)")
    
    all_results = {}
    all_trades = []
    
    for symbol in ["SPY", "QQQ", "IWM"]:
        result = run_backtest(symbol)
        if result:
            all_results[symbol] = result
            all_trades.extend(result["trades"])
    
    # Overall summary
    print("\n" + "=" * 60)
    print("📊 OVERALL SUMMARY")
    print("=" * 60)
    
    total_trades = len(all_trades)
    total_wins = len([t for t in all_trades if t["option_pnl"] > 0])
    total_pnl = sum(t["option_pnl"] for t in all_trades)
    
    print(f"\nTotal Trades: {total_trades}")
    print(f"Overall Win Rate: {total_wins/total_trades*100:.1f}%" if total_trades else "N/A")
    print(f"Combined P/L: {total_pnl:+.0f}%")
    
    print("\nPer Symbol:")
    for symbol, r in all_results.items():
        print(f"  {symbol}: {r['total_trades']} trades | {r['win_rate']:.0f}% WR | {r['total_pnl']:+.0f}% P/L | PF: {r['profit_factor']:.2f}")
    
    # Monthly breakdown
    print("\n📅 Monthly Breakdown (All Symbols):")
    monthly = defaultdict(lambda: {"trades": 0, "pnl": 0, "wins": 0})
    for t in all_trades:
        month = t["entry_date"][:7]  # YYYY-MM
        monthly[month]["trades"] += 1
        monthly[month]["pnl"] += t["option_pnl"]
        if t["option_pnl"] > 0:
            monthly[month]["wins"] += 1
    
    for month in sorted(monthly.keys()):
        m = monthly[month]
        wr = m["wins"] / m["trades"] * 100 if m["trades"] else 0
        print(f"  {month}: {m['trades']} trades | {wr:.0f}% WR | {m['pnl']:+.0f}% P/L")
    
    # Sample trades
    print("\n📋 Sample Trades (Last 10):")
    for t in all_trades[-10:]:
        emoji = "✅" if t["option_pnl"] > 0 else "❌"
        print(f"  {emoji} {t['direction']} @ ${t['entry_price']:.2f} ({t['entry_date']})")
        print(f"     → {t['result']} | Option P/L: {t['option_pnl']:+.0f}%")
    
    return all_results


if __name__ == "__main__":
    run_full_backtest()
