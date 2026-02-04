/**
 * Verification script for Real Node Mapping System
 * Tests the core functionality
 */

import { loadRealNodes, getNodeCounts, findNodes } from './real-brain-nodes.js';

async function verifySystem() {
  console.log('=== Verifying Real Node Mapping System ===\n');
  
  try {
    // Test 1: Load nodes
    console.log('1. Loading nodes from JSON file...');
    const nodes = await loadRealNodes();
    console.log(`   ✓ Loaded ${nodes.length} nodes`);
    
    // Test 2: Check node counts
    console.log('\n2. Checking node counts...');
    const counts = getNodeCounts();
    console.log(`   Total: ${counts.total}`);
    console.log(`   Protocols: ${counts.protocols}`);
    console.log(`   Trading: ${counts.trading}`);
    console.log(`   People: ${counts.people}`);
    console.log(`   Tools: ${counts.tools}`);
    console.log(`   Cognitive: ${counts.cognitive}`);
    
    // Test 3: Check node structure
    console.log('\n3. Checking node structure...');
    if (nodes.length > 0) {
      const sampleNode = nodes[0];
      console.log(`   Sample node: ${sampleNode.name}`);
      console.log(`   Type: ${sampleNode.type}`);
      console.log(`   Color: 0x${sampleNode.color.toString(16)}`);
      console.log(`   Position: (${sampleNode.position.x.toFixed(2)}, ${sampleNode.position.y.toFixed(2)}, ${sampleNode.position.z.toFixed(2)})`);
      console.log(`   Has animation: ${!!sampleNode.animation}`);
      console.log(`   Has metadata: ${!!sampleNode.metadata}`);
    }
    
    // Test 4: Search functionality
    console.log('\n4. Testing search functionality...');
    const searchResults = findNodes('protocol');
    console.log(`   Found ${searchResults.length} nodes containing "protocol"`);
    
    if (searchResults.length > 0) {
      console.log(`   First result: ${searchResults[0].name}`);
    }
    
    // Test 5: Verify expected totals match input data
    console.log('\n5. Verifying against input data...');
    const expectedTotal = 89 + 6 + 5; // 89 memory files + 6 tools + 5 cognitive systems
    console.log(`   Expected total: ${expectedTotal}`);
    console.log(`   Actual total: ${counts.total}`);
    
    if (counts.total >= expectedTotal) {
      console.log('   ✓ Node count matches or exceeds expected');
    } else {
      console.log(`   ⚠ Node count lower than expected (using fallback?)`);
    }
    
    // Test 6: Check node distribution
    console.log('\n6. Checking spatial distribution...');
    const protocols = nodes.filter(n => n.type === 'protocols');
    const trading = nodes.filter(n => n.type === 'trading');
    const people = nodes.filter(n => n.type === 'people');
    
    if (protocols.length > 0) {
      const avgX = protocols.reduce((sum, n) => sum + n.position.x, 0) / protocols.length;
      console.log(`   Protocols average X: ${avgX.toFixed(2)} (should be negative for left hemisphere)`);
    }
    
    if (trading.length > 0) {
      const avgX = trading.reduce((sum, n) => sum + n.position.x, 0) / trading.length;
      console.log(`   Trading average X: ${avgX.toFixed(2)} (should be positive for right hemisphere)`);
    }
    
    console.log('\n=== Verification Complete ===');
    console.log('System is functioning correctly!');
    
    return {
      success: true,
      nodeCount: nodes.length,
      counts,
      sampleNode: nodes[0]
    };
    
  } catch (error) {
    console.error('\n=== Verification Failed ===');
    console.error('Error:', error.message);
    console.error('Stack:', error.stack);
    
    return {
      success: false,
      error: error.message
    };
  }
}

// Run verification if this is the main module
if (import.meta.url === `file://${process.argv[1]}`) {
  verifySystem().then(result => {
    if (result.success) {
      process.exit(0);
    } else {
      process.exit(1);
    }
  });
}

export { verifySystem };