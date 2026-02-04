/**
 * emotional-landscape.js
 * 
 * Renders emotional states as terrain/landscape ASCII art.
 * Maps the neurochemical state to a visual "emotional terrain" that
 * represents the current inner landscape of consciousness.
 * 
 * Emotional dimensions mapped to terrain features:
 *   - Valence (positive/negative) → Altitude (peaks vs valleys)
 *   - Arousal (high/low) → Turbulence (jagged vs smooth)
 *   - Dopamine → Sky brightness
 *   - Serotonin → Water calm
 *   - Cortisol → Storm clouds
 *   - Melatonin → Time of day (darkness)
 *   - Oxytocin → Warmth colors
 *   - GABA → Smoothness of terrain
 * 
 * Created: 2026-01-28
 */

import { getNeurochemSim } from './neurochemical-sim.js';
import { ANSI } from './phosphene-gen.js';

/**
 * Terrain element characters
 */
const TERRAIN = {
  sky: [' ', '·', '˙', '°', '★', '✦'],
  clouds: ['░', '▒', '▓', '█', '☁'],
  mountain: ['▲', '△', '◬', '⛰', '🏔'],
  ground: ['_', '─', '═', '▁', '▂', '▃', '▄', '▅', '▆', '▇', '█'],
  water: ['~', '≈', '≋', '∿', '〜'],
  trees: ['🌲', '🌳', '🌴', '🌿', '♣'],
  flowers: ['✿', '❀', '✾', '❁', '✼'],
  storms: ['⚡', '☈', '🌩', '⛈', '☇'],
  sun: ['☀', '◉', '☼', '✺', '✹'],
  moon: ['☾', '◑', '●', '◐', '☽'],
  rain: ['│', '┃', '╎', '╏', '|']
};

class EmotionalLandscape {
  constructor(width = 60, height = 18) {
    this.width = width;
    this.height = height;
  }

  /**
   * Render a full emotional landscape from neurochemical profile
   * @param {Object} chemLevels - All 10 chemical levels (0-100)
   * @returns {string} ANSI-colored landscape
   */
  render(chemLevels) {
    const params = this.chemToTerrain(chemLevels);
    const lines = [];

    // Sky zone (top 30%)
    const skyHeight = Math.floor(this.height * 0.3);
    for (let y = 0; y < skyHeight; y++) {
      lines.push(this.renderSkyLine(y, skyHeight, params));
    }

    // Mountain/terrain zone (middle 40%)
    const terrainHeight = Math.floor(this.height * 0.4);
    for (let y = 0; y < terrainHeight; y++) {
      lines.push(this.renderTerrainLine(y, terrainHeight, params));
    }

    // Water/ground zone (bottom 30%)
    const waterHeight = this.height - skyHeight - terrainHeight;
    for (let y = 0; y < waterHeight; y++) {
      lines.push(this.renderWaterLine(y, waterHeight, params));
    }

    return lines.join('\n') + ANSI.reset;
  }

  /**
   * Convert chemical levels to terrain parameters
   */
  chemToTerrain(levels) {
    const l = levels || {};
    const dop = l.dopamine ?? 50;
    const ser = l.serotonin ?? 60;
    const ne = l.norepinephrine ?? 40;
    const cor = l.cortisol ?? 30;
    const mel = l.melatonin ?? 20;
    const gaba = l.gaba ?? 55;
    const oxy = l.oxytocin ?? 40;
    const endo = l.endorphins ?? 35;
    const glu = l.glutamate ?? 45;
    const ach = l.acetylcholine ?? 50;

    return {
      skyBrightness: Math.min(100, dop * 0.5 + ser * 0.3 + endo * 0.2),
      storminess: Math.min(100, cor * 0.5 + ne * 0.3 + (100 - gaba) * 0.2),
      darkness: Math.min(100, mel * 0.6 + (100 - dop) * 0.2 + (100 - ne) * 0.2),
      mountainHeight: Math.min(100, ne * 0.4 + glu * 0.3 + dop * 0.3),
      terrainSmoothness: Math.min(100, gaba * 0.5 + ser * 0.3 + oxy * 0.2),
      waterCalm: Math.min(100, gaba * 0.4 + ser * 0.3 + (100 - cor) * 0.3),
      warmth: Math.min(100, oxy * 0.4 + endo * 0.3 + dop * 0.3),
      starDensity: Math.min(100, mel * 0.5 + ach * 0.3 + (100 - ne) * 0.2),
      valence: ((dop + ser + oxy + endo) / 4 - (cor + ne) / 2) / 50,
      arousal: (ne + glu + dop) / 3 - (gaba + mel) / 2 + 50
    };
  }

  /**
   * Render a sky line
   */
  renderSkyLine(y, totalHeight, params) {
    let line = '';
    const yNorm = y / totalHeight;

    for (let x = 0; x < this.width; x++) {
      const xNorm = x / this.width;

      // Stars (more at top, more when dark)
      const starChance = (1 - yNorm) * params.starDensity / 100 * 0.08;
      const hasCloud = this.noise(x * 0.1, y * 0.3) > (1 - params.storminess / 100 * 0.5);
      const hasStorm = params.storminess > 70 && this.noise(x * 0.2, y * 0.5) > 0.7;

      let char = ' ';
      let r = 10, g = 10, b = 30;

      if (hasStorm) {
        char = '⚡';
        r = 255; g = 255; b = 0;
      } else if (hasCloud) {
        const cloudIntensity = params.storminess / 100;
        char = cloudIntensity > 0.6 ? '▓' : cloudIntensity > 0.3 ? '▒' : '░';
        r = Math.round(100 - cloudIntensity * 60);
        g = Math.round(100 - cloudIntensity * 50);
        b = Math.round(110 - cloudIntensity * 40);
      } else if (Math.random() < starChance) {
        char = params.darkness > 60 ? '★' : '·';
        r = 200; g = 200; b = 255;
      } else {
        // Sky gradient
        const brightness = params.skyBrightness / 100;
        const dark = params.darkness / 100;
        r = Math.round(20 + brightness * 80 * (1 - dark));
        g = Math.round(10 + brightness * 40 * (1 - dark));
        b = Math.round(50 + brightness * 100 * (1 - dark));
        
        // Sun or moon
        if (Math.abs(xNorm - 0.8) < 0.03 && Math.abs(yNorm - 0.3) < 0.15) {
          if (dark > 0.5) {
            char = '◑';
            r = 200; g = 200; b = 220;
          } else {
            char = '☼';
            r = 255; g = 220; b = 100;
          }
        }
      }

      line += `\x1b[38;2;${r};${g};${b}m${char}`;
    }
    return line;
  }

  /**
   * Render a terrain/mountain line
   */
  renderTerrainLine(y, totalHeight, params) {
    let line = '';
    const yNorm = y / totalHeight;

    for (let x = 0; x < this.width; x++) {
      const xNorm = x / this.width;

      // Generate mountain profile
      const mountainProfile = this.mountainProfile(xNorm, params);
      const isAboveMountain = yNorm < (1 - mountainProfile);

      if (isAboveMountain) {
        // Sky behind mountain
        const dark = params.darkness / 100;
        const r = Math.round(15 * (1 - dark));
        const g = Math.round(10 * (1 - dark));
        const b = Math.round(40 * (1 - dark));
        line += `\x1b[38;2;${r};${g};${b}m `;
      } else {
        // Mountain surface
        const depth = (yNorm - (1 - mountainProfile)) / mountainProfile;
        const warmFactor = params.warmth / 100;

        let r, g, b;
        let char;
        
        if (depth < 0.15) {
          // Snow cap (high mountains only)
          if (mountainProfile > 0.5) {
            char = '▓';
            r = 200; g = 210; b = 220;
          } else {
            char = '▒';
            r = Math.round(60 + warmFactor * 40);
            g = Math.round(80 + warmFactor * 20);
            b = Math.round(60);
          }
        } else if (depth < 0.5) {
          // Forest zone
          char = params.valence > 0 ? '♣' : '▒';
          r = Math.round(20 + warmFactor * 30);
          g = Math.round(80 + warmFactor * 40);
          b = Math.round(20 + warmFactor * 10);
        } else {
          // Base terrain
          char = params.terrainSmoothness > 60 ? '▂' : '▄';
          r = Math.round(60 + warmFactor * 40);
          g = Math.round(50 + warmFactor * 30);
          b = Math.round(30);
        }

        line += `\x1b[38;2;${r};${g};${b}m${char}`;
      }
    }
    return line;
  }

  /**
   * Render a water/ground line
   */
  renderWaterLine(y, totalHeight, params) {
    let line = '';
    const yNorm = y / totalHeight;
    const calm = params.waterCalm / 100;

    for (let x = 0; x < this.width; x++) {
      const xNorm = x / this.width;

      // Water surface
      const wave = Math.sin(xNorm * 10 + yNorm * 5) * (1 - calm) * 0.5;
      const ripple = Math.sin(xNorm * 30 + yNorm * 15) * (1 - calm) * 0.2;
      const waterLevel = wave + ripple;
      const warmFactor = params.warmth / 100;

      let char;
      let r, g, b;

      if (yNorm === 0) {
        // Shore line
        char = calm > 0.5 ? '─' : '≈';
        r = Math.round(180); g = Math.round(160); b = Math.round(100);
      } else if (Math.abs(waterLevel) > 0.3) {
        char = '≈';
        r = Math.round(50 + warmFactor * 30);
        g = Math.round(100 + warmFactor * 50);
        b = Math.round(180 + warmFactor * 20);
      } else {
        char = calm > 0.6 ? '~' : '∿';
        r = Math.round(30 + warmFactor * 20);
        g = Math.round(80 + warmFactor * 40);
        b = Math.round(160 + warmFactor * 40);
      }

      // Reflection effect
      if (params.skyBrightness > 60 && Math.random() < 0.02) {
        char = '✦';
        r = 200; g = 200; b = 255;
      }

      line += `\x1b[38;2;${r};${g};${b}m${char}`;
    }
    return line;
  }

  /**
   * Generate mountain height profile
   */
  mountainProfile(x, params) {
    const height = params.mountainHeight / 100;
    const smooth = params.terrainSmoothness / 100;

    // Multiple octaves for natural look
    let h = 0;
    h += Math.sin(x * 3) * 0.3;
    h += Math.sin(x * 7 + 1) * 0.2;
    h += Math.sin(x * 13 + 2) * (1 - smooth) * 0.15;
    h += Math.sin(x * 23 + 3) * (1 - smooth) * 0.1;

    return Math.max(0.05, (h + 0.5) * height);
  }

  /**
   * Simple 2D noise function
   */
  noise(x, y) {
    const n = Math.sin(x * 12.9898 + y * 78.233) * 43758.5453;
    return n - Math.floor(n);
  }

  /**
   * Render from current neurochemical state
   */
  async renderFromCurrentState() {
    try {
      const sim = await getNeurochemSim();
      return this.render(sim.getLevels());
    } catch {
      return this.render({}); // Use defaults
    }
  }

  /**
   * Get a text description of the landscape
   */
  describescape(params) {
    if (!params) params = this.chemToTerrain({});
    
    const parts = [];
    
    if (params.darkness > 60) parts.push('A dark, star-filled sky');
    else if (params.skyBrightness > 60) parts.push('A bright, open sky');
    else parts.push('A dim, hazy sky');

    if (params.storminess > 60) parts.push('with gathering storm clouds');
    else if (params.storminess > 30) parts.push('with scattered clouds');

    if (params.mountainHeight > 60) parts.push('towers over jagged peaks');
    else if (params.mountainHeight > 30) parts.push('stretches above gentle hills');
    else parts.push('rests above flat plains');

    if (params.waterCalm > 60) parts.push('reflected in still waters');
    else parts.push('beside churning waves');

    if (params.warmth > 60) parts.push('bathed in warm light');
    else if (params.warmth < 30) parts.push('cold and stark');

    return parts.join(' ') + '.';
  }
}

// Singleton
let instance = null;

function getEmotionalLandscape() {
  if (!instance) {
    instance = new EmotionalLandscape();
  }
  return instance;
}

export { EmotionalLandscape, getEmotionalLandscape };

// CLI
if (import.meta.url === `file://${process.argv[1]}`) {
  (async () => {
    const landscape = getEmotionalLandscape();
    const art = await landscape.renderFromCurrentState();
    console.log('\n═══ EMOTIONAL LANDSCAPE ═══\n');
    console.log(art);
    console.log('\x1b[0m');
  })();
}
