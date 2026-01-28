#!/usr/bin/env node

/**
 * Atlas Gamma Tracker - Gamma Exposure Calculator
 * Calculates dealer gamma positioning and potential squeeze zones
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

async function getSpotPrice(symbol) {
  try {
    const quote = await alpacaRequest(`/v2/stocks/${symbol}/quotes/latest`);
    return quote.quote?.ap || null;
  } catch (err) {
    console.warn('Failed to get spot price:', err.message);
    return null;
  }
}

async function getOptionsChain(symbol) {
  try {
    const contracts = await alpacaRequest(`/v2/options/contracts?underlying_symbols=${symbol}&limit=200`);
    return contracts.options_contracts || [];
  } catch (err) {
    console.warn('Failed to fetch options:', err.message);
    return [];
  }
}

function calculateGammaExposure(contracts, spotPrice) {
  if (!contracts.length || !spotPrice) return null;
  
  // Simplified gamma calculation
  // Real implementation would need Black-Scholes for accurate gamma
  // This is a directional estimate
  
  const gammaByStrike = {};
  
  contracts.forEach(c => {
    const strike = c.strike_price;
    const oi = c.open_interest || 0;
    const contractSize = 100;
    
    // Approximate gamma (peaks ATM, decays away)
    const moneyness = Math.abs(spotPrice - strike) / spotPrice;
    const gamma = Math.exp(-10 * moneyness * moneyness) * 0.01; // Simplified gamma curve
    
    // Dealer position: short calls = negative gamma, short puts = negative gamma
    const dealerGamma = (c.type === 'call' ? -1 : -1) * gamma * oi * contractSize * spotPrice * spotPrice * 0.01;
    
    if (!gammaByStrike[strike]) gammaByStrike[strike] = 0;
    gammaByStrike[strike] += dealerGamma;
  });
  
  // Find key levels
  const strikes = Object.keys(gammaByStrike).map(Number).sort((a, b) => a - b);
  const gammaLevels = strikes.map(s => ({ strike: s, gamma: gammaByStrike[s] }));
  
  const totalGamma = gammaLevels.reduce((sum, l) => sum + l.gamma, 0);
  const maxGamma = Math.max(...gammaLevels.map(l => Math.abs(l.gamma)));
  
  // Identify gamma walls (high concentration)
  const walls = gammaLevels
    .filter(l => Math.abs(l.gamma) > maxGamma * 0.3)
    .sort((a, b) => Math.abs(b.gamma) - Math.abs(a.gamma))
    .slice(0, 5);
  
  return {
    spotPrice,
    totalGamma: totalGamma.toFixed(0),
    dealerPosition: totalGamma < 0 ? 'SHORT GAMMA' : 'LONG GAMMA',
    walls,
    strikes: gammaLevels
  };
}

async function main() {
  const symbol = process.argv[2] || 'SPY';
  
  console.log(`⚡ Atlas Gamma Tracker - ${symbol}\n`);
  
  const [spotPrice, contracts] = await Promise.all([
    getSpotPrice(symbol),
    getOptionsChain(symbol)
  ]);
  
  if (!contracts.length) {
    console.log('❌ No options data available');
    console.log('ℹ️  Note: Gamma tracking requires live options data');
    return;
  }
  
  const analysis = calculateGammaExposure(contracts, spotPrice);
  
  console.log('📊 Gamma Exposure Analysis:');
  console.log(`  Symbol: ${symbol}`);
  console.log(`  Spot Price: $${analysis.spotPrice.toFixed(2)}`);
  console.log(`  Total Gamma: ${analysis.totalGamma}`);
  console.log(`  Dealer Position: ${analysis.dealerPosition}`);
  
  console.log(`\n🧱 Key Gamma Walls:`);
  analysis.walls.forEach((w, i) => {
    const direction = w.gamma < 0 ? '📉' : '📈';
    console.log(`  ${i + 1}. $${w.strike.toFixed(2)} ${direction} (${w.gamma.toFixed(0)} gamma)`);
  });
  
  console.log(`\n💡 Interpretation:`);
  if (analysis.dealerPosition === 'SHORT GAMMA') {
    console.log('  ⚠️  Dealers short gamma = potential for increased volatility');
    console.log('  📈 Price moves may be amplified by dealer hedging');
  } else {
    console.log('  ✅ Dealers long gamma = volatility dampening');
    console.log('  📉 Price moves may be suppressed by dealer hedging');
  }
  
  // Save
  const timestamp = new Date().toISOString().split('T')[0];
  const mdPath = `/Users/atlasbuilds/clawd/memory/trading/gamma/${timestamp}-${symbol}-gamma.md`;
  
  const markdown = `# Gamma Exposure - ${symbol} - ${timestamp}

**Generated:** ${new Date().toISOString()}

## Summary
- **Symbol:** ${symbol}
- **Spot Price:** $${analysis.spotPrice.toFixed(2)}
- **Total Gamma:** ${analysis.totalGamma}
- **Dealer Position:** ${analysis.dealerPosition}

## Key Gamma Walls
${analysis.walls.map((w, i) => `${i + 1}. **$${w.strike.toFixed(2)}** - ${w.gamma.toFixed(0)} gamma ${w.gamma < 0 ? '(resistance)' : '(support)'}`).join('\n')}

## Interpretation
${analysis.dealerPosition === 'SHORT GAMMA' 
  ? '⚠️ **Dealers short gamma** - Expect increased volatility. Price moves amplified as dealers hedge.' 
  : '✅ **Dealers long gamma** - Expect dampened volatility. Price moves suppressed by dealer hedging.'}

## Trading Implications
${analysis.dealerPosition === 'SHORT GAMMA'
  ? '- Watch for momentum plays\n- Breakouts can accelerate\n- Gamma squeezes possible at key levels'
  : '- Expect mean reversion\n- Breakouts may fail\n- Range-bound likely near gamma walls'}
`;
  
  writeFileSync(mdPath, markdown);
  console.log(`\n💾 Saved to: ${mdPath}`);
}

main().catch(console.error);
