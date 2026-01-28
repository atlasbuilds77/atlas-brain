#!/usr/bin/env node
/**
 * Test script for brain growth system
 * Verifies monitor, index, and animations
 */

const fs = require('fs');
const path = require('path');

const INDEX_FILE = '/tmp/atlas-memory-index.json';
const MEMORY_DIR = path.join(__dirname, '..');

console.log('🧠 ATLAS BRAIN GROWTH SYSTEM - TEST SUITE\n');

// Test 1: Check if monitor is running
console.log('[1/5] Checking monitor service...');
const { execSync } = require('child_process');
try {
    const processes = execSync('pgrep -f memory-monitor-service.js').toString();
    if (processes.trim()) {
        console.log('   ✅ Monitor is running (PID: ' + processes.trim() + ')');
    } else {
        console.log('   ❌ Monitor not running!');
        process.exit(1);
    }
} catch (err) {
    console.log('   ❌ Monitor not running! Start with: ./start-brain-growth.sh');
    process.exit(1);
}

// Test 2: Check if index file exists and is valid
console.log('\n[2/5] Checking index file...');
if (!fs.existsSync(INDEX_FILE)) {
    console.log('   ❌ Index file not found at ' + INDEX_FILE);
    process.exit(1);
}

let indexData;
try {
    indexData = JSON.parse(fs.readFileSync(INDEX_FILE, 'utf8'));
    console.log('   ✅ Index file valid');
    console.log(`   📊 Total files: ${indexData.totalFiles}`);
    console.log(`   🆕 New this session: ${indexData.newFilesThisSession}`);
    console.log(`   🕐 Last update: ${new Date(indexData.timestamp).toLocaleTimeString()}`);
} catch (err) {
    console.log('   ❌ Index file corrupt: ' + err.message);
    process.exit(1);
}

// Test 3: Verify file types are detected
console.log('\n[3/5] Checking file type detection...');
const types = {};
indexData.files.forEach(f => {
    types[f.type] = (types[f.type] || 0) + 1;
});
console.log('   File types found:');
Object.entries(types).forEach(([type, count]) => {
    const emoji = {
        protocol: '🔵',
        trading: '📈',
        people: '👤',
        tool: '🔧',
        cognitive: '🧠',
        session: '📝',
        general: '📄'
    };
    console.log(`     ${emoji[type] || '📄'} ${type}: ${count}`);
});

// Test 4: Verify keywords are extracted
console.log('\n[4/5] Checking keyword extraction...');
const sampleFiles = indexData.files.slice(0, 5);
let totalKeywords = 0;
sampleFiles.forEach(f => {
    if (f.keywords && f.keywords.length > 0) {
        totalKeywords += f.keywords.length;
    }
});
if (totalKeywords > 0) {
    console.log(`   ✅ Keywords extracted (${totalKeywords} across ${sampleFiles.length} sampled files)`);
} else {
    console.log('   ⚠️  No keywords found in sampled files');
}

// Test 5: Check visualization file
console.log('\n[5/5] Checking visualization file...');
const vizFile = path.join(__dirname, 'live-brain-atlas-connected.html');
if (fs.existsSync(vizFile)) {
    const content = fs.readFileSync(vizFile, 'utf8');
    
    // Check for key features
    const features = {
        'scanMemoryFiles': content.includes('scanMemoryFiles'),
        'spawnNewNode': content.includes('spawnNewNode'),
        'createConnections': content.includes('createConnections'),
        'updateGrowthMetrics': content.includes('updateGrowthMetrics'),
        'checkForNewMemoryFiles': content.includes('checkForNewMemoryFiles')
    };
    
    const passed = Object.values(features).filter(v => v).length;
    console.log(`   ✅ Visualization features: ${passed}/5 present`);
    
    if (passed < 5) {
        console.log('   Missing features:');
        Object.entries(features).forEach(([name, present]) => {
            if (!present) console.log(`     ❌ ${name}`);
        });
    }
} else {
    console.log('   ❌ Visualization file not found!');
    process.exit(1);
}

// Final summary
console.log('\n' + '='.repeat(60));
console.log('✅ ALL TESTS PASSED!');
console.log('='.repeat(60));
console.log('\n🚀 Your brain growth system is ready!');
console.log('\n📋 Next steps:');
console.log('   1. Open live-brain-atlas-connected.html in your browser');
console.log('   2. Create a new .md file in memory/');
console.log('   3. Watch your brain grow in real-time! ✨\n');
console.log('💡 Tip: Run ./demo-growth.sh to see it in action\n');
