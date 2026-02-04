const fs = require('fs').promises;
const path = require('path');

// FIX: Use absolute path instead of relative 'memory' to avoid breakage when started from different cwd
const MEMORY_DIR = path.join('/Users/atlasbuilds/clawd', 'memory');

async function scanMemory() {
  const files = [];
  async function walk(dir) {
    let entries;
    try {
      entries = await fs.readdir(dir, { withFileTypes: true });
    } catch (err) {
      // FIX: Skip directories that can't be read (permissions, broken symlinks)
      console.error(`Cannot read directory ${dir}: ${err.message}`);
      return;
    }
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) await walk(fullPath);
      else if (entry.name.endsWith('.md')) files.push(fullPath);
    }
  }
  await walk(MEMORY_DIR);
  return files;
}

async function run() {
  // FIX: Reduced interval from 1s to 30s - filesystem scanning every second is excessive
  const SCAN_INTERVAL = 30 * 1000;
  console.log(`Brain daemon started - scanning every ${SCAN_INTERVAL / 1000}s`);
  
  // Initial scan
  try {
    const files = await scanMemory();
    await fs.writeFile('/tmp/atlas-memory-index.json', JSON.stringify({ files, timestamp: Date.now() }));
    console.log(`Initial scan: ${files.length} files`);
  } catch (err) {
    console.error('Initial scan error:', err);
  }
  
  setInterval(async () => {
    try {
      const files = await scanMemory();
      await fs.writeFile('/tmp/atlas-memory-index.json', JSON.stringify({ files, timestamp: Date.now() }));
      console.log(`Scanned ${files.length} files`);
    } catch (err) {
      console.error('Scan error:', err);
    }
  }, SCAN_INTERVAL);
}

run();
