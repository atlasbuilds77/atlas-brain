const fs = require('fs');
const path = require('path');

const hooksDir = path.join(__dirname, 'clawdbot-hooks');
console.log('Hooks directory:', hooksDir);
console.log('Contents:', fs.readdirSync(hooksDir));
