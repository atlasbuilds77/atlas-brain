#!/usr/bin/env python3
"""
TITAN Scanner - Order Block Detection on Multiple Timeframes
Scans SPY, QQQ, IWM for order blocks on 4H, 30m, 15m
Identifies strongest ticker and direction (long/short)
"""

import requests
from datetime import datetime, timedelta
from typing import Optional
import sys
sys.path.insert(0, '/Users/atlasbuilds/clawd')

# Tradier API
try:
    from trading_creds import get_tradier_token
    TRADIER_TOKEN = get_tradier_token()
except:
    TRADIER_TOKEN = "jj8L3RuSVG5MUwUpz2XHrjXjAFrq"

HEADERS = {
    "Authorization": f"Bearer {TRADIER_TOKEN}",
    "Accept": "application/json"
}

TICKERS = ["SPY", "QQQ", "IWM"]


def fetch_candles(symbol: str, interval: str = "15min", days: int = 5) -> list[dict]:
    """Fetch candle data from Tradier."""
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
        timeout=15,
    )
    
    data = resp.json()
    series = data.get("series", {})
    if not series:
        return []
    candles = series.get("data", [])
    if isinstance(candles, dict):
        candles = [candles]
    return candles


def aggregate_to_timeframe(candles_15m: list, target_minutes: int) -> list:
    """Aggregate 15m candles to higher timeframes (30m, 1H, 4H)."""
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
    """
    Detect order blocks (institutional supply/demand zones).
    
    Bullish OB: Last down candle before explosive up move
    Bearish OB: Last up candle before explosive down move
    """
    if len(candles) < lookback:
        return {"demand": [], "supply": []}
    
    recent = candles[-lookback:]
    demand_zones = []  # Bullish OBs (buy zones)
    supply_zones = []  # Bearish OBs (sell zones)
    
    for i in range(2, len(recent) - 1):
        prev = recent[i - 1]
        curr = recent[i]
        next_c = recent[i + 1]
        
        # Get OHLC
        curr_open = float(curr.get("open", curr.get("price", 0)))
        curr_close = float(curr.get("close", curr.get("price", 0)))
        curr_high = float(curr.get("high", curr.get("price", 0)))
        curr_low = float(curr.get("low", curr.get("price", 0)))
        
        next_open = float(next_c.get("open", next_c.get("price", 0)))
        next_close = float(next_c.get("close", next_c.get("price", 0)))
        next_high = float(next_c.get("high", next_c.get("price", 0)))
        
        prev_close = float(prev.get("close", prev.get("price", 0)))
        
        # Candle body sizes
        curr_body = abs(curr_close - curr_open)
        next_body = abs(next_close - next_open)
        
        # Bullish OB: Down candle followed by explosive up move
        if curr_close < curr_open:  # Current is red/down
            if next_close > next_open and next_body > curr_body * 1.5:  # Next is big green
                if next_close > curr_high:  # Breaks above current high
                    demand_zones.append({
                        "high": curr_high,
                        "low": curr_low,
                        "time": curr.get("time"),
                        "strength": next_body / curr_body if curr_body > 0 else 1,
                        "mitigated": False
                    })
        
        # Bearish OB: Up candle followed by explosive down move
        if curr_close > curr_open:  # Current is green/up
            if next_close < next_open and next_body > curr_body * 1.5:  # Next is big red
                if next_close < curr_low:  # Breaks below current low
                    supply_zones.append({
                        "high": curr_high,
                        "low": curr_low,
                        "time": curr.get("time"),
                        "strength": next_body / curr_body if curr_body > 0 else 1,
                        "mitigated": False
                    })
    
    # Check if OBs are mitigated (price returned to zone)
    if recent:
        current_price = float(recent[-1].get("close", recent[-1].get("price", 0)))
        
        for ob in demand_zones:
            if current_price < ob["low"]:
                ob["mitigated"] = True
        
        for ob in supply_zones:
            if current_price > ob["high"]:
                ob["mitigated"] = True
    
    # Filter to unmitigated zones only, sort by strength
    demand_zones = [z for z in demand_zones if not z["mitigated"]]
    supply_zones = [z for z in supply_zones if not z["mitigated"]]
    
    demand_zones.sort(key=lambda x: x["strength"], reverse=True)
    supply_zones.sort(key=lambda x: x["strength"], reverse=True)
    
    return {
        "demand": demand_zones[:5],  # Top 5 demand zones
        "supply": supply_zones[:5]   # Top 5 supply zones
    }


def get_relative_strength(tickers: list) -> dict:
    """Calculate relative strength between tickers."""
    strengths = {}
    
    for ticker in tickers:
        candles = fetch_candles(ticker, "15min", days=1)
        if len(candles) < 20:
            strengths[ticker] = 0
            continue
        
        # Calculate % change over last 20 candles (~5 hours)
        start_price = float(candles[-20].get("close", candles[-20].get("price", 0)))
        end_price = float(candles[-1].get("close", candles[-1].get("price", 0)))
        
        if start_price > 0:
            strengths[ticker] = ((end_price - start_price) / start_price) * 100
        else:
            strengths[ticker] = 0
    
    return strengths


def scan_all() -> dict:
    """
    Full scan of all tickers on all timeframes.
    Returns structured data for trading decisions.
    """
    results = {}
    
    for ticker in TICKERS:
        print(f"  Scanning {ticker}...")
        
        # Fetch 15m candles (base timeframe)
        candles_15m = fetch_candles(ticker, "15min", days=10)
        
        if len(candles_15m) < 50:
            print(f"    ⚠️ Not enough data for {ticker}")
            continue
        
        # Current price
        current_price = float(candles_15m[-1].get("close", candles_15m[-1].get("price", 0)))
        
        # Aggregate to higher timeframes
        candles_30m = aggregate_to_timeframe(candles_15m, 30)
        candles_4h = aggregate_to_timeframe(candles_15m, 240)
        
        # Detect order blocks on each timeframe
        ob_15m = detect_order_blocks(candles_15m)
        ob_30m = detect_order_blocks(candles_30m)
        ob_4h = detect_order_blocks(candles_4h)
        
        results[ticker] = {
            "price": current_price,
            "order_blocks": {
                "15m": ob_15m,
                "30m": ob_30m,
                "4h": ob_4h
            },
            "candles_15m": candles_15m[-10:]  # Last 10 for context
        }
    
    # Add relative strength
    rs = get_relative_strength(TICKERS)
    for ticker in results:
        results[ticker]["relative_strength"] = rs.get(ticker, 0)
    
    # Determine strongest and weakest
    sorted_tickers = sorted(rs.items(), key=lambda x: x[1], reverse=True)
    
    return {
        "tickers": results,
        "strongest": sorted_tickers[0][0] if sorted_tickers else None,
        "weakest": sorted_tickers[-1][0] if sorted_tickers else None,
        "relative_strength": rs,
        "scan_time": datetime.now().isoformat()
    }


def find_setups(scan_data: dict) -> list:
    """
    Find tradeable setups based on order block confluence.
    Returns list of setups with direction and conviction.
    """
    setups = []
    
    for ticker, data in scan_data.get("tickers", {}).items():
        price = data["price"]
        obs = data["order_blocks"]
        rs = data["relative_strength"]
        
        # Check for LONG setup (price near demand zone)
        for tf in ["4h", "30m", "15m"]:
            for demand in obs[tf].get("demand", []):
                distance_pct = ((price - demand["high"]) / price) * 100
                
                # Price within 0.5% of demand zone
                if -0.5 <= distance_pct <= 0.3:
                    # Check for confluence with other timeframes
                    confluence = 1
                    for other_tf in ["4h", "30m", "15m"]:
                        if other_tf != tf:
                            for other_demand in obs[other_tf].get("demand", []):
                                if abs(other_demand["high"] - demand["high"]) / price < 0.005:
                                    confluence += 1
                    
                    setups.append({
                        "ticker": ticker,
                        "direction": "LONG",
                        "entry_zone": (demand["low"], demand["high"]),
                        "timeframe": tf,
                        "confluence": confluence,
                        "strength": demand["strength"],
                        "relative_strength": rs,
                        "current_price": price,
                        "conviction": min(confluence + (1 if rs > 0 else 0), 5)
                    })
        
        # Check for SHORT setup (price near supply zone)
        for tf in ["4h", "30m", "15m"]:
            for supply in obs[tf].get("supply", []):
                distance_pct = ((supply["low"] - price) / price) * 100
                
                # Price within 0.5% of supply zone
                if -0.5 <= distance_pct <= 0.3:
                    # Check for confluence
                    confluence = 1
                    for other_tf in ["4h", "30m", "15m"]:
                        if other_tf != tf:
                            for other_supply in obs[other_tf].get("supply", []):
                                if abs(other_supply["low"] - supply["low"]) / price < 0.005:
                                    confluence += 1
                    
                    setups.append({
                        "ticker": ticker,
                        "direction": "SHORT",
                        "entry_zone": (supply["low"], supply["high"]),
                        "timeframe": tf,
                        "confluence": confluence,
                        "strength": supply["strength"],
                        "relative_strength": rs,
                        "current_price": price,
                        "conviction": min(confluence + (1 if rs < 0 else 0), 5)
                    })
    
    # Sort by conviction
    setups.sort(key=lambda x: x["conviction"], reverse=True)
    
    return setups


if __name__ == "__main__":
    print("🔍 TITAN SCANNER - Order Block Detection")
    print("=" * 50)
    
    scan = scan_all()
    
    print(f"\n📊 RELATIVE STRENGTH:")
    for ticker, rs in scan["relative_strength"].items():
        emoji = "🟢" if rs > 0 else "🔴"
        print(f"  {emoji} {ticker}: {rs:+.2f}%")
    
    print(f"\n💪 Strongest: {scan['strongest']}")
    print(f"😰 Weakest: {scan['weakest']}")
    
    setups = find_setups(scan)
    
    if setups:
        print(f"\n🎯 SETUPS FOUND: {len(setups)}")
        for setup in setups[:5]:
            direction_emoji = "📈" if setup["direction"] == "LONG" else "📉"
            print(f"\n  {direction_emoji} {setup['ticker']} {setup['direction']}")
            print(f"     Entry: ${setup['entry_zone'][0]:.2f} - ${setup['entry_zone'][1]:.2f}")
            print(f"     TF: {setup['timeframe']} | Confluence: {setup['confluence']}")
            print(f"     Conviction: {'⭐' * setup['conviction']}")
    else:
        print("\n⏳ No setups found - waiting for price to reach OB zones")
