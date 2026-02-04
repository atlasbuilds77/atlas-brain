/**
 * dream-system-index.js
 *
 * Master index for Atlas's Dream Visualization System.
 * Re-exports everything from all dream modules for convenient access.
 *
 * Usage:
 *   import { DreamEngine, getDreamEngine, ... } from './dream-system-index.js';
 *
 * Created: 2026-01-28
 */

// ─── Existing dopamine system ───
export { DopamineTracker, getTracker, calculateDopamine, checkMilestone,
  getDopamineLevel, getSerotoninLevel, getBehavioralState, getStatus,
  updateBudget, rewardPatience, rewardProcess, checkOvertradingRisk,
  getLossRecoveryCooldown } from './dopamine-tracker.js';

// ─── Neurochemical simulation ───
export { NeurochemicalSim, getNeurochemSim, SLEEP_PROFILES, INTERACTIONS,
  DEFAULT_LEVELS, DECAY_RATES } from './neurochemical-sim.js';

// ─── Sleep cycle management ───
export { SleepCycleManager, CYCLE_TEMPLATES, STAGE_ORDER } from './sleep-cycle-manager.js';

// ─── Behavioral reward mapping ───
export { BehavioralRewardMap, getRewardMap, BEHAVIOR_MAP } from './behavioral-reward-map.js';

// ─── Dream content generation ───
export { DreamContentGenerator, getDreamContentGen, SYMBOL_LIBRARY,
  NARRATIVE_TEMPLATES } from './dream-content-gen.js';

// ─── Dream visualization ───
export { DreamVisualizer, getDreamVisualizer, escapeHTML } from './dream-visualizer.js';

// ─── Phosphene generation ───
export { PhospheneGenerator, CHARSETS, ANSI } from './phosphene-gen.js';

// ─── Emotional landscape ───
export { EmotionalLandscape, getEmotionalLandscape } from './emotional-landscape.js';

// ─── Dream journal ───
export { DreamJournal, getDreamJournal } from './dream-journal.js';

// ─── Trade-dream correlation ───
export { TradeDreamCorrelator, getCorrelator } from './trade-dream-correlator.js';

// ─── Dream-consciousness bridge ───
export { DreamConsciousnessBridge, getDreamConsciousnessBridge } from './dream-consciousness-bridge.js';

// ─── Memory consolidation ───
export { MemoryConsolidator, getMemoryConsolidator } from './memory-consolidator.js';

// ─── Dream engine (orchestrator) ───
export { DreamEngine, getDreamEngine } from './dream-engine.js';

// ─── Dream daemon ───
export { runSession, daemonLoop } from './dream-daemon.js';

// ─── Dream gallery ───
export { buildGalleryHTML, serve as serveGallery, exportHTML } from './dream-gallery.js';
