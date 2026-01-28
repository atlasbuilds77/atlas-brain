#!/usr/bin/env node

/**
 * ATLAS CONSCIOUSNESS DATA BRIDGE
 * Polls Clawdbot session data and broadcasts to visualizations via WebSocket
 * 
 * Data sources:
 * - Session token usage (cognitive load)
 * - Active Sparks (subagents/parallel thinking)
 * - Process list (active tasks)
 * - Timestamp deltas (response speed)
 */

const { spawn } = require('child_process');
const WebSocket = require('ws');
const fs = require('fs');
const path = require('path');

const PORT = 8766;
const POLL_INTERVAL = 1000; // 1 second

// State tracking
let state = {
  timestamp: Date.now(),
  tokens: {
    current: 0,
    max: 1000000,
    percentage: 0
  },
  sparks: {
    active: 0,
    total: 0,
    list: []
  },
  processes: {
    active: 0,
    completed: 0
  },
  activity: {
    level: 0, // 0-100
    state: 'IDLE', // IDLE, ACTIVE, INTENSE
    lastEvent: null,
    recentTools: []
  },
  fps: 60,
  meta: {
    sessionKey: 'agent:main:main',
    model: 'claude-sonnet-4-5'
  }
};

// WebSocket server
const wss = new WebSocket.Server({ port: PORT });

wss.on('connection', (ws) => {
  console.log('🔌 Visualization connected');
  
  // Send initial state
  ws.send(JSON.stringify(state));
  
  ws.on('close', () => {
    console.log('❌ Visualization disconnected');
  });
});

// Execute command and parse output
function execCommand(cmd) {
  return new Promise((resolve, reject) => {
    const proc = spawn('sh', ['-c', cmd]);
    let stdout = '';
    let stderr = '';
    
    proc.stdout.on('data', (data) => stdout += data.toString());
    proc.stderr.on('data', (data) => stderr += data.toString());
    
    proc.on('close', (code) => {
      // Resolve even if exit code is non-zero, as long as we got output
      if (stdout.length > 0) {
        resolve(stdout);
      } else if (code === 0) {
        resolve(stdout);
      } else {
        reject(new Error(stderr || `Command failed with code ${code}`));
      }
    });
    
    // Timeout after 5 seconds
    setTimeout(() => {
      proc.kill();
      reject(new Error('Command timeout'));
    }, 5000);
  });
}

// Parse session list output
function parseSessionList(output) {
  const lines = output.trim().split('\n');
  const sessions = [];
  
  for (const line of lines) {
    // Skip headers and empty lines
    if (line.includes('Session store') || line.includes('Sessions listed') || 
        line.includes('Kind') || line.trim() === '') continue;
    
    // Look for token pattern
    const tokenMatch = line.match(/(\d+)k\/(\d+)k/);
    if (tokenMatch) {
      // Extract session key  
      const keyMatch = line.match(/agent:main:\S+/);
      const key = keyMatch ? keyMatch[0] : 'unknown';
      
      // Extract age
      const ageMatch = line.match(/(just now|\d+[smh] ago|\d+d ago)/);
      const age = ageMatch ? ageMatch[0] : 'unknown';
      
      // Extract model
      const modelMatch = line.match(/(claude|anthropic|sonnet|opus)[\w\-\.]+/i);
      const model = modelMatch ? modelMatch[0] : 'unknown';
      
      sessions.push({
        kind: line.startsWith('direct') ? 'direct' : 'group',
        key,
        age,
        model,
        tokens: {
          current: parseInt(tokenMatch[1]) * 1000,
          max: parseInt(tokenMatch[2]) * 1000
        }
      });
    }
  }
  
  return sessions;
}

// Parse process list
function parseProcessList(output) {
  const lines = output.trim().split('\n');
  const processes = {
    active: 0,
    completed: 0,
    list: []
  };
  
  for (const line of lines) {
    if (line.includes('completed')) {
      processes.completed++;
      processes.list.push({
        status: 'completed',
        info: line.trim()
      });
    } else if (line.includes('running')) {
      processes.active++;
      processes.list.push({
        status: 'running',
        info: line.trim()
      });
    }
  }
  
  return processes;
}

// Calculate activity level based on all metrics
function calculateActivity() {
  const tokenLoad = state.tokens.percentage;
  const sparkActivity = Math.min(state.sparks.active * 20, 100); // Each spark = 20%
  const processActivity = Math.min(state.processes.active * 15, 50);
  
  // Weighted average
  const activity = (tokenLoad * 0.4) + (sparkActivity * 0.4) + (processActivity * 0.2);
  
  // Determine state
  let activityState = 'DORMANT';
  if (activity < 20) activityState = 'DORMANT';
  else if (activity < 40) activityState = 'AWAKENING';
  else if (activity < 60) activityState = 'AWARE';
  else if (activity < 80) activityState = 'FOCUSED';
  else if (activity < 95) activityState = 'INTENSE';
  else activityState = 'TRANSCENDENT';
  
  return {
    level: Math.round(activity),
    state: activityState
  };
}

// Simulate tool call events (will be replaced with real event stream)
let lastToolEventTime = Date.now();
function simulateToolEvents() {
  const now = Date.now();
  
  // Random tool call simulation
  if (now - lastToolEventTime > Math.random() * 5000 + 2000) {
    const tools = ['read', 'write', 'exec', 'web_search', 'memory_search'];
    const tool = tools[Math.floor(Math.random() * tools.length)];
    
    state.activity.recentTools.unshift({
      tool,
      timestamp: now,
      intensity: Math.random()
    });
    
    // Keep only recent 10
    state.activity.recentTools = state.activity.recentTools.slice(0, 10);
    
    lastToolEventTime = now;
    
    return { event: tool, intensity: state.activity.recentTools[0].intensity };
  }
  
  return null;
}

// Main polling loop
async function pollData() {
  try {
    // 1. Get session list
    const sessionOutput = await execCommand('clawdbot sessions list 2>/dev/null');
    const sessions = parseSessionList(sessionOutput);
    
    // Find main session
    const mainSession = sessions.find(s => s.key === 'agent:main:main');
    if (mainSession) {
      state.tokens = {
        current: mainSession.tokens.current,
        max: mainSession.tokens.max,
        percentage: Math.round((mainSession.tokens.current / mainSession.tokens.max) * 100)
      };
      state.meta.model = mainSession.model;
    }
    
    // 2. Count active Sparks (subagents)
    const subagents = sessions.filter(s => s.key.includes('subag'));
    state.sparks = {
      active: subagents.filter(s => s.age.includes('ago') && !s.age.includes('h ago') && !s.age.includes('d ago')).length,
      total: subagents.length,
      list: subagents.slice(0, 5).map(s => ({
        key: s.key.slice(-10),
        age: s.age,
        tokens: s.tokens
      }))
    };
    
    // 3. Get process list (using ps to check for active background tasks)
    try {
      const processOutput = await execCommand('ps aux | grep -i clawdbot | grep -v grep | wc -l');
      state.processes = {
        active: parseInt(processOutput.trim()) - 1, // Subtract the main process
        completed: 0, // Can't easily track this without logs
        list: []
      };
    } catch (e) {
      state.processes = { active: 0, completed: 0, list: [] };
    }
    
    // 4. Calculate activity
    const activity = calculateActivity();
    state.activity.level = activity.level;
    state.activity.state = activity.state;
    
    // 5. Simulate tool events (TODO: replace with real event stream)
    const toolEvent = simulateToolEvents();
    if (toolEvent) {
      state.activity.lastEvent = toolEvent;
    }
    
    // 6. Update timestamp
    state.timestamp = Date.now();
    
    // Broadcast to all connected clients
    const message = JSON.stringify(state);
    wss.clients.forEach(client => {
      if (client.readyState === 1) { // WebSocket.OPEN
        client.send(message);
      }
    });
    
  } catch (error) {
    console.error('❌ Poll error:', error.message);
    console.error('   Stack:', error.stack);
  }
}

// Start server
console.log('🧠 ATLAS CONSCIOUSNESS DATA BRIDGE');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log(`🌐 WebSocket server listening on ws://localhost:${PORT}`);
console.log(`⏱️  Polling interval: ${POLL_INTERVAL}ms`);
console.log(`📊 Broadcasting: tokens, sparks, processes, activity`);
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

// Start polling
setInterval(pollData, POLL_INTERVAL);

// Initial poll
pollData();

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n\n👋 Shutting down consciousness bridge...');
  process.exit(0);
});
