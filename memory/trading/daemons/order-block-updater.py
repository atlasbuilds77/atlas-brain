#!/usr/bin/env python3
"""
Order Block Updater Daemon
Updates order blocks for watchlist every 15 minutes, alerts on NEW strong blocks
"""

import sys
import os
import time
import json
import signal
import subprocess
from datetime import datetime
from pathlib import Path

# Add order block detector to path
sys.path.insert(0, '/Users/atlasbuilds/clawd/memory/trading/order-blocks')

try:
    from order_block_detector import OrderBlockDetector
except ImportError:
    print("ERROR: Cannot import order_block_detector")
    sys.exit(1)

# Configuration
WATCHLIST = ['SPY', 'QQQ', 'AAPL', 'TSLA', 'NVDA', 'AMD', 'AMZN', 'GOOGL', 'META', 'MSFT']
UPDATE_INTERVAL = 15 * 60  # 15 minutes
CACHE_DIR = '/Users/atlasbuilds/clawd/memory/trading/order-blocks/cache'
LOG_FILE = '/Users/atlasbuilds/clawd/memory/trading/order-block-updater-log.jsonl'
IMSG_SCRIPT = '/Users/atlasbuilds/clawd/tools/imsg-enhanced.sh'
IMSG_GROUP_ID = 'id:10'

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

def get_cache_path(symbol):
    """Get cache file path for symbol"""
    return Path(CACHE_DIR) / f'{symbol}.json'

def load_cached_blocks(symbol):
    """Load previously cached order blocks for symbol"""
    cache_path = get_cache_path(symbol)
    
    if not cache_path.exists():
        return None
    
    try:
        with open(cache_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        log_event('error', f'Failed to load cache for {symbol}: {e}')
        return None

def save_cached_blocks(symbol, data):
    """Save order blocks to cache"""
    cache_path = get_cache_path(symbol)
    
    # Ensure cache directory exists
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(cache_path, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        log_event('error', f'Failed to save cache for {symbol}: {e}')

def detect_new_strong_blocks(symbol, new_blocks, old_blocks):
    """
    Detect if there are NEW strong order blocks (8+ strength)
    
    Returns list of new strong blocks not present in old data
    """
    if not new_blocks:
        return []
    
    # Get old block timestamps
    old_timestamps = set()
    if old_blocks and 'order_blocks' in old_blocks:
        for ob in old_blocks['order_blocks']:
            old_timestamps.add(ob.get('timestamp'))
    
    # Find new strong blocks
    new_strong = []
    for ob in new_blocks:
        strength = ob.get('adjusted_strength', 0)
        timestamp = ob.get('timestamp')
        
        # Check if strong and new
        if strength >= 8 and timestamp not in old_timestamps:
            new_strong.append(ob)
    
    return new_strong

def send_new_block_alert(symbol, block):
    """Send alert for newly detected strong order block"""
    ob_type = block.get('type', 'unknown')
    strength = block.get('adjusted_strength', 0)
    zone_low = block.get('zone_low', 0)
    zone_high = block.get('zone_high', 0)
    age = block.get('age_candles', 0)
    
    emoji = '🟢' if ob_type == 'bullish' else '🔴'
    
    message = (
        f"{emoji} NEW ORDER BLOCK: {symbol}\n\n"
        f"Type: {ob_type.upper()}\n"
        f"Strength: {strength:.1f}/10\n"
        f"Zone: ${zone_low:.2f} - ${zone_high:.2f}\n"
        f"Age: {age} candles\n\n"
        f"{block.get('notes', 'Strong institutional level detected')}\n\n"
        f"📊 Fresh order block identified"
    )
    
    try:
        subprocess.run(
            [IMSG_SCRIPT, IMSG_GROUP_ID, message],
            check=True,
            capture_output=True,
            timeout=10
        )
        log_event('alert', f'New strong block alert sent for {symbol}')
        return True
    except subprocess.TimeoutExpired:
        log_event('error', f'iMessage alert timeout for {symbol}')
        return False
    except Exception as e:
        log_event('error', f'Failed to send iMessage alert: {e}')
        return False

def update_symbol_blocks(detector, symbol):
    """Update order blocks for a single symbol"""
    try:
        log_event('debug', f'Updating order blocks for {symbol}...')
        
        # Detect current order blocks
        result = detector.detect(symbol, timeframe='1h', asset_type='stock')
        
        if not result:
            log_event('warning', f'No result for {symbol}')
            return
        
        # Load previous cache
        old_cache = load_cached_blocks(symbol)
        
        # Check for new strong blocks
        new_blocks = result.get('order_blocks', [])
        new_strong_blocks = detect_new_strong_blocks(symbol, new_blocks, old_cache)
        
        # Send alerts for new strong blocks
        for block in new_strong_blocks:
            log_event('info', f'NEW strong block detected: {symbol} {block["type"]} (strength: {block["adjusted_strength"]:.1f})')
            send_new_block_alert(symbol, block)
        
        # Save updated cache
        save_cached_blocks(symbol, result)
        
        log_event('info', f'Updated {symbol}: {len(new_blocks)} blocks ({len(new_strong_blocks)} new strong)')
    
    except Exception as e:
        log_event('error', f'Error updating {symbol}: {e}')

def update_all_blocks(detector):
    """Update order blocks for entire watchlist"""
    log_event('info', f'Updating order blocks for {len(WATCHLIST)} symbols')
    
    for symbol in WATCHLIST:
        update_symbol_blocks(detector, symbol)
        
        # Rate limit
        time.sleep(2)
    
    log_event('info', 'Order block update complete')

def main():
    """Main daemon loop"""
    global running
    
    # Setup signal handler
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    log_event('info', 'Order Block Updater Daemon starting')
    log_event('info', f'Watchlist: {", ".join(WATCHLIST)}')
    log_event('info', f'Cache directory: {CACHE_DIR}')
    log_event('info', f'Market hours: {MARKET_OPEN_HOUR}:{MARKET_OPEN_MINUTE:02d} - {MARKET_CLOSE_HOUR}:{MARKET_CLOSE_MINUTE:02d} PST')
    log_event('info', f'Update interval: {UPDATE_INTERVAL}s')
    
    # Initialize detector
    try:
        detector = OrderBlockDetector()
        log_event('info', 'Order block detector initialized')
    except Exception as e:
        log_event('error', f'Failed to initialize detector: {e}')
        sys.exit(1)
    
    # Main loop
    last_update_time = None
    
    while running:
        try:
            now = datetime.now()
            
            # Check if market hours
            if not is_market_hours():
                if last_update_time is None or (now - last_update_time).total_seconds() > 3600:
                    log_event('info', 'Outside market hours - daemon idle')
                    last_update_time = now
                time.sleep(60)  # Check every minute when market closed
                continue
            
            # Check if it's time to update
            if last_update_time is None or (now - last_update_time).total_seconds() >= UPDATE_INTERVAL:
                update_all_blocks(detector)
                last_update_time = now
            
            # Sleep
            time.sleep(30)
        
        except Exception as e:
            log_event('error', f'Error in main loop: {e}')
            time.sleep(60)
    
    log_event('info', 'Order Block Updater Daemon stopped')

if __name__ == '__main__':
    main()
