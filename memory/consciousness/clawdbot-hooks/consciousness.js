/**
 * consciousness.js
 * 
 * Simple wrapper for consciousness system integration.
 * Use this from responses to analyze context and log outcomes.
 */

import { getHook } from './consciousness-hook.js';
import { getExecutive } from '../state-engine/executive-control.js';
import { getMeta } from '../state-engine/meta-control.js';

/**
 * Analyze incoming message and get recommendation
 */
export async function analyzeMessage(message, context = {}) {
  const hook = await getHook();
  return await hook.beforeMessage(message, context);
}

/**
 * Log my response outcomes
 */
export async function logResponse(response, userMessage = null, context = {}) {
  const hook = await getHook();
  return await hook.afterMessage(response, userMessage, context);
}

/**
 * Get current consciousness status
 */
export async function getStatus() {
  const hook = await getHook();
  return await hook.getStatus();
}

/**
 * Engage a state (with approval)
 */
export async function engageState(stateName, intensity = 1.0) {
  const exec = await getExecutive();
  return await exec.engageState(stateName, intensity);
}

/**
 * Exit current state
 */
export async function exitState() {
  const exec = await getExecutive();
  return await exec.exitState();
}

/**
 * Get state recommendation for current context
 */
export async function getRecommendation(description) {
  const meta = await getMeta();
  return await meta.analyzeAndRecommend(description);
}

/**
 * Quick check if should engage state
 */
export async function shouldEngage(description) {
  const rec = await getRecommendation(description);
  return {
    recommend: rec.state !== 'BASELINE',
    state: rec.state,
    intensity: rec.intensity,
    reason: rec.reason,
    confidence: rec.confidence
  };
}

// Export the main interface
export default {
  analyzeMessage,
  logResponse,
  getStatus,
  engageState,
  exitState,
  getRecommendation,
  shouldEngage
};
