"""
TITAN V2 FULL SYSTEM
- Bidirectional (CALLS + PUTS)
- Multi-day liquidity tracking (unswiped levels)
- Sweep detection + 1-min reclaim confirmation
- Position sizing + trailing stops
"""

import requests
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from typing import List, Optional, Tuple
from enum import Enum
import json

POLYGON_API_KEY = "h7J74V1cd8_4NQpTxwQpudpqXWaIHMhv"
TRADIER_API_KEY = "jj8L3RuSVG5MUwUpz2XHrjXjAFrq"

# ============================================================
# LIQUIDITY LEVEL TRACKING
# ============================================================

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
    session: str
    status: LevelStatus = LevelStatus.UNSWIPED
    swept_date: Optional[str] = None
    
    def __repr__(self):
        return f"{self.level_type.value.upper()} ${self.price:.2f} ({self.created_date})"


class LiquidityTracker:
    def __init__(self, symbol: str, lookback_days: int = 10):
        self.symbol = symbol
        self.lookback_days = lookback_days
        self.levels: List[LiquidityLevel] = []
        self._cache = {}
    
    def _fetch_day(self, date: str) -> dict:
        if date in self._cache:
            return self._cache[date]
            
        url = f"https://api.polygon.io/v2/aggs/ticker/{self.symbol}/range/1/minute/{date}/{date}"
        params = {"adjusted": "true", "sort": "asc", "limit": 50000, "apiKey": POLYGON_API_KEY}
        
        try:
            resp = requests.get(url, params=params, timeout=30)
            data = resp.json()
            bars = data.get("results", [])
        except:
            bars = []
        
        # Split into sessions
        premarket, regular, afterhours = [], [], []
        for bar in bars:
            ts = datetime.fromtimestamp(bar['t']/1000, tz=timezone.utc)
            h = ts.hour
            m = ts.minute
            
            if h < 14 or (h == 14 and m < 30):
                premarket.append(bar)
            elif h < 21:
                regular.append(bar)
            else:
                afterhours.append(bar)
        
        result = {"premarket": premarket, "regular": regular, "afterhours": afterhours, "all": bars}
        self._cache[date] = result
        return result
    
    def build_levels(self, before_date: str) -> List[LiquidityLevel]:
        """Build level pool from lookback period, ending before target date."""
        end_dt = datetime.strptime(before_date, "%Y-%m-%d")
        self.levels = []
        
        for i in range(self.lookback_days, 0, -1):
            dt = end_dt - timedelta(days=i)
            if dt.weekday() >= 5:
                continue
            
            date_str = dt.strftime("%Y-%m-%d")
            data = self._fetch_day(date_str)
            
            for session in ["premarket", "regular"]:
                bars = data[session]
                if bars:
                    high = max(b['h'] for b in bars)
                    low = min(b['l'] for b in bars)
                    self.levels.append(LiquidityLevel(high, LevelType.HIGH, date_str, session))
                    self.levels.append(LiquidityLevel(low, LevelType.LOW, date_str, session))
        
        return self.levels
    
    def mark_swept_before(self, before_date: str):
        """Mark levels that were swept before the target date."""
        target_dt = datetime.strptime(before_date, "%Y-%m-%d")
        
        for level in self.levels:
            level_dt = datetime.strptime(level.created_date, "%Y-%m-%d")
            
            # Check each day between level creation and target
            check_dt = level_dt + timedelta(days=1)
            while check_dt < target_dt:
                if check_dt.weekday() >= 5:
                    check_dt += timedelta(days=1)
                    continue
                
                data = self._fetch_day(check_dt.strftime("%Y-%m-%d"))
                bars = data["all"]
                
                if bars:
                    if level.level_type == LevelType.HIGH:
                        if max(b['h'] for b in bars) > level.price:
                            level.status = LevelStatus.SWEPT
                            level.swept_date = check_dt.strftime("%Y-%m-%d")
                            break
                    else:
                        if min(b['l'] for b in bars) < level.price:
                            level.status = LevelStatus.SWEPT
                            level.swept_date = check_dt.strftime("%Y-%m-%d")
                            break
                
                check_dt += timedelta(days=1)
    
    def get_unswiped(self) -> List[LiquidityLevel]:
        return [l for l in self.levels if l.status == LevelStatus.UNSWIPED]
    
    def get_nearest(self, price: float) -> Tuple[List[LiquidityLevel], List[LiquidityLevel]]:
        """Get nearest unswiped levels above and below price."""
        unswiped = self.get_unswiped()
        above = sorted([l for l in unswiped if l.price > price], key=lambda x: x.price)
        below = sorted([l for l in unswiped if l.price < price], key=lambda x: -x.price)
        return above, below


# ============================================================
# TRADE DETECTION
# ============================================================

@dataclass
class TradeSetup:
    direction: str  # "CALL" or "PUT"
    symbol: str
    level_swept: LiquidityLevel
    sweep_time: str
    sweep_price: float
    entry_time: str
    entry_price: float
    target_level: Optional[LiquidityLevel]
    target_price: Optional[float]
    stop_pct: float = 0.35  # 35% stop on options


def find_setups_for_day(symbol: str, date: str, lookback: int = 10) -> List[TradeSetup]:
    """Find all TITAN setups for a given day."""
    
    tracker = LiquidityTracker(symbol, lookback)
    tracker.build_levels(date)
    tracker.mark_swept_before(date)
    
    unswiped = tracker.get_unswiped()
    if not unswiped:
        return []
    
    # Get target day's data
    data = tracker._fetch_day(date)
    bars = data["premarket"] + data["regular"]
    
    if not bars:
        return []
    
    setups = []
    levels_already_triggered = set()
    
    for i, bar in enumerate(bars):
        ts = datetime.fromtimestamp(bar['t']/1000, tz=timezone.utc)
        time_et = f"{ts.hour-5}:{ts.minute:02d}"
        
        for level in unswiped:
            if id(level) in levels_already_triggered:
                continue
            
            # HIGH SWEEP = PUT setup
            if level.level_type == LevelType.HIGH and bar['h'] > level.price:
                # Find reclaim (close below level)
                for j in range(i+1, min(i+10, len(bars))):
                    nb = bars[j]
                    if nb['c'] < level.price:
                        nts = datetime.fromtimestamp(nb['t']/1000, tz=timezone.utc)
                        entry_time = f"{nts.hour-5}:{nts.minute:02d}"
                        
                        # Find target (nearest unswiped low)
                        lows = [l for l in unswiped if l.level_type == LevelType.LOW and l.price < level.price]
                        target = min(lows, key=lambda x: level.price - x.price) if lows else None
                        
                        setup = TradeSetup(
                            direction="PUT",
                            symbol=symbol,
                            level_swept=level,
                            sweep_time=time_et,
                            sweep_price=bar['h'],
                            entry_time=entry_time,
                            entry_price=nb['c'],
                            target_level=target,
                            target_price=target.price if target else None
                        )
                        setups.append(setup)
                        levels_already_triggered.add(id(level))
                        break
                break
            
            # LOW SWEEP = CALL setup
            if level.level_type == LevelType.LOW and bar['l'] < level.price:
                # Find reclaim (close above level)
                for j in range(i+1, min(i+10, len(bars))):
                    nb = bars[j]
                    if nb['c'] > level.price:
                        nts = datetime.fromtimestamp(nb['t']/1000, tz=timezone.utc)
                        entry_time = f"{nts.hour-5}:{nts.minute:02d}"
                        
                        # Find target (nearest unswiped high)
                        highs = [l for l in unswiped if l.level_type == LevelType.HIGH and l.price > level.price]
                        target = min(highs, key=lambda x: x.price - level.price) if highs else None
                        
                        setup = TradeSetup(
                            direction="CALL",
                            symbol=symbol,
                            level_swept=level,
                            sweep_time=time_et,
                            sweep_price=bar['l'],
                            entry_time=entry_time,
                            entry_price=nb['c'],
                            target_level=target,
                            target_price=target.price if target else None
                        )
                        setups.append(setup)
                        levels_already_triggered.add(id(level))
                        break
                break
    
    return setups


# ============================================================
# TRADE SIMULATION
# ============================================================

def simulate_trade(setup: TradeSetup, date: str) -> dict:
    """Simulate a trade and return P&L."""
    
    tracker = LiquidityTracker(setup.symbol, 1)
    data = tracker._fetch_day(date)
    bars = data["premarket"] + data["regular"]
    
    # Find bars after entry
    entry_found = False
    entry_bar_idx = 0
    
    for i, bar in enumerate(bars):
        ts = datetime.fromtimestamp(bar['t']/1000, tz=timezone.utc)
        time_et = f"{ts.hour-5}:{ts.minute:02d}"
        if time_et == setup.entry_time:
            entry_found = True
            entry_bar_idx = i
            break
    
    if not entry_found:
        return {"status": "NO_ENTRY", "pnl_pct": 0}
    
    # Track trade
    entry = setup.entry_price
    target = setup.target_price
    
    max_move = 0
    max_adverse = 0
    exit_price = None
    exit_reason = None
    exit_time = None
    trailing_stop_active = False
    trailing_stop_price = None
    
    for bar in bars[entry_bar_idx+1:]:
        ts = datetime.fromtimestamp(bar['t']/1000, tz=timezone.utc)
        time_et = f"{ts.hour-5}:{ts.minute:02d}"
        
        if setup.direction == "CALL":
            current_move = (bar['h'] - entry) / entry
            adverse_move = (entry - bar['l']) / entry
            
            # Check target hit
            if target and bar['h'] >= target:
                exit_price = target
                exit_reason = "TARGET"
                exit_time = time_et
                break
            
            # Update max favorable
            if current_move > max_move:
                max_move = current_move
                
                # Activate trailing stop at +30%
                if max_move >= 0.30 and not trailing_stop_active:
                    trailing_stop_active = True
                
                if trailing_stop_active:
                    # Trail at +15% from current high
                    trailing_stop_price = entry * (1 + max_move - 0.15)
            
            # Check trailing stop
            if trailing_stop_active and bar['l'] <= trailing_stop_price:
                exit_price = trailing_stop_price
                exit_reason = "TRAIL_STOP"
                exit_time = time_et
                break
            
            # Check hard stop (-35% option value approximated as -1% SPY)
            if adverse_move >= 0.01:  # Roughly -35% on option
                exit_price = bar['l']
                exit_reason = "STOP"
                exit_time = time_et
                break
                
        else:  # PUT
            current_move = (entry - bar['l']) / entry
            adverse_move = (bar['h'] - entry) / entry
            
            # Check target hit
            if target and bar['l'] <= target:
                exit_price = target
                exit_reason = "TARGET"
                exit_time = time_et
                break
            
            if current_move > max_move:
                max_move = current_move
                
                if max_move >= 0.30 and not trailing_stop_active:
                    trailing_stop_active = True
                
                if trailing_stop_active:
                    trailing_stop_price = entry * (1 - max_move + 0.15)
            
            if trailing_stop_active and bar['h'] >= trailing_stop_price:
                exit_price = trailing_stop_price
                exit_reason = "TRAIL_STOP"
                exit_time = time_et
                break
            
            if adverse_move >= 0.01:
                exit_price = bar['h']
                exit_reason = "STOP"
                exit_time = time_et
                break
    
    # EOD exit if no other trigger
    if exit_price is None:
        last_bar = bars[-1]
        exit_price = last_bar['c']
        exit_reason = "EOD"
        ts = datetime.fromtimestamp(last_bar['t']/1000, tz=timezone.utc)
        exit_time = f"{ts.hour-5}:{ts.minute:02d}"
    
    # Calculate option P&L (rough approximation)
    if setup.direction == "CALL":
        underlying_move = (exit_price - entry) / entry
    else:
        underlying_move = (entry - exit_price) / entry
    
    # Option leverage roughly 50-100x for ATM 0DTE
    option_pnl = underlying_move * 75  # Conservative 75x
    option_pnl = max(option_pnl, -0.80)  # Max loss 80%
    
    return {
        "status": "CLOSED",
        "direction": setup.direction,
        "entry_price": entry,
        "exit_price": exit_price,
        "exit_reason": exit_reason,
        "exit_time": exit_time,
        "underlying_move_pct": underlying_move * 100,
        "option_pnl_pct": option_pnl * 100,
        "max_favorable_pct": max_move * 100
    }


# ============================================================
# BACKTEST
# ============================================================

def backtest(symbol: str, start_date: str, end_date: str, lookback: int = 10) -> dict:
    """Run backtest over date range."""
    
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    
    all_trades = []
    current_dt = start_dt
    
    print(f"\n{'='*60}")
    print(f"TITAN V2 BACKTEST - {symbol}")
    print(f"{start_date} to {end_date}")
    print(f"{'='*60}\n")
    
    while current_dt <= end_dt:
        if current_dt.weekday() >= 5:
            current_dt += timedelta(days=1)
            continue
        
        date_str = current_dt.strftime("%Y-%m-%d")
        print(f"Scanning {date_str}...", end=" ")
        
        setups = find_setups_for_day(symbol, date_str, lookback)
        
        if setups:
            for setup in setups:
                result = simulate_trade(setup, date_str)
                result["date"] = date_str
                result["setup"] = setup
                all_trades.append(result)
                
                pnl = result.get("option_pnl_pct", 0)
                direction = setup.direction
                print(f"{direction} {setup.level_swept.price:.2f} → {pnl:+.1f}%", end=" ")
            print()
        else:
            print("no setup")
        
        current_dt += timedelta(days=1)
    
    # Summary
    if not all_trades:
        print("\nNo trades found.")
        return {"trades": 0}
    
    wins = [t for t in all_trades if t.get("option_pnl_pct", 0) > 0]
    losses = [t for t in all_trades if t.get("option_pnl_pct", 0) <= 0]
    
    win_rate = len(wins) / len(all_trades) * 100
    avg_win = sum(t["option_pnl_pct"] for t in wins) / len(wins) if wins else 0
    avg_loss = sum(t["option_pnl_pct"] for t in losses) / len(losses) if losses else 0
    
    # Compound returns with 10% risk per trade
    balance = 10000
    for t in all_trades:
        pnl_pct = t.get("option_pnl_pct", 0) / 100
        position_size = balance * 0.10
        pnl_dollar = position_size * pnl_pct
        balance += pnl_dollar
    
    print(f"\n{'='*60}")
    print("RESULTS")
    print(f"{'='*60}")
    print(f"Total Trades: {len(all_trades)}")
    print(f"Wins: {len(wins)} | Losses: {len(losses)}")
    print(f"Win Rate: {win_rate:.1f}%")
    print(f"Avg Win: +{avg_win:.1f}%")
    print(f"Avg Loss: {avg_loss:.1f}%")
    print(f"\n$10K → ${balance:,.0f} (10% risk/trade)")
    print(f"Total Return: {((balance-10000)/10000)*100:.1f}%")
    
    # By direction
    calls = [t for t in all_trades if t["direction"] == "CALL"]
    puts = [t for t in all_trades if t["direction"] == "PUT"]
    
    print(f"\nBy Direction:")
    print(f"  CALLS: {len(calls)} trades, {len([c for c in calls if c['option_pnl_pct']>0])}/{len(calls)} wins")
    print(f"  PUTS:  {len(puts)} trades, {len([p for p in puts if p['option_pnl_pct']>0])}/{len(puts)} wins")
    
    return {
        "trades": len(all_trades),
        "win_rate": win_rate,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "final_balance": balance,
        "all_trades": all_trades
    }


if __name__ == "__main__":
    # Test Jan 2 QQQ
    print("\n" + "="*60)
    print("TESTING JAN 2, 2026 - QQQ")
    print("="*60)
    
    setups = find_setups_for_day("QQQ", "2026-01-02", lookback=10)
    
    for setup in setups:
        print(f"\n{setup.direction} SETUP:")
        print(f"  Level: {setup.level_swept}")
        print(f"  Sweep: {setup.sweep_time} ET @ ${setup.sweep_price:.2f}")
        print(f"  Entry: {setup.entry_time} ET @ ${setup.entry_price:.2f}")
        print(f"  Target: ${setup.target_price:.2f}" if setup.target_price else "  Target: None")
        
        result = simulate_trade(setup, "2026-01-02")
        print(f"  Result: {result['exit_reason']} @ ${result.get('exit_price', 0):.2f}")
        print(f"  Option P&L: {result.get('option_pnl_pct', 0):+.1f}%")
    
    # Full backtest
    print("\n\n")
    backtest("QQQ", "2026-01-02", "2026-02-13", lookback=10)
