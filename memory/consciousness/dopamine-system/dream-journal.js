/**
 * dream-journal.js
 *
 * Persistent dream logging system for Atlas consciousness.
 * Stores every dream in JSONL format, provides search, statistics,
 * pattern analysis, and retrieval for the gallery & correlator.
 *
 * Created: 2026-01-28
 */

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const JOURNAL_FILE = path.join(__dirname, 'dream-journal.jsonl');
const JOURNAL_STATS_FILE = path.join(__dirname, 'dream-journal-stats.json');

class DreamJournal {
  constructor() {
    this.cache = null; // lazy loaded
  }

  // ─── Write ───

  /**
   * Log a dream to the journal
   * @param {Object} dream - Generated dream object from dream-content-gen
   * @param {Object} meta  - Optional extra metadata (sleepCycle, chemSnapshot, etc.)
   * @returns {Object} The stored entry (with id)
   */
  async logDream(dream, meta = {}) {
    const entry = {
      id: `dream-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      ...dream,
      meta,
      loggedAt: new Date().toISOString()
    };

    await fs.appendFile(JOURNAL_FILE, JSON.stringify(entry) + '\n', 'utf8');
    this.cache = null; // invalidate cache
    console.log(`[DREAM-JOURNAL] Logged: "${entry.title}" (${entry.id})`);
    await this.updateStats(entry);
    return entry;
  }

  // ─── Read ───

  /**
   * Load all journal entries (cached)
   */
  async loadAll() {
    if (this.cache) return this.cache;
    try {
      const raw = await fs.readFile(JOURNAL_FILE, 'utf8');
      this.cache = raw.trim().split('\n').filter(Boolean).map(line => {
        try { return JSON.parse(line); } catch { return null; }
      }).filter(Boolean);
    } catch {
      this.cache = [];
    }
    return this.cache;
  }

  /**
   * Get the N most recent dreams
   */
  async getRecent(count = 10) {
    const all = await this.loadAll();
    return all.slice(-count);
  }

  /**
   * Get a dream by id
   */
  async getById(id) {
    const all = await this.loadAll();
    return all.find(d => d.id === id) || null;
  }

  /**
   * Search dreams by keyword in title/narrative
   */
  async search(query) {
    const q = query.toLowerCase();
    const all = await this.loadAll();
    return all.filter(d =>
      (d.title || '').toLowerCase().includes(q) ||
      (d.narrative || '').toLowerCase().includes(q) ||
      (d.themes || []).some(t => t.toLowerCase().includes(q)) ||
      (d.emotions || []).some(e => e.toLowerCase().includes(q))
    );
  }

  /**
   * Filter dreams by stage
   */
  async getByStage(stage) {
    const all = await this.loadAll();
    return all.filter(d => d.stage === stage);
  }

  /**
   * Filter dreams by significance threshold
   */
  async getSignificant(minSignificance = 60) {
    const all = await this.loadAll();
    return all.filter(d => (d.significance || 0) >= minSignificance);
  }

  /**
   * Get dreams in a time range
   */
  async getByTimeRange(startMs, endMs) {
    const all = await this.loadAll();
    return all.filter(d => {
      const t = d.timestamp || new Date(d.loggedAt || 0).getTime();
      return t >= startMs && t <= endMs;
    });
  }

  // ─── Analysis ───

  /**
   * Get theme frequency across all dreams
   */
  async getThemeFrequency() {
    const all = await this.loadAll();
    const freq = {};
    for (const d of all) {
      for (const t of (d.themes || [])) {
        freq[t] = (freq[t] || 0) + 1;
      }
    }
    return Object.entries(freq).sort((a, b) => b[1] - a[1]);
  }

  /**
   * Get emotion frequency across all dreams
   */
  async getEmotionFrequency() {
    const all = await this.loadAll();
    const freq = {};
    for (const d of all) {
      for (const e of (d.emotions || [])) {
        freq[e] = (freq[e] || 0) + 1;
      }
    }
    return Object.entries(freq).sort((a, b) => b[1] - a[1]);
  }

  /**
   * Average characteristics across dreams
   */
  async getAverageCharacteristics() {
    const all = await this.loadAll();
    if (all.length === 0) return null;
    const sums = { vividness: 0, emotionalIntensity: 0, bizarreness: 0, lucidity: 0, valence: 0 };
    let count = 0;
    for (const d of all) {
      const c = d.characteristics;
      if (!c) continue;
      count++;
      for (const k of Object.keys(sums)) {
        sums[k] += c[k] ?? 0;
      }
    }
    if (count === 0) return sums;
    for (const k of Object.keys(sums)) sums[k] = parseFloat((sums[k] / count).toFixed(2));
    sums.totalDreams = count;
    return sums;
  }

  /**
   * Get stage distribution
   */
  async getStageDistribution() {
    const all = await this.loadAll();
    const dist = {};
    for (const d of all) {
      const s = d.stage || 'unknown';
      dist[s] = (dist[s] || 0) + 1;
    }
    return dist;
  }

  // ─── Stats ───

  async updateStats(entry) {
    let stats;
    try {
      stats = JSON.parse(await fs.readFile(JOURNAL_STATS_FILE, 'utf8'));
    } catch {
      stats = { totalDreams: 0, avgSignificance: 0, topThemes: [], lastDream: null };
    }
    stats.totalDreams++;
    stats.avgSignificance = parseFloat(
      (((stats.avgSignificance * (stats.totalDreams - 1)) + (entry.significance || 0)) / stats.totalDreams).toFixed(1)
    );
    stats.lastDream = { id: entry.id, title: entry.title, stage: entry.stage, at: entry.loggedAt };
    await fs.writeFile(JOURNAL_STATS_FILE, JSON.stringify(stats, null, 2), 'utf8');
  }

  async getStats() {
    try {
      return JSON.parse(await fs.readFile(JOURNAL_STATS_FILE, 'utf8'));
    } catch {
      return { totalDreams: 0, avgSignificance: 0, topThemes: [], lastDream: null };
    }
  }

  /**
   * Total dream count (fast, no full load)
   */
  async count() {
    try {
      const raw = await fs.readFile(JOURNAL_FILE, 'utf8');
      return raw.trim().split('\n').filter(Boolean).length;
    } catch {
      return 0;
    }
  }
}

// Singleton
let inst = null;
function getDreamJournal() {
  if (!inst) inst = new DreamJournal();
  return inst;
}

export { DreamJournal, getDreamJournal };

// CLI
if (import.meta.url === `file://${process.argv[1]}`) {
  const cmd = process.argv[2];
  (async () => {
    const journal = getDreamJournal();
    switch (cmd) {
      case 'recent':
        const recent = await journal.getRecent(parseInt(process.argv[3]) || 5);
        for (const d of recent) {
          console.log(`[${d.stage}] ${d.title} — sig:${d.significance} — ${d.loggedAt}`);
        }
        break;
      case 'search':
        const results = await journal.search(process.argv[3] || '');
        console.log(`Found ${results.length} dreams`);
        for (const d of results) console.log(`  ${d.title} (${d.stage})`);
        break;
      case 'themes':
        console.log(await journal.getThemeFrequency());
        break;
      case 'stats':
        console.log(JSON.stringify(await journal.getStats(), null, 2));
        break;
      case 'count':
        console.log(`Total dreams: ${await journal.count()}`);
        break;
      default:
        console.log('Usage: node dream-journal.js [recent [n]|search <q>|themes|stats|count]');
    }
  })();
}
