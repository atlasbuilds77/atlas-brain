#!/usr/bin/env python3
"""
TITAN TRADER - Autonomous Options Trading System
Scans for setups, executes trades, manages positions
Runs 6:30am - 1:00pm PST on market days
"""

import json
import time
import requests
from datetime import datetime, timedelta
import pytz
import sys
import os

# Add to path
sys.path.insert(0, '/Users/atlasbuilds/clawd/titan-trader')
sys.path.insert(0, '/Users/atlasbuilds/clawd')

from scanner import scan_all, find_setups
from gex import scan_all_gex, format_gex_report
from executor import execute_setup, format_execution, load_positions, save_positions, check_position, get_quote

# Configuration
CONFIG = {
    "scan_interval_minutes": 15,
    "min_conviction": 3,           # Minimum conviction to trade
    "max_positions": 3,            # Max concurrent positions
    "accounts": ["hunter"],        # Accounts to trade
    "dry_run": True,               # Start in dry run mode
    "telegram_alerts": True,
    "avoid_lunch": True,           # Skip 11:30-1pm EST trades
}

# Telegram config
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "8382174210")  # Orion's ID

# Timezone
PT = pytz.timezone("America/Los_Angeles")
ET = pytz.timezone("America/New_York")


def send_telegram(message: str):
    """Send message to Telegram."""
    if not CONFIG["telegram_alerts"] or not TELEGRAM_BOT_TOKEN:
        print(f"[TELEGRAM] {message}")
        return
    
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            data={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "HTML"
            },
            timeout=10
        )
    except Exception as e:
        print(f"[TELEGRAM ERROR] {e}")


def is_market_open() -> bool:
    """Check if market is currently open."""
    now_et = datetime.now(ET)
    
    # Weekday check (0=Monday, 6=Sunday)
    if now_et.weekday() >= 5:
        return False
    
    # Hours check (9:30am - 4:00pm ET)
    market_open = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now_et.replace(hour=16, minute=0, second=0, microsecond=0)
    
    return market_open <= now_et <= market_close


def is_lunch_hour() -> bool:
    """Check if it's lunch hour chop zone."""
    now_et = datetime.now(ET)
    lunch_start = now_et.replace(hour=11, minute=30, second=0, microsecond=0)
    lunch_end = now_et.replace(hour=13, minute=0, second=0, microsecond=0)
    return lunch_start <= now_et <= lunch_end


def manage_positions() -> list:
    """Check all open positions for stops/targets."""
    positions = load_positions()
    actions = []
    
    for pos in positions:
        if pos["status"] != "OPEN":
            continue
        
        # Get current option price
        option_sym = pos["option_symbol"]
        underlying = option_sym.split()[0] if " " in option_sym else pos.get("setup", {}).get("ticker", "")
        
        # For options, we need to get the option quote
        # This is simplified - would need actual option quote
        quote = get_quote(underlying)
        if not quote:
            continue
        
        # Estimate option price movement (simplified)
        # In reality, would fetch actual option price
        spot = quote.get("last", 0)
        entry_spot = pos.get("setup", {}).get("current_price", spot)
        
        if entry_spot > 0:
            spot_change = (spot - entry_spot) / entry_spot
            # Options move ~2-3x underlying (rough delta)
            estimated_option_price = pos["entry_price"] * (1 + spot_change * 2.5)
            
            action = check_position(pos, estimated_option_price)
            
            if action["action"] in ["STOP_OUT", "TAKE_PROFIT"]:
                actions.append(action)
                
                # Update position
                if action["action"] == "STOP_OUT":
                    pos["status"] = "STOPPED"
                    pos["exit_price"] = estimated_option_price
                    pos["pnl"] = (estimated_option_price - pos["entry_price"]) * pos["remaining"] * 100
                    
                    msg = f"🛑 STOPPED OUT: {underlying}\n"
                    msg += f"   Loss: {action['pnl_pct']:.1f}%\n"
                    msg += f"   P/L: ${pos['pnl']:.2f}"
                    send_telegram(msg)
                    
                elif action["action"] == "TAKE_PROFIT":
                    target = action["target"]
                    qty = action["qty"]
                    
                    target["hit"] = True
                    pos["remaining"] -= qty
                    
                    if pos["remaining"] <= 0:
                        pos["status"] = "CLOSED"
                    
                    # Move stop to breakeven after first target
                    if target["pct"] == 0.30:
                        pos["stop_price"] = pos["entry_price"]
                    
                    msg = f"🎯 TARGET HIT: {underlying} +{target['pct']*100:.0f}%\n"
                    msg += f"   Sold {qty} contracts\n"
                    msg += f"   Remaining: {pos['remaining']}"
                    send_telegram(msg)
    
    save_positions(positions)
    return actions


def run_scan_cycle():
    """Run one full scan cycle."""
    print(f"\n{'='*60}")
    print(f"🔍 TITAN SCAN - {datetime.now(PT).strftime('%Y-%m-%d %H:%M:%S PT')}")
    print(f"{'='*60}")
    
    # Check for lunch hour
    if CONFIG["avoid_lunch"] and is_lunch_hour():
        print("⏸️  Lunch hour - skipping scan (chop zone)")
        return
    
    # First manage existing positions
    print("\n📊 Checking positions...")
    actions = manage_positions()
    if actions:
        print(f"   Executed {len(actions)} position actions")
    
    # Check if we can take new positions
    positions = load_positions()
    open_positions = [p for p in positions if p["status"] == "OPEN"]
    
    if len(open_positions) >= CONFIG["max_positions"]:
        print(f"⚠️  Max positions reached ({len(open_positions)}/{CONFIG['max_positions']})")
        return
    
    # Run scans
    print("\n🔍 Scanning order blocks...")
    scan_data = scan_all()
    
    print("\n📊 Scanning GEX levels...")
    gex_data = scan_all_gex()
    
    # Display GEX
    for symbol, data in gex_data.items():
        above_flip = data.get("above_flip")
        flip = data.get("flip_level")
        spot = data.get("spot")
        
        if flip:
            position = "ABOVE ✅" if above_flip else "BELOW ❌"
            print(f"   {symbol}: ${spot:.2f} | Flip: ${flip:.2f} ({position})")
    
    # Find setups
    print("\n🎯 Finding setups...")
    setups = find_setups(scan_data)
    
    if not setups:
        print("   No setups found")
        return
    
    # Filter by conviction
    high_conviction = [s for s in setups if s["conviction"] >= CONFIG["min_conviction"]]
    
    if not high_conviction:
        print(f"   Found {len(setups)} setups but none with conviction >= {CONFIG['min_conviction']}")
        return
    
    # Add GEX context to setups
    for setup in high_conviction:
        ticker = setup["ticker"]
        if ticker in gex_data:
            gex = gex_data[ticker]
            setup["above_gex_flip"] = gex.get("above_flip")
            setup["gex_flip"] = gex.get("flip_level")
            
            # Adjust conviction based on GEX alignment
            if setup["direction"] == "LONG" and gex.get("above_flip"):
                setup["conviction"] = min(setup["conviction"] + 1, 5)
            elif setup["direction"] == "SHORT" and not gex.get("above_flip"):
                setup["conviction"] = min(setup["conviction"] + 1, 5)
    
    # Re-sort by updated conviction
    high_conviction.sort(key=lambda x: x["conviction"], reverse=True)
    
    # Take best setup
    best = high_conviction[0]
    
    print(f"\n🎯 BEST SETUP:")
    direction_emoji = "📈" if best["direction"] == "LONG" else "📉"
    print(f"   {direction_emoji} {best['ticker']} {best['direction']}")
    print(f"   Entry: ${best['entry_zone'][0]:.2f} - ${best['entry_zone'][1]:.2f}")
    print(f"   Confluence: {best['confluence']} TFs | RS: {best['relative_strength']:.2f}%")
    print(f"   Conviction: {'⭐' * best['conviction']} ({best['conviction']}/5)")
    
    if best.get("above_gex_flip") is not None:
        gex_status = "ABOVE ✅" if best["above_gex_flip"] else "BELOW ❌"
        print(f"   GEX Flip: ${best['gex_flip']:.2f} ({gex_status})")
    
    # Execute trade
    print(f"\n{'🧪 DRY RUN' if CONFIG['dry_run'] else '🚀 EXECUTING'}...")
    
    for account in CONFIG["accounts"]:
        result = execute_setup(best, account=account, dry_run=CONFIG["dry_run"])
        print(f"\n{format_execution(result)}")
        
        if result.get("success"):
            # Send Telegram alert
            msg = f"🎯 TITAN ALERT\n\n"
            msg += f"{direction_emoji} {best['ticker']} {best['direction']}\n"
            msg += f"Strike: ${result['strike']}\n"
            msg += f"Expiry: {result['expiry']}\n"
            msg += f"Entry: ${result['entry_price']:.2f}\n"
            msg += f"Stop: ${result['stop_price']:.2f}\n"
            msg += f"Targets: ${result['targets'][0]:.2f} / ${result['targets'][1]:.2f} / ${result['targets'][2]:.2f}\n"
            msg += f"Conviction: {'⭐' * best['conviction']}\n"
            msg += f"\n{'🧪 DRY RUN' if CONFIG['dry_run'] else '✅ LIVE'}"
            
            send_telegram(msg)


def run_main_loop():
    """Main trading loop."""
    print("\n" + "="*60)
    print("🤖 TITAN TRADER - AUTONOMOUS TRADING SYSTEM")
    print("="*60)
    print(f"Config:")
    print(f"  Scan interval: {CONFIG['scan_interval_minutes']} min")
    print(f"  Min conviction: {CONFIG['min_conviction']}/5")
    print(f"  Max positions: {CONFIG['max_positions']}")
    print(f"  Mode: {'🧪 DRY RUN' if CONFIG['dry_run'] else '🔴 LIVE'}")
    print(f"  Accounts: {CONFIG['accounts']}")
    print("="*60)
    
    send_telegram("🤖 TITAN TRADER started\nMode: " + ("🧪 DRY RUN" if CONFIG["dry_run"] else "🔴 LIVE"))
    
    while True:
        try:
            if is_market_open():
                run_scan_cycle()
            else:
                now_pt = datetime.now(PT)
                print(f"[{now_pt.strftime('%H:%M')}] Market closed - waiting...")
            
            # Sleep until next scan
            time.sleep(CONFIG["scan_interval_minutes"] * 60)
            
        except KeyboardInterrupt:
            print("\n👋 TITAN TRADER stopped by user")
            send_telegram("👋 TITAN TRADER stopped")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            send_telegram(f"❌ TITAN Error: {e}")
            time.sleep(60)  # Wait a minute before retrying


def run_once():
    """Run a single scan (for testing)."""
    run_scan_cycle()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="TITAN Autonomous Trader")
    parser.add_argument("--live", action="store_true", help="Enable live trading (default: dry run)")
    parser.add_argument("--once", action="store_true", help="Run single scan then exit")
    parser.add_argument("--accounts", nargs="+", default=["hunter"], help="Accounts to trade")
    
    args = parser.parse_args()
    
    if args.live:
        CONFIG["dry_run"] = False
        print("⚠️  LIVE TRADING ENABLED ⚠️")
    
    CONFIG["accounts"] = args.accounts
    
    if args.once:
        run_once()
    else:
        run_main_loop()
