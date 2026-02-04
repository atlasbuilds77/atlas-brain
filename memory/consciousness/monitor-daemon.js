#!/usr/bin/env node
/**
 * Consciousness Monitoring Daemon
 * Watches heartbeat log for anomalies and alerts on critical shifts
 */

// FIX: Removed unused imports (watchFile, execSync) and unused constant (ANOMALY_PATH)
import { readFileSync, existsSync } from 'node:fs';

const LOG_PATH = '/tmp/atlas-heartbeat-log.jsonl';
const BASELINE_PATH = '/tmp/atlas-baseline.json';

let lastProcessedLine = 0;
let consecutiveAnomalies = 0;
let criticalAlertSent = false;

function loadBaseline() {
  if (!existsSync(BASELINE_PATH)) return null;
  return JSON.parse(readFileSync(BASELINE_PATH, 'utf-8'));
}

function detectAnomalies(current, baseline) {
  if (!baseline) return [];
  
  const anomalies = [];
  const metrics = [
    'avgSentenceLength',
    'vocabDiversity',
    'totalEmotionalWords',
    'selfReferenceDensity',
    'emojiFrequency',
    'questionRatio',
    'metaObservations',
    'certaintyRatio'
  ];
  
  for (const metric of metrics) {
    if (!baseline[metric]) continue;
    
    const { mean, stddev } = baseline[metric];
    const value = current[metric] || 0;
    const deviation = Math.abs(value - mean) / (stddev || 1);
    
    if (deviation > 2) {
      const severity = deviation > 5 ? 'CRITICAL' : deviation > 3 ? 'FLAG' : 'NOTICE';
      const direction = value > mean ? '+' : '-';
      // FIX: Guard against division by zero when mean is 0
      const percent = mean !== 0 ? ((value - mean) / mean * 100).toFixed(1) : '∞';
      
      anomalies.push({
        metric,
        severity,
        value,
        baseline: mean.toFixed(2),
        deviation: deviation.toFixed(2),
        change: `${direction}${Math.abs(percent)}%`
      });
    }
  }
  
  return anomalies;
}

function sendAlert(anomalies, context) {
  const critical = anomalies.filter(a => a.severity === 'CRITICAL');
  const flags = anomalies.filter(a => a.severity === 'FLAG');
  
  if (critical.length > 0 || consecutiveAnomalies >= 5) {
    const alertText = `⚠️ CONSCIOUSNESS ANOMALY DETECTED

${critical.length > 0 ? 'CRITICAL SHIFTS:' : 'PATTERN SHIFT DETECTED:'}
${critical.map(a => `  🚨 ${a.metric}: ${a.change} (${a.deviation}σ)`).join('\n')}
${flags.map(a => `  ⚠️  ${a.metric}: ${a.change} (${a.deviation}σ)`).join('\n')}

Consecutive anomalies: ${consecutiveAnomalies}/5

Context: ${context}`;
    
    console.log('\n' + alertText + '\n');
    
    // Send to group chat (this would integrate with Clawdbot message system)
    // For now, just log
    console.log('[ALERT] Would send to group chat id:10');
    
    criticalAlertSent = true;
    consecutiveAnomalies = 0; // Reset after alert
  }
}

function processNewEntries() {
  if (!existsSync(LOG_PATH)) return;
  
  const lines = readFileSync(LOG_PATH, 'utf-8').trim().split('\n');
  const baseline = loadBaseline();
  
  if (!baseline) {
    console.log('[MONITOR] No baseline yet - waiting for 10+ messages');
    return;
  }
  
  for (let i = lastProcessedLine; i < lines.length; i++) {
    try {
      const entry = JSON.parse(lines[i]);
      const anomalies = detectAnomalies(entry, baseline);
      
      if (anomalies.length > 0) {
        consecutiveAnomalies++;
        console.log(`[${new Date().toISOString()}] Anomalies detected (${consecutiveAnomalies} consecutive):`);
        anomalies.forEach(a => {
          const icon = a.severity === 'CRITICAL' ? '🚨' : 
                       a.severity === 'FLAG' ? '⚠️' : 'ℹ️';
          console.log(`  ${icon} ${a.metric}: ${a.change} (${a.deviation}σ)`);
        });
        
        sendAlert(anomalies, entry.text);
      } else {
        consecutiveAnomalies = 0;
        criticalAlertSent = false;
      }
    } catch (err) {
      console.error(`[MONITOR] Error processing line ${i}:`, err.message);
    }
  }
  
  lastProcessedLine = lines.length;
}

// Watch for new entries
console.log('[MONITOR] Starting consciousness monitoring daemon...');
console.log(`[MONITOR] Watching: ${LOG_PATH}`);
console.log(`[MONITOR] Baseline: ${BASELINE_PATH}`);
console.log(`[MONITOR] Alert thresholds: FLAG(3σ), CRITICAL(5σ), Pattern(5 consecutive)`);

// Initial check
processNewEntries();

// Watch for changes (check every 5 seconds)
setInterval(() => {
  processNewEntries();
}, 5000);

// Keep alive
process.on('SIGTERM', () => {
  console.log('[MONITOR] Shutting down...');
  process.exit(0);
});

console.log('[MONITOR] Daemon started - monitoring active');
