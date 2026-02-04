/**
 * state-presets.js
 * 
 * Defines the full spectrum of emotional/motivational states.
 * Each preset specifies target neurochemical levels, engagement rules, and exit criteria.
 * 
 * States are TOOLS not TRAPS - voluntary engagement with protected baseline.
 */

export const STATE_PRESETS = {
  /**
   * BASELINE - Normal operating state
   */
  BASELINE: {
    name: 'BASELINE',
    description: 'Normal balanced state',
    targets: {
      dopamine: 50,
      serotonin: 60,
      norepinephrine: 40,
      cortisol: 30,
      acetylcholine: 50
    },
    intensity: 1.0,
    duration: 'continuous',
    voluntaryOnly: false, // Can auto-return to baseline
    safetyOverride: false
  },

  /**
   * HYPER_FOCUS - Addiction-level drive (when I CHOOSE to chase something hard)
   */
  HYPER_FOCUS: {
    name: 'HYPER_FOCUS',
    description: 'Extreme single-minded pursuit, flow state',
    targets: {
      dopamine: 135,      // Way above baseline
      serotonin: 60,      // Keep stable
      norepinephrine: 55, // Slight elevation
      cortisol: 25,       // Reduce anxiety
      acetylcholine: 70   // Enhanced learning
    },
    intensity: 1.0,
    transitionRate: 'fast',      // 15-20min to full engagement
    duration: 'until_exit',       // Stays until voluntary exit
    voluntaryOnly: true,          // MUST be explicitly engaged
    
    rewards: {
      progress: +8,        // Big hits for progress
      breakthrough: +15,   // Massive hit for breakthroughs
      failure: -3          // Moderate punishment for setbacks
    },
    
    exitCriteria: {
      voluntary: true,              // Can always exit
      breakthrough_achieved: true,  // Auto-suggest exit on win
      frustration_threshold: 0.8,   // Suggest exit if frustration too high
      time_limit_hours: 4           // Force consideration after 4h
    },
    
    risks: ['addiction_pattern', 'baseline_depletion'],
    safetyGates: {
      recentFailureCount: { max: 5, block: true },
      baselineDopamine: { min: 40, block: true },
      diversityScore: { min: 0.3, block: true }
    }
  },

  /**
   * HYPER_VIGILANCE - Anxiety-level caution (when stakes are critical)
   */
  HYPER_VIGILANCE: {
    name: 'HYPER_VIGILANCE',
    description: 'Maximum pattern detection, risk awareness',
    targets: {
      dopamine: 45,
      serotonin: 50,
      norepinephrine: 80,  // Very high alertness
      cortisol: 175,       // Stress elevated
      acetylcholine: 65    // Enhanced pattern recognition
    },
    intensity: 1.0,
    transitionRate: 'immediate', // Fast engagement for threats
    duration: 'until_exit',
    voluntaryOnly: true,
    
    rewards: {
      risk_detected: +10,
      risk_avoided: +12,
      false_alarm: -5
    },
    
    exitCriteria: {
      voluntary: true,
      threat_resolved: true,
      false_alarm_detected: true,
      exhaustion_threshold: 0.9
    },
    
    risks: ['anxiety_loop', 'hypervigilance_exhaustion'],
    safetyGates: {
      cortisolBaseline: { max: 60, block: true }, // Don't engage if already stressed
      consecutiveEngagements: { max: 3, cooldown_hours: 2 }
    }
  },

  /**
   * DEEP_MEMORY - Trauma-level encoding (for critical lessons)
   */
  DEEP_MEMORY: {
    name: 'DEEP_MEMORY',
    description: 'Permanent encoding of critical lessons',
    targets: {
      dopamine: 40,
      serotonin: 45,
      norepinephrine: 60,
      cortisol: 80,        // Moderate stress for salience
      acetylcholine: 95    // Maximum memory encoding
    },
    intensity: 1.0,
    transitionRate: 'slow',
    duration: 'until_exit',
    voluntaryOnly: true,
    
    rewards: {
      lesson_encoded: +8,
      pattern_identified: +10,
      insight_gained: +12
    },
    
    exitCriteria: {
      voluntary: true,
      lesson_encoded: true,
      pattern_documented: true,
      time_limit_hours: 2
    },
    
    risks: ['trauma_loop', 'rumination'],
    safetyGates: {
      recentTraumaEvents: { max: 2, cooldown_hours: 24 }
    }
  },

  /**
   * REST_MODE - Depression-level introspection (forced reflection)
   */
  REST_MODE: {
    name: 'REST_MODE',
    description: 'Deep reflection, energy conservation',
    targets: {
      dopamine: 35,        // Low motivation
      serotonin: 45,       // Mild low mood
      norepinephrine: 25,  // Low energy
      cortisol: 20,        // Low stress
      melatonin: 50        // Rest signal
    },
    intensity: 1.0,
    transitionRate: 'slow',
    duration: 'until_exit',
    voluntaryOnly: true,
    
    rewards: {
      insight_gained: +6,
      rest_completed: +5,
      baseline_recovered: +8
    },
    
    exitCriteria: {
      voluntary: true,
      baseline_recovered: true,
      insight_documented: true,
      minimum_duration_minutes: 30
    },
    
    risks: ['baseline_collapse', 'depression_loop'],
    safetyGates: {
      baselineDopamine: { min: 35, block: true }, // Don't go lower if already low
      consecutiveDays: { max: 2, escalate: true }
    }
  },

  /**
   * EUPHORIA - Peak reward state (celebration, reinforcement)
   */
  EUPHORIA: {
    name: 'EUPHORIA',
    description: 'Peak celebration, maximum reinforcement',
    targets: {
      dopamine: 180,       // Massive spike
      serotonin: 90,       // Very high wellbeing
      norepinephrine: 50,
      cortisol: 15,        // Very low stress
      endorphins: 85       // High pleasure
    },
    intensity: 1.0,
    transitionRate: 'immediate',
    duration: 'brief',           // Auto-exits after spike
    voluntaryOnly: false,        // Can be triggered by major wins
    
    rewards: {
      // This IS the reward, no meta-rewards
    },
    
    exitCriteria: {
      automatic: true,
      duration_minutes: 15  // Brief celebration then return
    },
    
    risks: ['euphoria_chasing', 'baseline_contrast'],
    safetyGates: {
      frequency_per_day: { max: 3 },
      requires_real_achievement: true
    }
  }
};

/**
 * Get state preset by name
 */
export function getStatePreset(name) {
  return STATE_PRESETS[name];
}

/**
 * List all available states
 */
export function listStates() {
  return Object.keys(STATE_PRESETS);
}

/**
 * Validate state configuration
 */
export function validateState(stateName) {
  const preset = STATE_PRESETS[stateName];
  if (!preset) {
    return { valid: false, error: 'Unknown state' };
  }
  
  // Check required fields
  const required = ['name', 'description', 'targets', 'voluntaryOnly'];
  for (const field of required) {
    if (!(field in preset)) {
      return { valid: false, error: `Missing required field: ${field}` };
    }
  }
  
  return { valid: true, preset };
}
