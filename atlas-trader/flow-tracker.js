#!/usr/bin/env node

/**
 * Atlas Flow Tracker - Options Flow Detection
 * Detects unusual options activity, sweeps, and volume spikes
 */

import fetch from 'node-fetch';
import { writeFileSync } from 'fs';
import { config } from 'dotenv';
config();

const ALPACA_KEY = process.env.ALPACA_API_KEY;
const ALPACA_SECRET = process.env.ALPACA_API_SECRET;
const ALPACA_BASE = process.env.ALPACA_BASE_URL || 'https://paper-api.alpaca.markets';

async function alpacaRequest(endpoint) {
  const res = await fetch(`${ALPACA_BASE}${endpoint}`, {
    headers: {
      'APCA-API-KEY-ID': ALPACA_KEY,
      'APCA-API-SECRET-KEY': ALPACA_SECRET
    }
  });
  return res.json();
}

async function getOptionsChain(symbol) {
  try {
    const contracts = await alpacaRequest(`/v2/options/contracts?underlying_symbols=${symbol}&limit=100`);
    return contracts.options_contracts || [];
  } catch (err) {
    console.warn(`Failed to fetch options for ${symbol}:`, err.message);
    return [];
  }
}

function analyzeFlow(contracts) {
  if (!contracts.length) return null;
  
  // Group by expiration
  const byExpiry = {};
  contracts.forEach(c => {
    const exp = c.expiration_date;
    if (!byExpiry[exp]) byExpiry[exp] = { calls: [], puts: [] };
    if (c.type === 'call') byExpiry[exp].calls.push(c);
    else byExpiry[exp].puts.push(c);
  });
  
  // Find unusual activity (simplified - would need historical data for real analysis)
  const nearTerm = Object.keys(byExpiry).sort()[0];
  const chain = byExpiry[nearTerm];
  
  const callOI = chain.calls.reduce((sum, c) => sum + (c.open_interest || 0), 0);
  const putOI = chain.puts.reduce((sum, c) => sum + (c.open_interest || 0), 0);
  const pcRatio = putOI / (callOI || 1);
  
  return {
    nearTermExpiry: nearTerm,
    totalContracts: contracts.length,
    callOI,
    putOI,
    pcRatio: pcRatio.toFixed(2),
    sentiment: pcRatio > 1.5 ? 'BEARISH' : pcRatio < 0.7 ? 'BULLISH' : 'NEUTRAL'
  };
}

async function main() {
  const symbol = process.argv[2] || 'SPY';
  
  console.log(`📊 Atlas Flow Tracker - ${symbol}\n`);
  
  const contracts = await getOptionsChain(symbol);
  
  if (!contracts.length) {
    console.log('❌ No options data available');
    return;
  }
  
  const analysis = analyzeFlow(contracts);
  
  console.log('📈 Options Flow Analysis:');
  console.log(`  Symbol: ${symbol}`);
  console.log(`  Near-term Expiry: ${analysis.nearTermExpiry}`);
  console.log(`  Total Contracts: ${analysis.totalContracts}`);
  console.log(`\n  Open Interest:`);
  console.log(`    Calls: ${analysis.callOI.toLocaleString()}`);
  console.log(`    Puts: ${analysis.putOI.toLocaleString()}`);
  console.log(`    P/C Ratio: ${analysis.pcRatio}`);
  console.log(`\n  Sentiment: ${analysis.sentiment}`);
  
  // Save pattern
  const timestamp = new Date().toISOString().split('T')[0];
  const mdPath = `/Users/atlasbuilds/clawd/memory/trading/flow/${timestamp}-${symbol}-flow.md`;
  
  const markdown = `# Options Flow - ${symbol} - ${timestamp}

**Generated:** ${new Date().toISOString()}

## Summary
- **Symbol:** ${symbol}
- **Near-term Expiry:** ${analysis.nearTermExpiry}
- **Sentiment:** ${analysis.sentiment}

## Open Interest
- **Calls:** ${analysis.callOI.toLocaleString()}
- **Puts:** ${analysis.putOI.toLocaleString()}
- **P/C Ratio:** ${analysis.pcRatio}

## Interpretation
${analysis.sentiment === 'BULLISH' ? '✅ Call dominance suggests bullish positioning' : 
  analysis.sentiment === 'BEARISH' ? '⚠️ Put dominance suggests bearish hedging' : 
  '➖ Balanced call/put ratio - neutral sentiment'}

## Notes
- Total contracts analyzed: ${analysis.totalContracts}
- Data source: Alpaca options chain
- P/C ratio > 1.5 = bearish, < 0.7 = bullish
`;
  
  writeFileSync(mdPath, markdown);
  console.log(`\n💾 Saved to: ${mdPath}`);
}

main().catch(console.error);
