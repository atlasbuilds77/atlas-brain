#!/usr/bin/env node
const { Hyperliquid } = require('hyperliquid');
const { ethers } = require('ethers');
const fs = require('fs');

(async () => {
  try {
    const walletData = JSON.parse(
      fs.readFileSync('../hyperliquid-bot/.secrets/wallet.json', 'utf8')
    );
    
    console.log('Creating wallet...');
    const wallet = new ethers.Wallet(walletData.private_key);
    console.log('Wallet address:', wallet.address);
    
    console.log('\nInitializing Hyperliquid SDK...');
    const sdk = new Hyperliquid(wallet);
    
    console.log('\nSDK methods:');
    console.log('Keys:', Object.keys(sdk));
    
    // Try to get user state
    console.log('\nTrying different methods...');
    
    if (sdk.info) {
      console.log('info methods:', Object.keys(sdk.info));
    }
    
    if (sdk.exchange) {
      console.log('exchange methods:', Object.keys(sdk.exchange));
    }
    
  } catch (error) {
    console.error('Error:', error.message);
    console.error(error);
  }
})();
