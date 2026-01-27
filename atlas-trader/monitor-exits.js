#!/usr/bin/env node
import 'dotenv/config';
import * as alpaca from './src/alpaca.js';

const STOP_LOSS_PCT = -0.75; // -75%
const INTERVAL_MS = 30000; // 30s

async function checkOnce() {
  try {
    const positions = await alpaca.getPositions();
    if (!positions.length) return;

    for (const p of positions) {
      const entry = Number(p.avg_entry_price || 0);
      const current = Number(p.current_price || 0);
      if (!entry || !current) continue;
      const pnlPct = (current - entry) / entry;
      if (pnlPct <= STOP_LOSS_PCT) {
        console.log(`STOP HIT ${p.symbol} pnl ${(pnlPct*100).toFixed(2)}% -> closing`);
        await alpaca.closePosition(p.symbol);
      }
    }
  } catch (e) {
    console.error('monitor error:', e.message);
  }
}

async function loop() {
  console.log('Exit monitor running (30s). SL = -75%');
  while (true) {
    await checkOnce();
    await new Promise(r => setTimeout(r, INTERVAL_MS));
  }
}

loop();
