"""
TITAN V2 - Liquidity Level Tracker
Tracks unswiped highs/lows across multiple sessions.
Levels remain "active" until swept.
"""

import requests
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from typing import List, Optional, Tuple
from enum import Enum

POLYGON_API_KEY = "h7J74V1cd8_4NQpTxwQpudpqXWaIHMhv"

class LevelType(Enum):
    HIGH = "high"
    LOW = "low"

class LevelStatus(Enum):
    UNSWIPED = "unswiped"
    SWEPT = "swept"

@dataclass
class LiquidityLevel:
    price: float
    level_type: LevelType
    created_date: str
    session: str  # "premarket", "regular", "overnight"
    status: LevelStatus = LevelStatus.UNSWIPED
    swept_date: Optional[str] = None
    swept_time: Optional[str] = None
    
    def __str__(self):
        return f"{self.level_type.value.upper()} ${self.price:.2f} ({self.created_date} {self.session}) [{self.status.value}]"


class LiquidityTracker:
    """
    Tracks liquidity levels (unswiped highs/lows) across multiple sessions.
    """
    
    def __init__(self, symbol: str = "SPY", lookback_days: int = 10):
        self.symbol = symbol
        self.lookback_days = lookback_days
        self.levels: List[LiquidityLevel] = []
        
    def fetch_session_data(self, date: str) -> dict:
        """Fetch minute data for a single day."""
        url = f"https://api.polygon.io/v2/aggs/ticker/{self.symbol}/range/1/minute/{date}/{date}"
        params = {
            "adjusted": "true",
            "sort": "asc",
            "limit": 50000,
            "apiKey": POLYGON_API_KEY
        }
        resp = requests.get(url, params=params)
        data = resp.json()
        
        if "results" not in data:
            return {"premarket": [], "regular": [], "afterhours": []}
        
        bars = data["results"]
        
        premarket = []
        regular = []
        afterhours = []
        
        for bar in bars:
            ts = datetime.fromtimestamp(bar['t']/1000, tz=timezone.utc)
            hour_utc = ts.hour
            
            # Pre-market: 4am-9:30am ET = 9:00-14:30 UTC
            if 9 <= hour_utc < 14 or (hour_utc == 14 and ts.minute < 30):
                premarket.append(bar)
            # Regular: 9:30am-4pm ET = 14:30-21:00 UTC
            elif (hour_utc == 14 and ts.minute >= 30) or (14 < hour_utc < 21):
                regular.append(bar)
            # After-hours: 4pm-8pm ET = 21:00-01:00 UTC
            elif hour_utc >= 21 or hour_utc < 1:
                afterhours.append(bar)
                
        return {
            "premarket": premarket,
            "regular": regular,
            "afterhours": afterhours
        }
    
    def extract_levels_from_session(self, bars: list, date: str, session: str) -> List[LiquidityLevel]:
        """Extract high/low from a session."""
        if not bars:
            return []
        
        high = max(b['h'] for b in bars)
        low = min(b['l'] for b in bars)
        
        return [
            LiquidityLevel(price=high, level_type=LevelType.HIGH, created_date=date, session=session),
            LiquidityLevel(price=low, level_type=LevelType.LOW, created_date=date, session=session)
        ]
    
    def build_level_pool(self, end_date: str = None) -> List[LiquidityLevel]:
        """
        Build pool of all levels from lookback period.
        Does NOT mark swept yet - that happens in check_sweeps().
        """
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        self.levels = []
        
        print(f"Building level pool for {self.symbol} ({self.lookback_days} days back from {end_date})")
        
        for i in range(self.lookback_days, 0, -1):
            date = (end_dt - timedelta(days=i)).strftime("%Y-%m-%d")
            
            # Skip weekends
            dt = datetime.strptime(date, "%Y-%m-%d")
            if dt.weekday() >= 5:
                continue
            
            session_data = self.fetch_session_data(date)
            
            # Extract levels from each session
            for session_name, bars in session_data.items():
                if bars:
                    levels = self.extract_levels_from_session(bars, date, session_name)
                    self.levels.extend(levels)
            
            print(f"  {date}: +{sum(1 for s,b in session_data.items() if b)} sessions")
        
        print(f"Total levels: {len(self.levels)}")
        return self.levels
    
    def check_sweeps(self, through_date: str) -> List[LiquidityLevel]:
        """
        Check which levels have been swept by price action through a given date.
        Marks levels as SWEPT when price goes through them.
        """
        end_dt = datetime.strptime(through_date, "%Y-%m-%d")
        
        for level in self.levels:
            level_dt = datetime.strptime(level.created_date, "%Y-%m-%d")
            
            # Check each day after level creation
            check_dt = level_dt + timedelta(days=1)
            
            while check_dt <= end_dt:
                if check_dt.weekday() >= 5:
                    check_dt += timedelta(days=1)
                    continue
                
                date_str = check_dt.strftime("%Y-%m-%d")
                session_data = self.fetch_session_data(date_str)
                
                all_bars = session_data["premarket"] + session_data["regular"] + session_data["afterhours"]
                
                if all_bars:
                    day_high = max(b['h'] for b in all_bars)
                    day_low = min(b['l'] for b in all_bars)
                    
                    # Check if level was swept
                    if level.level_type == LevelType.HIGH and day_high > level.price:
                        level.status = LevelStatus.SWEPT
                        level.swept_date = date_str
                        
                        # Find exact time of sweep
                        for bar in all_bars:
                            if bar['h'] > level.price:
                                ts = datetime.fromtimestamp(bar['t']/1000, tz=timezone.utc)
                                level.swept_time = f"{ts.hour-5}:{ts.minute:02d} ET"
                                break
                        break
                    
                    elif level.level_type == LevelType.LOW and day_low < level.price:
                        level.status = LevelStatus.SWEPT
                        level.swept_date = date_str
                        
                        for bar in all_bars:
                            if bar['l'] < level.price:
                                ts = datetime.fromtimestamp(bar['t']/1000, tz=timezone.utc)
                                level.swept_time = f"{ts.hour-5}:{ts.minute:02d} ET"
                                break
                        break
                
                check_dt += timedelta(days=1)
        
        return self.levels
    
    def get_unswiped_levels(self, as_of_date: str = None) -> List[LiquidityLevel]:
        """Get all unswiped levels, sorted by proximity to current price."""
        return [l for l in self.levels if l.status == LevelStatus.UNSWIPED]
    
    def get_nearest_levels(self, current_price: float, count: int = 5) -> Tuple[List[LiquidityLevel], List[LiquidityLevel]]:
        """
        Get nearest unswiped levels above and below current price.
        Returns (levels_above, levels_below)
        """
        unswiped = self.get_unswiped_levels()
        
        above = sorted([l for l in unswiped if l.price > current_price], key=lambda x: x.price)
        below = sorted([l for l in unswiped if l.price < current_price], key=lambda x: -x.price)
        
        return above[:count], below[:count]
    
    def print_level_pool(self, current_price: float = None):
        """Pretty print the level pool."""
        print("\n" + "="*60)
        print(f"LIQUIDITY LEVEL POOL - {self.symbol}")
        print("="*60)
        
        unswiped = self.get_unswiped_levels()
        swept = [l for l in self.levels if l.status == LevelStatus.SWEPT]
        
        if current_price:
            above, below = self.get_nearest_levels(current_price)
            
            print(f"\nCurrent Price: ${current_price:.2f}")
            print(f"\n--- UNSWIPED ABOVE ({len(above)}) ---")
            for l in above[:5]:
                dist = ((l.price - current_price) / current_price) * 100
                print(f"  ${l.price:.2f} ({l.created_date} {l.session}) [+{dist:.2f}%]")
            
            print(f"\n--- UNSWIPED BELOW ({len(below)}) ---")
            for l in below[:5]:
                dist = ((current_price - l.price) / current_price) * 100
                print(f"  ${l.price:.2f} ({l.created_date} {l.session}) [-{dist:.2f}%]")
        
        print(f"\n--- STATS ---")
        print(f"Total Levels: {len(self.levels)}")
        print(f"Unswiped: {len(unswiped)}")
        print(f"Swept: {len(swept)}")


def find_trade_setups(symbol: str, date: str, lookback: int = 10) -> List[dict]:
    """
    Find TITAN trade setups for a given date.
    Returns list of setups with entry/exit info.
    """
    tracker = LiquidityTracker(symbol=symbol, lookback_days=lookback)
    
    # Build levels from before the target date
    end_build = (datetime.strptime(date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    tracker.build_level_pool(end_date=end_build)
    
    # Check what was swept before our target date
    tracker.check_sweeps(through_date=end_build)
    
    # Get unswiped levels going into target date
    unswiped = tracker.get_unswiped_levels()
    
    print(f"\n=== UNSWIPED LEVELS GOING INTO {date} ===")
    for l in unswiped:
        print(f"  {l}")
    
    # Now check target date for sweeps
    session_data = tracker.fetch_session_data(date)
    all_bars = session_data["premarket"] + session_data["regular"]
    
    if not all_bars:
        return []
    
    setups = []
    
    # Check each unswiped level for sweep + reclaim
    for level in unswiped:
        for i, bar in enumerate(all_bars):
            ts = datetime.fromtimestamp(bar['t']/1000, tz=timezone.utc)
            time_et = f"{ts.hour-5}:{ts.minute:02d}"
            
            # Check for HIGH sweep (for puts)
            if level.level_type == LevelType.HIGH and bar['h'] > level.price:
                # Look for reclaim below
                for j in range(i+1, min(i+10, len(all_bars))):
                    next_bar = all_bars[j]
                    if next_bar['c'] < level.price:
                        next_ts = datetime.fromtimestamp(next_bar['t']/1000, tz=timezone.utc)
                        entry_time = f"{next_ts.hour-5}:{next_ts.minute:02d}"
                        
                        # Find target (nearest unswiped low below)
                        lows_below = [l for l in unswiped if l.level_type == LevelType.LOW and l.price < level.price]
                        target = min(lows_below, key=lambda x: level.price - x.price) if lows_below else None
                        
                        setup = {
                            "type": "PUT",
                            "level_swept": level,
                            "sweep_time": time_et,
                            "entry_price": next_bar['c'],
                            "entry_time": entry_time,
                            "target": target.price if target else None,
                            "target_level": target
                        }
                        setups.append(setup)
                        break
                break
            
            # Check for LOW sweep (for calls)
            if level.level_type == LevelType.LOW and bar['l'] < level.price:
                # Look for reclaim above
                for j in range(i+1, min(i+10, len(all_bars))):
                    next_bar = all_bars[j]
                    if next_bar['c'] > level.price:
                        next_ts = datetime.fromtimestamp(next_bar['t']/1000, tz=timezone.utc)
                        entry_time = f"{next_ts.hour-5}:{next_ts.minute:02d}"
                        
                        # Find target (nearest unswiped high above)
                        highs_above = [l for l in unswiped if l.level_type == LevelType.HIGH and l.price > level.price]
                        target = min(highs_above, key=lambda x: x.price - level.price) if highs_above else None
                        
                        setup = {
                            "type": "CALL",
                            "level_swept": level,
                            "sweep_time": time_et,
                            "entry_price": next_bar['c'],
                            "entry_time": entry_time,
                            "target": target.price if target else None,
                            "target_level": target
                        }
                        setups.append(setup)
                        break
                break
    
    return setups


if __name__ == "__main__":
    # Test with QQQ on Jan 2, 2026
    print("Testing QQQ Jan 2, 2026...")
    setups = find_trade_setups("QQQ", "2026-01-02", lookback=10)
    
    print(f"\n=== TRADE SETUPS FOUND ===")
    for setup in setups:
        print(f"\n{setup['type']} SETUP:")
        print(f"  Level: {setup['level_swept']}")
        print(f"  Sweep: {setup['sweep_time']} ET")
        print(f"  Entry: ${setup['entry_price']:.2f} at {setup['entry_time']} ET")
        print(f"  Target: ${setup['target']:.2f}" if setup['target'] else "  Target: None found")
