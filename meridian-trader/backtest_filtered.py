#!/usr/bin/env python3
"""
TITAN Backtester - WITH FILTERS
Tests order blocks + volume + time + confluence filters
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

# ═══════════════════════════════════════════════════════════════
# FILTERS CONFIG
# ═══════════════════════════════════════════════════════════════
FILTERS = {
    "min_volume_ratio": 1.2,      # OB candle must have 1.2x avg volume
    "skip_lunch": True,           # Skip 11:30-13:00 ET
    "skip_first_30": True,        # Skip first 30 min (9:30-10:00)
    "require_trend_align": True,  # OB must align with higher TF trend
    "min_ob_strength": 1.3,       # Impulse must be 1.3x the OB candle
    "max_trades_per_day": 3,      # Don't overtrade
    "only_strongest": True,       # Only trade strongest RS ticker
}


def fetch_intraday(symbol: str, interval: str = "15min", days: int = 20) -> list:
    """Fetch intraday candles."""
    all_candles = []
    
    for chunk in range(0, days, 5):
        end = datetime.now() - timedelta(days=chunk)
        start = end - timedelta(days=5)
        
        try:
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
                data = resp.json()
                series = data.get("series", {})
                if series:
                    candles = series.get("data", [])
                    if isinstance(candles, dict):
                        candles = [candles]
                    all_candles.extend(candles)
        except:
            continue
    
    # Dedupe and sort
    seen = set()
    unique = []
    for c in all_candles:
        t = c.get("time", "")
        if t not in seen:
            seen.add(t)
            unique.append(c)
    
    unique.sort(key=lambda x: x.get("time", ""))
    return unique


def calculate_trend(candles: list, lookback: int = 20) -> str:
    """Determine trend from recent candles."""
    if len(candles) < lookback:
        return "NEUTRAL"
    
    recent = candles[-lookback:]
    first_close = float(recent[0].get("close", recent[0].get("price", 0)))
    last_close = float(recent[-1].get("close", recent[-1].get("price", 0)))
    
    change = (last_close - first_close) / first_close
    
    if change > 0.003:  # >0.3% = uptrend
        return "UP"
    elif change < -0.003:
        return "DOWN"
    return "NEUTRAL"


def is_lunch_hour(time_str: str) -> bool:
    """Check if time is during lunch chop (11:30-13:00 ET)."""
    # Time format: "2026-02-13T12:30:00"
    try:
        if "T" in time_str:
            hour_min = time_str.split("T")[1][:5]
            hour = int(hour_min.split(":")[0])
            minute = int(hour_min.split(":")[1])
            
            # 11:30 to 13:00
            if hour == 11 and minute >= 30:
                return True
            if hour == 12:
                return True
        return False
    except:
        return False


def is_first_30_min(time_str: str) -> bool:
    """Check if time is in first 30 min (9:30-10:00 ET)."""
    try:
        if "T" in time_str:
            hour_min = time_str.split("T")[1][:5]
            hour = int(hour_min.split(":")[0])
            minute = int(hour_min.split(":")[1])
            
            if hour == 9 and minute >= 30:
                return True
        return False
    except:
        return False


def get_date(time_str: str) -> str:
    """Extract date from timestamp."""
    try:
        return time_str.split("T")[0]
    except:
        return ""


def detect_order_blocks_filtered(candles: list, filters: dict) -> dict:
    """Detect order blocks with volume and strength filters."""
    demand_zones = []
    supply_zones = []
    
    # Calculate average volume
    volumes = [int(c.get("volume", 0)) for c in candles if c.get("volume")]
    avg_volume = sum(volumes) / len(volumes) if volumes else 1
    
    for i in range(2, len(candles) - 1):
        prev = candles[i - 1]
        curr = candles[i]
        next_c = candles[i + 1]
        
        curr_open = float(curr.get("open", curr.get("price", 0)))
        curr_close = float(curr.get("close", curr.get("price", 0)))
        curr_high = float(curr.get("high", curr.get("price", 0)))
        curr_low = float(curr.get("low", curr.get("price", 0)))
        curr_volume = int(curr.get("volume", 0))
        
        next_open = float(next_c.get("open", next_c.get("price", 0)))
        next_close = float(next_c.get("close", next_c.get("price", 0)))
        next_volume = int(next_c.get("volume", 0))
        
        curr_body = abs(curr_close - curr_open)
        next_body = abs(next_close - next_open)
        
        if curr_body == 0:
            continue
        
        strength = next_body / curr_body
        
        # VOLUME FILTER: Impulse candle must have above-avg volume
        volume_ratio = next_volume / avg_volume if avg_volume > 0 else 0
        if volume_ratio < filters.get("min_volume_ratio", 1.0):
            continue
        
        # STRENGTH FILTER
        if strength < filters.get("min_ob_strength", 1.2):
            continue
        
        time_str = curr.get("time", "")
        
        # TIME FILTERS
        if filters.get("skip_lunch") and is_lunch_hour(time_str):
            continue
        if filters.get("skip_first_30") and is_first_30_min(time_str):
            continue
        
        # DEMAND (Bullish OB)
        is_red = curr_close < curr_open
        is_next_green = next_close > next_open
        
        if is_red and is_next_green:
            demand_zones.append({
                "high": curr_high,
                "low": curr_low,
                "time": time_str,
                "index": i,
                "strength": strength,
                "volume_ratio": volume_ratio,
                "touched": False
            })
        
        # SUPPLY (Bearish OB)
        is_green = curr_close > curr_open
        is_next_red = next_close < next_open
        
        if is_green and is_next_red:
            supply_zones.append({
                "high": curr_high,
                "low": curr_low,
                "time": time_str,
                "index": i,
                "strength": strength,
                "volume_ratio": volume_ratio,
                "touched": False
            })
    
    return {"demand": demand_zones, "supply": supply_zones}


def simulate_filtered(candles: list, order_blocks: dict, filters: dict,
                      stop_pct: float = 0.003,
                      target_pct: float = 0.006) -> list:
    """Simulate with all filters applied."""
    trades = []
    active_trade = None
    trades_today = defaultdict(int)
    
    OPTION_MULT = 12
    
    demand_zones = order_blocks["demand"].copy()
    supply_zones = order_blocks["supply"].copy()
    
    for i, candle in enumerate(candles):
        time_str = candle.get("time", "")
        date = get_date(time_str)
        price = float(candle.get("close", candle.get("price", 0)))
        high = float(candle.get("high", candle.get("price", 0)))
        low = float(candle.get("low", candle.get("price", 0)))
        
        # TIME FILTERS for entries
        if filters.get("skip_lunch") and is_lunch_hour(time_str):
            continue
        if filters.get("skip_first_30") and is_first_30_min(time_str):
            continue
        
        # EOD close
        if "15:30" in time_str or "15:45" in time_str:
            if active_trade:
                entry = active_trade["entry_price"]
                if active_trade["direction"] == "LONG":
                    pnl = (price - entry) / entry
                else:
                    pnl = (entry - price) / entry
                
                active_trade["exit_price"] = price
                active_trade["exit_time"] = time_str
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
                if low <= entry * (1 - stop_pct):
                    active_trade["exit_price"] = entry * (1 - stop_pct)
                    active_trade["exit_time"] = time_str
                    active_trade["result"] = "STOPPED"
                    active_trade["underlying_pnl"] = -stop_pct
                    active_trade["option_pnl"] = -stop_pct * OPTION_MULT * 100
                    trades.append(active_trade)
                    active_trade = None
                    continue
                
                if high >= entry * (1 + target_pct):
                    active_trade["exit_price"] = entry * (1 + target_pct)
                    active_trade["exit_time"] = time_str
                    active_trade["result"] = "TARGET"
                    active_trade["underlying_pnl"] = target_pct
                    active_trade["option_pnl"] = target_pct * OPTION_MULT * 100
                    trades.append(active_trade)
                    active_trade = None
                    continue
            
            elif direction == "SHORT":
                if high >= entry * (1 + stop_pct):
                    active_trade["exit_price"] = entry * (1 + stop_pct)
                    active_trade["exit_time"] = time_str
                    active_trade["result"] = "STOPPED"
                    active_trade["underlying_pnl"] = -stop_pct
                    active_trade["option_pnl"] = -stop_pct * OPTION_MULT * 100
                    trades.append(active_trade)
                    active_trade = None
                    continue
                
                if low <= entry * (1 - target_pct):
                    active_trade["exit_price"] = entry * (1 - target_pct)
                    active_trade["exit_time"] = time_str
                    active_trade["result"] = "TARGET"
                    active_trade["underlying_pnl"] = target_pct
                    active_trade["option_pnl"] = target_pct * OPTION_MULT * 100
                    trades.append(active_trade)
                    active_trade = None
                    continue
            
            continue
        
        # MAX TRADES PER DAY filter
        max_per_day = filters.get("max_trades_per_day", 999)
        if trades_today[date] >= max_per_day:
            continue
        
        # TREND ALIGNMENT filter
        trend = calculate_trend(candles[:i+1], 20)
        
        # Look for entries
        for zone in demand_zones:
            if zone["touched"] or zone["index"] >= i:
                continue
            
            # Trend filter: only LONG in uptrend or neutral
            if filters.get("require_trend_align") and trend == "DOWN":
                continue
            
            if low <= zone["high"] and high >= zone["low"]:
                zone["touched"] = True
                active_trade = {
                    "direction": "LONG",
                    "entry_price": zone["high"],
                    "entry_time": time_str,
                    "zone": zone,
                    "trend": trend,
                    "exit_price": None,
                    "exit_time": None,
                    "result": None
                }
                trades_today[date] += 1
                break
        
        if not active_trade:
            for zone in supply_zones:
                if zone["touched"] or zone["index"] >= i:
                    continue
                
                # Trend filter: only SHORT in downtrend or neutral
                if filters.get("require_trend_align") and trend == "UP":
                    continue
                
                if high >= zone["low"] and low <= zone["high"]:
                    zone["touched"] = True
                    active_trade = {
                        "direction": "SHORT",
                        "entry_price": zone["low"],
                        "entry_time": time_str,
                        "zone": zone,
                        "trend": trend,
                        "exit_price": None,
                        "exit_time": None,
                        "result": None
                    }
                    trades_today[date] += 1
                    break
    
    return trades


def run_backtest(symbol: str, filters: dict):
    """Run filtered backtest."""
    print(f"\n📊 {symbol} (30min, filtered)")
    print("-" * 40)
    
    candles = fetch_intraday(symbol, "30min", 20)
    if len(candles) < 50:
        print(f"  ❌ Not enough data")
        return None
    
    print(f"  ✓ {len(candles)} candles")
    
    obs = detect_order_blocks_filtered(candles, filters)
    print(f"  ✓ {len(obs['demand'])} demand, {len(obs['supply'])} supply (after filters)")
    
    trades = simulate_filtered(candles, obs, filters)
    print(f"  ✓ {len(trades)} trades")
    
    if not trades:
        print("  ⚠️ No trades after filters")
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
        "trades": len(trades),
        "win_rate": win_rate,
        "profit_factor": pf,
        "total_pnl": total_pnl,
        "trade_list": trades
    }


def run_full():
    """Run with all filters."""
    print("\n" + "=" * 60)
    print("🧪 TITAN FILTERED BACKTESTER")
    print("=" * 60)
    print("\nFILTERS ACTIVE:")
    for k, v in FILTERS.items():
        print(f"  ✓ {k}: {v}")
    
    all_results = []
    
    for symbol in ["SPY", "QQQ", "IWM"]:
        result = run_backtest(symbol, FILTERS)
        if result:
            all_results.append(result)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 FILTERED vs UNFILTERED COMPARISON")
    print("=" * 60)
    
    print("\nFILTERED RESULTS:")
    for r in all_results:
        emoji = "✅" if r["profit_factor"] > 1.5 else "⚠️" if r["profit_factor"] > 1 else "❌"
        print(f"  {emoji} {r['symbol']}: {r['trades']} trades | {r['win_rate']:.0f}% WR | PF: {r['profit_factor']:.2f} | {r['total_pnl']:+.0f}%")
    
    if all_results:
        total_trades = sum(r["trades"] for r in all_results)
        weighted_wr = sum(r["win_rate"] * r["trades"] for r in all_results) / total_trades if total_trades else 0
        total_pnl = sum(r["total_pnl"] for r in all_results)
        
        print(f"\n  TOTAL: {total_trades} trades | {weighted_wr:.0f}% WR | {total_pnl:+.0f}%")
    
    print("\nUNFILTERED (from previous run):")
    print("  SPY 30min: 28 trades | 39% WR | PF: 1.05")
    print("  QQQ 30min: 34 trades | 53% WR | PF: 1.67")
    print("  IWM 30min: 38 trades | 24% WR | PF: 0.58")


if __name__ == "__main__":
    run_full()
