#!/usr/bin/env python3
"""
TITAN AUTO - Automated Options Day Trading
QQQ/SPY Order Blocks + GEX Wall Confluence

Runs every 15 min during market hours
Executes options trades via Tradier
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import sys
sys.path.insert(0, '/Users/atlasbuilds/clawd')

# ============================================================
# CONFIGURATION
# ============================================================

CONFIG = {
    "tickers": ["QQQ", "SPY"],  # QQQ priority, skip IWM
    "timeframe": "30min",
    "max_trades_per_day": 3,
    "max_position_size": 500,  # Max $ per trade
    "default_contracts": 2,
    "stop_loss_pct": 0.35,  # -35%
    "scale_targets": [0.30, 0.50, 0.75, 1.00],  # +30%, +50%, +75%, +100%
    "wall_proximity_pct": 0.01,  # Within 1% of wall
    "skip_lunch_start": 11,  # 11:30 ET
    "skip_lunch_end": 13,    # 1:00 PM ET
}

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

TRADIER_BASE = "https://api.tradier.com/v1"
POSITIONS_FILE = "/Users/atlasbuilds/clawd/titan-trader/positions.json"
TRADES_LOG = "/Users/atlasbuilds/clawd/titan-trader/trades.json"

# ============================================================
# DATA FETCHING
# ============================================================

def fetch_candles(symbol: str, interval: str = "30min", days: int = 5) -> List[Dict]:
    """Fetch candle data from Tradier."""
    end = datetime.now()
    start = end - timedelta(days=days)
    
    resp = requests.get(
        f"{TRADIER_BASE}/markets/timesales",
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
    
    if resp.status_code != 200:
        print(f"  ❌ Failed to fetch {symbol} candles: {resp.status_code}")
        return []
    
    data = resp.json()
    series = data.get("series", {})
    candles = series.get("data", []) if series else []
    if isinstance(candles, dict):
        candles = [candles]
    return candles


def get_quote(symbol: str) -> Optional[float]:
    """Get current price."""
    resp = requests.get(
        f"{TRADIER_BASE}/markets/quotes",
        params={"symbols": symbol},
        headers=HEADERS,
        timeout=10
    )
    if resp.status_code == 200:
        data = resp.json()
        quote = data.get("quotes", {}).get("quote", {})
        return float(quote.get("last", 0))
    return None


def get_gex_levels(symbol: str) -> Optional[Dict]:
    """Get GEX levels from options chain."""
    try:
        # Get next weekly expiry
        today = datetime.now()
        days_until_friday = (4 - today.weekday()) % 7
        if days_until_friday == 0:
            days_until_friday = 7
        next_friday = today + timedelta(days=days_until_friday)
        expiry = next_friday.strftime("%Y-%m-%d")
        
        resp = requests.get(
            f"{TRADIER_BASE}/markets/options/chains",
            params={"symbol": symbol, "expiration": expiry},
            headers=HEADERS,
            timeout=15
        )
        
        if resp.status_code == 200:
            data = resp.json()
            options = data.get("options", {}).get("option", [])
            if not options:
                return None
            
            calls = [o for o in options if o.get("option_type") == "call"]
            puts = [o for o in options if o.get("option_type") == "put"]
            
            if calls and puts:
                call_wall = max(calls, key=lambda x: x.get("open_interest", 0))
                put_wall = max(puts, key=lambda x: x.get("open_interest", 0))
                
                return {
                    "call_wall": call_wall["strike"],
                    "put_wall": put_wall["strike"],
                    "flip": (call_wall["strike"] + put_wall["strike"]) / 2,
                    "call_oi": call_wall.get("open_interest", 0),
                    "put_oi": put_wall.get("open_interest", 0),
                    "expiry": expiry
                }
    except Exception as e:
        print(f"  ⚠️ GEX fetch error: {e}")
    return None


# ============================================================
# ORDER BLOCK DETECTION
# ============================================================

def detect_order_blocks(candles: List[Dict]) -> Dict:
    """Detect supply/demand zones with first-touch tracking."""
    if len(candles) < 20:
        return {"demand": [], "supply": []}
    
    demand = []
    supply = []
    
    for i in range(10, len(candles) - 2):
        c = candles[i]
        prev = candles[i - 1]
        next1 = candles[i + 1]
        
        o = float(c.get("open", c.get("price", 0)))
        h = float(c.get("high", c.get("price", 0)))
        l = float(c.get("low", c.get("price", 0)))
        cl = float(c.get("close", c.get("price", 0)))
        
        body = abs(cl - o)
        range_size = h - l
        if range_size == 0:
            continue
        
        body_ratio = body / range_size
        
        # Bullish OB (demand zone) - strong green candle with follow-through
        if cl > o and body_ratio > 0.6:
            next_cl = float(next1.get("close", next1.get("price", 0)))
            if next_cl > h:  # Follow-through confirmed
                demand.append({
                    "idx": i,
                    "time": c.get("time"),
                    "low": l,
                    "high": o,  # OB zone is from low to open
                    "touched": False,
                    "strength": body_ratio
                })
        
        # Bearish OB (supply zone) - strong red candle with follow-through
        if cl < o and body_ratio > 0.6:
            next_cl = float(next1.get("close", next1.get("price", 0)))
            if next_cl < l:  # Follow-through confirmed
                supply.append({
                    "idx": i,
                    "time": c.get("time"),
                    "low": o,  # OB zone is from open to high
                    "high": h,
                    "touched": False,
                    "strength": body_ratio
                })
    
    # Keep only recent OBs (last 10 of each)
    return {
        "demand": demand[-10:],
        "supply": supply[-10:]
    }


def check_first_touch(price: float, zones: List[Dict], zone_type: str) -> Optional[Dict]:
    """Check if price is touching an untouched zone."""
    for zone in reversed(zones):  # Check most recent first
        if zone["touched"]:
            continue
        if zone["low"] <= price <= zone["high"]:
            return zone
    return None


# ============================================================
# TRADING EXECUTION
# ============================================================

def get_option_symbol(underlying: str, expiry: str, strike: float, option_type: str) -> str:
    """Build OCC option symbol."""
    # Format: SPY240215C00500000
    exp_date = datetime.strptime(expiry, "%Y-%m-%d").strftime("%y%m%d")
    strike_str = f"{int(strike * 1000):08d}"
    opt_type = "C" if option_type.lower() == "call" else "P"
    return f"{underlying}{exp_date}{opt_type}{strike_str}"


def find_atm_option(symbol: str, option_type: str, expiry: str = None) -> Optional[Dict]:
    """Find ATM option for trading."""
    price = get_quote(symbol)
    if not price:
        return None
    
    # Use 0DTE or next day
    if not expiry:
        today = datetime.now()
        if today.weekday() < 4:  # Mon-Thu: use today
            expiry = today.strftime("%Y-%m-%d")
        else:  # Fri: use next Monday
            expiry = (today + timedelta(days=3)).strftime("%Y-%m-%d")
    
    try:
        resp = requests.get(
            f"{TRADIER_BASE}/markets/options/chains",
            params={"symbol": symbol, "expiration": expiry},
            headers=HEADERS,
            timeout=15
        )
        
        if resp.status_code == 200:
            data = resp.json()
            options = data.get("options", {}).get("option", [])
            
            # Filter by type and find closest to ATM
            filtered = [o for o in options if o.get("option_type") == option_type]
            if filtered:
                atm = min(filtered, key=lambda x: abs(x["strike"] - price))
                return {
                    "symbol": atm["symbol"],
                    "strike": atm["strike"],
                    "bid": atm.get("bid", 0),
                    "ask": atm.get("ask", 0),
                    "expiry": expiry
                }
    except Exception as e:
        print(f"  ⚠️ Option lookup error: {e}")
    return None


def place_order(option_symbol: str, side: str, quantity: int, price: float = None) -> Optional[str]:
    """Place options order via Tradier."""
    try:
        order_data = {
            "class": "option",
            "symbol": option_symbol.split(")")[0] if ")" in option_symbol else option_symbol[:3],
            "option_symbol": option_symbol,
            "side": side,  # "buy_to_open", "sell_to_close"
            "quantity": quantity,
            "type": "market",
            "duration": "day"
        }
        
        if price:
            order_data["type"] = "limit"
            order_data["price"] = price
        
        resp = requests.post(
            f"{TRADIER_BASE}/accounts/YOUR_ACCOUNT_ID/orders",  # TODO: Add account ID
            data=order_data,
            headers={**HEADERS, "Content-Type": "application/x-www-form-urlencoded"},
            timeout=15
        )
        
        if resp.status_code == 200:
            data = resp.json()
            order_id = data.get("order", {}).get("id")
            print(f"  ✅ Order placed: {order_id}")
            return order_id
        else:
            print(f"  ❌ Order failed: {resp.text}")
    except Exception as e:
        print(f"  ❌ Order error: {e}")
    return None


def broadcast_trade(symbol: str, strike: float, expiry: str, action: str, contracts: int):
    """Broadcast trade to copy-trading relay."""
    try:
        requests.post(
            "http://localhost:8001/broadcast",
            json={
                "symbol": symbol,
                "strike": strike,
                "expiry": expiry,
                "action": action,
                "contracts": contracts,
                "source": "TITAN"
            },
            timeout=5
        )
        print(f"  📡 Broadcast sent")
    except:
        pass  # Non-critical


# ============================================================
# POSITION MANAGEMENT
# ============================================================

def load_positions() -> Dict:
    """Load current positions."""
    try:
        with open(POSITIONS_FILE, "r") as f:
            return json.load(f)
    except:
        return {"positions": [], "daily_trades": 0, "last_date": ""}


def save_positions(data: Dict):
    """Save positions."""
    with open(POSITIONS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def log_trade(trade: Dict):
    """Log trade to history."""
    try:
        with open(TRADES_LOG, "r") as f:
            trades = json.load(f)
    except:
        trades = []
    
    trades.append({**trade, "timestamp": datetime.now().isoformat()})
    
    with open(TRADES_LOG, "w") as f:
        json.dump(trades, f, indent=2)


# ============================================================
# MAIN SCANNER
# ============================================================

def scan_for_setups() -> List[Dict]:
    """Scan for trading setups."""
    setups = []
    
    for symbol in CONFIG["tickers"]:
        print(f"\n📊 Scanning {symbol}...")
        
        # Get current price
        price = get_quote(symbol)
        if not price:
            print(f"  ❌ No price data")
            continue
        print(f"  💰 Price: ${price:.2f}")
        
        # Get candles and detect OBs
        candles = fetch_candles(symbol, CONFIG["timeframe"], days=5)
        if len(candles) < 20:
            print(f"  ❌ Not enough candles")
            continue
        
        obs = detect_order_blocks(candles)
        print(f"  📦 OBs: {len(obs['demand'])} demand, {len(obs['supply'])} supply")
        
        # Get GEX levels
        gex = get_gex_levels(symbol)
        if gex:
            print(f"  📈 GEX: Put ${gex['put_wall']} | Call ${gex['call_wall']}")
        
        # Check for demand zone touch (LONG signal)
        demand_touch = check_first_touch(price, obs["demand"], "demand")
        if demand_touch:
            near_put_wall = gex and abs(price - gex["put_wall"]) / price < CONFIG["wall_proximity_pct"]
            setups.append({
                "symbol": symbol,
                "direction": "LONG",
                "zone": demand_touch,
                "price": price,
                "near_wall": near_put_wall,
                "wall_type": "put" if near_put_wall else None,
                "gex": gex
            })
            print(f"  🟢 DEMAND TOUCH @ ${price:.2f} {'(at put wall!)' if near_put_wall else ''}")
        
        # Check for supply zone touch (SHORT signal)
        supply_touch = check_first_touch(price, obs["supply"], "supply")
        if supply_touch:
            near_call_wall = gex and abs(price - gex["call_wall"]) / price < CONFIG["wall_proximity_pct"]
            setups.append({
                "symbol": symbol,
                "direction": "SHORT",
                "zone": supply_touch,
                "price": price,
                "near_wall": near_call_wall,
                "wall_type": "call" if near_call_wall else None,
                "gex": gex
            })
            print(f"  🔴 SUPPLY TOUCH @ ${price:.2f} {'(at call wall!)' if near_call_wall else ''}")
    
    return setups


def should_trade() -> bool:
    """Check if we should be trading (market hours, not lunch)."""
    now = datetime.now()
    
    # Check day of week (Mon-Fri only)
    if now.weekday() > 4:
        print("❌ Weekend - no trading")
        return False
    
    # Convert to ET (assuming PST, add 3 hours)
    et_hour = now.hour + 3
    et_minute = now.minute
    
    # Market hours: 9:30 AM - 4:00 PM ET
    if et_hour < 9 or (et_hour == 9 and et_minute < 30):
        print("❌ Pre-market")
        return False
    if et_hour >= 16:
        print("❌ After hours")
        return False
    
    # Skip lunch (11:30 - 1:00 PM ET)
    if et_hour == 11 and et_minute >= 30:
        print("⏸️ Lunch hour - skipping")
        return False
    if et_hour == 12:
        print("⏸️ Lunch hour - skipping")
        return False
    
    return True


def run_scan():
    """Main scanning loop."""
    print("\n" + "="*60)
    print(f"🔥 TITAN AUTO - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    if not should_trade():
        return
    
    # Load position state
    state = load_positions()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Reset daily counter if new day
    if state.get("last_date") != today:
        state["daily_trades"] = 0
        state["last_date"] = today
    
    # Check daily limit
    if state["daily_trades"] >= CONFIG["max_trades_per_day"]:
        print(f"📊 Daily limit reached ({CONFIG['max_trades_per_day']} trades)")
        return
    
    # Scan for setups
    setups = scan_for_setups()
    
    if not setups:
        print("\n😴 No setups found")
        return
    
    # Prioritize setups (wall confluence first, QQQ shorts preferred)
    def score_setup(s):
        score = 0
        if s["near_wall"]:
            score += 10
        if s["symbol"] == "QQQ" and s["direction"] == "SHORT":
            score += 5
        if s["symbol"] == "SPY":
            score += 2
        return score
    
    setups.sort(key=score_setup, reverse=True)
    best = setups[0]
    
    print(f"\n🎯 BEST SETUP: {best['symbol']} {best['direction']} @ ${best['price']:.2f}")
    if best["near_wall"]:
        print(f"   ⚡ AT {best['wall_type'].upper()} WALL - HIGH CONFIDENCE")
    
    # Determine option type
    option_type = "call" if best["direction"] == "LONG" else "put"
    
    # Find ATM option
    option = find_atm_option(best["symbol"], option_type, best["gex"]["expiry"] if best["gex"] else None)
    if not option:
        print("  ❌ No option found")
        return
    
    print(f"  📋 Option: {option['symbol']} @ ${option['ask']:.2f}")
    
    # Calculate position size
    contracts = CONFIG["default_contracts"]
    if best["near_wall"]:
        contracts = contracts * 2  # Size up at walls
    
    cost = option["ask"] * 100 * contracts
    if cost > CONFIG["max_position_size"]:
        contracts = int(CONFIG["max_position_size"] / (option["ask"] * 100))
    
    if contracts < 1:
        print("  ❌ Position too small")
        return
    
    print(f"  📦 Size: {contracts} contracts (${cost:.0f})")
    
    # Execute trade (commented out for safety - uncomment when ready)
    print("\n  ⚠️ DRY RUN - Would execute:")
    print(f"     BUY {contracts}x {option['symbol']}")
    print(f"     Stop: -35% | Targets: +30/50/75/100%")
    
    # Uncomment to go live:
    # order_id = place_order(option["symbol"], "buy_to_open", contracts)
    # if order_id:
    #     state["daily_trades"] += 1
    #     state["positions"].append({
    #         "symbol": option["symbol"],
    #         "contracts": contracts,
    #         "entry": option["ask"],
    #         "stop": option["ask"] * (1 - CONFIG["stop_loss_pct"]),
    #         "direction": best["direction"],
    #         "underlying": best["symbol"]
    #     })
    #     save_positions(state)
    #     broadcast_trade(best["symbol"], option["strike"], option["expiry"], "buy", contracts)
    #     log_trade({
    #         "symbol": option["symbol"],
    #         "direction": best["direction"],
    #         "contracts": contracts,
    #         "entry": option["ask"],
    #         "near_wall": best["near_wall"]
    #     })


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Enable live trading")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    args = parser.parse_args()
    
    if args.once:
        run_scan()
    else:
        import time
        print("🔥 TITAN AUTO starting - scanning every 15 minutes")
        while True:
            run_scan()
            print("\n⏳ Next scan in 15 minutes...")
            time.sleep(900)  # 15 minutes
