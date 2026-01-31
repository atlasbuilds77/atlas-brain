#!/usr/bin/env python3
"""
Level Watcher Daemon
Monitors price alerts for key levels, alerts when crossed
"""

import sys
import os
import time
import json
import signal
import subprocess
from datetime import datetime
from pathlib import Path

try:
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockLatestQuoteRequest
except ImportError:
    print("ERROR: alpaca-py not installed. Run: pip install alpaca-py")
    sys.exit(1)

# Configuration
WATCH_FILE = '/Users/atlasbuilds/clawd/memory/trading/watch-levels.json'
LOG_FILE = '/Users/atlasbuilds/clawd/memory/trading/level-alerts.jsonl'
IMSG_SCRIPT = '/Users/atlasbuilds/clawd/tools/imsg-enhanced.sh'
IMSG_GROUP_ID = 'id:10'
CHECK_INTERVAL = 60  # Check every 60 seconds during market hours

# Market hours: 6:30 AM - 1:00 PM PST (Mon-Fri)
MARKET_OPEN_HOUR = 6
MARKET_OPEN_MINUTE = 30
MARKET_CLOSE_HOUR = 13
MARKET_CLOSE_MINUTE = 0

running = True

def signal_handler(signum, frame):
    """Handle SIGTERM gracefully"""
    global running
    log_event('info', 'Received shutdown signal')
    running = False

def log_event(level, message, data=None):
    """Log to JSONL file and console"""
    entry = {
        'timestamp': datetime.now().isoformat(),
        'level': level,
        'message': message
    }
    if data:
        entry['data'] = data
    
    # Write to log file
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    except Exception as e:
        print(f"ERROR writing to log: {e}")
    
    # Also print to console
    print(f"[{entry['timestamp']}] {level.upper()}: {message}")

def is_market_hours():
    """Check if currently within market hours (6:30 AM - 1:00 PM PST, Mon-Fri)"""
    now = datetime.now()
    
    # Check if weekend
    if now.weekday() >= 5:  # Saturday=5, Sunday=6
        return False
    
    # Check time
    current_time = now.hour * 60 + now.minute
    market_open = MARKET_OPEN_HOUR * 60 + MARKET_OPEN_MINUTE
    market_close = MARKET_CLOSE_HOUR * 60 + MARKET_CLOSE_MINUTE
    
    return market_open <= current_time < market_close

def load_watch_levels():
    """Load watch levels from JSON file"""
    if not Path(WATCH_FILE).exists():
        # Create empty watch file
        with open(WATCH_FILE, 'w') as f:
            json.dump([], f, indent=2)
        return []
    
    try:
        with open(WATCH_FILE, 'r') as f:
            levels = json.load(f)
            return levels if isinstance(levels, list) else []
    except Exception as e:
        log_event('error', f'Failed to load watch levels: {e}')
        return []

def save_watch_levels(levels):
    """Save watch levels to JSON file"""
    try:
        with open(WATCH_FILE, 'w') as f:
            json.dump(levels, f, indent=2)
    except Exception as e:
        log_event('error', f'Failed to save watch levels: {e}')

def get_current_price(client, symbol):
    """Get current price for symbol from Alpaca"""
    try:
        request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
        quotes = client.get_stock_latest_quote(request)
        
        if symbol in quotes:
            quote = quotes[symbol]
            # Return mid-price
            return (quote.ask_price + quote.bid_price) / 2
        
        return None
    except Exception as e:
        log_event('error', f'Error fetching price for {symbol}: {e}')
        return None

def check_level_crossed(current_price, watch):
    """
    Check if price has crossed watched level
    
    Returns True if crossed, False otherwise
    """
    level = watch.get('level')
    direction = watch.get('direction')  # 'above' or 'below'
    
    if direction == 'above' and current_price >= level:
        return True
    elif direction == 'below' and current_price <= level:
        return True
    
    return False

def send_alert(watch, current_price):
    """Send iMessage alert when level crossed"""
    symbol = watch.get('symbol')
    level = watch.get('level')
    direction = watch.get('direction')
    note = watch.get('note', '')
    
    message = (
        f"🚨 LEVEL ALERT: {symbol}\n\n"
        f"Price crossed {direction.upper()} ${level:.2f}\n"
        f"Current price: ${current_price:.2f}\n"
    )
    
    if note:
        message += f"\nNote: {note}"
    
    message += "\n⚡ Check chart for confirmation"
    
    try:
        subprocess.run(
            [IMSG_SCRIPT, IMSG_GROUP_ID, message],
            check=True,
            capture_output=True,
            timeout=10
        )
        log_event('alert', f'{symbol} crossed {direction} ${level:.2f} (current: ${current_price:.2f})')
        return True
    except subprocess.TimeoutExpired:
        log_event('error', f'iMessage alert timeout for {symbol}')
        return False
    except Exception as e:
        log_event('error', f'Failed to send iMessage alert: {e}')
        return False

def check_all_levels(client):
    """Check all watched levels"""
    levels = load_watch_levels()
    
    if not levels:
        return  # Nothing to watch
    
    # Group by symbol to minimize API calls
    by_symbol = {}
    for idx, watch in enumerate(levels):
        if watch.get('triggered'):
            continue  # Skip already triggered levels
        
        symbol = watch.get('symbol')
        if not symbol:
            continue
        
        if symbol not in by_symbol:
            by_symbol[symbol] = []
        
        by_symbol[symbol].append({'watch': watch, 'index': idx})
    
    if not by_symbol:
        return  # No active watches
    
    log_event('debug', f'Checking {len(by_symbol)} symbols, {sum(len(v) for v in by_symbol.values())} levels')
    
    any_triggered = False
    
    for symbol, watches in by_symbol.items():
        # Get current price
        price = get_current_price(client, symbol)
        
        if price is None:
            log_event('warning', f'Failed to get price for {symbol}')
            continue
        
        # Check each level for this symbol
        for item in watches:
            watch = item['watch']
            idx = item['index']
            
            if check_level_crossed(price, watch):
                # Level crossed!
                send_alert(watch, price)
                
                # Mark as triggered
                levels[idx]['triggered'] = True
                levels[idx]['triggered_at'] = datetime.now().isoformat()
                levels[idx]['triggered_price'] = price
                any_triggered = True
    
    # Save updated levels if any triggered
    if any_triggered:
        save_watch_levels(levels)

def main():
    """Main daemon loop"""
    global running
    
    # Setup signal handler
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    log_event('info', 'Level Watcher Daemon starting')
    log_event('info', f'Watch file: {WATCH_FILE}')
    log_event('info', f'Market hours: {MARKET_OPEN_HOUR}:{MARKET_OPEN_MINUTE:02d} - {MARKET_CLOSE_HOUR}:{MARKET_CLOSE_MINUTE:02d} PST')
    log_event('info', f'Check interval: {CHECK_INTERVAL}s')
    
    # Initialize Alpaca client
    api_key = os.getenv('ALPACA_API_KEY')
    api_secret = os.getenv('ALPACA_API_SECRET')
    
    if not api_key or not api_secret:
        log_event('error', 'ALPACA_API_KEY and ALPACA_API_SECRET must be set')
        sys.exit(1)
    
    try:
        client = StockHistoricalDataClient(api_key, api_secret)
        log_event('info', 'Alpaca client initialized')
    except Exception as e:
        log_event('error', f'Failed to initialize Alpaca client: {e}')
        sys.exit(1)
    
    # Main loop
    last_check_time = None
    
    while running:
        try:
            now = datetime.now()
            
            # Check if market hours
            if not is_market_hours():
                if last_check_time is None or (now - last_check_time).total_seconds() > 3600:
                    log_event('info', 'Outside market hours - daemon idle')
                    last_check_time = now
                time.sleep(60)  # Check every minute when market closed
                continue
            
            # Check levels
            if last_check_time is None or (now - last_check_time).total_seconds() >= CHECK_INTERVAL:
                check_all_levels(client)
                last_check_time = now
            
            # Sleep
            time.sleep(10)
        
        except Exception as e:
            log_event('error', f'Error in main loop: {e}')
            time.sleep(60)
    
    log_event('info', 'Level Watcher Daemon stopped')

if __name__ == '__main__':
    main()
