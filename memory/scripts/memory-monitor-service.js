#!/usr/bin/env node

/**
 * Memory Monitor Service
 * Continuously watches memory/ directory and updates index
 * Runs in background to support live brain visualization
 */

const fs = require('fs');
const path = require('path');
const { generateIndex } = require('./generate-memory-index.js');

const WATCH_INTERVAL = 10000; // 10 seconds
const MEMORY_DIR = path.join(__dirname, '..');

console.log('🧠 Atlas Memory Monitor starting...');
console.log(`   Watching: ${MEMORY_DIR}`);
console.log(`   Update interval: ${WATCH_INTERVAL}ms`);

let lastFileCount = 0;
let lastModified = new Date();

function monitorMemory() {
    try {
        // Generate index
        generateIndex();
        
        // Read back to check
        const indexPath = '/tmp/atlas-memory-index.json';
        if (fs.existsSync(indexPath)) {
            const index = JSON.parse(fs.readFileSync(indexPath, 'utf8'));
            const fileCount = index.totalFiles;
            
            if (fileCount !== lastFileCount) {
                console.log(`📈 File count changed: ${lastFileCount} → ${fileCount}`);
                lastFileCount = fileCount;
            }
            
            lastModified = new Date();
        }
    } catch (err) {
        console.error('❌ Monitor error:', err.message);
    }
}

// Initial scan
monitorMemory();

// Continuous monitoring
setInterval(monitorMemory, WATCH_INTERVAL);

console.log('✅ Monitor active - scanning every 10 seconds');
console.log('   Press Ctrl+C to stop');

// Keep alive
process.on('SIGINT', () => {
    console.log('\n🛑 Stopping memory monitor...');
    process.exit(0);
});
