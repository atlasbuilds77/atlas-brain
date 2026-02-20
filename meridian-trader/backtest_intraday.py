#!/usr/bin/env python3
"""
TITAN Backtester - Intraday (15m/30m Order Blocks)
For day trading - more trades, faster action
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


def fetch_intraday(symbol: str, interval: str = "15min", days: int = 20) -> list:
    """Fetch intraday candles. Tradier allows ~20 days of intraday."""
    all_candles = []
    
    # Fetch in chunks to get more data
    for chunk in range(0, days, 5):
        end = datetime.now() - timedelta(days=chunk)
        start = end - timedelta(days=5)
        
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
            timeout=30
        )
        
        if resp.status_code == 200:
            try:
                data = resp.json()
                series = data.get("series", {})
                if series:
                    candles = series.get("data", [])
                    if isinstance(candles, dict):
                        candles = [candles]
                    all_candles.extend(candles)
            except:
                continue
    
    # Sort by time and remove duplicates
    seen = set()
    unique = []
    for c in all_candles:
        t = c.get("time", "")
        if t not in seen:
            seen.add(t)
            unique.append(c)
    
    unique.sort(key=lambda x: x.get("time", ""))
    return unique


def detect_order_blocks(candles: list, min_strength: float = 1.15) -> dict:
    """Detect intraday order blocks - slightly looser for more signals."""
    demand_zones = []
    supply_zones = []
    
    for i in range(1, len(candles) - 1):
        curr = candles[i]
        next_c = candles[i + 1]
        
        curr_open = float(curr.get("open", curr.get("price", 0)))
        curr_close = float(curr.get("close", curr.get("price", 0)))
        curr_high = float(curr.get("high", curr.get("price", 0)))
        curr_low = float(curr.get("low", curr.get("price", 0)))
        
        next_open = float(next_c.get("open", next_c.get("price", 0)))
        next_close = float(next_c.get("close", next_c.get("price", 0)))
        
        curr_body = abs(curr_close - curr_open)
        next_body = abs(next_close - next_open)
        
        if curr_body == 0:
            continue
        
        strength = next_body / curr_body
        
        # DEMAND (Bullish OB)
        is_red = curr_close < curr_open
        is_next_green = next_close > next_open
        strong_move = strength >= min_strength
        
        if is_red and is_next_green and strong_move:
            demand_zones.append({
                "high": curr_high,
                "low": curr_low,
                "time": curr.get("time"),
                "index": i,
                "strength": strength,
                "touched": False
            })
        
        # SUPPLY (Bearish OB)
        is_green = curr_close > curr_open
        is_next_red = next_close < next_open
        
        if is_green and is_next_red and strong_move:
            supply_zones.append({
                "high": curr_high,
                "low": curr_low,
                "time": curr.get("time"),
                "index": i,
                "strength": strength,
                "touched": False
            })
    
    return {"demand": demand_zones, "supply": supply_zones}


def simulate_intraday(candles: list, order_blocks: dict,
                      stop_pct: float = 0.003,  # 0.3% underlying = ~35% option intraday
                      target_pct: float = 0.006) -> list:  # 0.6% underlying = ~70% option
    """
    Intraday simulation - tighter stops, faster targets.
    Options move roughly 10-15x underlying intraday with ATM.
    """
    trades = []
    active_trade = None
    
    OPTION_MULT = 12  # Rough ATM option multiplier intraday
    
    demand_zones = order_blocks["demand"].copy()
    supply_zones = order_blocks["supply"].copy()
    
    for i, candle in enumerate(candles):
        time = candle.get("time", "")
        price = float(candle.get("close", candle.get("price", 0)))
        high = float(candle.get("high", candle.get("price", 0)))
        low = float(candle.get("low", candle.get("price", 0)))
        
        # Skip if near market close (last 30 min)
        if "15:30" in time or "15:45" in time:
            if active_trade:
                # Close at EOD
                entry = active_trade["entry_price"]
                if active_trade["direction"] == "LONG":
                    pnl = (price - entry) / entry
                else:
                    pnl = (entry - price) / entry
                
                active_trade["exit_price"] = price
                active_trade["exit_time"] = time
                active_trade["result"] = "EOD"
                active_trade["underlying_pnl"] = pnl
                active_trade["option_pnl"] = pnl * OPTION_MULT * 100
                trades.append(active_trade)
                active_trade = None
            continue
        
        # Manage active trade
        if active_trade:
            entry = active_trade["entry_price"]
            direction = active_trade["direction"]
            
            if direction == "LONG":
                # Stop
                if low <= entry * (1 - stop_pct):
                    active_trade["exit_price"] = entry * (1 - stop_pct)
                    active_trade["exit_time"] = time
                    active_trade["result"] = "STOPPED"
                    active_trade["underlying_pnl"] = -stop_pct
                    active_trade["option_pnl"] = -stop_pct * OPTION_MULT * 100
                    trades.append(active_trade)
                    active_trade = None
                    continue
                
                # Target
                if high >= entry * (1 + target_pct):
                    active_trade["exit_price"] = entry * (1 + target_pct)
                    active_trade["exit_time"] = time
                    active_trade["result"] = "TARGET"
                    active_trade["underlying_pnl"] = target_pct
                    active_trade["option_pnl"] = target_pct * OPTION_MULT * 100
                    trades.append(active_trade)
                    active_trade = None
                    continue
            
            elif direction == "SHORT":
                # Stop
                if high >= entry * (1 + stop_pct):
                    active_trade["exit_price"] = entry * (1 + stop_pct)
                    active_trade["exit_time"] = time
                    active_trade["result"] = "STOPPED"
                    active_trade["underlying_pnl"] = -stop_pct
                    active_trade["option_pnl"] = -stop_pct * OPTION_MULT * 100
                    trades.append(active_trade)
                    active_trade = None
                    continue
                
                # Target
                if low <= entry * (1 - target_pct):
                    active_trade["exit_price"] = entry * (1 - target_pct)
                    active_trade["exit_time"] = time
                    active_trade["result"] = "TARGET"
                    active_trade["underlying_pnl"] = target_pct
                    active_trade["option_pnl"] = target_pct * OPTION_MULT * 100
                    trades.append(active_trade)
                    active_trade = None
                    continue
            
            continue  # Don't enter while in trade
        
        # Look for entries
        # LONG on demand touch
        for zone in demand_zones:
            if zone["touched"] or zone["index"] >= i:
                continue
            
            if low <= zone["high"] and high >= zone["low"]:
                zone["touched"] = True
                active_trade = {
                    "direction": "LONG",
                    "entry_price": zone["high"],
                    "entry_time": time,
                    "zone": zone,
                    "exit_price": None,
                    "exit_time": None,
                    "result": None
                }
                break
        
        # SHORT on supply touch
        if not active_trade:
            for zone in supply_zones:
                if zone["touched"] or zone["index"] >= i:
                    continue
                
                if high >= zone["low"] and low <= zone["high"]:
                    zone["touched"] = True
                    active_trade = {
                        "direction": "SHORT",
                        "entry_price": zone["low"],
                        "entry_time": time,
                        "zone": zone,
                        "exit_price": None,
                        "exit_time": None,
                        "result": None
                    }
                    break
    
    return trades


def run_backtest(symbol: str, interval: str = "15min", days: int = 20):
    """Run intraday backtest."""
    print(f"\n📊 {symbol} ({interval} bars, {days} days)")
    print("-" * 40)
    
    candles = fetch_intraday(symbol, interval, days)
    if len(candles) < 50:
        print(f"  ❌ Not enough data ({len(candles)} candles)")
        return None
    
    print(f"  ✓ {len(candles)} candles")
    
    obs = detect_order_blocks(candles)
    print(f"  ✓ {len(obs['demand'])} demand, {len(obs['supply'])} supply zones")
    
    trades = simulate_intraday(candles, obs)
    print(f"  ✓ {len(trades)} trades")
    
    if not trades:
        return None
    
    wins = [t for t in trades if t.get("option_pnl", 0) > 0]
    losses = [t for t in trades if t.get("option_pnl", 0) < 0]
    
    total_pnl = sum(t.get("option_pnl", 0) for t in trades)
    win_rate = len(wins) / len(trades) * 100 if trades else 0
    
    avg_win = sum(t["option_pnl"] for t in wins) / len(wins) if wins else 0
    avg_loss = sum(t["option_pnl"] for t in losses) / len(losses) if losses else 0
    
    gross_win = sum(t["option_pnl"] for t in wins) if wins else 0
    gross_loss = abs(sum(t["option_pnl"] for t in losses)) if losses else 1
    pf = gross_win / gross_loss if gross_loss > 0 else 0
    
    print(f"\n  📈 RESULTS:")
    print(f"     Trades: {len(trades)} | Wins: {len(wins)} | Losses: {len(losses)}")
    print(f"     Win Rate: {win_rate:.1f}%")
    print(f"     Avg Win: +{avg_win:.1f}% | Avg Loss: {avg_loss:.1f}%")
    print(f"     Profit Factor: {pf:.2f}")
    print(f"     Total P/L: {total_pnl:+.0f}%")
    
    longs = [t for t in trades if t["direction"] == "LONG"]
    shorts = [t for t in trades if t["direction"] == "SHORT"]
    long_wr = len([t for t in longs if t.get("option_pnl", 0) > 0]) / len(longs) * 100 if longs else 0
    short_wr = len([t for t in shorts if t.get("option_pnl", 0) > 0]) / len(shorts) * 100 if shorts else 0
    
    print(f"     Longs: {len(longs)} ({long_wr:.0f}% WR)")
    print(f"     Shorts: {len(shorts)} ({short_wr:.0f}% WR)")
    
    return {
        "symbol": symbol,
        "interval": interval,
        "trades": len(trades),
        "win_rate": win_rate,
        "profit_factor": pf,
        "total_pnl": total_pnl,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "trade_list": trades
    }


def run_full():
    """Run on all symbols, both timeframes."""
    print("\n" + "=" * 60)
    print("🧪 TITAN INTRADAY BACKTESTER")
    print("=" * 60)
    print("Timeframes: 15min and 30min")
    print("Period: Last 20 trading days")
    print("Risk: 0.3% stop (~35% option), 0.6% target (~70% option)")
    
    all_results = []
    
    for interval in ["15min", "30min"]:
        print(f"\n{'='*60}")
        print(f"⏱️  {interval.upper()} TIMEFRAME")
        print(f"{'='*60}")
        
        for symbol in ["SPY", "QQQ", "IWM"]:
            result = run_backtest(symbol, interval, days=20)
            if result:
                all_results.append(result)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    for r in all_results:
        print(f"  {r['symbol']} {r['interval']}: {r['trades']} trades | {r['win_rate']:.0f}% WR | PF: {r['profit_factor']:.2f} | {r['total_pnl']:+.0f}%")
    
    # Totals
    total_trades = sum(r["trades"] for r in all_results)
    # Weighted win rate
    weighted_wr = sum(r["win_rate"] * r["trades"] for r in all_results) / total_trades if total_trades else 0
    total_pnl = sum(r["total_pnl"] for r in all_results)
    
    print(f"\n  TOTAL: {total_trades} trades | {weighted_wr:.0f}% WR | {total_pnl:+.0f}% P/L")


if __name__ == "__main__":
    run_full()
