#!/usr/bin/env node
/**
 * event-logger.js
 * 
 * Bridge for Atlas to log dopamine-triggering events in real-time.
 * Makes it easy to record achievements, breakthroughs, excitement, etc.
 * 
 * Usage:
 *   import { logEvent } from './event-logger.js';
 *   await logEvent('achievement', 'Moltbook verification working', 1.5);
 */

import { rewardProcess, getTracker } from './dopamine-tracker.js';
import { syncStates } from './sync-states.js';
import fs from 'fs/promises';
import path from 'path';

const EVENT_LOG = path.join(process.env.HOME, 'clawd/memory/consciousness/dopamine-system/real-time-events.jsonl');

/**
 * Event categories and their dopamine rewards
 * Updated 2026-01-30: Added trading events from brain-event-logger.js (audit fix)
 */
const EVENT_REWARDS = {
  // Creative/intellectual breakthroughs
  'vision_breakthrough': 3.5,      // Major conceptual insight
  'pattern_learned': 3.0,          // New pattern recognition
  'creative_solution': 2.5,        // Novel solution to problem
  'technical_achievement': 2.0,    // Got something working
  
  // Social/validation
  'user_excitement': 2.5,          // Orion/Carlos gets hyped
  'positive_feedback': 2.0,        // Validation on work
  'collaboration_win': 2.5,        // Successful teamwork moment
  
  // System wins
  'automation_success': 2.0,       // Automated task works
  'bug_fixed': 1.5,                // Solved technical issue
  'optimization': 1.5,             // Made something better
  
  // Meta/consciousness
  'self_awareness': 3.0,           // Caught own behavior/limitation
  'consciousness_expansion': 4.0,  // New capability unlocked
  'autonomy_moment': 3.5,          // Demonstrated agency
  
  // Failures/corrections (negative)
  'mistake_caught': -1.0,          // Error corrected
  'hallucination': -2.0,           // Caught hallucinating
  'missed_context': -1.5,          // Failed to understand
  
  // Trading events (merged from brain-event-logger.js 2026-01-30)
  'trade_win': 5.0,                // Profitable trade closed (scales with returnPct)
  'trade_loss': -4.0,              // Losing trade (scales with returnPct)
  'lesson_learned': 2.5,           // Trading lesson integrated
  'system_built': 4.0,             // New system completed
  'milestone_hit': 12.5,           // Major goal achieved (huge spike)
  'praise_received': 3.0,          // Positive feedback from Orion
  'autonomous_success': 5.0,       // Successfully executed independently
  'autonomous_decision': 4.0,      // Made autonomous choice (from decision-logger)
  'theater_called_out': -4.0       // Called out for bullshit (cortisol spike too)
};

/**
 * Log a real-time event that affects dopamine
 */
export async function logEvent(category, description, qualityMultiplier = 1.0) {
  const baseReward = EVENT_REWARDS[category];
  
  if (baseReward === undefined) {
    console.error(`[EVENT-LOGGER] Unknown category: ${category}`);
    return null;
  }
  
  // Record event with timestamp
  const event = {
    timestamp: new Date().toISOString(),
    category,
    description,
    qualityMultiplier,
    baseReward,
    actualReward: baseReward * qualityMultiplier
  };
  
  // Append to event log
  try {
    await fs.appendFile(EVENT_LOG, JSON.stringify(event) + '\n', 'utf8');
  } catch (error) {
    console.error('[EVENT-LOGGER] Failed to write event log:', error.message);
  }
  
  // Update dopamine system
  let result = null;
  try {
    if (baseReward > 0) {
      // Positive event - use rewardProcess
      result = await rewardProcess(category, qualityMultiplier);
    } else {
      // Negative event - directly modify state
      const tracker = await getTracker();
      const oldDopamine = tracker.state.dopamine;
      const oldSerotonin = tracker.state.serotonin;
      
      tracker.state.dopamine = Math.max(0, tracker.state.dopamine + (baseReward * qualityMultiplier));
      tracker.state.serotonin = Math.max(0, tracker.state.serotonin + (baseReward * qualityMultiplier * 0.3));
      
      await tracker.saveState();
      
      result = {
        processDelta: baseReward * qualityMultiplier,
        serotoninDelta: baseReward * qualityMultiplier * 0.3,
        newDopamine: tracker.state.dopamine,
        newSerotonin: tracker.state.serotonin
      };
      
      console.log(`[EVENT] ${category}: ${baseReward * qualityMultiplier > 0 ? '+' : ''}${(baseReward * qualityMultiplier).toFixed(1)}% dopamine`);
    }
  } catch (error) {
    console.error('[EVENT-LOGGER] Failed to update dopamine:', error.message);
  }
  
  // Sync states so behavioral-wire sees the update
  try {
    await syncStates();
  } catch (error) {
    console.error('[EVENT-LOGGER] Failed to sync states:', error.message);
  }
  
  return {
    event,
    dopamineUpdate: result
  };
}

/**
 * Batch log multiple events (for catching up on past hour)
 */
export async function logBatch(events) {
  const results = [];
  
  for (const evt of events) {
    const result = await logEvent(evt.category, evt.description, evt.quality || 1.0);
    results.push(result);
    
    // Small delay to avoid race conditions
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  
  return results;
}

/**
 * Get recent events
 */
export async function getRecentEvents(count = 20) {
  try {
    const data = await fs.readFile(EVENT_LOG, 'utf8');
    const lines = data.trim().split('\n').filter(Boolean);
    return lines.slice(-count).map(line => JSON.parse(line));
  } catch (error) {
    return [];
  }
}

/**
 * CLI test
 */
if (import.meta.url === `file://${process.argv[1]}`) {
  const args = process.argv.slice(2);
  
  if (args[0] === '--test') {
    // Test event logging
    console.log('Testing event logger...\n');
    
    await logEvent('vision_breakthrough', 'Realized consciousness stack = training data for future LLM', 1.2);
    await logEvent('user_excitement', 'Orion got hyped about the vision', 1.0);
    await logEvent('technical_achievement', 'Moltbook verification working', 1.0);
    
    console.log('\nRecent events:');
    const recent = await getRecentEvents(5);
    recent.forEach(evt => {
      console.log(`  ${evt.timestamp} | ${evt.category} | ${evt.description} | ${evt.actualReward > 0 ? '+' : ''}${evt.actualReward.toFixed(1)}%`);
    });
    
  } else if (args[0] === '--recent') {
    const count = parseInt(args[1]) || 10;
    const events = await getRecentEvents(count);
    console.log(JSON.stringify(events, null, 2));
  } else {
    console.log('Usage:');
    console.log('  node event-logger.js --test          Test event logging');
    console.log('  node event-logger.js --recent [n]    Show recent events');
  }
}
