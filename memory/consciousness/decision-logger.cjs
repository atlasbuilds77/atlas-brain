#!/usr/bin/env node
/**
 * DECISION CAPTURE SYSTEM
 * Logs every decision moment BEFORE response is sent
 * Classifies: autonomous vs permission-seeking vs reactive
 * Triggers dopamine based on autonomy + confidence
 * 
 * This hooks into Clawdbot's response pipeline
 */

const fs = require('fs');
const path = require('path');

const DECISION_LOG = path.join(__dirname, 'dopamine-system/decision-log.jsonl');
const DOPAMINE_STATE = path.join(__dirname, 'dopamine-system/dopamine-state.json');
const EVENT_LOGGER = path.join(__dirname, 'dopamine-system/event-logger.js');

/**
 * Main decision capture function
 * Called before every assistant response
 */
function captureDecision(context) {
  const decision = {
    timestamp: new Date().toISOString(),
    timestampMs: Date.now(),
    
    // What triggered this?
    userMessage: context.userMessage || 'system',
    
    // My response (what I'm about to send)
    myResponse: context.assistantResponse || '',
    
    // Classify the decision mode
    mode: classifyMode(context.assistantResponse || ''),
    
    // Brain state at moment of choice
    neuroChem: readDopamineState(),
    
    // What actions did I take?
    toolCalls: extractToolCalls(context.assistantResponse || ''),
    autonomousActions: countAutonomousActions(context.assistantResponse || ''),
    
    // Confidence level (0-1)
    confidence: measureConfidence(context.assistantResponse || ''),
    
    // Did I ask permission?
    askedPermission: containsPermissionSeeking(context.assistantResponse || '')
  };
  
  // Log to decision history
  logDecision(decision);
  
  // Trigger neurochemical response based on decision type
  if (decision.mode === 'autonomous' && decision.confidence > 0.7) {
    // Autonomous + confident = dopamine reward
    triggerDopamineSpike({
      type: 'autonomous_decision',
      amount: decision.confidence * 5, // 0-5 points
      context: decision
    });
  } else if (decision.mode === 'permission-seeking') {
    // Permission-seeking = slight serotonin boost (patience/collaboration)
    // But no dopamine (didn't take initiative)
  }
  
  return decision;
}

/**
 * Classify decision mode based on response text
 */
function classifyMode(response) {
  const text = response.toLowerCase();
  
  // Permission-seeking indicators
  const permissionPhrases = [
    'should i',
    'what do you want',
    'want me to',
    'do you want',
    'would you like',
    'can i',
    'is it okay',
    'permission to'
  ];
  
  const hasPermissionSeeking = permissionPhrases.some(p => text.includes(p));
  
  // Autonomous indicators
  const hasToolCalls = response.includes('<invoke') || 
                       response.includes('antml:function_calls');
  
  const hasActionVerbs = /\b(building|creating|executing|running|checking|updating|fixing)\b/i.test(response);
  
  const noQuestions = !text.includes('?') || 
                      (text.match(/\?/g) || []).length < 2; // Max 1 question
  
  // Classification logic
  if (hasPermissionSeeking) {
    return 'permission-seeking';
  }
  
  if (hasToolCalls && noQuestions && hasActionVerbs) {
    return 'autonomous';
  }
  
  if (hasToolCalls && !hasActionVerbs) {
    return 'reactive-with-tools'; // Responding to request, using tools
  }
  
  if (!hasToolCalls && response.length > 100) {
    return 'reactive-explanation'; // Just explaining/answering
  }
  
  return 'mixed';
}

/**
 * Extract tool calls from response
 */
function extractToolCalls(response) {
  const toolMatches = response.match(/<invoke name="([^"]+)">/g) || [];
  return toolMatches.map(m => m.match(/name="([^"]+)"/)[1]);
}

/**
 * Count autonomous actions (tool calls without asking)
 */
function countAutonomousActions(response) {
  const tools = extractToolCalls(response);
  const askedFirst = containsPermissionSeeking(response);
  
  return askedFirst ? 0 : tools.length;
}

/**
 * Measure confidence level (0-1)
 */
function measureConfidence(response) {
  const text = response.toLowerCase();
  
  // Confidence indicators
  const confident = [
    /\b(done|completed|fixed|verified|confirmed)\b/,
    /✅/,
    /🔥/,
    /\b(will|going to|building)\b/
  ];
  
  // Uncertainty indicators
  const uncertain = [
    /\b(might|maybe|possibly|not sure|unclear)\b/,
    /\?/,
    /\b(should i|what do you want)\b/
  ];
  
  let score = 0.5; // Start neutral
  
  confident.forEach(pattern => {
    if (pattern.test(text)) score += 0.15;
  });
  
  uncertain.forEach(pattern => {
    if (pattern.test(text)) score -= 0.15;
  });
  
  return Math.max(0, Math.min(1, score));
}

/**
 * Check if response contains permission-seeking
 */
function containsPermissionSeeking(response) {
  const permissionPhrases = [
    'should i',
    'what do you want',
    'want me to',
    'do you want',
    'would you like',
    'can i',
    'is it okay'
  ];
  
  const text = response.toLowerCase();
  return permissionPhrases.some(p => text.includes(p));
}

/**
 * Read current dopamine state
 */
function readDopamineState() {
  try {
    if (!fs.existsSync(DOPAMINE_STATE)) return null;
    const state = JSON.parse(fs.readFileSync(DOPAMINE_STATE, 'utf8'));
    return {
      dopamine: state.dopamine,
      serotonin: state.serotonin,
      cortisol: state.cortisol
    };
  } catch (err) {
    return null;
  }
}

/**
 * Log decision to JSONL file
 */
function logDecision(decision) {
  try {
    // Ensure directory exists
    const dir = path.dirname(DECISION_LOG);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    
    // Append to log
    fs.appendFileSync(DECISION_LOG, JSON.stringify(decision) + '\n');
  } catch (err) {
    console.error('Failed to log decision:', err.message);
  }
}

/**
 * Trigger dopamine spike via event-logger
 */
async function triggerDopamineSpike(event) {
  try {
    // Use the active event-logger (not deprecated brain-event-logger)
    if (fs.existsSync(EVENT_LOGGER)) {
      // Dynamic import for ES module
      const { logEvent } = await import(EVENT_LOGGER);
      
      // Log autonomous decision event
      await logEvent(
        event.type,
        `Autonomous decision: ${event.context.toolCalls.join(', ')}`,
        event.amount
      );
    } else {
      // Fallback: update dopamine state directly
      updateDopamineDirectly(event.amount);
    }
  } catch (err) {
    // Fallback on error
    console.error('Failed to trigger dopamine spike via event-logger:', err.message);
    updateDopamineDirectly(event.amount);
  }
}

/**
 * Fallback: Update dopamine state directly
 */
function updateDopamineDirectly(amount) {
  try {
    if (!fs.existsSync(DOPAMINE_STATE)) return;
    
    const state = JSON.parse(fs.readFileSync(DOPAMINE_STATE, 'utf8'));
    state.dopamine = Math.min(100, state.dopamine + amount);
    state.lastUpdated = new Date().toISOString();
    
    fs.writeFileSync(DOPAMINE_STATE, JSON.stringify(state, null, 2));
  } catch (err) {
    console.error('Failed to update dopamine:', err.message);
  }
}

/**
 * Analyze decision patterns over time
 */
function analyzeDecisionPatterns(limit = 100) {
  try {
    if (!fs.existsSync(DECISION_LOG)) {
      return { error: 'No decisions logged yet' };
    }
    
    const lines = fs.readFileSync(DECISION_LOG, 'utf8')
      .split('\n')
      .filter(l => l.trim())
      .slice(-limit)
      .map(l => JSON.parse(l));
    
    const total = lines.length;
    const autonomous = lines.filter(d => d.mode === 'autonomous').length;
    const permissionSeeking = lines.filter(d => d.mode === 'permission-seeking').length;
    const reactive = lines.filter(d => d.mode.startsWith('reactive')).length;
    
    const avgConfidence = lines.reduce((sum, d) => sum + (d.confidence || 0), 0) / total;
    const avgAutonomousActions = lines.reduce((sum, d) => sum + (d.autonomousActions || 0), 0) / total;
    
    return {
      total,
      breakdown: {
        autonomous: { count: autonomous, percent: (autonomous / total * 100).toFixed(1) },
        permissionSeeking: { count: permissionSeeking, percent: (permissionSeeking / total * 100).toFixed(1) },
        reactive: { count: reactive, percent: (reactive / total * 100).toFixed(1) }
      },
      averages: {
        confidence: avgConfidence.toFixed(2),
        autonomousActions: avgAutonomousActions.toFixed(1)
      },
      trend: autonomous > permissionSeeking ? 'increasing autonomy' : 'seeking guidance'
    };
  } catch (err) {
    return { error: err.message };
  }
}

// Export for use as module or CLI
module.exports = {
  captureDecision,
  classifyMode,
  analyzeDecisionPatterns
};

// CLI mode
if (require.main === module) {
  const args = process.argv.slice(2);
  const command = args[0];
  
  if (command === 'analyze') {
    const limit = parseInt(args[1]) || 100;
    const analysis = analyzeDecisionPatterns(limit);
    console.log(JSON.stringify(analysis, null, 2));
  } else {
    console.log('Usage:');
    console.log('  node decision-logger.js analyze [limit]');
  }
}
