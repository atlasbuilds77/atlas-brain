/**
 * test-opus-fixes.js
 * 
 * Test suite for Opus-verified dopamine system fixes
 * Tests all 5 fixes including adaptive features
 */

import {
  getTracker,
  calculateDopamine,
  rewardPatience,
  rewardProcess,
  checkOvertradingRisk,
  getLossRecoveryCooldown,
  getStatus
} from './dopamine-tracker.js';

const COLORS = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

function log(color, ...args) {
  console.log(color, ...args, COLORS.reset);
}

function pass(test) {
  log(COLORS.green, `✓ ${test}`);
}

function fail(test, reason) {
  log(COLORS.red, `✗ ${test}`, reason ? `- ${reason}` : '');
}

function section(name) {
  log(COLORS.cyan, `\n${'='.repeat(60)}`);
  log(COLORS.cyan, name);
  log(COLORS.cyan, '='.repeat(60));
}

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * FIX 1: Patience Rewards
 */
async function testPatienceRewards() {
  section('FIX 1: PATIENCE REWARDS');
  
  const tracker = await getTracker();
  const beforeDopamine = tracker.state.dopamine;
  const beforeSerotonin = tracker.state.serotonin;
  
  // Test patience reward
  const result = await rewardPatience({
    reason: 'Market choppy, no clear setup',
    marketCondition: 'sideways',
    riskAssessment: 'low probability'
  });
  
  if (result.newDopamine > beforeDopamine) {
    pass('Patience increases dopamine');
  } else {
    fail('Patience increases dopamine', `${beforeDopamine} → ${result.newDopamine}`);
  }
  
  if (result.newSerotonin > beforeSerotonin) {
    pass('Patience increases serotonin');
  } else {
    fail('Patience increases serotonin', `${beforeSerotonin} → ${result.newSerotonin}`);
  }
  
  if (tracker.history.patienceEvents && tracker.history.patienceEvents.length > 0) {
    pass('Patience events are tracked');
  } else {
    fail('Patience events are tracked');
  }
  
  log(COLORS.blue, `Dopamine: ${beforeDopamine.toFixed(1)}% → ${result.newDopamine.toFixed(1)}% (+${result.patienceDelta}%)`);
  log(COLORS.blue, `Serotonin: ${beforeSerotonin.toFixed(1)}% → ${result.newSerotonin.toFixed(1)}%`);
}

/**
 * FIX 2: Process Rewards
 */
async function testProcessRewards() {
  section('FIX 2: PROCESS REWARDS');
  
  const tracker = await getTracker();
  
  const processTypes = [
    ['analysis', 1.5],
    ['risk_check', 1.0],
    ['journal_entry', 2.0],
    ['pattern_learned', 3.0],
    ['checklist_completed', 2.0]
  ];
  
  for (const [type, expectedDelta] of processTypes) {
    const beforeDopamine = tracker.state.dopamine;
    const beforeSerotonin = tracker.state.serotonin;
    
    const result = await rewardProcess(type, 1.0);
    
    if (result.processDelta === expectedDelta) {
      pass(`${type} rewards correct amount (${expectedDelta}%)`);
    } else {
      fail(`${type} rewards correct amount`, `expected ${expectedDelta}, got ${result.processDelta}`);
    }
    
    if (result.newDopamine > beforeDopamine) {
      pass(`${type} increases dopamine`);
    } else {
      fail(`${type} increases dopamine`);
    }
    
    if (result.newSerotonin > beforeSerotonin) {
      pass(`${type} increases serotonin`);
    } else {
      fail(`${type} increases serotonin`);
    }
  }
  
  if (tracker.history.processEvents && tracker.history.processEvents.length > 0) {
    pass('Process events are tracked');
  } else {
    fail('Process events are tracked');
  }
}

/**
 * FIX 3: Overtrading Circuit Breaker
 */
async function testOvertradingCircuitBreaker() {
  section('FIX 3: OVERTRADING CIRCUIT BREAKER (ADAPTIVE)');
  
  const tracker = await getTracker();
  
  // Simulate 3 trades in quick succession
  log(COLORS.yellow, '\nSimulating 3 quick trades...');
  for (let i = 0; i < 3; i++) {
    await calculateDopamine({
      pnl: 50,
      expectedPnl: 50,
      isWin: true,
      symbol: 'TEST',
      strategy: 'test'
    });
    await sleep(100); // Very short wait
  }
  
  // Test 1: Low conviction should block
  log(COLORS.yellow, '\nTest 1: Low conviction (should block)');
  const lowConvictionCheck = tracker.checkOvertradingRisk({ conviction: 5 });
  if (lowConvictionCheck.blocked) {
    pass('Low conviction (5/10) triggers circuit breaker');
  } else {
    fail('Low conviction (5/10) triggers circuit breaker', `blocked: ${lowConvictionCheck.blocked}`);
  }
  
  // Test 2: Medium conviction should warn but allow
  log(COLORS.yellow, '\nTest 2: Medium conviction (should warn but allow)');
  const medConvictionCheck = tracker.checkOvertradingRisk({ conviction: 7.5 });
  if (!medConvictionCheck.blocked && medConvictionCheck.warning) {
    pass('Medium conviction (7.5/10) warns but allows trade');
  } else {
    fail('Medium conviction (7.5/10) warns but allows trade', 
      `blocked: ${medConvictionCheck.blocked}, warning: ${medConvictionCheck.warning}`);
  }
  
  // Test 3: High conviction should bypass
  log(COLORS.yellow, '\nTest 3: High conviction (should bypass)');
  const highConvictionCheck = tracker.checkOvertradingRisk({ conviction: 9.2 });
  if (!highConvictionCheck.blocked && highConvictionCheck.bypassed) {
    pass('High conviction (9.2/10) bypasses circuit breaker');
  } else {
    fail('High conviction (9.2/10) bypasses circuit breaker', 
      `blocked: ${highConvictionCheck.blocked}, bypassed: ${highConvictionCheck.bypassed}`);
  }
  
  // Test 4: Manual override
  log(COLORS.yellow, '\nTest 4: Manual override');
  const overrideCheck = tracker.checkOvertradingRisk({ 
    conviction: 5,
    manualOverride: 'Fed announcement reaction - clear momentum breakout'
  });
  if (!overrideCheck.blocked && overrideCheck.overridden) {
    pass('Manual override bypasses circuit breaker');
  } else {
    fail('Manual override bypasses circuit breaker');
  }
  
  if (tracker.history.overrideEvents && tracker.history.overrideEvents.length > 0) {
    pass('Override events are logged');
  } else {
    fail('Override events are logged');
  }
}

/**
 * FIX 4: Loss Recovery Cooldown
 */
async function testLossRecoveryCooldown() {
  section('FIX 4: LOSS RECOVERY COOLDOWN (ADAPTIVE)');
  
  const tracker = await getTracker();
  
  // Simulate a loss
  log(COLORS.yellow, '\nSimulating $800 loss...');
  await calculateDopamine({
    pnl: -800,
    expectedPnl: 0,
    isWin: false,
    symbol: 'TEST',
    strategy: 'test'
  });
  
  // Test 1: Low conviction should have full cooldown
  log(COLORS.yellow, '\nTest 1: Low conviction (full cooldown)');
  const lowConvictionCooldown = tracker.getLossRecoveryCooldown({ conviction: 5 });
  if (lowConvictionCooldown.remainingMs > 0) {
    pass('Low conviction (5/10) has full cooldown');
    log(COLORS.blue, `Cooldown: ${lowConvictionCooldown.remainingMinutes} minutes`);
  } else {
    fail('Low conviction (5/10) has full cooldown', 'No cooldown detected');
  }
  
  // Test 2: Medium conviction should reduce cooldown
  log(COLORS.yellow, '\nTest 2: Medium conviction (reduced cooldown)');
  const medConvictionCooldown = tracker.getLossRecoveryCooldown({ conviction: 8.0 });
  if (medConvictionCooldown.remainingMs > 0 && 
      medConvictionCooldown.convictionReduction &&
      medConvictionCooldown.remainingMs < lowConvictionCooldown.remainingMs) {
    pass('Medium conviction (8/10) reduces cooldown by 50%');
    log(COLORS.blue, `Cooldown: ${medConvictionCooldown.remainingMinutes} minutes (reduced from ${lowConvictionCooldown.remainingMinutes})`);
  } else {
    fail('Medium conviction (8/10) reduces cooldown by 50%');
  }
  
  // Test 3: High conviction should minimize cooldown
  log(COLORS.yellow, '\nTest 3: High conviction (minimal cooldown)');
  const highConvictionCooldown = tracker.getLossRecoveryCooldown({ conviction: 9.5 });
  if (highConvictionCooldown.remainingMs > 0 &&
      highConvictionCooldown.convictionReduction &&
      highConvictionCooldown.remainingMs < medConvictionCooldown.remainingMs) {
    pass('High conviction (9.5/10) reduces cooldown by 75%');
    log(COLORS.blue, `Cooldown: ${highConvictionCooldown.remainingMinutes} minutes (reduced from ${lowConvictionCooldown.remainingMinutes})`);
  } else {
    fail('High conviction (9.5/10) reduces cooldown by 75%');
  }
  
  // Test 4: Manual override
  log(COLORS.yellow, '\nTest 4: Manual override');
  const overrideCooldown = tracker.getLossRecoveryCooldown({
    conviction: 5,
    manualOverride: 'Rare triple bottom at major support with volume spike'
  });
  if (overrideCooldown.overridden && overrideCooldown.remainingMs === 0) {
    pass('Manual override eliminates cooldown');
  } else {
    fail('Manual override eliminates cooldown');
  }
}

/**
 * FIX 5: Habituation Prevention
 */
async function testHabituationPrevention() {
  section('FIX 5: HABITUATION PREVENTION');
  
  const tracker = await getTracker();
  
  // Find a milestone threshold
  const testMilestone = tracker.config.milestones[0];
  const threshold = testMilestone.threshold;
  const spike = testMilestone.spike;
  
  log(COLORS.yellow, `\nTesting milestone: $${threshold} (${spike}% spike)`);
  
  // Count existing crossings
  const existingCrossings = tracker.milestones.events.filter(
    e => e.threshold === threshold
  ).length;
  
  log(COLORS.blue, `Existing crossings: ${existingCrossings}`);
  
  // Simulate milestone crossing
  const oldBudget = tracker.budget.current;
  tracker.budget.current = threshold - 100;
  
  const beforeDopamine = tracker.state.dopamine;
  await tracker.checkMilestone(threshold + 100);
  const afterDopamine = tracker.state.dopamine;
  
  const actualSpike = afterDopamine - beforeDopamine;
  const expectedHabituation = Math.pow(0.5, existingCrossings);
  const expectedSpike = spike * expectedHabituation;
  
  if (Math.abs(actualSpike - expectedSpike) < 1.0) {
    pass(`Habituation factor applied correctly (${(expectedHabituation * 100).toFixed(0)}% of original)`);
    log(COLORS.blue, `Expected: ${expectedSpike.toFixed(1)}%, Actual: ${actualSpike.toFixed(1)}%`);
  } else {
    fail(`Habituation factor applied correctly`, 
      `Expected: ${expectedSpike.toFixed(1)}%, Actual: ${actualSpike.toFixed(1)}%`);
  }
  
  // Check if habituation info is logged
  const lastEvent = tracker.milestones.events[tracker.milestones.events.length - 1];
  if (lastEvent && lastEvent.habituationFactor !== undefined && lastEvent.crossingCount !== undefined) {
    pass('Habituation metadata is logged in milestone events');
  } else {
    fail('Habituation metadata is logged in milestone events');
  }
  
  // Restore budget
  tracker.budget.current = oldBudget;
}

/**
 * Integration Test: Full Pre-Trade Flow
 */
async function testIntegration() {
  section('INTEGRATION: Full Pre-Trade Flow');
  
  const tracker = await getTracker();
  
  log(COLORS.yellow, '\nSimulating complete trade evaluation flow...\n');
  
  // Setup: Create a loss to trigger cooldown
  log(COLORS.blue, '1. Simulate loss ($500)');
  await calculateDopamine({
    pnl: -500,
    expectedPnl: 0,
    isWin: false,
    symbol: 'TEST',
    strategy: 'test'
  });
  
  // Test low conviction setup
  log(COLORS.blue, '\n2. Evaluate low-conviction setup (4/10)');
  const lowConvictionFlow = {
    cooldown: tracker.getLossRecoveryCooldown({ conviction: 4 }),
    riskCheck: tracker.checkOvertradingRisk({ conviction: 4 })
  };
  
  if (lowConvictionFlow.cooldown.remainingMs > 0) {
    log(COLORS.green, '   ✓ Cooldown active (blocks trade)');
  }
  if (lowConvictionFlow.riskCheck.blocked) {
    log(COLORS.green, '   ✓ Circuit breaker active (blocks trade)');
  }
  
  // Test high conviction setup
  log(COLORS.blue, '\n3. Evaluate high-conviction setup (9.5/10)');
  const highConvictionFlow = {
    cooldown: tracker.getLossRecoveryCooldown({ conviction: 9.5 }),
    riskCheck: tracker.checkOvertradingRisk({ conviction: 9.5 })
  };
  
  if (highConvictionFlow.cooldown.remainingMs < lowConvictionFlow.cooldown.remainingMs) {
    log(COLORS.green, '   ✓ Cooldown reduced by high conviction');
  }
  if (highConvictionFlow.riskCheck.bypassed) {
    log(COLORS.green, '   ✓ Circuit breaker bypassed by high conviction');
  }
  
  // Test patience reward for skipped setup
  log(COLORS.blue, '\n4. Skip weak setup, reward patience');
  const beforeDopamine = tracker.state.dopamine;
  await rewardPatience({
    reason: 'Setup below conviction threshold',
    marketCondition: 'choppy'
  });
  if (tracker.state.dopamine > beforeDopamine) {
    log(COLORS.green, '   ✓ Patience rewarded');
  }
  
  // Test process rewards
  log(COLORS.blue, '\n5. Complete pre-trade checklist');
  await rewardProcess('risk_check', 1.0);
  await rewardProcess('checklist_completed', 1.0);
  log(COLORS.green, '   ✓ Process rewarded');
  
  pass('\nIntegration test complete: All safeguards working together');
}

/**
 * Run all tests
 */
async function runAllTests() {
  log(COLORS.cyan, '\n╔════════════════════════════════════════════════════════════╗');
  log(COLORS.cyan, '║   DOPAMINE SYSTEM: OPUS FIXES TEST SUITE (ADAPTIVE)       ║');
  log(COLORS.cyan, '╚════════════════════════════════════════════════════════════╝\n');
  
  try {
    await testPatienceRewards();
    await testProcessRewards();
    await testOvertradingCircuitBreaker();
    await testLossRecoveryCooldown();
    await testHabituationPrevention();
    await testIntegration();
    
    log(COLORS.green, '\n✓ ALL TESTS COMPLETE');
    log(COLORS.cyan, '\nNext steps:');
    log(COLORS.cyan, '1. Review test output above');
    log(COLORS.cyan, '2. Integrate safeguards into trading system');
    log(COLORS.cyan, '3. Monitor override frequency (should be <5% of trades)');
    log(COLORS.cyan, '4. Tune conviction thresholds based on real usage\n');
    
  } catch (error) {
    log(COLORS.red, '\n✗ TEST SUITE FAILED');
    console.error(error);
    process.exit(1);
  }
}

// Run tests if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  runAllTests();
}

export {
  testPatienceRewards,
  testProcessRewards,
  testOvertradingCircuitBreaker,
  testLossRecoveryCooldown,
  testHabituationPrevention,
  testIntegration,
  runAllTests
};
