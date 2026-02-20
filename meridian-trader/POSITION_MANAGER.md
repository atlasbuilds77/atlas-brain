# TITAN Position Manager - 3-Phase Scale-In System

## Overview

The Position Manager implements a systematic 3-phase scale-in strategy that builds positions as price confirms direction through session levels.

## Components

### 1. `position_manager.py` - Core Position Logic
Handles all position lifecycle:
- Creates 3-phase positions
- Tracks entries, stops, targets
- Manages position sizing (50% → 30% → 20%)
- Updates trailing stops
- Saves positions to `/tmp/titan_positions.json`

### 2. `session_scanner.py` - Level Detection & Triggering
Monitors session levels and triggers position manager:
- Pre-market high/low
- Prior day high/low
- Opening range high/low
- Detects level touches → Phase 1
- Detects level breaks → Phase 2/3

## Scale-In Logic

### PHASE 1 - ENTRY (50% size)
**Trigger**: Price touches session level (pre-high/low, prior high/low)

**Action**:
- Enter OTM option at next target level strike
- Stop: 0.5% below entry on underlying (~-50% on option)
- Target: Next session level

**Example**:
```
QQQ touches prior low at $597.50
→ Enter $600C (next level at $602)
→ Stop: $594.50
→ Target: $602.28
```

### PHASE 2 - ADD (30% size)
**Trigger**: Price breaks through Phase 1 target

**Action**:
- Add position, new strike at NEXT level
- Move stop to broken level (locks Phase 1 profit)
- Target: Next level beyond

**Example**:
```
QQQ breaks $602.28
→ Add $604C or $605C
→ Stop moved to $602.28 (Phase 1 now risk-free)
→ Target: $605.00
```

### PHASE 3 - RUNNERS (20% size)
**Trigger**: Price breaks through Phase 2 target

**Action**:
- Final add OR just trail existing
- Tight trailing stop (0.3% below each new high)
- Let it run

**Example**:
```
QQQ breaks $605.00
→ Trail stop at 0.3% below each new high
→ No fixed target - ride the trend
```

## Position Tracking

Positions saved to `/tmp/titan_positions.json`:

```json
{
  "QQQ": {
    "symbol": "QQQ",
    "direction": "long",
    "phases": [
      {
        "phase": 1,
        "entry": 597.50,
        "strike": 600,
        "size": 0.5,
        "stop": 594.50,
        "target": 602.28,
        "status": "open"
      },
      {
        "phase": 2,
        "entry": 602.50,
        "strike": 604,
        "size": 0.3,
        "stop": 601.00,
        "target": 605.00,
        "status": "open"
      },
      {
        "phase": 3,
        "entry": 605.50,
        "strike": 604,
        "size": 0.2,
        "stop": 603.68,
        "target": null,
        "status": "open"
      }
    ],
    "total_size": 1.0,
    "session_levels": [597.50, 602.28, 605.00, 608.50]
  }
}
```

## Alert Examples

### Phase 1 Entry
```
📈 PHASE 1 ENTRY: QQQ LONG
   Entry: $597.50
   Strike: $600C
   Stop: $594.50
   Target: $602.28
   Size: 50%
```

### Phase 2 Add
```
🚀 PHASE 2 ADD: QQQ broke $602.28!
   Adding at: $602.50
   Strike: $604C
   Stop moved to: $602.28 (locks Phase 1 profit)
   Target: $605.00
   Total size: 80%
```

### Phase 3 Runners
```
🎯 PHASE 3 RUNNERS: QQQ broke $605.00!
   Trailing stop: $603.68
   Let it run 🚀
   Total size: 100%
```

### Stop Out
```
🛑 STOPPED: QQQ Phase 1
   Stop: $594.50
   P/L: -50.2%
```

## Usage

### Standalone Position Manager

```python
from position_manager import PositionManager

# Create manager
pm = PositionManager()

# Create position with session levels
session_levels = [597.50, 602.28, 605.00, 608.50]
pos = pm.create_position("QQQ", "long", 597.50, session_levels)

# Trigger Phase 1
alert = pm.trigger_phase_1("QQQ")
print(alert)

# Update with current price
alerts = pm.update_position("QQQ", 602.50)  # Triggers Phase 2 if target hit
for alert in alerts:
    print(alert)
```

### Integrated Session Scanner

```python
from session_scanner import SessionScanner

# Create scanner (includes position manager)
scanner = SessionScanner()

# Scan for level touches and breaks
alerts = scanner.scan_and_trigger("QQQ")
for alert in alerts:
    print(alert)

# Or scan all tickers
all_alerts = scanner.scan_all(["SPY", "QQQ", "IWM"])

# Get status report
print(scanner.get_status_report())
```

### Run Continuous Scanner

```bash
# Run session scanner in continuous mode
python3 session_scanner.py

# Or via PM2
pm2 start session_scanner.py --name titan-session --interpreter python3
```

## Integration with Existing TITAN

Add to `main.py` scan cycle:

```python
from session_scanner import SessionScanner

# In run_scan_cycle():
scanner = SessionScanner()

# After finding setups, check session levels
session_alerts = scanner.scan_all(TICKERS)
for alert in session_alerts:
    print(alert)
    send_telegram(alert)
```

## Stop Loss Strategy

### Phase 1
- **Initial Stop**: 0.5% below entry on underlying
- **Rationale**: Options amplify moves (~2-3x), so 0.5% spot = ~50% option loss
- **Example**: Entry $597.50 → Stop $594.50 (0.5% = $3)

### Phase 2
- **Break-Even Stop**: Move to Phase 1 target (broken level)
- **Rationale**: Once level breaks, previous resistance becomes support
- **Example**: Phase 1 target $602.28 → new stop $602.28 (locks profit)

### Phase 3
- **Trailing Stop**: 0.3% below each new high
- **Rationale**: Tighter stop for runners, let winners run but protect profits
- **Example**: High $605.50 → Stop $603.68 (0.3% = $1.82)

## Position Sizing

- **Total capital**: 100%
- **Phase 1**: 50% (initial conviction)
- **Phase 2**: 30% (confirmation)
- **Phase 3**: 20% (fully confirmed trend)

**Advantages**:
1. Start small (reduce risk)
2. Add on confirmation (increase conviction)
3. Let winners run (maximize profit)
4. Risk-free after Phase 1 target (stop at breakeven)

## Risk Management

### Max Loss Per Trade
- **Phase 1 only**: -25% of capital (50% size × -50% option loss)
- **Phase 1 + 2**: Risk-free (stop at Phase 1 entry)
- **Phase 1 + 2 + 3**: Protected profit (trailing stop)

### Position Limits
- **Max concurrent positions**: 3
- **Max size per symbol**: 100% (all 3 phases)
- **Avoid pyramiding**: Only one position per symbol

## Testing

```bash
# Test position manager
python3 position_manager.py

# Test session scanner (will scan live)
python3 session_scanner.py
```

## Files

- `position_manager.py` - Core position logic
- `session_scanner.py` - Level detection & integration
- `/tmp/titan_positions.json` - Position state (persisted)
- `POSITION_MANAGER.md` - This documentation

## Next Steps

1. ✅ Position manager created
2. ✅ Session scanner created
3. ⏳ Integrate with main.py
4. ⏳ Add Telegram alerts
5. ⏳ Add option pricing (real quotes vs. estimates)
6. ⏳ Backtest on historical data
