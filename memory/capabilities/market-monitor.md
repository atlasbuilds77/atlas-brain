# Market Monitor Capability

**Status**: ✅ Built and Ready for Configuration  
**Location**: `/Users/atlasbuilds/clawd/atlas-monitor/`  
**Created**: 2026-01-30

## Overview

The Atlas Market Monitor is a production-ready autonomous system that watches Discord for trading signals, tracks positions, and sends real-time alerts via iMessage.

## Components

### 1. Discord Signal Monitor (`discord-monitor.js`)
- Connects to Discord using bot token
- Monitors #helios channel for trading signals
- Real-time message processing
- Graceful reconnection handling

### 2. Signal Parser (`signal-parser.js`)
- Intelligent pattern matching for trading signals
- Recognizes multiple formats:
  - Entry: `Long $BTC at $45000, SL: $44000, Target: $47000`
  - Exit: `Exit $ETH at $3000`
  - Alerts: Messages with keywords or emojis (🚨, ⚠️, 🔥)
- Extracts: symbol, price, stop loss, targets
- Stores structured signal data

### 3. Position Tracker (`position-tracker.js`)
- Automatically opens positions from ENTRY signals
- Monitors price movements (configurable interval)
- Detects stop loss hits
- Detects target hits
- Calculates real-time P/L
- Archives closed positions

### 4. Alert Dispatcher (`alert-dispatcher.js`)
- Sends iMessage alerts via Clawdbot
- Rate limiting (2 seconds between alerts)
- Alert types:
  - 🎯 Entry signals
  - 🚪 Exit signals
  - ⚠️ Market alerts
  - 🛑 Stop loss hits
  - 🎯 Target hits
  - ✅/❌ Position closed (with P/L)
  - 🤖 System events

### 5. Signal Storage (`signal-store.js`)
- Persists all signals to JSON files
- Location: `/Users/atlasbuilds/clawd/memory/trading/signals/`
- Archive closed positions
- Query by symbol, type, date
- Load recent signals

### 6. Logging System (`logger.js`)
- Structured JSON logging
- Daily log files: `logs/monitor-YYYY-MM-DD.log`
- Log levels: info, warn, error, debug, signal, alert
- Console + file output

## Installation

```bash
cd /Users/atlasbuilds/clawd/atlas-monitor
chmod +x install.sh
./install.sh
```

## Configuration

Edit `.env`:

```bash
# Required
DISCORD_BOT_TOKEN=your_bot_token_here
DISCORD_GUILD_ID=your_guild_id
HELIOS_CHANNEL_ID=your_channel_id

# Optional
ALERT_PHONE=+14245157194
CHECK_INTERVAL_MS=5000
POSITION_CHECK_INTERVAL_MS=30000
DEV_MODE=false
```

### Getting Discord Credentials

1. Create bot: https://discord.com/developers/applications
2. Enable intents: Guilds, Guild Messages, Message Content
3. Copy bot token → `DISCORD_BOT_TOKEN`
4. Invite bot to server
5. Get Guild ID: Right-click server → Copy ID
6. Get Channel ID: Right-click #helios → Copy ID

## Usage

```bash
# Start
./scripts/start.sh

# Stop
./scripts/stop.sh

# Status
./scripts/status.sh

# Restart
./scripts/restart.sh

# Test
npm test

# Dev mode (no actual alerts sent)
npm run dev
```

## Architecture

```
Discord (#helios) 
    ↓
Discord Monitor → Signal Parser
    ↓                    ↓
Signal Store    Position Tracker
    ↓                    ↓
Alert Dispatcher ← [Triggers]
    ↓
iMessage (via Clawdbot)
```

## Data Flow

1. **Signal Detection**:
   - Discord message received
   - Signal parser extracts structured data
   - Signal saved to `/memory/trading/signals/`
   - Alert sent via iMessage

2. **Position Management**:
   - ENTRY signal → Open position
   - Position tracked continuously
   - Price updates → P/L calculation
   - Stop loss/target detection
   - EXIT signal → Close position
   - Archived with final P/L

3. **Alert Flow**:
   - Alert formatted with relevant data
   - Rate limited (2s between alerts)
   - Sent via: `clawdbot message send --channel imessage --to +14245157194 --message "..."`
   - Logged to file

## Testing

The system includes comprehensive tests:

```bash
npm test
```

Tests cover:
- ✅ Signal parsing (entry/exit/alerts)
- ✅ Signal storage (save/load/query)
- ✅ Alert formatting
- ✅ Position tracking (open/close/P/L)
- ✅ Integration flow

All tests pass without requiring Discord connection.

## Background Daemon

Runs autonomously with:
- **Graceful shutdown** (SIGINT, SIGTERM)
- **Error handling** (uncaught exceptions)
- **Process management** (PID file)
- **Auto-restart** capability
- **Status monitoring** (every 5 minutes)

## Production Deployment

### Option 1: Manual Start
```bash
./scripts/start.sh
```

### Option 2: System Service (macOS launchd)

See README.md for launchd plist configuration to:
- Auto-start on boot
- Auto-restart on crash
- Run in background

### Option 3: Cron Monitor
```bash
*/5 * * * * /Users/atlasbuilds/clawd/atlas-monitor/scripts/status.sh
```

## Logs

- **Application logs**: `logs/monitor-YYYY-MM-DD.log`
- **Stdout**: `logs/stdout.log` (if using launchd)
- **Stderr**: `logs/stderr.log` (if using launchd)

Each log entry includes:
```json
{
  "timestamp": "2026-01-30T12:00:00.000Z",
  "level": "info",
  "message": "Signal detected",
  "data": { "type": "ENTRY", "symbol": "BTC" }
}
```

## Signal Storage

Signals stored at: `/Users/atlasbuilds/clawd/memory/trading/signals/`

Structure:
```
signals/
├── sig_1738254000000_abc123.json  # Active signals
├── sig_1738254001000_def456.json
├── _positions.json                 # Current positions
└── archive/                        # Closed positions
    └── pos_BTC_1738254002000.json
```

## Integration Points

### Clawdbot Message Tool
```bash
clawdbot message send \
  --channel imessage \
  --to +14245157194 \
  --message "🎯 ENTRY SIGNAL\nSymbol: $BTC\nPrice: $45000"
```

### Signal Files
Other systems can read signals:
```bash
ls /Users/atlasbuilds/clawd/memory/trading/signals/*.json
```

### Position Data
```bash
cat /Users/atlasbuilds/clawd/memory/trading/signals/_positions.json
```

## Capabilities

✅ **Real-time signal detection** - Monitors Discord 24/7  
✅ **Intelligent parsing** - Recognizes multiple signal formats  
✅ **Automatic position tracking** - Opens/closes based on signals  
✅ **Stop loss detection** - Alerts when SL hit  
✅ **Target detection** - Alerts when targets reached  
✅ **P/L calculation** - Real-time profit/loss tracking  
✅ **iMessage alerts** - Instant notifications  
✅ **Signal archival** - Complete trade history  
✅ **Graceful shutdown** - Safe stop/restart  
✅ **Error recovery** - Handles disconnections  
✅ **Production ready** - Logging, monitoring, tests  

## Next Steps

1. **Configure Discord Bot**:
   - Create bot at Discord Developer Portal
   - Add to server
   - Copy credentials to `.env`

2. **Install Dependencies**:
   ```bash
   cd /Users/atlasbuilds/clawd/atlas-monitor
   ./install.sh
   ```

3. **Test**:
   ```bash
   npm test
   ```

4. **Start**:
   ```bash
   ./scripts/start.sh
   ```

5. **Verify**:
   - Check logs: `tail -f logs/monitor.log`
   - Check status: `./scripts/status.sh`
   - Send test message in #helios
   - Verify iMessage received

## Troubleshooting

**Discord not connecting?**
- Verify `DISCORD_BOT_TOKEN` in `.env`
- Check bot has Message Content intent enabled
- Ensure bot is in the server

**No alerts received?**
- Test Clawdbot: `clawdbot message send --channel imessage --to +14245157194 --message "test"`
- Check `DEV_MODE=false` in `.env`
- Review logs for errors

**Signals not detected?**
- Verify `HELIOS_CHANNEL_ID` is correct
- Check bot has permission to read channel
- Review logs for parsing attempts
- Run tests: `npm test`

## Maintenance

**View logs**:
```bash
tail -f /Users/atlasbuilds/clawd/atlas-monitor/logs/monitor-$(date +%Y-%m-%d).log
```

**Check disk usage**:
```bash
du -sh /Users/atlasbuilds/clawd/memory/trading/signals/
```

**Archive old signals** (manual):
```bash
find /Users/atlasbuilds/clawd/memory/trading/signals/ -name "*.json" -mtime +30 -exec mv {} /Users/atlasbuilds/clawd/memory/trading/signals/archive/ \;
```

## Resources

- **Project**: `/Users/atlasbuilds/clawd/atlas-monitor/`
- **README**: `atlas-monitor/README.md`
- **Tests**: `npm test`
- **Logs**: `atlas-monitor/logs/`
- **Signals**: `/Users/atlasbuilds/clawd/memory/trading/signals/`

---

**Built**: 2026-01-30  
**Status**: Production Ready  
**Dependencies**: Node.js, discord.js, Clawdbot  
**Maintenance**: Autonomous, minimal maintenance required
