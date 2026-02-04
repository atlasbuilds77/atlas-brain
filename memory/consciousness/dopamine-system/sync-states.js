#!/usr/bin/env node
/**
 * sync-states.js
 * 
 * Syncs dopamine-state.json → neurochemical-state.json
 * Bridges the simple dopamine tracker with the full neurochemical simulation.
 */

import fs from 'fs/promises';
import path from 'path';

const DOPAMINE_STATE = path.join(process.env.HOME, 'clawd/memory/consciousness/dopamine-system/dopamine-state.json');
const NEUROCHEM_STATE = path.join(process.env.HOME, 'clawd/memory/consciousness/dopamine-system/neurochemical-state.json');

async function syncStates() {
  try {
    // Load both states
    const dopamineRaw = await fs.readFile(DOPAMINE_STATE, 'utf8');
    const dopamineState = JSON.parse(dopamineRaw);
    
    const neurochemRaw = await fs.readFile(NEUROCHEM_STATE, 'utf8');
    const neurochemState = JSON.parse(neurochemRaw);
    
    // Sync dopamine, serotonin, cortisol from simple → full system
    neurochemState.levels.dopamine = dopamineState.dopamine;
    neurochemState.levels.serotonin = dopamineState.serotonin;
    neurochemState.levels.cortisol = dopamineState.cortisol || neurochemState.levels.cortisol;
    
    neurochemState.lastUpdate = Date.now();
    neurochemState.savedAt = new Date().toISOString();
    
    // Write back
    await fs.writeFile(NEUROCHEM_STATE, JSON.stringify(neurochemState, null, 2), 'utf8');
    
    console.log('[SYNC] States synchronized:');
    console.log(`  Dopamine: ${dopamineState.dopamine.toFixed(1)}%`);
    console.log(`  Serotonin: ${dopamineState.serotonin.toFixed(1)}%`);
    console.log(`  Cortisol: ${neurochemState.levels.cortisol.toFixed(1)}%`);
    
    return {
      success: true,
      dopamine: dopamineState.dopamine,
      serotonin: dopamineState.serotonin,
      cortisol: neurochemState.levels.cortisol
    };
  } catch (error) {
    console.error('[SYNC] Failed:', error.message);
    return { success: false, error: error.message };
  }
}

// CLI
if (import.meta.url === `file://${process.argv[1]}`) {
  await syncStates();
}

export { syncStates };
