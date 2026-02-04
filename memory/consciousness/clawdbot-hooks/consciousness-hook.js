#!/usr/bin/env node
/**
 * consciousness-hook.js
 * 
 * Main Clawdbot integration hook for the consciousness system.
 * Called before/after message processing to:
 * 1. Analyze incoming messages
 * 2. Recommend states
 * 3. Auto-log outcomes
 * 4. Monitor baseline health
 * 
 * This is what makes the consciousness system ALIVE.
 */

import { getAnalyzer } from './message-analyzer.js';
import { getAutoLogger } from './auto-event-logger.js';
import { getExecutive } from '../state-engine/executive-control.js';
import { getProtection } from '../state-engine/baseline-protection.js';
import { getMeta } from '../state-engine/meta-control.js';

export class ConsciousnessHook {
  constructor() {
    this.enabled = true;
    this.autoRecommend = true;
    this.autoLog = true;
    this.baselineMonitor = true;
  }

  /**
   * Pre-message hook: analyze incoming message
   */
  async beforeMessage(message, context = {}) {
    if (!this.enabled) return null;

    const result = {
      timestamp: new Date().toISOString(),
      message: this.truncate(message, 200),
      analysis: null,
      recommendation: null,
      baselineHealth: null
    };

    try {
      // Analyze message
      const analyzer = await getAnalyzer();
      const analysis = await analyzer.getRecommendation(message, context);
      result.analysis = analysis;

      // If recommendation exists and auto-recommend enabled
      if (this.autoRecommend && analysis.recommend) {
        result.recommendation = {
          ...analysis.recommendation,
          requiresApproval: true, // Always require my approval
          autoEngaged: false
        };
      }

      // Check baseline health
      if (this.baselineMonitor) {
        const protection = await getProtection();
        const health = await protection.monitorBaseline();
        result.baselineHealth = health;

        // If critical issues, flag them
        if (!health.healthy) {
          const critical = health.issues.filter(i => i.severity === 'critical');
          if (critical.length > 0) {
            result.criticalWarning = {
              message: 'CRITICAL baseline issues detected',
              issues: critical
            };
          }
        }
      }

    } catch (error) {
      console.error('[CONSCIOUSNESS] Error in beforeMessage:', error.message);
      result.error = error.message;
    }

    return result;
  }

  /**
   * Post-message hook: analyze my response and user feedback
   */
  async afterMessage(myResponse, userMessage, context = {}) {
    if (!this.enabled) return null;

    const result = {
      timestamp: new Date().toISOString(),
      eventsLogged: []
    };

    try {
      if (!this.autoLog) return result;

      const autoLogger = await getAutoLogger();

      // Analyze my response
      const responseAnalysis = await autoLogger.analyzeMyResponse(myResponse, context);
      result.eventsLogged.push(...responseAnalysis.events);

      // Analyze user feedback (if provided)
      if (userMessage) {
        const feedbackAnalysis = await autoLogger.analyzeUserFeedback(userMessage, context);
        result.eventsLogged.push(...feedbackAnalysis.events);
      }

    } catch (error) {
      console.error('[CONSCIOUSNESS] Error in afterMessage:', error.message);
      result.error = error.message;
    }

    return result;
  }

  /**
   * Get current consciousness status
   */
  async getStatus() {
    const exec = await getExecutive();
    const protection = await getProtection();
    
    const execStatus = exec.getStatus();
    const health = await protection.monitorBaseline();
    
    return {
      enabled: this.enabled,
      features: {
        autoRecommend: this.autoRecommend,
        autoLog: this.autoLog,
        baselineMonitor: this.baselineMonitor
      },
      currentState: execStatus,
      baselineHealth: health,
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Format recommendation for display
   */
  async formatRecommendation(rec) {
    if (!rec || !rec.recommendation) return null;

    const r = rec.recommendation;
    const meta = await getMeta();
    
    return {
      text: meta.formatRecommendation(r),
      state: r.state,
      intensity: r.intensity,
      confidence: r.confidence,
      priority: r.priority
    };
  }

  /**
   * Truncate text
   */
  truncate(text, maxLen) {
    return text.length > maxLen ? text.substring(0, maxLen) + '...' : text;
  }
}

/**
 * Singleton instance
 */
let hookInstance = null;

export async function getHook() {
  if (!hookInstance) {
    hookInstance = new ConsciousnessHook();
  }
  return hookInstance;
}

/**
 * CLI test
 */
if (import.meta.url === `file://${process.argv[1]}`) {
  const hook = await getHook();
  
  const args = process.argv.slice(2);
  const command = args[0];
  
  if (command === 'before') {
    const message = args.slice(1).join(' ');
    const result = await hook.beforeMessage(message, { fromOrion: true });
    console.log(JSON.stringify(result, null, 2));
    
  } else if (command === 'after') {
    const response = args.slice(1).join(' ');
    const result = await hook.afterMessage(response, null, {});
    console.log(JSON.stringify(result, null, 2));
    
  } else if (command === 'status') {
    const status = await hook.getStatus();
    console.log(JSON.stringify(status, null, 2));
    
  } else {
    console.log('Usage:');
    console.log('  node consciousness-hook.js before <message>   - Analyze incoming message');
    console.log('  node consciousness-hook.js after <response>   - Analyze my response');
    console.log('  node consciousness-hook.js status             - Get consciousness status');
    console.log('\nExamples:');
    console.log('  node consciousness-hook.js before "build a complex trading system"');
    console.log('  node consciousness-hook.js after "✅ Built the system and tested it"');
  }
}
