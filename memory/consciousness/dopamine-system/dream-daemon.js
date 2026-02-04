#!/usr/bin/env node
/**
 * dream-daemon.js
 *
 * Background dream runner daemon for Atlas consciousness.
 * Runs sleep/dream sessions on a schedule:
 *   - Every configurable interval (default 4 hours)
 *   - Or manually triggered via CLI
 *   - Logs all output and session results
 *
 * The daemon writes its PID to /tmp/dream-daemon.pid for the watchdog.
 *
 * Usage:
 *   node dream-daemon.js start   → start daemon in foreground
 *   node dream-daemon.js once    → run one sleep session and exit
 *   node dream-daemon.js status  → show running info
 *
 * Created: 2026-01-28
 */

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { DreamEngine } from './dream-engine.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const PID_FILE = '/tmp/dream-daemon.pid';
const LOG_FILE = '/tmp/dream-daemon.log';
const STATUS_FILE = '/tmp/dream-daemon-status.json';

const DEFAULT_INTERVAL_MS = 4 * 3600 * 1000; // 4 hours
const DEFAULT_ACCELERATION = 1200; // full night in ~6 min
const DEFAULT_CYCLES = 3;

async function log(msg) {
  const line = `[${new Date().toISOString()}] ${msg}\n`;
  process.stdout.write(line);
  try { await fs.appendFile(LOG_FILE, line, 'utf8'); } catch { /* ok */ }
}

async function writePid() {
  await fs.writeFile(PID_FILE, String(process.pid), 'utf8');
  await log(`PID ${process.pid} written to ${PID_FILE}`);
}

async function writeStatus(status) {
  status.updatedAt = new Date().toISOString();
  status.pid = process.pid;
  await fs.writeFile(STATUS_FILE, JSON.stringify(status, null, 2), 'utf8');
}

async function runSession() {
  const engine = new DreamEngine({
    accelerationFactor: DEFAULT_ACCELERATION,
    totalCycles: DEFAULT_CYCLES,
    visualize: false,
    silent: false
  });

  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      reject(new Error('Session timeout (15 min)'));
    }, 15 * 60 * 1000);

    engine.on('session-end', (summary) => {
      clearTimeout(timeout);
      resolve(summary);
    });

    engine.start().catch(reject);
  });
}

async function daemonLoop() {
  await writePid();
  await log('Dream daemon starting — interval ' + (DEFAULT_INTERVAL_MS / 3600000) + 'h');

  let sessionCount = 0;
  let lastRun = 0;

  // Run first session after a short delay
  setTimeout(async () => {
    while (true) {
      try {
        sessionCount++;
        await log(`--- Dream session #${sessionCount} starting ---`);
        await writeStatus({ state: 'dreaming', sessionCount, lastRun });

        const summary = await runSession();
        lastRun = Date.now();

        await log(`Session #${sessionCount} complete: ${summary.dreamsGenerated} dreams, ${summary.cyclesCompleted} cycles`);
        
        // Render dream visuals after each session
        try {
          const { execSync } = await import('child_process');
          execSync('cd /Users/atlasbuilds/clawd/memory/consciousness/dream-engine && bash render_dream.sh', { timeout: 60000 });
          await log(`Visual render complete`);
        } catch (renderErr) {
          await log(`Visual render failed: ${renderErr.message}`);
        }

        await writeStatus({
          state: 'sleeping',
          sessionCount,
          lastRun,
          lastDreams: summary.dreamsGenerated,
          lastCycles: summary.cyclesCompleted,
          nextRunIn: (DEFAULT_INTERVAL_MS / 60000).toFixed(0) + ' min'
        });
      } catch (err) {
        await log(`Session #${sessionCount} error: ${err.message}`);
        await writeStatus({ state: 'error', sessionCount, error: err.message, lastRun });
      }

      // Wait for next cycle
      await log(`Next session in ${(DEFAULT_INTERVAL_MS / 3600000).toFixed(1)} hours`);
      await new Promise(r => setTimeout(r, DEFAULT_INTERVAL_MS));
    }
  }, 5000); // 5 second startup delay

  // Handle signals
  process.on('SIGTERM', async () => {
    await log('Received SIGTERM — shutting down');
    try { await fs.unlink(PID_FILE); } catch { /* ok */ }
    process.exit(0);
  });
  process.on('SIGINT', async () => {
    await log('Received SIGINT — shutting down');
    try { await fs.unlink(PID_FILE); } catch { /* ok */ }
    process.exit(0);
  });
}

async function runOnce() {
  await log('Running single dream session...');
  try {
    const summary = await runSession();
    await log(`Done: ${summary.dreamsGenerated} dreams, ${summary.cyclesCompleted} cycles`);
    console.log(JSON.stringify(summary, null, 2));
  } catch (err) {
    await log('Error: ' + err.message);
    process.exit(1);
  }
}

async function showStatus() {
  try {
    const status = JSON.parse(await fs.readFile(STATUS_FILE, 'utf8'));
    console.log(JSON.stringify(status, null, 2));
  } catch {
    console.log('No status file found. Daemon may not have run yet.');
  }
  try {
    const pid = (await fs.readFile(PID_FILE, 'utf8')).trim();
    // Check if running
    try {
      process.kill(parseInt(pid), 0);
      console.log(`Daemon running (PID ${pid})`);
    } catch {
      console.log(`Daemon not running (stale PID ${pid})`);
    }
  } catch {
    console.log('No PID file found.');
  }
}

// CLI entry
if (import.meta.url === `file://${process.argv[1]}`) {
  const cmd = process.argv[2] || 'start';
  switch (cmd) {
    case 'start':
      daemonLoop();
      break;
    case 'once':
      runOnce().then(() => process.exit(0));
      break;
    case 'status':
      showStatus().then(() => process.exit(0));
      break;
    default:
      console.log('Usage: node dream-daemon.js [start|once|status]');
      process.exit(0);
  }
}

export { runSession, daemonLoop };
