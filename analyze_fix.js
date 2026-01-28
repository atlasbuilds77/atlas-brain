// Analyze the bash-tools.exec.js file to find all detached: occurrences
const fs = require('fs');

try {
  const filePath = '/opt/homebrew/lib/node_modules/clawdbot/dist/agents/bash-tools.exec.js';
  const content = fs.readFileSync(filePath, 'utf8');
  const lines = content.split('\n');
  
  console.log('Analyzing file for detached: occurrences...\n');
  
  const occurrences = [];
  lines.forEach((line, index) => {
    if (line.includes('detached:')) {
      occurrences.push({
        lineNumber: index + 1,
        line: line.trim(),
        context: lines.slice(Math.max(0, index - 2), Math.min(lines.length, index + 3))
      });
    }
  });
  
  console.log(`Found ${occurrences.length} occurrences:\n`);
  
  occurrences.forEach((occ, i) => {
    console.log(`=== Occurrence ${i + 1} (Line ${occ.lineNumber}) ===`);
    console.log('Line:', occ.line);
    console.log('\nContext:');
    occ.context.forEach((ctxLine, ctxIdx) => {
      const ctxLineNum = occ.lineNumber - 2 + ctxIdx;
      const prefix = ctxLineNum === occ.lineNumber ? '>>> ' : '    ';
      console.log(`${prefix}${ctxLineNum}: ${ctxLine}`);
    });
    console.log('\n');
  });
  
  // Also check for process.platform !== "win32"
  console.log('\n\nChecking for process.platform !== "win32" patterns...\n');
  const platformChecks = [];
  lines.forEach((line, index) => {
    if (line.includes('process.platform') && line.includes('win32')) {
      platformChecks.push({
        lineNumber: index + 1,
        line: line.trim()
      });
    }
  });
  
  console.log(`Found ${platformChecks.length} platform checks:`);
  platformChecks.forEach((check, i) => {
    console.log(`${i + 1}. Line ${check.lineNumber}: ${check.line}`);
  });
  
} catch (error) {
  console.error('Error:', error.message);
}