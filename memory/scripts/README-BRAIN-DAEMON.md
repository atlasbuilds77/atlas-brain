# Brain Daemon - Persistent Memory Monitor

## Overview

The brain daemon is a lightweight Node.js service that continuously monitors the `memory/` directory and generates a searchable index for instant file recall. It runs persistently in the background, ensuring Atlas always has up-to-date knowledge of available memory files.

## Architecture

### Components

1. **brain-daemon.js** - The main daemon script
   - Scans memory/ directory every 1 second (configurable)
   - Generates categorized index at `/tmp/atlas-memory-index.json`
   - Auto-restarts on errors (up to 10 consecutive errors)
   - Logs all activity to `/tmp/brain-daemon.log`
   - Creates PID file at `/tmp/brain-daemon.pid`

2. **brain-daemon-control.sh** - Control script for managing the daemon
   - Start/stop/restart/status commands
   - Graceful shutdown with fallback force-kill
   - Status display with index stats

3. **HEARTBEAT.md** - Updated with daemon startup in session initialization

## Usage

### Starting the Daemon

```bash
bash memory/scripts/brain-daemon-control.sh start
```

The daemon will:
- Start in background (detached from terminal)
- Perform initial scan
- Continue scanning every 1 second
- Log activity to `/tmp/brain-daemon.log`

### Checking Status

```bash
bash memory/scripts/brain-daemon-control.sh status
```

Shows:
- Running status and PID
- Index statistics (total files, categories)
- Recent log entries

### Stopping the Daemon

```bash
bash memory/scripts/brain-daemon-control.sh stop
```

Graceful shutdown with SIGTERM, force-kill after 5 seconds if needed.

### Restarting the Daemon

```bash
bash memory/scripts/brain-daemon-control.sh restart
```

## Index Format

The generated `/tmp/atlas-memory-index.json` contains:

```json
{
  "generated": "2024-01-15T10:30:45.123Z",
  "scanCount": 42,
  "totalFiles": 156,
  "categories": {
    "protocols": [...],
    "trading": [...],
    "projects": [...],
    "people": [...],
    "tools": [...],
    "other": [...]
  },
  "allFiles": [...],
  "stats": {
    "protocols": 25,
    "trading": 48,
    "projects": 15,
    "people": 12,
    "tools": 8,
    "other": 48
  }
}
```

Each file entry includes:
- `path` - Relative path from memory/
- `fullPath` - Absolute path
- `name` - Filename
- `size` - File size in bytes
- `modified` - ISO timestamp of last modification
- `preview` - First 200 characters of content
- `extension` - File extension

## Configuration

Environment variables (set before starting daemon):

- `SCAN_INTERVAL` - Scan interval in milliseconds (default: 1000)

Example:
```bash
SCAN_INTERVAL=500 bash memory/scripts/brain-daemon-control.sh start
```

## Integration

### Session Startup (HEARTBEAT.md)

The daemon is automatically started during session initialization:

1. Check model fallback
2. Read CURRENT_STATE.md
3. **Start brain daemon** (if not running)
4. Read protocols
5. Continue normal boot sequence

### Using the Index

Instead of scanning memory/ manually, read the index:

```javascript
const fs = require('fs');
const index = JSON.parse(fs.readFileSync('/tmp/atlas-memory-index.json', 'utf8'));

// Find all trading files
const tradingFiles = index.categories.trading;

// Search for specific file
const target = index.allFiles.find(f => f.name === 'active-positions.md');

// Get stats
console.log(`Total files: ${index.totalFiles}`);
console.log(`Protocols: ${index.stats.protocols}`);
```

## Features

### Resilience

- **Auto-restart on crash** - Exits with code 1 after 10 consecutive errors, allowing external process manager to restart
- **Graceful shutdown** - Handles SIGTERM/SIGINT cleanly
- **Error recovery** - Continues operation after individual scan failures
- **Log rotation** - Rotates log file at 10MB

### Performance

- **Async scanning** - Non-blocking directory traversal
- **Efficient writes** - Atomic index updates (write to .tmp, rename)
- **Smart filtering** - Skips hidden files, node_modules, scripts directory
- **Size limits** - Only indexes files < 1MB (prevents memory issues)

### Observability

- **Structured logging** - JSON-formatted logs with timestamps
- **Scan metrics** - Tracks scan count, error count, duration
- **Status command** - Quick overview of daemon health
- **Real-time updates** - Index reflects file changes within 1 second

## Troubleshooting

### Daemon won't start

1. Check if already running: `bash memory/scripts/brain-daemon-control.sh status`
2. Check logs: `tail -50 /tmp/brain-daemon.log`
3. Verify Node.js is installed: `node --version`
4. Check file permissions: `ls -la memory/scripts/brain-daemon.js`

### High error count

Check log file for specific errors:
```bash
grep ERROR /tmp/brain-daemon.log | tail -20
```

Common issues:
- Permission errors (can't read memory/ directory)
- Disk space issues (can't write index)
- Corrupted files in memory/

### Stale PID file

If status shows "not running" but PID file exists:
```bash
rm /tmp/brain-daemon.pid
bash memory/scripts/brain-daemon-control.sh start
```

## Future Enhancements

Potential improvements:
- [ ] File change events (inotify/fswatch) instead of polling
- [ ] Full-text search index (using simple keyword extraction)
- [ ] HTTP API endpoint for remote queries
- [ ] Multiple memory directory support
- [ ] Index compression for large memory sets
- [ ] Delta updates (only scan changed files)

## Design Principles

1. **Always running** - Start with session, run until shutdown
2. **Lightweight** - Minimal CPU/memory overhead
3. **Fast** - Sub-second response to file changes
4. **Reliable** - Graceful error handling and recovery
5. **Observable** - Clear logging and status reporting
6. **Simple** - Easy to understand, modify, and debug

---

**Status:** ✅ Production ready
**Maintained by:** Atlas cognitive architecture
**Last updated:** 2024-01-15
