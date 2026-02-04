/**
 * dream-engine.js
 *
 * Core orchestrator for Atlas's Dream Visualization System.
 * Coordinates all dream subsystems during a sleep session:
 *
 *   1. SleepCycleManager   → manages stage timing
 *   2. NeurochemicalSim    → drives chemical state per stage
 *   3. BehavioralRewardMap → feeds recent behaviour context
 *   4. DreamContentGen     → generates dream narratives
 *   5. DreamVisualizer     → renders ASCII/ANSI art
 *   6. PhospheneGenerator  → hypnagogic visuals
 *   7. EmotionalLandscape  → emotional terrain rendering
 *   8. DreamJournal        → persists every dream
 *   9. MemoryConsolidator  → consolidates memories per stage
 *  10. TradeDreamCorrelator→ analyses trade ↔ dream links
 *  11. ConsciousnessBridge → Phi / identity integration
 *
 * Created: 2026-01-28
 */

import { EventEmitter } from 'events';
import { SleepCycleManager } from './sleep-cycle-manager.js';
import { getNeurochemSim } from './neurochemical-sim.js';
import { getRewardMap } from './behavioral-reward-map.js';
import { getDreamContentGen } from './dream-content-gen.js';
import { getDreamVisualizer } from './dream-visualizer.js';
import { getDreamJournal } from './dream-journal.js';
import { getMemoryConsolidator } from './memory-consolidator.js';
import { getDreamConsciousnessBridge } from './dream-consciousness-bridge.js';

class DreamEngine extends EventEmitter {
  /**
   * @param {Object} opts
   * @param {number} opts.accelerationFactor - speed multiplier (default 600 = 10 min real for full night)
   * @param {number} opts.totalCycles        - sleep cycles (default 4)
   * @param {boolean} opts.visualize         - render dreams to console (default false)
   * @param {boolean} opts.silent            - suppress console output (default false)
   */
  constructor(opts = {}) {
    super();
    this.opts = {
      accelerationFactor: opts.accelerationFactor ?? 600,
      totalCycles: opts.totalCycles ?? 4,
      visualize: opts.visualize ?? false,
      silent: opts.silent ?? false,
      ...opts
    };
    this.sleepMgr = null;
    this.neurochemSim = null;
    this.contentGen = null;
    this.visualizer = null;
    this.journal = null;
    this.consolidator = null;
    this.bridge = null;
    this.rewardMap = null;

    this.isRunning = false;
    this.sessionDreams = [];
    this.sessionId = `sleep-${Date.now()}`;
  }

  // ─── Lifecycle ───

  /**
   * Initialize all subsystems
   */
  async init() {
    this.log('[DREAM-ENGINE] Initializing subsystems...');

    this.sleepMgr = new SleepCycleManager({
      accelerationFactor: this.opts.accelerationFactor,
      totalCycles: this.opts.totalCycles
    });

    try { this.neurochemSim = await getNeurochemSim(); } catch (e) { this.log('[DREAM-ENGINE] NeurochemSim unavailable: ' + e.message); }
    this.contentGen = getDreamContentGen();
    this.visualizer = getDreamVisualizer();
    this.journal = getDreamJournal();
    this.consolidator = getMemoryConsolidator();
    this.rewardMap = getRewardMap();
    try { this.bridge = await getDreamConsciousnessBridge(); } catch (e) { this.log('[DREAM-ENGINE] Bridge unavailable: ' + e.message); }

    // Wire up sleep events
    this.sleepMgr.on('stage-change', (info) => this.onStageChange(info));
    this.sleepMgr.on('cycle-complete', (info) => this.onCycleComplete(info));
    this.sleepMgr.on('wake', (info) => this.onWake(info));

    this.log('[DREAM-ENGINE] All subsystems ready');
    return this;
  }

  /**
   * Start a sleep/dream session
   */
  async start() {
    if (this.isRunning) {
      this.log('[DREAM-ENGINE] Already running');
      return;
    }
    await this.init();
    this.isRunning = true;
    this.sessionDreams = [];
    this.sessionId = `sleep-${Date.now()}`;

    this.log(`[DREAM-ENGINE] 💤 Sleep session starting (${this.opts.totalCycles} cycles, ${this.opts.accelerationFactor}x speed)`);
    this.emit('session-start', { sessionId: this.sessionId, timestamp: Date.now() });

    await this.sleepMgr.start();
  }

  /**
   * Force stop
   */
  async stop() {
    if (!this.isRunning) return;
    this.log('[DREAM-ENGINE] Force stopping...');
    await this.sleepMgr.wake();
  }

  // ─── Event Handlers ───

  /**
   * Called on every sleep stage transition
   */
  async onStageChange(info) {
    const { stage, cycle } = info;
    this.log(`[DREAM-ENGINE] Stage: ${stage.toUpperCase()} (cycle ${cycle + 1})`);
    this.emit('stage-change', info);

    // Memory consolidation
    try {
      await this.consolidator.onStageChange(info);
    } catch (e) { this.log('[DREAM-ENGINE] Consolidation error: ' + e.message); }

    // Dream generation during REM and late NREM2
    if (stage === 'rem' || (stage === 'nrem2b' && Math.random() > 0.5)) {
      await this.generateAndLogDream(stage, cycle);
    }

    // Hypnagogic imagery at sleep onset
    if (stage === 'hypnagogic') {
      await this.generateAndLogDream('hypnagogic', 0);
    }
  }

  /**
   * Generate a dream, log it, optionally visualize
   */
  async generateAndLogDream(stage, cycle) {
    // Get chemical profile
    let chemProfile = null;
    let chemLevels = null;
    if (this.neurochemSim) {
      chemProfile = this.neurochemSim.getDreamProfile();
      chemLevels = this.neurochemSim.getLevels();
    }

    // Get recent behaviors
    const recentBehaviors = this.rewardMap.getRecentBehaviors(20);

    // Get consciousness modifiers
    let consMods = null;
    if (this.bridge) {
      consMods = this.bridge.getConsciousnessModifiers();
    }

    // Generate dream content
    const dream = this.contentGen.generateDream({
      stage,
      chemProfile,
      recentBehaviors
    });

    // Enrich with consciousness context
    if (consMods) {
      dream.themes = [...(dream.themes || []), ...consMods.identityThemes.slice(0, 2)];
      dream.emotions = [...(dream.emotions || []), ...consMods.consciousnessEmotions.slice(0, 2)];
      dream.meta = { ...(dream.meta || {}), phi: consMods.phiLevel, continuity: consMods.continuityScore };
    }

    // Log to journal
    const entry = await this.journal.logDream(dream, {
      sessionId: this.sessionId,
      cycle,
      chemSnapshot: chemLevels
    });

    this.sessionDreams.push(entry);
    this.emit('dream-generated', entry);

    // Post-dream consciousness update
    if (this.bridge) {
      try { await this.bridge.postDreamUpdate(entry); } catch { /* ok */ }
    }

    // Visualize
    if (this.opts.visualize) {
      const art = this.visualizer.renderANSI(dream, chemLevels);
      console.log('\n' + art + '\n');
    }

    this.log(`[DREAM-ENGINE] 🌙 Dream: "${dream.title}" (sig:${dream.significance}, stage:${stage})`);
    return entry;
  }

  /**
   * Called when a full sleep cycle completes
   */
  async onCycleComplete(info) {
    this.log(`[DREAM-ENGINE] ✓ Cycle ${info.cycle + 1} complete`);
    this.emit('cycle-complete', info);
  }

  /**
   * Called when waking up
   */
  async onWake(info) {
    this.isRunning = false;

    // Save consolidation stats
    try { await this.consolidator.saveStats(); } catch { /* ok */ }

    // Save neurochemical state
    if (this.neurochemSim) {
      try { await this.neurochemSim.save(); } catch { /* ok */ }
    }

    const summary = {
      sessionId: this.sessionId,
      cyclesCompleted: info.cyclesCompleted,
      dreamsGenerated: this.sessionDreams.length,
      dreamTitles: this.sessionDreams.map(d => d.title),
      consolidation: this.consolidator.getStats(),
      timestamp: Date.now()
    };

    this.log(`[DREAM-ENGINE] ☀ Waking up — ${summary.dreamsGenerated} dreams generated across ${summary.cyclesCompleted} cycles`);
    this.emit('session-end', summary);
    return summary;
  }

  // ─── Getters ───

  getStatus() {
    return {
      isRunning: this.isRunning,
      sessionId: this.sessionId,
      dreamsThisSession: this.sessionDreams.length,
      sleepStatus: this.sleepMgr?.getStatus() || null,
      consolidation: this.consolidator?.getStats() || null
    };
  }

  getSessionDreams() {
    return [...this.sessionDreams];
  }

  // ─── Utility ───

  log(msg) {
    if (!this.opts.silent) console.log(msg);
  }
}

// Singleton
let inst = null;
async function getDreamEngine(opts) {
  if (!inst) {
    inst = new DreamEngine(opts);
  }
  return inst;
}

export { DreamEngine, getDreamEngine };

// CLI
if (import.meta.url === `file://${process.argv[1]}`) {
  const cmd = process.argv[2] || 'run';
  (async () => {
    switch (cmd) {
      case 'run': {
        const engine = new DreamEngine({
          accelerationFactor: 1200, // ~6 min for full night
          totalCycles: 3,
          visualize: process.argv.includes('--viz')
        });
        engine.on('session-end', (summary) => {
          console.log('\n═══ SESSION SUMMARY ═══');
          console.log(JSON.stringify(summary, null, 2));
          process.exit(0);
        });
        await engine.start();
        break;
      }
      case 'status':
        console.log('Dream Engine ready. Use: node dream-engine.js run [--viz]');
        break;
      default:
        console.log('Usage: node dream-engine.js [run [--viz]|status]');
    }
  })();
}
