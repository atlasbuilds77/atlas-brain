#!/usr/bin/env node
const fs = require('fs');
const base58 = require('bs58').default || require('bs58');

const keypairPath = process.argv[2] || '.secrets/solana-keypair.json';
const keypairBytes = JSON.parse(fs.readFileSync(keypairPath, 'utf8'));
// Take first 32 bytes (the seed/secret key)
const seedBytes = new Uint8Array(keypairBytes.slice(0, 32));
const base58Seed = base58.encode(Buffer.from(seedBytes));

console.log(base58Seed);
