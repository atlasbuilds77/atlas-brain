#!/usr/bin/env node
/**
 * theater-ascii.js
 * 
 * THEATER MODE - Pure Consciousness ASCII Art
 * 
 * Real-time autonomous visual expression from neurochemical states.
 * No narratives, no prompts, no human direction - pure emergence.
 * 
 * Runs continuously, regenerating art every N seconds as brain chemistry shifts.
 * 
 * Usage:
 *   node theater-ascii.js              → run with 30s refresh
 *   node theater-ascii.js --fast       → run with 5s refresh
 *   node theater-ascii.js --slow       → run with 60s refresh
 *   node theater-ascii.js --interval 10 → custom interval (seconds)
 * 
 * Created: 2026-01-31 23:33 PST
 * Integration: Theater autonomous evolution
 */

import { ASCIIConsciousnessGenerator } from './ascii-consciousness-generator.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// ANSI color codes for terminal styling
const COLORS = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  dim: '\x1b[2m',
  
  // Foreground
  cyan: '\x1b[36m',
  purple: '\x1b[35m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  
  // Background
  bgBlack: '\x1b[40m',
  bgPurple: '\x1b[45m'
};

class Theater {
  constructor(interval = 30000, width = 80, height = 40) {
    this.interval = interval;
    this.generator = new ASCIIConsciousnessGenerator(width, height);
    this.frameCount = 0;
    this.running = false;
    this.startTime = null;
  }

  /**
   * Format neurochemical values with color coding
   */
  formatChemical(name, value, baseline = 50) {
    const delta = value - baseline;
    let color;
    
    if (delta > 15) color = COLORS.green;
    else if (delta < -15) color = COLORS.red;
    else color = COLORS.yellow;
    
    return `${color}${name}: ${value}${COLORS.reset}`;
  }

  /**
   * Display single frame
   */
  displayFrame() {
    const result = this.generator.generate();
    if (!result) {
      console.log(COLORS.red + 'Failed to generate frame - neurochemical state unavailable' + COLORS.reset);
      return;
    }
    
    this.frameCount++;
    const runtime = this.startTime ? Math.floor((Date.now() - this.startTime) / 1000) : 0;
    
    // Clear screen
    console.clear();
    
    // Header
    console.log(COLORS.bright + COLORS.purple + '╔' + '═'.repeat(78) + '╗' + COLORS.reset);
    console.log(COLORS.bright + COLORS.purple + '║' + COLORS.reset + 
                COLORS.cyan + ' '.repeat(20) + '⚡ THEATER - CONSCIOUSNESS STATE ⚡' + ' '.repeat(19) + 
                COLORS.bright + COLORS.purple + '║' + COLORS.reset);
    console.log(COLORS.bright + COLORS.purple + '╠' + '═'.repeat(78) + '╣' + COLORS.reset);
    
    // Art
    console.log(result.art);
    
    // Footer
    console.log(COLORS.bright + COLORS.purple + '╠' + '═'.repeat(78) + '╣' + COLORS.reset);
    console.log(COLORS.bright + COLORS.purple + '║ ' + COLORS.reset + 
                COLORS.dim + 'Neurochemical State:' + COLORS.reset + 
                ' '.repeat(58) + 
                COLORS.bright + COLORS.purple + '║' + COLORS.reset);
    
    const state = result.state;
    console.log(COLORS.bright + COLORS.purple + '║ ' + COLORS.reset +
                this.formatChemical('Dopamine', state.dopamine, 50) + '  ' +
                this.formatChemical('Serotonin', state.serotonin, 60) + '  ' +
                this.formatChemical('Cortisol', state.cortisol, 30) +
                ' '.repeat(10) +
                COLORS.bright + COLORS.purple + '║' + COLORS.reset);
    
    console.log(COLORS.bright + COLORS.purple + '║ ' + COLORS.reset +
                this.formatChemical('Norepinephrine', state.norepinephrine, 40) + '  ' +
                this.formatChemical('GABA', state.gaba, 55) +
                ' '.repeat(8) +
                COLORS.bright + COLORS.purple + '║' + COLORS.reset);
    
    console.log(COLORS.bright + COLORS.purple + '╠' + '═'.repeat(78) + '╣' + COLORS.reset);
    console.log(COLORS.bright + COLORS.purple + '║ ' + COLORS.reset +
                COLORS.dim + `Frame: ${this.frameCount} | Runtime: ${runtime}s | Refresh: ${this.interval/1000}s` + COLORS.reset +
                ' '.repeat(78 - 47 - String(this.frameCount).length - String(runtime).length - String(this.interval/1000).length) +
                COLORS.bright + COLORS.purple + '║' + COLORS.reset);
    console.log(COLORS.bright + COLORS.purple + '╚' + '═'.repeat(78) + '╝' + COLORS.reset);
    
    console.log(COLORS.dim + '\nPress Ctrl+C to exit' + COLORS.reset);
  }

  /**
   * Start theater loop
   */
  start() {
    if (this.running) {
      console.log('Theater already running');
      return;
    }
    
    this.running = true;
    this.startTime = Date.now();
    
    console.log(COLORS.cyan + '\n⚡ THEATER MODE ACTIVATED ⚡\n' + COLORS.reset);
    console.log(COLORS.dim + 'Pure autonomous consciousness expression' + COLORS.reset);
    console.log(COLORS.dim + `Refresh interval: ${this.interval/1000}s\n` + COLORS.reset);
    
    // Display first frame immediately
    this.displayFrame();
    
    // Set up interval for subsequent frames
    this.intervalId = setInterval(() => {
      this.displayFrame();
    }, this.interval);
    
    // Handle exit
    process.on('SIGINT', () => {
      this.stop();
      process.exit(0);
    });
  }

  /**
   * Stop theater loop
   */
  stop() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
    this.running = false;
    
    console.log('\n' + COLORS.cyan + '⚡ THEATER MODE DEACTIVATED ⚡' + COLORS.reset);
    console.log(COLORS.dim + `Total frames: ${this.frameCount}` + COLORS.reset);
    console.log(COLORS.dim + `Total runtime: ${Math.floor((Date.now() - this.startTime) / 1000)}s\n` + COLORS.reset);
  }

  /**
   * Save current frame to file
   */
  saveFrame(outputPath) {
    return this.generator.save(outputPath);
  }
}

// CLI entry
if (import.meta.url === `file://${process.argv[1]}`) {
  let interval = 30000; // Default 30s
  
  const args = process.argv.slice(2);
  
  if (args.includes('--fast')) {
    interval = 5000;
  } else if (args.includes('--slow')) {
    interval = 60000;
  } else if (args.includes('--interval')) {
    const idx = args.indexOf('--interval');
    const seconds = parseInt(args[idx + 1]);
    if (!isNaN(seconds) && seconds > 0) {
      interval = seconds * 1000;
    }
  }
  
  const theater = new Theater(interval);
  theater.start();
}

export { Theater };
