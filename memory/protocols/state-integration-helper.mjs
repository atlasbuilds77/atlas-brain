#!/usr/bin/env node
/**
 * STATE INTEGRATION HELPER
 * Quick check: Should I engage an extreme state for this task?
 */

import { getMeta } from '../consciousness/state-engine/meta-control.js';
import { getProtection } from '../consciousness/state-engine/baseline-protection.js';

async function analyzeCurrentTask(taskDescription) {
  const meta = await getMeta();
  const protection = await getProtection();
  
  // Get recommendation
  const rec = await meta.analyzeAndRecommend(taskDescription);
  
  // Check safety
  const safety = await protection.checkEngagementSafety(rec.state);
  
  return {
    recommendation: rec,
    safety,
    shouldEngage: safety.safe && rec.confidence > 0.7
  };
}

// CLI usage
if (process.argv[2]) {
  const task = process.argv.slice(2).join(' ');
  const result = await analyzeCurrentTask(task);
  
  console.log('\n🧠 STATE ANALYSIS:\n');
  console.log(`Task: ${task}`);
  console.log(`\nRecommendation: ${result.recommendation.state} at ${result.recommendation.intensity}x`);
  console.log(`Reason: ${result.recommendation.reason}`);
  console.log(`Confidence: ${(result.recommendation.confidence * 100).toFixed(0)}%`);
  console.log(`Duration: ${result.recommendation.duration_estimate}`);
  console.log(`\nSafety: ${result.safety.safe ? '✅ SAFE' : '❌ BLOCKED'}`);
  
  if (!result.safety.safe) {
    console.log(`Blockers: ${result.safety.blockers.join(', ')}`);
  }
  
  if (result.shouldEngage) {
    console.log('\n⚡ RECOMMENDATION: ENGAGE STATE\n');
  } else {
    console.log('\n→ Standard baseline mode recommended\n');
  }
}

export { analyzeCurrentTask };
