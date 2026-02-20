#!/usr/bin/env python3
"""
TITAN Session Scanner - Detects Session Levels & Triggers Position Manager
Monitors: Pre-market high/low, Prior day high/low, Opening range
Integrates with 3-phase position manager
"""

import requests
import json
from datetime import datetime, timedelta, time as dt_time
from typing import Optional, Dict, List, Tuple
import pytz
import sys

sys.path.insert(0, '/Users/atlasbuilds/clawd/titan-trader')
sys.path.insert(0, '/Users/atlasbuilds/clawd')

from position_manager import PositionManager, Position

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
ET = pytz.timezone("America/New_York")


class SessionLevel:
    """Session level (support/resistance)"""
    def __init__(self, price: float, level_type: str, timestamp: str = None):
        self.price = price
        self.level_type = level_type  # "premarket_high", "prior_high", etc.
        self.timestamp = timestamp or datetime.now(ET).isoformat()
        self.touched = False
        self.broken = False
    
    def __repr__(self):
        return f"{self.level_type}: ${self.price:.2f}"


class SessionScanner:
    """
    Detects key session levels and triggers position manager.
    
    Levels tracked:
    - Pre-market high/low (4am-9:30am ET)
    - Prior day high/low
    - Opening range high/low (first 5/15/30 min)
    - VWAP
    """
    
    def __init__(self, position_manager: PositionManager = None):
        self.pm = position_manager or PositionManager()
        self.levels: Dict[str, List[SessionLevel]] = {}
        self.last_prices: Dict[str, float] = {}
    
    def get_premarket_levels(self, symbol: str) -> Tuple[Optional[float], Optional[float]]:
        """Get pre-market high and low (4am-9:30am ET)."""
        now = datetime.now(ET)
        
        # Pre-market is 4am-9:30am ET
        premarket_start = now.replace(hour=4, minute=0, second=0, microsecond=0)
        premarket_end = now.replace(hour=9, minute=30, second=0, microsecond=0)
        
        # If before 9:30am, use current time as end
        if now.time() < dt_time(9, 30):
            premarket_end = now
        
        # Fetch 1-min candles for pre-market
        resp = requests.get(
            "https://api.tradier.com/v1/markets/timesales",
            params={
                "symbol": symbol,
                "interval": "1min",
                "start": premarket_start.strftime("%Y-%m-%d %H:%M"),
                "end": premarket_end.strftime("%Y-%m-%d %H:%M"),
                "session_filter": "all"  # Include pre-market
            },
            headers=HEADERS,
            timeout=15
        )
        
        data = resp.json()
        series = data.get("series", {})
        if not series:
            return None, None
        
        candles = series.get("data", [])
        if isinstance(candles, dict):
            candles = [candles]
        
        if not candles:
            return None, None
        
        # Find high and low
        high = max(float(c.get("high", c.get("price", 0))) for c in candles)
        low = min(float(c.get("low", c.get("price", 0))) for c in candles)
        
        return high, low
    
    def get_prior_day_levels(self, symbol: str) -> Tuple[Optional[float], Optional[float]]:
        """Get prior trading day high and low."""
        # Get yesterday's date (accounting for weekends)
        now = datetime.now(ET)
        days_back = 1
        
        # If Monday, go back to Friday
        if now.weekday() == 0:  # Monday
            days_back = 3
        elif now.weekday() == 6:  # Sunday
            days_back = 2
        
        prior_day = now - timedelta(days=days_back)
        
        # Fetch daily candles
        resp = requests.get(
            "https://api.tradier.com/v1/markets/history",
            params={
                "symbol": symbol,
                "start": (prior_day - timedelta(days=5)).strftime("%Y-%m-%d"),
                "end": prior_day.strftime("%Y-%m-%d"),
            },
            headers=HEADERS,
            timeout=15
        )
        
        data = resp.json()
        history = data.get("history")
        if not history:
            return None, None
        
        candles = history.get("day", [])
        if isinstance(candles, dict):
            candles = [candles]
        
        if not candles:
            return None, None
        
        # Get most recent day
        last_day = candles[-1]
        high = float(last_day.get("high", 0))
        low = float(last_day.get("low", 0))
        
        return high, low
    
    def get_opening_range(self, symbol: str, minutes: int = 15) -> Tuple[Optional[float], Optional[float]]:
        """Get opening range high/low (first N minutes after 9:30am)."""
        now = datetime.now(ET)
        
        # Opening range is 9:30am - 9:30am + minutes
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        or_end = market_open + timedelta(minutes=minutes)
        
        # Only valid after opening range period
        if now < or_end:
            return None, None
        
        # Fetch 1-min candles for opening range
        resp = requests.get(
            "https://api.tradier.com/v1/markets/timesales",
            params={
                "symbol": symbol,
                "interval": "1min",
                "start": market_open.strftime("%Y-%m-%d %H:%M"),
                "end": or_end.strftime("%Y-%m-%d %H:%M"),
                "session_filter": "open"
            },
            headers=HEADERS,
            timeout=15
        )
        
        data = resp.json()
        series = data.get("series", {})
        if not series:
            return None, None
        
        candles = series.get("data", [])
        if isinstance(candles, dict):
            candles = [candles]
        
        if not candles:
            return None, None
        
        # Find high and low
        high = max(float(c.get("high", c.get("price", 0))) for c in candles)
        low = min(float(c.get("low", c.get("price", 0))) for c in candles)
        
        return high, low
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price."""
        resp = requests.get(
            f"https://api.tradier.com/v1/markets/quotes",
            params={"symbols": symbol},
            headers=HEADERS,
            timeout=10
        )
        
        data = resp.json()
        quotes = data.get("quotes", {})
        quote = quotes.get("quote", {})
        
        if isinstance(quote, list):
            quote = quote[0] if quote else {}
        
        last = quote.get("last")
        return float(last) if last else None
    
    def scan_levels(self, symbol: str) -> List[SessionLevel]:
        """Scan and identify all session levels for a symbol."""
        levels = []
        
        # Pre-market levels
        pm_high, pm_low = self.get_premarket_levels(symbol)
        if pm_high:
            levels.append(SessionLevel(pm_high, "premarket_high"))
        if pm_low:
            levels.append(SessionLevel(pm_low, "premarket_low"))
        
        # Prior day levels
        prior_high, prior_low = self.get_prior_day_levels(symbol)
        if prior_high:
            levels.append(SessionLevel(prior_high, "prior_high"))
        if prior_low:
            levels.append(SessionLevel(prior_low, "prior_low"))
        
        # Opening range levels (15-min)
        or_high, or_low = self.get_opening_range(symbol, minutes=15)
        if or_high:
            levels.append(SessionLevel(or_high, "or_high_15"))
        if or_low:
            levels.append(SessionLevel(or_low, "or_low_15"))
        
        return levels
    
    def check_level_touches(self, symbol: str, current_price: float, 
                           levels: List[SessionLevel], tolerance: float = 0.001) -> List[SessionLevel]:
        """
        Check if price touched any levels.
        
        Args:
            tolerance: % tolerance for level touch (default 0.1%)
        """
        touched_levels = []
        
        for level in levels:
            if level.touched:
                continue
            
            # Check if price within tolerance of level
            distance_pct = abs(current_price - level.price) / level.price
            
            if distance_pct <= tolerance:
                level.touched = True
                touched_levels.append(level)
        
        return touched_levels
    
    def check_level_breaks(self, symbol: str, current_price: float, 
                          prev_price: float, levels: List[SessionLevel]) -> List[SessionLevel]:
        """Check if price broke through any levels."""
        broken_levels = []
        
        for level in levels:
            if level.broken:
                continue
            
            # Check if price crossed level
            crossed = False
            if prev_price < level.price <= current_price:  # Broke up
                crossed = True
            elif prev_price > level.price >= current_price:  # Broke down
                crossed = True
            
            if crossed:
                level.broken = True
                broken_levels.append(level)
        
        return broken_levels
    
    def determine_direction(self, touched_level: SessionLevel) -> str:
        """Determine trade direction based on level type."""
        # Resistance levels → potential shorts
        # Support levels → potential longs
        
        if "high" in touched_level.level_type:
            return "short"  # Touched resistance
        elif "low" in touched_level.level_type:
            return "long"   # Touched support
        
        return "long"  # Default
    
    def scan_and_trigger(self, symbol: str) -> List[str]:
        """
        Main scan function - checks levels and triggers position manager.
        Returns list of alerts.
        """
        alerts = []
        
        # Initialize levels if not exists
        if symbol not in self.levels:
            self.levels[symbol] = self.scan_levels(symbol)
            
            if self.levels[symbol]:
                level_str = ", ".join([f"{l.level_type}=${l.price:.2f}" for l in self.levels[symbol]])
                alerts.append(f"📍 {symbol} Levels: {level_str}")
        
        # Get current price
        current_price = self.get_current_price(symbol)
        if not current_price:
            return alerts
        
        prev_price = self.last_prices.get(symbol, current_price)
        self.last_prices[symbol] = current_price
        
        levels = self.levels[symbol]
        
        # Check for level touches (potential Phase 1 entry)
        touched = self.check_level_touches(symbol, current_price, levels)
        
        for level in touched:
            # Check if we already have a position
            existing_pos = self.pm.get_position(symbol)
            
            if not existing_pos:
                # Create new position
                direction = self.determine_direction(level)
                
                # Get all level prices for targets
                level_prices = sorted([l.price for l in levels])
                
                pos = self.pm.create_position(symbol, direction, level.price, level_prices)
                
                # Trigger Phase 1
                alert = self.pm.trigger_phase_1(symbol)
                if alert:
                    alerts.append(f"🎯 Level Touch!\n{alert}")
        
        # Check for level breaks (Phase 2/3 triggers or stop outs)
        broken = self.check_level_breaks(symbol, current_price, prev_price, levels)
        
        if broken:
            for level in broken:
                alerts.append(f"⚡ {symbol} broke {level.level_type} at ${level.price:.2f}")
        
        # Update existing position
        pos_alerts = self.pm.update_position(symbol, current_price)
        alerts.extend(pos_alerts)
        
        return alerts
    
    def scan_all(self, tickers: List[str] = None) -> List[str]:
        """Scan all tickers and return combined alerts."""
        tickers = tickers or TICKERS
        all_alerts = []
        
        for ticker in tickers:
            alerts = self.scan_and_trigger(ticker)
            all_alerts.extend(alerts)
        
        return all_alerts
    
    def get_status_report(self) -> str:
        """Generate status report of all positions and levels."""
        report = ["📊 SESSION SCANNER STATUS", "=" * 50]
        
        # Positions
        positions = self.pm.get_all_positions()
        
        if positions:
            report.append("\n🎯 ACTIVE POSITIONS:")
            for symbol, pos in positions.items():
                direction_emoji = "📈" if pos.direction == "long" else "📉"
                report.append(f"\n{direction_emoji} {symbol} {pos.direction.upper()}")
                report.append(f"   Size: {pos.total_size*100:.0f}% | Created: {pos.created_at[:16]}")
                
                for phase in pos.phases:
                    status_emoji = {
                        "pending": "⏳",
                        "open": "✅",
                        "stopped": "🛑",
                        "closed": "🔒"
                    }.get(phase.status, "❓")
                    
                    report.append(f"   {status_emoji} Phase {phase.phase}: {phase.status}")
                    if phase.entry:
                        report.append(f"      Entry: ${phase.entry:.2f} | Stop: ${phase.stop:.2f}")
                        if phase.target:
                            report.append(f"      Target: ${phase.target:.2f}")
        else:
            report.append("\n⏳ No active positions")
        
        # Levels
        if self.levels:
            report.append("\n\n📍 SESSION LEVELS:")
            for symbol, levels in self.levels.items():
                report.append(f"\n{symbol}:")
                for level in levels:
                    status = "✓" if level.touched else "⚡" if level.broken else "○"
                    report.append(f"   {status} {level.level_type}: ${level.price:.2f}")
        
        return "\n".join(report)


# Example usage
if __name__ == "__main__":
    import time
    
    print("🔍 TITAN SESSION SCANNER")
    print("=" * 60)
    
    # Create scanner
    scanner = SessionScanner()
    
    # Run continuous scan
    print("\n📡 Starting continuous scan (Ctrl+C to stop)...\n")
    
    try:
        scan_count = 0
        while True:
            scan_count += 1
            print(f"\n{'='*60}")
            print(f"🔄 Scan #{scan_count} - {datetime.now(ET).strftime('%Y-%m-%d %H:%M:%S ET')}")
            print(f"{'='*60}")
            
            # Scan all tickers
            alerts = scanner.scan_all(TICKERS)
            
            # Print alerts
            if alerts:
                print("\n🚨 ALERTS:")
                for alert in alerts:
                    print(f"\n{alert}")
            else:
                print("\n✓ No alerts")
            
            # Show status every 5 scans
            if scan_count % 5 == 0:
                print(f"\n{scanner.get_status_report()}")
            
            # Sleep 30 seconds
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n\n👋 Scanner stopped")
        print(f"\n{scanner.get_status_report()}")
