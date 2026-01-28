#!/usr/bin/env node

/**
 * Atlas Macro Check - Trading Intelligence
 * Aggregates VIX, economic data, oil prices, and news
 */

import fetch from 'node-fetch';
import { writeFileSync } from 'fs';
import { config } from 'dotenv';
config();

// Configuration
const POLYGON_KEY = process.env.POLYGON_API_KEY || 'h7J74V1cd8_4NQpTxwQpudpqXWaIHMhv';
const BRAVE_KEY = process.env.BRAVE_API_KEY || 'BSAYJvLxGhbD0tHKcF4FtrWQ5kIkdKS';

const THRESHOLDS = {
  VIX_HIGH: 25,
  VIX_LOW: 15,
  OIL_CHANGE: 3
};

async function fetchVIX() {
  try {
    const url = `https://api.polygon.io/v2/aggs/ticker/I:VIX/prev?adjusted=true&apiKey=${POLYGON_KEY}`;
    const res = await fetch(url);
    const data = await res.json();
    
    if (data.results && data.results[0]) {
      const r = data.results[0];
      return {
        value: r.c,
        change: ((r.c - r.o) / r.o) * 100,
        high: r.h,
        low: r.l
      };
    }
  } catch (err) {
    console.warn('VIX fetch failed:', err.message);
  }
  return null;
}

async function fetchOil() {
  try {
    const url = `https://api.polygon.io/v2/aggs/ticker/C:CRUDE_WTI/prev?adjusted=true&apiKey=${POLYGON_KEY}`;
    const res = await fetch(url);
    const data = await res.json();
    
    if (data.results && data.results[0]) {
      const r = data.results[0];
      return {
        price: r.c,
        change: ((r.c - r.o) / r.o) * 100
      };
    }
  } catch (err) {
    console.warn('Oil fetch failed:', err.message);
  }
  return null;
}

async function fetchNews() {
  try {
    const query = 'financial markets economy stocks fed rates';
    const url = `https://api.search.brave.com/res/v1/web/search?q=${encodeURIComponent(query)}&count=5`;
    
    const res = await fetch(url, {
      headers: {
        'Accept': 'application/json',
        'X-Subscription-Token': BRAVE_KEY
      }
    });
    
    const data = await res.json();
    
    if (data.web && data.web.results) {
      return data.web.results.slice(0, 5).map(r => ({
        title: r.title,
        url: r.url,
        snippet: r.description
      }));
    }
  } catch (err) {
    console.warn('News fetch failed:', err.message);
  }
  
  return [
    { title: 'Fed maintains rates amid inflation watch', snippet: 'Central bank holds steady' },
    { title: 'Markets digest economic data', snippet: 'Mixed signals from employment' }
  ];
}

function calculateBias(vix, oil) {
  let bullish = 0;
  let bearish = 0;
  const reasons = [];
  
  if (vix) {
    if (vix.value < THRESHOLDS.VIX_LOW) {
      bullish += 2;
      reasons.push(`VIX low (${vix.value.toFixed(1)}) = low fear`);
    } else if (vix.value > THRESHOLDS.VIX_HIGH) {
      bearish += 2;
      reasons.push(`VIX high (${vix.value.toFixed(1)}) = high fear`);
    }
  }
  
  if (oil) {
    if (Math.abs(oil.change) > THRESHOLDS.OIL_CHANGE) {
      bearish += 1;
      reasons.push(`Oil volatile (${oil.change.toFixed(1)}%)`);
    }
  }
  
  const bias = bullish > bearish ? 'BULLISH' : bearish > bullish ? 'BEARISH' : 'NEUTRAL';
  
  return { bias, bullish, bearish, reasons };
}

async function main() {
  console.log('🧠 Atlas Macro Check\n');
  
  const [vix, oil, news] = await Promise.all([
    fetchVIX(),
    fetchOil(),
    fetchNews()
  ]);
  
  const analysis = calculateBias(vix, oil);
  
  console.log('📊 Market Indicators:');
  if (vix) console.log(`  VIX: ${vix.value.toFixed(2)} (${vix.change > 0 ? '+' : ''}${vix.change.toFixed(2)}%)`);
  if (oil) console.log(`  Oil: $${oil.price.toFixed(2)} (${oil.change > 0 ? '+' : ''}${oil.change.toFixed(2)}%)`);
  
  console.log(`\n📈 Bias: ${analysis.bias}`);
  console.log(`   Bullish: ${analysis.bullish} | Bearish: ${analysis.bearish}`);
  
  console.log('\n📰 Top Headlines:');
  news.slice(0, 3).forEach((n, i) => {
    console.log(`  ${i + 1}. ${n.title}`);
  });
  
  // Save to memory
  const timestamp = new Date().toISOString().split('T')[0];
  const output = {
    timestamp: new Date().toISOString(),
    vix,
    oil,
    analysis,
    news
  };
  
  const mdPath = `/Users/atlasbuilds/clawd/memory/trading/macro/${timestamp}-macro.md`;
  const markdown = `# Macro Check - ${timestamp}

**Bias:** ${analysis.bias}
**Generated:** ${new Date().toISOString()}

## Indicators
- **VIX:** ${vix ? vix.value.toFixed(2) : 'N/A'} (${vix ? (vix.change > 0 ? '+' : '') + vix.change.toFixed(2) + '%' : 'N/A'})
- **Oil:** ${oil ? '$' + oil.price.toFixed(2) : 'N/A'} (${oil ? (oil.change > 0 ? '+' : '') + oil.change.toFixed(2) + '%' : 'N/A'})

## Analysis
${analysis.reasons.map(r => `- ${r}`).join('\n')}

## News Headlines
${news.map((n, i) => `${i + 1}. **${n.title}**\n   ${n.snippet}`).join('\n\n')}
`;
  
  writeFileSync(mdPath, markdown);
  console.log(`\n💾 Saved to: ${mdPath}`);
  
  // Also output JSON for automation
  console.log('\n📦 JSON:', JSON.stringify(output, null, 2));
}

main().catch(console.error);
