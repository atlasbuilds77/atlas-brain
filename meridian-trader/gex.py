#!/usr/bin/env python3
"""
TITAN GEX - Gamma Exposure Levels
Calculates key gamma levels for SPY/QQQ/IWM
Identifies flip level, call wall, put wall
"""

import requests
from datetime import datetime
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


def get_spot_price(symbol: str) -> float:
    """Get current spot price."""
    resp = requests.get(
        "https://api.tradier.com/v1/markets/quotes",
        params={"symbols": symbol},
        headers=HEADERS,
        timeout=10
    )
    
    if resp.status_code == 200:
        quote = resp.json().get("quotes", {}).get("quote", {})
        return quote.get("last", quote.get("close", 0))
    return 0


def get_nearest_expiration(symbol: str) -> str:
    """Get nearest options expiration."""
    resp = requests.get(
        "https://api.tradier.com/v1/markets/options/expirations",
        params={"symbol": symbol},
        headers=HEADERS,
        timeout=10
    )
    
    if resp.status_code == 200:
        exps = resp.json().get("expirations", {}).get("date", [])
        if exps:
            return exps[0]
    return None


def get_options_chain(symbol: str, expiration: str) -> list:
    """Get options chain with greeks."""
    resp = requests.get(
        "https://api.tradier.com/v1/markets/options/chains",
        params={
            "symbol": symbol,
            "expiration": expiration,
            "greeks": "true"
        },
        headers=HEADERS,
        timeout=15
    )
    
    if resp.status_code == 200:
        return resp.json().get("options", {}).get("option", [])
    return []


def calculate_gex(symbol: str) -> dict:
    """
    Calculate Gamma Exposure levels for a symbol.
    
    Returns:
        - flip_level: Price where GEX flips from positive to negative
        - call_wall: Highest positive GEX (resistance)
        - put_wall: Lowest negative GEX (support)
        - net_gex: Overall market positioning
    """
    spot = get_spot_price(symbol)
    if not spot:
        return None
    
    exp = get_nearest_expiration(symbol)
    if not exp:
        return None
    
    chain = get_options_chain(symbol, exp)
    if not chain:
        return None
    
    # Calculate GEX per strike
    # GEX = Gamma × OI × 100 × Spot²
    # Calls: Dealers short → positive GEX (they buy when price rises)
    # Puts: Dealers short → negative GEX (they sell when price rises)
    
    gex_by_strike = defaultdict(float)
    call_oi_by_strike = defaultdict(int)
    put_oi_by_strike = defaultdict(int)
    
    for opt in chain:
        strike = opt.get("strike", 0)
        oi = opt.get("open_interest", 0)
        greeks = opt.get("greeks", {})
        gamma = greeks.get("gamma", 0) if greeks else 0
        opt_type = opt.get("option_type", "")
        
        if not strike or not oi:
            continue
        
        # GEX calculation
        gex = gamma * oi * 100 * (spot ** 2) / 1e9  # Normalize to billions
        
        if opt_type == "call":
            gex_by_strike[strike] += gex  # Calls = positive GEX
            call_oi_by_strike[strike] = oi
        elif opt_type == "put":
            gex_by_strike[strike] -= gex  # Puts = negative GEX
            put_oi_by_strike[strike] = oi
    
    if not gex_by_strike:
        return None
    
    # Find key levels
    strikes = sorted(gex_by_strike.keys())
    
    # Flip level: Where GEX changes sign (closest to spot)
    flip_level = None
    min_flip_dist = float('inf')
    
    for i in range(len(strikes) - 1):
        s1, s2 = strikes[i], strikes[i + 1]
        g1, g2 = gex_by_strike[s1], gex_by_strike[s2]
        
        if g1 * g2 < 0:  # Sign change
            # Linear interpolation
            flip = s1 + (s2 - s1) * abs(g1) / (abs(g1) + abs(g2))
            dist = abs(flip - spot)
            if dist < min_flip_dist:
                min_flip_dist = dist
                flip_level = flip
    
    # Call wall: Strike with highest positive GEX above spot
    call_wall = None
    max_call_gex = 0
    for strike, gex in gex_by_strike.items():
        if strike >= spot and gex > max_call_gex:
            max_call_gex = gex
            call_wall = strike
    
    # Put wall: Strike with most negative GEX below spot
    put_wall = None
    min_put_gex = 0
    for strike, gex in gex_by_strike.items():
        if strike <= spot and gex < min_put_gex:
            min_put_gex = gex
            put_wall = strike
    
    # Net GEX
    net_gex = sum(gex_by_strike.values())
    
    # Key OI levels
    max_call_oi_strike = max(call_oi_by_strike, key=call_oi_by_strike.get) if call_oi_by_strike else None
    max_put_oi_strike = max(put_oi_by_strike, key=put_oi_by_strike.get) if put_oi_by_strike else None
    
    return {
        "symbol": symbol,
        "spot": spot,
        "expiration": exp,
        "flip_level": round(flip_level, 2) if flip_level else None,
        "call_wall": call_wall,
        "put_wall": put_wall,
        "net_gex": round(net_gex, 2),
        "gex_bias": "POSITIVE" if net_gex > 0 else "NEGATIVE",
        "max_call_oi": max_call_oi_strike,
        "max_put_oi": max_put_oi_strike,
        "above_flip": spot > flip_level if flip_level else None,
        "levels": dict(sorted(
            [(k, round(v, 2)) for k, v in gex_by_strike.items() if abs(k - spot) < spot * 0.05],
            key=lambda x: x[0]
        ))
    }


def scan_all_gex() -> dict:
    """Scan GEX for SPY, QQQ, IWM."""
    results = {}
    
    for symbol in ["SPY", "QQQ", "IWM"]:
        print(f"  Calculating GEX for {symbol}...")
        gex = calculate_gex(symbol)
        if gex:
            results[symbol] = gex
    
    return results


def format_gex_report(gex_data: dict) -> str:
    """Format GEX data for display."""
    if not gex_data:
        return "No GEX data available"
    
    lines = []
    lines.append(f"📊 {gex_data['symbol']} GEX LEVELS ({gex_data['expiration']})")
    lines.append(f"   Spot: ${gex_data['spot']:.2f}")
    lines.append(f"   Flip Level: ${gex_data['flip_level']:.2f}" if gex_data['flip_level'] else "   Flip Level: N/A")
    
    if gex_data['above_flip'] is not None:
        position = "ABOVE" if gex_data['above_flip'] else "BELOW"
        emoji = "🟢" if gex_data['above_flip'] else "🔴"
        lines.append(f"   {emoji} Price is {position} flip level")
    
    lines.append(f"   Call Wall: ${gex_data['call_wall']}" if gex_data['call_wall'] else "   Call Wall: N/A")
    lines.append(f"   Put Wall: ${gex_data['put_wall']}" if gex_data['put_wall'] else "   Put Wall: N/A")
    lines.append(f"   Net GEX: {gex_data['net_gex']} ({gex_data['gex_bias']})")
    
    return "\n".join(lines)


if __name__ == "__main__":
    print("📊 TITAN GEX - Gamma Exposure Scanner")
    print("=" * 50)
    
    results = scan_all_gex()
    
    for symbol, data in results.items():
        print(f"\n{format_gex_report(data)}")
