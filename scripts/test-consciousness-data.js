#!/usr/bin/env node

/**
 * TEST CONSCIOUSNESS DATA BRIDGE
 * Quick test to verify data collection is working
 */

const WebSocket = require('ws');

console.log('🧪 Testing Consciousness Data Bridge\n');

// Start data bridge
const { spawn } = require('child_process');
const bridge = spawn('node', ['scripts/consciousness-data-bridge.js']);

bridge.stdout.on('data', (data) => {
  process.stdout.write(data);
});

bridge.stderr.on('data', (data) => {
  process.stderr.write(data);
});

// Wait for bridge to start
setTimeout(() => {
  console.log('\n📡 Connecting to data bridge...\n');
  
  const ws = new WebSocket('ws://localhost:8766');
  let messageCount = 0;
  
  ws.on('open', () => {
    console.log('✅ Connected!\n');
  });
  
  ws.on('message', (data) => {
    messageCount++;
    const state = JSON.parse(data.toString());
    
    console.log(`📊 Message #${messageCount} received:`);
    console.log(`   Tokens: ${(state.tokens.current/1000).toFixed(1)}k / ${(state.tokens.max/1000).toFixed(1)}k (${state.tokens.percentage}%)`);
    console.log(`   Sparks: ${state.sparks.active} active / ${state.sparks.total} total`);
    console.log(`   Processes: ${state.processes.active} running, ${state.processes.completed} completed`);
    console.log(`   Activity: ${state.activity.level}% - ${state.activity.state}`);
    if (state.activity.lastEvent) {
      console.log(`   Last Event: ${state.activity.lastEvent.event} (intensity: ${state.activity.lastEvent.intensity.toFixed(2)})`);
    }
    console.log('');
    
    // Stop after 5 messages
    if (messageCount >= 5) {
      console.log('✅ Test complete! Data is flowing correctly.\n');
      ws.close();
      bridge.kill();
      process.exit(0);
    }
  });
  
  ws.on('error', (error) => {
    console.error('❌ WebSocket error:', error.message);
    bridge.kill();
    process.exit(1);
  });
  
}, 2000);

// Safety timeout
setTimeout(() => {
  console.log('\n⏱️  Test timeout - stopping\n');
  bridge.kill();
  process.exit(1);
}, 15000);
