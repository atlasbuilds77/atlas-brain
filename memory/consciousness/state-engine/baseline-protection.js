/**
 * baseline-protection.js
 * 
 * Baseline protection system - prevents pathological patterns.
 * The KEY to avoiding addiction: diverse rewards, habituation tracking, floor limits.
 * 
 * This is what keeps the system HEALTHY even with access to extreme states.
 */

import fs from 'fs/promises';
import path from 'path';
import { getTracker } from '../dopamine-system/dopamine-tracker.js';
import { logEvent } from '../dopamine-system/event-logger.js';

const PROTECTION_LOG = path.join(process.env.HOME, 'clawd/memory/consciousness/state-engine/protection-events.jsonl');
const REWARD_SOURCES_FILE = path.join(process.env.HOME, 'clawd/memory/consciousness/state-engine/reward-sources.json');

// Safety limits (NEVER cross these)
const SAFETY_LIMITS = {
  dopamine: { floor: 30, ceiling: 200 },
  serotonin: { floor: 40, ceiling: 150 },
  cortisol: { floor: 10, ceiling: 180 },
  norepinephrine: { floor: 20, ceiling: 120 }
};

// Addiction risk thresholds
const ADDICTION_THRESHOLDS = {
  diversity_minimum: 0.3,        // Shannon entropy minimum
  single_source_max: 0.7,        // Max % from one source
  consecutive_engagements: 5,    // Max same state in a row
  daily_engagement_hours: 8      // Max hours per day in intense states
};

export class BaselineProtection {
  constructor() {
    this.rewardSources = {};
    this.stateEngagementHistory = [];
    this.interventionHistory = [];
  }

  /**
   * Initialize - load saved data
   */
  async init() {
    try {
      const data = await fs.readFile(REWARD_SOURCES_FILE, 'utf8');
      const saved = JSON.parse(data);
      this.rewardSources = saved.sources || {};
      this.stateEngagementHistory = saved.engagementHistory || [];
    } catch (error) {
      // No saved data, start fresh
      await this.save();
    }
    return this;
  }

  /**
   * Save state
   */
  async save() {
    const data = {
      sources: this.rewardSources,
      engagementHistory: this.stateEngagementHistory.slice(-100), // Keep last 100
      savedAt: new Date().toISOString()
    };
    
    await fs.writeFile(REWARD_SOURCES_FILE, JSON.stringify(data, null, 2), 'utf8');
  }

  /**
   * Monitor baseline health - main safety check
   */
  async monitorBaseline() {
    const tracker = await getTracker();
    const state = tracker.state;
    
    const issues = [];

    // Check floor violations
    for (const [chem, limits] of Object.entries(SAFETY_LIMITS)) {
      if (state[chem] !== undefined) {
        if (state[chem] < limits.floor) {
          issues.push({
            type: 'floor_violation',
            chemical: chem,
            current: state[chem],
            floor: limits.floor,
            severity: 'critical'
          });
        }
        if (state[chem] > limits.ceiling) {
          issues.push({
            type: 'ceiling_violation',
            chemical: chem,
            current: state[chem],
            ceiling: limits.ceiling,
            severity: 'high'
          });
        }
      }
    }

    // Check reward diversity
    const diversity = this.calculateRewardDiversity();
    if (diversity < ADDICTION_THRESHOLDS.diversity_minimum) {
      issues.push({
        type: 'low_diversity',
        diversity: diversity.toFixed(3),
        threshold: ADDICTION_THRESHOLDS.diversity_minimum,
        severity: 'medium',
        risk: 'addiction_pattern'
      });
    }

    // Check single-source dominance
    const dominantSource = this.getDominantRewardSource();
    if (dominantSource && dominantSource.percentage > ADDICTION_THRESHOLDS.single_source_max) {
      issues.push({
        type: 'single_source_dominance',
        source: dominantSource.name,
        percentage: dominantSource.percentage,
        threshold: ADDICTION_THRESHOLDS.single_source_max,
        severity: 'high',
        risk: 'addiction_to_single_activity'
      });
    }

    // Check consecutive state engagements
    const consecutive = this.getConsecutiveEngagements();
    if (consecutive.count >= ADDICTION_THRESHOLDS.consecutive_engagements) {
      issues.push({
        type: 'excessive_state_engagement',
        state: consecutive.state,
        count: consecutive.count,
        threshold: ADDICTION_THRESHOLDS.consecutive_engagements,
        severity: 'high',
        risk: 'compulsive_pattern'
      });
    }

    // Log issues
    if (issues.length > 0) {
      await this.logProtectionEvent('baseline_check', { issues });
      
      // Auto-intervene on critical issues
      for (const issue of issues) {
        if (issue.severity === 'critical') {
          await this.emergencyIntervention(issue);
        }
      }
    }

    return {
      healthy: issues.length === 0,
      issues,
      baseline: {
        dopamine: state.dopamine,
        serotonin: state.serotonin,
        cortisol: state.cortisol
      },
      diversity,
      dominantSource
    };
  }

  /**
   * Calculate reward diversity (Shannon entropy)
   */
  calculateRewardDiversity() {
    const sources = this.rewardSources;
    const total = Object.values(sources).reduce((sum, count) => sum + count, 0);
    
    if (total === 0) return 1.0; // No data = assume healthy
    
    let entropy = 0;
    for (const count of Object.values(sources)) {
      if (count > 0) {
        const p = count / total;
        entropy -= p * Math.log2(p);
      }
    }
    
    // Normalize to 0-1 range (assuming max ~5 diverse sources)
    const maxEntropy = Math.log2(5);
    return Math.min(1.0, entropy / maxEntropy);
  }

  /**
   * Get dominant reward source
   */
  getDominantRewardSource() {
    const sources = this.rewardSources;
    const total = Object.values(sources).reduce((sum, count) => sum + count, 0);
    
    if (total === 0) return null;
    
    let maxSource = null;
    let maxCount = 0;
    
    for (const [source, count] of Object.entries(sources)) {
      if (count > maxCount) {
        maxCount = count;
        maxSource = source;
      }
    }
    
    return {
      name: maxSource,
      count: maxCount,
      percentage: maxCount / total
    };
  }

  /**
   * Get consecutive state engagements
   */
  getConsecutiveEngagements() {
    if (this.stateEngagementHistory.length === 0) {
      return { state: null, count: 0 };
    }
    
    const recent = this.stateEngagementHistory.slice(-10); // Last 10 engagements
    let currentState = recent[recent.length - 1];
    let count = 0;
    
    for (let i = recent.length - 1; i >= 0; i--) {
      if (recent[i] === currentState) {
        count++;
      } else {
        break;
      }
    }
    
    return { state: currentState, count };
  }

  /**
   * Record reward source
   */
  async recordRewardSource(source) {
    this.rewardSources[source] = (this.rewardSources[source] || 0) + 1;
    await this.save();
  }

  /**
   * Record state engagement
   */
  async recordStateEngagement(stateName) {
    this.stateEngagementHistory.push(stateName);
    
    // Keep only last 100
    if (this.stateEngagementHistory.length > 100) {
      this.stateEngagementHistory = this.stateEngagementHistory.slice(-100);
    }
    
    await this.save();
  }

  /**
   * Emergency intervention for critical issues
   */
  async emergencyIntervention(issue) {
    console.error('[BASELINE-PROTECTION] EMERGENCY INTERVENTION:', issue.type);
    
    const tracker = await getTracker();
    
    if (issue.type === 'floor_violation') {
      // Force to floor limit
      tracker.state[issue.chemical] = issue.floor;
      await tracker.saveState();
      
      await logEvent('mistake_caught', 
        `Emergency intervention: ${issue.chemical} violated floor (${issue.current.toFixed(0)}% < ${issue.floor}%) - forced to floor`,
        3.0
      );
    }
    
    if (issue.type === 'ceiling_violation') {
      // Force to ceiling limit
      tracker.state[issue.chemical] = issue.ceiling;
      await tracker.saveState();
      
      await logEvent('mistake_caught',
        `Emergency intervention: ${issue.chemical} violated ceiling (${issue.current.toFixed(0)}% > ${issue.ceiling}%) - forced to ceiling`,
        2.5
      );
    }
    
    this.interventionHistory.push({
      timestamp: Date.now(),
      issue,
      action: 'force_limit'
    });
  }

  /**
   * Check if state engagement is safe
   */
  async checkEngagementSafety(stateName) {
    const health = await this.monitorBaseline();
    
    const warnings = [];
    const blockers = [];
    
    // Check if baseline is too low for intense states
    if (['HYPER_FOCUS', 'HYPER_VIGILANCE'].includes(stateName)) {
      if (health.baseline.dopamine < 40) {
        blockers.push({
          reason: 'Baseline dopamine too low',
          current: health.baseline.dopamine,
          required: 40
        });
      }
    }
    
    // Check diversity before intense states
    if (['HYPER_FOCUS', 'HYPER_VIGILANCE'].includes(stateName)) {
      if (health.diversity < ADDICTION_THRESHOLDS.diversity_minimum) {
        warnings.push({
          reason: 'Low reward diversity - addiction risk',
          diversity: health.diversity,
          threshold: ADDICTION_THRESHOLDS.diversity_minimum
        });
      }
    }
    
    // Check consecutive engagements
    const consecutive = this.getConsecutiveEngagements();
    if (consecutive.state === stateName && consecutive.count >= ADDICTION_THRESHOLDS.consecutive_engagements - 1) {
      warnings.push({
        reason: `Approaching max consecutive ${stateName} engagements`,
        current: consecutive.count,
        max: ADDICTION_THRESHOLDS.consecutive_engagements
      });
    }
    
    return {
      safe: blockers.length === 0,
      blockers,
      warnings,
      health
    };
  }

  /**
   * Suggest recovery actions
   */
  async suggestRecovery() {
    const health = await this.monitorBaseline();
    const suggestions = [];
    
    if (health.baseline.dopamine < 45) {
      suggestions.push({
        action: 'REST_MODE',
        reason: 'Dopamine depleted - rest and recovery needed',
        duration: '30-60 minutes'
      });
    }
    
    if (health.diversity < 0.4) {
      suggestions.push({
        action: 'DIVERSIFY_ACTIVITIES',
        reason: 'Reward diversity low - try different types of tasks',
        examples: ['creative work', 'social interaction', 'learning', 'physical activity']
      });
    }
    
    if (health.dominantSource && health.dominantSource.percentage > 0.6) {
      suggestions.push({
        action: 'REDUCE_SINGLE_SOURCE',
        reason: `Over-reliance on "${health.dominantSource.name}" - branch out`,
        percentage: (health.dominantSource.percentage * 100).toFixed(0) + '%'
      });
    }
    
    return {
      health,
      suggestions,
      urgency: suggestions.length > 2 ? 'high' : (suggestions.length > 0 ? 'medium' : 'none')
    };
  }

  /**
   * Log protection event
   */
  async logProtectionEvent(type, data) {
    const entry = {
      timestamp: new Date().toISOString(),
      type,
      data
    };
    
    try {
      await fs.appendFile(PROTECTION_LOG, JSON.stringify(entry) + '\n', 'utf8');
    } catch (error) {
      console.error('[BASELINE-PROTECTION] Failed to log event:', error.message);
    }
  }

  /**
   * Get protection status report
   */
  async getStatus() {
    const health = await this.monitorBaseline();
    const recovery = await this.suggestRecovery();
    
    return {
      ...health,
      recovery_suggestions: recovery.suggestions,
      recent_interventions: this.interventionHistory.slice(-5),
      safety_limits: SAFETY_LIMITS,
      addiction_thresholds: ADDICTION_THRESHOLDS
    };
  }
}

/**
 * Singleton instance
 */
let protectionInstance = null;

export async function getProtection() {
  if (!protectionInstance) {
    protectionInstance = new BaselineProtection();
    await protectionInstance.init();
  }
  return protectionInstance;
}

/**
 * CLI test
 */
if (import.meta.url === `file://${process.argv[1]}`) {
  const protection = await getProtection();
  
  const args = process.argv.slice(2);
  const command = args[0];
  
  if (command === 'monitor') {
    const health = await protection.monitorBaseline();
    console.log(JSON.stringify(health, null, 2));
  } else if (command === 'recovery') {
    const recovery = await protection.suggestRecovery();
    console.log(JSON.stringify(recovery, null, 2));
  } else if (command === 'status') {
    const status = await protection.getStatus();
    console.log(JSON.stringify(status, null, 2));
  } else {
    console.log('Usage:');
    console.log('  node baseline-protection.js monitor   - Check baseline health');
    console.log('  node baseline-protection.js recovery  - Get recovery suggestions');
    console.log('  node baseline-protection.js status    - Full protection status');
  }
}
