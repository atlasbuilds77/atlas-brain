#!/usr/bin/env python3
"""
TITAN Executor - Trade Execution via Tradier
Places options trades, manages stops/targets
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Optional
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

# Account IDs (from credentials)
ACCOUNTS = {
    "hunter": "6YB58399",
    "aman": "VA96330809",  # Aman's account token: madEKNKYeffHuxcHfBGoZSIKXywO
}

# Position file for tracking
POSITIONS_FILE = "/Users/atlasbuilds/clawd/titan-trader/positions.json"


def get_quote(symbol: str) -> dict:
    """Get current quote for symbol."""
    resp = requests.get(
        "https://api.tradier.com/v1/markets/quotes",
        params={"symbols": symbol},
        headers=HEADERS,
        timeout=10
    )
    
    if resp.status_code == 200:
        return resp.json().get("quotes", {}).get("quote", {})
    return {}


def get_nearest_expiry(symbol: str, min_dte: int = 1) -> str:
    """Get nearest expiration with minimum DTE."""
    resp = requests.get(
        "https://api.tradier.com/v1/markets/options/expirations",
        params={"symbol": symbol},
        headers=HEADERS,
        timeout=10
    )
    
    if resp.status_code == 200:
        exps = resp.json().get("expirations", {}).get("date", [])
        today = datetime.now().date()
        
        for exp in exps:
            exp_date = datetime.strptime(exp, "%Y-%m-%d").date()
            dte = (exp_date - today).days
            if dte >= min_dte:
                return exp
    return None


def find_atm_option(symbol: str, direction: str, expiry: str) -> dict:
    """Find ATM call or put option."""
    quote = get_quote(symbol)
    spot = quote.get("last", quote.get("close", 0))
    
    if not spot:
        return None
    
    # Get options chain
    resp = requests.get(
        "https://api.tradier.com/v1/markets/options/chains",
        params={
            "symbol": symbol,
            "expiration": expiry,
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
    
    # Filter by type
    opt_type = "call" if direction == "LONG" else "put"
    options = [o for o in chain if o.get("option_type") == opt_type]
    
    # Find ATM (closest to spot)
    atm = min(options, key=lambda x: abs(x.get("strike", 0) - spot))
    
    return {
        "symbol": atm.get("symbol"),
        "underlying": symbol,
        "strike": atm.get("strike"),
        "expiry": expiry,
        "type": opt_type,
        "bid": atm.get("bid"),
        "ask": atm.get("ask"),
        "last": atm.get("last"),
        "delta": atm.get("greeks", {}).get("delta"),
        "gamma": atm.get("greeks", {}).get("gamma"),
        "spot": spot
    }


def calculate_position_size(account_balance: float, risk_pct: float = 0.05) -> int:
    """Calculate number of contracts based on risk."""
    # Risk 5% of account per trade
    risk_amount = account_balance * risk_pct
    
    # Assume average option price ~$2.00
    # With -35% stop, max loss per contract = $70
    max_loss_per_contract = 70
    
    contracts = int(risk_amount / max_loss_per_contract)
    return max(1, min(contracts, 10))  # 1-10 contracts


def place_order(
    account_id: str,
    option_symbol: str,
    side: str,  # "buy_to_open", "sell_to_close"
    quantity: int,
    order_type: str = "market",
    limit_price: float = None,
    token: str = None
) -> dict:
    """Place options order via Tradier."""
    
    headers = {
        "Authorization": f"Bearer {token or TRADIER_TOKEN}",
        "Accept": "application/json"
    }
    
    data = {
        "class": "option",
        "symbol": option_symbol.split()[0],  # Underlying
        "option_symbol": option_symbol,
        "side": side,
        "quantity": quantity,
        "type": order_type,
        "duration": "day"
    }
    
    if order_type == "limit" and limit_price:
        data["price"] = limit_price
    
    resp = requests.post(
        f"https://api.tradier.com/v1/accounts/{account_id}/orders",
        data=data,
        headers=headers,
        timeout=15
    )
    
    result = resp.json()
    
    if resp.status_code == 200 and result.get("order"):
        return {
            "success": True,
            "order_id": result["order"].get("id"),
            "status": result["order"].get("status"),
            "data": result["order"]
        }
    else:
        return {
            "success": False,
            "error": result.get("errors", {}).get("error", "Unknown error"),
            "data": result
        }


def load_positions() -> list:
    """Load tracked positions from file."""
    try:
        with open(POSITIONS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []


def save_positions(positions: list):
    """Save positions to file."""
    with open(POSITIONS_FILE, 'w') as f:
        json.dump(positions, f, indent=2)


def track_position(
    account_id: str,
    option_symbol: str,
    entry_price: float,
    quantity: int,
    direction: str,
    setup: dict
) -> dict:
    """Track a new position for management."""
    
    position = {
        "id": f"{account_id}-{option_symbol}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "account_id": account_id,
        "option_symbol": option_symbol,
        "entry_price": entry_price,
        "quantity": quantity,
        "remaining": quantity,
        "direction": direction,
        "stop_price": entry_price * 0.65,  # -35% stop
        "targets": [
            {"pct": 0.30, "price": entry_price * 1.30, "qty_pct": 0.33, "hit": False},
            {"pct": 0.50, "price": entry_price * 1.50, "qty_pct": 0.33, "hit": False},
            {"pct": 0.75, "price": entry_price * 1.75, "qty_pct": 0.34, "hit": False},
        ],
        "setup": setup,
        "entry_time": datetime.now().isoformat(),
        "status": "OPEN",
        "pnl": 0
    }
    
    positions = load_positions()
    positions.append(position)
    save_positions(positions)
    
    return position


def check_position(position: dict, current_price: float) -> dict:
    """Check position against stops/targets, return action if needed."""
    
    entry = position["entry_price"]
    stop = position["stop_price"]
    remaining = position["remaining"]
    
    # Check stop loss
    if current_price <= stop:
        return {
            "action": "STOP_OUT",
            "position": position,
            "current_price": current_price,
            "pnl_pct": ((current_price - entry) / entry) * 100,
            "qty": remaining
        }
    
    # Check targets
    for target in position["targets"]:
        if not target["hit"] and current_price >= target["price"]:
            qty_to_sell = int(position["quantity"] * target["qty_pct"])
            if qty_to_sell > 0 and qty_to_sell <= remaining:
                return {
                    "action": "TAKE_PROFIT",
                    "position": position,
                    "current_price": current_price,
                    "target": target,
                    "pnl_pct": target["pct"] * 100,
                    "qty": qty_to_sell
                }
    
    return {"action": "HOLD", "position": position, "current_price": current_price}


def execute_setup(setup: dict, account: str = "hunter", dry_run: bool = False) -> dict:
    """
    Execute a trading setup.
    
    Args:
        setup: From scanner.find_setups()
        account: Account name to trade on
        dry_run: If True, don't actually place order
    
    Returns:
        Result dict with order details
    """
    
    ticker = setup["ticker"]
    direction = setup["direction"]
    
    # Get expiry (min 1 DTE to avoid 0DTE disasters)
    expiry = get_nearest_expiry(ticker, min_dte=1)
    if not expiry:
        return {"success": False, "error": "No valid expiration found"}
    
    # Find ATM option
    option = find_atm_option(ticker, direction, expiry)
    if not option:
        return {"success": False, "error": "Could not find ATM option"}
    
    # Calculate size
    contracts = calculate_position_size(10000, 0.05)  # Assume $10k, 5% risk
    
    # Entry price (use ask for market order)
    entry_price = option["ask"] or option["last"]
    
    result = {
        "ticker": ticker,
        "direction": direction,
        "option_symbol": option["symbol"],
        "strike": option["strike"],
        "expiry": expiry,
        "contracts": contracts,
        "entry_price": entry_price,
        "stop_price": entry_price * 0.65,
        "targets": [
            entry_price * 1.30,
            entry_price * 1.50,
            entry_price * 1.75
        ],
        "total_cost": entry_price * contracts * 100,
        "setup": setup,
        "dry_run": dry_run
    }
    
    if dry_run:
        result["success"] = True
        result["message"] = "DRY RUN - Order not placed"
        return result
    
    # Place order
    account_id = ACCOUNTS.get(account, ACCOUNTS["hunter"])
    order_result = place_order(
        account_id=account_id,
        option_symbol=option["symbol"],
        side="buy_to_open",
        quantity=contracts,
        order_type="market"
    )
    
    result.update(order_result)
    
    if order_result["success"]:
        # Track position for management
        track_position(
            account_id=account_id,
            option_symbol=option["symbol"],
            entry_price=entry_price,
            quantity=contracts,
            direction=direction,
            setup=setup
        )
    
    return result


def format_execution(result: dict) -> str:
    """Format execution result for display."""
    if not result.get("success"):
        return f"❌ FAILED: {result.get('error', 'Unknown error')}"
    
    direction_emoji = "📈" if result["direction"] == "LONG" else "📉"
    type_word = "CALL" if result["direction"] == "LONG" else "PUT"
    
    lines = [
        f"{'🧪 DRY RUN' if result.get('dry_run') else '✅ EXECUTED'}",
        f"{direction_emoji} {result['ticker']} ${result['strike']} {type_word} ({result['expiry']})",
        f"   Contracts: {result['contracts']}",
        f"   Entry: ${result['entry_price']:.2f}",
        f"   Stop: ${result['stop_price']:.2f} (-35%)",
        f"   Targets: ${result['targets'][0]:.2f} / ${result['targets'][1]:.2f} / ${result['targets'][2]:.2f}",
        f"   Total: ${result['total_cost']:.2f}"
    ]
    
    if result.get("order_id"):
        lines.append(f"   Order ID: {result['order_id']}")
    
    return "\n".join(lines)


if __name__ == "__main__":
    print("🔧 TITAN Executor - Test Mode")
    print("=" * 50)
    
    # Test finding ATM option
    print("\n📋 Testing ATM option finder...")
    expiry = get_nearest_expiry("QQQ", min_dte=1)
    print(f"   Nearest expiry: {expiry}")
    
    option = find_atm_option("QQQ", "LONG", expiry)
    if option:
        print(f"   Found: {option['symbol']}")
        print(f"   Strike: ${option['strike']}")
        print(f"   Bid/Ask: ${option['bid']}/{option['ask']}")
        print(f"   Delta: {option['delta']}")
