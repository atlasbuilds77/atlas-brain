# ✅ TITAN Scale-In Position Manager - COMPLETE

## What Was Built

### 1. **position_manager.py** - Core Position Management
- ✅ 3-phase position structure (50% → 30% → 20%)
- ✅ Automatic stop management (0.5% → breakeven → 0.3% trailing)
- ✅ Target calculation based on session levels
- ✅ Position tracking in `/tmp/titan_positions.json`
- ✅ Alert generation for all phase triggers
- ✅ Modular design - can be imported anywhere

### 2. **session_scanner.py** - Level Detection & Integration
- ✅ Pre-market high/low detection (4am-9:30am)
- ✅ Prior day high/low detection
- ✅ Opening range high/low (15-min)
- ✅ Level touch detection (triggers Phase 1)
- ✅ Level break detection (triggers Phase 2/3)
- ✅ Automatic position manager integration
- ✅ Status reporting

### 3. **POSITION_MANAGER.md** - Complete Documentation
- ✅ Full logic explanation
- ✅ Usage examples
- ✅ Integration guide
- ✅ Risk management rules

### 4. **example_integration.py** - Integration Example
- ✅ Shows how to combine with existing TITAN scanner
- ✅ Ready to run example

## Files Created

```
/Users/atlasbuilds/clawd/titan-trader/
├── position_manager.py         (18KB - core logic)
├── session_scanner.py          (15KB - level detection)
├── POSITION_MANAGER.md         (6KB - documentation)
├── SCALE_IN_SUMMARY.md         (this file)
└── example_integration.py      (2KB - integration example)

/tmp/
└── titan_positions.json        (position state - persisted)
```

## How It Works

### Phase 1 - Entry (50%)
```
Price touches session level
    ↓
Create position with 3 phases
    ↓
Enter Phase 1: 50% size
    ↓
OTM option at next level strike
    ↓
Stop: 0.5% below entry (~-50% on option)
    ↓
Alert: "PHASE 1 ENTRY: QQQ Long at $597.50..."
```

### Phase 2 - Add (30%)
```
Price breaks Phase 1 target
    ↓
Trigger Phase 2 add
    ↓
New strike at NEXT level
    ↓
Move stop to broken level (LOCKS PHASE 1 PROFIT)
    ↓
Alert: "PHASE 2 ADD: QQQ broke $602! Adding at $604C..."
```

### Phase 3 - Runners (20%)
```
Price breaks Phase 2 target
    ↓
Trigger Phase 3 runners
    ↓
Tight trailing stop (0.3%)
    ↓
Let it run - no fixed target
    ↓
Alert: "PHASE 3 RUNNERS: Trailing stop at $604.50"
```

## Quick Start

### Test Position Manager Standalone
```bash
cd /Users/atlasbuilds/clawd/titan-trader
python3 position_manager.py
```

### Run Session Scanner
```bash
python3 session_scanner.py
```

### Use in Your Code
```python
from position_manager import PositionManager

pm = PositionManager()

# Create position
levels = [597.50, 602.28, 605.00, 608.50]
pos = pm.create_position("QQQ", "long", 597.50, levels)

# Trigger Phase 1
alert = pm.trigger_phase_1("QQQ")
print(alert)

# Update with current price (auto-triggers Phase 2/3)
alerts = pm.update_position("QQQ", 602.50)
```

### Use Session Scanner
```python
from session_scanner import SessionScanner

scanner = SessionScanner()

# Single ticker
alerts = scanner.scan_and_trigger("QQQ")

# All tickers
alerts = scanner.scan_all(["SPY", "QQQ", "IWM"])

# Status report
print(scanner.get_status_report())
```

## Integration Options

### Option A: Add to Existing main.py
```python
from session_scanner import SessionScanner

# In run_scan_cycle():
session_scanner = SessionScanner()
session_alerts = session_scanner.scan_all(TICKERS)

for alert in session_alerts:
    send_telegram(alert)
```

### Option B: Run Standalone Scanner
```bash
# Via PM2
pm2 start session_scanner.py --name titan-session --interpreter python3

# Or direct
python3 session_scanner.py
```

### Option C: Combined Approach
Use `example_integration.py` which combines:
1. Session level monitoring (fast, every 30s)
2. Order block scanning (slower, every 5 min)
3. Automatic position management

## Alert Examples

### Level Touch (Phase 1 Trigger)
```
🎯 Level Touch!
📈 PHASE 1 ENTRY: QQQ LONG
   Entry: $597.50
   Strike: $600C
   Stop: $594.50
   Target: $602.28
   Size: 50%
```

### Target Hit (Phase 2 Trigger)
```
🚀 PHASE 2 ADD: QQQ broke $602.28!
   Adding at: $602.50
   Strike: $604C
   Stop moved to: $602.28 (locks Phase 1 profit)
   Target: $605.00
   Total size: 80%
```

### Runners (Phase 3 Trigger)
```
🎯 PHASE 3 RUNNERS: QQQ broke $605.00!
   Trailing stop: $603.68
   Let it run 🚀
   Total size: 100%
```

### Level Break
```
⚡ QQQ broke prior_high at $605.00
```

### Stop Out
```
🛑 STOPPED: QQQ Phase 1
   Stop: $594.50
   P/L: -0.5%
```

## Position Tracking

All positions saved to `/tmp/titan_positions.json`:

```json
{
  "QQQ": {
    "symbol": "QQQ",
    "direction": "long",
    "phases": [
      {"phase": 1, "entry": 597.50, "strike": 600, "size": 0.5, "status": "open"},
      {"phase": 2, "entry": 602.50, "strike": 604, "size": 0.3, "status": "pending"},
      {"phase": 3, "size": 0.2, "status": "pending"}
    ],
    "total_size": 0.5,
    "session_levels": [597.50, 602.28, 605.00, 608.50]
  }
}
```

## Key Features

### ✅ Risk Management
- **Defined stops**: Every phase has a stop loss
- **Progressive tightening**: 0.5% → breakeven → 0.3% trailing
- **Risk-free after Phase 1**: Stop moves to entry after first target
- **Position sizing**: Start small (50%), add on confirmation

### ✅ Automation
- **Auto-trigger**: Phase 2/3 trigger automatically when targets hit
- **Auto-stop**: Positions close automatically on stop hit
- **Auto-trail**: Phase 3 trailing stop updates automatically
- **Persistence**: Positions saved to disk, survive restarts

### ✅ Modularity
- **Import anywhere**: `from position_manager import PositionManager`
- **Standalone**: Can run session_scanner.py independently
- **Integrate easily**: Add to existing TITAN with 3 lines of code

### ✅ Monitoring
- **Real-time alerts**: Every action generates an alert
- **Status reports**: See all positions and levels at a glance
- **Position history**: Track all phase entries/exits with timestamps

## Testing Results

Ran test simulation:
```
✅ Created position (QQQ long at $597.50)
✅ Triggered Phase 1 (50% entry)
✅ Price hit $602.50 → Phase 2 triggered (30% add)
✅ Stop moved to breakeven ($602.28)
✅ Price hit $605.50 → Phase 3 triggered (20% runners)
✅ Trailing stop calculated ($603.68)
✅ All data saved to /tmp/titan_positions.json
```

## Next Steps

### Immediate
1. ✅ **Position manager built** - Complete
2. ✅ **Session scanner built** - Complete
3. ✅ **Documentation written** - Complete

### Integration (Choose One)
4. ⏳ **Add to main.py** - Integrate with existing TITAN
5. ⏳ **Run standalone** - Use session_scanner.py independently
6. ⏳ **Use example** - Run example_integration.py

### Enhancements (Optional)
7. ⏳ **Telegram alerts** - Hook up to your Telegram bot
8. ⏳ **Real option pricing** - Get actual option quotes (vs. estimates)
9. ⏳ **Backtesting** - Test on historical data
10. ⏳ **GEX integration** - Combine with gamma exposure levels

## Questions?

The code is fully documented and modular. You can:
- Import `PositionManager` in any Python script
- Run `session_scanner.py` standalone
- Integrate with existing TITAN scanner
- Modify phase sizes/stops/logic as needed

All logic is in `position_manager.py` (core) and `session_scanner.py` (integration).

---

**Status**: ✅ COMPLETE - Ready to use!
