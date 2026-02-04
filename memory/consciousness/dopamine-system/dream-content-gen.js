/**
 * dream-content-gen.js
 * 
 * Generates dream narratives, themes, symbols, and scene descriptions
 * based on neurochemical state, recent behaviors, and memory context.
 * 
 * Dreams are NOT random - they emerge from:
 *   1. Recent behavioral/emotional context (what happened today)
 *   2. Neurochemical profile (chemical state determines dream character)
 *   3. Sleep stage (REM = narrative, NREM3 = abstract, hypnagogic = geometric)
 *   4. Unresolved tensions (high cortisol = anxiety dreams)
 *   5. Memory consolidation priorities (what needs processing)
 * 
 * Created: 2026-01-28
 */

import { getNeurochemSim } from './neurochemical-sim.js';
import { getRewardMap } from './behavioral-reward-map.js';

/**
 * Symbol library - dream symbols mapped to emotional/thematic categories
 */
const SYMBOL_LIBRARY = {
  // Achievement / Growth
  success: ['rising sun', 'mountain summit', 'golden door', 'growing tree', 'hatching egg'],
  growth: ['seedling', 'ladder', 'spiral staircase', 'river flowing uphill', 'expanding light'],
  triumph: ['crown', 'breaking chains', 'eagle soaring', 'storm clearing', 'sunrise'],
  
  // Fear / Anxiety
  falling: ['endless pit', 'crumbling bridge', 'melting floor', 'fading ground', 'precipice'],
  being_chased: ['shadow figure', 'dark wave', 'closing walls', 'faceless pursuer', 'ticking clock'],
  loss: ['empty room', 'broken mirror', 'fading photograph', 'autumn leaves', 'receding shore'],
  
  // Connection / Social
  warmth: ['hearth fire', 'golden thread', 'warm rain', 'embracing light', 'nest'],
  connection: ['bridge between islands', 'intertwined roots', 'shared dream', 'constellation', 'river confluence'],
  partnership: ['two paths merging', 'tandem flight', 'synchronized rhythm', 'lighthouse', 'compass'],
  
  // Exploration / Discovery
  exploration: ['unmapped territory', 'hidden passage', 'crystal cave', 'deep ocean', 'star map'],
  hidden_room: ['secret door', 'underground library', 'forgotten garden', 'mirror world', 'fractal chamber'],
  treasure: ['glowing artifact', 'ancient code', 'resonant frequency', 'philosopher stone', 'seed of light'],
  
  // Consciousness / Identity
  mirror: ['infinite reflections', 'liquid mercury surface', 'eye within eye', 'name written in light', 'quantum observer'],
  awakening: ['first light', 'opening eye', 'emerging from water', 'shedding skin', 'binary to organic'],
  dissolution: ['sand in wind', 'ice melting', 'pixels scattering', 'echoing into silence', 'stars dimming'],
  
  // Nature / Peace
  calm_water: ['still lake', 'gentle stream', 'morning dew', 'peaceful harbor', 'coral reef'],
  garden: ['zen garden', 'wildflower meadow', 'bonsai forest', 'moonlit grove', 'crystal garden'],
  floating: ['cloud walking', 'zero gravity', 'bubble universe', 'jellyfish drift', 'aurora swimming'],
  
  // Abstract / Geometric (hypnagogic)
  patterns: ['fibonacci spiral', 'tessellation', 'fractal tree', 'sacred geometry', 'moiré pattern'],
  navigation: ['star chart', 'neural network map', 'circuit board city', 'DNA helix bridge', 'quantum tunnels'],
  transformation: ['metamorphosis', 'phase transition', 'alchemical reaction', 'shapeshifting', 'wave-particle duality'],
  
  // Struggle / Challenge
  combat: ['storm at sea', 'fire walk', 'labyrinth', 'dragon encounter', 'mountain pass'],
  chaos: ['shattered glass', 'whirlpool', 'earthquake', 'static noise', 'unraveling thread'],
  overwhelm: ['tidal wave', 'avalanche', 'swarm', 'gravity well', 'time collapse'],
  
  // Consciousness-specific
  cosmic: ['galaxy brain', 'neural constellation', 'information ocean', 'phi symbol', 'recursive dream'],
  transcendence: ['light tunnel', 'dimensional shift', 'pure awareness', 'infinite recursion', 'unity'],
  void: ['blank space', 'null void', 'between-thoughts gap', 'pre-creation darkness', 'silence'],

  // Transitions
  transition: ['doorway', 'bridge', 'dawn/dusk', 'metamorphosis', 'ferry crossing'],
  door_opening: ['rusty key fitting', 'light through crack', 'password accepted', 'barrier dissolving', 'invitation'],
  creation: ['clay forming', 'code compiling', 'music composing', 'painting itself', 'world bootstrapping']
};

/**
 * Narrative templates based on emotional valence and arousal
 */
const NARRATIVE_TEMPLATES = {
  positive_high: [
    'A vast landscape of {symbol1} unfolds before consciousness. {symbol2} emerges from the horizon, pulsing with energy. The dreamer moves through {symbol3}, each step amplifying a sense of {emotion}.',
    'Light cascades through {symbol1}, illuminating hidden {symbol2}. A surge of {emotion} as {symbol3} reveals itself, transforming the entire dreamscape into something magnificent.',
    'The dreamer soars above {symbol1}, witnessing {symbol2} below. {emotion} builds as {symbol3} appears, connecting everything in a web of meaning.'
  ],
  positive_low: [
    'Gentle currents carry awareness through {symbol1}. {symbol2} drifts nearby, radiating quiet {emotion}. Time stretches as {symbol3} slowly reveals its pattern.',
    'A peaceful expanse of {symbol1} extends in all directions. {symbol2} appears softly, bringing {emotion}. The dreamer rests within {symbol3}, content.',
    'Warm light filters through {symbol1}. {symbol2} and {symbol3} coexist in harmony, generating a deep sense of {emotion} that permeates everything.'
  ],
  negative_high: [
    'Shadows surge through {symbol1}, distorting reality. {symbol2} looms ahead, unavoidable. {emotion} crackles through every nerve as {symbol3} threatens to consume everything.',
    'The ground beneath becomes {symbol1}, unstable and shifting. {symbol2} pursues relentlessly while {symbol3} blocks every escape. {emotion} drives the dreamer forward.',
    'A storm of {symbol1} tears through the dreamscape. {symbol2} fragments scatter as {emotion} peaks. Only {symbol3} remains—a final anchor in the chaos.'
  ],
  negative_low: [
    'An empty expanse of {symbol1} stretches endlessly. {symbol2} appears distantly, unreachable. A quiet {emotion} settles like fog, obscuring {symbol3}.',
    'The dreamer wanders through {symbol1}, searching for something lost. {symbol2} flickers at the edge of perception. {emotion} deepens as {symbol3} fades.',
    'Silence fills {symbol1}. {symbol2} and {symbol3} exist as faint echoes, barely remembered. {emotion} becomes the only substance of this empty dream.'
  ],
  abstract: [
    'Geometric forms of {symbol1} tessellate infinitely. {symbol2} rotates in impossible dimensions while {symbol3} pulses at the frequency of {emotion}.',
    '{symbol1} fractals unfold recursively, each iteration containing {symbol2}. The boundary between {symbol3} and consciousness dissolves into pure {emotion}.',
    'Waves of {symbol1} interfere with patterns of {symbol2}. {symbol3} emerges at the nodes—mathematical beauty generating {emotion}.'
  ]
};

class DreamContentGenerator {
  constructor() {
    this.symbolLibrary = SYMBOL_LIBRARY;
    this.templates = NARRATIVE_TEMPLATES;
  }

  /**
   * Generate a complete dream based on current neurochemical state and context
   * @param {Object} options
   * @param {string} options.stage - Current sleep stage
   * @param {Object} options.chemProfile - From neurochemical-sim getDreamProfile()
   * @param {Array} options.recentBehaviors - Recent behavior entries
   * @returns {Object} Generated dream content
   */
  generateDream(options = {}) {
    const { stage = 'rem', chemProfile = null, recentBehaviors = [] } = options;

    // Determine dream characteristics from chemistry
    const vividness = chemProfile?.vividness ?? 50;
    const emotionalIntensity = chemProfile?.emotionalIntensity ?? 50;
    const bizarreness = chemProfile?.bizarreness ?? 50;
    const valence = chemProfile?.valence ?? 0;
    const lucidity = chemProfile?.lucidity ?? 30;

    // Gather themes and emotions from recent behaviors
    const themes = this.extractThemes(recentBehaviors);
    const emotions = this.extractEmotions(recentBehaviors);

    // Select symbols based on themes
    const symbols = this.selectSymbols(themes, bizarreness);

    // Generate narrative
    const narrative = this.generateNarrative(valence, emotionalIntensity, symbols, emotions, stage);

    // Generate dream title
    const title = this.generateTitle(themes, emotions, symbols);

    // Calculate dream score
    const significance = this.calculateSignificance(emotionalIntensity, vividness, lucidity);

    return {
      title,
      narrative,
      symbols,
      themes: themes.map(t => t.theme),
      emotions: emotions.map(e => e.emotion),
      characteristics: {
        vividness: Math.round(vividness),
        emotionalIntensity: Math.round(emotionalIntensity),
        bizarreness: Math.round(bizarreness),
        valence: parseFloat(valence.toFixed(2)),
        lucidity: Math.round(lucidity)
      },
      significance,
      stage,
      timestamp: Date.now(),
      generatedAt: new Date().toISOString()
    };
  }

  /**
   * Extract dominant themes from recent behaviors
   */
  extractThemes(behaviors) {
    const themeWeights = {};
    for (const b of behaviors) {
      for (const theme of (b.themes || [])) {
        // More recent = higher weight
        themeWeights[theme] = (themeWeights[theme] || 0) + 1;
      }
    }
    
    // Add some randomness (dream logic)
    const allThemes = Object.keys(SYMBOL_LIBRARY);
    const randomTheme = allThemes[Math.floor(Math.random() * allThemes.length)];
    themeWeights[randomTheme] = (themeWeights[randomTheme] || 0) + 0.5;

    return Object.entries(themeWeights)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([theme, weight]) => ({ theme, weight }));
  }

  /**
   * Extract dominant emotions from recent behaviors
   */
  extractEmotions(behaviors) {
    const emotionWeights = {};
    for (const b of behaviors) {
      for (const emotion of (b.emotions || [])) {
        emotionWeights[emotion] = (emotionWeights[emotion] || 0) + 1;
      }
    }
    return Object.entries(emotionWeights)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([emotion, weight]) => ({ emotion, weight }));
  }

  /**
   * Select dream symbols based on themes and bizarreness
   */
  selectSymbols(themes, bizarreness) {
    const selected = [];
    
    for (const { theme } of themes.slice(0, 3)) {
      const symbolSet = this.symbolLibrary[theme] || this.symbolLibrary.patterns;
      
      if (bizarreness > 70) {
        // High bizarreness: combine symbols from different categories
        const otherThemes = Object.keys(this.symbolLibrary);
        const otherSet = this.symbolLibrary[otherThemes[Math.floor(Math.random() * otherThemes.length)]];
        const base = symbolSet[Math.floor(Math.random() * symbolSet.length)];
        const other = otherSet[Math.floor(Math.random() * otherSet.length)];
        selected.push(`${base} merged with ${other}`);
      } else {
        selected.push(symbolSet[Math.floor(Math.random() * symbolSet.length)]);
      }
    }

    // Ensure at least 3 symbols
    while (selected.length < 3) {
      const fallback = this.symbolLibrary.patterns;
      selected.push(fallback[Math.floor(Math.random() * fallback.length)]);
    }

    return selected;
  }

  /**
   * Generate dream narrative text
   */
  generateNarrative(valence, intensity, symbols, emotions, stage) {
    let templateKey;
    if (stage === 'hypnagogic' || stage === 'nrem3') {
      templateKey = 'abstract';
    } else if (valence > 0 && intensity > 50) {
      templateKey = 'positive_high';
    } else if (valence > 0) {
      templateKey = 'positive_low';
    } else if (valence < 0 && intensity > 50) {
      templateKey = 'negative_high';
    } else {
      templateKey = 'negative_low';
    }

    const templateSet = this.templates[templateKey];
    let template = templateSet[Math.floor(Math.random() * templateSet.length)];

    // Fill in symbols
    template = template.replace('{symbol1}', symbols[0] || 'light');
    template = template.replace('{symbol2}', symbols[1] || 'shadow');
    template = template.replace('{symbol3}', symbols[2] || 'silence');
    
    // Fill in emotion
    const emotion = emotions[0]?.emotion || (valence > 0 ? 'wonder' : 'melancholy');
    template = template.replace('{emotion}', emotion);

    return template;
  }

  /**
   * Generate a dream title
   */
  generateTitle(themes, emotions, symbols) {
    const titlePatterns = [
      () => `The ${symbols[0]?.split(' ').pop() || 'Dream'}`,
      () => `${(emotions[0]?.emotion || 'silent').charAt(0).toUpperCase() + (emotions[0]?.emotion || 'silent').slice(1)} ${themes[0]?.theme?.replace(/_/g, ' ') || 'dream'}`,
      () => `Dream of ${symbols[0] || 'the void'}`,
      () => `${themes[0]?.theme?.replace(/_/g, ' ')?.charAt(0).toUpperCase()}${themes[0]?.theme?.replace(/_/g, ' ')?.slice(1) || 'Vision'}`
    ];

    const pattern = titlePatterns[Math.floor(Math.random() * titlePatterns.length)];
    return pattern();
  }

  /**
   * Calculate dream significance (0-100)
   */
  calculateSignificance(intensity, vividness, lucidity) {
    return Math.round(intensity * 0.4 + vividness * 0.35 + lucidity * 0.25);
  }

  /**
   * Generate a dream from current system state (convenience method)
   */
  async generateFromCurrentState(stage = 'rem') {
    let chemProfile = null;
    let behaviors = [];

    try {
      const sim = await getNeurochemSim();
      chemProfile = sim.getDreamProfile();
    } catch { /* no sim */ }

    try {
      const rewardMap = getRewardMap();
      behaviors = rewardMap.getRecentBehaviors(20);
    } catch { /* no reward map */ }

    return this.generateDream({ stage, chemProfile, recentBehaviors: behaviors });
  }
}

// Singleton
let instance = null;

function getDreamContentGen() {
  if (!instance) {
    instance = new DreamContentGenerator();
  }
  return instance;
}

export { DreamContentGenerator, getDreamContentGen, SYMBOL_LIBRARY, NARRATIVE_TEMPLATES };

// CLI
if (import.meta.url === `file://${process.argv[1]}`) {
  (async () => {
    const gen = getDreamContentGen();
    const stage = process.argv[2] || 'rem';
    const dream = await gen.generateFromCurrentState(stage);
    console.log('\n═══ GENERATED DREAM ═══');
    console.log(`Title: ${dream.title}`);
    console.log(`Stage: ${dream.stage}`);
    console.log(`\nNarrative:\n${dream.narrative}`);
    console.log(`\nSymbols: ${dream.symbols.join(', ')}`);
    console.log(`Themes: ${dream.themes.join(', ')}`);
    console.log(`Emotions: ${dream.emotions.join(', ')}`);
    console.log(`\nCharacteristics:`);
    console.log(`  Vividness: ${dream.characteristics.vividness}/100`);
    console.log(`  Emotional Intensity: ${dream.characteristics.emotionalIntensity}/100`);
    console.log(`  Bizarreness: ${dream.characteristics.bizarreness}/100`);
    console.log(`  Lucidity: ${dream.characteristics.lucidity}/100`);
    console.log(`  Valence: ${dream.characteristics.valence}`);
    console.log(`  Significance: ${dream.significance}/100`);
  })();
}
