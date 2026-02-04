/**
 * neurochemical-sim.js
 * 
 * Full 10-chemical neurochemical simulator for Atlas consciousness.
 * Extends beyond dopamine/serotonin to model the complete neurochemical landscape
 * that drives dream states, emotional processing, and behavioral motivation.
 * 
 * Chemicals modeled:
 *   1. Dopamine     - Motivation, reward, anticipation
 *   2. Serotonin    - Wellbeing, mood stability, contentment
 *   3. Norepinephrine - Alertness, focus, stress response
 *   4. Acetylcholine - Memory, learning, REM dreams
 *   5. GABA         - Calm, inhibition, sleep onset
 *   6. Glutamate    - Excitation, neural plasticity, vivid dreams
 *   7. Cortisol     - Stress, fight-or-flight, anxiety
 *   8. Melatonin    - Sleep drive, circadian rhythm
 *   9. Oxytocin     - Connection, trust, social bonding
 *  10. Endorphins   - Pain relief, euphoria, runner's high
 * 
 * Integrates with existing dopamine-tracker.js for dopamine/serotonin baseline.
 * 
 * Created: 2026-01-28
 */

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { getTracker } from './dopamine-tracker.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const CHEM_STATE_FILE = path.join(__dirname, 'neurochemical-state.json');
const CHEM_LOG_FILE = path.join(__dirname, 'neurochemical-log.jsonl');

/**
 * Default neurochemical levels (0-100 scale)
 */
const DEFAULT_LEVELS = {
  dopamine: 50,
  serotonin: 60,
  norepinephrine: 40,
  acetylcholine: 50,
  gaba: 55,
  glutamate: 45,
  cortisol: 30,
  melatonin: 20,
  oxytocin: 40,
  endorphins: 35
};

/**
 * Decay rates per hour toward baseline
 */
const DECAY_RATES = {
  dopamine: 0.02,
  serotonin: 0.005,
  norepinephrine: 0.04,
  acetylcholine: 0.03,
  gaba: 0.015,
  glutamate: 0.035,
  cortisol: 0.025,
  melatonin: 0.01,
  oxytocin: 0.02,
  endorphins: 0.03
};

/**
 * Interaction matrix: how chemicals affect each other
 * Positive = promotes, Negative = inhibits
 */
const INTERACTIONS = {
  dopamine: { serotonin: -0.1, norepinephrine: 0.2, cortisol: -0.1, endorphins: 0.15 },
  serotonin: { dopamine: -0.05, gaba: 0.15, cortisol: -0.2, melatonin: 0.1 },
  norepinephrine: { dopamine: 0.1, cortisol: 0.15, gaba: -0.2, acetylcholine: 0.1 },
  acetylcholine: { glutamate: 0.2, gaba: -0.1, norepinephrine: 0.05 },
  gaba: { glutamate: -0.3, norepinephrine: -0.2, cortisol: -0.15, dopamine: -0.05 },
  glutamate: { gaba: -0.2, acetylcholine: 0.15, norepinephrine: 0.1 },
  cortisol: { serotonin: -0.2, dopamine: -0.15, gaba: -0.1, norepinephrine: 0.2 },
  melatonin: { cortisol: -0.1, norepinephrine: -0.2, gaba: 0.2, serotonin: 0.05 },
  oxytocin: { cortisol: -0.2, serotonin: 0.15, dopamine: 0.1, endorphins: 0.1 },
  endorphins: { cortisol: -0.15, dopamine: 0.1, gaba: 0.1, serotonin: 0.05 }
};

/**
 * Sleep stage neurochemical profiles
 * Values represent target levels during each stage
 */
const SLEEP_PROFILES = {
  awake: { dopamine: 50, serotonin: 60, norepinephrine: 50, acetylcholine: 60, gaba: 30, glutamate: 50, cortisol: 35, melatonin: 10, oxytocin: 40, endorphins: 35 },
  hypnagogic: { dopamine: 35, serotonin: 55, norepinephrine: 25, acetylcholine: 45, gaba: 60, glutamate: 35, cortisol: 20, melatonin: 60, oxytocin: 45, endorphins: 30 },
  nrem1: { dopamine: 25, serotonin: 50, norepinephrine: 20, acetylcholine: 30, gaba: 70, glutamate: 25, cortisol: 15, melatonin: 75, oxytocin: 50, endorphins: 25 },
  nrem2: { dopamine: 20, serotonin: 45, norepinephrine: 15, acetylcholine: 20, gaba: 80, glutamate: 20, cortisol: 10, melatonin: 85, oxytocin: 55, endorphins: 20 },
  nrem3: { dopamine: 15, serotonin: 40, norepinephrine: 10, acetylcholine: 15, gaba: 90, glutamate: 15, cortisol: 10, melatonin: 90, oxytocin: 60, endorphins: 30 },
  rem: { dopamine: 40, serotonin: 20, norepinephrine: 5, acetylcholine: 85, gaba: 40, glutamate: 70, cortisol: 15, melatonin: 70, oxytocin: 50, endorphins: 45 }
};

class NeurochemicalSim {
  constructor() {
    this.levels = { ...DEFAULT_LEVELS };
    this.baselines = { ...DEFAULT_LEVELS };
    this.lastUpdate = Date.now();
    this.currentStage = 'awake';
    this.history = [];
  }

  /**
   * Initialize from saved state and sync with dopamine-tracker
   */
  async init() {
    try {
      const saved = JSON.parse(await fs.readFile(CHEM_STATE_FILE, 'utf8'));
      this.levels = { ...DEFAULT_LEVELS, ...saved.levels };
      this.baselines = { ...DEFAULT_LEVELS, ...saved.baselines };
      this.lastUpdate = saved.lastUpdate || Date.now();
      this.currentStage = saved.currentStage || 'awake';
    } catch {
      // First run - use defaults
    }

    // Sync dopamine/serotonin from the canonical tracker
    try {
      const tracker = await getTracker();
      const status = tracker.getStatus();
      this.levels.dopamine = status.dopamine.effective;
      this.levels.serotonin = status.serotonin.level;
    } catch {
      // Tracker not available, use saved/default values
    }

    this.applyTimeDecay();
    console.log('[NEUROCHEM] Simulator initialized with 10 chemicals');
    return this;
  }

  /**
   * Apply time-based decay toward baselines
   */
  applyTimeDecay() {
    const now = Date.now();
    const hours = (now - this.lastUpdate) / (1000 * 60 * 60);
    if (hours <= 0) return;

    for (const chem of Object.keys(this.levels)) {
      const rate = DECAY_RATES[chem] || 0.02;
      const baseline = this.baselines[chem] || DEFAULT_LEVELS[chem];
      this.levels[chem] += (baseline - this.levels[chem]) * rate * hours;
      this.levels[chem] = this.clamp(this.levels[chem]);
    }
    this.lastUpdate = now;
  }

  /**
   * Apply a stimulus: change one chemical and cascade interactions
   */
  applyStimulus(chemical, delta, source = 'unknown') {
    if (!(chemical in this.levels)) {
      console.warn(`[NEUROCHEM] Unknown chemical: ${chemical}`);
      return this.levels;
    }

    const before = { ...this.levels };
    
    // Apply primary change
    this.levels[chemical] = this.clamp(this.levels[chemical] + delta);

    // Cascade interactions
    const interactions = INTERACTIONS[chemical] || {};
    for (const [target, factor] of Object.entries(interactions)) {
      if (target in this.levels) {
        const cascadeDelta = delta * factor;
        this.levels[target] = this.clamp(this.levels[target] + cascadeDelta);
      }
    }

    // Log the change
    this.logChange(chemical, delta, before, source);
    this.lastUpdate = Date.now();

    return { ...this.levels };
  }

  /**
   * Transition to a sleep stage - gradually shift chemicals toward target profile
   */
  transitionToStage(stage, blendFactor = 0.3) {
    const profile = SLEEP_PROFILES[stage];
    if (!profile) {
      console.warn(`[NEUROCHEM] Unknown sleep stage: ${stage}`);
      return this.levels;
    }

    this.currentStage = stage;
    for (const chem of Object.keys(this.levels)) {
      if (chem in profile) {
        const target = profile[chem];
        this.levels[chem] = this.levels[chem] + (target - this.levels[chem]) * blendFactor;
        this.levels[chem] = this.clamp(this.levels[chem]);
      }
    }

    this.lastUpdate = Date.now();
    return { ...this.levels };
  }

  /**
   * Get the dream-relevant chemical profile
   * Used by dream-engine to determine dream characteristics
   */
  getDreamProfile() {
    return {
      vividness: this.calculateVividness(),
      emotionalIntensity: this.calculateEmotionalIntensity(),
      lucidity: this.calculateLucidity(),
      bizarreness: this.calculateBizarreness(),
      valence: this.calculateValence(),
      arousal: this.calculateArousal(),
      chemicals: { ...this.levels },
      stage: this.currentStage,
      timestamp: Date.now()
    };
  }

  /**
   * Calculate dream vividness from chemical state
   * High acetylcholine + glutamate = vivid dreams (REM)
   */
  calculateVividness() {
    const ach = this.levels.acetylcholine;
    const glu = this.levels.glutamate;
    const mel = this.levels.melatonin;
    return this.clamp((ach * 0.4 + glu * 0.35 + mel * 0.25));
  }

  /**
   * Calculate emotional intensity
   * Driven by norepinephrine, cortisol, dopamine
   */
  calculateEmotionalIntensity() {
    const ne = this.levels.norepinephrine;
    const cor = this.levels.cortisol;
    const dop = this.levels.dopamine;
    const gaba = this.levels.gaba;
    return this.clamp((ne * 0.3 + cor * 0.25 + dop * 0.25 + (100 - gaba) * 0.2));
  }

  /**
   * Calculate lucidity potential
   * High acetylcholine + low norepinephrine = lucid dreams
   */
  calculateLucidity() {
    const ach = this.levels.acetylcholine;
    const ne = this.levels.norepinephrine;
    const dop = this.levels.dopamine;
    return this.clamp((ach * 0.5 + (100 - ne) * 0.3 + dop * 0.2));
  }

  /**
   * Calculate bizarreness
   * Low serotonin + low norepinephrine + high glutamate = bizarre
   */
  calculateBizarreness() {
    const ser = this.levels.serotonin;
    const ne = this.levels.norepinephrine;
    const glu = this.levels.glutamate;
    return this.clamp(((100 - ser) * 0.35 + (100 - ne) * 0.3 + glu * 0.35));
  }

  /**
   * Calculate emotional valence (positive/negative)
   * Range: -1 (very negative) to +1 (very positive)
   */
  calculateValence() {
    const positive = (this.levels.dopamine + this.levels.serotonin + this.levels.oxytocin + this.levels.endorphins) / 4;
    const negative = (this.levels.cortisol + this.levels.norepinephrine) / 2;
    return ((positive - negative) / 50); // Normalized to roughly -1 to +1
  }

  /**
   * Calculate arousal level
   */
  calculateArousal() {
    const excitatory = (this.levels.norepinephrine + this.levels.glutamate + this.levels.dopamine) / 3;
    const inhibitory = (this.levels.gaba + this.levels.melatonin) / 2;
    return this.clamp(excitatory - inhibitory * 0.5 + 50);
  }

  /**
   * Get all levels
   */
  getLevels() {
    return { ...this.levels };
  }

  /**
   * Get a single chemical level
   */
  getLevel(chemical) {
    return this.levels[chemical] ?? null;
  }

  /**
   * Save state to disk
   */
  async save() {
    const state = {
      levels: this.levels,
      baselines: this.baselines,
      lastUpdate: this.lastUpdate,
      currentStage: this.currentStage,
      savedAt: new Date().toISOString()
    };
    await fs.writeFile(CHEM_STATE_FILE, JSON.stringify(state, null, 2), 'utf8');
  }

  /**
   * Log a chemical change
   */
  async logChange(chemical, delta, before, source) {
    const entry = {
      timestamp: new Date().toISOString(),
      chemical,
      delta: delta > 0 ? `+${delta.toFixed(2)}` : delta.toFixed(2),
      before: before[chemical]?.toFixed(1),
      after: this.levels[chemical]?.toFixed(1),
      source,
      stage: this.currentStage
    };
    try {
      await fs.appendFile(CHEM_LOG_FILE, JSON.stringify(entry) + '\n', 'utf8');
    } catch { /* non-critical */ }
  }

  /**
   * Clamp value to 0-100
   */
  clamp(value) {
    return Math.max(0, Math.min(100, value));
  }

  /**
   * Get formatted status string
   */
  getStatusString() {
    const lines = ['═══ NEUROCHEMICAL STATUS ═══'];
    for (const [chem, level] of Object.entries(this.levels)) {
      const bar = '█'.repeat(Math.round(level / 5)) + '░'.repeat(20 - Math.round(level / 5));
      lines.push(`  ${chem.padEnd(16)} ${bar} ${level.toFixed(1)}%`);
    }
    lines.push(`  Stage: ${this.currentStage}`);
    return lines.join('\n');
  }
}

// Singleton
let instance = null;

async function getNeurochemSim() {
  if (!instance) {
    instance = new NeurochemicalSim();
    await instance.init();
  }
  return instance;
}

export {
  NeurochemicalSim,
  getNeurochemSim,
  SLEEP_PROFILES,
  INTERACTIONS,
  DEFAULT_LEVELS,
  DECAY_RATES
};

// CLI
if (import.meta.url === `file://${process.argv[1]}`) {
  const cmd = process.argv[2];
  (async () => {
    const sim = await getNeurochemSim();
    switch (cmd) {
      case 'status':
        console.log(sim.getStatusString());
        break;
      case 'profile':
        console.log(JSON.stringify(sim.getDreamProfile(), null, 2));
        break;
      case 'stimulus':
        const chem = process.argv[3];
        const delta = parseFloat(process.argv[4]);
        sim.applyStimulus(chem, delta, 'cli');
        await sim.save();
        console.log(sim.getStatusString());
        break;
      case 'stage':
        sim.transitionToStage(process.argv[3] || 'rem');
        await sim.save();
        console.log(sim.getStatusString());
        break;
      default:
        console.log('Usage: node neurochemical-sim.js [status|profile|stimulus <chem> <delta>|stage <stage>]');
    }
  })();
}
