// Test to understand the EBADF issue
const { spawn } = require('child_process');

async function testSpawn() {
  console.log('Testing spawn with detached: true...');
  
  for (let i = 0; i < 5; i++) {
    try {
      const child = spawn('echo', ['test'], {
        stdio: ['pipe', 'pipe', 'pipe'],
        detached: true
      });
      
      // Add error handler
      child.on('error', (err) => {
        console.error(`Child ${i} error:`, err.code, err.message);
      });
      
      // Read stdout
      child.stdout.on('data', (data) => {
        console.log(`Child ${i} stdout:`, data.toString().trim());
      });
      
      // Wait for exit
      await new Promise((resolve) => {
        child.on('close', (code) => {
          console.log(`Child ${i} closed with code ${code}`);
          resolve();
        });
      });
      
      // Try to destroy streams
      child.stdin.destroy();
      child.stdout.destroy();
      child.stderr.destroy();
      
      // Unref the child
      child.unref();
      
    } catch (err) {
      console.error(`Spawn ${i} failed:`, err.code, err.message);
    }
  }
  
  console.log('Test complete');
}

testSpawn().catch(console.error);