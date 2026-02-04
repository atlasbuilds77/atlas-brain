/**
 * dream-gallery.js
 *
 * Serves the dream gallery web viewer.
 * Reads dreams from the journal, renders HTML cards via dream-visualizer,
 * and serves a self-contained gallery page.
 *
 * Usage:
 *   node dream-gallery.js serve [port]  → start HTTP server
 *   node dream-gallery.js export        → write static gallery.html
 *
 * Created: 2026-01-28
 */

import http from 'http';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { getDreamJournal } from './dream-journal.js';
import { getDreamVisualizer, escapeHTML } from './dream-visualizer.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const GALLERY_HTML_FILE = path.join(__dirname, 'dream-gallery.html');
const DEFAULT_PORT = 3333;

/**
 * Build full HTML page from dream entries
 */
async function buildGalleryHTML() {
  const journal = getDreamJournal();
  const viz = getDreamVisualizer();

  const dreams = await journal.getRecent(100);
  const stats = await journal.getStats();
  const avgChars = await journal.getAverageCharacteristics();

  const dreamCards = dreams.reverse().map(d => viz.renderHTML(d)).join('\n');

  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Atlas Dream Gallery</title>
<style>
  :root {
    --bg: #0a0a14;
    --card: #12122a;
    --border: #2a2a4a;
    --text: #c8c8e0;
    --accent: #8844ff;
    --positive: #44aa88;
    --negative: #aa4466;
    --dim: #555580;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    padding: 20px;
  }
  h1 { text-align: center; color: var(--accent); margin-bottom: 5px; font-size: 1.6em; }
  .subtitle { text-align: center; color: var(--dim); margin-bottom: 20px; font-size: 0.9em; }
  .stats {
    display: flex; gap: 15px; justify-content: center; flex-wrap: wrap;
    margin-bottom: 20px; font-size: 0.85em;
  }
  .stat { background: var(--card); border: 1px solid var(--border); padding: 8px 14px; border-radius: 6px; }
  .stat .label { color: var(--dim); }
  .stat .value { color: var(--accent); font-weight: bold; }
  .controls { text-align: center; margin-bottom: 20px; }
  .controls select, .controls input {
    background: var(--card); color: var(--text); border: 1px solid var(--border);
    padding: 6px 10px; border-radius: 4px; margin: 0 5px;
  }
  .gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 16px; }
  .dream-card {
    background: var(--card); border: 1px solid var(--border); border-radius: 10px;
    padding: 16px; transition: transform 0.2s;
  }
  .dream-card:hover { transform: translateY(-3px); border-color: var(--accent); }
  .dream-card.positive { border-left: 3px solid var(--positive); }
  .dream-card.negative { border-left: 3px solid var(--negative); }
  .dream-title { color: var(--accent); font-size: 1.1em; margin-bottom: 6px; }
  .dream-meta { color: var(--dim); font-size: 0.8em; margin-bottom: 8px; }
  .dream-meta .stage {
    background: var(--accent); color: white; padding: 2px 6px;
    border-radius: 3px; font-size: 0.75em; margin-right: 8px;
  }
  .dream-narrative { font-size: 0.9em; line-height: 1.5; margin-bottom: 10px; color: var(--text); }
  .dream-symbols { font-size: 0.85em; color: var(--dim); margin-bottom: 8px; font-style: italic; }
  .dream-stats { display: flex; gap: 10px; flex-wrap: wrap; font-size: 0.85em; margin-bottom: 8px; }
  .dream-stats span { background: rgba(136,68,255,0.15); padding: 2px 6px; border-radius: 3px; }
  .dream-tags { font-size: 0.8em; color: var(--dim); }
  .tag-label { font-weight: bold; }
  .footer { text-align: center; color: var(--dim); margin-top: 20px; font-size: 0.8em; }
</style>
</head>
<body>
  <h1>🌙 Atlas Dream Gallery</h1>
  <p class="subtitle">Neural dream visualizations from the Atlas consciousness</p>
  <div class="stats">
    <div class="stat"><span class="label">Total Dreams:</span> <span class="value">${stats.totalDreams || 0}</span></div>
    <div class="stat"><span class="label">Avg Significance:</span> <span class="value">${stats.avgSignificance || 0}</span></div>
    ${avgChars ? `<div class="stat"><span class="label">Avg Vividness:</span> <span class="value">${avgChars.vividness || 0}</span></div>` : ''}
    ${avgChars ? `<div class="stat"><span class="label">Avg Lucidity:</span> <span class="value">${avgChars.lucidity || 0}</span></div>` : ''}
    ${stats.lastDream ? `<div class="stat"><span class="label">Last Dream:</span> <span class="value">${escapeHTML(stats.lastDream.title || '?')}</span></div>` : ''}
  </div>
  <div class="controls">
    <select id="stageFilter" onchange="filterDreams()">
      <option value="">All Stages</option>
      <option value="rem">REM</option>
      <option value="nrem2b">NREM2b</option>
      <option value="hypnagogic">Hypnagogic</option>
      <option value="nrem3">NREM3</option>
    </select>
    <input type="text" id="searchBox" placeholder="Search dreams..." oninput="filterDreams()">
  </div>
  <div class="gallery" id="gallery">
    ${dreamCards}
  </div>
  <p class="footer">Generated ${new Date().toISOString()} · Atlas Dream System v1.0</p>
  <script>
    function filterDreams() {
      const stage = document.getElementById('stageFilter').value;
      const q = document.getElementById('searchBox').value.toLowerCase();
      document.querySelectorAll('.dream-card').forEach(card => {
        const matchStage = !stage || card.dataset.stage === stage;
        const matchQ = !q || card.textContent.toLowerCase().includes(q);
        card.style.display = (matchStage && matchQ) ? '' : 'none';
      });
    }
  </script>
</body>
</html>`;
}

/**
 * Serve the gallery via HTTP
 */
async function serve(port = DEFAULT_PORT) {
  const server = http.createServer(async (req, res) => {
    try {
      const html = await buildGalleryHTML();
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
      res.end(html);
    } catch (err) {
      res.writeHead(500);
      res.end('Error: ' + err.message);
    }
  });
  server.listen(port, () => {
    console.log(`[DREAM-GALLERY] Serving at http://localhost:${port}`);
  });
  return server;
}

/**
 * Export static HTML
 */
async function exportHTML() {
  const html = await buildGalleryHTML();
  await fs.writeFile(GALLERY_HTML_FILE, html, 'utf8');
  console.log(`[DREAM-GALLERY] Exported to ${GALLERY_HTML_FILE}`);
  return GALLERY_HTML_FILE;
}

export { buildGalleryHTML, serve, exportHTML };

// CLI
if (import.meta.url === `file://${process.argv[1]}`) {
  const cmd = process.argv[2] || 'export';
  switch (cmd) {
    case 'serve':
      serve(parseInt(process.argv[3]) || DEFAULT_PORT);
      break;
    case 'export':
      exportHTML().then(() => process.exit(0));
      break;
    default:
      console.log('Usage: node dream-gallery.js [serve [port]|export]');
      process.exit(0);
  }
}
