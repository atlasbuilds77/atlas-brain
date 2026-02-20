#!/usr/bin/env python3
"""
TITAN Backtester - Test order block + GEX strategy on historical data
"""

import requests
import json
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


def fetch_historical_candles(symbol: str, interval: str = "15min", days: int = 30) -> list:
    """Fetch historical candle data."""
    end = datetime.now()
    start = end - timedelta(days=days)
    
    resp = requests.get(
        "https://api.tradier.com/v1/markets/timesales",
        params={
            "symbol": symbol,
            "interval": interval,
            "start": start.strftime("%Y-%m-%d %H:%M"),
            "end": end.strftime("%Y-%m-%d %H:%M"),
            "session_filter": "open"
        },
        headers=HEADERS,
        timeout=30,
    )
    
    data = resp.json()
    series = data.get("series", {})
    if not series:
        return []
    candles = series.get("data", [])
    if isinstance(candles, dict):
        candles = [candles]
    return candles


def aggregate_candles(candles_15m: list, target_minutes: int) -> list:
    """Aggregate 15m candles to higher timeframes."""
    if not candles_15m or target_minutes <= 15:
        return candles_15m
    
    ratio = target_minutes // 15
    aggregated = []
    
    for i in range(0, len(candles_15m) - ratio + 1, ratio):
        chunk = candles_15m[i:i + ratio]
        if len(chunk) < ratio:
            continue
        
        agg_candle = {
            "time": chunk[0].get("time"),
            "open": float(chunk[0].get("open", chunk[0].get("price", 0))),
            "high": max(float(c.get("high", c.get("price", 0))) for c in chunk),
            "low": min(float(c.get("low", c.get("price", 0))) for c in chunk),
            "close": float(chunk[-1].get("close", chunk[-1].get("price", 0))),
            "volume": sum(int(c.get("volume", 0)) for c in chunk)
        }
        aggregated.append(agg_candle)
    
    return aggregated


def detect_order_blocks(candles: list, lookback: int = 50) -> dict:
    """Detect order blocks in candle data."""
    if len(candles) < lookback:
        return {"demand": [], "supply": []}
    
    recent = candles[-lookback:]
    demand_zones = []
    supply_zones = []
    
    for i in range(2, len(recent) - 1):
        curr = recent[i]
        next_c = recent[i + 1]
        
        curr_open = float(curr.get("open", curr.get("price", 0)))
        curr_close = float(curr.get("close", curr.get("price", 0)))
        curr_high = float(curr.get("high", curr.get("price", 0)))
        curr_low = float(curr.get("low", curr.get("price", 0)))
        
        next_open = float(next_c.get("open", next_c.get("price", 0)))
        next_close = float(next_c.get("close", next_c.get("price", 0)))
        
        curr_body = abs(curr_close - curr_open)
        next_body = abs(next_close - next_open)
        
        # Bullish OB (looser criteria - 1.2x instead of 1.5x)
        if curr_close < curr_open:
            if next_close > next_open and next_body > curr_body * 1.2:
                demand_zones.append({
                    "high": curr_high,
                    "low": curr_low,
                    "time": curr.get("time"),
                    "index": i,
                    "strength": next_body / curr_body if curr_body > 0 else 1
                })
        
        # Bearish OB (looser criteria)
        if curr_close > curr_open:
            if next_close < next_open and next_body > curr_body * 1.2:
                supply_zones.append({
                    "high": curr_high,
                    "low": curr_low,
                    "time": curr.get("time"),
                    "index": i,
                    "strength": next_body / curr_body if curr_body > 0 else 1
                })
    
    return {"demand": demand_zones, "supply": supply_zones}


def simulate_trades(candles: list, order_blocks: dict, 
                   stop_pct: float = 0.35, 
                   target_pcts: list = [0.30, 0.50, 0.75]) -> list:
    """
    Simulate trades based on order block touches.
    
    Entry: When price touches order block zone
    Stop: -35% on option (approximated as % of underlying move)
    Targets: 30%, 50%, 75% on option
    
    Approximation: Options move ~2.5x underlying
    So -35% option ≈ -14% underlying move
    And +30% option ≈ +12% underlying move
    """
    trades = []
    active_trade = None
    
    # Option leverage approximation
    OPTION_LEVERAGE = 2.5
    underlying_stop = stop_pct / OPTION_LEVERAGE  # ~14%
    underlying_targets = [t / OPTION_LEVERAGE for t in target_pcts]  # ~12%, 20%, 30%
    
    for i, candle in enumerate(candles):
        price = float(candle.get("close", candle.get("price", 0)))
        high = float(candle.get("high", candle.get("price", 0)))
        low = float(candle.get("low", candle.get("price", 0)))
        time = candle.get("time", "")
        
        # Manage active trade
        if active_trade:
            entry = active_trade["entry_price"]
            direction = active_trade["direction"]
            
            if direction == "LONG":
                # Check stop
                move_pct = (low - entry) / entry
                if move_pct <= -underlying_stop:
                    active_trade["exit_price"] = entry * (1 - underlying_stop)
                    active_trade["exit_time"] = time
                    active_trade["result"] = "STOPPED"
                    active_trade["pnl_pct"] = -stop_pct * 100
                    trades.append(active_trade)
                    active_trade = None
                    continue
                
                # Check targets
                move_pct = (high - entry) / entry
                for j, target in enumerate(underlying_targets):
                    if move_pct >= target and not active_trade["targets_hit"][j]:
                        active_trade["targets_hit"][j] = True
                        
                        # Exit on last target
                        if all(active_trade["targets_hit"]):
                            active_trade["exit_price"] = entry * (1 + target)
                            active_trade["exit_time"] = time
                            active_trade["result"] = "TARGET_3"
                            active_trade["pnl_pct"] = target_pcts[-1] * 100
                            trades.append(active_trade)
                            active_trade = None
                            break
            
            elif direction == "SHORT":
                # Check stop (price goes up)
                move_pct = (high - entry) / entry
                if move_pct >= underlying_stop:
                    active_trade["exit_price"] = entry * (1 + underlying_stop)
                    active_trade["exit_time"] = time
                    active_trade["result"] = "STOPPED"
                    active_trade["pnl_pct"] = -stop_pct * 100
                    trades.append(active_trade)
                    active_trade = None
                    continue
                
                # Check targets (price goes down)
                move_pct = (entry - low) / entry
                for j, target in enumerate(underlying_targets):
                    if move_pct >= target and not active_trade["targets_hit"][j]:
                        active_trade["targets_hit"][j] = True
                        
                        if all(active_trade["targets_hit"]):
                            active_trade["exit_price"] = entry * (1 - target)
                            active_trade["exit_time"] = time
                            active_trade["result"] = "TARGET_3"
                            active_trade["pnl_pct"] = target_pcts[-1] * 100
                            trades.append(active_trade)
                            active_trade = None
                            break
            
            continue  # Don't enter new trade while one is active
        
        # Look for entry on demand zones (LONG)
        for demand in order_blocks["demand"]:
            if demand.get("used"):
                continue
            
            # Price touches demand zone
            if low <= demand["high"] and high >= demand["low"]:
                active_trade = {
                    "direction": "LONG",
                    "entry_price": demand["high"],  # Entry at top of zone
                    "entry_time": time,
                    "zone": demand,
                    "targets_hit": [False, False, False],
                    "exit_price": None,
                    "exit_time": None,
                    "result": None,
                    "pnl_pct": 0
                }
                demand["used"] = True
                break
        
        # Look for entry on supply zones (SHORT)
        if not active_trade:
            for supply in order_blocks["supply"]:
                if supply.get("used"):
                    continue
                
                # Price touches supply zone
                if high >= supply["low"] and low <= supply["high"]:
                    active_trade = {
                        "direction": "SHORT",
                        "entry_price": supply["low"],  # Entry at bottom of zone
                        "entry_time": time,
                        "zone": supply,
                        "targets_hit": [False, False, False],
                        "exit_price": None,
                        "exit_time": None,
                        "result": None,
                        "pnl_pct": 0
                    }
                    supply["used"] = True
                    break
    
    # Close any remaining trade at last price
    if active_trade:
        last_price = float(candles[-1].get("close", candles[-1].get("price", 0)))
        entry = active_trade["entry_price"]
        
        if active_trade["direction"] == "LONG":
            move_pct = (last_price - entry) / entry
        else:
            move_pct = (entry - last_price) / entry
        
        active_trade["exit_price"] = last_price
        active_trade["exit_time"] = candles[-1].get("time", "")
        active_trade["result"] = "OPEN"
        active_trade["pnl_pct"] = move_pct * OPTION_LEVERAGE * 100
        trades.append(active_trade)
    
    return trades


def run_backtest(symbol: str, days: int = 30):
    """Run full backtest on a symbol."""
    print(f"\n📊 BACKTESTING {symbol} ({days} days)")
    print("=" * 50)
    
    # Fetch data
    print("  Fetching historical data...")
    candles_15m = fetch_historical_candles(symbol, "15min", days)
    
    if len(candles_15m) < 100:
        print(f"  ❌ Not enough data ({len(candles_15m)} candles)")
        return None
    
    print(f"  ✓ Got {len(candles_15m)} candles")
    
    # Aggregate to 30m for order block detection
    candles_30m = aggregate_candles(candles_15m, 30)
    
    # Detect order blocks
    print("  Detecting order blocks...")
    order_blocks = detect_order_blocks(candles_30m)
    
    print(f"  ✓ Found {len(order_blocks['demand'])} demand zones")
    print(f"  ✓ Found {len(order_blocks['supply'])} supply zones")
    
    # Simulate trades
    print("  Simulating trades...")
    trades = simulate_trades(candles_30m, order_blocks)
    
    if not trades:
        print("  ⚠️ No trades generated")
        return None
    
    # Calculate stats
    wins = [t for t in trades if t["pnl_pct"] > 0]
    losses = [t for t in trades if t["pnl_pct"] < 0]
    
    total_pnl = sum(t["pnl_pct"] for t in trades)
    win_rate = len(wins) / len(trades) * 100 if trades else 0
    avg_win = sum(t["pnl_pct"] for t in wins) / len(wins) if wins else 0
    avg_loss = sum(t["pnl_pct"] for t in losses) / len(losses) if losses else 0
    
    # Profit factor
    gross_profit = sum(t["pnl_pct"] for t in wins)
    gross_loss = abs(sum(t["pnl_pct"] for t in losses))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
    
    # Results
    print(f"\n📈 RESULTS FOR {symbol}")
    print("-" * 40)
    print(f"  Total Trades: {len(trades)}")
    print(f"  Wins: {len(wins)} | Losses: {len(losses)}")
    print(f"  Win Rate: {win_rate:.1f}%")
    print(f"  Avg Win: +{avg_win:.1f}%")
    print(f"  Avg Loss: {avg_loss:.1f}%")
    print(f"  Profit Factor: {profit_factor:.2f}")
    print(f"  Total P/L: {total_pnl:+.1f}%")
    
    # Trade breakdown
    longs = [t for t in trades if t["direction"] == "LONG"]
    shorts = [t for t in trades if t["direction"] == "SHORT"]
    
    print(f"\n  Long trades: {len(longs)}")
    print(f"  Short trades: {len(shorts)}")
    
    # Sample trades
    print(f"\n  📋 Sample Trades:")
    for trade in trades[:5]:
        emoji = "✅" if trade["pnl_pct"] > 0 else "❌"
        print(f"    {emoji} {trade['direction']} @ ${trade['entry_price']:.2f}")
        print(f"       → {trade['result']} | P/L: {trade['pnl_pct']:+.1f}%")
    
    return {
        "symbol": symbol,
        "days": days,
        "total_trades": len(trades),
        "wins": len(wins),
        "losses": len(losses),
        "win_rate": win_rate,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "profit_factor": profit_factor,
        "total_pnl": total_pnl,
        "trades": trades
    }


def run_full_backtest(days: int = 30):
    """Run backtest on all symbols."""
    print("\n" + "=" * 60)
    print("🧪 TITAN BACKTESTER")
    print("=" * 60)
    print(f"Period: Last {days} days")
    print(f"Strategy: Order Block entries")
    print(f"Risk: -35% stop, +30/50/75% targets")
    
    results = {}
    
    for symbol in ["SPY", "QQQ", "IWM"]:
        result = run_backtest(symbol, days)
        if result:
            results[symbol] = result
    
    # Summary
    if results:
        print("\n" + "=" * 60)
        print("📊 BACKTEST SUMMARY")
        print("=" * 60)
        
        total_trades = sum(r["total_trades"] for r in results.values())
        total_wins = sum(r["wins"] for r in results.values())
        overall_pnl = sum(r["total_pnl"] for r in results.values())
        
        print(f"\nTotal Trades: {total_trades}")
        print(f"Overall Win Rate: {total_wins/total_trades*100:.1f}%" if total_trades else "N/A")
        print(f"Combined P/L: {overall_pnl:+.1f}%")
        
        print("\nPer Symbol:")
        for symbol, r in results.items():
            print(f"  {symbol}: {r['win_rate']:.0f}% WR | {r['total_pnl']:+.1f}% P/L | PF: {r['profit_factor']:.2f}")
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="TITAN Backtester")
    parser.add_argument("--days", type=int, default=30, help="Days to backtest")
    parser.add_argument("--symbol", type=str, default=None, help="Single symbol to test")
    
    args = parser.parse_args()
    
    if args.symbol:
        run_backtest(args.symbol, args.days)
    else:
        run_full_backtest(args.days)
