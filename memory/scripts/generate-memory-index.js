#!/usr/bin/env node

/**
 * Generate memory index for brain visualization auto-scan
 * Scans memory/ directory and creates /tmp/atlas-memory-index.json
 */

const fs = require('fs');
const path = require('path');

const MEMORY_DIR = path.join(__dirname, '..');
const INDEX_PATH = '/tmp/atlas-memory-index.json';

function detectFileType(filepath) {
    if (filepath.includes('/protocols/')) return 'protocol';
    if (filepath.includes('/trading/')) return 'trading';
    if (filepath.includes('/people/')) return 'people';
    if (filepath.includes('/tools/')) return 'tool';
    if (filepath.includes('/cognitive/')) return 'cognitive';
    if (filepath.includes('/sessions/')) return 'session';
    return 'memory';
}

function extractKeywords(filepath, content) {
    const keywords = new Set();
    const text = (filepath + ' ' + content.substring(0, 500)).toLowerCase();
    
    const patterns = [
        'protocol', 'trade', 'strategy', 'risk', 'market', 'crypto',
        'options', 'kalshi', 'alpaca', 'analysis', 'execution', 'orion',
        'bias', 'cognitive', 'memory', 'pattern', 'emotional', 'meta',
        'jupiter', 'solana', 'ethereum', 'bitcoin', 'defi', 'leverage'
    ];
    
    patterns.forEach(keyword => {
        if (text.includes(keyword)) {
            keywords.add(keyword);
        }
    });
    
    return Array.from(keywords);
}

function scanDirectory(dir, relativePath = '') {
    const files = [];
    
    try {
        const entries = fs.readdirSync(dir, { withFileTypes: true });
        
        entries.forEach(entry => {
            const fullPath = path.join(dir, entry.name);
            const relPath = path.join(relativePath, entry.name);
            
            if (entry.isDirectory()) {
                // Skip certain directories
                if (!['node_modules', '.git', 'visuals', 'scripts'].includes(entry.name)) {
                    files.push(...scanDirectory(fullPath, relPath));
                }
            } else if (entry.isFile() && entry.name.endsWith('.md')) {
                try {
                    const content = fs.readFileSync(fullPath, 'utf8');
                    const stats = fs.statSync(fullPath);
                    
                    const fileData = {
                        path: 'memory/' + relPath.replace(/\\/g, '/'),
                        name: entry.name.replace('.md', ''),
                        type: detectFileType(relPath),
                        keywords: extractKeywords(relPath, content),
                        size: stats.size,
                        modified: stats.mtime.toISOString(),
                        created: stats.birthtime.toISOString()
                    };
                    
                    files.push(fileData);
                } catch (err) {
                    console.error(`Error reading ${fullPath}:`, err.message);
                }
            }
        });
    } catch (err) {
        console.error(`Error scanning ${dir}:`, err.message);
    }
    
    return files;
}

function generateIndex() {
    console.log('🔍 Scanning memory directory...');
    
    const files = scanDirectory(MEMORY_DIR);
    
    const index = {
        generated: new Date().toISOString(),
        totalFiles: files.length,
        files: files,
        byType: {}
    };
    
    // Count by type
    files.forEach(f => {
        index.byType[f.type] = (index.byType[f.type] || 0) + 1;
    });
    
    // Write to temp file
    try {
        fs.writeFileSync(INDEX_PATH, JSON.stringify(index, null, 2));
        console.log(`✅ Generated index: ${files.length} files`);
        console.log(`   Types:`, index.byType);
        console.log(`   Written to: ${INDEX_PATH}`);
    } catch (err) {
        console.error('❌ Error writing index:', err.message);
        process.exit(1);
    }
}

// Run if called directly
if (require.main === module) {
    generateIndex();
}

module.exports = { generateIndex, scanDirectory };
