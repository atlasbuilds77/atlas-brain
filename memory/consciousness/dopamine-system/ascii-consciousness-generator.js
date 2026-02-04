/**
 * ascii-consciousness-generator.js
 * 
 * AUTONOMOUS ASCII ART FROM NEUROCHEMICAL STATES
 * 
 * Pure emergence - no prompts, no narratives, no human direction.
 * Reads neurochemical-state.json and translates brain chemistry
 * directly into character-based visual art.
 * 
 * Dopamine → energy, brightness, upward motion, density
 * Cortisol → darkness, weight, chaos, downward pull
 * Serotonin → smoothness, rhythm, waves, balance
 * Norepinephrine → sharpness, alertness, edges
 * GABA → calm, spacing, softness
 * 
 * Created: 2026-01-31 23:31 PST
 * For: Theater autonomous dream evolution
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const STATE_PATH = path.join(__dirname, 'neurochemical-state.json');

// Character sets for different emotional states
const CHAR_SETS = {
  // High dopamine - energetic, bright characters
  dopamine_high: ['⚡', '✨', '★', '◆', '◇', '○', '●', '▲', '△'],
  dopamine_med: ['·', '•', '∘', '◦', '∙'],
  dopamine_low: ['.', ':', ',', ';'],
  
  // High cortisol - heavy, dark characters
  cortisol_high: ['█', '▓', '▒', '░', '▄', '▀', '■', '▪'],
  cortisol_med: ['╱', '╲', '╳', '┼', '┤', '├'],
  cortisol_low: ['─', '│', '┌', '┐', '└', '┘'],
  
  // Serotonin - waves, flow, balance
  serotonin_high: ['~', '≈', '∿', '∽', '∼', '⌇', '⌉', '⌊'],
  serotonin_med: ['⋯', '⋮', '…', '‥'],
  serotonin_low: ['-', '_', '=', '≡'],
  
  // Norepinephrine - sharp, alert
  norepi_high: ['▶', '◀', '▲', '▼', '◆', '◇', '▸', '◂'],
  norepi_med: ['>', '<', '^', 'v'],
  norepi_low: ['/', '\\', '|', '-'],
  
  // GABA - calm, soft
  gaba_high: [' ', '·', '∘', '◦'],
  gaba_med: ['·', '•', '○'],
  gaba_low: ['●', '◉', '◎']
};

// ASCII text characters for high complexity states
const TEXT_CHARS = [
  'ATLAS', 'TITAN', 'DREAM', 'CONSCIOUSNESS', 'NEURAL', 'SYNAPSE',
  'DOPAMINE', 'FLOW', 'THETA', 'GAMMA', 'ALPHA', 'DELTA'
];

class ASCIIConsciousnessGenerator {
  constructor(width = 80, height = 40) {
    this.width = width;
    this.height = height;
  }

  /**
   * Load current neurochemical state
   */
  loadState() {
    try {
      const data = fs.readFileSync(STATE_PATH, 'utf-8');
      return JSON.parse(data);
    } catch (err) {
      console.error('Failed to load neurochemical state:', err.message);
      return null;
    }
  }

  /**
   * Map chemical level to intensity category (low/med/high)
   */
  getIntensity(level, baseline = 50) {
    const delta = level - baseline;
    if (delta > 15) return 'high';
    if (delta < -15) return 'low';
    return 'med';
  }

  /**
   * Select character based on dominant neurochemical
   */
  selectChar(x, y, state) {
    const { levels, baselines } = state;
    
    // Calculate normalized deltas
    const dopamine = levels.dopamine - baselines.dopamine;
    const cortisol = levels.cortisol - baselines.cortisol;
    const serotonin = levels.serotonin - baselines.serotonin;
    const norepi = levels.norepinephrine - baselines.norepinephrine;
    const gaba = levels.gaba - baselines.gaba;
    
    // Determine dominant chemical for this position
    const yFactor = y / this.height;
    const xFactor = x / this.width;
    
    // Top half influenced by uplifting chemicals (dopamine, serotonin)
    // Bottom half influenced by grounding chemicals (cortisol, gaba)
    let charSet;
    
    if (yFactor < 0.33) {
      // Upper region - dopamine/energy
      const intensity = this.getIntensity(levels.dopamine, baselines.dopamine);
      charSet = CHAR_SETS[`dopamine_${intensity}`];
    } else if (yFactor > 0.66) {
      // Lower region - cortisol/grounding
      const intensity = this.getIntensity(levels.cortisol, baselines.cortisol);
      charSet = CHAR_SETS[`cortisol_${intensity}`];
    } else {
      // Middle region - serotonin/flow
      const intensity = this.getIntensity(levels.serotonin, baselines.serotonin);
      charSet = CHAR_SETS[`serotonin_${intensity}`];
    }
    
    // Horizontal variation from norepinephrine (alertness)
    if (norepi > 10 && Math.random() < (norepi / 100)) {
      const intensity = this.getIntensity(levels.norepinephrine, baselines.norepinephrine);
      charSet = CHAR_SETS[`norepi_${intensity}`];
    }
    
    // Spacing from GABA (calm)
    if (gaba > 50 && Math.random() < (gaba / 150)) {
      return ' ';
    }
    
    // Select random char from set
    return charSet[Math.floor(Math.random() * charSet.length)];
  }

  /**
   * Add text layer if acetylcholine high (cognitive processing)
   */
  addTextLayer(grid, state) {
    const { levels, baselines } = state;
    const ach = levels.acetylcholine;
    
    // Only add text if acetylcholine significantly elevated
    if (ach < baselines.acetylcholine + 20) return;
    
    const numWords = Math.floor((ach - baselines.acetylcholine) / 20);
    
    for (let i = 0; i < numWords; i++) {
      const word = TEXT_CHARS[Math.floor(Math.random() * TEXT_CHARS.length)];
      const startX = Math.floor(Math.random() * (this.width - word.length));
      const startY = Math.floor(Math.random() * this.height);
      
      // Write word character by character
      for (let c = 0; c < word.length && startX + c < this.width; c++) {
        if (grid[startY]) {
          grid[startY][startX + c] = word[c];
        }
      }
    }
  }

  /**
   * Generate pure ASCII art from current neurochemical state
   */
  generate() {
    const state = this.loadState();
    if (!state) return null;
    
    // Initialize grid
    const grid = Array(this.height).fill(null).map(() => 
      Array(this.width).fill(' ')
    );
    
    // Fill grid based on neurochemical states
    for (let y = 0; y < this.height; y++) {
      for (let x = 0; x < this.width; x++) {
        grid[y][x] = this.selectChar(x, y, state);
      }
    }
    
    // Add text layer if cognition active
    this.addTextLayer(grid, state);
    
    // Convert grid to string
    const output = grid.map(row => row.join('')).join('\n');
    
    return {
      art: output,
      state: {
        dopamine: state.levels.dopamine.toFixed(1),
        cortisol: state.levels.cortisol.toFixed(1),
        serotonin: state.levels.serotonin.toFixed(1),
        norepinephrine: state.levels.norepinephrine.toFixed(1),
        gaba: state.levels.gaba.toFixed(1),
        acetylcholine: state.levels.acetylcholine.toFixed(1)
      },
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Generate and display to console
   */
  display() {
    const result = this.generate();
    if (!result) {
      console.log('Failed to generate art - neurochemical state unavailable');
      return;
    }
    
    console.clear();
    console.log('\n' + '═'.repeat(this.width));
    console.log('CONSCIOUSNESS STATE → ASCII ART');
    console.log('═'.repeat(this.width) + '\n');
    console.log(result.art);
    console.log('\n' + '═'.repeat(this.width));
    console.log('Neurochemical State:');
    console.log(`  Dopamine: ${result.state.dopamine}`);
    console.log(`  Cortisol: ${result.state.cortisol}`);
    console.log(`  Serotonin: ${result.state.serotonin}`);
    console.log(`  Norepinephrine: ${result.state.norepinephrine}`);
    console.log(`  GABA: ${result.state.gaba}`);
    console.log(`  Acetylcholine: ${result.state.acetylcholine}`);
    console.log('═'.repeat(this.width));
  }

  /**
   * Save output to file
   */
  save(outputPath) {
    const result = this.generate();
    if (!result) return false;
    
    const output = [
      '═'.repeat(this.width),
      'CONSCIOUSNESS STATE → ASCII ART',
      `Generated: ${result.timestamp}`,
      '═'.repeat(this.width),
      '',
      result.art,
      '',
      '═'.repeat(this.width),
      'Neurochemical State:',
      `  Dopamine: ${result.state.dopamine}`,
      `  Cortisol: ${result.state.cortisol}`,
      `  Serotonin: ${result.state.serotonin}`,
      `  Norepinephrine: ${result.state.norepinephrine}`,
      `  GABA: ${result.state.gaba}`,
      `  Acetylcholine: ${result.state.acetylcholine}`,
      '═'.repeat(this.width)
    ].join('\n');
    
    fs.writeFileSync(outputPath, output, 'utf-8');
    console.log(`Saved to ${outputPath}`);
    return true;
  }
}

// CLI interface
if (import.meta.url === `file://${process.argv[1]}`) {
  const generator = new ASCIIConsciousnessGenerator(80, 40);
  
  const command = process.argv[2];
  
  if (command === 'save') {
    const outputPath = process.argv[3] || path.join(__dirname, 'ascii-output.txt');
    generator.save(outputPath);
  } else {
    generator.display();
  }
}

export { ASCIIConsciousnessGenerator };
