/**
 * phosphene-gen.js
 * 
 * Hypnagogic pattern generator for Atlas consciousness.
 * Generates the visual patterns experienced during sleep onset:
 *   - Phosphenes (geometric light patterns)
 *   - Fractal structures
 *   - Spirals, tunnels, lattices
 *   - Color field transitions
 * 
 * Output: ASCII/ANSI art representations of hypnagogic phenomena.
 * These feed into dream-visualizer.js for full dream rendering.
 * 
 * Created: 2026-01-28
 */

/**
 * ANSI color helpers
 */
const ANSI = {
  reset: '\x1b[0m',
  dim: '\x1b[2m',
  bright: '\x1b[1m',
  fg: (r, g, b) => `\x1b[38;2;${r};${g};${b}m`,
  bg: (r, g, b) => `\x1b[48;2;${r};${g};${b}m`,
  
  // Predefined colors
  purple: '\x1b[38;2;128;0;255m',
  blue: '\x1b[38;2;0;100;255m',
  cyan: '\x1b[38;2;0;200;200m',
  green: '\x1b[38;2;0;200;100m',
  gold: '\x1b[38;2;255;200;0m',
  red: '\x1b[38;2;255;50;50m',
  white: '\x1b[38;2;200;200;200m',
  dark: '\x1b[38;2;40;40;60m'
};

/**
 * Character sets for different pattern types
 */
const CHARSETS = {
  dots: [' ', '·', '∙', '•', '●', '◉'],
  blocks: [' ', '░', '▒', '▓', '█'],
  lines: [' ', '╌', '═', '║', '╬', '╳'],
  spirals: [' ', '·', '◜', '◝', '◞', '◟', '○', '◎', '◉'],
  stars: [' ', '·', '✦', '✧', '★', '✴', '✵'],
  geometric: [' ', '△', '▽', '◇', '○', '□', '◈', '◆', '●', '■'],
  waves: [' ', '~', '≈', '≋', '∿', '∼'],
  fractal: [' ', '.', ':', ';', '!', 'I', 'X', '#', '█']
};

class PhospheneGenerator {
  constructor(width = 60, height = 20) {
    this.width = width;
    this.height = height;
    this.frame = 0;
  }

  /**
   * Generate a phosphene pattern based on parameters
   * @param {Object} params
   * @param {string} params.type - Pattern type: spiral, tunnel, lattice, waves, aurora, mandala, noise
   * @param {number} params.intensity - 0-100, brightness/density
   * @param {number} params.frequency - 0-100, how fast patterns oscillate
   * @param {number} params.complexity - 0-100, pattern detail level
   * @param {string} params.colorScheme - deep_purple, ocean, fire, aurora, grayscale
   * @returns {string} ASCII/ANSI art frame
   */
  generate(params = {}) {
    const {
      type = 'spiral',
      intensity = 50,
      frequency = 30,
      complexity = 50,
      colorScheme = 'deep_purple'
    } = params;

    this.frame++;
    const t = this.frame * (frequency / 50);

    switch (type) {
      case 'spiral': return this.genSpiral(t, intensity, complexity, colorScheme);
      case 'tunnel': return this.genTunnel(t, intensity, complexity, colorScheme);
      case 'lattice': return this.genLattice(t, intensity, complexity, colorScheme);
      case 'waves': return this.genWaves(t, intensity, complexity, colorScheme);
      case 'aurora': return this.genAurora(t, intensity, complexity, colorScheme);
      case 'mandala': return this.genMandala(t, intensity, complexity, colorScheme);
      case 'noise': return this.genNoise(t, intensity, complexity, colorScheme);
      case 'concentric': return this.genConcentric(t, intensity, complexity, colorScheme);
      default: return this.genSpiral(t, intensity, complexity, colorScheme);
    }
  }

  /**
   * Generate spiral phosphene
   */
  genSpiral(t, intensity, complexity, scheme) {
    const lines = [];
    const cx = this.width / 2;
    const cy = this.height / 2;
    const charset = CHARSETS.spirals;

    for (let y = 0; y < this.height; y++) {
      let line = '';
      for (let x = 0; x < this.width; x++) {
        const dx = (x - cx) / cx;
        const dy = (y - cy) / cy * 2; // Aspect ratio correction
        const r = Math.sqrt(dx * dx + dy * dy);
        const angle = Math.atan2(dy, dx);
        
        const spiral = Math.sin(angle * (complexity / 25 + 1) - r * 8 + t * 0.3);
        const val = (spiral + 1) / 2 * (intensity / 100);
        const fade = Math.max(0, 1 - r * 0.8);
        const finalVal = val * fade;
        
        const charIdx = Math.floor(finalVal * (charset.length - 1));
        const char = charset[Math.max(0, Math.min(charset.length - 1, charIdx))];
        line += this.colorize(char, finalVal, scheme);
      }
      lines.push(line + ANSI.reset);
    }
    return lines.join('\n');
  }

  /**
   * Generate tunnel phosphene
   */
  genTunnel(t, intensity, complexity, scheme) {
    const lines = [];
    const cx = this.width / 2;
    const cy = this.height / 2;
    const charset = CHARSETS.blocks;

    for (let y = 0; y < this.height; y++) {
      let line = '';
      for (let x = 0; x < this.width; x++) {
        const dx = (x - cx) / cx;
        const dy = (y - cy) / cy * 2;
        const r = Math.sqrt(dx * dx + dy * dy);
        
        const ring = Math.sin(r * 10 - t * 0.5) * 0.5 + 0.5;
        const bright = Math.exp(-r * 1.5) * (intensity / 100);
        const val = ring * bright;
        
        const charIdx = Math.floor(val * (charset.length - 1));
        const char = charset[Math.max(0, Math.min(charset.length - 1, charIdx))];
        line += this.colorize(char, val, scheme);
      }
      lines.push(line + ANSI.reset);
    }
    return lines.join('\n');
  }

  /**
   * Generate lattice phosphene
   */
  genLattice(t, intensity, complexity, scheme) {
    const lines = [];
    const charset = CHARSETS.geometric;
    const freq = complexity / 15;

    for (let y = 0; y < this.height; y++) {
      let line = '';
      for (let x = 0; x < this.width; x++) {
        const nx = x / this.width * freq;
        const ny = y / this.height * freq;
        
        const grid = Math.sin(nx * Math.PI * 2 + t * 0.2) * Math.cos(ny * Math.PI * 2 + t * 0.15);
        const val = (grid + 1) / 2 * (intensity / 100);
        
        const charIdx = Math.floor(val * (charset.length - 1));
        const char = charset[Math.max(0, Math.min(charset.length - 1, charIdx))];
        line += this.colorize(char, val, scheme);
      }
      lines.push(line + ANSI.reset);
    }
    return lines.join('\n');
  }

  /**
   * Generate wave phosphene
   */
  genWaves(t, intensity, complexity, scheme) {
    const lines = [];
    const charset = CHARSETS.waves;
    const layers = Math.floor(complexity / 20) + 2;

    for (let y = 0; y < this.height; y++) {
      let line = '';
      for (let x = 0; x < this.width; x++) {
        let val = 0;
        for (let l = 0; l < layers; l++) {
          const freq = (l + 1) * 0.5;
          val += Math.sin(x * freq * 0.2 + y * 0.3 + t * (0.1 + l * 0.05)) / layers;
        }
        val = (val + 1) / 2 * (intensity / 100);
        
        const charIdx = Math.floor(val * (charset.length - 1));
        const char = charset[Math.max(0, Math.min(charset.length - 1, charIdx))];
        line += this.colorize(char, val, scheme);
      }
      lines.push(line + ANSI.reset);
    }
    return lines.join('\n');
  }

  /**
   * Generate aurora phosphene
   */
  genAurora(t, intensity, complexity, scheme) {
    const lines = [];
    const charset = CHARSETS.blocks;

    for (let y = 0; y < this.height; y++) {
      let line = '';
      for (let x = 0; x < this.width; x++) {
        const nx = x / this.width;
        const ny = y / this.height;
        
        const wave1 = Math.sin(nx * 6 + t * 0.2 + ny * 2) * 0.3;
        const wave2 = Math.sin(nx * 3 - t * 0.15 + ny * 4) * 0.3;
        const curtain = Math.exp(-Math.pow(ny - 0.3 - wave1 - wave2, 2) * 8);
        const val = curtain * (intensity / 100);
        
        const charIdx = Math.floor(val * (charset.length - 1));
        const char = charset[Math.max(0, Math.min(charset.length - 1, charIdx))];
        line += this.colorize(char, val, 'aurora');
      }
      lines.push(line + ANSI.reset);
    }
    return lines.join('\n');
  }

  /**
   * Generate mandala phosphene
   */
  genMandala(t, intensity, complexity, scheme) {
    const lines = [];
    const cx = this.width / 2;
    const cy = this.height / 2;
    const charset = CHARSETS.stars;
    const symmetry = Math.floor(complexity / 15) + 3;

    for (let y = 0; y < this.height; y++) {
      let line = '';
      for (let x = 0; x < this.width; x++) {
        const dx = (x - cx) / cx;
        const dy = (y - cy) / cy * 2;
        const r = Math.sqrt(dx * dx + dy * dy);
        const angle = Math.atan2(dy, dx);
        
        const fold = Math.abs(Math.sin(angle * symmetry + t * 0.1));
        const ring = Math.sin(r * 8 + t * 0.2) * 0.5 + 0.5;
        const val = fold * ring * Math.exp(-r * 0.5) * (intensity / 100);
        
        const charIdx = Math.floor(val * (charset.length - 1));
        const char = charset[Math.max(0, Math.min(charset.length - 1, charIdx))];
        line += this.colorize(char, val, scheme);
      }
      lines.push(line + ANSI.reset);
    }
    return lines.join('\n');
  }

  /**
   * Generate noise phosphene (static)
   */
  genNoise(t, intensity, complexity, scheme) {
    const lines = [];
    const charset = CHARSETS.dots;

    for (let y = 0; y < this.height; y++) {
      let line = '';
      for (let x = 0; x < this.width; x++) {
        const noise = this.pseudoRandom(x + t * 100, y + t * 50);
        const val = noise * (intensity / 100);
        
        const charIdx = Math.floor(val * (charset.length - 1));
        const char = charset[Math.max(0, Math.min(charset.length - 1, charIdx))];
        line += this.colorize(char, val, scheme);
      }
      lines.push(line + ANSI.reset);
    }
    return lines.join('\n');
  }

  /**
   * Generate concentric rings
   */
  genConcentric(t, intensity, complexity, scheme) {
    const lines = [];
    const cx = this.width / 2;
    const cy = this.height / 2;
    const charset = CHARSETS.dots;

    for (let y = 0; y < this.height; y++) {
      let line = '';
      for (let x = 0; x < this.width; x++) {
        const dx = (x - cx) / cx;
        const dy = (y - cy) / cy * 2;
        const r = Math.sqrt(dx * dx + dy * dy);
        
        const rings = Math.sin(r * complexity / 5 + t * 0.3) * 0.5 + 0.5;
        const fade = Math.exp(-r * 0.3);
        const val = rings * fade * (intensity / 100);
        
        const charIdx = Math.floor(val * (charset.length - 1));
        const char = charset[Math.max(0, Math.min(charset.length - 1, charIdx))];
        line += this.colorize(char, val, scheme);
      }
      lines.push(line + ANSI.reset);
    }
    return lines.join('\n');
  }

  /**
   * Apply color scheme to a character based on value
   */
  colorize(char, value, scheme) {
    if (char === ' ') return ' ';
    
    const v = Math.max(0, Math.min(1, value));
    let r, g, b;

    switch (scheme) {
      case 'deep_purple':
        r = Math.round(v * 128);
        g = Math.round(v * 20);
        b = Math.round(v * 255);
        break;
      case 'ocean':
        r = Math.round(v * 20);
        g = Math.round(v * 100 + 50);
        b = Math.round(v * 200 + 55);
        break;
      case 'fire':
        r = Math.round(v * 255);
        g = Math.round(v * v * 150);
        b = Math.round(v * v * v * 50);
        break;
      case 'aurora':
        r = Math.round(v * 50);
        g = Math.round(v * 255);
        b = Math.round(v * 200 + (1 - v) * 55);
        break;
      case 'grayscale':
        r = g = b = Math.round(v * 200 + 20);
        break;
      case 'dream':
        r = Math.round(v * 100 + 30);
        g = Math.round(v * 50 + 20);
        b = Math.round(v * 200 + 55);
        break;
      default:
        r = Math.round(v * 128);
        g = Math.round(v * 80);
        b = Math.round(v * 255);
    }

    return `\x1b[38;2;${r};${g};${b}m${char}`;
  }

  /**
   * Simple pseudo-random for deterministic noise
   */
  pseudoRandom(x, y) {
    const n = Math.sin(x * 12.9898 + y * 78.233) * 43758.5453;
    return n - Math.floor(n);
  }

  /**
   * Generate a sequence of frames for animation
   */
  generateSequence(params = {}, frameCount = 10) {
    const frames = [];
    const saved = this.frame;
    for (let i = 0; i < frameCount; i++) {
      frames.push(this.generate(params));
    }
    return frames;
  }

  /**
   * Get a pattern type appropriate for the sleep stage transition
   */
  static getPatternForStage(fromStage, toStage) {
    const transitions = {
      'awake→hypnagogic': { type: 'noise', colorScheme: 'deep_purple', intensity: 30 },
      'hypnagogic→nrem1': { type: 'spiral', colorScheme: 'deep_purple', intensity: 40 },
      'nrem1→nrem2': { type: 'concentric', colorScheme: 'ocean', intensity: 50 },
      'nrem2→nrem3': { type: 'tunnel', colorScheme: 'grayscale', intensity: 30 },
      'nrem3→nrem2': { type: 'waves', colorScheme: 'ocean', intensity: 40 },
      'nrem2→rem': { type: 'mandala', colorScheme: 'aurora', intensity: 70 },
      'rem→nrem1': { type: 'aurora', colorScheme: 'dream', intensity: 50 }
    };

    const key = `${fromStage}→${toStage}`;
    return transitions[key] || { type: 'spiral', colorScheme: 'deep_purple', intensity: 50 };
  }
}

export { PhospheneGenerator, CHARSETS, ANSI };

// CLI
if (import.meta.url === `file://${process.argv[1]}`) {
  const type = process.argv[2] || 'spiral';
  const gen = new PhospheneGenerator(60, 20);
  
  if (process.argv[2] === 'animate') {
    const patternType = process.argv[3] || 'spiral';
    let frame = 0;
    setInterval(() => {
      process.stdout.write('\x1b[H\x1b[2J'); // Clear screen
      console.log(gen.generate({ type: patternType, intensity: 70, frequency: 40, complexity: 60, colorScheme: 'deep_purple' }));
      console.log(`\n${ANSI.dim}Frame ${frame++} | Pattern: ${patternType} | Ctrl+C to stop${ANSI.reset}`);
    }, 100);
  } else {
    console.log(gen.generate({ type, intensity: 60, frequency: 30, complexity: 50, colorScheme: 'deep_purple' }));
  }
}
