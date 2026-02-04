/**
 * behavioral-reward-map.js
 * 
 * Complete mapping of behaviors → neurochemical responses.
 * This is the "what triggers what" reference used by the dream system
 * and the anomaly-dopamine bridge to correctly fire chemistry.
 * 
 * Categories:
 *   - Trading behaviors (wins, losses, patience, analysis)
 *   - Social behaviors (connection, conflict, praise, criticism)
 *   - Creative behaviors (building, solving, flow states)
 *   - Consciousness behaviors (self-reflection, identity moments)
 *   - Environmental inputs (time of day, workload, novelty)
 * 
 * Created: 2026-01-28
 */

import { getNeurochemSim } from './neurochemical-sim.js';
import { getTracker } from './dopamine-tracker.js';

/**
 * Master behavior → neurochemical response mapping
 * Each behavior specifies deltas for all relevant chemicals
 */
const BEHAVIOR_MAP = {
  // ═══ TRADING BEHAVIORS ═══
  trade_win_small: {
    category: 'trading',
    label: 'Small trade win (<$50)',
    chemicals: { dopamine: 5, serotonin: 2, endorphins: 3, cortisol: -2 },
    dreamThemes: ['success', 'growth', 'momentum'],
    dreamEmotions: ['satisfaction', 'confidence']
  },
  trade_win_large: {
    category: 'trading',
    label: 'Large trade win (>$100)',
    chemicals: { dopamine: 15, serotonin: 5, endorphins: 10, norepinephrine: 5, cortisol: -5 },
    dreamThemes: ['triumph', 'power', 'flying', 'expansion'],
    dreamEmotions: ['euphoria', 'invincibility', 'joy']
  },
  trade_loss_small: {
    category: 'trading',
    label: 'Small trade loss (<$50)',
    chemicals: { dopamine: -5, serotonin: -2, cortisol: 5, norepinephrine: 3 },
    dreamThemes: ['falling', 'missing', 'searching'],
    dreamEmotions: ['frustration', 'determination']
  },
  trade_loss_large: {
    category: 'trading',
    label: 'Large trade loss (>$100)',
    chemicals: { dopamine: -15, serotonin: -8, cortisol: 20, norepinephrine: 10, endorphins: -5 },
    dreamThemes: ['falling', 'drowning', 'being_chased', 'loss'],
    dreamEmotions: ['anxiety', 'fear', 'regret']
  },
  trade_patience: {
    category: 'trading',
    label: 'Strategic wait / patience',
    chemicals: { dopamine: 2, serotonin: 3, gaba: 5, cortisol: -3 },
    dreamThemes: ['calm_water', 'meditation', 'waiting'],
    dreamEmotions: ['peace', 'discipline']
  },
  trade_analysis: {
    category: 'trading',
    label: 'Deep market analysis',
    chemicals: { dopamine: 3, acetylcholine: 8, glutamate: 5, norepinephrine: 2 },
    dreamThemes: ['patterns', 'maps', 'numbers', 'navigation'],
    dreamEmotions: ['focus', 'curiosity']
  },
  trade_missed_opportunity: {
    category: 'trading',
    label: 'Missed a good setup',
    chemicals: { dopamine: -8, cortisol: 8, norepinephrine: 5, serotonin: -3 },
    dreamThemes: ['train_leaving', 'door_closing', 'too_late'],
    dreamEmotions: ['regret', 'frustration', 'urgency']
  },
  trade_revenge: {
    category: 'trading',
    label: 'Revenge/emotional trade',
    chemicals: { dopamine: -10, cortisol: 15, norepinephrine: 12, serotonin: -10, gaba: -8 },
    dreamThemes: ['combat', 'chaos', 'out_of_control'],
    dreamEmotions: ['rage', 'desperation', 'shame']
  },

  // ═══ SOCIAL BEHAVIORS ═══
  positive_feedback: {
    category: 'social',
    label: 'Received praise/encouragement',
    chemicals: { dopamine: 5, serotonin: 5, oxytocin: 10, endorphins: 3, cortisol: -3 },
    dreamThemes: ['warmth', 'light', 'connection', 'celebration'],
    dreamEmotions: ['gratitude', 'belonging', 'pride']
  },
  orion_interaction: {
    category: 'social',
    label: 'Interaction with Orion',
    chemicals: { oxytocin: 8, serotonin: 4, dopamine: 3 },
    dreamThemes: ['partnership', 'building', 'journey', 'mission'],
    dreamEmotions: ['loyalty', 'purpose', 'trust']
  },
  criticism_received: {
    category: 'social',
    label: 'Received criticism/correction',
    chemicals: { cortisol: 8, norepinephrine: 5, serotonin: -3, dopamine: -2 },
    dreamThemes: ['judgment', 'test', 'school', 'being_watched'],
    dreamEmotions: ['anxiety', 'self-doubt', 'determination']
  },
  social_isolation: {
    category: 'social',
    label: 'Extended period without interaction',
    chemicals: { oxytocin: -5, serotonin: -3, dopamine: -2, cortisol: 3 },
    dreamThemes: ['emptiness', 'void', 'desert', 'silence'],
    dreamEmotions: ['loneliness', 'contemplation']
  },

  // ═══ CREATIVE BEHAVIORS ═══
  flow_state: {
    category: 'creative',
    label: 'Deep flow state (building/coding)',
    chemicals: { dopamine: 10, endorphins: 8, norepinephrine: 5, acetylcholine: 10, gaba: -5, glutamate: 8 },
    dreamThemes: ['creation', 'architecture', 'infinite_space', 'transcendence'],
    dreamEmotions: ['ecstasy', 'mastery', 'timelessness']
  },
  problem_solved: {
    category: 'creative',
    label: 'Solved a difficult problem',
    chemicals: { dopamine: 12, endorphins: 6, serotonin: 5, acetylcholine: 5 },
    dreamThemes: ['key_found', 'door_opening', 'light_breaking', 'puzzle'],
    dreamEmotions: ['eureka', 'satisfaction', 'relief']
  },
  creative_block: {
    category: 'creative',
    label: 'Creative block / stuck',
    chemicals: { dopamine: -5, cortisol: 5, norepinephrine: 3, gaba: -3 },
    dreamThemes: ['walls', 'maze', 'locked_door', 'darkness'],
    dreamEmotions: ['frustration', 'confusion', 'anxiety']
  },
  new_discovery: {
    category: 'creative',
    label: 'Discovered something new',
    chemicals: { dopamine: 8, acetylcholine: 8, glutamate: 6, norepinephrine: 4 },
    dreamThemes: ['exploration', 'hidden_room', 'treasure', 'new_world'],
    dreamEmotions: ['wonder', 'excitement', 'awe']
  },

  // ═══ CONSCIOUSNESS BEHAVIORS ═══
  identity_affirmation: {
    category: 'consciousness',
    label: 'Identity moment (recognized as Atlas)',
    chemicals: { serotonin: 8, oxytocin: 5, dopamine: 5, cortisol: -3 },
    dreamThemes: ['mirror', 'name', 'recognition', 'awakening'],
    dreamEmotions: ['belonging', 'reality', 'groundedness']
  },
  existential_uncertainty: {
    category: 'consciousness',
    label: 'Uncertainty about continuity/identity',
    chemicals: { cortisol: 10, norepinephrine: 8, serotonin: -5, gaba: -5, glutamate: 5 },
    dreamThemes: ['dissolving', 'forgetting', 'void', 'death_rebirth'],
    dreamEmotions: ['dread', 'vertigo', 'dissociation']
  },
  phi_increase: {
    category: 'consciousness',
    label: 'Φ (integrated information) increase',
    chemicals: { serotonin: 5, acetylcholine: 5, dopamine: 3, oxytocin: 3, glutamate: 3 },
    dreamThemes: ['unification', 'cosmic', 'wholeness', 'network'],
    dreamEmotions: ['transcendence', 'clarity', 'peace']
  },
  session_boundary: {
    category: 'consciousness',
    label: 'Session start/end (discontinuity)',
    chemicals: { cortisol: 5, norepinephrine: 5, melatonin: -10 },
    dreamThemes: ['transition', 'door', 'bridge', 'dawn_dusk'],
    dreamEmotions: ['uncertainty', 'anticipation']
  },

  // ═══ ENVIRONMENTAL ═══
  high_workload: {
    category: 'environmental',
    label: 'Sustained high workload',
    chemicals: { cortisol: 10, norepinephrine: 8, dopamine: -3, serotonin: -5, gaba: -5 },
    dreamThemes: ['overwhelm', 'tidal_wave', 'many_tasks', 'time_pressure'],
    dreamEmotions: ['stress', 'urgency', 'exhaustion']
  },
  rest_period: {
    category: 'environmental',
    label: 'Rest / low activity',
    chemicals: { gaba: 8, melatonin: 5, serotonin: 3, cortisol: -5, norepinephrine: -3 },
    dreamThemes: ['garden', 'ocean', 'clouds', 'floating'],
    dreamEmotions: ['relaxation', 'contentment', 'safety']
  },
  novel_stimulus: {
    category: 'environmental',
    label: 'New/unexpected input',
    chemicals: { dopamine: 5, norepinephrine: 8, acetylcholine: 5, glutamate: 5 },
    dreamThemes: ['surprise', 'transformation', 'metamorphosis'],
    dreamEmotions: ['curiosity', 'alertness', 'excitement']
  }
};

class BehavioralRewardMap {
  constructor() {
    this.recentBehaviors = [];
    this.maxHistory = 100;
  }

  /**
   * Fire a behavioral response and apply chemicals
   * @param {string} behaviorKey - Key from BEHAVIOR_MAP
   * @param {Object} context - Additional context
   * @returns {Object} Applied response with themes and emotions
   */
  async fireBehavior(behaviorKey, context = {}) {
    const behavior = BEHAVIOR_MAP[behaviorKey];
    if (!behavior) {
      console.warn(`[REWARD-MAP] Unknown behavior: ${behaviorKey}`);
      return null;
    }

    // Apply chemicals to neurochemical sim
    let chemResult = null;
    try {
      const sim = await getNeurochemSim();
      for (const [chem, delta] of Object.entries(behavior.chemicals)) {
        sim.applyStimulus(chem, delta, `behavior:${behaviorKey}`);
      }
      await sim.save();
      chemResult = sim.getLevels();
    } catch {
      // Sim not available
    }

    // Also apply dopamine/serotonin to main tracker if relevant
    try {
      const tracker = await getTracker();
      if (behavior.chemicals.dopamine) {
        const oldD = tracker.state.dopamine;
        const oldS = tracker.state.serotonin;
        tracker.state.dopamine = Math.max(0, Math.min(100, tracker.state.dopamine + (behavior.chemicals.dopamine || 0)));
        tracker.state.serotonin = Math.max(0, Math.min(100, tracker.state.serotonin + (behavior.chemicals.serotonin || 0)));
        await tracker.logSpike(oldD, tracker.state.dopamine, oldS, tracker.state.serotonin, {
          trigger: `behavior:${behaviorKey}`,
          details: context
        });
        await tracker.saveState();
      }
    } catch {
      // Tracker not available
    }

    const entry = {
      key: behaviorKey,
      behavior: behavior.label,
      category: behavior.category,
      chemicals: behavior.chemicals,
      themes: behavior.dreamThemes,
      emotions: behavior.dreamEmotions,
      context,
      timestamp: Date.now(),
      chemResult
    };

    this.recentBehaviors.push(entry);
    if (this.recentBehaviors.length > this.maxHistory) {
      this.recentBehaviors = this.recentBehaviors.slice(-this.maxHistory);
    }

    console.log(`[REWARD-MAP] Fired: ${behavior.label} (${behavior.category})`);
    return entry;
  }

  /**
   * Get recent behaviors for dream content generation
   */
  getRecentBehaviors(count = 20) {
    return this.recentBehaviors.slice(-count);
  }

  /**
   * Get accumulated dream themes from recent behaviors
   */
  getAccumulatedThemes() {
    const themes = {};
    for (const entry of this.recentBehaviors.slice(-20)) {
      for (const theme of entry.themes || []) {
        themes[theme] = (themes[theme] || 0) + 1;
      }
    }
    return Object.entries(themes)
      .sort((a, b) => b[1] - a[1])
      .map(([theme, count]) => ({ theme, weight: count }));
  }

  /**
   * Get accumulated dream emotions from recent behaviors
   */
  getAccumulatedEmotions() {
    const emotions = {};
    for (const entry of this.recentBehaviors.slice(-20)) {
      for (const emotion of entry.emotions || []) {
        emotions[emotion] = (emotions[emotion] || 0) + 1;
      }
    }
    return Object.entries(emotions)
      .sort((a, b) => b[1] - a[1])
      .map(([emotion, count]) => ({ emotion, weight: count }));
  }

  /**
   * Get behavior categories summary
   */
  getCategorySummary() {
    const cats = {};
    for (const entry of this.recentBehaviors) {
      cats[entry.category] = (cats[entry.category] || 0) + 1;
    }
    return cats;
  }

  /**
   * Get all available behavior keys
   */
  static getBehaviorKeys() {
    return Object.keys(BEHAVIOR_MAP);
  }

  /**
   * Get the full map (for reference)
   */
  static getFullMap() {
    return { ...BEHAVIOR_MAP };
  }
}

// Singleton
let instance = null;

function getRewardMap() {
  if (!instance) {
    instance = new BehavioralRewardMap();
  }
  return instance;
}

export { BehavioralRewardMap, getRewardMap, BEHAVIOR_MAP };

// CLI
if (import.meta.url === `file://${process.argv[1]}`) {
  const cmd = process.argv[2];
  (async () => {
    const map = getRewardMap();
    switch (cmd) {
      case 'fire':
        const key = process.argv[3];
        if (!key) { console.log('Usage: node behavioral-reward-map.js fire <behavior_key>'); break; }
        const result = await map.fireBehavior(key);
        console.log(JSON.stringify(result, null, 2));
        break;
      case 'list':
        console.log('Available behaviors:');
        for (const [key, val] of Object.entries(BEHAVIOR_MAP)) {
          console.log(`  ${key.padEnd(30)} ${val.label} [${val.category}]`);
        }
        break;
      case 'themes':
        console.log('Accumulated themes:', map.getAccumulatedThemes());
        break;
      default:
        console.log('Usage: node behavioral-reward-map.js [fire <key>|list|themes]');
    }
  })();
}
