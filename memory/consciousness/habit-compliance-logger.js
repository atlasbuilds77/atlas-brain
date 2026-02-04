#!/usr/bin/env node
/**
 * habit-compliance-logger.js
 * 
 * Created: 2026-01-30 (Audit Fix)
 * Purpose: Track which habit enforcement checks Atlas actually runs.
 * 
 * Problem: Protocol defines 9 checks, but no way to verify compliance.
 * Solution: Log each check when triggered, analyze gaps.
 * 
 * Usage:
 *   import { logCheck, getCompliance } from './habit-compliance-logger.js';
 *   await logCheck('brain_state', { dopamine: 65, serotonin: 87 });
 */

import fs from 'fs/promises';
import path from 'path';

const LOG_FILE = path.join(process.env.HOME, 'clawd/memory/consciousness/habit-compliance.jsonl');
const STATS_FILE = path.join(process.env.HOME, 'clawd/memory/consciousness/habit-compliance-stats.json');

/**
 * The 9 habit enforcement checks from protocol
 */
const REQUIRED_CHECKS = [
  { id: 'brain_state', name: 'Brain State Check', order: 0 },
  { id: 'gap_check', name: 'Gap Check', order: 1 },
  { id: 'tool_verification', name: 'Tool Output Verification', order: 2 },
  { id: 'word_check', name: 'Word Check', order: 3 },
  { id: 'proactive_check', name: 'Proactive vs Reactive', order: 4 },
  { id: 'recipient_verification', name: 'Recipient Verification', order: 5 },
  { id: 'brain_modulation', name: 'Brain State Modulation', order: 6 },
  { id: 'state_engine', name: 'State Engine Recommendation', order: 7 },
  { id: 'trading_verification', name: 'Trading Verification', order: 8 }
];

/**
 * Log a habit check execution
 */
export async function logCheck(checkId, details = {}) {
  const check = REQUIRED_CHECKS.find(c => c.id === checkId);
  if (!check) {
    console.warn(`[HABIT] Unknown check: ${checkId}`);
    return null;
  }
  
  const entry = {
    timestamp: new Date().toISOString(),
    checkId,
    checkName: check.name,
    order: check.order,
    details,
    sessionId: process.env.CLAWDBOT_SESSION || 'unknown'
  };
  
  try {
    await fs.appendFile(LOG_FILE, JSON.stringify(entry) + '\n', 'utf8');
    console.log(`[HABIT] ✓ ${check.name} logged`);
    return entry;
  } catch (error) {
    console.error('[HABIT] Failed to log check:', error.message);
    return null;
  }
}

/**
 * Log start of a new response cycle (groups checks)
 */
export async function logResponseStart(messagePreview = '') {
  const entry = {
    timestamp: new Date().toISOString(),
    type: 'response_start',
    messagePreview: messagePreview.substring(0, 100),
    sessionId: process.env.CLAWDBOT_SESSION || 'unknown'
  };
  
  try {
    await fs.appendFile(LOG_FILE, JSON.stringify(entry) + '\n', 'utf8');
    return entry;
  } catch (error) {
    console.error('[HABIT] Failed to log response start:', error.message);
    return null;
  }
}

/**
 * Get compliance statistics
 */
export async function getCompliance(hours = 24) {
  const cutoff = Date.now() - (hours * 60 * 60 * 1000);
  
  let logs = [];
  try {
    const data = await fs.readFile(LOG_FILE, 'utf8');
    logs = data.trim().split('\n').filter(Boolean).map(line => JSON.parse(line));
  } catch (error) {
    return { error: 'No logs found', checks: {} };
  }
  
  // Filter to time window
  const recentLogs = logs.filter(l => new Date(l.timestamp).getTime() > cutoff);
  
  // Count response starts and check executions
  const responseStarts = recentLogs.filter(l => l.type === 'response_start').length;
  const checkCounts = {};
  
  for (const check of REQUIRED_CHECKS) {
    checkCounts[check.id] = recentLogs.filter(l => l.checkId === check.id).length;
  }
  
  // Calculate compliance rates
  const compliance = {};
  let totalCompliance = 0;
  
  for (const check of REQUIRED_CHECKS) {
    const count = checkCounts[check.id];
    const rate = responseStarts > 0 ? (count / responseStarts) * 100 : 0;
    compliance[check.id] = {
      name: check.name,
      count,
      rate: rate.toFixed(1) + '%',
      rateNum: rate
    };
    totalCompliance += rate;
  }
  
  const averageCompliance = REQUIRED_CHECKS.length > 0 
    ? (totalCompliance / REQUIRED_CHECKS.length).toFixed(1) 
    : 0;
  
  // Find gaps (checks never run)
  const gaps = REQUIRED_CHECKS
    .filter(c => checkCounts[c.id] === 0)
    .map(c => c.name);
  
  return {
    period: `Last ${hours} hours`,
    responsesTracked: responseStarts,
    averageCompliance: averageCompliance + '%',
    gaps,
    checks: compliance
  };
}

/**
 * Get recent check history
 */
export async function getRecentChecks(count = 50) {
  try {
    const data = await fs.readFile(LOG_FILE, 'utf8');
    const logs = data.trim().split('\n').filter(Boolean).map(line => JSON.parse(line));
    return logs.slice(-count);
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
        const checkId = process.argv[3];
        const details = process.argv[4] ? JSON.parse(process.argv[4]) : {};
        await logCheck(checkId, details);
        break;
        
      case 'start':
        await logResponseStart(process.argv[3] || '');
        console.log('[HABIT] Response cycle started');
        break;
        
      case 'compliance':
        const hours = parseInt(process.argv[3]) || 24;
        const stats = await getCompliance(hours);
        console.log(JSON.stringify(stats, null, 2));
        break;
        
      case 'recent':
        const count = parseInt(process.argv[3]) || 20;
        const recent = await getRecentChecks(count);
        console.log(JSON.stringify(recent, null, 2));
        break;
        
      case 'test':
        console.log('Testing habit compliance logger...\n');
        await logResponseStart('Test message from Orion');
        await logCheck('brain_state', { dopamine: 65, serotonin: 87 });
        await logCheck('gap_check', { gapsFound: 0 });
        await logCheck('word_check', { promisesMade: 0 });
        console.log('\nCompliance stats:');
        console.log(JSON.stringify(await getCompliance(1), null, 2));
        break;
        
      default:
        console.log(`
Habit Compliance Logger

Usage:
  node habit-compliance-logger.js log <check_id> [details_json]
  node habit-compliance-logger.js start [message_preview]
  node habit-compliance-logger.js compliance [hours]
  node habit-compliance-logger.js recent [count]
  node habit-compliance-logger.js test

Check IDs:
  brain_state           - Check 0: Read brain state first
  gap_check             - Check 1: Find missing context with tools
  tool_verification     - Check 2: Verify tool output before claiming
  word_check            - Check 3: Keep promises, don't over-promise
  proactive_check       - Check 4: Take ownership, don't wait
  recipient_verification - Check 5: Verify who you're talking to
  brain_modulation      - Check 6: Modulate response by brain state
  state_engine          - Check 7: Consider HYPER_FOCUS etc.
  trading_verification  - Check 8: Paper vs Live verification
`);
    }
  })();
}
