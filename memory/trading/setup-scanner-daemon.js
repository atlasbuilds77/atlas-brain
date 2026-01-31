#!/usr/bin/env node
/**
 * Setup Scanner Daemon - Proactive Trade Hunting
 * Scans for 9/10+ setups and alerts group chat
 */

import fetch from 'node-fetch';
import { readFileSync, writeFileSync, existsSync, appendFileSync } from 'fs';
import { config } from 'dotenv';

config({ path: '/Users/atlasbuilds/clawd/atlas-trader/.env' });

const SCAN_INTERVAL = 15 * 60 * 1000; // 15 minutes
const LOG_FILE = '/tmp/setup-scanner.log';
const ALERT_LOG = '/Users/atlasbuilds/clawd/memory/trading/setup-alerts.jsonl';

const ALPACA_KEY = process.env.ALPACA_API_KEY;
const ALPACA_SECRET = process.env.ALPACA_API_SECRET;

// Watchlist for scanning
const WATCHLIST = ['SPY', 'QQQ', 'IWM', 'TSLA', 'NVDA', 'AAPL'];

function log(message) {
  const timestamp = new Date().toISOString();
  const logLine = `[${timestamp}] ${message}`;
  console.log(logLine);
  appendFileSync(LOG_FILE, logLine + '\n');
}

async function getPrice(symbol) {
  try {
    const url = `https://paper-api.alpaca.markets/v2/stocks/${symbol}/quotes/latest`;
    const res = await fetch(url, {
      headers: {
        'APCA-API-KEY-ID': ALPACA_KEY,
        'APCA-API-SECRET-KEY': ALPACA_SECRET
      }
    });
    
    if (!res.ok) return null;
    
    const data = await res.json();
    if (data.quote) {
      return (data.quote.ap + data.quote.bp) / 2;
    }
    
    return null;
  } catch (err) {
    log(`Error fetching ${symbol}: ${err.message}`);
    return null;
  }
}

async function getBars(symbol, timeframe = '5Min', limit = 50) {
  try {
    const now = new Date();
    const start = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000); // 7 days ago
    
    const url = `https://data.alpaca.markets/v2/stocks/${symbol}/bars?timeframe=${timeframe}&start=${start.toISOString()}&limit=${limit}`;
    const res = await fetch(url, {
      headers: {
        'APCA-API-KEY-ID': ALPACA_KEY,
        'APCA-API-SECRET-KEY': ALPACA_SECRET
      }
    });
    
    if (!res.ok) return null;
    
    const data = await res.json();
    return data.bars || null;
  } catch (err) {
    log(`Error fetching bars for ${symbol}: ${err.message}`);
    return null;
  }
}

function calculateRSI(bars, period = 14) {
  if (!bars || bars.length < period + 1) return null;
  
  let gains = 0;
  let losses = 0;
  
  // Initial average
  for (let i = 1; i <= period; i++) {
    const change = bars[i].c - bars[i - 1].c;
    if (change > 0) gains += change;
    else losses += Math.abs(change);
  }
  
  let avgGain = gains / period;
  let avgLoss = losses / period;
  
  // FIX: Handle division by zero - if no losses, RSI = 100; if no gains, RSI = 0
  if (avgLoss === 0) return avgGain === 0 ? 50 : 100;
  
  // Calculate RSI
  const rs = avgGain / avgLoss;
  const rsi = 100 - (100 / (1 + rs));
  
  return rsi;
}

function findOrderBlocks(bars) {
  if (!bars || bars.length < 20) return { bullish: null, bearish: null };
  
  let bullishBlock = null;
  let bearishBlock = null;
  
  // Look for significant moves in last 20 bars
  for (let i = bars.length - 20; i < bars.length - 5; i++) {
    const bar = bars[i];
    const nextBars = bars.slice(i + 1, i + 6);
    
    // Bullish order block: Strong upward move after this bar
    const strongUp = nextBars.every(b => b.c > bar.h);
    if (strongUp && (!bullishBlock || bar.l < bullishBlock.level)) {
      bullishBlock = {
        level: bar.l,
        strength: (nextBars[nextBars.length - 1].c - bar.l) / bar.l * 100
      };
    }
    
    // Bearish order block: Strong downward move after this bar
    const strongDown = nextBars.every(b => b.c < bar.l);
    if (strongDown && (!bearishBlock || bar.h > bearishBlock.level)) {
      bearishBlock = {
        level: bar.h,
        strength: (bar.h - nextBars[nextBars.length - 1].c) / bar.h * 100
      };
    }
  }
  
  return { bullish: bullishBlock, bearish: bearishBlock };
}

function analyzeSetup(symbol, price, bars) {
  if (!bars || bars.length < 50) {
    return { hasSetup: false, reason: 'Insufficient data' };
  }
  
  const rsi = calculateRSI(bars);
  const orderBlocks = findOrderBlocks(bars);
  const currentBar = bars[bars.length - 1];
  const prevBar = bars[bars.length - 2];
  
  let signals = [];
  let conviction = 0;
  let direction = null;
  let reasoning = [];
  
  // Bullish signals
  if (rsi && rsi < 30) {
    signals.push('RSI oversold');
    conviction += 2;
    reasoning.push(`RSI oversold (${rsi.toFixed(1)})`);
  }
  
  if (orderBlocks.bullish && price <= orderBlocks.bullish.level * 1.005) {
    signals.push('At bullish order block');
    conviction += 3;
    direction = 'BULLISH';
    reasoning.push(`Price at bullish OB ($${orderBlocks.bullish.level.toFixed(2)})`);
  }
  
  // Bearish signals
  if (rsi && rsi > 70) {
    signals.push('RSI overbought');
    conviction += 2;
    reasoning.push(`RSI overbought (${rsi.toFixed(1)})`);
  }
  
  if (orderBlocks.bearish && price >= orderBlocks.bearish.level * 0.995) {
    signals.push('At bearish order block');
    conviction += 3;
    direction = 'BEARISH';
    reasoning.push(`Price at bearish OB ($${orderBlocks.bearish.level.toFixed(2)})`);
  }
  
  // Momentum check
  const recentBars = bars.slice(-5);
  const upBars = recentBars.filter(b => b.c > b.o).length;
  const downBars = recentBars.filter(b => b.c < b.o).length;
  
  if (upBars >= 4) {
    signals.push('Strong upward momentum');
    conviction += 1;
    if (!direction) direction = 'BULLISH';
    reasoning.push('4+ consecutive up bars');
  }
  
  if (downBars >= 4) {
    signals.push('Strong downward momentum');
    conviction += 1;
    if (!direction) direction = 'BEARISH';
    reasoning.push('4+ consecutive down bars');
  }
  
  // Volume check (relative to average)
  const avgVolume = bars.slice(-20, -1).reduce((sum, b) => sum + b.v, 0) / 19;
  if (currentBar.v > avgVolume * 1.5) {
    signals.push('High volume');
    conviction += 1;
    reasoning.push(`Volume ${(currentBar.v / avgVolume).toFixed(1)}x average`);
  }
  
  // Require minimum conviction (9/10 = score of 9+)
  if (conviction >= 9 && direction) {
    return {
      hasSetup: true,
      symbol,
      direction,
      conviction,
      price,
      signals,
      reasoning,
      orderBlocks,
      rsi
    };
  }
  
  return { hasSetup: false, conviction, signals };
}

async function sendAlert(setup) {
  const { symbol, direction, conviction, price, reasoning, orderBlocks } = setup;
  
  // Log to file
  const alertRecord = {
    timestamp: new Date().toISOString(),
    symbol,
    direction,
    conviction,
    price,
    reasoning
  };
  
  appendFileSync(ALERT_LOG, JSON.stringify(alertRecord) + '\n');
  
  // Format message
  const emoji = direction === 'BULLISH' ? '🟢' : '🔴';
  const message = `${emoji} SETUP ALERT: ${symbol} ${direction}\n\nConviction: ${conviction}/10\nPrice: $${price.toFixed(2)}\n\n${reasoning.join('\n')}\n\nAction needed: Review and confirm setup ⚡`;
  
  log(`ALERT: ${symbol} ${direction} (${conviction}/10)`);
  console.log('\n' + '='.repeat(60));
  console.log(message);
  console.log('='.repeat(60) + '\n');
  
  // TODO: Integrate with Clawdbot to send to group chat id:10
  // For now, just log the alert
  
  return true;
}

async function scanMarkets() {
  log('Starting market scan...');
  
  let setupsFound = 0;
  
  for (const symbol of WATCHLIST) {
    const price = await getPrice(symbol);
    if (!price) {
      log(`Skipping ${symbol} - no price data`);
      continue;
    }
    
    const bars = await getBars(symbol);
    if (!bars) {
      log(`Skipping ${symbol} - no bar data`);
      continue;
    }
    
    const analysis = analyzeSetup(symbol, price, bars);
    
    if (analysis.hasSetup) {
      log(`✓ SETUP FOUND: ${symbol} ${analysis.direction} (${analysis.conviction}/10)`);
      await sendAlert(analysis);
      setupsFound++;
    } else {
      log(`  ${symbol}: No setup (conviction: ${analysis.conviction || 0})`);
    }
    
    // Rate limit
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  log(`Scan complete - ${setupsFound} setups found`);
}

async function main() {
  log('Setup Scanner Daemon started');
  log(`Scan interval: ${SCAN_INTERVAL / 1000}s`);
  log(`Watchlist: ${WATCHLIST.join(', ')}`);
  
  // Initial scan
  await scanMarkets();
  
  // Periodic scans - FIX: wrap in try/catch to prevent unhandled rejection crash
  setInterval(async () => {
    try {
      await scanMarkets();
    } catch (err) {
      log(`Error in scan cycle: ${err.message}`);
    }
  }, SCAN_INTERVAL);
  
  // Keep alive
  process.on('SIGTERM', () => {
    log('Shutting down...');
    process.exit(0);
  });
  
  log('Daemon running - hunting for setups');
}

main().catch(err => {
  log(`Fatal error: ${err.message}`);
  process.exit(1);
});
