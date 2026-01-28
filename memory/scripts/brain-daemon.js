const fs = require('fs').promises;
const path = require('path');

async function scanMemory() {
  const files = [];
  async function walk(dir) {
    const entries = await fs.readdir(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) await walk(fullPath);
      else if (entry.name.endsWith('.md')) files.push(fullPath);
    }
  }
  await walk('memory');
  return files;
}

async function run() {
  console.log('Brain daemon started - scanning every 1s');
  setInterval(async () => {
    try {
      const files = await scanMemory();
      await fs.writeFile('/tmp/atlas-memory-index.json', JSON.stringify({ files, timestamp: Date.now() }));
      console.log(`Scanned ${files.length} files`);
    } catch (err) {
      console.error('Scan error:', err);
    }
  }, 1000);
}

run();
