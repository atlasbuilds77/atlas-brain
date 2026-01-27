#!/usr/bin/env node
/**
 * Simple Hyperliquid REST API - No SDK
 * Direct API calls, reliable execution
 */
const axios = require('axios');
const { ethers } = require('ethers');
const fs = require('fs');

const API_URL = 'https://api.hyperliquid.xyz/info';
const EXCHANGE_URL = 'https://api.hyperliquid.xyz/exchange';

// Load wallet
const walletData = JSON.parse(
  fs.readFileSync('../hyperliquid-bot/.secrets/wallet.json', 'utf8')
);
const wallet = new ethers.Wallet(walletData.private_key);

async function getUserState() {
  const response = await axios.post(API_URL, {
    type: 'clearinghouseState',
    user: wallet.address
  });
  
  return response.data;
}

async function getAllMids() {
  const response = await axios.post(API_URL, {
    type: 'allMids'
  });
  
  return response.data;
}

async function placeOrder(coin, is_buy, sz, limit_px = null, order_type = 'Market') {
  const timestamp = Date.now();
  
  // Build order action
  const action = {
    type: 'order',
    orders: [{
      a: 2, // asset (ETH = 2)
      b: is_buy,
      p: limit_px || '0',
      s: sz.toString(),
      r: false, // reduce_only
      t: { limit: limit_px ? { tif: 'Gtc' } : { tif: 'Ioc' } }
    }],
    grouping: 'na'
  };
  
  // Sign the action
  const connection_id = ethers.utils.id(JSON.stringify(action) + timestamp);
  
  const message = {
    action: action,
    nonce: timestamp,
    vaultAddress: null
  };
  
  const signature = await wallet.signMessage(
    ethers.utils.arrayify(ethers.utils.id(JSON.stringify(message)))
  );
  
  // Send to exchange
  const response = await axios.post(EXCHANGE_URL, {
    action: action,
    nonce: timestamp,
    signature: signature,
    vaultAddress: null
  });
  
  return response.data;
}

async function setLeverage(coin, leverage) {
  const timestamp = Date.now();
  
  const action = {
    type: 'updateLeverage',
    asset: 2, // ETH
    isCross: true,
    leverage: leverage
  };
  
  const message = {
    action: action,
    nonce: timestamp,
    vaultAddress: null
  };
  
  const signature = await wallet.signMessage(
    ethers.utils.arrayify(ethers.utils.id(JSON.stringify(message)))
  );
  
  const response = await axios.post(EXCHANGE_URL, {
    action: action,
    nonce: timestamp,
    signature: signature,
    vaultAddress: null
  });
  
  return response.data;
}

async function main() {
  try {
    console.log('='.repeat(60));
    console.log('HYPERLIQUID SIMPLE API - ETH PERP');
    console.log('='.repeat(60));
    console.log(`Wallet: ${wallet.address}`);
    
    const command = process.argv[2];
    
    if (command === 'balance') {
      console.log('\n📊 Fetching account state...');
      const state = await getUserState();
      
      console.log('Account Value:', state.marginSummary.accountValue);
      console.log('Withdrawable:', state.marginSummary.withdrawable);
      
      if (state.assetPositions && state.assetPositions.length > 0) {
        console.log('\n📈 Positions:');
        state.assetPositions.forEach(p => {
          console.log(`  ${p.position.coin}: ${p.position.szi} @ $${p.position.entryPx}`);
          console.log(`    PnL: $${p.position.unrealizedPnl}`);
        });
      }
      
    } else if (command === 'price') {
      console.log('\n💰 Fetching prices...');
      const mids = await getAllMids();
      console.log('ETH:', mids.ETH);
      console.log('BTC:', mids.BTC);
      console.log('SOL:', mids.SOL);
      
    } else if (command === 'long') {
      const collateral = parseFloat(process.argv[3]) || 93;
      const leverage = parseInt(process.argv[4]) || 3;
      
      console.log(`\n🚀 Opening ETH LONG`);
      console.log(`  Collateral: $${collateral}`);
      console.log(`  Leverage: ${leverage}x`);
      
      // Get ETH price
      const mids = await getAllMids();
      const ethPrice = parseFloat(mids.ETH);
      console.log(`  ETH Price: $${ethPrice.toFixed(2)}`);
      
      // Calculate size
      const notional = collateral * leverage;
      const size = notional / ethPrice;
      
      console.log(`  Notional: $${notional.toFixed(2)}`);
      console.log(`  Size: ${size.toFixed(4)} ETH`);
      
      // Set leverage
      console.log(`\n⚙️  Setting leverage...`);
      await setLeverage('ETH', leverage);
      console.log('✅ Leverage set');
      
      // Place order
      console.log('📤 Placing market order...');
      const result = await placeOrder('ETH', true, size);
      
      console.log('\n✅ ORDER PLACED!');
      console.log(JSON.stringify(result, null, 2));
      
    } else {
      console.log('\nUsage:');
      console.log('  node simple_hl.js balance');
      console.log('  node simple_hl.js price');
      console.log('  node simple_hl.js long [collateral] [leverage]');
      console.log('\nExample:');
      console.log('  node simple_hl.js long 93 3');
    }
    
    process.exit(0);
    
  } catch (error) {
    console.error('\n❌ ERROR:', error.message);
    if (error.response) {
      console.error('Response:', error.response.data);
    }
    console.error(error);
    process.exit(1);
  }
}

main();
