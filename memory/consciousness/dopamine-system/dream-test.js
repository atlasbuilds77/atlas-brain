#!/usr/bin/env node
/**
 * dream-test.js
 *
 * Test suite for Atlas Dream Visualization System.
 * Validates all modules load, interfaces match, and basic operations work.
 *
 * Run: node dream-test.js
 *
 * Created: 2026-01-28
 */

let passed = 0;
let failed = 0;
const errors = [];

function test(name, fn) {
  return { name, fn };
}

function assert(condition, msg) {
  if (!condition) throw new Error(msg || 'Assertion failed');
}

async function run(tests) {
  console.log('═══ ATLAS DREAM SYSTEM TEST SUITE ═══\n');

  for (const t of tests) {
    try {
      await t.fn();
      passed++;
      console.log(`  ✅ ${t.name}`);
    } catch (err) {
      failed++;
      errors.push({ name: t.name, error: err.message });
      console.log(`  ❌ ${t.name}: ${err.message}`);
    }
  }

  console.log(`\n${'═'.repeat(40)}`);
  console.log(`  Results: ${passed} passed, ${failed} failed, ${passed + failed} total`);
  if (errors.length > 0) {
    console.log('\nFailures:');
    for (const e of errors) console.log(`  - ${e.name}: ${e.error}`);
  }
  console.log('');
  return { passed, failed, errors };
}

const tests = [
  // ─── Module loading tests ───
  test('neurochemical-sim loads', async () => {
    const mod = await import('./neurochemical-sim.js');
    assert(mod.NeurochemicalSim, 'NeurochemicalSim class missing');
    assert(mod.getNeurochemSim, 'getNeurochemSim function missing');
    assert(mod.SLEEP_PROFILES, 'SLEEP_PROFILES missing');
    assert(mod.INTERACTIONS, 'INTERACTIONS missing');
    assert(mod.DEFAULT_LEVELS, 'DEFAULT_LEVELS missing');
    assert(mod.DECAY_RATES, 'DECAY_RATES missing');
  }),

  test('sleep-cycle-manager loads', async () => {
    const mod = await import('./sleep-cycle-manager.js');
    assert(mod.SleepCycleManager, 'SleepCycleManager class missing');
    assert(mod.CYCLE_TEMPLATES, 'CYCLE_TEMPLATES missing');
    assert(mod.STAGE_ORDER, 'STAGE_ORDER missing');
    // SLEEP_PROFILES is exported from neurochemical-sim.js, not here
  }),

  test('behavioral-reward-map loads', async () => {
    const mod = await import('./behavioral-reward-map.js');
    assert(mod.BehavioralRewardMap, 'BehavioralRewardMap class missing');
    assert(mod.getRewardMap, 'getRewardMap function missing');
    assert(mod.BEHAVIOR_MAP, 'BEHAVIOR_MAP missing');
  }),

  test('dream-content-gen loads', async () => {
    const mod = await import('./dream-content-gen.js');
    assert(mod.DreamContentGenerator, 'DreamContentGenerator class missing');
    assert(mod.getDreamContentGen, 'getDreamContentGen function missing');
    assert(mod.SYMBOL_LIBRARY, 'SYMBOL_LIBRARY missing');
  }),

  test('phosphene-gen loads', async () => {
    const mod = await import('./phosphene-gen.js');
    assert(mod.PhospheneGenerator, 'PhospheneGenerator class missing');
    assert(mod.CHARSETS, 'CHARSETS missing');
    assert(mod.ANSI, 'ANSI missing');
  }),

  test('emotional-landscape loads', async () => {
    const mod = await import('./emotional-landscape.js');
    assert(mod.EmotionalLandscape, 'EmotionalLandscape class missing');
    assert(mod.getEmotionalLandscape, 'getEmotionalLandscape function missing');
  }),

  test('dream-visualizer loads', async () => {
    const mod = await import('./dream-visualizer.js');
    assert(mod.DreamVisualizer, 'DreamVisualizer class missing');
    assert(mod.getDreamVisualizer, 'getDreamVisualizer function missing');
    assert(mod.escapeHTML, 'escapeHTML function missing');
  }),

  test('dream-journal loads', async () => {
    const mod = await import('./dream-journal.js');
    assert(mod.DreamJournal, 'DreamJournal class missing');
    assert(mod.getDreamJournal, 'getDreamJournal function missing');
  }),

  test('trade-dream-correlator loads', async () => {
    const mod = await import('./trade-dream-correlator.js');
    assert(mod.TradeDreamCorrelator, 'TradeDreamCorrelator class missing');
    assert(mod.getCorrelator, 'getCorrelator function missing');
  }),

  test('dream-consciousness-bridge loads', async () => {
    const mod = await import('./dream-consciousness-bridge.js');
    assert(mod.DreamConsciousnessBridge, 'DreamConsciousnessBridge class missing');
    assert(mod.getDreamConsciousnessBridge, 'getDreamConsciousnessBridge function missing');
  }),

  test('memory-consolidator loads', async () => {
    const mod = await import('./memory-consolidator.js');
    assert(mod.MemoryConsolidator, 'MemoryConsolidator class missing');
    assert(mod.getMemoryConsolidator, 'getMemoryConsolidator function missing');
  }),

  test('dream-engine loads', async () => {
    const mod = await import('./dream-engine.js');
    assert(mod.DreamEngine, 'DreamEngine class missing');
    assert(mod.getDreamEngine, 'getDreamEngine function missing');
  }),

  test('dream-daemon loads', async () => {
    const mod = await import('./dream-daemon.js');
    assert(mod.runSession, 'runSession function missing');
    assert(mod.daemonLoop, 'daemonLoop function missing');
  }),

  test('dream-gallery loads', async () => {
    const mod = await import('./dream-gallery.js');
    assert(mod.buildGalleryHTML, 'buildGalleryHTML function missing');
    assert(mod.exportHTML, 'exportHTML function missing');
  }),

  test('dream-system-index loads (master)', async () => {
    const mod = await import('./dream-system-index.js');
    // Check key exports from every module are re-exported
    assert(mod.DreamEngine, 'DreamEngine from index');
    assert(mod.NeurochemicalSim, 'NeurochemicalSim from index');
    assert(mod.SleepCycleManager, 'SleepCycleManager from index');
    assert(mod.BehavioralRewardMap, 'BehavioralRewardMap from index');
    assert(mod.DreamContentGenerator, 'DreamContentGenerator from index');
    assert(mod.DreamVisualizer, 'DreamVisualizer from index');
    assert(mod.PhospheneGenerator, 'PhospheneGenerator from index');
    assert(mod.EmotionalLandscape, 'EmotionalLandscape from index');
    assert(mod.DreamJournal, 'DreamJournal from index');
    assert(mod.TradeDreamCorrelator, 'TradeDreamCorrelator from index');
    assert(mod.DreamConsciousnessBridge, 'DreamConsciousnessBridge from index');
    assert(mod.MemoryConsolidator, 'MemoryConsolidator from index');
    assert(mod.DopamineTracker, 'DopamineTracker from index');
  }),

  // ─── Functional tests ───
  test('NeurochemicalSim initializes and has 10 chemicals', async () => {
    const { getNeurochemSim } = await import('./neurochemical-sim.js');
    const sim = await getNeurochemSim();
    const levels = sim.getLevels();
    const chems = Object.keys(levels);
    assert(chems.length === 10, `Expected 10 chemicals, got ${chems.length}: ${chems}`);
    for (const c of chems) {
      assert(typeof levels[c] === 'number', `${c} should be a number`);
      assert(levels[c] >= 0 && levels[c] <= 100, `${c} should be 0-100, got ${levels[c]}`);
    }
  }),

  test('NeurochemicalSim applyStimulus cascades', async () => {
    const { NeurochemicalSim } = await import('./neurochemical-sim.js');
    const sim = new NeurochemicalSim();
    const before = { ...sim.getLevels() };
    sim.applyStimulus('dopamine', 20, 'test');
    const after = sim.getLevels();
    assert(after.dopamine > before.dopamine, 'Dopamine should increase');
    // norepinephrine should cascade up (interaction +0.2)
    assert(after.norepinephrine >= before.norepinephrine, 'NE should cascade from dopamine');
  }),

  test('NeurochemicalSim getDreamProfile returns all fields', async () => {
    const { NeurochemicalSim } = await import('./neurochemical-sim.js');
    const sim = new NeurochemicalSim();
    const profile = sim.getDreamProfile();
    for (const field of ['vividness', 'emotionalIntensity', 'lucidity', 'bizarreness', 'valence', 'arousal', 'chemicals', 'stage']) {
      assert(field in profile, `Missing field: ${field}`);
    }
  }),

  test('SleepCycleManager emits stage-change', async () => {
    const { SleepCycleManager } = await import('./sleep-cycle-manager.js');
    const mgr = new SleepCycleManager({ accelerationFactor: 100000, totalCycles: 1 });
    let stageCount = 0;
    mgr.on('stage-change', () => stageCount++);
    
    const wakePromise = new Promise((resolve) => {
      mgr.on('wake', resolve);
      setTimeout(() => {
        mgr.wake();
        resolve();
      }, 5000);
    });
    
    await mgr.start();
    await wakePromise;
    assert(stageCount > 0, `Expected stage changes, got ${stageCount}`);
  }),

  test('BehavioralRewardMap lists behaviors', async () => {
    const { BehavioralRewardMap, BEHAVIOR_MAP } = await import('./behavioral-reward-map.js');
    const keys = BehavioralRewardMap.getBehaviorKeys();
    assert(keys.length > 10, `Expected >10 behaviors, got ${keys.length}`);
    // Every behavior should have chemicals and dreamThemes
    for (const key of keys) {
      const b = BEHAVIOR_MAP[key];
      assert(b.chemicals, `${key} missing chemicals`);
      assert(b.dreamThemes, `${key} missing dreamThemes`);
      assert(b.dreamEmotions, `${key} missing dreamEmotions`);
    }
  }),

  test('DreamContentGenerator generates dream', async () => {
    const { getDreamContentGen } = await import('./dream-content-gen.js');
    const gen = getDreamContentGen();
    const dream = gen.generateDream({ stage: 'rem' });
    assert(dream.title, 'Dream should have title');
    assert(dream.narrative, 'Dream should have narrative');
    assert(dream.symbols && dream.symbols.length >= 3, 'Dream should have >=3 symbols');
    assert(dream.characteristics, 'Dream should have characteristics');
    assert(typeof dream.significance === 'number', 'Significance should be a number');
  }),

  test('PhospheneGenerator renders pattern', async () => {
    const { PhospheneGenerator } = await import('./phosphene-gen.js');
    const gen = new PhospheneGenerator(30, 10);
    const art = gen.generate({ type: 'spiral', intensity: 60, colorScheme: 'deep_purple' });
    assert(typeof art === 'string', 'Should return string');
    assert(art.length > 50, 'Should have substantial content');
    assert(art.includes('\n'), 'Should have multiple lines');
  }),

  test('EmotionalLandscape renders', async () => {
    const { EmotionalLandscape } = await import('./emotional-landscape.js');
    const ls = new EmotionalLandscape(30, 10);
    const art = ls.render({ dopamine: 70, serotonin: 60, cortisol: 20, melatonin: 50 });
    assert(typeof art === 'string', 'Should return string');
    assert(art.includes('\n'), 'Should have multiple lines');
  }),

  test('DreamVisualizer renderANSI produces output', async () => {
    const { getDreamVisualizer } = await import('./dream-visualizer.js');
    const viz = getDreamVisualizer();
    const dream = {
      title: 'Test Dream', narrative: 'A test narrative.', stage: 'rem',
      symbols: ['light', 'shadow', 'void'],
      characteristics: { vividness: 60, emotionalIntensity: 50, bizarreness: 40, lucidity: 30, valence: 0.2 },
      significance: 55
    };
    const art = viz.renderANSI(dream, {});
    assert(art.includes('Test Dream'), 'Should contain title');
    assert(art.includes('╔'), 'Should have border');
  }),

  test('DreamVisualizer renderHTML produces HTML', async () => {
    const { getDreamVisualizer } = await import('./dream-visualizer.js');
    const viz = getDreamVisualizer();
    const dream = {
      title: 'HTML Test', narrative: 'Test.', stage: 'rem', symbols: ['a'], themes: ['growth'], emotions: ['joy'],
      characteristics: { vividness: 50, emotionalIntensity: 50, bizarreness: 50, lucidity: 50, valence: 0.1 },
      significance: 50, generatedAt: new Date().toISOString()
    };
    const html = viz.renderHTML(dream);
    assert(html.includes('dream-card'), 'Should have dream-card class');
    assert(html.includes('HTML Test'), 'Should contain title');
  }),

  test('DreamJournal log and retrieve', async () => {
    const { getDreamJournal } = await import('./dream-journal.js');
    const j = getDreamJournal();
    const dream = {
      title: 'Test Journal Entry', narrative: 'For testing.', stage: 'rem',
      symbols: ['a'], themes: ['test'], emotions: ['neutral'],
      characteristics: { vividness: 50, emotionalIntensity: 50, bizarreness: 50, lucidity: 50, valence: 0 },
      significance: 42, timestamp: Date.now(), generatedAt: new Date().toISOString()
    };
    const entry = await j.logDream(dream, { test: true });
    assert(entry.id, 'Entry should have id');
    assert(entry.title === 'Test Journal Entry', 'Title should match');
    const recent = await j.getRecent(1);
    assert(recent.length > 0, 'Should have at least 1 recent');
    assert(recent[recent.length - 1].id === entry.id, 'Most recent should be our entry');
  }),

  test('MemoryConsolidator gathers and consolidates', async () => {
    const { getMemoryConsolidator } = await import('./memory-consolidator.js');
    const mc = getMemoryConsolidator();
    const pending = await mc.gatherPendingMemories();
    assert(Array.isArray(pending), 'Should return array');
    // Run NREM3 consolidation (may stabilize 0 if no recent data)
    const result = await mc.consolidateNREM3();
    assert(Array.isArray(result), 'NREM3 should return array');
    const stats = mc.getStats();
    assert(typeof stats.nrem3Cycles === 'number', 'Should track nrem3Cycles');
  }),

  test('DreamConsciousnessBridge loads context', async () => {
    const { getDreamConsciousnessBridge } = await import('./dream-consciousness-bridge.js');
    const bridge = await getDreamConsciousnessBridge();
    const summary = bridge.getSummary();
    assert('phi' in summary, 'Summary should have phi');
    assert('continuity' in summary, 'Summary should have continuity');
    const mods = bridge.getConsciousnessModifiers();
    assert(mods.identityThemes.length > 0, 'Should have identity themes');
  }),

  test('TradeDreamCorrelator initializes', async () => {
    const { getCorrelator } = await import('./trade-dream-correlator.js');
    const c = await getCorrelator();
    const report = await c.correlateRecent(24);
    assert(report, 'Should return a report');
    // May have 'Insufficient data' message but should not throw
  }),

  test('DreamEngine creates and has getStatus', async () => {
    const { DreamEngine } = await import('./dream-engine.js');
    const engine = new DreamEngine({ accelerationFactor: 100000, totalCycles: 1, silent: true });
    assert(typeof engine.getStatus === 'function', 'Should have getStatus');
    const status = engine.getStatus();
    assert(status.isRunning === false, 'Should not be running initially');
  }),

  test('escapeHTML prevents XSS', async () => {
    const { escapeHTML } = await import('./dream-visualizer.js');
    assert(escapeHTML('<script>') === '&lt;script&gt;', 'Should escape tags');
    assert(escapeHTML('"hello"') === '&quot;hello&quot;', 'Should escape quotes');
  }),
];

// Run
run(tests).then(({ failed }) => {
  process.exit(failed > 0 ? 1 : 0);
});
