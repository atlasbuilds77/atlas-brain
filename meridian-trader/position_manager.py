#!/usr/bin/env python3
"""
TITAN Position Manager - 3-Phase Scale-In System
Manages multi-phase entries with progressive position building
"""

import json
import os
from datetime import datetime
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict
from enum import Enum


class Phase(Enum):
    """Position phases"""
    PHASE_1 = 1  # Initial entry (50%)
    PHASE_2 = 2  # Add on breakout (30%)
    PHASE_3 = 3  # Runners (20%)


class PositionStatus(Enum):
    """Position status"""
    PENDING = "pending"
    OPEN = "open"
    STOPPED = "stopped"
    TARGET_HIT = "target_hit"
    CLOSED = "closed"


@dataclass
class PhaseEntry:
    """Single phase of a position"""
    phase: int
    entry: Optional[float] = None
    strike: Optional[float] = None
    size: float = 0.0
    stop: Optional[float] = None
    target: Optional[float] = None
    status: str = PositionStatus.PENDING.value
    entry_time: Optional[str] = None
    exit_time: Optional[str] = None
    exit_price: Optional[float] = None
    pnl: Optional[float] = None


@dataclass
class Position:
    """Complete multi-phase position"""
    symbol: str
    direction: str  # "long" or "short"
    phases: List[PhaseEntry]
    total_size: float = 0.0
    unrealized_pnl: str = "$0"
    realized_pnl: float = 0.0
    created_at: str = ""
    updated_at: str = ""
    
    # Session levels (for calculating targets)
    session_levels: Optional[List[float]] = None
    current_level_index: int = 0


class PositionManager:
    """
    Manages 3-phase scale-in positions.
    
    Phase 1 (50%): Initial entry at session level touch
    Phase 2 (30%): Add on breakout through Phase 1 target
    Phase 3 (20%): Runners with tight trailing stop
    """
    
    def __init__(self, position_file: str = "/tmp/titan_positions.json"):
        self.position_file = position_file
        self.positions: Dict[str, Position] = {}
        self.load_positions()
    
    def load_positions(self):
        """Load positions from disk."""
        if os.path.exists(self.position_file):
            try:
                with open(self.position_file, 'r') as f:
                    data = json.load(f)
                    
                # Convert dict to Position objects
                for symbol, pos_dict in data.items():
                    phases = [PhaseEntry(**p) for p in pos_dict.get("phases", [])]
                    pos_dict["phases"] = phases
                    self.positions[symbol] = Position(**pos_dict)
                    
            except Exception as e:
                print(f"⚠️  Error loading positions: {e}")
                self.positions = {}
    
    def save_positions(self):
        """Save positions to disk."""
        try:
            # Convert Position objects to dicts
            data = {}
            for symbol, pos in self.positions.items():
                pos_dict = asdict(pos)
                data[symbol] = pos_dict
            
            with open(self.position_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"❌ Error saving positions: {e}")
    
    def calculate_stop(self, entry_price: float, phase: int, direction: str) -> float:
        """
        Calculate stop loss for a phase.
        
        Phase 1: 0.5% below entry on underlying (~-50% on option)
        Phase 2: Move to broken level (locks Phase 1 profit)
        Phase 3: Tight trailing (0.3% below each new high)
        """
        if phase == Phase.PHASE_1.value:
            # 0.5% below entry
            if direction == "long":
                return entry_price * 0.995
            else:
                return entry_price * 1.005
                
        elif phase == Phase.PHASE_2.value:
            # Stop at Phase 1 target (broken level)
            # Will be set dynamically when Phase 2 triggers
            return entry_price
            
        elif phase == Phase.PHASE_3.value:
            # Tight trailing 0.3%
            if direction == "long":
                return entry_price * 0.997
            else:
                return entry_price * 1.003
        
        return entry_price
    
    def get_next_target_from_levels(self, current_price: float, 
                                    session_levels: List[float], 
                                    direction: str) -> Optional[float]:
        """Get next session level as target."""
        if not session_levels:
            return None
        
        sorted_levels = sorted(session_levels)
        
        if direction == "long":
            # Find next level above current price
            for level in sorted_levels:
                if level > current_price:
                    return level
        else:
            # Find next level below current price
            for level in reversed(sorted_levels):
                if level < current_price:
                    return level
        
        return None
    
    def create_position(self, symbol: str, direction: str, 
                       entry_price: float, session_levels: List[float]) -> Position:
        """
        Create new 3-phase position.
        
        Args:
            symbol: Underlying symbol (e.g., "QQQ")
            direction: "long" or "short"
            entry_price: Entry price on underlying
            session_levels: List of session high/low levels for targets
        """
        direction = direction.lower()
        
        # Calculate Phase 1 parameters
        phase1_stop = self.calculate_stop(entry_price, Phase.PHASE_1.value, direction)
        phase1_target = self.get_next_target_from_levels(entry_price, session_levels, direction)
        
        # Get strike for Phase 1 (OTM at next target level)
        phase1_strike = phase1_target if phase1_target else entry_price * (1.01 if direction == "long" else 0.99)
        
        # Create phases
        phase1 = PhaseEntry(
            phase=Phase.PHASE_1.value,
            entry=entry_price,
            strike=phase1_strike,
            size=0.5,  # 50% of total position
            stop=phase1_stop,
            target=phase1_target,
            status=PositionStatus.PENDING.value
        )
        
        phase2 = PhaseEntry(
            phase=Phase.PHASE_2.value,
            size=0.3,  # 30% of total position
            status=PositionStatus.PENDING.value
        )
        
        phase3 = PhaseEntry(
            phase=Phase.PHASE_3.value,
            size=0.2,  # 20% of total position
            status=PositionStatus.PENDING.value
        )
        
        # Create position
        pos = Position(
            symbol=symbol,
            direction=direction,
            phases=[phase1, phase2, phase3],
            total_size=0.0,
            session_levels=session_levels,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        self.positions[symbol] = pos
        self.save_positions()
        
        return pos
    
    def trigger_phase_1(self, symbol: str) -> Optional[str]:
        """
        Trigger Phase 1 entry.
        Returns alert message.
        """
        if symbol not in self.positions:
            return None
        
        pos = self.positions[symbol]
        phase1 = pos.phases[0]
        
        if phase1.status != PositionStatus.PENDING.value:
            return None
        
        # Mark as open
        phase1.status = PositionStatus.OPEN.value
        phase1.entry_time = datetime.now().isoformat()
        pos.total_size = phase1.size
        pos.updated_at = datetime.now().isoformat()
        
        self.save_positions()
        
        # Generate alert
        direction_emoji = "📈" if pos.direction == "long" else "📉"
        alert = (
            f"{direction_emoji} PHASE 1 ENTRY: {symbol} {pos.direction.upper()}\n"
            f"   Entry: ${phase1.entry:.2f}\n"
            f"   Strike: ${phase1.strike:.0f}{'C' if pos.direction == 'long' else 'P'}\n"
            f"   Stop: ${phase1.stop:.2f}\n"
            f"   Target: ${phase1.target:.2f}\n"
            f"   Size: {phase1.size*100:.0f}%"
        )
        
        return alert
    
    def trigger_phase_2(self, symbol: str, current_price: float) -> Optional[str]:
        """
        Trigger Phase 2 add.
        Price broke through Phase 1 target.
        """
        if symbol not in self.positions:
            return None
        
        pos = self.positions[symbol]
        phase1 = pos.phases[0]
        phase2 = pos.phases[1]
        
        if phase1.status != PositionStatus.OPEN.value:
            return None
        
        if phase2.status != PositionStatus.PENDING.value:
            return None
        
        # Calculate Phase 2 parameters
        phase2.entry = current_price
        
        # Next target (next session level beyond Phase 1 target)
        phase2.target = self.get_next_target_from_levels(
            current_price, 
            pos.session_levels, 
            pos.direction
        )
        
        # Strike at next level
        phase2.strike = phase2.target if phase2.target else current_price * (1.01 if pos.direction == "long" else 0.99)
        
        # Move stop to Phase 1 target (locks profit)
        phase2.stop = phase1.target
        phase1.stop = phase1.target  # Also move Phase 1 stop
        
        # Mark as open
        phase2.status = PositionStatus.OPEN.value
        phase2.entry_time = datetime.now().isoformat()
        pos.total_size += phase2.size
        pos.updated_at = datetime.now().isoformat()
        
        self.save_positions()
        
        # Generate alert
        alert = (
            f"🚀 PHASE 2 ADD: {symbol} broke ${phase1.target:.2f}!\n"
            f"   Adding at: ${phase2.entry:.2f}\n"
            f"   Strike: ${phase2.strike:.0f}{'C' if pos.direction == 'long' else 'P'}\n"
            f"   Stop moved to: ${phase2.stop:.2f} (locks Phase 1 profit)\n"
            f"   Target: ${phase2.target:.2f}\n"
            f"   Total size: {pos.total_size*100:.0f}%"
        )
        
        return alert
    
    def trigger_phase_3(self, symbol: str, current_price: float) -> Optional[str]:
        """
        Trigger Phase 3 runners.
        Price broke through Phase 2 target.
        """
        if symbol not in self.positions:
            return None
        
        pos = self.positions[symbol]
        phase2 = pos.phases[1]
        phase3 = pos.phases[2]
        
        if phase2.status != PositionStatus.OPEN.value:
            return None
        
        if phase3.status != PositionStatus.PENDING.value:
            return None
        
        # Calculate Phase 3 parameters
        phase3.entry = current_price
        phase3.target = None  # Let it run
        
        # Tight trailing stop (0.3%)
        phase3.stop = self.calculate_stop(current_price, Phase.PHASE_3.value, pos.direction)
        
        # Strike (can be same as Phase 2 or new)
        phase3.strike = phase2.strike
        
        # Mark as open
        phase3.status = PositionStatus.OPEN.value
        phase3.entry_time = datetime.now().isoformat()
        pos.total_size += phase3.size
        pos.updated_at = datetime.now().isoformat()
        
        self.save_positions()
        
        # Generate alert
        alert = (
            f"🎯 PHASE 3 RUNNERS: {symbol} broke ${phase2.target:.2f}!\n"
            f"   Trailing stop: ${phase3.stop:.2f}\n"
            f"   Let it run 🚀\n"
            f"   Total size: {pos.total_size*100:.0f}%"
        )
        
        return alert
    
    def update_trailing_stop(self, symbol: str, current_high: float) -> Optional[str]:
        """Update trailing stop for Phase 3."""
        if symbol not in self.positions:
            return None
        
        pos = self.positions[symbol]
        phase3 = pos.phases[2]
        
        if phase3.status != PositionStatus.OPEN.value:
            return None
        
        # Calculate new trailing stop (0.3% below new high)
        new_stop = self.calculate_stop(current_high, Phase.PHASE_3.value, pos.direction)
        
        # Only update if new stop is higher (for longs) or lower (for shorts)
        if pos.direction == "long" and new_stop > phase3.stop:
            phase3.stop = new_stop
            pos.updated_at = datetime.now().isoformat()
            self.save_positions()
            
            return f"📈 {symbol} trailing stop updated: ${new_stop:.2f}"
            
        elif pos.direction == "short" and new_stop < phase3.stop:
            phase3.stop = new_stop
            pos.updated_at = datetime.now().isoformat()
            self.save_positions()
            
            return f"📉 {symbol} trailing stop updated: ${new_stop:.2f}"
        
        return None
    
    def check_stops(self, symbol: str, current_price: float) -> Optional[str]:
        """Check if any phase hit stop loss."""
        if symbol not in self.positions:
            return None
        
        pos = self.positions[symbol]
        alerts = []
        
        for phase in pos.phases:
            if phase.status != PositionStatus.OPEN.value:
                continue
            
            # Check stop hit
            stop_hit = False
            if pos.direction == "long" and current_price <= phase.stop:
                stop_hit = True
            elif pos.direction == "short" and current_price >= phase.stop:
                stop_hit = True
            
            if stop_hit:
                phase.status = PositionStatus.STOPPED.value
                phase.exit_time = datetime.now().isoformat()
                phase.exit_price = current_price
                
                # Calculate P/L
                if phase.entry:
                    phase.pnl = ((current_price - phase.entry) / phase.entry) * 100
                    if pos.direction == "short":
                        phase.pnl *= -1
                
                pos.total_size -= phase.size
                pos.updated_at = datetime.now().isoformat()
                
                alerts.append(
                    f"🛑 STOPPED: {symbol} Phase {phase.phase}\n"
                    f"   Stop: ${phase.stop:.2f}\n"
                    f"   P/L: {phase.pnl:+.1f}%"
                )
        
        if alerts:
            self.save_positions()
            return "\n\n".join(alerts)
        
        return None
    
    def check_targets(self, symbol: str, current_price: float) -> Optional[str]:
        """Check if any phase hit target."""
        if symbol not in self.positions:
            return None
        
        pos = self.positions[symbol]
        alerts = []
        
        # Check Phase 1 → Phase 2 trigger
        phase1 = pos.phases[0]
        if (phase1.status == PositionStatus.OPEN.value and 
            phase1.target and
            ((pos.direction == "long" and current_price >= phase1.target) or
             (pos.direction == "short" and current_price <= phase1.target))):
            
            alert = self.trigger_phase_2(symbol, current_price)
            if alert:
                alerts.append(alert)
        
        # Check Phase 2 → Phase 3 trigger
        phase2 = pos.phases[1]
        if (phase2.status == PositionStatus.OPEN.value and 
            phase2.target and
            ((pos.direction == "long" and current_price >= phase2.target) or
             (pos.direction == "short" and current_price <= phase2.target))):
            
            alert = self.trigger_phase_3(symbol, current_price)
            if alert:
                alerts.append(alert)
        
        if alerts:
            return "\n\n".join(alerts)
        
        return None
    
    def update_position(self, symbol: str, current_price: float) -> List[str]:
        """
        Update position with current price.
        Returns list of alerts.
        """
        alerts = []
        
        # Check stops first
        stop_alert = self.check_stops(symbol, current_price)
        if stop_alert:
            alerts.append(stop_alert)
        
        # Check targets
        target_alert = self.check_targets(symbol, current_price)
        if target_alert:
            alerts.append(target_alert)
        
        # Update trailing stop for Phase 3
        if symbol in self.positions:
            pos = self.positions[symbol]
            phase3 = pos.phases[2]
            
            if phase3.status == PositionStatus.OPEN.value:
                trail_alert = self.update_trailing_stop(symbol, current_price)
                if trail_alert:
                    alerts.append(trail_alert)
        
        return alerts
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for symbol."""
        return self.positions.get(symbol)
    
    def get_all_positions(self) -> Dict[str, Position]:
        """Get all positions."""
        return self.positions
    
    def close_position(self, symbol: str, reason: str = "manual") -> Optional[str]:
        """Close position completely."""
        if symbol not in self.positions:
            return None
        
        pos = self.positions[symbol]
        
        # Close all open phases
        for phase in pos.phases:
            if phase.status == PositionStatus.OPEN.value:
                phase.status = PositionStatus.CLOSED.value
                phase.exit_time = datetime.now().isoformat()
        
        pos.total_size = 0.0
        pos.updated_at = datetime.now().isoformat()
        
        self.save_positions()
        
        return f"🔒 {symbol} position closed ({reason})"


# Example usage
if __name__ == "__main__":
    # Test the manager
    manager = PositionManager()
    
    # Create a position
    session_levels = [597.50, 602.28, 605.00, 608.50]
    pos = manager.create_position("QQQ", "long", 597.50, session_levels)
    
    print("📊 Created position:")
    print(json.dumps(asdict(pos), indent=2, default=str))
    
    # Trigger Phase 1
    alert = manager.trigger_phase_1("QQQ")
    if alert:
        print(f"\n{alert}")
    
    # Simulate price hitting Phase 1 target
    print("\n--- Price moves to $602.50 ---")
    alerts = manager.update_position("QQQ", 602.50)
    for alert in alerts:
        print(f"\n{alert}")
    
    # Simulate price hitting Phase 2 target
    print("\n--- Price moves to $605.50 ---")
    alerts = manager.update_position("QQQ", 605.50)
    for alert in alerts:
        print(f"\n{alert}")
    
    # Show final position
    print("\n📊 Final position:")
    pos = manager.get_position("QQQ")
    if pos:
        print(json.dumps(asdict(pos), indent=2, default=str))
