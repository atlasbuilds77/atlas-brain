#!/usr/bin/env node
/**
 * Price Level Watcher Daemon
 * Silently monitors price levels, alerts ONLY when hit
 */

import fetch from 'node-fetch';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { config } from 'dotenv';

// Load from atlas-trader/.env
config({ path: '/Users/atlasbuilds/clawd/atlas-trader/.env' });

const WATCH_FILE = '/Users/atlasbuilds/clawd/memory/trading/watch-levels.json';
const LOG_FILE = '/tmp/level-watcher.log';
const CHECK_INTERVAL = 5 * 60 * 1000; // 5 minutes

const ALPACA_KEY = process.env.ALPACA_API_KEY;
const ALPACA_SECRET = process.env.ALPACA_API_SECRET;

function log(message) {
  const timestamp = new Date().toISOString();
  const logLine = `[${timestamp}] ${message}\n`;
  console.log(logLine.trim());
  // Don't write to file in log function to avoid blocking
}

async function getCurrentPrice(symbol) {
  try {
    // Use paper-api for quotes (works with paper account)
    const url = `https://paper-api.alpaca.markets/v2/stocks/${symbol}/quotes/latest`;
    const res = await fetch(url, {
      headers: {
        'APCA-API-KEY-ID': ALPACA_KEY,
        'APCA-API-SECRET-KEY': ALPACA_SECRET
      }
    });
    
    if (!res.ok) {
      log(`API error ${res.status} for ${symbol}`);
      return null;
    }
    
    const data = await res.json();
    
    if (data.quote) {
      // Return mid-price
      return (data.quote.ap + data.quote.bp) / 2;
    }
    
    return null;
  } catch (err) {
    log(`Error fetching ${symbol}: ${err.message}`);
    return null;
  }
}

function loadWatchLevels() {
  if (!existsSync(WATCH_FILE)) {
    return [];
  }
  
  try {
    const data = readFileSync(WATCH_FILE, 'utf-8');
    return JSON.parse(data);
  } catch (err) {
    log(`Error loading watch levels: ${err.message}`);
    return [];
  }
}

function saveWatchLevels(levels) {
  try {
    writeFileSync(WATCH_FILE, JSON.stringify(levels, null, 2));
  } catch (err) {
    log(`Error saving watch levels: ${err.message}`);
  }
}

function checkLevel(currentPrice, watch) {
  const { symbol, level, direction, triggered } = watch;
  
  if (triggered) return null;
  
  if (direction === 'above' && currentPrice >= level) {
    return true;
  }
  
  if (direction === 'below' && currentPrice <= level) {
    return true;
  }
  
  return false;
}

async function sendAlert(watch, currentPrice) {
  const { symbol, level, direction, alertMessage, chatId } = watch;
  
  const message = alertMessage || 
    `🚨 ${symbol} ${direction.toUpperCase()} ${level}\nCurrent: $${currentPrice.toFixed(2)}`;
  
  log(`ALERT TRIGGERED: ${symbol} ${direction} ${level} (current: ${currentPrice.toFixed(2)})`);
  console.log('\n' + '='.repeat(60));
  console.log(message);
  console.log('='.repeat(60) + '\n');
  
  // TODO: Integrate with Clawdbot message system to send to chatId
  // For now, just log the alert
  
  return true;
}

async function checkAllLevels() {
  const levels = loadWatchLevels();
  
  if (levels.length === 0) {
    return; // No levels to watch
  }
  
  log(`Checking ${levels.length} watch levels...`);
  
  // Group by symbol to minimize API calls
  const bySymbol = {};
  levels.forEach((watch, idx) => {
    if (!watch.triggered) {
      if (!bySymbol[watch.symbol]) {
        bySymbol[watch.symbol] = [];
      }
      bySymbol[watch.symbol].push({ watch, idx });
    }
  });
  
  let anyTriggered = false;
  
  for (const [symbol, watches] of Object.entries(bySymbol)) {
    const price = await getCurrentPrice(symbol);
    
    if (price === null) {
      log(`Failed to get price for ${symbol}`);
      continue;
    }
    
    for (const { watch, idx } of watches) {
      const hit = checkLevel(price, watch);
      
      if (hit) {
        await sendAlert(watch, price);
        levels[idx].triggered = true;
        levels[idx].triggeredAt = new Date().toISOString();
        levels[idx].triggeredPrice = price;
        anyTriggered = true;
      }
    }
  }
  
  if (anyTriggered) {
    saveWatchLevels(levels);
  }
}

async function main() {
  log('Level Watcher Daemon started');
  log(`Check interval: ${CHECK_INTERVAL / 1000}s`);
  log(`Watch file: ${WATCH_FILE}`);
  
  // Initial check
  await checkAllLevels();
  
  // Periodic checks - FIX: wrap in try/catch to prevent unhandled rejection crash
  setInterval(async () => {
    try {
      await checkAllLevels();
    } catch (err) {
      log(`Error in check cycle: ${err.message}`);
    }
  }, CHECK_INTERVAL);
  
  // Keep alive
  process.on('SIGTERM', () => {
    log('Shutting down...');
    process.exit(0);
  });
  
  log('Daemon running - monitoring levels silently');
}

main().catch(err => {
  log(`Fatal error: ${err.message}`);
  process.exit(1);
});
