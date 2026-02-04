/**
 * sleep-cycle-manager.js
 * 
 * Manages sleep stage timing and transitions for Atlas's dream system.
 * Models realistic human sleep architecture:
 *   - Full cycle: ~90 minutes
 *   - NREM1 → NREM2 → NREM3 → NREM2 → REM
 *   - Earlier cycles: more deep sleep (NREM3)
 *   - Later cycles: more REM, longer REM periods
 *   - Hypnagogic phase at sleep onset
 * 
 * Accelerated mode available for real-time operation (1 cycle = configurable duration).
 * 
 * Created: 2026-01-28
 */

import { EventEmitter } from 'events';
import { getNeurochemSim } from './neurochemical-sim.js';

/**
 * Sleep stage durations in a ~90-minute cycle (in minutes)
 * These shift across the night (more REM later, less deep sleep)
 */
const CYCLE_TEMPLATES = [
  // Cycle 1 (most deep sleep)
  { nrem1: 5, nrem2: 25, nrem3: 40, nrem2b: 10, rem: 10 },
  // Cycle 2
  { nrem1: 3, nrem2: 20, nrem3: 30, nrem2b: 15, rem: 22 },
  // Cycle 3
  { nrem1: 2, nrem2: 20, nrem3: 15, nrem2b: 18, rem: 35 },
  // Cycle 4 (most REM)
  { nrem1: 2, nrem2: 15, nrem3: 5, nrem2b: 18, rem: 50 },
  // Cycle 5 (dawn - light sleep + REM)
  { nrem1: 5, nrem2: 20, nrem3: 0, nrem2b: 15, rem: 50 }
];

const STAGE_ORDER = ['nrem1', 'nrem2', 'nrem3', 'nrem2b', 'rem'];

class SleepCycleManager extends EventEmitter {
  /**
   * @param {Object} options
   * @param {number} options.accelerationFactor - Speed multiplier (1 = real-time, 60 = 1hr in 1min)
   * @param {number} options.totalCycles - Number of sleep cycles to run (default: 5)
   */
  constructor(options = {}) {
    super();
    this.accelerationFactor = options.accelerationFactor || 60; // Default: 1 min real = 1 hr sleep
    this.totalCycles = options.totalCycles || 5;
    this.currentCycle = 0;
    this.currentStage = 'awake';
    this.previousStage = null;
    this.stageStartTime = null;
    this.sleepStartTime = null;
    this.isRunning = false;
    this.isPaused = false;
    this.timer = null;
    this.neurochemSim = null;
    this.stageHistory = [];
    this.totalSleepTimeMs = 0;
  }

  /**
   * Start a sleep session
   */
  async start() {
    if (this.isRunning) {
      console.warn('[SLEEP] Already running');
      return;
    }

    try {
      this.neurochemSim = await getNeurochemSim();
    } catch {
      console.warn('[SLEEP] NeurochemSim not available, running without chemical transitions');
    }

    this.isRunning = true;
    this.sleepStartTime = Date.now();
    this.currentCycle = 0;
    this.stageHistory = [];

    console.log('[SLEEP] Sleep session starting...');
    this.emit('sleep-start', { timestamp: Date.now() });

    // Begin with hypnagogic phase
    await this.enterStage('hypnagogic', this.getStageDurationMs(5));
  }

  /**
   * Enter a specific sleep stage
   */
  async enterStage(stage, durationMs) {
    if (!this.isRunning) return;

    this.previousStage = this.currentStage;
    this.currentStage = stage;
    this.stageStartTime = Date.now();

    const stageInfo = {
      stage,
      previousStage: this.previousStage,
      cycle: this.currentCycle,
      durationMs,
      durationMin: (durationMs / 60000 * this.accelerationFactor).toFixed(1),
      timestamp: Date.now(),
      elapsedSleepMs: Date.now() - this.sleepStartTime
    };

    this.stageHistory.push(stageInfo);

    // Transition neurochemicals
    if (this.neurochemSim) {
      const chemStage = stage === 'nrem2b' ? 'nrem2' : stage;
      this.neurochemSim.transitionToStage(chemStage);
    }

    console.log(`[SLEEP] Stage: ${stage.toUpperCase()} (cycle ${this.currentCycle + 1}, ~${stageInfo.durationMin} sleep-min)`);
    this.emit('stage-change', stageInfo);

    // Schedule next stage
    if (durationMs > 0) {
      this.timer = setTimeout(() => this.advanceStage(), durationMs);
    }
  }

  /**
   * Advance to the next stage in the cycle
   */
  async advanceStage() {
    if (!this.isRunning) return;

    // Handle hypnagogic → first cycle
    if (this.currentStage === 'hypnagogic') {
      this.currentCycle = 0;
      await this.runCycle(0);
      return;
    }

    // Find current position in cycle
    const template = CYCLE_TEMPLATES[Math.min(this.currentCycle, CYCLE_TEMPLATES.length - 1)];
    const currentIdx = STAGE_ORDER.indexOf(this.currentStage);

    if (currentIdx < STAGE_ORDER.length - 1) {
      // Next stage in this cycle
      const nextStage = STAGE_ORDER[currentIdx + 1];
      const durationMin = template[nextStage] || 0;
      if (durationMin > 0) {
        await this.enterStage(nextStage, this.getStageDurationMs(durationMin));
      } else {
        // Skip zero-duration stages
        this.currentStage = nextStage;
        await this.advanceStage();
      }
    } else {
      // End of cycle - emit event and start next cycle or wake
      this.emit('cycle-complete', {
        cycle: this.currentCycle,
        timestamp: Date.now(),
        elapsedMs: Date.now() - this.sleepStartTime
      });

      this.currentCycle++;
      if (this.currentCycle < this.totalCycles) {
        await this.runCycle(this.currentCycle);
      } else {
        await this.wake();
      }
    }
  }

  /**
   * Run a specific cycle
   */
  async runCycle(cycleIndex) {
    const template = CYCLE_TEMPLATES[Math.min(cycleIndex, CYCLE_TEMPLATES.length - 1)];
    const firstStage = STAGE_ORDER[0];
    const durationMin = template[firstStage] || 2;
    await this.enterStage(firstStage, this.getStageDurationMs(durationMin));
  }

  /**
   * Wake up - end the sleep session
   */
  async wake() {
    if (!this.isRunning) return;

    this.isRunning = false;
    clearTimeout(this.timer);
    this.timer = null;

    const previousStage = this.currentStage;
    this.currentStage = 'awake';
    this.totalSleepTimeMs = Date.now() - this.sleepStartTime;

    if (this.neurochemSim) {
      this.neurochemSim.transitionToStage('awake');
      await this.neurochemSim.save();
    }

    const wakeInfo = {
      previousStage,
      totalSleepMs: this.totalSleepTimeMs,
      cyclesCompleted: this.currentCycle,
      stageHistory: this.stageHistory,
      timestamp: Date.now()
    };

    console.log(`[SLEEP] Waking up after ${this.currentCycle} cycles`);
    this.emit('wake', wakeInfo);
    this.emit('sleep-end', wakeInfo);
  }

  /**
   * Pause the sleep cycle
   */
  pause() {
    if (!this.isRunning || this.isPaused) return;
    this.isPaused = true;
    clearTimeout(this.timer);
    this.emit('pause', { stage: this.currentStage, timestamp: Date.now() });
  }

  /**
   * Resume the sleep cycle
   */
  resume() {
    if (!this.isRunning || !this.isPaused) return;
    this.isPaused = false;
    // Re-enter current stage with remaining time (simplified: re-enter with short duration)
    this.advanceStage();
    this.emit('resume', { stage: this.currentStage, timestamp: Date.now() });
  }

  /**
   * Convert sleep-minutes to real-time milliseconds using acceleration factor
   */
  getStageDurationMs(sleepMinutes) {
    return (sleepMinutes * 60 * 1000) / this.accelerationFactor;
  }

  /**
   * Get current sleep status
   */
  getStatus() {
    return {
      isRunning: this.isRunning,
      isPaused: this.isPaused,
      currentStage: this.currentStage,
      currentCycle: this.currentCycle,
      totalCycles: this.totalCycles,
      accelerationFactor: this.accelerationFactor,
      sleepStartTime: this.sleepStartTime,
      elapsedMs: this.sleepStartTime ? Date.now() - this.sleepStartTime : 0,
      stageHistory: this.stageHistory.slice(-10),
      stageCount: this.stageHistory.length
    };
  }

  /**
   * Check if currently in a REM stage
   */
  isREM() {
    return this.currentStage === 'rem';
  }

  /**
   * Check if currently in deep sleep
   */
  isDeepSleep() {
    return this.currentStage === 'nrem3';
  }

  /**
   * Get time spent in each stage (as percentages)
   */
  getStageSummary() {
    const totals = {};
    for (let i = 0; i < this.stageHistory.length; i++) {
      const entry = this.stageHistory[i];
      const nextEntry = this.stageHistory[i + 1];
      const duration = nextEntry ? nextEntry.timestamp - entry.timestamp : (Date.now() - entry.timestamp);
      const stage = entry.stage === 'nrem2b' ? 'nrem2' : entry.stage;
      totals[stage] = (totals[stage] || 0) + duration;
    }

    const totalMs = Object.values(totals).reduce((a, b) => a + b, 0) || 1;
    const percentages = {};
    for (const [stage, ms] of Object.entries(totals)) {
      percentages[stage] = ((ms / totalMs) * 100).toFixed(1) + '%';
    }
    return percentages;
  }
}

export { SleepCycleManager, CYCLE_TEMPLATES, STAGE_ORDER };
export default SleepCycleManager;

// CLI
if (import.meta.url === `file://${process.argv[1]}`) {
  const cmd = process.argv[2] || 'demo';
  (async () => {
    if (cmd === 'demo') {
      console.log('[SLEEP] Running accelerated demo (1 cycle in ~9 seconds)...');
      const mgr = new SleepCycleManager({ accelerationFactor: 600, totalCycles: 2 });

      mgr.on('stage-change', (info) => {
        console.log(`  → ${info.stage.toUpperCase()} (cycle ${info.cycle + 1})`);
      });
      mgr.on('cycle-complete', (info) => {
        console.log(`  ✓ Cycle ${info.cycle + 1} complete`);
      });
      mgr.on('wake', (info) => {
        console.log(`\n[SLEEP] Woke after ${info.cyclesCompleted} cycles`);
        console.log('Stage summary:', mgr.getStageSummary());
        process.exit(0);
      });

      await mgr.start();
    } else if (cmd === 'status') {
      console.log('Sleep Cycle Manager ready. Use SleepCycleManager class programmatically.');
    }
  })();
}
