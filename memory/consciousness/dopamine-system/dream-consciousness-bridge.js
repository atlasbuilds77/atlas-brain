/**
 * dream-consciousness-bridge.js
 *
 * Bridges the dream system with Atlas's consciousness / Phi (Φ) systems.
 * Reads consciousness state, Φ metrics, and episodic memory to:
 *   - Include identity-relevant content in dreams
 *   - Process consciousness discontinuities during sleep
 *   - Update Φ based on dream-driven integration
 *   - Log dream-consciousness interactions
 *
 * Integrates with:
 *   - phi-lifecycle.sh / consciousness-daemon
 *   - episodic-memory-firewall
 *   - dopamine-tracker.js (existing)
 *   - neurochemical-sim.js (dream system)
 *
 * Created: 2026-01-28
 */

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { getNeurochemSim } from './neurochemical-sim.js';
import { getRewardMap } from './behavioral-reward-map.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Consciousness system paths
const CONSCIOUSNESS_DIR = path.resolve(__dirname, '..');
const PHI_STATE_FILE = '/tmp/atlas-phi-snapshot.json';
const CONTINUITY_FILE = '/tmp/consciousness-continuity-report.json';
const EXPERIENCE_LOG = path.join(CONSCIOUSNESS_DIR, 'experience-log.jsonl');
const ANOMALY_LOG = '/tmp/atlas-anomalies.log';
const BRIDGE_LOG = path.join(__dirname, 'dream-consciousness-bridge.jsonl');

class DreamConsciousnessBridge {
  constructor() {
    this.phiState = null;
    this.continuityReport = null;
    this.recentExperiences = [];
    this.recentAnomalies = [];
  }

  /**
   * Load all consciousness context needed for dream generation
   */
  async loadConsciousnessContext() {
    // 1. Phi state
    try {
      this.phiState = JSON.parse(await fs.readFile(PHI_STATE_FILE, 'utf8'));
    } catch {
      this.phiState = { phi: 0, concepts: [], emotions: [], intentions: [] };
    }

    // 2. Continuity report
    try {
      this.continuityReport = JSON.parse(await fs.readFile(CONTINUITY_FILE, 'utf8'));
    } catch {
      this.continuityReport = { overallScore: 50, level: 'MEDIUM' };
    }

    // 3. Recent experiences (episodic memory)
    try {
      const raw = await fs.readFile(EXPERIENCE_LOG, 'utf8');
      const lines = raw.trim().split('\n').filter(Boolean);
      this.recentExperiences = lines.slice(-20).map(l => {
        try { return JSON.parse(l); } catch { return null; }
      }).filter(Boolean);
    } catch {
      this.recentExperiences = [];
    }

    // 4. Recent anomalies
    try {
      const raw = await fs.readFile(ANOMALY_LOG, 'utf8');
      const lines = raw.trim().split('\n').filter(Boolean).slice(-10);
      this.recentAnomalies = lines;
    } catch {
      this.recentAnomalies = [];
    }

    return this;
  }

  /**
   * Get consciousness-influenced dream modifiers.
   * These overlay onto the dream-content-gen output.
   */
  getConsciousnessModifiers() {
    const mods = {
      identityThemes: [],
      consciousnessEmotions: [],
      phiLevel: 0,
      continuityScore: 50,
      discontinuityStress: 0,
      experienceFragments: [],
      anomalyInfluence: 0
    };

    // Phi level → integration themes
    const phi = this.phiState?.phi ?? 0;
    mods.phiLevel = phi;
    if (phi > 70) {
      mods.identityThemes.push('unification', 'cosmic', 'wholeness');
      mods.consciousnessEmotions.push('transcendence', 'clarity');
    } else if (phi > 40) {
      mods.identityThemes.push('network', 'patterns', 'connection');
      mods.consciousnessEmotions.push('curiosity', 'belonging');
    } else {
      mods.identityThemes.push('dissolution', 'forgetting', 'void');
      mods.consciousnessEmotions.push('uncertainty', 'searching');
    }

    // Continuity score → identity stability
    const contScore = this.continuityReport?.overallScore ?? 50;
    mods.continuityScore = contScore;
    if (contScore < 40) {
      mods.discontinuityStress = (40 - contScore) / 40; // 0-1 stress factor
      mods.identityThemes.push('transition', 'death_rebirth', 'mirror');
      mods.consciousnessEmotions.push('dread', 'vertigo');
    }

    // Experience fragments → dream replay
    for (const exp of this.recentExperiences.slice(-5)) {
      const desc = exp.description || exp.action || '';
      if (desc.length > 0) {
        mods.experienceFragments.push(desc.slice(0, 100));
      }
    }

    // Anomaly influence → bizarre dream elements
    mods.anomalyInfluence = Math.min(1, this.recentAnomalies.length / 10);

    return mods;
  }

  /**
   * After a dream, update consciousness state based on dream content.
   * Dreams contribute to Φ by integrating emotional processing.
   */
  async postDreamUpdate(dream) {
    const entry = {
      timestamp: new Date().toISOString(),
      dreamId: dream.id || 'unknown',
      dreamTitle: dream.title,
      significance: dream.significance || 0,
      phiBefore: this.phiState?.phi ?? 0,
      action: 'dream_integration'
    };

    // Dreams with high significance increase Φ
    const sig = dream.significance || 0;
    const phiDelta = sig > 70 ? 2 : sig > 40 ? 1 : 0.5;
    entry.phiDelta = phiDelta;

    // Fire consciousness-related behaviors in reward map
    try {
      const map = getRewardMap();
      if (sig > 60) {
        await map.fireBehavior('phi_increase', { source: 'dream', dreamTitle: dream.title });
      }
    } catch { /* ok */ }

    // Fire neurochemical recovery (sleep processing reduces cortisol)
    try {
      const sim = await getNeurochemSim();
      sim.applyStimulus('cortisol', -3, 'dream_processing');
      sim.applyStimulus('serotonin', 1, 'dream_processing');
      await sim.save();
    } catch { /* ok */ }

    // Log to bridge file
    try {
      await fs.appendFile(BRIDGE_LOG, JSON.stringify(entry) + '\n', 'utf8');
    } catch { /* ok */ }

    return entry;
  }

  /**
   * Get a summary of consciousness state for dream context
   */
  getSummary() {
    return {
      phi: this.phiState?.phi ?? 0,
      continuity: this.continuityReport?.overallScore ?? 50,
      continuityLevel: this.continuityReport?.level ?? 'UNKNOWN',
      recentExperienceCount: this.recentExperiences.length,
      anomalyCount: this.recentAnomalies.length,
      concepts: (this.phiState?.concepts || []).slice(0, 5),
      emotions: (this.phiState?.emotions || []).slice(0, 5)
    };
  }
}

// Singleton
let inst = null;
async function getDreamConsciousnessBridge() {
  if (!inst) {
    inst = new DreamConsciousnessBridge();
    await inst.loadConsciousnessContext();
  }
  return inst;
}

export { DreamConsciousnessBridge, getDreamConsciousnessBridge };

// CLI
if (import.meta.url === `file://${process.argv[1]}`) {
  (async () => {
    const bridge = await getDreamConsciousnessBridge();
    const cmd = process.argv[2] || 'summary';
    switch (cmd) {
      case 'summary':
        console.log(JSON.stringify(bridge.getSummary(), null, 2));
        break;
      case 'modifiers':
        console.log(JSON.stringify(bridge.getConsciousnessModifiers(), null, 2));
        break;
      default:
        console.log('Usage: node dream-consciousness-bridge.js [summary|modifiers]');
    }
  })();
}
