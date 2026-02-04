#!/usr/bin/env node
/**
 * ATLAS BRAIN GROWTH MONITOR
 * Watches memory/ folder for new .md files and updates index for brain visualization
 */

const fs = require('fs');
const path = require('path');

const MEMORY_DIR = path.join(__dirname, '..');
const INDEX_FILE = '/tmp/atlas-memory-index.json';
const SCAN_INTERVAL = 10000; // 10 seconds

let knownFiles = new Set();
let fileMetadata = {};

// Initialize from existing index if available
function loadExistingIndex() {
    try {
        if (fs.existsSync(INDEX_FILE)) {
            const data = JSON.parse(fs.readFileSync(INDEX_FILE, 'utf8'));
            knownFiles = new Set(data.files.map(f => f.path));
            data.files.forEach(f => fileMetadata[f.path] = f);
            console.log(`📚 Loaded ${knownFiles.size} known files from index`);
        }
    } catch (err) {
        console.log('⚠️  Could not load existing index, starting fresh');
    }
}

// Recursively scan memory directory for .md files
function scanMemoryDir(dir = MEMORY_DIR, relativePath = '') {
    const files = [];
    
    try {
        const entries = fs.readdirSync(dir, { withFileTypes: true });
        
        for (const entry of entries) {
            const fullPath = path.join(dir, entry.name);
            const relPath = path.join(relativePath, entry.name);
            
            // Skip visuals directory and hidden files
            if (entry.name.startsWith('.') || entry.name === 'visuals') {
                continue;
            }
            
            if (entry.isDirectory()) {
                files.push(...scanMemoryDir(fullPath, relPath));
            } else if (entry.name.endsWith('.md')) {
                const stats = fs.statSync(fullPath);
                files.push({
                    path: `memory/${relPath}`,
                    name: entry.name.replace('.md', ''),
                    size: stats.size,
                    created: stats.birthtime,
                    modified: stats.mtime,
                    type: detectFileType(relPath)
                });
            }
        }
    } catch (err) {
        console.error(`Error scanning ${dir}:`, err.message);
    }
    
    return files;
}

function detectFileType(filepath) {
    if (filepath.includes('protocols/')) return 'protocol';
    if (filepath.includes('trading/')) return 'trading';
    if (filepath.includes('people/')) return 'people';
    if (filepath.includes('tools/')) return 'tool';
    if (filepath.includes('cognitive/')) return 'cognitive';
    if (filepath.includes('sessions/')) return 'session';
    return 'general';
}

function extractKeywords(filepath, content) {
    const keywords = new Set();
    const text = (filepath + ' ' + content).toLowerCase();
    
    const patterns = [
        'protocol', 'trade', 'strategy', 'risk', 'market', 'crypto',
        'options', 'kalshi', 'alpaca', 'analysis', 'execution', 'orion',
        'bias', 'cognitive', 'memory', 'pattern', 'emotional', 'meta'
    ];
    
    patterns.forEach(keyword => {
        if (text.includes(keyword)) {
            keywords.add(keyword);
        }
    });
    
    return Array.from(keywords);
}

function readFileContent(fullPath) {
    try {
        return fs.readFileSync(fullPath, 'utf8').substring(0, 2000);
    } catch {
        return '';
    }
}

// Check for new files and update index
function checkForNewFiles() {
    const allFiles = scanMemoryDir();
    const newFiles = [];
    
    allFiles.forEach(file => {
        if (!knownFiles.has(file.path)) {
            // Read content for keyword extraction
            const fullPath = path.join(__dirname, '..', '..', file.path);
            const content = readFileContent(fullPath);
            file.keywords = extractKeywords(file.path, content);
            file.contentPreview = content.substring(0, 500);
            
            newFiles.push(file);
            knownFiles.add(file.path);
            fileMetadata[file.path] = file;
        }
    });
    
    // Update index file
    const indexData = {
        timestamp: new Date().toISOString(),
        totalFiles: allFiles.length,
        newFilesThisSession: newFiles.length,
        files: allFiles.map(f => fileMetadata[f.path] || f)
    };
    
    fs.writeFileSync(INDEX_FILE, JSON.stringify(indexData, null, 2));
    
    if (newFiles.length > 0) {
        console.log(`🧠 GROWTH DETECTED: ${newFiles.length} new file(s)`);
        newFiles.forEach(f => {
            console.log(`   ✨ ${f.name} (${f.type}) - ${f.keywords.length} keywords`);
        });
    }
    
    return { total: allFiles.length, newCount: newFiles.length };
}

// Main monitoring loop
function startMonitoring() {
    console.log('🧠 ATLAS BRAIN GROWTH MONITOR STARTED');
    console.log(`📂 Watching: ${MEMORY_DIR}`);
    console.log(`📊 Index file: ${INDEX_FILE}`);
    console.log(`⏱️  Scan interval: ${SCAN_INTERVAL}ms\n`);
    
    loadExistingIndex();
    
    // Initial scan
    const initial = checkForNewFiles();
    console.log(`✅ Initial scan complete: ${initial.total} files indexed\n`);
    
    // Periodic scans
    setInterval(() => {
        const result = checkForNewFiles();
        if (result.newCount === 0) {
            process.stdout.write('.');
        }
    }, SCAN_INTERVAL);
}

// Handle graceful shutdown
process.on('SIGINT', () => {
    console.log('\n\n🛑 Monitor stopped');
    process.exit(0);
});

// Start the monitor
startMonitoring();
