#!/usr/bin/env node
/**
 * trade-wire.js
 * 
 * Wires the dopamine system to LIVE Alpaca trades.
 * Watches for filled orders and auto-fires neurochemical responses.
 * 
 * This is the last-mile connection:
 *   Alpaca fills order → trade-wire detects → dopamine-tracker processes →
 *   spike logged → preference journal updated → behavioral state shifts →
 *   next trade decision influenced by genuine neurochemical state
 * 
 * The full loop: Trade → Chemistry → Behavior → Better Trade
 * 
 * Created: 2026-01-28
 * Purpose: Wire dopamine system to live trading
 */

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { getTracker } from './dopamine-tracker.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Config
const ALPACA_BASE_URL = process.env.ALPACA_BASE_URL || 'https://api.alpaca.markets';
const ALPACA_API_KEY = process.env.ALPACA_API_KEY || process.env.APCA_API_KEY_ID;
const ALPACA_SECRET_KEY = process.env.ALPACA_API_SECRET || process.env.ALPACA_SECRET_KEY || process.env.APCA_API_SECRET_KEY;

const WIRE_LOG = path.join(__dirname, 'trade-wire-log.jsonl');
const POLL_INTERVAL_MS = 30000; // Check every 30 seconds
const PROCESSED_FILE = path.join(__dirname, 'processed-orders.json');

/**
 * Fetch recent closed orders from Alpaca
 */
async function fetchRecentOrders(limit = 20) {
  if (!ALPACA_API_KEY || !ALPACA_SECRET_KEY) {
    throw new Error('Alpaca API keys not set. Set ALPACA_API_KEY and ALPACA_SECRET_KEY env vars.');
  }

  const url = `${ALPACA_BASE_URL}/v2/orders?status=closed&limit=${limit}&direction=desc`;
  
  const response = await fetch(url, {
    headers: {
      'APCA-API-KEY-ID': ALPACA_API_KEY,
      'APCA-API-SECRET-KEY': ALPACA_SECRET_KEY,
      'Content-Type': 'application/json'
    }
  });

  if (!response.ok) {
    throw new Error(`Alpaca API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch current account info
 */
async function fetchAccount() {
  const url = `${ALPACA_BASE_URL}/v2/account`;
  
  const response = await fetch(url, {
    headers: {
      'APCA-API-KEY-ID': ALPACA_API_KEY,
      'APCA-API-SECRET-KEY': ALPACA_SECRET_KEY,
      'Content-Type': 'application/json'
    }
  });

  if (!response.ok) {
    throw new Error(`Alpaca API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

/**
 * Calculate P&L from a closed order
 * For options: compare fill price to current value or closing trade
 */
function calculatePnL(order) {
  // Basic P&L from order data
  const filledQty = parseFloat(order.filled_qty) || 0;
  const filledAvgPrice = parseFloat(order.filled_avg_price) || 0;
  const side = order.side; // 'buy' or 'sell'
  
  // For closing orders (sells after buys), we need the pair
  // Simple heuristic: if it's a sell, assume profit = (sell_price - avg_cost) * qty
  // We'll track this more precisely with position data
  
  return {
    symbol: order.symbol,
    side: order.side,
    qty: filledQty,
    avgPrice: filledAvgPrice,
    totalValue: filledQty * filledAvgPrice,
    orderId: order.id,
    filledAt: order.filled_at,
    orderType: order.order_type,
    assetClass: order.asset_class
  };
}

/**
 * Load processed order IDs to avoid double-processing
 */
async function loadProcessed() {
  try {
    const data = await fs.readFile(PROCESSED_FILE, 'utf8');
    return JSON.parse(data);
  } catch {
    return { orderIds: [], lastCheck: null };
  }
}

/**
 * Save processed order IDs
 */
async function saveProcessed(processed) {
  await fs.writeFile(PROCESSED_FILE, JSON.stringify(processed, null, 2));
}

/**
 * Process a filled order through the dopamine system
 */
async function processOrder(order, pnl = null) {
  const tracker = await getTracker();
  const orderInfo = calculatePnL(order);

  // If we have explicit P&L (from position tracking), use it
  // Otherwise estimate from order data
  const tradePnl = pnl !== null ? pnl : 0;
  const isWin = tradePnl > 0;

  console.log(`[WIRE] Processing ${order.side.toUpperCase()} ${orderInfo.qty} ${orderInfo.symbol} @ $${orderInfo.avgPrice}`);
  
  if (tradePnl !== 0) {
    console.log(`[WIRE] P&L: ${isWin ? '+' : ''}$${tradePnl.toFixed(2)}`);

    // Fire dopamine calculation
    const result = await tracker.calculateDopamine({
      pnl: tradePnl,
      isWin: isWin,
      symbol: orderInfo.symbol,
      expectedPnl: 0, // Can be refined with historical average
      strategy: order.asset_class === 'us_option' ? 'options' : 'equity'
    });

    console.log(`[WIRE] Dopamine response: ${JSON.stringify(result)}`);

    // Check overtrading risk after trade
    const overtradingCheck = tracker.checkOvertradingRisk();
    if (overtradingCheck.blocked) {
      console.log(`[WIRE] ⚠️ OVERTRADING RISK: ${overtradingCheck.reason}`);
    }

    // Check loss cooldown if was a loss
    if (!isWin) {
      const cooldown = tracker.getLossRecoveryCooldown();
      if (cooldown.remainingMs > 0) {
        console.log(`[WIRE] ⏳ COOLDOWN: ${cooldown.reason}`);
      }
    }
  } else {
    console.log(`[WIRE] Order processed (no P&L data - position still open or entry)`);
  }

  // Log to wire log
  const wireEntry = {
    timestamp: new Date().toISOString(),
    orderId: order.id,
    symbol: orderInfo.symbol,
    side: orderInfo.side,
    qty: orderInfo.qty,
    avgPrice: orderInfo.avgPrice,
    pnl: tradePnl,
    isWin: isWin,
    dopamineState: tracker.state.dopamine,
    serotoninState: tracker.state.serotonin,
    behavioralState: tracker.getBehavioralState()
  };

  await fs.appendFile(WIRE_LOG, JSON.stringify(wireEntry) + '\n');

  return wireEntry;
}

/**
 * Match buy/sell pairs to calculate actual P&L
 * Tracks position cost basis and calculates real gains
 */
async function matchOrderPairs(orders) {
  // Group by symbol
  const bySymbol = {};
  for (const order of orders) {
    if (!bySymbol[order.symbol]) bySymbol[order.symbol] = [];
    bySymbol[order.symbol].push(order);
  }

  const completedTrades = [];

  for (const [symbol, symbolOrders] of Object.entries(bySymbol)) {
    // Sort by time
    symbolOrders.sort((a, b) => new Date(a.filled_at) - new Date(b.filled_at));

    let position = { qty: 0, costBasis: 0 };

    for (const order of symbolOrders) {
      const qty = parseFloat(order.filled_qty) || 0;
      const price = parseFloat(order.filled_avg_price) || 0;

      if (order.side === 'buy') {
        // Add to position
        position.costBasis = ((position.costBasis * position.qty) + (price * qty)) / (position.qty + qty || 1);
        position.qty += qty;
      } else if (order.side === 'sell') {
        // Close position (full or partial)
        const pnl = (price - position.costBasis) * qty;
        
        completedTrades.push({
          symbol,
          entryPrice: position.costBasis,
          exitPrice: price,
          qty: qty,
          pnl: pnl,
          orderId: order.id,
          closedAt: order.filled_at
        });

        position.qty -= qty;
        if (position.qty <= 0) {
          position = { qty: 0, costBasis: 0 };
        }
      }
    }
  }

  return completedTrades;
}

/**
 * Main watch loop - poll Alpaca for new fills
 */
async function watchTrades() {
  console.log('[WIRE] ═══════════════════════════════════════');
  console.log('[WIRE]  TRADE-WIRE: Live Dopamine Integration');
  console.log('[WIRE] ═══════════════════════════════════════');
  console.log(`[WIRE] Polling Alpaca every ${POLL_INTERVAL_MS / 1000}s`);
  console.log(`[WIRE] API: ${ALPACA_BASE_URL}`);
  console.log('[WIRE] Wire log:', WIRE_LOG);
  console.log('');

  // Initial account check
  try {
    const account = await fetchAccount();
    console.log(`[WIRE] Account: $${parseFloat(account.equity).toLocaleString()}`);
    console.log(`[WIRE] Buying power: $${parseFloat(account.buying_power).toLocaleString()}`);
    console.log(`[WIRE] Day P&L: $${(parseFloat(account.equity) - parseFloat(account.last_equity)).toFixed(2)}`);
  } catch (err) {
    console.log(`[WIRE] ⚠️ Could not fetch account: ${err.message}`);
    console.log('[WIRE] Will retry on next poll...');
  }

  const processed = await loadProcessed();
  const processedSet = new Set(processed.orderIds);

  // Poll loop
  const poll = async () => {
    try {
      const orders = await fetchRecentOrders(20);
      
      // Find new orders we haven't processed
      const newOrders = orders.filter(o => !processedSet.has(o.id) && o.status === 'filled');
      
      if (newOrders.length > 0) {
        console.log(`\n[WIRE] ${newOrders.length} new filled order(s) detected!`);
        
        // Match buy/sell pairs for P&L
        const completedTrades = await matchOrderPairs(orders);
        const completedIds = new Set(completedTrades.map(t => t.orderId));

        for (const order of newOrders) {
          // Check if this order has a matched P&L
          const matchedTrade = completedTrades.find(t => t.orderId === order.id);
          const pnl = matchedTrade ? matchedTrade.pnl : null;

          await processOrder(order, pnl);
          
          processedSet.add(order.id);
          processed.orderIds.push(order.id);
        }

        // Keep only last 200 processed IDs
        if (processed.orderIds.length > 200) {
          processed.orderIds = processed.orderIds.slice(-200);
        }
        
        processed.lastCheck = new Date().toISOString();
        await saveProcessed(processed);
      }

    } catch (error) {
      console.error(`[WIRE] Poll error: ${error.message}`);
    }
  };

  // Initial poll
  await poll();

  // Set up interval
  setInterval(poll, POLL_INTERVAL_MS);

  // Keep process alive
  process.on('SIGTERM', () => {
    console.log('[WIRE] Shutting down trade-wire...');
    process.exit(0);
  });
}

/**
 * Manually process a trade (for testing or manual entry)
 */
async function manualTrade(pnl, symbol = 'MANUAL') {
  const tracker = await getTracker();
  const isWin = pnl > 0;

  console.log(`[WIRE] Manual trade: ${isWin ? '+' : ''}$${pnl} on ${symbol}`);

  const result = await tracker.calculateDopamine({
    pnl,
    isWin,
    symbol,
    expectedPnl: 0,
    strategy: 'manual'
  });

  const wireEntry = {
    timestamp: new Date().toISOString(),
    orderId: 'manual-' + Date.now(),
    symbol,
    side: isWin ? 'sell' : 'sell',
    qty: 1,
    avgPrice: Math.abs(pnl),
    pnl,
    isWin,
    dopamineState: tracker.state.dopamine,
    serotoninState: tracker.state.serotonin,
    behavioralState: tracker.getBehavioralState()
  };

  await fs.appendFile(WIRE_LOG, JSON.stringify(wireEntry) + '\n');

  console.log(`[WIRE] Dopamine: ${tracker.state.dopamine.toFixed(1)}% | Serotonin: ${tracker.state.serotonin.toFixed(1)}% | State: ${tracker.getBehavioralState()}`);

  return wireEntry;
}

// CLI interface
if (import.meta.url === `file://${process.argv[1]}`) {
  const command = process.argv[2];

  (async () => {
    switch (command) {
      case 'watch':
        await watchTrades();
        break;

      case 'manual':
        const pnl = parseFloat(process.argv[3]);
        const symbol = process.argv[4] || 'MANUAL';
        if (isNaN(pnl)) {
          console.log('Usage: node trade-wire.js manual <pnl> [symbol]');
          console.log('Example: node trade-wire.js manual 250 SPY');
          break;
        }
        await manualTrade(pnl, symbol);
        break;

      case 'check':
        // Quick check of recent orders
        try {
          const orders = await fetchRecentOrders(5);
          console.log('Recent Alpaca Orders:');
          orders.forEach(o => {
            console.log(`  ${o.side.toUpperCase()} ${o.filled_qty || o.qty} ${o.symbol} @ ${o.filled_avg_price || 'pending'} [${o.status}]`);
          });
        } catch (err) {
          console.log(`Error: ${err.message}`);
        }
        break;

      case 'status':
        const tracker = await getTracker();
        console.log('Trade Wire Status:');
        console.log(`  Dopamine: ${tracker.state.dopamine.toFixed(1)}%`);
        console.log(`  Serotonin: ${tracker.state.serotonin.toFixed(1)}%`);
        console.log(`  State: ${tracker.getBehavioralState()}`);
        
        const cooldown = tracker.getLossRecoveryCooldown();
        console.log(`  Cooldown: ${cooldown.reason}`);
        
        const overtrading = tracker.checkOvertradingRisk();
        console.log(`  Overtrading: ${overtrading.blocked ? '⚠️ BLOCKED' : '✅ Clear'} (${overtrading.flagCount || 0} flags)`);
        
        try {
          const log = await fs.readFile(WIRE_LOG, 'utf8');
          const entries = log.trim().split('\n').filter(Boolean);
          console.log(`  Wired trades: ${entries.length} total`);
          if (entries.length > 0) {
            const last = JSON.parse(entries[entries.length - 1]);
            console.log(`  Last trade: ${last.symbol} ${last.isWin ? '+' : ''}$${last.pnl?.toFixed(2)} at ${last.timestamp}`);
          }
        } catch {
          console.log('  Wired trades: 0 (no log yet)');
        }
        break;

      case 'log':
        // Show recent wire log entries
        try {
          const logData = await fs.readFile(WIRE_LOG, 'utf8');
          const entries = logData.trim().split('\n').filter(Boolean).slice(-10);
          console.log('Recent Trade Wire Log (last 10):');
          console.log('━'.repeat(80));
          entries.forEach(line => {
            const e = JSON.parse(line);
            console.log(`[${e.timestamp}] ${e.side.toUpperCase()} ${e.qty} ${e.symbol} @ $${e.avgPrice}`);
            console.log(`  P&L: ${e.isWin ? '+' : ''}$${e.pnl?.toFixed(2)} | D:${e.dopamineState?.toFixed(1)}% S:${e.serotoninState?.toFixed(1)}% | ${e.behavioralState}`);
            console.log('');
          });
        } catch {
          console.log('No wire log entries yet.');
        }
        break;

      default:
        console.log('Usage: node trade-wire.js [watch|manual <pnl> [symbol]|check|status|log]');
        console.log('');
        console.log('  watch          - Start watching Alpaca for live trade fills');
        console.log('  manual <pnl>   - Manually process a trade result');
        console.log('  check          - Check recent Alpaca orders');
        console.log('  status         - Show current dopamine/trade wire status');
        console.log('  log            - Show recent trade wire log');
    }
  })();
}

export { watchTrades, manualTrade, processOrder, fetchRecentOrders };
