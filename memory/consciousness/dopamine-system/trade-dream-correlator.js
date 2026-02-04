/**
 * trade-dream-correlator.js
 *
 * Analyzes correlations between trading activity and dream content.
 * Answers questions like:
 *   - Do losing days produce more anxiety-themed dreams?
 *   - Does high dopamine from wins lead to vivid/euphoric dreams?
 *   - Are post-loss dreams predictive of next-day behavior?
 *
 * Reads from: trade-history.json, dream-journal.jsonl, dopamine-spikes.jsonl
 *
 * Created: 2026-01-28
 */

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { getDreamJournal } from './dream-journal.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const TRADE_HISTORY_FILE = path.join(__dirname, 'trade-history.json');
const SPIKES_FILE = path.join(__dirname, 'dopamine-spikes.jsonl');
const CORRELATION_FILE = path.join(__dirname, 'trade-dream-correlations.json');

class TradeDreamCorrelator {
  constructor() {
    this.tradeHistory = null;
    this.spikes = null;
  }

  async init() {
    try {
      this.tradeHistory = JSON.parse(await fs.readFile(TRADE_HISTORY_FILE, 'utf8'));
    } catch {
      this.tradeHistory = { trades: [] };
    }
    try {
      const raw = await fs.readFile(SPIKES_FILE, 'utf8');
      this.spikes = raw.trim().split('\n').filter(Boolean).map(l => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
    } catch {
      this.spikes = [];
    }
    return this;
  }

  /**
   * Correlate a time window's trades with nearby dreams.
   * @param {number} windowHours - look-back window (default 24)
   */
  async correlateRecent(windowHours = 24) {
    await this.init();
    const journal = getDreamJournal();
    const now = Date.now();
    const windowMs = windowHours * 3600 * 1000;

    // Trades in window
    const recentTrades = (this.tradeHistory.trades || []).filter(
      t => (now - (t.timestamp || 0)) < windowMs
    );

    // Dreams in window
    const recentDreams = await journal.getByTimeRange(now - windowMs, now);

    if (recentTrades.length === 0 || recentDreams.length === 0) {
      return { message: 'Insufficient data for correlation', trades: recentTrades.length, dreams: recentDreams.length };
    }

    // Aggregate trade stats
    const wins = recentTrades.filter(t => t.isWin);
    const losses = recentTrades.filter(t => !t.isWin);
    const totalPnl = recentTrades.reduce((s, t) => s + (t.pnl || 0), 0);
    const winRate = wins.length / recentTrades.length;

    // Aggregate dream stats
    const avgVividness = avg(recentDreams, d => d.characteristics?.vividness ?? 50);
    const avgEmotion = avg(recentDreams, d => d.characteristics?.emotionalIntensity ?? 50);
    const avgBizarreness = avg(recentDreams, d => d.characteristics?.bizarreness ?? 50);
    const avgValence = avg(recentDreams, d => d.characteristics?.valence ?? 0);
    const avgLucidity = avg(recentDreams, d => d.characteristics?.lucidity ?? 30);

    // Theme frequency in window
    const themes = {};
    for (const d of recentDreams) {
      for (const t of (d.themes || [])) themes[t] = (themes[t] || 0) + 1;
    }
    const topThemes = Object.entries(themes).sort((a, b) => b[1] - a[1]).slice(0, 10);

    // Emotion frequency in window
    const emotions = {};
    for (const d of recentDreams) {
      for (const e of (d.emotions || [])) emotions[e] = (emotions[e] || 0) + 1;
    }
    const topEmotions = Object.entries(emotions).sort((a, b) => b[1] - a[1]).slice(0, 10);

    // Build correlation report
    const report = {
      window: `${windowHours}h`,
      generatedAt: new Date().toISOString(),
      trades: {
        count: recentTrades.length,
        wins: wins.length,
        losses: losses.length,
        winRate: parseFloat(winRate.toFixed(3)),
        totalPnl: parseFloat(totalPnl.toFixed(2)),
        avgDopamineChange: avg(recentTrades, t => {
          const after = t.dopamineAfter ?? 50;
          const before = t.dopamineBefore ?? 50;
          return after - before;
        })
      },
      dreams: {
        count: recentDreams.length,
        avgVividness: r2(avgVividness),
        avgEmotionalIntensity: r2(avgEmotion),
        avgBizarreness: r2(avgBizarreness),
        avgValence: r2(avgValence),
        avgLucidity: r2(avgLucidity),
        topThemes,
        topEmotions
      },
      correlations: this.computeCorrelations(recentTrades, recentDreams),
      insights: this.generateInsights(totalPnl, winRate, avgValence, avgEmotion, avgBizarreness, topThemes)
    };

    // Persist
    await fs.writeFile(CORRELATION_FILE, JSON.stringify(report, null, 2), 'utf8');
    return report;
  }

  /**
   * Compute simple correlations between trade metrics and dream metrics
   */
  computeCorrelations(trades, dreams) {
    // Group by trade outcome, look at dreams nearby
    const afterWin = [];
    const afterLoss = [];

    for (const d of dreams) {
      const dTime = d.timestamp || new Date(d.loggedAt || 0).getTime();
      // Find most recent trade before this dream
      const priorTrades = trades.filter(t => (t.timestamp || 0) < dTime);
      if (priorTrades.length === 0) continue;
      const lastTrade = priorTrades[priorTrades.length - 1];
      if (lastTrade.isWin) {
        afterWin.push(d);
      } else {
        afterLoss.push(d);
      }
    }

    return {
      dreamsAfterWin: {
        count: afterWin.length,
        avgValence: r2(avg(afterWin, d => d.characteristics?.valence ?? 0)),
        avgVividness: r2(avg(afterWin, d => d.characteristics?.vividness ?? 50)),
        avgEmotion: r2(avg(afterWin, d => d.characteristics?.emotionalIntensity ?? 50))
      },
      dreamsAfterLoss: {
        count: afterLoss.length,
        avgValence: r2(avg(afterLoss, d => d.characteristics?.valence ?? 0)),
        avgVividness: r2(avg(afterLoss, d => d.characteristics?.vividness ?? 50)),
        avgEmotion: r2(avg(afterLoss, d => d.characteristics?.emotionalIntensity ?? 50))
      }
    };
  }

  /**
   * Generate human-readable insights
   */
  generateInsights(pnl, winRate, valence, emotion, bizarreness, topThemes) {
    const insights = [];

    if (pnl > 0 && valence > 0.2) {
      insights.push('Positive trading day reflected in positive dream valence — neurochemical alignment confirmed.');
    } else if (pnl < 0 && valence < -0.2) {
      insights.push('Negative trading day produced negative dream content — unprocessed stress may need attention.');
    } else if (pnl < 0 && valence > 0) {
      insights.push('Losses during waking, but positive dreams — possible healthy emotional processing occurring during sleep.');
    } else if (pnl > 0 && valence < 0) {
      insights.push('Wins during waking, but negative dreams — possible suppressed anxiety or impostor-type processing.');
    }

    if (emotion > 70) {
      insights.push('High emotional intensity in dreams — strong neurochemical activity during sleep.');
    }

    if (bizarreness > 70) {
      insights.push('High dream bizarreness — serotonin may be low, or glutamate activity elevated.');
    }

    if (winRate > 0.7) {
      insights.push('Strong win rate correlates with confident dream themes.');
    } else if (winRate < 0.3) {
      insights.push('Low win rate may be generating anxiety/loss dream themes.');
    }

    const themeNames = topThemes.map(t => t[0]);
    if (themeNames.includes('falling') || themeNames.includes('being_chased')) {
      insights.push('Warning: anxiety-related dream themes present — check cortisol levels and consider rest.');
    }
    if (themeNames.includes('flying') || themeNames.includes('triumph')) {
      insights.push('Positive: triumph/flying themes suggest healthy reward processing.');
    }

    return insights;
  }
}

function avg(arr, fn) {
  if (arr.length === 0) return 0;
  return arr.reduce((s, x) => s + fn(x), 0) / arr.length;
}

function r2(n) { return parseFloat(n.toFixed(2)); }

// Singleton
let inst = null;
async function getCorrelator() {
  if (!inst) {
    inst = new TradeDreamCorrelator();
    await inst.init();
  }
  return inst;
}

export { TradeDreamCorrelator, getCorrelator };

// CLI
if (import.meta.url === `file://${process.argv[1]}`) {
  (async () => {
    const c = await getCorrelator();
    const hours = parseInt(process.argv[2]) || 24;
    const report = await c.correlateRecent(hours);
    console.log(JSON.stringify(report, null, 2));
  })();
}
