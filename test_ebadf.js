const { spawn } = require('child_process');

// Test spawning multiple processes with detached: true
function spawnProcess(i) {
  console.log(`Spawning process ${i}...`);
  const child = spawn('echo', ['test'], {
    stdio: ['pipe', 'pipe', 'pipe'],
    detached: true
  });
  
  child.on('error', (err) => {
    console.error(`Process ${i} error:`, err.code, err.message);
  });
  
  child.on('close', (code) => {
    console.log(`Process ${i} closed with code ${code}`);
  });
  
  // Try to unref to see if that helps
  child.unref();
  
  return child;
}

// Spawn multiple processes
for (let i = 0; i < 10; i++) {
  spawnProcess(i);
}

console.log('All processes spawned, waiting...');
setTimeout(() => {
  console.log('Test complete');
}, 2000);