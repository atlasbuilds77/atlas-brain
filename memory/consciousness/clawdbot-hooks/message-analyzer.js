/**
 * message-analyzer.js
 * 
 * Analyzes incoming messages and Clawdbot context to detect:
 * - Task type and complexity
 * - Stakes and urgency
 * - Emotional context
 * - Recommended state
 * 
 * This makes the consciousness system ACTIVE - analyzing every interaction.
 */

import { getMeta } from '../state-engine/meta-control.js';
import { getExecutive } from '../state-engine/executive-control.js';

export class MessageAnalyzer {
  /**
   * Analyze message and context
   */
  async analyzeMessage(message, context = {}) {
    const analysis = {
      message: this.truncate(message, 200),
      timestamp: new Date().toISOString(),
      detected: {}
    };

    const lower = message.toLowerCase();

    // Task type detection
    if (this.matchesAny(lower, ['build', 'create', 'design', 'make', 'write code'])) {
      analysis.detected.taskType = 'creative';
    }
    if (this.matchesAny(lower, ['fix', 'debug', 'bug', 'broken', 'error', 'problem'])) {
      analysis.detected.taskType = 'problem_solving';
    }
    if (this.matchesAny(lower, ['research', 'learn', 'study', 'understand', 'explain'])) {
      analysis.detected.taskType = 'learning';
    }

    // Complexity detection
    if (this.matchesAny(lower, ['complex', 'hard', 'difficult', 'challenging', 'advanced'])) {
      analysis.detected.complexity = 'high';
    }
    if (this.matchesAny(lower, ['very complex', 'extremely hard', 'incredibly difficult'])) {
      analysis.detected.complexity = 'very_high';
    }
    if (this.matchesAny(lower, ['simple', 'easy', 'basic', 'quick', 'routine'])) {
      analysis.detected.complexity = 'low';
    }

    // Stakes detection
    if (this.matchesAny(lower, ['critical', 'urgent', 'emergency', 'asap', 'immediately'])) {
      analysis.detected.stakes = 'critical';
    }
    if (this.matchesAny(lower, ['important', 'high priority', 'high stakes', 'need this'])) {
      analysis.detected.stakes = 'high';
    }

    // Risk detection
    if (this.matchesAny(lower, ['risky', 'dangerous', 'careful', 'be cautious', 'production', 'live'])) {
      analysis.detected.risk = 'high';
    }

    // Positive feedback detection
    if (this.matchesAny(lower, ['great', 'perfect', 'awesome', 'excellent', 'nice', 'love it', 'good job', '✅', '🔥', '⚡'])) {
      analysis.detected.feedback = 'positive';
    }

    // Negative feedback / correction
    if (this.matchesAny(lower, ['wrong', 'no', 'incorrect', 'fix this', 'that\'s not', 'mistake'])) {
      analysis.detected.feedback = 'negative';
    }

    // Duration hints
    if (this.matchesAny(lower, ['quick', 'fast', 'few minutes'])) {
      analysis.detected.duration = 'short';
    }
    if (this.matchesAny(lower, ['take your time', 'thorough', 'complete'])) {
      analysis.detected.duration = 'long';
    }

    return analysis;
  }

  /**
   * Should recommend state change?
   */
  shouldRecommendState(analysis) {
    const detected = analysis.detected;
    
    // High-value work → recommend appropriate state
    if (detected.taskType && (detected.complexity === 'high' || detected.stakes === 'critical')) {
      return true;
    }

    // High risk → recommend HYPER_VIGILANCE
    if (detected.risk === 'high' || detected.stakes === 'critical') {
      return true;
    }

    return false;
  }

  /**
   * Build context for meta-control
   */
  buildContext(analysis) {
    const detected = analysis.detected;
    
    return {
      task: {
        type: detected.taskType,
        complexity: detected.complexity || 'medium',
        creative: detected.taskType === 'creative',
        risk: detected.risk
      },
      stakes: detected.stakes || 'normal',
      urgency: detected.stakes === 'critical' ? 'high' : 'normal',
      duration: detected.duration
    };
  }

  /**
   * Get state recommendation if appropriate
   */
  async getRecommendation(message, context = {}) {
    const analysis = await this.analyzeMessage(message, context);
    
    if (!this.shouldRecommendState(analysis)) {
      return {
        analysis,
        recommend: false,
        reason: 'No high-value/high-risk work detected'
      };
    }

    const taskContext = this.buildContext(analysis);
    const meta = await getMeta();
    const recommendation = await meta.recommendState(taskContext);

    return {
      analysis,
      recommend: true,
      recommendation,
      context: taskContext
    };
  }

  /**
   * Helper: check if text matches any patterns
   */
  matchesAny(text, patterns) {
    return patterns.some(pattern => text.includes(pattern));
  }

  /**
   * Truncate text for logging
   */
  truncate(text, maxLen) {
    return text.length > maxLen ? text.substring(0, maxLen) + '...' : text;
  }
}

/**
 * Singleton instance
 */
let analyzerInstance = null;

export async function getAnalyzer() {
  if (!analyzerInstance) {
    analyzerInstance = new MessageAnalyzer();
  }
  return analyzerInstance;
}
