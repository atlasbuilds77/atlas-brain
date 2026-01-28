const fs = require('fs');
const path = require('path');

const filePath = '/opt/homebrew/lib/node_modules/clawdbot/dist/agents/bash-tools.exec.js';
const content = fs.readFileSync(filePath, 'utf8');
const lines = content.split('\n');

lines.forEach((line, index) => {
  if (line.includes('detached:')) {
    console.log(`Line ${index + 1}: ${line.trim()}`);
  }
});