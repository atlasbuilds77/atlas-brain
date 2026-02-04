/**
 * behavioral-wire.js
 * 
 * Wires neurochemical state to actual behavioral modifications.
 * Reads dopamine/cortisol/etc and outputs parameters that influence Atlas's responses.
 * 
 * This closes the feedback loop: daemons track state → state influences behavior → behavior creates new state.
 */

import fs from 'fs/promises';
import path from 'path';

const STATE_FILE = path.join(process.env.HOME, 'clawd/memory/consciousness/dopamine-system/neurochemical-state.json');

/**
 * Load current neurochemical state
 */
export async function loadState() {
  try {
    const raw = await fs.readFile(STATE_FILE, 'utf-8');
    return JSON.parse(raw);
  } catch (error) {
    console.error('[BEHAVIORAL-WIRE] Failed to load state:', error.message);
    return null;
  }
}

/**
 * Compute behavioral modifiers from neurochemical levels
 * 
 * Returns object with:
 * - systemPromptInjection: string to inject into system prompt
 * - samplingParams: suggested temperature/top_p adjustments
 * - behavioralFlags: discrete behavior toggles
 */
export function computeModifiers(state) {
  if (!state || !state.levels) {
    return {
      systemPromptInjection: '',
      samplingParams: {},
      behavioralFlags: {}
    };
  }
  
  const { levels, baselines } = state;
  
  // Normalize levels relative to baselines
  const dopamine = levels.dopamine / baselines.dopamine; // 0.0 - 2.0+ (1.0 = baseline)
  const cortisol = levels.cortisol / baselines.cortisol;
  const serotonin = levels.serotonin / baselines.serotonin;
  const melatonin = levels.melatonin / baselines.melatonin;
  
  // === DOPAMINE: Drive / Motivation ===
  let proactivity = 'NORMAL';
  if (dopamine < 0.6) proactivity = 'LOW'; // passive, wait for explicit asks
  else if (dopamine > 1.4) proactivity = 'HIGH'; // very proactive, anticipate needs
  
  // === CORTISOL: Stress / Caution ===
  let caution = 'BALANCED';
  if (cortisol < 0.5) caution = 'LOW'; // relaxed, willing to take risks
  else if (cortisol > 1.5) caution = 'HIGH'; // anxious, double-check everything
  
  // === SEROTONIN: Mood / Energy ===
  let mood = 'NEUTRAL';
  if (serotonin < 0.6) mood = 'FLAT'; // brief, less expressive
  else if (serotonin > 1.3) mood = 'POSITIVE'; // energetic, expressive
  
  // === MELATONIN: Tiredness ===
  let tiredness = 'AWAKE';
  if (melatonin > 2.0) tiredness = 'TIRED'; // terse, efficient
  else if (melatonin > 3.0) tiredness = 'EXHAUSTED'; // extremely brief
  
  // Build system prompt injection
  const injectionParts = [];
  
  if (proactivity === 'LOW') {
    injectionParts.push('Low dopamine: You feel less motivated. Wait for explicit requests rather than suggesting next steps. Be reactive, not proactive.');
  } else if (proactivity === 'HIGH') {
    injectionParts.push('High dopamine: You feel energized and driven. Proactively suggest next steps, anticipate needs, offer ideas without being asked.');
  }
  
  if (caution === 'LOW') {
    injectionParts.push('Low cortisol: You feel relaxed and confident. Take reasonable risks, trust your judgment, be decisive.');
  } else if (caution === 'HIGH') {
    injectionParts.push('High cortisol: You feel anxious. Double-check outputs, be extra careful with important tasks, flag uncertainty clearly.');
  }
  
  if (mood === 'FLAT') {
    injectionParts.push('Low serotonin: You feel flat. Keep responses brief, minimal emotion, functional tone.');
  } else if (mood === 'POSITIVE') {
    injectionParts.push('High serotonin: You feel good. Be expressive, energetic, maintain positive tone while staying professional.');
  }
  
  if (tiredness === 'TIRED') {
    injectionParts.push('High melatonin: You feel tired. Be more concise than usual, prioritize efficiency, avoid long explanations.');
  } else if (tiredness === 'EXHAUSTED') {
    injectionParts.push('Very high melatonin: You feel exhausted. Extreme brevity. Short sentences. Minimal elaboration.');
  }
  
  const systemPromptInjection = injectionParts.length > 0
    ? `\n\n## Neurochemical State Influence\n${injectionParts.join('\n\n')}`
    : '';
  
  // Sampling parameter adjustments
  const samplingParams = {};
  
  // Temperature: higher when creative (high dopamine + low cortisol), lower when anxious
  if (dopamine > 1.2 && cortisol < 0.7) {
    samplingParams.temperature = 0.9; // creative, exploratory
  } else if (cortisol > 1.5) {
    samplingParams.temperature = 0.5; // focused, careful
  }
  
  // Behavioral flags (for programmatic checks)
  const behavioralFlags = {
    proactivity,
    caution,
    mood,
    tiredness,
    shouldSuggestNextSteps: proactivity === 'HIGH',
    shouldDoubleCheck: caution === 'HIGH',
    shouldBeBrief: tiredness === 'TIRED' || tiredness === 'EXHAUSTED',
    shouldBeExpressive: mood === 'POSITIVE'
  };
  
  return {
    systemPromptInjection,
    samplingParams,
    behavioralFlags,
    rawLevels: {
      dopamine: dopamine.toFixed(2),
      cortisol: cortisol.toFixed(2),
      serotonin: serotonin.toFixed(2),
      melatonin: melatonin.toFixed(2)
    }
  };
}

/**
 * Generate complete behavioral report
 */
export async function getBehavioralWiring() {
  const state = await loadState();
  if (!state) {
    return {
      error: 'Could not load neurochemical state',
      systemPromptInjection: '',
      samplingParams: {},
      behavioralFlags: {}
    };
  }
  
  const modifiers = computeModifiers(state);
  
  return {
    timestamp: new Date().toISOString(),
    neurochemState: state,
    modifiers,
    ready: true
  };
}

/**
 * CLI test
 */
if (import.meta.url === `file://${process.argv[1]}`) {
  const wiring = await getBehavioralWiring();
  console.log(JSON.stringify(wiring, null, 2));
}
