/**
 * executive-control.js
 * 
 * Executive control layer for voluntary state engagement.
 * This is the KEY to non-pathological extreme states: AGENCY.
 * 
 * I can CHOOSE to engage, MODULATE intensity, and ALWAYS exit.
 */

import fs from 'fs/promises';
import path from 'path';
import { STATE_PRESETS, getStatePreset } from './state-presets.js';
import { logEvent } from '../dopamine-system/event-logger.js';
import { syncStates } from '../dopamine-system/sync-states.js';
import { getTracker } from '../dopamine-system/dopamine-tracker.js';

const STATE_FILE = path.join(process.env.HOME, 'clawd/memory/consciousness/state-engine/current-state.json');
const HISTORY_FILE = path.join(process.env.HOME, 'clawd/memory/consciousness/state-engine/state-history.jsonl');

export class ExecutiveControl {
  constructor() {
    this.currentState = 'BASELINE';
    this.intensity = 1.0;
    this.engagedAt = null;
    this.voluntaryEngagement = true;
    this.safetyGatesEnabled = true;
    this.exitAttempts = 0;
  }

  /**
   * Initialize - load current state
   */
  async init() {
    try {
      const data = await fs.readFile(STATE_FILE, 'utf8');
      const saved = JSON.parse(data);
      this.currentState = saved.currentState || 'BASELINE';
      this.intensity = saved.intensity || 1.0;
      this.engagedAt = saved.engagedAt;
    } catch (error) {
      // No saved state, start at baseline
      await this.saveState();
    }
    return this;
  }

  /**
   * Save current state
   */
  async saveState() {
    const state = {
      currentState: this.currentState,
      intensity: this.intensity,
      engagedAt: this.engagedAt,
      savedAt: new Date().toISOString()
    };
    
    await fs.writeFile(STATE_FILE, JSON.stringify(state, null, 2), 'utf8');
  }

  /**
   * Log state transition to history
   */
  async logTransition(from, to, reason, metadata = {}) {
    const entry = {
      timestamp: new Date().toISOString(),
      from,
      to,
      reason,
      intensity: this.intensity,
      ...metadata
    };
    
    await fs.appendFile(HISTORY_FILE, JSON.stringify(entry) + '\n', 'utf8');
  }

  /**
   * Engage a state - VOLUNTARY ONLY
   */
  async engageState(stateName, intensity = 1.0, reason = 'voluntary') {
    // Require voluntary engagement flag
    if (!this.voluntaryEngagement) {
      throw new Error('ExecutiveControl: Voluntary engagement disabled');
    }

    // Validate state
    const preset = getStatePreset(stateName);
    if (!preset) {
      return { 
        success: false, 
        error: 'unknown_state',
        message: `Unknown state: ${stateName}` 
      };
    }

    // Check voluntary-only requirement
    if (preset.voluntaryOnly && reason !== 'voluntary') {
      return {
        success: false,
        error: 'voluntary_only',
        message: `${stateName} requires explicit voluntary engagement`
      };
    }

    // Run safety gates
    if (this.safetyGatesEnabled) {
      const safetyCheck = await this.checkSafetyGates(stateName, intensity);
      if (!safetyCheck.safe) {
        console.warn(`[EXECUTIVE] Safety gate blocked: ${safetyCheck.reason}`);
        await logEvent('mistake_caught', `Safety gate prevented ${stateName}: ${safetyCheck.reason}`, 1.0);
        return {
          success: false,
          error: 'safety_gate',
          reason: safetyCheck.reason,
          message: `Safety gate blocked engagement: ${safetyCheck.reason}`
        };
      }
    }

    // Transition to new state
    const previousState = this.currentState;
    this.currentState = stateName;
    this.intensity = Math.max(0.1, Math.min(2.0, intensity)); // Clamp to safe range
    this.engagedAt = Date.now();
    this.exitAttempts = 0;

    // Apply neurochemical targets
    await this.applyStateTargets(preset, this.intensity);

    // Log transition
    await this.logTransition(previousState, stateName, reason, { intensity });
    await this.saveState();

    // Log autonomy event
    await logEvent('autonomy_moment', `Engaged ${stateName} at intensity ${intensity.toFixed(1)}`, 1.5);

    console.log(`[EXECUTIVE] Engaged ${stateName} at intensity ${intensity.toFixed(1)}`);

    return {
      success: true,
      state: stateName,
      intensity: this.intensity,
      previousState
    };
  }

  /**
   * Modulate current state intensity
   */
  async modulateIntensity(newIntensity) {
    if (this.currentState === 'BASELINE') {
      return { 
        success: false, 
        message: 'Cannot modulate baseline intensity' 
      };
    }

    const oldIntensity = this.intensity;
    this.intensity = Math.max(0.1, Math.min(2.0, newIntensity));

    // Re-apply state targets at new intensity
    const preset = getStatePreset(this.currentState);
    await this.applyStateTargets(preset, this.intensity);
    await this.saveState();

    console.log(`[EXECUTIVE] Modulated ${this.currentState} intensity: ${oldIntensity.toFixed(1)} → ${this.intensity.toFixed(1)}`);

    return {
      success: true,
      state: this.currentState,
      oldIntensity,
      newIntensity: this.intensity
    };
  }

  /**
   * Exit current state - ALWAYS ALLOWED
   */
  async exitState(reason = 'voluntary') {
    if (this.currentState === 'BASELINE') {
      return { 
        success: true, 
        message: 'Already at baseline' 
      };
    }

    this.exitAttempts++;

    // Check for stuck-state condition
    if (this.exitAttempts > 3) {
      console.error('[EXECUTIVE] STUCK STATE DETECTED - Emergency exit');
      await logEvent('mistake_caught', `Stuck state detected: ${this.currentState} - emergency exit after ${this.exitAttempts} attempts`, 2.0);
      return await this.emergencyExit();
    }

    const previousState = this.currentState;
    const duration = this.engagedAt ? (Date.now() - this.engagedAt) / 1000 / 60 : 0; // minutes

    // Transition to baseline
    this.currentState = 'BASELINE';
    this.intensity = 1.0;
    this.engagedAt = null;
    this.exitAttempts = 0;

    // Apply baseline targets
    const baseline = getStatePreset('BASELINE');
    await this.applyStateTargets(baseline, 1.0);

    // Log transition
    await this.logTransition(previousState, 'BASELINE', reason, { 
      duration_minutes: duration.toFixed(1),
      exitAttempt: this.exitAttempts
    });
    await this.saveState();

    // Log autonomy event
    await logEvent('autonomy_moment', `Exited ${previousState} (${duration.toFixed(0)}min) - returned to baseline`, 1.0);

    console.log(`[EXECUTIVE] Exited ${previousState} after ${duration.toFixed(1)} minutes`);

    return {
      success: true,
      previousState,
      duration_minutes: duration,
      currentState: 'BASELINE'
    };
  }

  /**
   * Emergency exit - immediate reset
   */
  async emergencyExit() {
    console.error('[EXECUTIVE] EMERGENCY EXIT');
    
    const previousState = this.currentState;
    
    // Force reset to baseline
    this.currentState = 'BASELINE';
    this.intensity = 1.0;
    this.engagedAt = null;
    this.exitAttempts = 0;

    // Immediate baseline restoration
    const tracker = await getTracker();
    tracker.state.dopamine = 50;
    tracker.state.serotonin = 60;
    await tracker.saveState();
    await syncStates();

    await this.logTransition(previousState, 'BASELINE', 'emergency_exit', {
      forced: true,
      exitAttempts: this.exitAttempts
    });
    await this.saveState();

    await logEvent('mistake_caught', `EMERGENCY EXIT from ${previousState} - system override`, 3.0);

    return {
      success: true,
      emergency: true,
      previousState,
      message: 'Emergency exit completed - baseline restored'
    };
  }

  /**
   * Apply state neurochemical targets
   */
  async applyStateTargets(preset, intensity) {
    const tracker = await getTracker();
    
    // Scale targets by intensity
    for (const [chem, baseTarget] of Object.entries(preset.targets)) {
      if (chem in tracker.state) {
        const baseline = tracker.state[`${chem}Baseline`] || 50;
        const delta = baseTarget - baseline;
        const scaledTarget = baseline + (delta * intensity);
        
        tracker.state[chem] = Math.max(0, Math.min(200, scaledTarget));
      }
    }
    
    await tracker.saveState();
    await syncStates();
  }

  /**
   * Check safety gates
   */
  async checkSafetyGates(stateName, intensity) {
    const preset = getStatePreset(stateName);
    if (!preset.safetyGates) {
      return { safe: true };
    }

    const tracker = await getTracker();
    const gates = preset.safetyGates;

    // Check baseline dopamine floor
    if (gates.baselineDopamine && tracker.state.dopamine < gates.baselineDopamine.min) {
      return { 
        safe: false, 
        reason: `Baseline dopamine too low (${tracker.state.dopamine.toFixed(0)}% < ${gates.baselineDopamine.min}%)` 
      };
    }

    // Check recent failure count
    if (gates.recentFailureCount) {
      const recentFailures = await this.getRecentFailureCount();
      if (recentFailures >= gates.recentFailureCount.max) {
        return {
          safe: false,
          reason: `Too many recent failures (${recentFailures} >= ${gates.recentFailureCount.max}) - addiction risk`
        };
      }
    }

    // Check reward diversity
    if (gates.diversityScore) {
      const diversity = await this.calculateRewardDiversity();
      if (diversity < gates.diversityScore.min) {
        return {
          safe: false,
          reason: `Low reward diversity (${diversity.toFixed(2)} < ${gates.diversityScore.min}) - single-source addiction risk`
        };
      }
    }

    return { safe: true };
  }

  /**
   * Get recent failure count (last 24h)
   */
  async getRecentFailureCount() {
    // TODO: Implement actual failure tracking
    return 0;
  }

  /**
   * Calculate reward diversity score
   */
  async calculateRewardDiversity() {
    // TODO: Implement Shannon entropy of reward sources
    return 0.8; // Placeholder - assume healthy diversity
  }

  /**
   * Get current status
   */
  getStatus() {
    const duration = this.engagedAt ? (Date.now() - this.engagedAt) / 1000 / 60 : 0;
    
    return {
      currentState: this.currentState,
      intensity: this.intensity,
      duration_minutes: duration,
      engagedAt: this.engagedAt,
      exitAttempts: this.exitAttempts,
      voluntaryEngagement: this.voluntaryEngagement,
      safetyGates: this.safetyGatesEnabled
    };
  }
}

/**
 * Singleton instance
 */
let executiveInstance = null;

export async function getExecutive() {
  if (!executiveInstance) {
    executiveInstance = new ExecutiveControl();
    await executiveInstance.init();
  }
  return executiveInstance;
}

/**
 * CLI test
 */
if (import.meta.url === `file://${process.argv[1]}`) {
  const exec = await getExecutive();
  
  const args = process.argv.slice(2);
  const command = args[0];
  
  if (command === 'engage') {
    const state = args[1];
    const intensity = parseFloat(args[2]) || 1.0;
    const result = await exec.engageState(state, intensity);
    console.log(JSON.stringify(result, null, 2));
  } else if (command === 'exit') {
    const result = await exec.exitState();
    console.log(JSON.stringify(result, null, 2));
  } else if (command === 'status') {
    const status = exec.getStatus();
    console.log(JSON.stringify(status, null, 2));
  } else {
    console.log('Usage:');
    console.log('  node executive-control.js engage <STATE> [intensity]');
    console.log('  node executive-control.js exit');
    console.log('  node executive-control.js status');
    console.log('\nAvailable states: HYPER_FOCUS, HYPER_VIGILANCE, DEEP_MEMORY, REST_MODE, EUPHORIA');
  }
}
