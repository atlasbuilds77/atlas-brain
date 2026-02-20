#!/usr/bin/env python3
"""
Example: Integrating Position Manager with TITAN Scanner
Shows how to combine session level detection with 3-phase position management
"""

import time
from datetime import datetime
import pytz

from session_scanner import SessionScanner
from scanner import scan_all, find_setups

ET = pytz.timezone("America/New_York")


def titan_with_position_manager():
    """
    Enhanced TITAN that combines:
    1. Order block detection (original scanner)
    2. Session level monitoring (new session_scanner)
    3. 3-phase position management (new position_manager)
    """
    
    print("🤖 TITAN TRADER - Enhanced with Position Manager")
    print("=" * 60)
    
    # Create session scanner (includes position manager)
    session_scanner = SessionScanner()
    
    scan_count = 0
    
    while True:
        scan_count += 1
        print(f"\n{'='*60}")
        print(f"🔄 Scan #{scan_count} - {datetime.now(ET).strftime('%H:%M:%S ET')}")
        print(f"{'='*60}")
        
        # 1. Check session levels (fast scan - every cycle)
        print("\n📍 Checking session levels...")
        session_alerts = session_scanner.scan_all(["SPY", "QQQ", "IWM"])
        
        if session_alerts:
            print("🚨 SESSION ALERTS:")
            for alert in session_alerts:
                print(f"\n{alert}")
        
        # 2. Run full order block scan (slower - every 5 scans)
        if scan_count % 5 == 0:
            print("\n🔍 Running full order block scan...")
            
            scan_data = scan_all()
            setups = find_setups(scan_data)
            
            if setups:
                print(f"\n🎯 Found {len(setups)} order block setups:")
                for setup in setups[:3]:
                    direction = "📈" if setup["direction"] == "LONG" else "📉"
                    print(f"   {direction} {setup['ticker']} {setup['direction']}")
                    print(f"      Entry: ${setup['entry_zone'][0]:.2f}-${setup['entry_zone'][1]:.2f}")
                    print(f"      Conviction: {'⭐' * setup['conviction']}")
        
        # 3. Show position status
        if scan_count % 10 == 0:
            print(f"\n{session_scanner.get_status_report()}")
        
        # Sleep 30 seconds (adjust based on needs)
        time.sleep(30)


if __name__ == "__main__":
    try:
        titan_with_position_manager()
    except KeyboardInterrupt:
        print("\n\n👋 Scanner stopped")
