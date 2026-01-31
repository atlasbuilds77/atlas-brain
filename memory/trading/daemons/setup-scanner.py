#!/usr/bin/env python3
"""
Continuous Setup Scanner Daemon
Scans for 9/10 or 10/10 setups during market hours using order block detector
"""

import sys
import os
import time
import json
import signal
import subprocess
from datetime import datetime, timedelta
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
SCAN_INTERVAL = 5 * 60  # 5 minutes during market hours
LOG_FILE = '/Users/atlasbuilds/clawd/memory/trading/setup-scanner-log.jsonl'
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

def send_imsg_alert(symbol, direction, strength, price, reasoning):
    """Send iMessage alert to group"""
    emoji = '🟢' if direction == 'bullish' else '🔴'
    
    message = (
        f"{emoji} SETUP ALERT: {symbol} {direction.upper()}\n\n"
        f"Strength: {strength}/10\n"
        f"Price: ${price:.2f}\n\n"
        f"Signals:\n{reasoning}\n\n"
        f"⚡ Review and confirm setup"
    )
    
    try:
        subprocess.run(
            [IMSG_SCRIPT, IMSG_GROUP_ID, message],
            check=True,
            capture_output=True,
            timeout=10
        )
        log_event('info', f'Alert sent for {symbol}')
        return True
    except subprocess.TimeoutExpired:
        log_event('error', f'iMessage alert timeout for {symbol}')
        return False
    except Exception as e:
        log_event('error', f'Failed to send iMessage alert: {e}')
        return False

def evaluate_setup(symbol, order_blocks, current_price):
    """
    Evaluate if order blocks meet 9/10 or 10/10 setup criteria
    
    Criteria:
    - Strong order blocks (8+ strength)
    - Fresh (<5 candles old)
    - Near current price (within 2%)
    """
    if not order_blocks:
        return None
    
    strong_setups = []
    
    for ob in order_blocks:
        strength = ob.get('adjusted_strength', 0)
        age = ob.get('age_candles', 999)
        zone_high = ob.get('zone_high', 0)
        zone_low = ob.get('zone_low', 0)
        ob_type = ob.get('type', '')
        
        # Check criteria
        if strength < 8:
            continue
        
        if age > 5:
            continue
        
        # Check if price is near this level (within 2%)
        zone_mid = (zone_high + zone_low) / 2
        distance_pct = abs(current_price - zone_mid) / current_price * 100
        
        if distance_pct > 2.0:
            continue
        
        # Build reasoning
        reasoning_parts = [
            f"• {ob.get('notes', 'Strong order block')}",
            f"• Zone: ${zone_low:.2f} - ${zone_high:.2f}",
            f"• Age: {age} candles (fresh)",
            f"• Volume: {ob.get('volume_ratio', 0):.1f}x average",
            f"• Impulse: {ob.get('impulse_pct', 0):.1f}%",
            f"• Distance: {distance_pct:.1f}% from current price"
        ]
        
        strong_setups.append({
            'type': ob_type,
            'strength': strength,
            'zone_high': zone_high,
            'zone_low': zone_low,
            'age': age,
            'distance_pct': distance_pct,
            'reasoning': '\n'.join(reasoning_parts)
        })
    
    # Return best setup if any found
    if strong_setups:
        # Sort by strength (descending)
        strong_setups.sort(key=lambda x: x['strength'], reverse=True)
        return strong_setups[0]
    
    return None

def scan_symbol(detector, symbol):
    """Scan a single symbol for setups"""
    try:
        log_event('debug', f'Scanning {symbol}...')
        
        # Detect order blocks (1h timeframe for swing setups)
        result = detector.detect(symbol, timeframe='1h', asset_type='stock')
        
        if not result or not result.get('order_blocks'):
            log_event('debug', f'{symbol}: No order blocks found')
            return None
        
        current_price = result.get('current_price', 0)
        order_blocks = result.get('order_blocks', [])
        
        # Evaluate setup quality
        setup = evaluate_setup(symbol, order_blocks, current_price)
        
        if setup:
            log_event('info', f'SETUP FOUND: {symbol} {setup["type"]} (strength: {setup["strength"]}/10)')
            return {
                'symbol': symbol,
                'setup': setup,
                'current_price': current_price,
                'full_analysis': result
            }
        else:
            log_event('debug', f'{symbol}: No qualifying setups')
            return None
    
    except Exception as e:
        log_event('error', f'Error scanning {symbol}: {e}')
        return None

def scan_watchlist(detector):
    """Scan entire watchlist for setups"""
    log_event('info', f'Starting watchlist scan ({len(WATCHLIST)} symbols)')
    
    setups_found = []
    
    for symbol in WATCHLIST:
        result = scan_symbol(detector, symbol)
        if result:
            setups_found.append(result)
        
        # Rate limit (be nice to API)
        time.sleep(2)
    
    # Send alerts for setups found
    for result in setups_found:
        symbol = result['symbol']
        setup = result['setup']
        price = result['current_price']
        
        send_imsg_alert(
            symbol,
            setup['type'],
            setup['strength'],
            price,
            setup['reasoning']
        )
        
        # Log setup to file
        log_event('setup', f'{symbol} {setup["type"]}', data=result)
    
    log_event('info', f'Scan complete - {len(setups_found)} setups found')

def main():
    """Main daemon loop"""
    global running
    
    # Setup signal handler
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    log_event('info', 'Setup Scanner Daemon starting')
    log_event('info', f'Watchlist: {", ".join(WATCHLIST)}')
    log_event('info', f'Market hours: {MARKET_OPEN_HOUR}:{MARKET_OPEN_MINUTE:02d} - {MARKET_CLOSE_HOUR}:{MARKET_CLOSE_MINUTE:02d} PST')
    log_event('info', f'Scan interval: {SCAN_INTERVAL}s')
    
    # Initialize detector
    try:
        detector = OrderBlockDetector()
        log_event('info', 'Order block detector initialized')
    except Exception as e:
        log_event('error', f'Failed to initialize detector: {e}')
        sys.exit(1)
    
    # Main loop
    last_scan_time = None
    
    while running:
        try:
            now = datetime.now()
            
            # Check if market hours
            if not is_market_hours():
                if last_scan_time is None or (now - last_scan_time).total_seconds() > 3600:
                    log_event('info', 'Outside market hours - daemon idle')
                    last_scan_time = now
                time.sleep(60)  # Check every minute when market closed
                continue
            
            # Check if it's time to scan
            if last_scan_time is None or (now - last_scan_time).total_seconds() >= SCAN_INTERVAL:
                scan_watchlist(detector)
                last_scan_time = now
            
            # Sleep for a bit
            time.sleep(30)
        
        except Exception as e:
            log_event('error', f'Error in main loop: {e}')
            time.sleep(60)
    
    log_event('info', 'Setup Scanner Daemon stopped')

if __name__ == '__main__':
    main()
