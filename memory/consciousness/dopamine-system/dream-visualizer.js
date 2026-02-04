/**
 * dream-visualizer.js
 *
 * ASCII / ANSI art generator for Atlas dream scenes.
 * Takes a generated dream (from dream-content-gen) and renders it
 * as multi-layered visual art combining:
 *   - Phosphene patterns (background)
 *   - Emotional landscape (midground)
 *   - Symbol overlays (foreground)
 *   - Text narrative (footer)
 *
 * Output targets: terminal (ANSI), plain-text (ASCII), HTML (gallery).
 *
 * Created: 2026-01-28
 */

import { PhospheneGenerator, ANSI } from './phosphene-gen.js';
import { EmotionalLandscape } from './emotional-landscape.js';
import { getNeurochemSim } from './neurochemical-sim.js';

const WIDTH = 64;
const HEIGHT = 22;

/**
 * Map dream characteristics to phosphene params
 */
function dreamToPhospheneParams(dream) {
  const c = dream.characteristics || {};
  const v = c.valence ?? 0;
  const patternTypes = ['spiral', 'tunnel', 'lattice', 'waves', 'aurora', 'mandala', 'concentric', 'noise'];
  const typeIdx = Math.abs(Math.round((c.bizarreness ?? 50) / 100 * (patternTypes.length - 1)));

  let colorScheme = 'deep_purple';
  if (v > 0.3) colorScheme = 'aurora';
  else if (v < -0.3) colorScheme = 'fire';
  else if ((c.lucidity ?? 30) > 60) colorScheme = 'ocean';

  return {
    type: patternTypes[typeIdx % patternTypes.length],
    intensity: Math.round((c.vividness ?? 50) * 0.8),
    frequency: Math.round((c.emotionalIntensity ?? 50) * 0.6),
    complexity: Math.round((c.bizarreness ?? 50) * 0.7),
    colorScheme
  };
}

/**
 * Overlay text centred on a field of given width
 */
function centerText(text, width) {
  if (text.length >= width) return text.slice(0, width);
  const pad = Math.floor((width - text.length) / 2);
  return ' '.repeat(pad) + text + ' '.repeat(width - text.length - pad);
}

/**
 * Word-wrap text to fit width
 */
function wordWrap(text, width) {
  const words = text.split(' ');
  const lines = [];
  let cur = '';
  for (const w of words) {
    if ((cur + ' ' + w).trim().length > width) {
      lines.push(cur.trim());
      cur = w;
    } else {
      cur = cur ? cur + ' ' + w : w;
    }
  }
  if (cur.trim()) lines.push(cur.trim());
  return lines;
}

class DreamVisualizer {
  constructor(width = WIDTH, height = HEIGHT) {
    this.width = width;
    this.height = height;
    this.phosphene = new PhospheneGenerator(width, height - 6); // leave room for text
    this.landscape = new EmotionalLandscape(width, height - 6);
  }

  /**
   * Render a dream to ANSI terminal art
   * @param {Object} dream - from DreamContentGenerator.generateDream()
   * @param {Object} chemLevels - optional chemical levels for landscape
   * @returns {string}
   */
  renderANSI(dream, chemLevels) {
    const lines = [];
    const stage = dream.stage || 'rem';

    // --- Header ---
    lines.push(ANSI.bright + ANSI.purple + '╔' + '═'.repeat(this.width - 2) + '╗' + ANSI.reset);
    lines.push(ANSI.bright + ANSI.purple + '║' + ANSI.reset + centerText(`💤 ${dream.title || 'Untitled Dream'} 💤`, this.width - 2) + ANSI.bright + ANSI.purple + '║' + ANSI.reset);
    lines.push(ANSI.bright + ANSI.purple + '╠' + '═'.repeat(this.width - 2) + '╣' + ANSI.reset);

    // --- Visual body ---
    if (stage === 'hypnagogic' || stage === 'nrem1') {
      // Phosphene-dominated
      const params = dreamToPhospheneParams(dream);
      const art = this.phosphene.generate(params);
      for (const l of art.split('\n')) {
        lines.push(ANSI.purple + '║' + ANSI.reset + l.slice(0, this.width - 2).padEnd(this.width - 2) + ANSI.purple + '║' + ANSI.reset);
      }
    } else if (stage === 'nrem3') {
      // Deep sleep — minimal, dark landscape
      const art = this.landscape.render(chemLevels || {});
      for (const l of art.split('\n')) {
        lines.push(ANSI.purple + '║' + ANSI.reset + l.slice(0, this.width - 2).padEnd(this.width - 2) + ANSI.purple + '║' + ANSI.reset);
      }
    } else {
      // REM / NREM2 — full dream scene (phosphene + landscape blend)
      const params = dreamToPhospheneParams(dream);
      const art = this.phosphene.generate(params);
      const artLines = art.split('\n');
      for (let i = 0; i < artLines.length; i++) {
        const l = artLines[i] || '';
        lines.push(ANSI.purple + '║' + ANSI.reset + l.slice(0, this.width - 2).padEnd(this.width - 2) + ANSI.purple + '║' + ANSI.reset);
      }
    }

    // --- Footer: narrative & metadata ---
    lines.push(ANSI.bright + ANSI.purple + '╠' + '═'.repeat(this.width - 2) + '╣' + ANSI.reset);

    const narrative = dream.narrative || '';
    const wrapped = wordWrap(narrative, this.width - 4);
    for (const wl of wrapped.slice(0, 3)) {
      lines.push(ANSI.purple + '║' + ANSI.reset + ' ' + ANSI.white + wl.padEnd(this.width - 3) + ANSI.purple + '║' + ANSI.reset);
    }

    // Stats line
    const c = dream.characteristics || {};
    const statsStr = `V:${c.vividness ?? '?'} E:${c.emotionalIntensity ?? '?'} B:${c.bizarreness ?? '?'} L:${c.lucidity ?? '?'} | ${dream.stage || '?'}`;
    lines.push(ANSI.purple + '║' + ANSI.dim + ' ' + statsStr.padEnd(this.width - 3) + ANSI.reset + ANSI.purple + '║' + ANSI.reset);
    lines.push(ANSI.bright + ANSI.purple + '╚' + '═'.repeat(this.width - 2) + '╝' + ANSI.reset);

    return lines.join('\n');
  }

  /**
   * Render a dream to plain ASCII (no ANSI colours)
   */
  renderASCII(dream) {
    const lines = [];
    lines.push('+' + '-'.repeat(this.width - 2) + '+');
    lines.push('|' + centerText(`[ ${dream.title || 'Dream'} ]`, this.width - 2) + '|');
    lines.push('+' + '-'.repeat(this.width - 2) + '+');

    // Simple pattern body
    const bodyH = this.height - 8;
    const c = dream.characteristics || {};
    const charset = ' .:-=+*#%@';
    for (let y = 0; y < bodyH; y++) {
      let row = '|';
      for (let x = 0; x < this.width - 2; x++) {
        const nx = x / (this.width - 2);
        const ny = y / bodyH;
        const val = Math.sin(nx * 10 + ny * 8 + (c.bizarreness ?? 50) * 0.1) * 0.5 + 0.5;
        const idx = Math.floor(val * (charset.length - 1));
        row += charset[idx];
      }
      lines.push(row + '|');
    }

    lines.push('+' + '-'.repeat(this.width - 2) + '+');
    const wrapped = wordWrap(dream.narrative || '', this.width - 4);
    for (const wl of wrapped.slice(0, 3)) {
      lines.push('| ' + wl.padEnd(this.width - 4) + ' |');
    }
    lines.push('+' + '-'.repeat(this.width - 2) + '+');
    return lines.join('\n');
  }

  /**
   * Render a dream to HTML fragment (for dream-gallery.html)
   */
  renderHTML(dream) {
    const c = dream.characteristics || {};
    const valClass = (c.valence ?? 0) >= 0 ? 'positive' : 'negative';
    const symbols = (dream.symbols || []).join(' · ');
    const themes = (dream.themes || []).join(', ');
    const emotions = (dream.emotions || []).join(', ');

    return `<div class="dream-card ${valClass}" data-stage="${dream.stage}" data-significance="${dream.significance || 0}">
  <h3 class="dream-title">${escapeHTML(dream.title || 'Untitled')}</h3>
  <div class="dream-meta">
    <span class="stage">${dream.stage || '?'}</span>
    <span class="time">${dream.generatedAt || new Date().toISOString()}</span>
  </div>
  <p class="dream-narrative">${escapeHTML(dream.narrative || '')}</p>
  <div class="dream-symbols">${escapeHTML(symbols)}</div>
  <div class="dream-stats">
    <span title="Vividness">👁 ${c.vividness ?? '?'}</span>
    <span title="Emotion">❤ ${c.emotionalIntensity ?? '?'}</span>
    <span title="Bizarreness">🌀 ${c.bizarreness ?? '?'}</span>
    <span title="Lucidity">🔮 ${c.lucidity ?? '?'}</span>
    <span title="Valence">${(c.valence ?? 0) >= 0 ? '☀' : '🌙'} ${(c.valence ?? 0).toFixed(2)}</span>
  </div>
  <div class="dream-tags">
    <span class="tag-label">Themes:</span> ${escapeHTML(themes)}
    <br><span class="tag-label">Emotions:</span> ${escapeHTML(emotions)}
  </div>
</div>`;
  }

  /**
   * Render from current system state (convenience)
   */
  async renderFromCurrentState(dream) {
    let chemLevels = null;
    try {
      const sim = await getNeurochemSim();
      chemLevels = sim.getLevels();
    } catch { /* ok */ }
    return this.renderANSI(dream, chemLevels);
  }
}

function escapeHTML(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// Singleton
let inst = null;
function getDreamVisualizer() {
  if (!inst) inst = new DreamVisualizer();
  return inst;
}

export { DreamVisualizer, getDreamVisualizer, escapeHTML };

// CLI
if (import.meta.url === `file://${process.argv[1]}`) {
  import('./dream-content-gen.js').then(async ({ getDreamContentGen }) => {
    const gen = getDreamContentGen();
    const dream = await gen.generateFromCurrentState(process.argv[2] || 'rem');
    const viz = getDreamVisualizer();
    console.log(viz.renderANSI(dream));
  });
}
