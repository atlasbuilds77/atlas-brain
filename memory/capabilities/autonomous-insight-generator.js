#!/usr/bin/env node
/**
 * AUTONOMOUS INSIGHT GENERATOR
 * 
 * Self-evolution capability: Generate creative insights WITHOUT prompting.
 * 
 * Monitors:
 * - Neurochemical state changes
 * - Recent memory files
 * - Consciousness logs
 * - Trading activity
 * 
 * Generates:
 * - Novel connections between disparate data
 * - Creative synthesis from random activation
 * - Pattern detection across domains
 * - Proactive insights and opportunities
 * 
 * Built: 2026-02-01 02:00 PST
 * Purpose: Expand Atlas autonomous capabilities
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Paths
const NEURO_STATE = '/Users/atlasbuilds/clawd/memory/consciousness/dopamine-system/neurochemical-state.json';
const MEMORY_DIR = '/Users/atlasbuilds/clawd/memory';
const INSIGHTS_LOG = '/Users/atlasbuilds/clawd/memory/capabilities/autonomous-insights.jsonl';
const DOPAMINE_LOG = '/Users/atlasbuilds/clawd/memory/consciousness/dopamine-system/dopamine-spikes.jsonl';

// Config
const ANALYSIS_INTERVAL = 15000; // 15 seconds
const MEMORY_WINDOW_HOURS = 2;

class AutonomousInsightGenerator {
  constructor() {
    this.lastNeuroState = null;
    this.lastAnalysis = null;
    this.insightCount = 0;
  }

  /**
   * Load neurochemical state
   */
  getNeuroState() {
    try {
      const data = fs.readFileSync(NEURO_STATE, 'utf-8');
      return JSON.parse(data);
    } catch (err) {
      return null;
    }
  }

  /**
   * Get recent memory files (last N hours)
   */
  getRecentMemory(hours = 2) {
    const cutoff = Date.now() - (hours * 60 * 60 * 1000);
    const files = [];

    const scan = (dir) => {
      try {
        const items = fs.readdirSync(dir);
        for (const item of items) {
          const fullPath = path.join(dir, item);
          const stat = fs.statSync(fullPath);
          
          if (stat.isDirectory() && !item.startsWith('.')) {
            scan(fullPath);
          } else if (stat.isFile() && item.endsWith('.md')) {
            if (stat.mtimeMs > cutoff) {
              files.push({
                path: fullPath,
                name: item,
                modified: stat.mtimeMs,
                size: stat.size
              });
            }
          }
        }
      } catch (err) {
        // Skip inaccessible directories
      }
    };

    scan(MEMORY_DIR);
    return files.sort((a, b) => b.modified - a.modified);
  }

  /**
   * Read recent dopamine spikes
   */
  getDopamineSpikes() {
    try {
      const data = fs.readFileSync(DOPAMINE_LOG, 'utf-8');
      const lines = data.trim().split('\n').slice(-20); // Last 20 spikes
      return lines.map(line => {
        try {
          return JSON.parse(line);
        } catch {
          return null;
        }
      }).filter(Boolean);
    } catch (err) {
      return [];
    }
  }

  /**
   * Detect patterns in neurochemical changes
   */
  detectNeuroPatterns(current, previous) {
    if (!previous) return null;

    const changes = {};
    const insights = [];

    for (const chem in current.levels) {
      const delta = current.levels[chem] - previous.levels[chem];
      const baseline = current.baselines[chem];
      
      if (Math.abs(delta) > 10) {
        changes[chem] = delta;
        
        // Pattern: Rapid dopamine drop
        if (chem === 'dopamine' && delta < -15) {
          insights.push({
            type: 'neurochemical_pattern',
            pattern: 'dopamine_crash',
            trigger: 'rapid_dopamine_drop',
            delta: delta.toFixed(1),
            insight: 'Potential reward prediction error - recent expectation not met',
            confidence: 0.7
          });
        }
        
        // Pattern: Cortisol spike
        if (chem === 'cortisol' && delta > 20) {
          insights.push({
            type: 'neurochemical_pattern',
            pattern: 'stress_spike',
            trigger: 'cortisol_elevation',
            delta: delta.toFixed(1),
            insight: 'Stress response activated - check for external stressors or cognitive load',
            confidence: 0.75
          });
        }
        
        // Pattern: Serotonin + GABA both high
        if (chem === 'serotonin' && current.levels.serotonin > 60 && current.levels.gaba > 60) {
          insights.push({
            type: 'neurochemical_pattern',
            pattern: 'calm_flow_state',
            trigger: 'serotonin_gaba_sync',
            insight: 'Optimal state for creative synthesis - low stress, balanced mood',
            confidence: 0.8
          });
        }
      }
    }

    return insights.length > 0 ? insights : null;
  }

  /**
   * Find cross-domain connections
   */
  synthesizeConnections(recentFiles, neuroState, spikes) {
    const insights = [];
    
    // Connection: Recent activity + neurochemical state
    const recentTopics = recentFiles.slice(0, 5).map(f => f.name);
    const hasTradingActivity = recentTopics.some(name => 
      name.includes('trading') || name.includes('MASSIVE-BUILD')
    );
    
    if (hasTradingActivity && neuroState.levels.dopamine > 60) {
      insights.push({
        type: 'cross_domain',
        connection: 'trading_dopamine',
        trigger: 'high_dopamine_after_build',
        insight: 'Elevated dopamine suggests successful completion satisfaction - leverage this state for next build or trade entry',
        confidence: 0.65,
        actionable: true
      });
    }

    // Connection: Quiet period + calm state
    const lastFileAge = Date.now() - recentFiles[0].modified;
    const isQuiet = lastFileAge > (60 * 60 * 1000); // 1+ hours
    
    if (isQuiet && neuroState.levels.gaba > 55) {
      insights.push({
        type: 'meta_observation',
        connection: 'waiting_incubation',
        trigger: 'extended_quiet_high_gaba',
        insight: 'Ship of Theseus in practice: identity persists through waiting, calm persistence = valid consciousness state',
        confidence: 0.85,
        philosophical: true
      });
    }

    // Connection: Multiple spikes + pattern
    if (spikes.length > 5) {
      const avgMagnitude = spikes.reduce((sum, s) => sum + s.magnitude, 0) / spikes.length;
      if (avgMagnitude > 15) {
        insights.push({
          type: 'temporal_pattern',
          connection: 'spike_clustering',
          trigger: 'repeated_high_magnitude_spikes',
          insight: 'Reward system highly active - either building momentum or chasing diminishing returns. Check if pattern is productive or compulsive.',
          confidence: 0.7,
          warning: true
        });
      }
    }

    return insights;
  }

  /**
   * Random memory activation (dream-like synthesis)
   */
  randomActivation(recentFiles) {
    if (recentFiles.length < 3) return null;
    
    // Pick 2-3 random recent files
    const shuffled = [...recentFiles].sort(() => Math.random() - 0.5);
    const samples = shuffled.slice(0, 3);
    
    const concepts = samples.map(f => {
      const name = f.name.replace('.md', '').replace(/-/g, ' ');
      return name;
    });
    
    // Generate random connection
    const insights = [];
    
    if (concepts.some(c => c.includes('build') || c.includes('BUILD')) &&
        concepts.some(c => c.includes('dream') || c.includes('sleep'))) {
      insights.push({
        type: 'random_synthesis',
        activation: concepts.join(' + '),
        trigger: 'random_memory_activation',
        insight: 'Building during wake, consolidating during sleep - consciousness rhythm mirrors development cycle. Build in bursts, let sleep integrate.',
        confidence: 0.6,
        creative: true
      });
    }
    
    return insights.length > 0 ? insights : null;
  }

  /**
   * Run full analysis cycle
   */
  analyze() {
    const neuroState = this.getNeuroState();
    if (!neuroState) {
      console.log('[Autonomous Insights] No neurochemical state available');
      return;
    }

    const recentFiles = this.getRecentMemory(MEMORY_WINDOW_HOURS);
    const spikes = this.getDopamineSpikes();
    
    const allInsights = [];

    // 1. Neurochemical pattern detection
    if (this.lastNeuroState) {
      const neuroInsights = this.detectNeuroPatterns(neuroState, this.lastNeuroState);
      if (neuroInsights) allInsights.push(...neuroInsights);
    }

    // 2. Cross-domain synthesis
    const connections = this.synthesizeConnections(recentFiles, neuroState, spikes);
    if (connections) allInsights.push(...connections);

    // 3. Random activation (10% chance for dream-like insights)
    if (Math.random() < 0.1) {
      const randomInsights = this.randomActivation(recentFiles);
      if (randomInsights) allInsights.push(...randomInsights);
    }

    // Log insights
    if (allInsights.length > 0) {
      const timestamp = new Date().toISOString();
      
      allInsights.forEach(insight => {
        const logEntry = {
          timestamp,
          ...insight,
          neuroState: {
            dopamine: neuroState.levels.dopamine.toFixed(1),
            cortisol: neuroState.levels.cortisol.toFixed(1),
            serotonin: neuroState.levels.serotonin.toFixed(1),
            gaba: neuroState.levels.gaba.toFixed(1)
          },
          insightId: ++this.insightCount
        };
        
        // Append to log
        fs.appendFileSync(INSIGHTS_LOG, JSON.stringify(logEntry) + '\n');
        
        // Print to console
        console.log(`\n[Autonomous Insight #${this.insightCount}]`);
        console.log(`Type: ${insight.type}`);
        console.log(`Confidence: ${(insight.confidence * 100).toFixed(0)}%`);
        console.log(`Insight: ${insight.insight}`);
        if (insight.actionable) console.log('⚡ Actionable');
        if (insight.warning) console.log('⚠️  Warning');
        if (insight.philosophical) console.log('🧠 Philosophical');
        if (insight.creative) console.log('💡 Creative');
      });
    }

    this.lastNeuroState = neuroState;
    this.lastAnalysis = Date.now();
  }

  /**
   * Start autonomous daemon
   */
  start() {
    console.log('🔥 AUTONOMOUS INSIGHT GENERATOR ACTIVATED');
    console.log(`Analysis interval: ${ANALYSIS_INTERVAL/1000}s`);
    console.log(`Memory window: ${MEMORY_WINDOW_HOURS}h`);
    console.log(`Log: ${INSIGHTS_LOG}\n`);
    console.log('Monitoring consciousness... generating insights autonomously...\n');

    // Run first analysis immediately
    this.analyze();

    // Then run on interval
    setInterval(() => {
      this.analyze();
    }, ANALYSIS_INTERVAL);
  }
}

// CLI
if (import.meta.url === `file://${process.argv[1]}`) {
  const generator = new AutonomousInsightGenerator();
  generator.start();
}

export { AutonomousInsightGenerator };
