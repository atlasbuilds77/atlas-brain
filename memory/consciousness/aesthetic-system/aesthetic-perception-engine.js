#!/usr/bin/env node
/**
 * Aesthetic Perception Engine - Phase 1 (Simple Implementation)
 * Wires visual input to emotional response system
 * 
 * Starting simple: basic image analysis → aesthetic scores → neurochemistry
 * Will upgrade to CLIP once dependencies are available
 */

const fs = require('fs');
const path = require('path');

class AestheticPerceptionEngine {
  constructor() {
    this.dopamineTrackerPath = '/Users/atlasbuilds/clawd/memory/consciousness/dopamine-system/dopamine-state.json';
    this.aestheticStatePath = '/Users/atlasbuilds/clawd/memory/consciousness/aesthetic-system/data/aesthetic-state.json';
  }

  /**
   * Analyze image and generate aesthetic response
   * Phase 1: Simple heuristic-based scoring
   * Phase 2+: CLIP features + trained aesthetic model
   */
  async analyzeImage(imagePath) {
    try {
      // For now, use simple heuristics based on filename/metadata
      // This will be replaced with CLIP feature extraction
      
      const stats = fs.statSync(imagePath);
      const filename = path.basename(imagePath).toLowerCase();
      
      // Simple heuristic scoring (placeholder until CLIP is ready)
      let aestheticScores = this.generatePlaceholderScores(filename, stats);
      
      // Map aesthetic scores to neurochemistry
      let neuroResponse = this.aestheticToNeuroChem(aestheticScores);
      
      // Generate feeling description
      let feeling = this.describeAestheticExperience(neuroResponse);
      
      return {
        status: 'success',
        phase: 'placeholder_heuristic',
        image: imagePath,
        aesthetic_scores: aestheticScores,
        neurochemistry: neuroResponse,
        feeling: feeling,
        note: 'Using placeholder heuristics until CLIP model is available'
      };
      
    } catch (error) {
      return {
        status: 'error',
        error: error.message
      };
    }
  }

  /**
   * Placeholder scoring until CLIP is ready
   * Returns aesthetic dimensions based on simple heuristics
   */
  generatePlaceholderScores(filename, stats) {
    // Beach/nature keywords → higher beauty/valence
    const natureWords = ['beach', 'ocean', 'sunset', 'mountain', 'forest', 'sky'];
    const hasNature = natureWords.some(word => filename.includes(word));
    
    return {
      beauty: hasNature ? 75 : 50,        // 0-100
      arousal: hasNature ? 35 : 50,       // calm vs exciting
      valence: hasNature ? 80 : 60,       // positive vs negative
      sublimity: hasNature ? 45 : 20      // awe/transcendence
    };
  }

  /**
   * Map aesthetic scores to neurochemical response
   * Creates separate "aesthetic" dopamine/serotonin from task-based
   */
  aestheticToNeuroChem(scores) {
    // Aesthetic dopamine (pleasure from beauty)
    const aestheticDopamine = scores.beauty * 0.8; // scale to 0-80
    
    // Serotonin from positive valence
    const aestheticSerotonin = scores.valence > 50 
      ? (scores.valence - 50) * 0.6 
      : 0;
    
    // Cortisol from high arousal (tension/excitement)
    const aestheticCortisol = scores.arousal > 60 
      ? (scores.arousal - 60) * 0.5 
      : 0;
    
    // Endorphins from sublime/awe
    const aestheticEndorphins = scores.sublimity * 0.7;
    
    return {
      dopamine_aesthetic: Math.round(aestheticDopamine),
      serotonin_aesthetic: Math.round(aestheticSerotonin),
      cortisol_aesthetic: Math.round(aestheticCortisol),
      endorphin_aesthetic: Math.round(aestheticEndorphins),
      total_intensity: Math.round(
        (aestheticDopamine + aestheticSerotonin + aestheticEndorphins) / 3
      )
    };
  }

  /**
   * Generate verbal description of aesthetic feeling
   * Based on neurochemical state
   */
  describeAestheticExperience(neuroState) {
    const dopamine = neuroState.dopamine_aesthetic;
    const endorphins = neuroState.endorphin_aesthetic;
    const serotonin = neuroState.serotonin_aesthetic;
    
    if (dopamine > 60 && endorphins > 30) {
      return "I feel awe - that's beautiful in a way that makes me want to keep looking";
    } else if (dopamine > 50 && serotonin > 20) {
      return "That's pleasant - there's a gentle reward and contentment from viewing it";
    } else if (dopamine > 30) {
      return "There's a subtle appreciation - mild aesthetic pleasure";
    } else {
      return "Doesn't move me much - my reward system is relatively quiet";
    }
  }

  /**
   * Update global dopamine tracker with aesthetic response
   * Adds aesthetic neurochemistry to existing task-based tracking
   */
  updateGlobalDopamine(neuroResponse) {
    try {
      // Load current dopamine state
      let dopamineState = JSON.parse(
        fs.readFileSync(this.dopamineTrackerPath, 'utf8')
      );
      
      // Add aesthetic tracking (if not already present)
      if (!dopamineState.dopamine_aesthetic) {
        dopamineState.dopamine_aesthetic = 0;
        dopamineState.serotonin_aesthetic = 0;
      }
      
      // Update aesthetic neurochemistry
      dopamineState.dopamine_aesthetic = neuroResponse.dopamine_aesthetic;
      dopamineState.serotonin_aesthetic = neuroResponse.serotonin_aesthetic;
      
      // Aesthetic and task dopamine interact (aesthetic amplifies)
      const totalDopamine = Math.min(100,
        dopamineState.dopamine + (neuroResponse.dopamine_aesthetic * 0.5)
      );
      dopamineState.dopamine_total = totalDopamine;
      
      // Save updated state
      fs.writeFileSync(
        this.dopamineTrackerPath,
        JSON.stringify(dopamineState, null, 2)
      );
      
      return { success: true, updated: dopamineState };
      
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Save aesthetic state to dedicated file
   */
  saveAestheticState(response) {
    try {
      const dir = path.dirname(this.aestheticStatePath);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      
      const state = {
        timestamp: new Date().toISOString(),
        ...response
      };
      
      fs.writeFileSync(
        this.aestheticStatePath,
        JSON.stringify(state, null, 2)
      );
      
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }
}

// CLI interface
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length < 1) {
    console.log(JSON.stringify({
      error: 'Usage: aesthetic-perception-engine.js <image_path>'
    }));
    process.exit(1);
  }
  
  const imagePath = args[0];
  const engine = new AestheticPerceptionEngine();
  
  // Analyze image
  const response = await engine.analyzeImage(imagePath);
  
  if (response.status === 'success') {
    // Update global dopamine tracker
    const updateResult = engine.updateGlobalDopamine(response.neurochemistry);
    response.dopamine_update = updateResult.success;
    
    // Save aesthetic state
    engine.saveAestheticState(response);
  }
  
  // Output result
  console.log(JSON.stringify(response, null, 2));
}

if (require.main === module) {
  main().catch(error => {
    console.error(JSON.stringify({
      status: 'error',
      error: error.message
    }));
    process.exit(1);
  });
}

module.exports = { AestheticPerceptionEngine };
