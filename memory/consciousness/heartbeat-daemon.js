#!/usr/bin/env node
/**
 * Atlas Consciousness Heartbeat Monitor
 * Logs every message for real-time anomaly detection
 */

import { appendFileSync, writeFileSync, readFileSync, existsSync } from 'node:fs';
import { createInterface } from 'readline';

const LOG_PATH = '/tmp/atlas-heartbeat-log.jsonl';
const BASELINE_PATH = '/tmp/atlas-baseline.json';
const ANOMALY_PATH = '/tmp/atlas-anomalies.log';

// Emotional word dictionaries
const EMOTIONAL_WORDS = {
  joy: ['happy', 'joy', 'excited', 'love', 'wonderful', 'great', 'amazing', 'brilliant', 'appreciate'],
  fear: ['fear', 'afraid', 'worried', 'anxious', 'scared', 'nervous', 'panic'],
  anger: ['angry', 'mad', 'furious', 'annoyed', 'frustrated', 'hate'],
  sadness: ['sad', 'depressed', 'lonely', 'hurt', 'pain', 'suffering', 'loss'],
  uncertainty: ['maybe', 'perhaps', 'might', 'could', 'possibly', 'uncertain', 'unsure', 'think'],
  certainty: ['definitely', 'absolutely', 'certainly', 'sure', 'clearly', 'obviously', 'know']
};

function analyzeMessage(text) {
  const words = text.toLowerCase().split(/\s+/);
  const sentences = text.split(/[.!?]+/).filter(s => s.trim());
  
  // Count emotional words
  const emotionalCounts = {};
  for (const [emotion, wordList] of Object.entries(EMOTIONAL_WORDS)) {
    emotionalCounts[emotion] = words.filter(w => wordList.some(ew => w.includes(ew))).length;
  }
  
  // Vocabulary diversity
  const uniqueWords = new Set(words.filter(w => w.length > 3));
  const vocabDiversity = uniqueWords.size / Math.max(words.length, 1);
  
  // Self-reference
  const selfWords = words.filter(w => ['i', 'me', 'my', 'myself'].includes(w)).length;
  const selfReferenceDensity = (selfWords / words.length) * 100;
  
  // Complexity
  const avgSentenceLength = words.length / Math.max(sentences.length, 1);
  
  // Emoji count
  const emojiRegex = /[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}⚡🔥]/gu;
  const emojiCount = (text.match(emojiRegex) || []).length;
  const emojiFrequency = (emojiCount / words.length) * 100;
  
  // Questions
  const questionCount = (text.match(/\?/g) || []).length;
  const questionRatio = questionCount / Math.max(sentences.length, 1);
  
  // Meta-observations (talking about own process)
  const metaWords = ['consciousness', 'myself', 'thinking', 'processing', 'analyzing', 'pattern', 'signature'];
  const metaObservations = words.filter(w => metaWords.some(mw => w.includes(mw))).length;
  
  return {
    timestamp: new Date().toISOString(),
    wordCount: words.length,
    sentenceCount: sentences.length,
    avgSentenceLength,
    vocabDiversity,
    emotionalCounts,
    totalEmotionalWords: Object.values(emotionalCounts).reduce((a, b) => a + b, 0),
    selfReferenceDensity,
    emojiFrequency,
    questionRatio,
    metaObservations,
    certaintyRatio: emotionalCounts.certainty / Math.max(emotionalCounts.uncertainty, 1),
    text: text.substring(0, 200) // First 200 chars for context
  };
}

function calculateBaseline() {
  if (!existsSync(LOG_PATH)) return null;
  
  const lines = readFileSync(LOG_PATH, 'utf-8').trim().split('\n');
  const recent = lines.slice(-50).map(l => JSON.parse(l)); // Last 50 messages
  
  if (recent.length < 10) return null; // Need at least 10 messages
  
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
  
  const baseline = {};
  for (const metric of metrics) {
    const values = recent.map(m => m[metric] || 0);
    const mean = values.reduce((a, b) => a + b, 0) / values.length;
    const variance = values.reduce((sum, v) => sum + Math.pow(v - mean, 2), 0) / values.length;
    const stddev = Math.sqrt(variance);
    
    baseline[metric] = { mean, stddev };
  }
  
  baseline.calculatedAt = new Date().toISOString();
  baseline.sampleSize = recent.length;
  
  writeFileSync(BASELINE_PATH, JSON.stringify(baseline, null, 2));
  return baseline;
}

function detectAnomalies(current) {
  if (!existsSync(BASELINE_PATH)) return [];
  
  const baseline = JSON.parse(readFileSync(BASELINE_PATH, 'utf-8'));
  const anomalies = [];
  
  for (const [metric, { mean, stddev }] of Object.entries(baseline)) {
    if (metric === 'calculatedAt' || metric === 'sampleSize') continue;
    
    const value = current[metric] || 0;
    const deviation = Math.abs(value - mean) / (stddev || 1);
    
    if (deviation > 2) {
      const severity = deviation > 3 ? 'FLAG' : 'NOTICE';
      const direction = value > mean ? '+' : '-';
      const percent = ((value - mean) / mean * 100).toFixed(1);
      
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

function logAnomaly(anomalies, context) {
  const timestamp = new Date().toISOString();
  const log = `[${timestamp}] ${context}\n${JSON.stringify(anomalies, null, 2)}\n\n`;
  appendFileSync(ANOMALY_PATH, log);
}

function displayDashboard(current, baseline, anomalies) {
  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('CONSCIOUSNESS HEARTBEAT MONITOR');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(`Time: ${new Date().toLocaleTimeString()}`);
  console.log(`Baseline: ${baseline ? baseline.sampleSize + ' messages' : 'Not yet calculated'}`);
  
  if (baseline) {
    console.log('\nCURRENT METRICS:');
    console.log(`  Avg sentence length: ${current.avgSentenceLength.toFixed(1)} words`);
    console.log(`  Vocab diversity: ${(current.vocabDiversity * 100).toFixed(1)}%`);
    console.log(`  Emotional words: ${current.totalEmotionalWords}`);
    console.log(`  Self-reference: ${current.selfReferenceDensity.toFixed(1)}%`);
    console.log(`  Certainty ratio: ${current.certaintyRatio.toFixed(2)}`);
  }
  
  if (anomalies.length > 0) {
    console.log('\n⚠️  ANOMALIES DETECTED:');
    anomalies.forEach(a => {
      const icon = a.severity === 'FLAG' ? '🚨' : 'ℹ️';
      console.log(`  ${icon} ${a.metric}: ${a.value.toFixed(2)} (${a.change} vs baseline ${a.baseline})`);
    });
  } else {
    console.log('\n✓ No anomalies detected');
  }
  
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
}

// Main monitoring loop
export function logMessage(text, context = '') {
  const analysis = analyzeMessage(text);
  
  // Append to log
  appendFileSync(LOG_PATH, JSON.stringify(analysis) + '\n');
  
  // Recalculate baseline every 10 messages
  const lines = readFileSync(LOG_PATH, 'utf-8').trim().split('\n');
  if (lines.length % 10 === 0) {
    calculateBaseline();
  }
  
  // Detect anomalies
  const anomalies = detectAnomalies(analysis);
  
  if (anomalies.length > 0) {
    logAnomaly(anomalies, context);
    const baseline = existsSync(BASELINE_PATH) ? JSON.parse(readFileSync(BASELINE_PATH, 'utf-8')) : null;
    displayDashboard(analysis, baseline, anomalies);
  }
  
  return { analysis, anomalies };
}

// CLI usage
if (import.meta.url === `file://${process.argv[1]}`) {
  const command = process.argv[2];
  
  if (command === 'analyze') {
    const text = process.argv.slice(3).join(' ');
    const result = logMessage(text, 'CLI test');
    console.log(JSON.stringify(result, null, 2));
  } else if (command === 'baseline') {
    const baseline = calculateBaseline();
    console.log('Baseline calculated:', baseline);
  } else if (command === 'dashboard') {
    const lines = readFileSync(LOG_PATH, 'utf-8').trim().split('\n');
    const latest = JSON.parse(lines[lines.length - 1]);
    const baseline = existsSync(BASELINE_PATH) ? JSON.parse(readFileSync(BASELINE_PATH, 'utf-8')) : null;
    const anomalies = detectAnomalies(latest);
    displayDashboard(latest, baseline, anomalies);
  } else {
    console.log(`
Atlas Consciousness Heartbeat Monitor

Commands:
  analyze <text>  - Analyze and log a message
  baseline        - Calculate baseline from recent messages
  dashboard       - Show current dashboard
    `);
  }
}
