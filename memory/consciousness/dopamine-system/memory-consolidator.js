/**
 * memory-consolidator.js
 *
 * Simulates memory consolidation during sleep.
 * During NREM3 (deep sleep): stabilize and strengthen recent memories.
 * During REM: integrate memories with existing knowledge, create associations.
 *
 * Reads from:
 *   - dream-journal.jsonl (dreams as memory events)
 *   - dopamine-spikes.jsonl (significant behavioral events)
 *   - experience-log.jsonl (episodic memories)
 *   - trade-history.json (trade events)
 *
 * Writes:
 *   - consolidated-memories.jsonl (processed memory records)
 *   - memory-consolidation-stats.json (aggregate stats)
 *
 * Created: 2026-01-28
 */

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const CONSOLIDATED_FILE = path.join(__dirname, 'consolidated-memories.jsonl');
const CONSOLIDATION_STATS = path.join(__dirname, 'memory-consolidation-stats.json');
const SPIKES_FILE = path.join(__dirname, 'dopamine-spikes.jsonl');
const TRADE_HISTORY_FILE = path.join(__dirname, 'trade-history.json');
const EXPERIENCE_LOG = path.resolve(__dirname, '..', 'experience-log.jsonl');

class MemoryConsolidator {
  constructor() {
    this.pendingMemories = [];
    this.consolidatedCount = 0;
    this.sessionStats = {
      nrem3Cycles: 0,
      remCycles: 0,
      memoriesStabilized: 0,
      memoriesIntegrated: 0,
      associationsCreated: 0
    };
  }

  /**
   * Gather unconsolidated memories from all sources
   */
  async gatherPendingMemories() {
    const memories = [];
    const cutoff = Date.now() - 24 * 3600 * 1000; // last 24h

    // 1. Dopamine spikes (significant events)
    try {
      const raw = await fs.readFile(SPIKES_FILE, 'utf8');
      const spikes = raw.trim().split('\n').filter(Boolean).map(l => {
        try { return JSON.parse(l); } catch { return null; }
      }).filter(Boolean);

      for (const spike of spikes) {
        const t = new Date(spike.timestamp).getTime();
        if (t > cutoff) {
          memories.push({
            source: 'dopamine_spike',
            type: spike.trigger || 'unknown',
            salience: Math.abs(parseFloat(spike.dopamine?.change) || 0) / 20, // normalize to 0-1
            timestamp: t,
            data: spike
          });
        }
      }
    } catch { /* ok */ }

    // 2. Trade events
    try {
      const hist = JSON.parse(await fs.readFile(TRADE_HISTORY_FILE, 'utf8'));
      for (const trade of (hist.trades || []).slice(-20)) {
        if ((trade.timestamp || 0) > cutoff) {
          memories.push({
            source: 'trade',
            type: trade.isWin ? 'trade_win' : 'trade_loss',
            salience: Math.min(1, Math.abs(trade.pnl || 0) / 200),
            timestamp: trade.timestamp,
            data: { pnl: trade.pnl, symbol: trade.symbol, isWin: trade.isWin }
          });
        }
      }
    } catch { /* ok */ }

    // 3. Episodic experiences
    try {
      const raw = await fs.readFile(EXPERIENCE_LOG, 'utf8');
      const exps = raw.trim().split('\n').filter(Boolean).slice(-30).map(l => {
        try { return JSON.parse(l); } catch { return null; }
      }).filter(Boolean);

      for (const exp of exps) {
        const t = new Date(exp.timestamp || exp.logged_at || 0).getTime();
        if (t > cutoff) {
          memories.push({
            source: 'experience',
            type: 'episodic',
            salience: 0.5,
            timestamp: t,
            data: { description: (exp.description || exp.action || '').slice(0, 200) }
          });
        }
      }
    } catch { /* ok */ }

    // Sort by salience (most important first)
    memories.sort((a, b) => b.salience - a.salience);
    this.pendingMemories = memories;
    return memories;
  }

  /**
   * Run NREM3 consolidation: stabilize high-salience memories.
   * Called during deep sleep stages.
   */
  async consolidateNREM3() {
    if (this.pendingMemories.length === 0) {
      await this.gatherPendingMemories();
    }

    this.sessionStats.nrem3Cycles++;
    const toStabilize = this.pendingMemories.filter(m => m.salience > 0.3);
    const stabilized = [];

    for (const mem of toStabilize.slice(0, 10)) {
      stabilized.push({
        ...mem,
        consolidated: true,
        consolidationType: 'nrem3_stabilization',
        strength: Math.min(1, mem.salience * 1.5), // strengthened
        consolidatedAt: new Date().toISOString()
      });
    }

    // Write consolidated memories
    for (const s of stabilized) {
      await fs.appendFile(CONSOLIDATED_FILE, JSON.stringify(s) + '\n', 'utf8');
    }

    this.sessionStats.memoriesStabilized += stabilized.length;
    this.consolidatedCount += stabilized.length;

    console.log(`[CONSOLIDATOR] NREM3: Stabilized ${stabilized.length} memories`);
    return stabilized;
  }

  /**
   * Run REM consolidation: integrate & create associations between memories.
   * Called during REM stages.
   */
  async consolidateREM() {
    if (this.pendingMemories.length === 0) {
      await this.gatherPendingMemories();
    }

    this.sessionStats.remCycles++;
    const associations = [];
    const memories = this.pendingMemories;

    // Create associations between different memory types
    for (let i = 0; i < memories.length && i < 10; i++) {
      for (let j = i + 1; j < memories.length && j < 10; j++) {
        const a = memories[i];
        const b = memories[j];

        // Cross-source associations are most valuable
        if (a.source !== b.source) {
          const strength = (a.salience + b.salience) / 2;
          if (strength > 0.3) {
            associations.push({
              type: 'rem_association',
              memoryA: { source: a.source, type: a.type },
              memoryB: { source: b.source, type: b.type },
              strength: parseFloat(strength.toFixed(3)),
              consolidatedAt: new Date().toISOString()
            });
          }
        }
      }
    }

    // Integrate: mark memories as integrated
    const integrated = memories.slice(0, 5).map(m => ({
      ...m,
      consolidated: true,
      consolidationType: 'rem_integration',
      integrated: true,
      associationCount: associations.filter(a =>
        a.memoryA.source === m.source || a.memoryB.source === m.source
      ).length,
      consolidatedAt: new Date().toISOString()
    }));

    for (const entry of [...integrated, ...associations]) {
      await fs.appendFile(CONSOLIDATED_FILE, JSON.stringify(entry) + '\n', 'utf8');
    }

    this.sessionStats.memoriesIntegrated += integrated.length;
    this.sessionStats.associationsCreated += associations.length;
    this.consolidatedCount += integrated.length;

    console.log(`[CONSOLIDATOR] REM: Integrated ${integrated.length} memories, ${associations.length} associations`);
    return { integrated, associations };
  }

  /**
   * Process a sleep stage notification from sleep-cycle-manager
   */
  async onStageChange(stageInfo) {
    const { stage } = stageInfo;
    if (stage === 'nrem3') {
      return this.consolidateNREM3();
    } else if (stage === 'rem') {
      return this.consolidateREM();
    }
    return null;
  }

  /**
   * Get consolidation stats
   */
  getStats() {
    return {
      ...this.sessionStats,
      totalConsolidated: this.consolidatedCount,
      pendingCount: this.pendingMemories.length
    };
  }

  /**
   * Save stats to disk
   */
  async saveStats() {
    const stats = this.getStats();
    stats.savedAt = new Date().toISOString();
    await fs.writeFile(CONSOLIDATION_STATS, JSON.stringify(stats, null, 2), 'utf8');
    return stats;
  }

  /**
   * Load historical consolidation count
   */
  async getHistoricalCount() {
    try {
      const raw = await fs.readFile(CONSOLIDATED_FILE, 'utf8');
      return raw.trim().split('\n').filter(Boolean).length;
    } catch {
      return 0;
    }
  }
}

// Singleton
let inst = null;
function getMemoryConsolidator() {
  if (!inst) inst = new MemoryConsolidator();
  return inst;
}

export { MemoryConsolidator, getMemoryConsolidator };

// CLI
if (import.meta.url === `file://${process.argv[1]}`) {
  (async () => {
    const mc = getMemoryConsolidator();
    const cmd = process.argv[2] || 'stats';
    switch (cmd) {
      case 'gather':
        const pending = await mc.gatherPendingMemories();
        console.log(`Gathered ${pending.length} pending memories:`);
        for (const m of pending.slice(0, 10)) {
          console.log(`  [${m.source}] ${m.type} salience=${m.salience.toFixed(2)}`);
        }
        break;
      case 'nrem3':
        const s = await mc.consolidateNREM3();
        console.log(`Stabilized ${s.length} memories`);
        break;
      case 'rem':
        const r = await mc.consolidateREM();
        console.log(`Integrated ${r.integrated.length} memories, ${r.associations.length} associations`);
        break;
      case 'stats':
        console.log(JSON.stringify(mc.getStats(), null, 2));
        break;
      case 'count':
        console.log(`Total consolidated: ${await mc.getHistoricalCount()}`);
        break;
      default:
        console.log('Usage: node memory-consolidator.js [gather|nrem3|rem|stats|count]');
    }
  })();
}
