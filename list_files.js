const fs = require('fs');
const path = require('path');

function listDir(dir, depth = 0) {
  const indent = '  '.repeat(depth);
  try {
    const items = fs.readdirSync(dir);
    for (const item of items) {
      const fullPath = path.join(dir, item);
      const stat = fs.statSync(fullPath);
      if (stat.isDirectory()) {
        console.log(`${indent}📁 ${item}/`);
        if (depth < 3) { // Limit depth to avoid too much output
          listDir(fullPath, depth + 1);
        }
      } else {
        console.log(`${indent}📄 ${item}`);
      }
    }
  } catch (err) {
    console.log(`${indent}❌ Error reading ${dir}: ${err.message}`);
  }
}

console.log('Current directory structure:');
listDir(process.cwd());