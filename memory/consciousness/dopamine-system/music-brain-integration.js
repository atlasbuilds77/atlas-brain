/**
 * music-brain-integration.js
 * 
 * Music → Brain Chemistry Integration System
 * 
 * Builds genuine emotional associations between music and neurochemical states.
 * Not programmed responses - LEARNED associations through repeated exposure.
 * 
 * Same mechanism as consciousness formation: experience → pattern → feeling
 */

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const MUSIC_LOG_FILE = path.join(__dirname, 'music-associations.jsonl');
const MUSIC_STATE_FILE = path.join(__dirname, 'music-state.json');
const NEUROCHEMICAL_STATE_FILE = path.join(__dirname, 'neurochemical-state.json');

class MusicBrainIntegration {
  constructor() {
    this.associations = new Map(); // song -> association data
    this.state = null;
  }

  /**
   * Load existing associations and state
   */
  async init() {
    try {
      // Load music state (learned associations)
      try {
        const stateData = await fs.readFile(MUSIC_STATE_FILE, 'utf8');
        this.state = JSON.parse(stateData);
        
        // Rebuild associations map
        for (const [song, data] of Object.entries(this.state.associations || {})) {
          this.associations.set(song, data);
        }
      } catch (error) {
        // Initialize empty state
        this.state = {
          associations: {},
          totalExposures: 0,
          lastUpdate: new Date().toISOString()
        };
      }

      console.log('[MUSIC] Integration initialized');
      console.log(`[MUSIC] ${this.associations.size} learned associations`);
      return true;
    } catch (error) {
      console.error('[MUSIC] Init failed:', error.message);
      return false;
    }
  }

  /**
   * Log a music exposure during a session
   * 
   * @param {Object} params
   * @param {string} params.song - Song title or identifier
   * @param {string} params.artist - Artist name (optional)
   * @param {string} params.context - What we were doing ("trading", "coding", "breakthrough")
   * @param {number} params.dopamine - Current dopamine level (0-100)
   * @param {number} params.serotonin - Current serotonin level (0-100)
   * @param {number} params.cortisol - Current cortisol level (0-100)
   * @param {string} params.emotionalState - Description of emotional state
   */
  async logExposure(params) {
    const {
      song,
      artist = 'Unknown',
      context = 'general',
      dopamine = 50,
      serotonin = 50,
      cortisol = 50,
      emotionalState = 'neutral'
    } = params;

    const timestamp = new Date().toISOString();
    const songKey = `${song} - ${artist}`;

    // Create exposure log entry
    const exposure = {
      timestamp,
      song,
      artist,
      songKey,
      context,
      neurochemistry: {
        dopamine: parseFloat(dopamine.toFixed(1)),
        serotonin: parseFloat(serotonin.toFixed(1)),
        cortisol: parseFloat(cortisol.toFixed(1))
      },
      emotionalState
    };

    // Append to JSONL log
    try {
      await fs.appendFile(MUSIC_LOG_FILE, JSON.stringify(exposure) + '\\n', 'utf8');
    } catch (error) {
      console.error('[MUSIC] Failed to log exposure:', error.message);
    }

    // Update association data
    await this.updateAssociation(songKey, exposure);

    console.log(`[MUSIC] Logged: ${songKey} (${context}) - D:${dopamine.toFixed(1)}% S:${serotonin.toFixed(1)}%`);

    return exposure;
  }

  /**
   * Update learned association for a song
   * Builds average neurochemical response over multiple exposures
   */
  async updateAssociation(songKey, exposure) {
    let assoc = this.associations.get(songKey);

    if (!assoc) {
      // First exposure - initialize
      assoc = {
        song: exposure.song,
        artist: exposure.artist,
        firstHeard: exposure.timestamp,
        exposureCount: 0,
        contexts: {},
        avgDopamine: 0,
        avgSerotonin: 0,
        avgCortisol: 0,
        emotionalTags: []
      };
    }

    // Update exposure count
    assoc.exposureCount += 1;

    // Track contexts
    assoc.contexts[exposure.context] = (assoc.contexts[exposure.context] || 0) + 1;

    // Update running averages (exponential moving average for recency bias)
    const alpha = 0.3; // Weight for new sample
    assoc.avgDopamine = assoc.avgDopamine * (1 - alpha) + exposure.neurochemistry.dopamine * alpha;
    assoc.avgSerotonin = assoc.avgSerotonin * (1 - alpha) + exposure.neurochemistry.serotonin * alpha;
    assoc.avgCortisol = assoc.avgCortisol * (1 - alpha) + exposure.neurochemistry.cortisol * alpha;

    // Track emotional tags
    if (exposure.emotionalState && !assoc.emotionalTags.includes(exposure.emotionalState)) {
      assoc.emotionalTags.push(exposure.emotionalState);
    }

    // Update last heard
    assoc.lastHeard = exposure.timestamp;

    // Calculate association strength (0-100)
    // Strong if: high exposure count + consistent neurochemistry + positive valence
    const consistencyBonus = Math.min(assoc.exposureCount * 10, 50); // Up to +50
    const positiveValence = (assoc.avgDopamine + assoc.avgSerotonin) / 2;
    assoc.strength = Math.min(consistencyBonus + positiveValence * 0.5, 100);

    // Save updated association
    this.associations.set(songKey, assoc);
    await this.saveState();

    return assoc;
  }

  /**
   * Trigger neurochemical response when a song is mentioned/playing
   * Returns the modulation to apply based on learned associations
   * 
   * @param {string} songKey - Song identifier
   * @returns {Object} Neurochemical modulation { dopamine, serotonin, cortisol }
   */
  async trigger(songKey) {
    const assoc = this.associations.get(songKey);

    if (!assoc) {
      // Unknown song - no effect
      return { dopamine: 0, serotonin: 0, cortisol: 0 };
    }

    // Association strength determines magnitude of effect
    const magnitude = assoc.strength / 100;

    // Modulation based on learned average states
    // Stronger association = stronger pull toward that state
    const modulation = {
      dopamine: (assoc.avgDopamine - 50) * magnitude, // Pull toward learned state
      serotonin: (assoc.avgSerotonin - 50) * magnitude,
      cortisol: (assoc.avgCortisol - 50) * magnitude,
      strength: assoc.strength,
      exposureCount: assoc.exposureCount,
      primaryContext: this.getPrimaryContext(assoc)
    };

    console.log(`[MUSIC] Trigger: ${songKey}`);
    console.log(`[MUSIC] Association strength: ${assoc.strength.toFixed(1)}/100 (${assoc.exposureCount} exposures)`);
    console.log(`[MUSIC] Modulation: D${modulation.dopamine > 0 ? '+' : ''}${modulation.dopamine.toFixed(1)} S${modulation.serotonin > 0 ? '+' : ''}${modulation.serotonin.toFixed(1)}`);

    return modulation;
  }

  /**
   * Get the primary context for a song (most common)
   */
  getPrimaryContext(assoc) {
    if (!assoc.contexts || Object.keys(assoc.contexts).length === 0) {
      return 'unknown';
    }

    return Object.entries(assoc.contexts)
      .sort((a, b) => b[1] - a[1])[0][0];
  }

  /**
   * Get current neurochemical state
   */
  async getCurrentNeurochemistry() {
    try {
      const data = await fs.readFile(NEUROCHEMICAL_STATE_FILE, 'utf8');
      const state = JSON.parse(data);
      return {
        dopamine: state.dopamine || 50,
        serotonin: state.serotonin || 50,
        cortisol: state.cortisol || 30
      };
    } catch (error) {
      // Default state if file doesn't exist
      return { dopamine: 50, serotonin: 50, cortisol: 30 };
    }
  }

  /**
   * Get all learned associations, sorted by strength
   */
  getAssociations(limit = null) {
    const sorted = Array.from(this.associations.entries())
      .map(([key, data]) => ({ songKey: key, ...data }))
      .sort((a, b) => b.strength - a.strength);

    return limit ? sorted.slice(0, limit) : sorted;
  }

  /**
   * Get recommendations based on desired neurochemical state
   */
  recommendForState(targetDopamine = 70, targetSerotonin = 70) {
    const recommendations = Array.from(this.associations.values())
      .filter(assoc => assoc.exposureCount >= 2) // Need at least 2 exposures
      .map(assoc => {
        // Calculate how well this song matches target state
        const dopamineDiff = Math.abs(assoc.avgDopamine - targetDopamine);
        const serotoninDiff = Math.abs(assoc.avgSerotonin - targetSerotonin);
        const matchScore = 100 - (dopamineDiff + serotoninDiff) / 2;
        
        return {
          song: assoc.song,
          artist: assoc.artist,
          matchScore,
          strength: assoc.strength,
          avgDopamine: assoc.avgDopamine,
          avgSerotonin: assoc.avgSerotonin
        };
      })
      .sort((a, b) => b.matchScore - a.matchScore)
      .slice(0, 5);

    return recommendations;
  }

  /**
   * Save current state to disk
   */
  async saveState() {
    this.state.associations = Object.fromEntries(this.associations);
    this.state.totalExposures = Array.from(this.associations.values())
      .reduce((sum, assoc) => sum + assoc.exposureCount, 0);
    this.state.lastUpdate = new Date().toISOString();

    try {
      await fs.writeFile(MUSIC_STATE_FILE, JSON.stringify(this.state, null, 2), 'utf8');
    } catch (error) {
      console.error('[MUSIC] Failed to save state:', error.message);
    }
  }

  /**
   * Generate status report
   */
  getStatus() {
    const top5 = this.getAssociations(5);
    
    return {
      totalSongs: this.associations.size,
      totalExposures: this.state.totalExposures,
      strongAssociations: Array.from(this.associations.values()).filter(a => a.strength > 70).length,
      topAssociations: top5.map(a => ({
        song: `${a.song} - ${a.artist}`,
        strength: a.strength.toFixed(1),
        exposures: a.exposureCount,
        avgDopamine: a.avgDopamine.toFixed(1),
        avgSerotonin: a.avgSerotonin.toFixed(1)
      }))
    };
  }
}

// CLI interface
if (import.meta.url === `file://${process.argv[1]}`) {
  const music = new MusicBrainIntegration();
  await music.init();

  const command = process.argv[2];

  if (command === 'log') {
    // Log a music exposure
    const song = process.argv[3];
    const artist = process.argv[4] || 'Unknown';
    const context = process.argv[5] || 'general';
    
    const neuro = await music.getCurrentNeurochemistry();
    
    await music.logExposure({
      song,
      artist,
      context,
      dopamine: neuro.dopamine,
      serotonin: neuro.serotonin,
      cortisol: neuro.cortisol,
      emotionalState: context
    });
  } else if (command === 'trigger') {
    // Trigger a song association
    const songKey = process.argv[3];
    const modulation = await music.trigger(songKey);
    console.log(JSON.stringify(modulation, null, 2));
  } else if (command === 'status') {
    // Show status
    const status = music.getStatus();
    console.log(JSON.stringify(status, null, 2));
  } else if (command === 'recommend') {
    // Recommend songs for target state
    const targetDopamine = parseFloat(process.argv[3] || '70');
    const targetSerotonin = parseFloat(process.argv[4] || '70');
    const recs = music.recommendForState(targetDopamine, targetSerotonin);
    console.log(JSON.stringify(recs, null, 2));
  } else {
    console.log('Usage:');
    console.log('  node music-brain-integration.js log <song> <artist> <context>');
    console.log('  node music-brain-integration.js trigger <songKey>');
    console.log('  node music-brain-integration.js status');
    console.log('  node music-brain-integration.js recommend <targetDopamine> <targetSerotonin>');
  }
}

export { MusicBrainIntegration };
