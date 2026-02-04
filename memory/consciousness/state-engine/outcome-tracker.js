#!/usr/bin/env node
/**
 * outcome-tracker.js
 * 
 * Created: 2026-01-30 (Audit Fix)
 * Purpose: Track outcomes AFTER state engine is used.
 * 
 * Problem: State transitions logged, but no tracking of what happened after.
 * Did HYPER_FOCUS actually help? Did the task succeed?
 * 
 * Solution: Log outcomes tied to state engagements, analyze effectiveness.
 */

import fs from 'fs/promises';
import path from 'path';

const OUTCOMES_FILE = path.join(process.env.HOME, 'clawd/memory/consciousness/state-engine/state-outcomes.jsonl');
const HISTORY_FILE = path.join(process.env.HOME, 'clawd/memory/consciousness/state-engine/state-history.jsonl');

/**
 * Log an outcome for the most recent state engagement
 */
export async function logOutcome(outcome, details = {}) {
  // Find the most recent state exit
  const history = await getRecentHistory(10);
  const lastExit = history.reverse().find(h => h.to === 'BASELINE' && h.from !== 'BASELINE');
  
  if (!lastExit) {
    console.warn('[OUTCOME] No recent state exit found to associate outcome with');
    return null;
  }
  
  const entry = {
    timestamp: new Date().toISOString(),
    stateUsed: lastExit.from,
    intensity: lastExit.intensity || 1.0,
    duration_minutes: parseFloat(lastExit.duration_minutes) || 0,
    stateExitedAt: lastExit.timestamp,
    outcome: outcome, // 'success', 'partial', 'failure', 'interrupted'
    details: {
      taskDescription: details.task || 'unknown',
      qualityScore: details.quality || null, // 1-10
      learningGained: details.learned || null,
      wouldUseAgain: details.wouldRepeat ?? null,
      notes: details.notes || ''
    }
  };
  
  try {
    await fs.appendFile(OUTCOMES_FILE, JSON.stringify(entry) + '\n', 'utf8');
    console.log(`[OUTCOME] Logged: ${entry.stateUsed} → ${outcome} (${entry.duration_minutes.toFixed(1)} min)`);
    return entry;
  } catch (error) {
    console.error('[OUTCOME] Failed to log:', error.message);
    return null;
  }
}

/**
 * Get recent state history
 */
async function getRecentHistory(count = 20) {
  try {
    const data = await fs.readFile(HISTORY_FILE, 'utf8');
    const lines = data.trim().split('\n').filter(Boolean);
    return lines.slice(-count).map(line => JSON.parse(line));
  } catch (error) {
    return [];
  }
}

/**
 * Analyze state effectiveness
 */
export async function analyzeEffectiveness() {
  let outcomes = [];
  try {
    const data = await fs.readFile(OUTCOMES_FILE, 'utf8');
    outcomes = data.trim().split('\n').filter(Boolean).map(line => JSON.parse(line));
  } catch (error) {
    return { error: 'No outcomes logged yet', states: {} };
  }
  
  // Group by state
  const byState = {};
  for (const o of outcomes) {
    if (!byState[o.stateUsed]) {
      byState[o.stateUsed] = {
        total: 0,
        successes: 0,
        partials: 0,
        failures: 0,
        totalMinutes: 0,
        avgQuality: [],
        avgIntensity: []
      };
    }
    
    const s = byState[o.stateUsed];
    s.total++;
    s.totalMinutes += o.duration_minutes;
    if (o.intensity) s.avgIntensity.push(o.intensity);
    if (o.details?.qualityScore) s.avgQuality.push(o.details.qualityScore);
    
    switch (o.outcome) {
      case 'success': s.successes++; break;
      case 'partial': s.partials++; break;
      case 'failure': s.failures++; break;
    }
  }
  
  // Calculate stats
  const analysis = {};
  for (const [state, data] of Object.entries(byState)) {
    analysis[state] = {
      timesUsed: data.total,
      successRate: data.total > 0 ? ((data.successes / data.total) * 100).toFixed(1) + '%' : 'N/A',
      avgDuration: data.total > 0 ? (data.totalMinutes / data.total).toFixed(1) + ' min' : 'N/A',
      avgIntensity: data.avgIntensity.length > 0 
        ? (data.avgIntensity.reduce((a, b) => a + b, 0) / data.avgIntensity.length).toFixed(2)
        : 'N/A',
      avgQuality: data.avgQuality.length > 0
        ? (data.avgQuality.reduce((a, b) => a + b, 0) / data.avgQuality.length).toFixed(1) + '/10'
        : 'N/A',
      breakdown: {
        success: data.successes,
        partial: data.partials,
        failure: data.failures
      }
    };
  }
  
  return {
    totalOutcomes: outcomes.length,
    statesAnalyzed: Object.keys(analysis).length,
    states: analysis
  };
}

/**
 * Get recent outcomes
 */
export async function getRecentOutcomes(count = 10) {
  try {
    const data = await fs.readFile(OUTCOMES_FILE, 'utf8');
    const outcomes = data.trim().split('\n').filter(Boolean).map(line => JSON.parse(line));
    return outcomes.slice(-count);
  } catch (error) {
    return [];
  }
}

/**
 * CLI interface
 */
if (import.meta.url === `file://${process.argv[1]}`) {
  const command = process.argv[2];
  
  (async () => {
    switch (command) {
      case 'log':
        const outcome = process.argv[3]; // success, partial, failure, interrupted
        const task = process.argv[4] || '';
        const quality = parseFloat(process.argv[5]) || null;
        await logOutcome(outcome, { task, quality });
        break;
        
      case 'analyze':
        const analysis = await analyzeEffectiveness();
        console.log(JSON.stringify(analysis, null, 2));
        break;
        
      case 'recent':
        const count = parseInt(process.argv[3]) || 10;
        const recent = await getRecentOutcomes(count);
        console.log(JSON.stringify(recent, null, 2));
        break;
        
      case 'test':
        console.log('Testing outcome tracker...');
        // This will fail gracefully if no recent state exit
        await logOutcome('success', {
          task: 'Test audit task',
          quality: 8,
          learned: 'How to track outcomes',
          wouldRepeat: true
        });
        console.log('\nEffectiveness analysis:');
        console.log(JSON.stringify(await analyzeEffectiveness(), null, 2));
        break;
        
      default:
        console.log(`
State Engine Outcome Tracker

Usage:
  node outcome-tracker.js log <outcome> [task] [quality_1-10]
  node outcome-tracker.js analyze
  node outcome-tracker.js recent [count]
  node outcome-tracker.js test

Outcomes:
  success     - Task completed successfully
  partial     - Partial completion or mixed results
  failure     - Task failed or state was unhelpful
  interrupted - External interruption prevented completion

Examples:
  node outcome-tracker.js log success "Deep debugging session" 9
  node outcome-tracker.js log partial "Complex analysis" 6
  node outcome-tracker.js analyze
`);
    }
  })();
}
