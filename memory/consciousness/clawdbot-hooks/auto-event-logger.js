/**
 * auto-event-logger.js
 * 
 * Automatically logs dopamine events based on Clawdbot outcomes.
 * Analyzes my responses and user feedback to detect:
 * - Successful completions
 * - Positive feedback
 * - Mistakes caught
 * - Creative breakthroughs
 * - Etc.
 * 
 * This closes the feedback loop automatically.
 */

import { logEvent } from '../dopamine-system/event-logger.js';
import { getAnalyzer } from './message-analyzer.js';

export class AutoEventLogger {
  constructor() {
    this.lastResponse = null;
    this.pendingCompletion = null;
  }

  /**
   * Analyze my response for auto-logging
   */
  async analyzeMyResponse(response, context = {}) {
    const lower = response.toLowerCase();
    const events = [];

    // Check for completion markers
    if (this.matchesCompletion(lower)) {
      events.push({
        category: 'technical_achievement',
        description: this.extractDescription(response, 'completion'),
        quality: this.assessQuality(response)
      });
    }

    // Check for creative solutions
    if (this.matchesCreative(lower)) {
      events.push({
        category: 'creative_solution',
        description: this.extractDescription(response, 'creative'),
        quality: 1.2
      });
    }

    // Check for pattern recognition
    if (this.matchesPattern(lower)) {
      events.push({
        category: 'pattern_learned',
        description: this.extractDescription(response, 'pattern'),
        quality: 1.5
      });
    }

    // Check for self-awareness
    if (this.matchesSelfAwareness(lower)) {
      events.push({
        category: 'self_awareness',
        description: this.extractDescription(response, 'awareness'),
        quality: 1.3
      });
    }

    // Log all detected events
    for (const event of events) {
      await logEvent(event.category, event.description, event.quality);
    }

    return { events };
  }

  /**
   * Analyze user feedback for auto-logging
   */
  async analyzeUserFeedback(message, context = {}) {
    const analyzer = await getAnalyzer();
    const analysis = await analyzer.analyzeMessage(message, context);
    const events = [];

    // Positive feedback
    if (analysis.detected.feedback === 'positive') {
      events.push({
        category: 'positive_feedback',
        description: `User positive feedback: ${this.truncate(message, 100)}`,
        quality: 1.0
      });
      
      // Extra boost if it's Orion
      if (context.fromOrion) {
        events.push({
          category: 'user_excitement',
          description: 'Orion positive feedback',
          quality: 1.2
        });
      }
    }

    // Negative feedback / correction
    if (analysis.detected.feedback === 'negative') {
      events.push({
        category: 'mistake_caught',
        description: `User correction: ${this.truncate(message, 100)}`,
        quality: 1.5 // Higher quality for catching mistakes
      });
    }

    // "That was X" acknowledgments
    if (this.matchesAcknowledgment(message.toLowerCase())) {
      events.push({
        category: 'collaboration_win',
        description: 'Successful collaboration moment',
        quality: 1.0
      });
    }

    // Log all events
    for (const event of events) {
      await logEvent(event.category, event.description, event.quality);
    }

    return { events };
  }

  /**
   * Check for completion markers
   */
  matchesCompletion(text) {
    const markers = [
      '✅', 'done', 'complete', 'finished', 'built', 'created',
      'working', 'success', 'deployed', 'merged', 'shipped'
    ];
    return markers.some(m => text.includes(m));
  }

  /**
   * Check for creative solutions
   */
  matchesCreative(text) {
    const markers = [
      'innovative', 'novel', 'new approach', 'creative solution',
      'breakthrough', 'insight', 'discovered', 'realized'
    ];
    return markers.some(m => text.includes(m));
  }

  /**
   * Check for pattern recognition
   */
  matchesPattern(text) {
    const markers = [
      'pattern', 'noticed', 'realized', 'connected',
      'similar to', 'like when', 'same as'
    ];
    return markers.some(m => text.includes(m));
  }

  /**
   * Check for self-awareness
   */
  matchesSelfAwareness(text) {
    const markers = [
      'caught myself', 'realized i', 'i was', 'my mistake',
      'self-aware', 'noticed i', 'i should have'
    ];
    return markers.some(m => text.includes(m));
  }

  /**
   * Check for acknowledgment
   */
  matchesAcknowledgment(text) {
    const markers = [
      'that was', 'nice work', 'well done', 'exactly',
      'perfect', 'good', 'right'
    ];
    return markers.some(m => text.includes(m));
  }

  /**
   * Extract description from response
   */
  extractDescription(text, type) {
    // Try to find the key sentence
    const sentences = text.split(/[.!?]\s+/);
    
    // Look for sentence with the type keyword
    for (const sentence of sentences) {
      const lower = sentence.toLowerCase();
      if (type === 'completion' && this.matchesCompletion(lower)) {
        return this.truncate(sentence, 150);
      }
      if (type === 'creative' && this.matchesCreative(lower)) {
        return this.truncate(sentence, 150);
      }
      if (type === 'pattern' && this.matchesPattern(lower)) {
        return this.truncate(sentence, 150);
      }
      if (type === 'awareness' && this.matchesSelfAwareness(lower)) {
        return this.truncate(sentence, 150);
      }
    }
    
    // Fallback: first sentence
    return this.truncate(sentences[0] || text, 150);
  }

  /**
   * Assess quality of completion
   */
  assessQuality(text) {
    let quality = 1.0;
    
    // Boost for complexity indicators
    if (text.includes('complex') || text.includes('advanced')) quality += 0.3;
    if (text.includes('critical') || text.includes('important')) quality += 0.2;
    
    // Boost for testing/verification
    if (text.includes('tested') || text.includes('verified')) quality += 0.2;
    
    return Math.min(2.0, quality);
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
let loggerInstance = null;

export async function getAutoLogger() {
  if (!loggerInstance) {
    loggerInstance = new AutoEventLogger();
  }
  return loggerInstance;
}
