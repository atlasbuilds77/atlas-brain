#!/usr/bin/env node
const { Hyperliquid } = require('hyperliquid');
const { ethers } = require('ethers');
const fs = require('fs');

(async () => {
  const walletData = JSON.parse(
    fs.readFileSync('../hyperliquid-bot/.secrets/wallet.json', 'utf8')
  );
  
  const wallet = new ethers.Wallet(walletData.private_key);
  const sdk = new Hyperliquid(wallet);
  
  console.log('perpetuals methods:', Object.keys(sdk.info.perpetuals));
  console.log('\nexchange methods:', Object.keys(sdk.exchange));
  
  // Try to get user state
  try {
    const userState = await sdk.info.perpetuals.getUserState(walletData.address);
    console.log('\n✅ getUserState works!');
    console.log(userState);
  } catch (e) {
    console.log('\n❌ getUserState failed:', e.message);
  }
})();
