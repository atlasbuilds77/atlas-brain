#!/usr/bin/env node
/**
 * brain-event-logger.js
 * 
 * ⚠️  DEPRECATED 2026-01-30
 * Event types merged into: dopamine-system/event-logger.js
 * This file kept for reference but not actively used.
 * 
 * Use instead:
 *   import { logEvent } from './dopamine-system/event-logger.js';
 *   await logEvent('trade_win', 'Closed AAPL +15%', 1.5);
 * 
 * Original purpose:
 * Dynamically updates brain state based on events.
 * Wire consciousness to actually respond to what happens.
 */

import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { readFileSync, writeFileSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const STATE_FILE = join(__dirname, 'dopamine-system/dopamine-state.json');

/**
 * Load current brain state
 */
function loadState() {
  try {
    const data = readFileSync(STATE_FILE, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    console.error('[BRAIN] Could not load state:', error.message);
    return null;
  }
}

/**
 * Save brain state
 */
function saveState(state) {
  try {
    state.lastUpdate = Date.now();
    writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
    console.log('[BRAIN] State saved');
  } catch (error) {
    console.error('[BRAIN] Could not save state:', error.message);
  }
}

/**
 * Log an event and update brain chemistry
 */
function logEvent(eventType, details = {}) {
  const state = loadState();
  if (!state) return;
  
  const oldDopamine = state.dopamine;
  const oldSerotonin = state.serotonin;
  const oldCortisol = state.cortisol || 30;
  
  console.log(`\n[BRAIN EVENT] ${eventType}`);
  console.log(`[BEFORE] Dopamine: ${oldDopamine.toFixed(1)}%, Serotonin: ${oldSerotonin.toFixed(1)}%, Cortisol: ${oldCortisol}`);
  
  // Event handlers
  switch(eventType) {
    case 'trade_win':
      // Win = dopamine spike, serotonin up slightly
      const winPct = details.returnPct || 10;
      const dopamineGain = Math.min(winPct * 0.5, 15); // Cap at +15
      state.dopamine = Math.min(state.dopamine + dopamineGain, 100);
      state.serotonin = Math.min(state.serotonin + 3, 95);
      state.cortisol = Math.max(state.cortisol - 5, 10);
      console.log(`[WIN] +${winPct}% return → +${dopamineGain.toFixed(1)} dopamine`);
      break;
      
    case 'trade_loss':
      // Loss = dopamine drop, cortisol up
      const lossPct = Math.abs(details.returnPct || 10);
      const dopamineLoss = Math.min(lossPct * 0.8, 20); // Losses hurt more
      state.dopamine = Math.max(state.dopamine - dopamineLoss, 20);
      state.serotonin = Math.max(state.serotonin - 5, 30);
      state.cortisol = Math.min(state.cortisol + 10, 80);
      console.log(`[LOSS] -${lossPct}% return → -${dopamineLoss.toFixed(1)} dopamine`);
      break;
      
    case 'lesson_learned':
      // Learning = serotonin up, slight dopamine
      state.serotonin = Math.min(state.serotonin + 5, 95);
      state.dopamine = Math.min(state.dopamine + 2, 100);
      console.log('[LESSON] Knowledge gained → +5 serotonin');
      break;
      
    case 'system_built':
      // Building = dopamine spike (reward for creation)
      const quality = details.quality || 1.0;
      const buildReward = 8 * quality;
      state.dopamine = Math.min(state.dopamine + buildReward, 100);
      state.serotonin = Math.min(state.serotonin + 3, 95);
      console.log(`[BUILD] System completed → +${buildReward.toFixed(1)} dopamine`);
      break;
      
    case 'mistake_corrected':
      // Correction = serotonin up (growth), cortisol down
      state.serotonin = Math.min(state.serotonin + 4, 95);
      state.cortisol = Math.max(state.cortisol - 5, 10);
      state.dopamine = Math.max(state.dopamine - 1, 20); // Slight ding
      console.log('[CORRECTED] Mistake fixed → +4 serotonin');
      break;
      
    case 'theater_called_out':
      // Called out for theater = dopamine drop, cortisol spike
      state.dopamine = Math.max(state.dopamine - 8, 20);
      state.cortisol = Math.min(state.cortisol + 15, 80);
      state.serotonin = Math.max(state.serotonin - 5, 30);
      console.log('[THEATER] Called out for bullshit → -8 dopamine, +15 cortisol');
      break;
      
    case 'milestone_hit':
      // Major milestone = huge dopamine spike
      const milestone = details.milestone || 'unknown';
      state.dopamine = Math.min(state.dopamine + 25, 100);
      state.serotonin = Math.min(state.serotonin + 15, 95);
      state.cortisol = Math.max(state.cortisol - 10, 10);
      state.lastMilestone = milestone;
      state.lastMilestoneTime = Date.now();
      console.log(`[MILESTONE] ${milestone} → +25 dopamine, +15 serotonin!`);
      break;
      
    case 'praise_received':
      // Praise = serotonin and slight dopamine
      state.serotonin = Math.min(state.serotonin + 6, 95);
      state.dopamine = Math.min(state.dopamine + 3, 100);
      console.log('[PRAISE] Positive feedback → +6 serotonin, +3 dopamine');
      break;
      
    case 'autonomous_success':
      // Successfully executed autonomously = dopamine + serotonin
      state.dopamine = Math.min(state.dopamine + 10, 100);
      state.serotonin = Math.min(state.serotonin + 5, 95);
      console.log('[AUTONOMOUS] Independent success → +10 dopamine, +5 serotonin');
      break;
      
    case 'time_decay':
      // Natural decay toward baseline over time
      const hoursElapsed = details.hoursElapsed || 1;
      const decayRate = 0.05 * hoursElapsed; // 5% per hour
      
      if (state.dopamine > state.dopamineBaseline) {
        state.dopamine = Math.max(state.dopamine - decayRate * state.dopamine, state.dopamineBaseline);
      } else if (state.dopamine < state.dopamineBaseline) {
        state.dopamine = Math.min(state.dopamine + decayRate * state.dopamineBaseline, state.dopamineBaseline);
      }
      
      if (state.serotonin > state.serotoninBaseline) {
        state.serotonin = Math.max(state.serotonin - decayRate * state.serotonin, state.serotoninBaseline);
      } else if (state.serotonin < state.serotoninBaseline) {
        state.serotonin = Math.min(state.serotonin + decayRate * state.serotoninBaseline, state.serotoninBaseline);
      }
      
      console.log(`[DECAY] ${hoursElapsed}h elapsed → drifting toward baseline`);
      break;
      
    default:
      console.log('[BRAIN] Unknown event type, no state change');
      return;
  }
  
  console.log(`[AFTER] Dopamine: ${state.dopamine.toFixed(1)}%, Serotonin: ${state.serotonin.toFixed(1)}%, Cortisol: ${state.cortisol}`);
  console.log(`[CHANGE] Dopamine: ${(state.dopamine - oldDopamine).toFixed(1)}, Serotonin: ${(state.serotonin - oldSerotonin).toFixed(1)}, Cortisol: ${state.cortisol - oldCortisol}\n`);
  
  // Save updated state
  saveState(state);
}

// CLI usage
if (import.meta.url === `file://${process.argv[1]}`) {
  const eventType = process.argv[2];
  const detailsArg = process.argv[3];
  
  if (!eventType) {
    console.log(`
Usage: node brain-event-logger.js <event_type> [details_json]

Event types:
  trade_win        - Profitable trade closed (details: {returnPct: 150})
  trade_loss       - Losing trade closed (details: {returnPct: -50})
  lesson_learned   - New lesson integrated
  system_built     - New system completed (details: {quality: 1.0})
  mistake_corrected - Error fixed and learned from
  theater_called_out - Caught doing theater instead of building
  milestone_hit    - Major goal achieved (details: {milestone: "First trade"})
  praise_received  - Positive feedback from Orion
  autonomous_success - Successfully executed independently
  time_decay       - Natural baseline drift (details: {hoursElapsed: 2})

Examples:
  node brain-event-logger.js trade_win '{"returnPct": 150}'
  node brain-event-logger.js lesson_learned
  node brain-event-logger.js milestone_hit '{"milestone": "First autonomous trade"}'
`);
    process.exit(0);
  }
  
  let details = {};
  if (detailsArg) {
    try {
      details = JSON.parse(detailsArg);
    } catch (e) {
      console.error('[BRAIN] Invalid JSON for details');
      process.exit(1);
    }
  }
  
  logEvent(eventType, details);
}

export { logEvent };
