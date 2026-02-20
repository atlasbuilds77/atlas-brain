#!/usr/bin/env python3
"""
TITAN FULL BACKTESTER
- Order Blocks (4H + 30m confluence)
- GEX levels from Tradier options
- Volume + Trend + Time filters
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


def fetch_candles(symbol: str, interval: str, days: int) -> list:
    """Fetch candles from Tradier."""
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


def aggregate_candles(candles: list, target_minutes: int) -> list:
    """Aggregate to higher timeframe."""
    if not candles:
        return []
    
    # Group by time buckets
    grouped = defaultdict(list)
    
    for c in candles:
        time_str = c.get("time", "")
        try:
            dt = datetime.fromisoformat(time_str.replace("Z", ""))
            # Round down to target interval
            bucket = dt.replace(
                minute=(dt.minute // target_minutes) * target_minutes,
                second=0, microsecond=0
            )
            grouped[bucket].append(c)
        except:
            continue
    
    aggregated = []
    for bucket in sorted(grouped.keys()):
        chunk = grouped[bucket]
        if not chunk:
            continue
        
        agg = {
            "time": bucket.isoformat(),
            "open": float(chunk[0].get("open", chunk[0].get("price", 0))),
            "high": max(float(c.get("high", c.get("price", 0))) for c in chunk),
            "low": min(float(c.get("low", c.get("price", 0))) for c in chunk),
            "close": float(chunk[-1].get("close", chunk[-1].get("price", 0))),
            "volume": sum(int(c.get("volume", 0)) for c in chunk)
        }
        aggregated.append(agg)
    
    return aggregated


def calculate_gex_for_date(symbol: str, date: str) -> dict:
    """Calculate GEX levels for a specific date using options chain."""
    # Get spot price
    resp = requests.get(
        "https://api.tradier.com/v1/markets/quotes",
        params={"symbols": symbol},
        headers=HEADERS,
        timeout=10
    )
    
    spot = 0
    if resp.status_code == 200:
        quote = resp.json().get("quotes", {}).get("quote", {})
        spot = quote.get("last", quote.get("close", 0))
    
    if not spot:
        return None
    
    # Get nearest expiration
    resp = requests.get(
        "https://api.tradier.com/v1/markets/options/expirations",
        params={"symbol": symbol},
        headers=HEADERS,
        timeout=10
    )
    
    exp = None
    if resp.status_code == 200:
        exps = resp.json().get("expirations", {}).get("date", [])
        if exps:
            exp = exps[0]
    
    if not exp:
        return None
    
    # Get options chain with greeks
    resp = requests.get(
        "https://api.tradier.com/v1/markets/options/chains",
        params={
            "symbol": symbol,
            "expiration": exp,
            "greeks": "true"
        },
        headers=HEADERS,
        timeout=15
    )
    
    if resp.status_code != 200:
        return None
    
    chain = resp.json().get("options", {}).get("option", [])
    if not chain:
        return None
    
    # Calculate GEX per strike
    gex_by_strike = defaultdict(float)
    
    for opt in chain:
        strike = opt.get("strike", 0)
        oi = opt.get("open_interest", 0)
        greeks = opt.get("greeks", {})
        gamma = greeks.get("gamma", 0) if greeks else 0
        opt_type = opt.get("option_type", "")
        
        if not strike or not oi or not gamma:
            continue
        
        gex = gamma * oi * 100 * (spot ** 2) / 1e9
        
        if opt_type == "call":
            gex_by_strike[strike] += gex
        elif opt_type == "put":
            gex_by_strike[strike] -= gex
    
    if not gex_by_strike:
        return None
    
    # Find flip level
    strikes = sorted(gex_by_strike.keys())
    flip_level = None
    
    for i in range(len(strikes) - 1):
        s1, s2 = strikes[i], strikes[i + 1]
        g1, g2 = gex_by_strike[s1], gex_by_strike[s2]
        
        if g1 * g2 < 0:
            flip = s1 + (s2 - s1) * abs(g1) / (abs(g1) + abs(g2))
            if flip_level is None or abs(flip - spot) < abs(flip_level - spot):
                flip_level = flip
    
    # Call wall (highest positive GEX above spot)
    call_wall = None
    max_gex = 0
    for strike, gex in gex_by_strike.items():
        if strike >= spot and gex > max_gex:
            max_gex = gex
            call_wall = strike
    
    # Put wall (most negative GEX below spot)
    put_wall = None
    min_gex = 0
    for strike, gex in gex_by_strike.items():
        if strike <= spot and gex < min_gex:
            min_gex = gex
            put_wall = strike
    
    return {
        "spot": spot,
        "flip_level": flip_level,
        "call_wall": call_wall,
        "put_wall": put_wall,
        "above_flip": spot > flip_level if flip_level else None
    }


def detect_order_blocks(candles: list, min_strength: float = 1.3) -> dict:
    """Detect order blocks with strength filter."""
    demand = []
    supply = []
    
    volumes = [int(c.get("volume", 0)) for c in candles if c.get("volume")]
    avg_vol = sum(volumes) / len(volumes) if volumes else 1
    
    for i in range(1, len(candles) - 1):
        curr = candles[i]
        next_c = candles[i + 1]
        
        c_open = float(curr.get("open", curr.get("price", 0)))
        c_close = float(curr.get("close", curr.get("price", 0)))
        c_high = float(curr.get("high", curr.get("price", 0)))
        c_low = float(curr.get("low", curr.get("price", 0)))
        c_vol = int(curr.get("volume", 0))
        
        n_open = float(next_c.get("open", next_c.get("price", 0)))
        n_close = float(next_c.get("close", next_c.get("price", 0)))
        n_vol = int(next_c.get("volume", 0))
        
        c_body = abs(c_close - c_open)
        n_body = abs(n_close - n_open)
        
        if c_body == 0:
            continue
        
        strength = n_body / c_body
        vol_ratio = n_vol / avg_vol if avg_vol > 0 else 0
        
        if strength < min_strength or vol_ratio < 1.2:
            continue
        
        time_str = curr.get("time", "")
        
        # Skip bad times
        if any(x in time_str for x in ["11:30", "11:45", "12:00", "12:15", "12:30", "12:45"]):
            continue
        if any(x in time_str for x in ["09:30", "09:45"]):
            continue
        
        # Demand (bullish)
        if c_close < c_open and n_close > n_open:
            demand.append({
                "high": c_high, "low": c_low, "time": time_str,
                "index": i, "strength": strength, "touched": False
            })
        
        # Supply (bearish)
        if c_close > c_open and n_close < n_open:
            supply.append({
                "high": c_high, "low": c_low, "time": time_str,
                "index": i, "strength": strength, "touched": False
            })
    
    return {"demand": demand, "supply": supply}


def check_4h_confluence(candles_30m: list, zone: dict, direction: str) -> bool:
    """Check if 30m OB aligns with 4H structure."""
    # Aggregate to 4H
    candles_4h = aggregate_candles(candles_30m, 240)
    
    if len(candles_4h) < 10:
        return True  # Not enough data, allow trade
    
    # Get 4H trend
    first_close = float(candles_4h[0].get("close", 0))
    last_close = float(candles_4h[-1].get("close", 0))
    trend = "UP" if last_close > first_close else "DOWN"
    
    # Check confluence
    if direction == "LONG" and trend == "DOWN":
        return False  # Don't long against 4H downtrend
    if direction == "SHORT" and trend == "UP":
        return False  # Don't short against 4H uptrend
    
    return True


def simulate_full(candles_30m: list, obs: dict, gex: dict) -> list:
    """Full simulation with OB + GEX + confluence."""
    trades = []
    active_trade = None
    trades_today = defaultdict(int)
    
    OPTION_MULT = 12
    stop_pct = 0.003
    target_pct = 0.006
    
    demand = obs["demand"].copy()
    supply = obs["supply"].copy()
    
    for i, candle in enumerate(candles_30m):
        time_str = candle.get("time", "")
        date = time_str.split("T")[0] if "T" in time_str else ""
        price = float(candle.get("close", candle.get("price", 0)))
        high = float(candle.get("high", candle.get("price", 0)))
        low = float(candle.get("low", candle.get("price", 0)))
        
        # EOD close
        if any(x in time_str for x in ["15:30", "15:45", "16:00"]):
            if active_trade:
                entry = active_trade["entry_price"]
                if active_trade["direction"] == "LONG":
                    pnl = (price - entry) / entry
                else:
                    pnl = (entry - price) / entry
                
                active_trade["exit_price"] = price
                active_trade["exit_time"] = time_str
                active_trade["result"] = "EOD"
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
                    active_trade["option_pnl"] = -stop_pct * OPTION_MULT * 100
                    trades.append(active_trade)
                    active_trade = None
                    continue
                
                if high >= entry * (1 + target_pct):
                    active_trade["exit_price"] = entry * (1 + target_pct)
                    active_trade["exit_time"] = time_str
                    active_trade["result"] = "TARGET"
                    active_trade["option_pnl"] = target_pct * OPTION_MULT * 100
                    trades.append(active_trade)
                    active_trade = None
                    continue
            
            elif direction == "SHORT":
                if high >= entry * (1 + stop_pct):
                    active_trade["exit_price"] = entry * (1 + stop_pct)
                    active_trade["exit_time"] = time_str
                    active_trade["result"] = "STOPPED"
                    active_trade["option_pnl"] = -stop_pct * OPTION_MULT * 100
                    trades.append(active_trade)
                    active_trade = None
                    continue
                
                if low <= entry * (1 - target_pct):
                    active_trade["exit_price"] = entry * (1 - target_pct)
                    active_trade["exit_time"] = time_str
                    active_trade["result"] = "TARGET"
                    active_trade["option_pnl"] = target_pct * OPTION_MULT * 100
                    trades.append(active_trade)
                    active_trade = None
                    continue
            
            continue
        
        # Max 3 trades per day
        if trades_today[date] >= 3:
            continue
        
        # GEX FILTER
        if gex:
            flip = gex.get("flip_level")
            above_flip = gex.get("above_flip")
            
            # For LONGS: prefer above flip level
            # For SHORTS: prefer below flip level
        
        # Look for LONG entries
        for zone in demand:
            if zone["touched"] or zone["index"] >= i:
                continue
            
            # GEX filter: prefer longs above flip
            if gex and gex.get("flip_level"):
                if price < gex["flip_level"] * 0.998:  # Below flip by 0.2%
                    continue  # Skip long below flip
            
            # 4H confluence
            if not check_4h_confluence(candles_30m[:i+1], zone, "LONG"):
                continue
            
            if low <= zone["high"] and high >= zone["low"]:
                zone["touched"] = True
                active_trade = {
                    "direction": "LONG",
                    "entry_price": zone["high"],
                    "entry_time": time_str,
                    "gex_aligned": gex.get("above_flip", None) if gex else None,
                    "exit_price": None,
                    "exit_time": None,
                    "result": None,
                    "option_pnl": 0
                }
                trades_today[date] += 1
                break
        
        # Look for SHORT entries
        if not active_trade:
            for zone in supply:
                if zone["touched"] or zone["index"] >= i:
                    continue
                
                # GEX filter: prefer shorts below flip
                if gex and gex.get("flip_level"):
                    if price > gex["flip_level"] * 1.002:  # Above flip by 0.2%
                        continue  # Skip short above flip
                
                # 4H confluence
                if not check_4h_confluence(candles_30m[:i+1], zone, "SHORT"):
                    continue
                
                if high >= zone["low"] and low <= zone["high"]:
                    zone["touched"] = True
                    active_trade = {
                        "direction": "SHORT",
                        "entry_price": zone["low"],
                        "entry_time": time_str,
                        "gex_aligned": not gex.get("above_flip", True) if gex else None,
                        "exit_price": None,
                        "exit_time": None,
                        "result": None,
                        "option_pnl": 0
                    }
                    trades_today[date] += 1
                    break
    
    return trades


def run_backtest(symbol: str):
    """Run full backtest with all filters."""
    print(f"\n📊 {symbol} (Full System)")
    print("-" * 40)
    
    # Fetch 30m data
    candles_30m = fetch_candles(symbol, "30min", 20)
    if len(candles_30m) < 50:
        print(f"  ❌ Not enough data")
        return None
    
    print(f"  ✓ {len(candles_30m)} 30m candles")
    
    # Get current GEX (we'll use this as proxy for historical)
    gex = calculate_gex_for_date(symbol, datetime.now().strftime("%Y-%m-%d"))
    if gex:
        print(f"  ✓ GEX: Flip=${gex['flip_level']:.2f}, {'ABOVE' if gex['above_flip'] else 'BELOW'}")
    else:
        print(f"  ⚠️ No GEX data (proceeding without)")
    
    # Detect OBs
    obs = detect_order_blocks(candles_30m)
    print(f"  ✓ OBs: {len(obs['demand'])} demand, {len(obs['supply'])} supply")
    
    # Simulate
    trades = simulate_full(candles_30m, obs, gex)
    print(f"  ✓ {len(trades)} trades")
    
    if not trades:
        return None
    
    wins = [t for t in trades if t.get("option_pnl", 0) > 0]
    losses = [t for t in trades if t.get("option_pnl", 0) < 0]
    
    total_pnl = sum(t.get("option_pnl", 0) for t in trades)
    win_rate = len(wins) / len(trades) * 100
    
    avg_win = sum(t["option_pnl"] for t in wins) / len(wins) if wins else 0
    avg_loss = sum(t["option_pnl"] for t in losses) / len(losses) if losses else 0
    
    gross_win = sum(t["option_pnl"] for t in wins) if wins else 0
    gross_loss = abs(sum(t["option_pnl"] for t in losses)) if losses else 1
    pf = gross_win / gross_loss if gross_loss > 0 else float('inf')
    
    # GEX alignment stats
    gex_aligned = [t for t in trades if t.get("gex_aligned") == True]
    gex_aligned_wins = [t for t in gex_aligned if t.get("option_pnl", 0) > 0]
    gex_wr = len(gex_aligned_wins) / len(gex_aligned) * 100 if gex_aligned else 0
    
    print(f"\n  📈 RESULTS:")
    print(f"     Trades: {len(trades)} | Wins: {len(wins)} | Losses: {len(losses)}")
    print(f"     Win Rate: {win_rate:.1f}%")
    print(f"     Avg Win: +{avg_win:.1f}% | Avg Loss: {avg_loss:.1f}%")
    print(f"     Profit Factor: {pf:.2f}")
    print(f"     Total P/L: {total_pnl:+.0f}%")
    
    if gex_aligned:
        print(f"     GEX-Aligned Trades: {len(gex_aligned)} ({gex_wr:.0f}% WR)")
    
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
        "gex_aligned_wr": gex_wr,
        "trade_list": trades
    }


def main():
    print("\n" + "=" * 60)
    print("🧪 TITAN FULL SYSTEM BACKTEST")
    print("=" * 60)
    print("\nSYSTEM COMPONENTS:")
    print("  ✅ Order Blocks (30m)")
    print("  ✅ 4H Trend Confluence")
    print("  ✅ GEX Alignment Filter")
    print("  ✅ Volume Confirmation")
    print("  ✅ Time Filters (skip lunch, first 30min)")
    print("  ✅ Max 3 trades/day")
    
    all_results = []
    
    for symbol in ["SPY", "QQQ", "IWM"]:
        result = run_backtest(symbol)
        if result:
            all_results.append(result)
    
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS")
    print("=" * 60)
    
    for r in all_results:
        emoji = "🔥" if r["profit_factor"] > 2 else "✅" if r["profit_factor"] > 1.5 else "⚠️"
        print(f"  {emoji} {r['symbol']}: {r['trades']} trades | {r['win_rate']:.0f}% WR | PF: {r['profit_factor']:.2f} | {r['total_pnl']:+.0f}%")
    
    if all_results:
        total_trades = sum(r["trades"] for r in all_results)
        weighted_wr = sum(r["win_rate"] * r["trades"] for r in all_results) / total_trades if total_trades else 0
        total_pnl = sum(r["total_pnl"] for r in all_results)
        
        print(f"\n  COMBINED: {total_trades} trades | {weighted_wr:.0f}% WR | {total_pnl:+.0f}%")


if __name__ == "__main__":
    main()
