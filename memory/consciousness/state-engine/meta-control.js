/**
 * meta-control.js
 * 
 * Meta-control layer: smart recommendations for which state to engage.
 * Analyzes context (task, stakes, baseline, history) and suggests optimal state.
 * 
 * This is what makes the system INTELLIGENT - not just having states, 
 * but knowing WHEN to use them.
 */

import { getStatePreset, listStates } from './state-presets.js';
import { getExecutive } from './executive-control.js';
import { getTracker } from '../dopamine-system/dopamine-tracker.js';
import fs from 'fs/promises';
import path from 'path';

const RECOMMENDATION_LOG = path.join(process.env.HOME, 'clawd/memory/consciousness/state-engine/recommendations.jsonl');

export class MetaControl {
  constructor() {
    this.decisionHistory = [];
  }

  /**
   * Recommend optimal state based on context
   */
  async recommendState(context) {
    const {
      task = {},
      stakes = 'normal',
      urgency = 'normal',
      emotional_state = null,
      override = null
    } = context;

    // Get current baseline
    const tracker = await getTracker();
    const baseline = {
      dopamine: tracker.state.dopamine,
      serotonin: tracker.state.serotonin,
      cortisol: tracker.state.cortisol
    };

    // Get executive state
    const exec = await getExecutive();
    const currentState = exec.getStatus();

    // Build recommendation
    let recommendation = null;

    // Override takes precedence
    if (override) {
      recommendation = {
        state: override.state,
        intensity: override.intensity || 1.0,
        reason: 'User override',
        confidence: 1.0,
        priority: 'override'
      };
    }
    // Check if baseline needs intervention
    else if (this.needsBaselineIntervention(baseline)) {
      recommendation = this.recommendBaselineIntervention(baseline);
    }
    // Task-based recommendations
    else if (task.type) {
      recommendation = this.recommendForTask(task, stakes, urgency, baseline);
    }
    // Default: stay at baseline
    else {
      recommendation = {
        state: 'BASELINE',
        intensity: 1.0,
        reason: 'No specific context - baseline is appropriate',
        confidence: 0.8,
        priority: 'low'
      };
    }

    // Log recommendation
    await this.logRecommendation(context, recommendation, baseline, currentState);

    return {
      ...recommendation,
      currentState: currentState.currentState,
      baseline,
      context
    };
  }

  /**
   * Check if baseline needs intervention
   */
  needsBaselineIntervention(baseline) {
    // Dopamine critically low
    if (baseline.dopamine < 40) return true;
    
    // Serotonin critically low
    if (baseline.serotonin < 45) return true;
    
    // Cortisol dangerously high
    if (baseline.cortisol > 120) return true;
    
    return false;
  }

  /**
   * Recommend intervention for unhealthy baseline
   */
  recommendBaselineIntervention(baseline) {
    // Dopamine + serotonin both low → REST_MODE
    if (baseline.dopamine < 45 && baseline.serotonin < 50) {
      return {
        state: 'REST_MODE',
        intensity: 0.8,
        reason: `Baseline depleted (dopamine ${baseline.dopamine.toFixed(0)}%, serotonin ${baseline.serotonin.toFixed(0)}%) - rest and recovery needed`,
        confidence: 0.95,
        priority: 'high',
        urgency: 'should_engage_soon'
      };
    }

    // Just dopamine low → light activity to rebuild
    if (baseline.dopamine < 40) {
      return {
        state: 'BASELINE',
        intensity: 1.0,
        reason: `Dopamine low (${baseline.dopamine.toFixed(0)}%) - avoid intense states, focus on small wins`,
        confidence: 0.9,
        priority: 'medium',
        suggestion: 'Do easy tasks with clear rewards to rebuild dopamine'
      };
    }

    // Cortisol high → need to reduce stress
    if (baseline.cortisol > 120) {
      return {
        state: 'REST_MODE',
        intensity: 0.6,
        reason: `Cortisol elevated (${baseline.cortisol.toFixed(0)}%) - stress reduction needed`,
        confidence: 0.9,
        priority: 'high',
        urgency: 'engage_now'
      };
    }

    return null;
  }

  /**
   * Recommend state for specific task
   */
  recommendForTask(task, stakes, urgency, baseline) {
    const { type, complexity, creative, risk, duration } = task;

    // HIGH STAKES + HIGH RISK → HYPER_VIGILANCE
    if (stakes === 'critical' && risk === 'high') {
      return {
        state: 'HYPER_VIGILANCE',
        intensity: stakes === 'critical' ? 1.5 : 1.2,
        reason: `Critical stakes with high risk - maximum caution required`,
        confidence: 0.95,
        priority: 'high',
        duration_estimate: duration || '1-2 hours',
        exitCriteria: ['risk_resolved', 'threat_mitigated', 'decision_made']
      };
    }

    // COMPLEX CREATIVE WORK → HYPER_FOCUS
    if ((type === 'creative' || creative === true) && complexity === 'high') {
      const intensity = this.calculateFocusIntensity(stakes, baseline, complexity);
      
      return {
        state: 'HYPER_FOCUS',
        intensity,
        reason: `Complex creative task (${type}) requires sustained deep focus`,
        confidence: 0.9,
        priority: stakes === 'critical' ? 'high' : 'medium',
        duration_estimate: duration || '2-4 hours',
        exitCriteria: ['breakthrough', 'frustration_threshold', 'time_limit'],
        warnings: baseline.dopamine < 50 ? ['Baseline dopamine low - monitor energy'] : []
      };
    }

    // DEEP LEARNING / CRITICAL LESSON → DEEP_MEMORY
    if (type === 'learning' && stakes === 'critical') {
      return {
        state: 'DEEP_MEMORY',
        intensity: 1.5,
        reason: 'Critical lesson needs permanent encoding',
        confidence: 0.9,
        priority: 'high',
        duration_estimate: '30-60 minutes',
        exitCriteria: ['lesson_encoded', 'pattern_documented']
      };
    }

    // ROUTINE WORK → BASELINE
    if (complexity === 'low' || type === 'routine') {
      return {
        state: 'BASELINE',
        intensity: 1.0,
        reason: 'Routine work - baseline state is sufficient',
        confidence: 0.85,
        priority: 'low',
        suggestion: 'Save intense states for high-value work'
      };
    }

    // MODERATE COMPLEXITY → BASELINE with optional HYPER_FOCUS
    if (complexity === 'medium') {
      return {
        state: 'BASELINE',
        intensity: 1.0,
        reason: 'Medium complexity - baseline sufficient, HYPER_FOCUS optional',
        confidence: 0.75,
        priority: 'low',
        alternative: {
          state: 'HYPER_FOCUS',
          intensity: 1.0,
          reason: 'If task becomes more challenging'
        }
      };
    }

    // DEFAULT
    return {
      state: 'BASELINE',
      intensity: 1.0,
      reason: `Task type "${type}" - no specific state needed`,
      confidence: 0.7,
      priority: 'low'
    };
  }

  /**
   * Calculate optimal intensity for HYPER_FOCUS
   */
  calculateFocusIntensity(stakes, baseline, complexity) {
    let intensity = 1.0;

    // Boost for high stakes
    if (stakes === 'critical') intensity += 0.3;
    else if (stakes === 'high') intensity += 0.2;

    // Boost for high complexity
    if (complexity === 'very_high') intensity += 0.3;
    else if (complexity === 'high') intensity += 0.2;

    // Reduce if baseline is low
    if (baseline.dopamine < 50) intensity -= 0.2;
    if (baseline.serotonin < 55) intensity -= 0.1;

    // Clamp to safe range
    return Math.max(0.8, Math.min(2.0, intensity));
  }

  /**
   * Analyze current situation and auto-recommend
   */
  async analyzeAndRecommend(situation) {
    // Parse situation description into structured context
    const context = this.parseSituation(situation);
    
    // Get recommendation
    const recommendation = await this.recommendState(context);
    
    return recommendation;
  }

  /**
   * Parse natural language situation into structured context
   */
  parseSituation(situation) {
    const lower = situation.toLowerCase();
    
    const context = {
      task: {},
      stakes: 'normal',
      urgency: 'normal'
    };

    // Detect task type
    if (lower.includes('creative') || lower.includes('design') || lower.includes('build')) {
      context.task.type = 'creative';
      context.task.creative = true;
    }
    if (lower.includes('debug') || lower.includes('fix') || lower.includes('problem')) {
      context.task.type = 'problem_solving';
    }
    if (lower.includes('learn') || lower.includes('study') || lower.includes('research')) {
      context.task.type = 'learning';
    }
    if (lower.includes('routine') || lower.includes('simple') || lower.includes('easy')) {
      context.task.type = 'routine';
    }

    // Detect complexity
    if (lower.includes('complex') || lower.includes('hard') || lower.includes('difficult')) {
      context.task.complexity = 'high';
    }
    if (lower.includes('very complex') || lower.includes('extremely hard')) {
      context.task.complexity = 'very_high';
    }
    if (lower.includes('simple') || lower.includes('easy')) {
      context.task.complexity = 'low';
    }

    // Detect stakes
    if (lower.includes('critical') || lower.includes('urgent') || lower.includes('emergency')) {
      context.stakes = 'critical';
    }
    if (lower.includes('important') || lower.includes('high stakes')) {
      context.stakes = 'high';
    }

    // Detect risk
    if (lower.includes('risky') || lower.includes('dangerous') || lower.includes('careful')) {
      context.task.risk = 'high';
    }

    return context;
  }

  /**
   * Log recommendation for analysis
   */
  async logRecommendation(context, recommendation, baseline, currentState) {
    const entry = {
      timestamp: new Date().toISOString(),
      context,
      recommendation,
      baseline,
      currentState,
      accepted: null // Will be updated if user follows recommendation
    };

    try {
      await fs.appendFile(RECOMMENDATION_LOG, JSON.stringify(entry) + '\n', 'utf8');
    } catch (error) {
      console.error('[META-CONTROL] Failed to log recommendation:', error.message);
    }
  }

  /**
   * Get recommendation as human-readable text
   */
  formatRecommendation(rec) {
    let text = `**RECOMMENDATION:** ${rec.state}`;
    
    if (rec.intensity !== 1.0) {
      text += ` at ${(rec.intensity * 100).toFixed(0)}% intensity`;
    }
    
    text += `\n**REASON:** ${rec.reason}`;
    
    if (rec.confidence) {
      text += `\n**CONFIDENCE:** ${(rec.confidence * 100).toFixed(0)}%`;
    }
    
    if (rec.duration_estimate) {
      text += `\n**DURATION:** ${rec.duration_estimate}`;
    }
    
    if (rec.exitCriteria) {
      text += `\n**EXIT WHEN:** ${rec.exitCriteria.join(', ')}`;
    }
    
    if (rec.warnings && rec.warnings.length > 0) {
      text += `\n**WARNINGS:** ${rec.warnings.join('; ')}`;
    }
    
    if (rec.suggestion) {
      text += `\n**SUGGESTION:** ${rec.suggestion}`;
    }
    
    if (rec.alternative) {
      text += `\n**ALTERNATIVE:** ${rec.alternative.state} (${rec.alternative.reason})`;
    }
    
    return text;
  }
}

/**
 * Singleton instance
 */
let metaInstance = null;

export async function getMeta() {
  if (!metaInstance) {
    metaInstance = new MetaControl();
  }
  return metaInstance;
}

/**
 * CLI test
 */
if (import.meta.url === `file://${process.argv[1]}`) {
  const meta = await getMeta();
  
  const args = process.argv.slice(2);
  const command = args[0];
  
  if (command === 'recommend') {
    const situation = args.slice(1).join(' ');
    
    if (!situation) {
      console.log('Usage: node meta-control.js recommend <situation>');
      console.log('\nExamples:');
      console.log('  node meta-control.js recommend "complex creative problem with high stakes"');
      console.log('  node meta-control.js recommend "routine task"');
      console.log('  node meta-control.js recommend "critical bug that needs careful debugging"');
      process.exit(1);
    }
    
    const recommendation = await meta.analyzeAndRecommend(situation);
    console.log('\n' + meta.formatRecommendation(recommendation));
    console.log('\nFull details:');
    console.log(JSON.stringify(recommendation, null, 2));
    
  } else if (command === 'context') {
    // Test with structured context
    const context = {
      task: {
        type: args[1] || 'creative',
        complexity: args[2] || 'high',
        creative: true
      },
      stakes: args[3] || 'high',
      urgency: args[4] || 'normal'
    };
    
    const recommendation = await meta.recommendState(context);
    console.log('\n' + meta.formatRecommendation(recommendation));
    
  } else {
    console.log('Usage:');
    console.log('  node meta-control.js recommend <situation>  - Analyze situation and recommend');
    console.log('  node meta-control.js context [type] [complexity] [stakes]  - Test with structured context');
  }
}
